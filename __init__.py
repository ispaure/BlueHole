"""
Blue Hole is a blender addon that was created and written by Marc-André Voyer for Environment Artists.

Highlights are export scripts and Perforce source control integration.
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
# Need to be first import, and throw error in case .commonUtils stuff cannot be accessed.
from .Lib.commonUtils import uiUtils
uiUtils.use_pyside = False

# Import Blue Hole Scripts
from .blenderUtils import callbacks

from .preferences import addon_prefs as addon_prefs

# Import Blue Hole Operators
from .Operators import dirOp as dirOp
from .Operators import envOp as envOp
from .Operators import externalAddonOp as externalAddonOp
from .Operators import foodOp as foodOp
from .Operators import helpOp as helpOp
from .Operators import impExpOp as impExpOp
from .Operators import musicOp as musicOp
from .Operators import otherOp as otherOp
from .Operators import sendOp as sendOp
from .Operators import sortOp as sortOp
from .Operators import sourceControlOp as sourceControlOp
from .Operators import themeOp as themeOp

# Import Env Utils
from .environment import envManager as envManager

# Import Menus
from .Menus import menu as menu
from .Menus import pieMenu as pieMenu

# ----------------------------------------------------------------------------------------------------------------------
# PLUGIN INFO

bl_info = {"name": "Blue Hole",
           "author": "Marc-André Voyer",
           "description": "",
           "blender": (4, 5, 1),
           "version": (2, 0, 0),
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
operator_file_lst = (dirOp,
                     envOp,
                     externalAddonOp,
                     foodOp,
                     helpOp,
                     impExpOp,
                     musicOp,
                     otherOp,
                     sendOp,
                     sortOp,
                     sourceControlOp,
                     themeOp)

menu_file_lst = (menu, pieMenu)


# Register
def register():

    # Register Callbacks
    callbacks.register()
    # Register preferences
    addon_prefs.register()

    # Register operators
    for file in operator_file_lst:
        file.register()

    # Register menus
    for file in menu_file_lst:
        file.register()

    # Register Current Env Tools
    envManager.if_current_env_missing_set_default()  # When a saved environment is no longer available, rever to default
    env_cls = envManager.get_env_from_prefs_active_env()
    env_cls.set_pref_from_ini()

    # Register Header Menu
    from .Menus import headerMenu
    headerMenu.register()

    # Register timer to update .ini file if modified in Blender Prefs
    if not hasattr(bpy.app.timers, "_bluehole_timer_registered"):
        bpy.app.timers.register(update_env_timer, persistent=True)
        bpy.app.timers._bluehole_timer_registered = True


# Unregister
def unregister():
    # Unregister Callbacks
    callbacks.unregister()

    # Unregister preferences
    addon_prefs.unregister()

    # Unregister Header Menu
    from .Menus import headerMenu
    headerMenu.unregister()

    # Register operators
    for file in operator_file_lst:
        file.unregister()

    # Register menus
    for file in menu_file_lst:
        file.unregister()

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
