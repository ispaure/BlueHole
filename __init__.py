"""
Blue Hole is a Blender add-on created by Marc-André Voyer for environment artists.

Highlights include Perforce integration and a bridge to Unity and Unreal.
Official GitHub: https://github.com/ispaure/BlueHole
Official website: https://blue-hole.weebly.com
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION

__author__ = "Marc-André Voyer"
__copyright__ = "Copyright (C) 2020-2026, Marc-André Voyer"
__license__ = "MIT License"
__maintainer__ = "Marc-André Voyer"
__email__ = "marcandre.voyer@gmail.com"
__status__ = "Production"

# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS

print('STARTING BLUE HOLE')

import bpy

# Disable PySide UI usage and rely on the native OS UI backend instead.
from .Lib.commonUtils import ui
ui.use_pyside = False

# Set Debug Project Prefix for logging, remove time delta unless profiling.
from .Lib.commonUtils.runtime import diagnostics as debugUtils
from .Lib.commonUtils.ui.diagnostics import present_diagnostic
debugUtils.configure(project_prefix="Blue Hole", use_time_delta=False, presenter=present_diagnostic)

from .wrappers.perforce import initialize_runtime as initialize_perforce_runtime
initialize_perforce_runtime()

from .blenderUtils import callbacks, addon_callbacks
from .preferences import addon_prefs
from .operators import operators_register
from .environment import envManager
from .ui.menus import menus_register
from .keymaps import keymaps_register

# ----------------------------------------------------------------------------------------------------------------------
# ADD-ON INFO

bl_info = {
    "name": "Blue Hole",
    "author": "Marc-André Voyer",
    "description": "",
    "blender": (5, 2, 2),
    "version": (6, 9, 21),
    "location": "",
    "warning": "",
    "category": "Generic",
}

# Set project prefix to include version for logging purposes.
debugUtils.configure(project_prefix=f'{bl_info["name"]} {".".join(map(str, bl_info["version"]))}')

# ----------------------------------------------------------------------------------------------------------------------
# STATE

_keymaps_registered = False
_addon_registered = False
_post_register_wait = 0.05
_post_register_error = None

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
    global _addon_registered, _post_register_wait
    _addon_registered = True
    _post_register_wait = 0.05
    callbacks.register()
    addon_callbacks.register()
    addon_prefs.register()
    operators_register.register()
    menus_register.register()

    # Preference-dependent initialization must wait until Blender has fully
    # enabled the add-on and created its AddonPreferences instance.
    if not bpy.app.timers.is_registered(_post_register_init):
        bpy.app.timers.register(_post_register_init, first_interval=0.0)


def _post_register_init():
    """
    Complete preference-dependent initialization once the Blue Hole
    AddonPreferences instance becomes available.
    """

    global _keymaps_registered, _post_register_wait, _post_register_error

    if not _addon_registered:
        return None

    from .preferences.prefs import prefs

    p = prefs()

    wm = getattr(bpy.context, 'window_manager', None)
    configs = getattr(wm, 'keyconfigs', None)
    if (not p.is_ready() or configs is None or configs.addon is None
            or configs.user is None or configs.active is None):
        _post_register_wait = min(2.0, _post_register_wait * 2)
        return _post_register_wait

    if not _keymaps_registered:
        try:
            keymaps_register.register()
            _keymaps_registered = True
            _post_register_error = None
        except Exception as exc:
            # Registration drains partial ownership. Keep a bounded retry until
            # providers are ready; unload must also work before this succeeds.
            message = type(exc).__name__ + ': ' + str(exc)
            if message != _post_register_error:
                print('Blue Hole keymap initialization pending: ' + message)
                _post_register_error = message
            _post_register_wait = min(2.0, _post_register_wait * 2)
            return _post_register_wait

    envManager.if_current_env_missing_set_default()

    env_cls = envManager.get_env_from_prefs_active_env()
    env_cls.set_pref_from_ini()

    if not bpy.app.timers.is_registered(update_env_timer):
        bpy.app.timers.register(update_env_timer, persistent=True)

    return None


def unregister():
    global _keymaps_registered, _addon_registered
    _addon_registered = False

    if bpy.app.timers.is_registered(_post_register_init):
        bpy.app.timers.unregister(_post_register_init)

    if bpy.app.timers.is_registered(update_env_timer):
        bpy.app.timers.unregister(update_env_timer)

    try:
        keymaps_register.unregister()
    finally:
        _keymaps_registered = False

    menus_register.unregister()
    operators_register.unregister()
    addon_prefs.unregister()
    addon_callbacks.unregister()
    callbacks.unregister()


def update_env_timer():
    """
    While the add-on preferences are visible, compare Blue Hole preference values
    against the active environment's env_variables.ini file and overwrite the file
    if changes are detected.
    """

    interval = 0.25

    prefs = bpy.context.preferences
    addon = prefs.addons.get(__package__)

    if addon is None:
        return interval

    addon_preferences = addon.preferences

    if addon_preferences is None:
        return interval

    if prefs.active_section != "ADDONS":
        return interval

    visible = getattr(addon_preferences, "_prefs_visible", False)
    addon_preferences._prefs_visible = False

    if not visible:
        return interval

    env_cls = envManager.get_env_from_prefs_active_env()
    env_cls.set_ini_from_pref(addon_preferences)

    return interval
