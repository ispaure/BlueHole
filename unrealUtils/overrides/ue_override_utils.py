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
    """
    Execute a configured Blender operator used as an Unreal override.

    The configured operator is validated before execution:
        - The operator IDName must use the expected "category.operator" format.
        - The operator must exist in bpy.ops.
        - Every supplied keyword argument must exist as a Blender RNA property.
        - Each supplied argument must match the expected Blender RNA property type.

    Configuration or execution errors are logged as CRITICAL and return False.
    A correctly configured operator returning CANCELLED, None, or another
    non-FINISHED result is treated as a normal override failure and returns False.
    """
    op_idname = op_idname.strip()

    if not op_idname or "." not in op_idname:
        msg = f'Invalid override operator IDName: "{op_idname}"'
        log(Severity.CRITICAL, log_name, msg)
        return False

    try:
        category_name, operator_name = op_idname.split(".", 1)

        if not category_name or not operator_name:
            raise ValueError(
                f'Operator IDName must use the format "category.operator", got "{op_idname}".'
            )

        operator_category = getattr(bpy.ops, category_name)
        operator = getattr(operator_category, operator_name)

        _validate_operator_kwargs(
            operator=operator,
            op_idname=op_idname,
            operator_kwargs=operator_kwargs,
        )

        result = operator(**operator_kwargs)

    except (AttributeError, ValueError, TypeError, RuntimeError) as exc:
        log(
            Severity.CRITICAL,
            log_name,
            (
                f'Override operator "{op_idname}" is invalid or could not be executed.\n\n'
                f'Arguments: {operator_kwargs}\n\n'
                f'Error: {exc}'
            ),
        )
        return False

    if result == {'FINISHED'}:
        return True

    if result == {'CANCELLED'}:
        log(Severity.WARNING, log_name, f'Override operator "{op_idname}" returned CANCELLED.')
        return False

    if result is None:
        log(Severity.WARNING, log_name, f'Override operator "{op_idname}" returned None.')
        return False

    log(Severity.WARNING, log_name, f'Override operator "{op_idname}" returned unexpected result: {result}')
    return False


def _validate_operator_kwargs(*, operator, op_idname: str, operator_kwargs: dict) -> None:
    """
    Validate keyword arguments against the configured Blender operator's RNA properties.

    Raises:
        RuntimeError:
            If a required property is missing from the operator.

        TypeError:
            If a supplied Python value does not match the operator property's RNA type,
            or if the Python value type is not supported by this validation helper.
    """
    rna_type = operator.get_rna_type()
    operator_properties = {
        prop.identifier: prop
        for prop in rna_type.properties
    }

    for property_name, value in operator_kwargs.items():
        prop = operator_properties.get(property_name)

        if prop is None:
            raise RuntimeError(
                f'Override operator "{op_idname}" is missing required property "{property_name}".'
            )

        expected_rna_type = _get_expected_rna_type(value)

        if prop.type != expected_rna_type:
            raise TypeError(
                f'Override operator "{op_idname}" property "{property_name}" must be '
                f'{expected_rna_type}, but its Blender RNA type is "{prop.type}".'
            )


def _get_expected_rna_type(value) -> str:
    """
    Return the Blender RNA property type expected for a Python value.

    bool is checked before int because bool is a subclass of int in Python.
    """
    if isinstance(value, bool):
        return 'BOOLEAN'

    if isinstance(value, str):
        return 'STRING'

    if isinstance(value, int):
        return 'INT'

    if isinstance(value, float):
        return 'FLOAT'

    raise TypeError(
        f'Unsupported override argument type "{type(value).__name__}". '
        f'Supported types are str, bool, int, and float.'
    )
