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


class WM_OT_BH_tool_select_box_xray_object(bpy.types.Operator):
    bl_idname = "wm.bh_tool_select_box_xray_object"
    bl_label = "Blue Hole: Selection Box (Object)"
    bl_description = "Set Select Box XRay tool if available, else Blender Select Box"

    def execute(self, context):

        # Prefer addon tool
        if prefs().thirdparty.x_ray_selection_tools.enable_selection_tool_switch_box_x_ray and tool_set("object_tool.select_box_xray"):
            return {'FINISHED'}

        tool_set("builtin.select_box")
        return {'FINISHED'}


class WM_OT_BH_tool_select_box_xray_mesh(bpy.types.Operator):
    bl_idname = "wm.bh_tool_select_box_xray_mesh"
    bl_label = "Blue Hole: Selection Box (Mesh)"
    bl_description = "Set Select Box XRay tool if available, else Blender Select Box"

    def execute(self, context):

        # Prefer addon tool
        if prefs().thirdparty.x_ray_selection_tools.enable_selection_tool_switch_box_x_ray and tool_set("mesh_tool.select_box_xray"):
            return {'FINISHED'}

        tool_set("builtin.select_box")
        return {'FINISHED'}


class WM_OT_BH_tool_select_box_xray_curve(bpy.types.Operator):
    bl_idname = "wm.bh_tool_select_box_xray_curve"
    bl_label = "Blue Hole: Selection Box (Curve)"
    bl_description = "Set Select Box XRay tool if available, else Blender Select Box"

    def execute(self, context):
        tool_set("builtin.select_box")
        return {'FINISHED'}


class WM_OT_BH_tool_select_box_xray_curves(bpy.types.Operator):
    bl_idname = "wm.bh_tool_select_box_xray_curves"
    bl_label = "Blue Hole: Selection Box (Curves)"
    bl_description = "Set Select Box XRay tool if available, else Blender Select Box"

    def execute(self, context):
        tool_set("builtin.select_box")
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (
    WM_OT_BH_tool_select_box_xray_object,
    WM_OT_BH_tool_select_box_xray_mesh,
    WM_OT_BH_tool_select_box_xray_curve,
    WM_OT_BH_tool_select_box_xray_curves,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
