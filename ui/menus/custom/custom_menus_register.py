"""
Registration and runtime management for Blue Hole custom menus.

This module orchestrates registration and unregistration of all custom menu modules,
including the Blue Hole header menu.
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

from ....Lib.commonUtils.debugUtils import *

from . import (
    containers_menu,
    directories_menu,
    export_send_menus,
    food_menu,
    help_menu,
    import_menu,
    misc_menu,
    music_menu,
    sort_menu,
    source_control_menu,
    theme_menu,
    update_menus,
    header_menu,
)

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

TOOL_NAME = 'Custom Menus'

# ----------------------------------------------------------------------------------------------------------------------
# MODULES

CUSTOM_MENU_MODULES = (
    containers_menu,
    directories_menu,
    export_send_menus,
    food_menu,
    help_menu,
    import_menu,
    misc_menu,
    music_menu,
    sort_menu,
    source_control_menu,
    theme_menu,
    update_menus,
)

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def _get_module_label(module) -> str:
    return module.__name__.split('.')[-1]

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
    log(Severity.DEBUG, TOOL_NAME, 'Registering...')

    for menu in CUSTOM_MENU_MODULES:
        menu.register()
        log(Severity.DEBUG, TOOL_NAME, f'Registered: {_get_module_label(menu)}')

    header_menu.register()
    log(Severity.DEBUG, TOOL_NAME, f'Registered: {_get_module_label(header_menu)}')

    log(Severity.DEBUG, TOOL_NAME, 'Registration complete')


def unregister():
    log(Severity.DEBUG, TOOL_NAME, 'Unregistering...')

    header_menu.unregister()
    log(Severity.DEBUG, TOOL_NAME, f'Unregistered: {_get_module_label(header_menu)}')

    for menu in reversed(CUSTOM_MENU_MODULES):
        menu.unregister()
        log(Severity.DEBUG, TOOL_NAME, f'Unregistered: {_get_module_label(menu)}')

    log(Severity.DEBUG, TOOL_NAME, 'Unregistration complete')
