"""
Directories Operators
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
import BlueHole.blenderUtils.fileUtils as fileUtils
import BlueHole.envUtils.projectOpenDirectory as envOpenDirectory
from BlueHole.blenderUtils.languageUtils import loc_str as loc_str
import BlueHole.wrappers.perforceWrapper as p4Wrapper
import BlueHole.blenderUtils.exportUtils2 as exportUtils2
import BlueHole.blenderUtils.filterUtils as filterUtils
import BlueHole.blenderUtils.addon as addon
import BlueHole.envUtils.envUtils2 as envUtils2


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class OpenFinalFolder(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_final"
    bl_label = loc_str('open_final_folder')
    bl_description = loc_str('open_final_folder_tt')

    def execute(self, context):
        envOpenDirectory.open_project_sub_dir('path_final')
        return {'FINISHED'}


class OpenReferencesFolder(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_references"
    bl_label = loc_str('open_references_folder')
    bl_description = loc_str('open_references_folder_tt')

    def execute(self, context):
        envOpenDirectory.open_project_sub_dir('path_references')
        return {'FINISHED'}


class OpenResourcesFolder(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_resources"
    bl_label = loc_str('open_resources_folder')
    bl_description = loc_str('open_resources_folder_tt')

    def execute(self, context):
        envOpenDirectory.open_project_sub_dir('path_resources')
        return {'FINISHED'}


class OpenRootFolder(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_root"
    bl_label = loc_str('open_root_folder')
    bl_description = loc_str('open_root_folder_tt')

    def execute(self, context):
        envOpenDirectory.open_project_sub_dir('path_root')
        return {'FINISHED'}


class OpenP4WorkspaceRootFolder(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_workspace_root"
    bl_label = loc_str('open_workspace_root_folder')
    bl_description = loc_str('open_workspace_root_folder_tt')

    def execute(self, context):
        # Initial checks
        check_result = filterUtils.check_tests('Open Workspace Root',
                                               check_source_control_enable=True,
                                               check_source_control_connection=True)
        if not check_result:
            return {'FINISHED'}

        # Open folder
        fileUtils.open_dir_path(p4Wrapper.P4Info().client_root)
        return {'FINISHED'}


class OpenSpeedTreeMeshesFolder(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_speedtree_msh"
    bl_label = loc_str('open_speedtree_msh_folder')
    bl_description = loc_str('open_speedtree_msh_folder_tt')

    def execute(self, context):
        envOpenDirectory.open_project_sub_dir('path_speedtree_msh')
        return {'FINISHED'}


class OpenUserResourcePath(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_user_resource"
    bl_label = loc_str('open_user_resource_path')
    bl_description = loc_str('open_user_resource_path_tt')

    def execute(self, context):
        appdata_path = fileUtils.get_resource_path_user()
        fileUtils.open_dir_path(appdata_path)
        return {'FINISHED'}


class OpenSourceContentPath(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_source_content_root_dir"
    bl_label = 'Open SOURCE CONTENT ROOT Folder'
    bl_description = 'Opens Source Content Root Path, as specified in the active environment\'s settings.'

    def execute(self, context):
        fileUtils.open_dir_path(envUtils2.get_valid_sc_path())
        return {'FINISHED'}


class OpenUnityAssetsPath(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_unity_assets_dir"
    bl_label = 'Open UNITY PROJECT ASSETS Folder'
    bl_description = 'Opens Unity Project\'s Assets Path, as specified in the active environment\'s settings.'

    def execute(self, context):
        if filterUtils.filter_platform('win'):
            fileUtils.open_dir_path(addon.preference().general.unity_assets_path)
        else:
            fileUtils.open_dir_path(addon.preference().general.unity_assets_path_mac)
        return {'FINISHED'}


class OpenUnityAssetsCurrentExportPath(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_unity_assets_current_exp_dir"
    bl_label = 'Open UNITY ASSETS CURRENT EXPORT Folder'
    bl_description = 'Opens Unity Project\'s Assets Path to the folder used for export.'

    def execute(self, context):
        result = filterUtils.check_tests('Open Directory',
                                         check_blend_exist=True,
                                         check_blend_loc_in_dir_structure=True,
                                         check_source_content_root_path_exist=True,
                                         check_blend_in_source_content=True,
                                         check_unity_assets_path_exist=True)
        if not result:
            return False
        else:
            fileUtils.open_dir_path(exportUtils2.get_unity_exp_path())
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (OpenFinalFolder,
           OpenReferencesFolder,
           OpenResourcesFolder,
           OpenRootFolder,
           OpenP4WorkspaceRootFolder,
           OpenSpeedTreeMeshesFolder,
           OpenUserResourcePath,
           OpenSourceContentPath,
           OpenUnityAssetsPath,
           OpenUnityAssetsCurrentExportPath
           )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators
