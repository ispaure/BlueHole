"""
Adds Blue Hole Blender Operators [Send]
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

import bpy
import BlueHole.blenderUtils.debugUtils as debugUtils
import BlueHole.envUtils.envUtils as envUtils
import BlueHole.blenderUtils.exportUtils2 as exportUtils2
import BlueHole.blenderUtils.configUtils as configUtils
import BlueHole.blenderUtils.fileUtils as fileUtils
import BlueHole.blenderUtils.uiUtils as uiUtils


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

# Start of File Debug Message
debugUtils.print_debug_msg('\nLoading Send Menu and Operators...', show_verbose)


# ----------------------------------------------------------------------------------------------------------------------
# MENUS

class BLUE_HOLE_MT_send(bpy.types.Menu):
    bl_label = "Send (to Game Engine)"

    def draw(self, context):
        layout = self.layout
        # These options are always available, regardless of active environment

        # Unity
        layout.operator(SendToUnityDoc.bl_idname, icon='KEYTYPE_EXTREME_VEC')
        layout.operator(SendAllHierarchiesToUnity.bl_idname, icon='UV_SYNC_SELECT')
        layout.operator(SendSelectedHierarchiesToUnity.bl_idname, icon='UV_SYNC_SELECT')

        layout.separator()

        # Unreal
        layout.operator(SendToUnrealDoc.bl_idname, icon='KEYTYPE_EXTREME_VEC')
        layout.operator(SendAllHierarchiesToUnreal.bl_idname, icon='UV_SYNC_SELECT')
        layout.operator(SendSelectedHierarchiesToUnreal.bl_idname, icon='UV_SYNC_SELECT')

        # Discontinued UVLayout Bridge for now (I don't really use it anymore)
        # show_label('UVLAYOUT', layout)
        # layout.operator(SendToUVLayoutNew.bl_idname, icon='UV_SYNC_SELECT')
        # layout.operator(SendToUVLayoutEdit.bl_idname, icon='UV_SYNC_SELECT')

        # Draw additional operators from the active environment (if available)
        envUtils.draw_current_env_menu_items('globalSend', layout)


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class SendToUnityDoc(bpy.types.Operator):

    bl_idname = "wm.bh_send_unity_doc"
    bl_label = '[[[[ ' + 'UNITY' + ' ]]]]'
    bl_description = 'Opens the Documentation for the Blender to Unity Bridge'

    def execute(self, context):
        fileUtils.open_url(configUtils.get_url_db_value('Tutorial', 'unity_bridge'))
        return{'FINISHED'}


class SendAllHierarchiesToUnity(bpy.types.Operator):
    bl_idname = "wm.bh_send_unity"
    bl_label = "Send *ALL* (Asset Hierarchies)"
    bl_description = 'Sends all asset hierarchies to Unity'

    def execute(self, context):
        # exportUtils.exp_obj_hierarchies_unity(selected_only=False)
        msg = 'Do you really want to send *ALL* Asset Hierarchies to Unity? Press OK to confirm.'
        state = uiUtils.show_dialog_box('Unity Export', msg)
        if state:
            exportUtils2.export_asset_hierarchies(selected_only=False,
                                                  preset='Unity',
                                                  is_send=True,
                                                  skip_sc=False)
        return {'FINISHED'}


class SendSelectedHierarchiesToUnity(bpy.types.Operator):
    bl_idname = "wm.bh_send_selected_unity"
    bl_label = "Send Selected (Asset Hierarchies)"
    bl_description = 'Sends selected asset hierarchies to Unity'

    def execute(self, context):
        exportUtils2.export_asset_hierarchies(selected_only=True,
                                              preset='Unity',
                                              is_send=True,
                                              skip_sc=False)
        return {'FINISHED'}


class SendToUnrealDoc(bpy.types.Operator):

    bl_idname = "wm.bh_send_unreal_doc"
    bl_label = '[[[[ ' + 'UNREAL' + ' ]]]]'
    bl_description = 'Opens the documentation for the Blender to Unreal Bridge'

    def execute(self, context):
        fileUtils.open_url(configUtils.get_url_db_value('Tutorial', 'unreal_bridge'))
        return{'FINISHED'}


class SendAllHierarchiesToUnreal(bpy.types.Operator):
    bl_idname = "wm.bh_send_unreal"
    bl_label = "Send *ALL* (Asset Hierarchies)"
    bl_description = 'Sends all asset hierarchies to Unreal'

    def execute(self, context):
        # exportUtils.exp_obj_hierarchies_unreal(selected_only=False, trigger_import_cmd=True)
        msg = 'Do you really want to send *ALL* Asset Hierarchies to Unreal? Press OK to confirm.'
        state = uiUtils.show_dialog_box('Unreal Export', msg)
        if state:
            exportUtils2.export_asset_hierarchies(selected_only=False,
                                                  preset='Unreal',
                                                  is_send=True,
                                                  skip_sc=False)
        return {'FINISHED'}


class SendSelectedHierarchiesToUnreal(bpy.types.Operator):
    bl_idname = "wm.bh_send_selected_unreal"
    bl_label = "Send Selected (Asset Hierarchies)"
    bl_description = 'Sends selected asset hierarchies to Unreal'

    def execute(self, context):
        # exportUtils.exp_obj_hierarchies_unreal(selected_only=True, trigger_import_cmd=True)
        exportUtils2.export_asset_hierarchies(selected_only=True,
                                              preset='Unreal',
                                              is_send=True,
                                              skip_sc=False)
        return {'FINISHED'}


class SendToUVLayoutNew(bpy.types.Operator):

    bl_idname = "wm.bh_send_uv_layout_new"
    bl_label = "Send to UVLayout (New)"

    def execute(self, context):
        bpy.data.window_managers["WinMan"].uvlBridgeProps.uvlb_mode = '0'
        bpy.ops.uvlbridge.props()
        return {'FINISHED'}


class SendToUVLayoutEdit(bpy.types.Operator):

    bl_idname = "wm.bh_send_uv_layout_edit"
    bl_label = "Send to UVLayout (Edit)"

    def execute(self, context):
        bpy.data.window_managers["WinMan"].uvlBridgeProps.uvlb_mode = '1'
        bpy.ops.uvlbridge.props()
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (SendToUVLayoutNew,
           SendToUnrealDoc,
           SendToUnityDoc,
           SendToUVLayoutEdit,
           SendAllHierarchiesToUnity,
           SendSelectedHierarchiesToUnity,
           SendAllHierarchiesToUnreal,
           SendSelectedHierarchiesToUnreal
           )


# Register
def register():
    # Register Menu
    bpy.utils.register_class(BLUE_HOLE_MT_send)
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    # Unregister Menu
    bpy.utils.unregister_class(BLUE_HOLE_MT_send)
    # Unregister Operators
    for cls in classes:
        bpy.utils.unregister_class(cls)


# ----------------------------------------------------------------------------------------------------------------------
# End of File Debug Message
debugUtils.print_debug_msg('Send Menu and Operators Loaded!', show_verbose)
