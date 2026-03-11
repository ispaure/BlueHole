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


class WM_OT_unsupported_os(bpy.types.Operator):
    bl_idname = "wm.unsupported_os"
    bl_label = "Unsupported OS!"
    bl_description = "This button is unsupported on this platform!"

    open_prefs: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        msg = "Button is unsupported on this platform!"
        self.report({'WARNING'}, msg)
        return {'CANCELLED'}


class BH_OT_disabled_notice(bpy.types.Operator):
    bl_idname = "wm.bh_disabled_notice"
    bl_label = "Disabled"
    bl_description = "Disabled"

    def execute(self, context):
        return {'CANCELLED'}


class BH_OT_addon_missing(bpy.types.Operator):
    bl_idname = "wm.bh_addon_missing"
    bl_label = "Add-on Missing"
    bl_description = "An add-on is missing"

    def execute(self, context):
        msg = "Addon is not enabled or available. Get the missing addon and enable it in Preferences > Add-ons."
        self.report({'WARNING'}, msg)
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
classes = (WM_OT_unsupported_os,
           BH_OT_addon_missing,
           BH_OT_disabled_notice,
           ZUV_OT_trim_mode
           )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators
