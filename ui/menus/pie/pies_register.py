"""
Registration and runtime management for Blue Hole pie menus.
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
from ....debug.debug_flags import *

from . import (
    add_pies,
    curve_pies,
    directories_pies,
    global_pies,
    import_export_pies,
    mesh_pies,
    object_pies,
    sculpt_pies,
    source_control_pies,
    uv_pies,
)

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

TOOL_NAME = 'Pie Menus'

# ----------------------------------------------------------------------------------------------------------------------
# MODULES

PIE_MODULES = (
    add_pies,
    curve_pies,
    directories_pies,
    global_pies,
    import_export_pies,
    mesh_pies,
    object_pies,
    sculpt_pies,
    source_control_pies,
    uv_pies,
)

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def _get_module_name(module) -> str:
    return getattr(module, 'TOOL_NAME', module.__name__.split('.')[-1])

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
    log(Severity.DEBUG, TOOL_NAME, 'Registering Pie Menus...')

    for pie in PIE_MODULES:
        pie.register()
        log(Severity.DEBUG, TOOL_NAME, f'Registered: {_get_module_name(pie)} Pie Menus')

    log(Severity.DEBUG, TOOL_NAME, 'Registration of Pie Menus completed!')


def unregister():
    log(Severity.DEBUG, TOOL_NAME, 'Unregistering...')

    for pie in reversed(PIE_MODULES):
        pie.unregister()
        log(Severity.DEBUG, TOOL_NAME, f'Unregistered: {_get_module_name(pie)} Pie Menus')

    log(Severity.DEBUG, TOOL_NAME, 'Unregistration complete')
