"""
Registration and runtime management for Blue Hole override menus.
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
    file_menu_override
)

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

TOOL_NAME = 'Override Menus'

# ----------------------------------------------------------------------------------------------------------------------
# MODULES

OVERRIDE_MENU_MODULES = (
    file_menu_override,
)

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def _get_module_label(module) -> str:
    return module.__name__.split('.')[-1]

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
    log(Severity.DEBUG, TOOL_NAME, 'Registering...')

    for menu in OVERRIDE_MENU_MODULES:
        menu.register()
        log(Severity.DEBUG, TOOL_NAME, f'Registered: {_get_module_label(menu)}')

    log(Severity.DEBUG, TOOL_NAME, 'Registration complete')


def unregister():
    log(Severity.DEBUG, TOOL_NAME, 'Unregistering...')

    for menu in reversed(OVERRIDE_MENU_MODULES):
        menu.unregister()
        log(Severity.DEBUG, TOOL_NAME, f'Unregistered: {_get_module_label(menu)}')

    log(Severity.DEBUG, TOOL_NAME, 'Unregistration complete')
