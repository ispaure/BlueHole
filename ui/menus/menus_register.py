"""
Top-level registration and refresh management for Blue Hole menus.

This module orchestrates registration and unregistration of all menu modules.

Child menu modules are responsible for:
- registering their own menus
- unregistering their own menus

This module is responsible for:
- registration order
- centralized high-level logging
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

from ...Lib.commonUtils.debugUtils import *

from .custom import custom_menus_register
from .append import append_menus_register
from .override import override_menus_register
from .pie import pies_register

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

TOOL_NAME = 'Menus'

# ----------------------------------------------------------------------------------------------------------------------
# MODULES

MENU_MODULES = (
    custom_menus_register,
    append_menus_register,
    override_menus_register,
    pies_register,
)

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def _get_module_name(module) -> str:
    return getattr(module, 'TOOL_NAME', module.__name__.split('.')[-1])

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
    log(Severity.INFO, TOOL_NAME, f'=== Registering {TOOL_NAME} ===')

    for module in MENU_MODULES:
        module.register()
        log(Severity.INFO, TOOL_NAME, f'Registered: {_get_module_name(module)}')

    log(Severity.INFO, TOOL_NAME, 'Registration complete')


def unregister():
    log(Severity.INFO, TOOL_NAME, f'=== Unregistering {TOOL_NAME} ===')

    for module in reversed(MENU_MODULES):
        module.unregister()
        log(Severity.INFO, TOOL_NAME, f'Unregistered: {_get_module_name(module)}')

    log(Severity.INFO, TOOL_NAME, 'Unregistration complete')
