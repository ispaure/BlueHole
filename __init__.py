"""
Blue Hole is a blender addon that was created and written by Marc-André Voyer for Environment Artists.

Highlights are Perforce integration and Bridge to Unity/Unreal
Official GitHUB: https://www.github.com/ispaure/BlueHole
Official Website: https://blue-hole.weebly.com
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

# Import bpy
import bpy

# Disable use of pySide for UI (rely on OS terminal to create windows instead)
from .Lib.commonUtils import uiUtils
uiUtils.use_pyside = False

# Import Blue Hole Scripts
from .blenderUtils import callbacks
from .preferences import addon_prefs as addon_prefs
from .operators import operators_register
from .environment import envManager as envManager
from .ui.menus import menus_register
from .keymaps import keymaps_register

# ----------------------------------------------------------------------------------------------------------------------
# PLUGIN INFO

bl_info = {"name": "Blue Hole",
           "author": "Marc-André Voyer",
           "description": "",
           "blender": (4, 5, 1),
           "version": (6, 3, 10),
           "location": "",
           "warning": "",
           "category": "Generic"
           }


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Classes
# Operators in List


# Register
def register():

    callbacks.register()
    addon_prefs.register()
    operators_register.register()
    menus_register.register()
    keymaps_register.register()

    # Schedule init AFTER Blender finishes enabling the addon
    bpy.app.timers.register(_post_register_init, first_interval=0.0)


def _post_register_init():
    from .preferences.prefs import prefs
    p = prefs()
    if not p.is_ready() or p.container is None:
        return 0.05

    # Now safe: prefs exist
    envManager.if_current_env_missing_set_default()
    env_cls = envManager.get_env_from_prefs_active_env()
    env_cls.set_pref_from_ini()

    # Start your recurring timer ONLY after init is safe
    if not hasattr(bpy.app.timers, "_bluehole_timer_registered"):
        bpy.app.timers.register(update_env_timer, persistent=True)
        bpy.app.timers._bluehole_timer_registered = True

    return None  # stop running


# Unregister
def unregister():

    keymaps_register.unregister()
    menus_register.unregister()
    operators_register.unregister()
    addon_prefs.unregister()
    callbacks.unregister()


    # Unregister timer
    bpy.app.timers.unregister(update_env_timer)
    if hasattr(bpy.app.timers, "_bluehole_timer_registered"):
        del bpy.app.timers._bluehole_timer_registered


def update_env_timer():
    """
    Every set interval whilst the preferences are opened, fields from Blue Hole are compared to the Active Environment's
    env_variables.ini. If changes are detected, the .ini file is overwritten with the changes.
    """

    interval = 0.25
    prefs = bpy.context.preferences
    addon = prefs.addons.get(__package__)
    if addon is None:
        return interval  # addon not loaded

    addon_preferences = addon.preferences
    if addon_preferences is None:
        return interval  # should not happen

    # Only run if Add-ons section is active
    if prefs.active_section != 'ADDONS':
        return interval

    # Check if the panel was drawn recently
    visible = getattr(addon_preferences, "_prefs_visible", False)
    # Reset for next timer run
    addon_preferences._prefs_visible = False
    if not visible:
        return interval  # skip logic if panel not drawn

    # Safe to run expensive logic
    env_cls = envManager.get_env_from_prefs_active_env()
    env_cls.set_ini_from_pref(addon_preferences)

    return interval
