"""
Top-level registration and refresh management for Blue Hole operators.

This module orchestrates registration and unregistration of all operator modules.

Child operator modules are responsible for:
- registering their own Blender operator classes
- unregistering their own Blender operator classes

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

from ..Lib.commonUtils.debugUtils import *

from . import (
    add_ops,
    box_xray_ops,
    directory_ops,
    environment_ops,
    export_send_ops,
    external_addon_ops,
    food_ops,
    help_ops,
    import_ops,
    model_ops,
    music_ops,
    other_ops,
    save_ops,
    sort_ops,
    source_control_ops,
    theme_ops,
    transform_ops,
    ui_ops
)

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

TOOL_NAME = 'Operators'

# ----------------------------------------------------------------------------------------------------------------------
# MODULES

OPERATOR_MODULES = (
    add_ops,
    box_xray_ops,
    directory_ops,
    environment_ops,
    export_send_ops,
    external_addon_ops,
    food_ops,
    help_ops,
    import_ops,
    model_ops,
    music_ops,
    other_ops,
    save_ops,
    sort_ops,
    source_control_ops,
    theme_ops,
    transform_ops,
    ui_ops
)

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def _get_module_label(module) -> str:
    return module.__name__.split('.')[-1]

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
    log(Severity.INFO, TOOL_NAME, f'=== Registering {TOOL_NAME} ===')

    for module in OPERATOR_MODULES:
        module.register()
        log(Severity.DEBUG, TOOL_NAME, f'Registered: {_get_module_label(module)}')

    log(Severity.INFO, TOOL_NAME, 'Registration complete')


def unregister():
    log(Severity.INFO, TOOL_NAME, f'=== Unregistering {TOOL_NAME} ===')

    for module in reversed(OPERATOR_MODULES):
        module.unregister()
        log(Severity.DEBUG, TOOL_NAME, f'Unregistered: {_get_module_label(module)}')

    log(Severity.INFO, TOOL_NAME, 'Unregistration complete')
