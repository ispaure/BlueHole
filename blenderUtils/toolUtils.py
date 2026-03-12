"""
Utility functions for setting Blender tools.
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

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def tool_set(tool_id: str) -> bool:
    """
    Attempt to set a Blender tool by ID.

    :param tool_id: Tool identifier
    :return: True if the tool was successfully activated, otherwise False
    """
    try:
        # Operator returns {'FINISHED'} or {'CANCELLED'}
        res = bpy.ops.wm.tool_set_by_id(name=tool_id)
        return 'FINISHED' in res
    except Exception:
        # Tool not found or unavailable in the current build/context
        return False
