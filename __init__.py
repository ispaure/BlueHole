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
from .Lib.commonUtils import debugUtils
debugUtils.project_prefix = "Blue Hole"
debugUtils.use_time_delta = False

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
    "blender": (4, 5, 1),
    "version": (6, 9, 21),
    "location": "",
    "warning": "",
    "category": "Generic",
}

# Set project prefix to include version for logging purposes.
debugUtils.project_prefix = f'{bl_info["name"]} {".".join(map(str, bl_info["version"]))}'

# ----------------------------------------------------------------------------------------------------------------------
# STATE

_keymaps_registered = False

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
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
    global _keymaps_registered

    from .preferences.prefs import prefs

    print("Blue Hole: _post_register_init called")

    p = prefs()

    print("Blue Hole: prefs object:", p)
    print("Blue Hole: prefs ready:", p.is_ready())
    print("Blue Hole: prefs container:", p.container)

    if not p.is_ready() or p.container is None:
        print("Blue Hole: preferences not ready, retrying...")
        return 0.5

    print("Blue Hole: preferences ready")

    if not _keymaps_registered:
        keymaps_register.register()
        _keymaps_registered = True

    envManager.if_current_env_missing_set_default()

    env_cls = envManager.get_env_from_prefs_active_env()
    env_cls.set_pref_from_ini()

    if not bpy.app.timers.is_registered(update_env_timer):
        bpy.app.timers.register(update_env_timer, persistent=True)

    return None


def unregister():
    global _keymaps_registered

    # The post-register timer may still be waiting for preferences to become ready.
    if bpy.app.timers.is_registered(_post_register_init):
        bpy.app.timers.unregister(_post_register_init)

    if bpy.app.timers.is_registered(update_env_timer):
        bpy.app.timers.unregister(update_env_timer)

    if _keymaps_registered:
        keymaps_register.unregister()
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
