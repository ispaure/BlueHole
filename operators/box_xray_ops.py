"""
Operators that did not fit in another category
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

# Blender
import bpy
from bpy.props import *
from ..blenderUtils.toolUtils import tool_set
from ..Lib.commonUtils.debugUtils import *
from ..preferences.prefs import prefs

# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class WM_OT_BH_tool_select_box_xray(bpy.types.Operator):
    bl_idname = "wm.bh_tool_select_box_xray"
    bl_label = "Blue Hole: Selection Box"
    bl_description = "Set Select Box XRay tool if available, else Blender Select Box"

    def execute(self, context):

        # Prefer addon tool
        if prefs().keymap.selection.enable_selection_tool_switch_box_x_ray and tool_set("object_tool.select_box_xray"):
            return {'FINISHED'}

        tool_set("builtin.select_box")
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (
    WM_OT_BH_tool_select_box_xray,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
