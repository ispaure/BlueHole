"""
Top-level registration and refresh management for Blue Hole keymaps.

This module orchestrates registration, unregistration, and refresh of all
standard keymap categories and pie keymaps.

Child keymap register modules are responsible for:
- determining which actions are enabled
- registering their own keymaps
- storing runtime keymap references
- returning the number of successfully registered keymaps

This module is responsible for:
- registration order
- centralized high-level logging
- total keymap registration summaries
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://github.com/ispaure/BlueHole

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS

import time

import bpy

from ..Lib.commonUtils.runtime.diagnostics import *
from . import keymap_utils
from ..preferences.prefs import prefs
from ..debug.debug_flags import *
from .pie import pie_keymaps_register
from . import mesh_keymaps_register
from . import navigation_keymaps_register
from . import object_keymaps_register
from . import pipeline_keymaps_register
from . import sculpt_keymaps_register
from . import selection_keymaps_register
from . import transform_keymaps_register
from . import uv_keymaps_register
from . import other_keymaps_register

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

TOOL_NAME = 'Keymaps'

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

keymap_module_lst = (
    mesh_keymaps_register,
    navigation_keymaps_register,
    object_keymaps_register,
    pipeline_keymaps_register,
    sculpt_keymaps_register,
    selection_keymaps_register,
    transform_keymaps_register,
    uv_keymaps_register,
    other_keymaps_register,
)


# A single persistent timer owns readiness and reconciliation. No timer writes
# preferences or changes a foreign keymap item.
_enabled = False
_registering = False
_preference_state = None
_last_error = None
_wait_interval = 0.25
WATCH_INTERVAL = 0.25
MAX_WAIT_INTERVAL = 2.0
WATCH_REQUEST_BUDGET = 16
WATCH_TIME_BUDGET = 0.004
watcher_stats = {'ticks': 0, 'max_seconds': 0.0, 'last_seconds': 0.0,
                 'category_refreshes': 0, 'errors': 0}


def _ready():
    wm = getattr(bpy.context, 'window_manager', None)
    configs = getattr(wm, 'keyconfigs', None)
    return (prefs().is_ready() and configs is not None and
            configs.addon is not None and configs.user is not None and
            configs.active is not None)


def _boolean_preferences(group):
    """Watch behavior switches, including categories with old no-op callbacks."""
    raw = getattr(group, '_raw', group)
    values = []
    for prop in raw.bl_rna.properties:
        if prop.identifier == 'rna_type':
            continue
        if prop.type == 'BOOLEAN':
            values.append((prop.identifier, bool(getattr(raw, prop.identifier))))
        elif prop.type == 'POINTER':
            value = getattr(raw, prop.identifier)
            if isinstance(value, bpy.types.PropertyGroup):
                values.append((prop.identifier, _boolean_preferences(value)))
    return tuple(values)


def _preference_signature():
    p = prefs()
    return tuple((name, _boolean_preferences(getattr(p, name)))
                 for name in ('keymap', 'pie', 'thirdparty') if hasattr(p, name))


def _bind_category(module):
    lists = [value for name, value in vars(module).items()
             if name.startswith('registered_') and name.endswith('_keymaps')
             and isinstance(value, list)]
    if len(lists) != 1:
        raise RuntimeError('Category must expose one registered keymap list: ' + module.KEYMAP_CATEGORY)
    keymap_utils.bind_category_pairs(module.KEYMAP_CATEGORY, lists[0])


def _clear_categories():
    errors = []
    for module in (pie_keymaps_register, *reversed(keymap_module_lst)):
        try:
            module.unregister()
        except Exception as exc:
            errors.append((module.KEYMAP_CATEGORY, type(exc).__name__))
    # Drain pending requests and items from partial category initialization too.
    keymap_utils.release_all()
    retained = keymap_utils.retained_edits()
    if retained:
        log(Severity.WARNING, TOOL_NAME,
            f'{len(retained)} directly edited source keymap item(s) retained as user data; '
            'inspect keymap runtime diagnostics before removing them.')
    pending = keymap_utils.pending_cleanup()
    if pending:
        log(Severity.WARNING, TOOL_NAME,
            f'{len(pending)} owned keymap item(s) still await native removal; '
            'ownership is retained for the next cleanup attempt.')
    for category, error in errors:
        log(Severity.WARNING, TOOL_NAME, f'{category} cleanup reported {error}.')


def _apply_categories():
    global _registering, _preference_state
    if _registering or not _ready():
        return 0
    _registering = True
    total = 0
    try:
        _clear_categories()
        p = prefs()
        for module in (*keymap_module_lst, pie_keymaps_register):
            _bind_category(module)
            # Pipeline chooses its obligatory actions itself; Pie has its own gate.
            if module not in (pipeline_keymaps_register, pie_keymaps_register) and not p.keymap.enable_keymaps:
                continue
            total += module.register()
        _preference_state = _preference_signature()
        watcher_stats['category_refreshes'] += 1
        return total
    except Exception:
        _preference_state = None
        _clear_categories()
        raise
    finally:
        _registering = False


def _watch_keymaps():
    global _wait_interval, _last_error
    if not _enabled:
        return None
    started = time.monotonic()
    try:
        if not _ready():
            _wait_interval = min(MAX_WAIT_INTERVAL, _wait_interval * 2)
            return _wait_interval
        if _preference_state != _preference_signature():
            _apply_categories()
        keymap_utils.reconcile(budget=WATCH_REQUEST_BUDGET, time_budget=WATCH_TIME_BUDGET)
        _wait_interval = WATCH_INTERVAL
        _last_error = None
        return WATCH_INTERVAL
    except Exception as exc:
        message = type(exc).__name__ + ': ' + str(exc)
        if message != _last_error:
            log(Severity.WARNING, TOOL_NAME, 'Keymap reconciliation pending: ' + message)
            _last_error = message
        watcher_stats['errors'] += 1
        _wait_interval = min(MAX_WAIT_INTERVAL, max(WATCH_INTERVAL, _wait_interval * 2))
        return _wait_interval
    finally:
        elapsed = time.monotonic() - started
        watcher_stats['ticks'] += 1
        watcher_stats['last_seconds'] = elapsed
        watcher_stats['max_seconds'] = max(watcher_stats['max_seconds'], elapsed)


def register():
    global _enabled
    _enabled = True
    try:
        total = _apply_categories()
    except Exception:
        _enabled = False
        raise
    if not bpy.app.timers.is_registered(_watch_keymaps):
        bpy.app.timers.register(_watch_keymaps, first_interval=WATCH_INTERVAL, persistent=True)
    log(Severity.INFO, TOOL_NAME, f'Registered {total} owned keymaps.')
    return total


def unregister():
    global _enabled, _preference_state, _last_error
    _enabled = False
    if bpy.app.timers.is_registered(_watch_keymaps):
        bpy.app.timers.unregister(_watch_keymaps)
    try:
        _clear_categories()
    finally:
        _preference_state = None
        _last_error = None


def refresh():
    """Refresh category requests without creating another watcher."""
    if _registering:
        return
    if _enabled:
        _apply_categories()
