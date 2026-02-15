"""
Operators for external addons. Mostly to display warnings if addon is missing (in Pie Menus)
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

# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class WM_OT_disabled_addon_interactive_tools(bpy.types.Operator):
    bl_idname = "wm.disabled_addon_interactive_tools"
    bl_label = "Interactive Tools add-on is not enabled"
    bl_description = "Interactive Tools add-on is required for this button"

    open_prefs: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        self.report({'WARNING'}, "Interactive Tools add-on is not enabled. Enable it in Preferences > Add-ons.")
        if self.open_prefs:
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {'CANCELLED'}


class WM_OT_disabled_addon_machin3tools(bpy.types.Operator):
    bl_idname = "wm.disabled_addon_machin3tools"
    bl_label = "Interactive Tools add-on is not enabled"
    bl_description = "Interactive Tools add-on is required for this button"

    open_prefs: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        self.report({'WARNING'}, "MACHIN3tools add-on is not enabled. Enable it in Preferences > Add-ons.")
        if self.open_prefs:
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {'CANCELLED'}


class WM_OT_disabled_addon_hardops(bpy.types.Operator):
    bl_idname = "wm.disabled_addon_hardops"
    bl_label = "HardOps add-on is not enabled"
    bl_description = "HardOps add-on is required for this button"

    open_prefs: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        self.report({'WARNING'}, "HardOps add-on is not enabled. Enable it in Preferences > Add-ons.")
        if self.open_prefs:
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {'CANCELLED'}


class WM_OT_disabled_addon_mesh_angle(bpy.types.Operator):
    bl_idname = "wm.disabled_addon_mesh_angle"
    bl_label = "Mesh Angle add-on is not enabled"
    bl_description = "Mesh Angle add-on is required for this button"

    open_prefs: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        self.report({'WARNING'}, "Mesh Angle add-on is not enabled. Enable it in Preferences > Add-ons.")
        if self.open_prefs:
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {'CANCELLED'}


class WM_OT_disabled_addon_dreamuv(bpy.types.Operator):
    bl_idname = "wm.disabled_addon_dreamuv"
    bl_label = "DreamUV add-on is not enabled"
    bl_description = "DreamUV add-on is required for this button"

    open_prefs: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        self.report({'WARNING'}, "DreamUV add-on is not enabled. Enable it in Preferences > Add-ons.")
        if self.open_prefs:
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {'CANCELLED'}


class WM_OT_disabled_addon_zen_uv(bpy.types.Operator):
    bl_idname = "wm.disabled_addon_zen_uv"
    bl_label = "Zen UV add-on is not enabled"
    bl_description = "Zen UV add-on is required for this button"

    open_prefs: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        self.report({'WARNING'}, "Zen UV add-on is not enabled. Enable it in Preferences > Add-ons.")
        if self.open_prefs:
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {'CANCELLED'}


class WM_OT_disabled_addon_uv_toolkit(bpy.types.Operator):
    bl_idname = "wm.disabled_addon_uv_toolkit"
    bl_label = "UV Toolkit add-on is not enabled"
    bl_description = "UV Toolkit add-on is required for this button"

    open_prefs: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        self.report({'WARNING'}, "UV Toolkit add-on is not enabled. Enable it in Preferences > Add-ons.")
        if self.open_prefs:
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {'CANCELLED'}


class ZUV_OT_trim_mode(bpy.types.Operator):
    bl_idname = "zuv.set_trim_tool"
    bl_label = "Trim Select Mode"

    def execute(self, context):

        # 1) Set Zen-UV tool mode via context toggle
        bpy.ops.wm.context_toggle(
            data_path="scene.zen_uv.ui.uv_tool.select_trim"
        )

        # 2) Activate the actual Zen-UV tool
        bpy.ops.wm.tool_set_by_id(name="zenuv.uv_tool")

        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (WM_OT_disabled_addon_interactive_tools,
           WM_OT_disabled_addon_machin3tools,
           WM_OT_disabled_addon_hardops,
           WM_OT_disabled_addon_mesh_angle,
           WM_OT_disabled_addon_dreamuv,
           WM_OT_disabled_addon_zen_uv,
           WM_OT_disabled_addon_uv_toolkit,
           ZUV_OT_trim_mode
           )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators
