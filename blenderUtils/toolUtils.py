"""
Main point of contact for source control scripts. They might get redirected to the proper source control solutions
afterwards.
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

# Blue Hole
import bpy

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def tool_set(tool_id: str) -> bool:
    """
    Try to set a tool by id. Returns True if it succeeded, False otherwise.
    """
    try:
        # operator returns {'FINISHED'} or {'CANCELLED'}
        res = bpy.ops.wm.tool_set_by_id(name=tool_id)
        return 'FINISHED' in res
    except Exception:
        # Tool not found / not available in this build/context
        return False
