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
import addon_utils

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
_diagnostics_printed = False

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
    print("Blue Hole: register()")
    print("Blue Hole: root __name__:", repr(__name__))
    print("Blue Hole: root __package__:", repr(__package__))

    callbacks.register()
    addon_callbacks.register()
    addon_prefs.register()
    operators_register.register()
    menus_register.register()

    # Preference-dependent initialization must wait until Blender has fully
    # enabled the add-on and created its AddonPreferences instance.
    if not bpy.app.timers.is_registered(_post_register_init):
        bpy.app.timers.register(_post_register_init, first_interval=0.0)


def _print_addon_diagnostics():
    """
    Print Blender's current view of the Blue Hole add-on state.
    """

    global _diagnostics_printed

    if _diagnostics_printed:
        return

    _diagnostics_printed = True

    print("")
    print("------------------------------------------------------------")
    print("BLUE HOLE ADD-ON DIAGNOSTICS")
    print("------------------------------------------------------------")

    print("Root __name__:", repr(__name__))
    print("Root __package__:", repr(__package__))

    try:
        state = addon_utils.check("BlueHole")
        print('addon_utils.check("BlueHole"):', state)
    except Exception as exc:
        print('addon_utils.check("BlueHole") failed:', repr(exc))

    try:
        addon = bpy.context.preferences.addons.get("BlueHole")
        print('preferences.addons.get("BlueHole"):', addon)
    except Exception as exc:
        print('preferences.addons.get("BlueHole") failed:', repr(exc))

    print("")
    print("Preference add-on entries containing 'blue':")

    found_pref_entry = False

    try:
        for addon in bpy.context.preferences.addons:
            module_name = addon.module

            if "blue" in module_name.lower():
                found_pref_entry = True
                print(
                    "    module:",
                    repr(module_name),
                    "preferences:",
                    addon.preferences,
                )
    except Exception as exc:
        print("    Failed to enumerate preference add-ons:", repr(exc))

    if not found_pref_entry:
        print("    <none>")

    print("")
    print("addon_utils modules containing 'blue':")

    found_module = False

    try:
        for module in addon_utils.modules():
            module_name = getattr(module, "__name__", "")

            if "blue" in module_name.lower():
                found_module = True
                print(
                    "    module:",
                    repr(module_name),
                    "package:",
                    repr(getattr(module, "__package__", None)),
                )
    except Exception as exc:
        print("    Failed to enumerate addon_utils modules:", repr(exc))

    if not found_module:
        print("    <none>")

    print("------------------------------------------------------------")
    print("")


def _post_register_init():
    global _keymaps_registered

    from .preferences.prefs import prefs, addon_module_name

    print("Blue Hole: _post_register_init called")
    print("Blue Hole: prefs addon module name:", repr(addon_module_name()))

    p = prefs()
    ready = p.is_ready()

    print("Blue Hole: prefs ready:", ready)

    if not ready:
        _print_addon_diagnostics()

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
    global _diagnostics_printed

    # The post-register timer may still be waiting for preferences to become ready.
    if bpy.app.timers.is_registered(_post_register_init):
        bpy.app.timers.unregister(_post_register_init)

    if bpy.app.timers.is_registered(update_env_timer):
        bpy.app.timers.unregister(update_env_timer)

    if _keymaps_registered:
        keymaps_register.unregister()
        _keymaps_registered = False

    _diagnostics_printed = False

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