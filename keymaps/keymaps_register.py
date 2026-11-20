"""Register, refresh and release the JSON Deluxe catalog on Blender’s main thread."""

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
from . import default_bindings
from ..preferences.prefs import prefs
from ..overlays.deluxe import applyDeluxePrefs

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

TOOL_NAME = 'Keymaps'

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# A single persistent timer owns readiness and reconciliation. No timer writes
# preferences. Explicit managed-default rules use their own restoration ledger.
_enabled = False
_registering = False
_preference_state = None
_profile_store = None
_retired_stock_services = []
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


def _preference_signature():
    p = prefs()
    allowed = runtime_keymaps_allowed(bpy.context, p.keymap)
    # Category and section choices are committed through the catalog editor.
    # Legacy preference groups must neither gate nor rebuild that catalog.
    return allowed, bool(p.keymap.deluxe_configured), bool(p.keymap.enable_keymaps)


def runtime_keymaps_allowed(context, settings):
    """Guard saved opt-ins and preset switches through Blender's own UI."""
    if applyDeluxePrefs.legacy_preset_active(context):
        return False
    if settings.deluxe_configured:
        return applyDeluxePrefs.uses_blender_keyconfig(context.window_manager.keyconfigs)
    return not _legacy_profile


def deluxe_profile():
    """Return the configured Deluxe editing API on Blender's main thread."""
    if not _ready() or not prefs().keymap.deluxe_configured:
        raise ValueError('Configure Deluxe keymaps before opening the profile editor')
    return _catalog_store()


def has_unsaved_edits():
    return _profile_store is not None and _profile_store.has_unsaved_edits


def _restore_stock_bindings():
    """Keep restoration ownership alive after its profile store is closed."""
    if _profile_store is not None and _profile_store.registration not in _retired_stock_services:
        _retired_stock_services.append(_profile_store.registration)
    _retired_stock_services[:] = [service for service in _retired_stock_services
                                 if not service.restore_stock_add()]
    return not _retired_stock_services


def _catalog_store():
    """Load one catalog for required shortcuts and the configured editor."""
    global _profile_store
    if _profile_store is None:
        from .deluxe_profiles import ProfileStore

        path = Path(__file__).resolve().with_name('deluxe-defaults.json')
        options = dict(install_toggle=_install_toggle,
                       allowed=lambda: runtime_keymaps_allowed(bpy.context, prefs().keymap))
        if getattr(prefs().keymap, 'edit_shipped_defaults', False):
            _profile_store = ProfileStore.open_catalog(path, prefs, _install_profile, **options)
        else:
            profile = Path(bpy.utils.user_resource('CONFIG')) / 'bluehole/keymaps.json'
            _profile_store = ProfileStore.open_user(path, profile, prefs, _install_profile, **options)
        if _profile_store.load_issue:
            log(Severity.WARNING, TOOL_NAME, 'Deluxe profile recovery: ' + _profile_store.load_issue)
    return _profile_store


def set_authoring_mode(enabled):
    """Switch storage explicitly; unsaved drafts must be resolved first."""
    global _profile_store
    from ..preferences.addon.keymaps import deluxe_editor_ops
    deluxe_editor_ops.require_saved_draft()
    old = bool(getattr(prefs().keymap, 'edit_shipped_defaults', False))
    _clear_categories()
    if _profile_store is not None:
        _profile_store.close()
    _profile_store = None
    prefs().keymap.edit_shipped_defaults = enabled
    try:
        _apply_categories()
    except Exception:
        _profile_store = None
        prefs().keymap.edit_shipped_defaults = old
        _apply_categories()
        raise
    bpy.context.preferences.is_dirty = True


def deluxe_section_enabled(section):
    """Report the applied section state when the Deluxe profile is available."""
    if not runtime_keymaps_allowed(bpy.context, prefs().keymap):
        return False
    try:
        return deluxe_profile().section_enabled(section)
    except ValueError:
        return False


def _install_toggle(candidate, previous, plans):
    if (not _enabled or _registering or not _ready() or not prefs().keymap.deluxe_configured
            or _preference_state != _preference_signature()):
        return None
    return deluxe_profile().update_registration(candidate, previous, plans=plans, verify=True)


def _install_profile(candidate, previous):
    """Apply through the same registrar and reject newly failed native work."""
    global _preference_state
    from .deluxe_schema import ProfileError

    if not _enabled or _registering or not _ready() or not prefs().keymap.deluxe_configured:
        raise ProfileError('Deluxe keymap runtime is unavailable')
    store = deluxe_profile()
    before = store.registration_results() if previous is not None else None
    try:
        if previous is None or _preference_state != _preference_signature():
            _apply_categories(profile=candidate)
        else:
            store.update_registration(candidate, previous)
        if keymap_utils.blocking_cleanup() or default_bindings.pending_cleanup():
            raise ProfileError('Native keymap cleanup is pending')
        if before is not None:
            store.check_registration(candidate, before)
    except Exception:
        _preference_state = None
        raise


@keymap_utils.batch_merged_updates()
def _clear_categories():
    _restore_stock_bindings()
    default_bindings.release_all()
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


def _apply_categories(*, profile=None):
    global _registering, _preference_state
    if _registering or not _ready():
        return 0
    _registering = True
    total = 0
    try:
        _clear_categories()
        if _retired_stock_services or default_bindings.pending_cleanup() or keymap_utils.blocking_cleanup():
            raise RuntimeError('Blender default bindings still await restoration')
        p = prefs()
        if runtime_keymaps_allowed(bpy.context, p.keymap):
            total = _catalog_store().register(profile, required_only=not p.keymap.deluxe_configured)
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
        default_bindings.retry_cleanup()
        default_bindings.reconcile(budget=4, time_budget=WATCH_TIME_BUDGET)
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
    remaining = bool(default_bindings.retry_cleanup()) or remaining
    remaining = not _restore_stock_bindings() or remaining
    if remaining and _unload_cleanup_attempts:
        return WATCH_INTERVAL
    return None


def drain_cleanup():
    """Updater barrier: retain this callable until all old ownership is released."""
    if _enabled:
        raise RuntimeError('Keymap cleanup requires an unloaded runtime')
    if bpy.app.timers.is_registered(_retry_unload_cleanup):
        bpy.app.timers.unregister(_retry_unload_cleanup)
    owned_ready = keymap_utils.drain_cleanup(WATCH_REQUEST_BUDGET)
    defaults_ready = not default_bindings.retry_cleanup()
    stock_ready = _restore_stock_bindings()
    return owned_ready and defaults_ready and stock_ready


def unregister():
    global _enabled, _preference_state, _last_error, _profile_store, _unload_cleanup_attempts
    _enabled = False
    if bpy.app.timers.is_registered(_watch_keymaps):
        bpy.app.timers.unregister(_watch_keymaps)
    try:
        _clear_categories()
    finally:
        # Read Preferences may unload us before Blender restores operator RNA.
        if (_retired_stock_services or default_bindings.pending_cleanup()
                or keymap_utils.unreadable_cleanup_pending()):
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
