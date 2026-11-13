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
from pathlib import Path

import bpy

from ..Lib.commonUtils.runtime.diagnostics import *
from . import keymap_utils
from ..preferences.prefs import prefs
from ..overlays.deluxe import applyDeluxePrefs
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
_profile_store = None
_legacy_profile = False
_last_error = None
_wait_interval = 0.25
_unload_cleanup_attempts = 0
WATCH_INTERVAL = 0.25
MAX_WAIT_INTERVAL = 2.0
WATCH_REQUEST_BUDGET = 16
WATCH_TIME_BUDGET = 0.004
UNLOAD_CLEANUP_ATTEMPTS = 4
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
    allowed = runtime_keymaps_allowed(bpy.context, p.keymap)
    switches = tuple((name, _boolean_preferences(getattr(p, name)))
                     for name in ('keymap', 'pie', 'thirdparty'))
    return allowed, switches


def runtime_keymaps_allowed(context, settings):
    """Guard saved opt-ins and preset switches through Blender's own UI."""
    if applyDeluxePrefs.legacy_preset_active(context):
        return False
    if settings.deluxe_configured:
        return applyDeluxePrefs.uses_blender_keyconfig(context.window_manager.keyconfigs)
    return not _legacy_profile


def _bind_category(module):
    lists = [value for name, value in vars(module).items()
             if name.startswith('registered_') and name.endswith('_keymaps')
             and isinstance(value, list)]
    if len(lists) != 1:
        raise RuntimeError('Category must expose one registered keymap list: ' + module.KEYMAP_CATEGORY)
    keymap_utils.bind_category_pairs(module.KEYMAP_CATEGORY, lists[0])


def deluxe_profile():
    """Return the configured Deluxe editing API on Blender's main thread."""
    global _profile_store
    if not _ready() or not prefs().keymap.deluxe_configured:
        raise ValueError('Configure Deluxe keymaps before opening the profile editor')
    if _profile_store is None:
        from .deluxe_profiles import ProfileStore

        path = Path(__file__).resolve().with_name('deluxe-defaults.json')
        _profile_store = ProfileStore.open_catalog(
            path, prefs, _install_profile,
            allowed=lambda: runtime_keymaps_allowed(bpy.context, prefs().keymap))
        if _profile_store.load_issue:
            log(Severity.WARNING, TOOL_NAME, 'Deluxe profile recovery: ' + _profile_store.load_issue)
    return _profile_store


def deluxe_section_enabled(section):
    """Report the applied section state when the Deluxe profile is available."""
    try:
        return deluxe_profile().section_enabled(section)
    except ValueError:
        return False


def _install_profile(candidate, previous):
    """Apply through the same registrar and reject newly failed native work."""
    global _preference_state
    from .deluxe_schema import ProfileError

    if not _enabled or _registering or not _ready() or not prefs().keymap.deluxe_configured:
        raise ProfileError('Deluxe keymap runtime is unavailable')
    store = deluxe_profile()
    before = store.registration_results() if previous is not None else None
    try:
        _apply_categories(profile=candidate)
        if keymap_utils.pending_cleanup():
            raise ProfileError('Native keymap cleanup is pending')
        if before is not None:
            store.check_registration(candidate, before)
    except Exception:
        _preference_state = None
        raise


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
            f'{len(pending)} owned keymap item(s) still await cleanup; '
            'ownership is retained for the next cleanup attempt.')
    for category, error in errors:
        log(Severity.WARNING, TOOL_NAME, f'{category} cleanup reported {error}.')


def _apply_categories(*, profile=None):
    global _registering, _preference_state
    if _registering or not _ready():
        return 0
    _registering = True
    total = 0
    try:
        _clear_categories()
        p = prefs()
        if runtime_keymaps_allowed(bpy.context, p.keymap):
            modules = (*keymap_module_lst, pie_keymaps_register)
            if p.keymap.deluxe_configured:
                for module in modules:
                    _bind_category(module)
                total = deluxe_profile().register(profile)
                for module in modules:
                    keymap_utils.sync_category_pairs(module.KEYMAP_CATEGORY)
            else:
                for module in modules:
                    _bind_category(module)
                    if not p.keymap.enable_keymaps and module not in (
                            pipeline_keymaps_register, pie_keymaps_register):
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
    global _enabled, _legacy_profile
    _legacy_profile = (not prefs().keymap.deluxe_configured
                       and applyDeluxePrefs.has_legacy_profile(bpy.context))
    _enabled = True
    try:
        total = _apply_categories()
    except Exception:
        _enabled = False
        raise
    if bpy.app.timers.is_registered(_retry_unload_cleanup):
        bpy.app.timers.unregister(_retry_unload_cleanup)
    if not bpy.app.timers.is_registered(_watch_keymaps):
        bpy.app.timers.register(_watch_keymaps, first_interval=WATCH_INTERVAL, persistent=True)
    log(Severity.INFO, TOOL_NAME, f'Registered {total} owned keymaps.')
    return total


def _retry_unload_cleanup():
    global _unload_cleanup_attempts
    if _enabled:
        return None
    _unload_cleanup_attempts -= 1
    remaining = keymap_utils.retry_unreadable_cleanup(WATCH_REQUEST_BUDGET)
    if remaining and _unload_cleanup_attempts:
        return WATCH_INTERVAL
    return None


def unregister():
    global _enabled, _preference_state, _last_error, _profile_store, _unload_cleanup_attempts
    _enabled = False
    if bpy.app.timers.is_registered(_watch_keymaps):
        bpy.app.timers.unregister(_watch_keymaps)
    try:
        _clear_categories()
    finally:
        # Read Preferences may unload us before Blender restores operator RNA.
        if any(row['reason'] == 'owned_snapshot_unavailable' for row in keymap_utils.pending_cleanup()):
            if not bpy.app.timers.is_registered(_retry_unload_cleanup):
                _unload_cleanup_attempts = UNLOAD_CLEANUP_ATTEMPTS
                bpy.app.timers.register(_retry_unload_cleanup, first_interval=WATCH_INTERVAL)
        _preference_state = None
        _last_error = None
        if _profile_store is not None:
            _profile_store.close()
        _profile_store = None


def refresh():
    """Return the installed count, or None if a refresh could not start."""
    if _enabled and not _registering and _ready():
        return _apply_categories()
