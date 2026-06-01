"""
Code to trigger the Unreal Execute Code Override, that calls in a custom function when specified by the user in lieu of
Blue Hole's vanilla way of executing Unreal code. Offers freedom for use within a studio environment with custom
Unreal setup.
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

import bpy

from ...Lib.commonUtils.debugUtils import *
from ...preferences.prefs import prefs
from .ue_override_utils import run_unreal_override_operator

# ----------------------------------------------------------------------------------------------------------------------
# CODE

exec_code_ue_name = 'Blue Hole Bridge to Unreal (Execute Code Operator Override)'


def run_unreal_python_commands_override(code: str) -> bool:
    return run_unreal_override_operator(
        op_idname=prefs().bridge.ue_op_exec_code_override,
        log_name=exec_code_ue_name,
        operator_kwargs={
            "code": str(code),
        },
    )
