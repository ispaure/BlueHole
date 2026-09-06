"""
Directories Operators
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
from pathlib import Path

# Blue Hole
from ..blenderUtils import blenderFile, projectUtils, filterUtils
from ..environment import envPathResolver
from ..preferences.prefs import *
from ..Lib.commonUtils import dirUtils
from ..Lib.commonUtils.osUtils import get_os, OS
from ..wrappers.sourceContentPath import get_valid_source_content_path
from ..wrappers.perforce.p4_info import P4Info

# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class OpenFinalFolder(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_final"
    bl_label = 'Open FINAL Folder'
    bl_description = 'Open FINAL Project Folder'

    def execute(self, context):
        projectUtils.open_project_sub_dir(prefs().directory.sc_dir_struct_final)
        return {'FINISHED'}


class OpenReferencesFolder(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_references"
    bl_label = 'Open REFERENCE Folder'
    bl_description = 'Open REFERENCE Project Folder'

    def execute(self, context):
        projectUtils.open_project_sub_dir(prefs().directory.sc_dir_struct_ref)
        return {'FINISHED'}


class OpenResourcesFolder(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_resources"
    bl_label = 'Open RESOURCE Folder'
    bl_description = 'Open RESOURCE Project Folder'

    def execute(self, context):
        projectUtils.open_project_sub_dir(prefs().directory.sc_dir_struct_resources)
        return {'FINISHED'}


class OpenSceneFolder(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_scene"
    bl_label = 'Open SCENE Folder'
    bl_description = 'Open SCENE Project Folder'

    def execute(self, context):
        projectUtils.open_project_sub_dir(prefs().directory.sc_dir_struct_scenes)
        return {'FINISHED'}


class OpenP4WorkspaceRootFolder(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_workspace_root"
    bl_label = 'Open WORKSPACE ROOT Folder'
    bl_description = 'Open WORKSPACE ROOT Folder'

    def execute(self, context):
        # Initial checks
        check_result = filterUtils.check_tests('Open Workspace Root',
                                               check_source_control_enable=True,
                                               check_source_control_connection=True)
        if not check_result:
            return {'FINISHED'}

        # Open folder
        dirUtils.Directory(P4Info().client_root).open()
        return {'FINISHED'}


class OpenSpeedTreeMeshesFolder(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_speedtree_msh"
    bl_label = 'Open SPEEDTREE MSH Folder'
    bl_description = 'Open SPEEDTREE MSH Project Folder'

    def execute(self, context):
        projectUtils.open_project_sub_dir(prefs().directory.sc_dir_struct_st)
        return {'FINISHED'}


class OpenUserResourcePath(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_user_resource"
    bl_label = 'Open USER RESOURCE Folder'
    bl_description = 'Open USER RESOURCE Folder'

    def execute(self, context):
        appdata_path = blenderFile.get_resource_path_user()
        dirUtils.Directory(appdata_path).open()
        return {'FINISHED'}


class OpenSourceContentPath(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_source_content_root_dir"
    bl_label = 'Open SOURCE CONTENT ROOT Folder'
    bl_description = 'Opens Source Content Root Path, as specified in the active environment\'s settings.'

    def execute(self, context):
        valid_sc_path = get_valid_source_content_path()
        if valid_sc_path:
            dirUtils.Directory(valid_sc_path).open()
        return {'FINISHED'}


class OpenUnityAssetsPath(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_unity_assets_dir"
    bl_label = 'Open UNITY PROJECT ASSETS Folder'
    bl_description = 'Opens Unity Project\'s Assets Path, as specified in the active environment\'s settings.'

    def execute(self, context):
        unity_assets_path_os_dict = {
            OS.WIN: prefs().bridge.unity_assets_path,
            OS.MAC: prefs().bridge.unity_assets_path_mac,
            OS.LINUX: prefs().bridge.unity_assets_path_linux
        }
        dirUtils.Directory(Path(unity_assets_path_os_dict[get_os()])).open()
        return {'FINISHED'}


class OpenGodotProjectRootPath(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_godot_project_root_dir"
    bl_label = 'Open GODOT PROJECT ROOT Folder'
    bl_description = 'Opens Godot\'s Project Root Folder, as specified in the active environment\'s settings.'

    def execute(self, context):
        godot_project_root_path = {
            OS.WIN: prefs().bridge.godot_project_root_path,
            OS.MAC: prefs().bridge.godot_project_root_path_mac,
            OS.LINUX: prefs().bridge.godot_project_root_path_linux
        }
        dirUtils.Directory(Path(godot_project_root_path[get_os()])).open()
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
            unity_exp_dir_path = envPathResolver.get_unity_exp_dir_path()
            if unity_exp_dir_path:
                dirUtils.Directory(unity_exp_dir_path).open()
        return {'FINISHED'}


class OpenGodotCurrentExportPath(bpy.types.Operator):

    bl_idname = "wm.bh_dir_open_godot_current_exp_dir"
    bl_label = 'Open GODOT CURRENT EXPORT Folder'
    bl_description = 'Opens Godot Project\'s Path to the folder used for export.'

    def execute(self, context):
        result = filterUtils.check_tests('Open Directory',
                                         check_blend_exist=True,
                                         check_blend_loc_in_dir_structure=True,
                                         check_source_content_root_path_exist=True,
                                         check_blend_in_source_content=True,
                                         check_godot_project_root_path_exist=True)
        if not result:
            return False
        else:
            godot_exp_dir_path = envPathResolver.get_godot_exp_dir_path()
            if godot_exp_dir_path:
                dirUtils.Directory(godot_exp_dir_path).open()
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (OpenFinalFolder,
           OpenReferencesFolder,
           OpenResourcesFolder,
           OpenSceneFolder,
           OpenP4WorkspaceRootFolder,
           OpenSpeedTreeMeshesFolder,
           OpenUserResourcePath,
           OpenSourceContentPath,
           OpenUnityAssetsPath,
           OpenGodotProjectRootPath,
           OpenUnityAssetsCurrentExportPath,
           OpenGodotCurrentExportPath
           )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators
