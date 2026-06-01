"""
Shared utilities for Unreal override operators.
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

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def run_unreal_override_operator(*, op_idname: str, log_name: str, operator_kwargs: dict) -> bool:
    op_idname = op_idname.strip()

    if "." not in op_idname:
        msg = f'Invalid operator idname: "{op_idname}"'
        log(Severity.CRITICAL, log_name, msg)
        raise ValueError(msg)

    cat, op = op_idname.split(".", 1)

    try:
        res = getattr(getattr(bpy.ops, cat), op)(**operator_kwargs)
    except Exception as e:
        log(
            Severity.CRITICAL,
            log_name,
            f'Failed to run override operator "{op_idname}": {e}',
        )
        raise

    if res == {'CANCELLED'}:
        log(Severity.WARNING, log_name, f'Override operator "{op_idname}" returned CANCELLED.')
        return False

    if res == {'FINISHED'}:
        return True

    if res is None:
        log(Severity.WARNING, log_name, f'Override operator "{op_idname}" returned None.')
        return False

    log(Severity.WARNING, log_name, f'Override operator "{op_idname}" returned unexpected result: {res}')
    return False
