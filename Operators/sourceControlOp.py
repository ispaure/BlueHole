"""
Operators for source control related things.
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS


import bpy
import BlueHole.blenderUtils.sourceControlUtils as scUtils
import BlueHole.wrappers.perforceWrapper as p4Wrapper


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class P4CheckOutCurrentScene(bpy.types.Operator):

    bl_idname = "wm.bh_p4_check_out_blend"
    bl_label = "Check Out Current Blend Scene"

    def execute(self, context):
        scUtils.sc_check_blend()
        return {'FINISHED'}


class P4DisplayServerInfo(bpy.types.Operator):

    bl_idname = "wm.bh_p4_display_server_info"
    bl_label = "Display Server Info"

    def execute(self, context):
        scUtils.sc_dialog_box_info()
        return {'FINISHED'}


class WM_OT_SetP4EnvSettings(bpy.types.Operator):
    """Set Perforce Environment Settings"""
    bl_idname = "wm.bh_set_p4_env_settings"
    bl_label = "Set Perforce Environment Settings"
    bl_options = {'INTERNAL'}

    def execute(self, _context):
        p4Wrapper.set_p4_env_settings()
        return {'FINISHED'}


class WM_OT_disabled_source_control(bpy.types.Operator):
    bl_idname = "wm.disabled_source_control"
    bl_label = "Source Control is Disabled!"
    bl_description = "Source Control is required for this button."

    open_prefs: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        self.report({'WARNING'}, "Source Control is not enabled for this Environment. Enable it in Preferences > Add-ons > Blue Hole.")
        if self.open_prefs:
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {'CANCELLED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (P4CheckOutCurrentScene,
           P4DisplayServerInfo,
           WM_OT_SetP4EnvSettings,
           WM_OT_disabled_source_control
           )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators
