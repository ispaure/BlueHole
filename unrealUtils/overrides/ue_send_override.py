"""
Code to trigger the Unreal Send Override, that calls in a custom function when specified by the user in lieu of
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


# ----------------------------------------------------------------------------------------------------------------------
# CODE

send_ue_name = 'Blue Hole Bridge to Unreal (Send Operator Override)'


def trigger_unreal_import_override(file_path_source: str) -> bool | set[str]:

    op_idname = prefs().bridge.ue_op_send_override.strip()

    if "." not in op_idname:
        log(Severity.CRITICAL, send_ue_name, f'Invalid operator idname: "{op_idname}"')
        raise ValueError(f'Invalid operator idname: "{op_idname}"')

    cat, op = op_idname.split(".", 1)

    try:
        res = getattr(getattr(bpy.ops, cat), op)(path=str(file_path_source))
    except Exception as e:
        log(
            Severity.CRITICAL,
            send_ue_name,
            f'Failed to run override operator "{op_idname}": {e}',
        )
        raise

    if res == {'CANCELLED'}:
        return {'CANCELLED'}

    return True
