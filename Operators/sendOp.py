"""
Operators for send to engines
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
from BlueHole.blenderUtils.exportSettings import *
import BlueHole.blenderUtils.exportHierarchy as exportHierarchy
import BlueHole.blenderUtils.uiUtils as uiUtils


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class SendAllHierarchiesToUnity(bpy.types.Operator):
    bl_idname = "wm.bh_send_unity"
    bl_label = "Send *ALL* (Asset Hierarchies)"
    bl_description = 'Sends all asset hierarchies to Unity'

    def execute(self, context):
        # exportUtils.exp_obj_hierarchies_unity(selected_only=False)
        msg = 'Do you really want to send *ALL* Asset Hierarchies to Unity? Press OK to confirm.'
        state = uiUtils.show_prompt('Unity Export', msg)
        if state:
            # Get Unity Export Profile
            export_settings = export_settings_dict[ExportSettingsPreset.UNITY]
            asset_hierarchies = exportHierarchy.AssetHierarchies(export_settings)
            asset_hierarchies.set_hierarchies_from_scene()
            asset_hierarchies.export(send=True, skip_sc=False)
        return {'FINISHED'}


class SendSelectedHierarchiesToUnity(bpy.types.Operator):
    bl_idname = "wm.bh_send_selected_unity"
    bl_label = "Send Selected (Asset Hierarchies)"
    bl_description = 'Sends selected asset hierarchies to Unity'

    def execute(self, context):
        # Get Unity Export Profile
        export_settings = export_settings_dict[ExportSettingsPreset.UNITY]
        asset_hierarchies = exportHierarchy.AssetHierarchies(export_settings)
        asset_hierarchies.set_hierarchies_from_selection()
        asset_hierarchies.export(send=True, skip_sc=False)
        return {'FINISHED'}


class SendAllHierarchiesToUnreal(bpy.types.Operator):
    bl_idname = "wm.bh_send_unreal"
    bl_label = "Send *ALL* (Asset Hierarchies)"
    bl_description = 'Sends all asset hierarchies to Unreal'

    def execute(self, context):
        # exportUtils.exp_obj_hierarchies_unreal(selected_only=False, trigger_import_cmd=True)
        msg = 'Do you really want to send *ALL* Asset Hierarchies to Unreal? Press OK to confirm.'
        state = uiUtils.show_prompt('Unreal Export', msg)
        if state:
            # Get Unreal Export Profile
            export_settings = export_settings_dict[ExportSettingsPreset.UNREAL]
            asset_hierarchies = exportHierarchy.AssetHierarchies(export_settings)
            asset_hierarchies.set_hierarchies_from_scene()
            asset_hierarchies.export(send=True, skip_sc=False)
        return {'FINISHED'}


class SendSelectedHierarchiesToUnreal(bpy.types.Operator):
    bl_idname = "wm.bh_send_selected_unreal"
    bl_label = "Send Selected (Asset Hierarchies)"
    bl_description = 'Sends selected asset hierarchies to Unreal'

    def execute(self, context):
        # Get Unreal Export Profile
        export_settings = export_settings_dict[ExportSettingsPreset.UNREAL]
        asset_hierarchies = exportHierarchy.AssetHierarchies(export_settings)
        asset_hierarchies.set_hierarchies_from_selection()
        asset_hierarchies.export(send=True, skip_sc=False)
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (SendAllHierarchiesToUnity,
           SendSelectedHierarchiesToUnity,
           SendAllHierarchiesToUnreal,
           SendSelectedHierarchiesToUnreal
           )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators
