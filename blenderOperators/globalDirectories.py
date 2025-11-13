"""
Adds Blue Hole Blender Operators [Directories]
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
import os
import BlueHole.blenderUtils.fileUtils as fileUtils
import BlueHole.envUtils.projectOpenDirectory as envOpenDirectory
import BlueHole.blenderUtils.debugUtils as debugUtils
from BlueHole.blenderUtils.languageUtils import loc_str as loc_str
import BlueHole.blenderUtils.objectUtils as objectUtils
from BlueHole.blenderUtils.uiUtils import show_label as show_label
import BlueHole.envUtils.envUtils as envUtils
import BlueHole.wrappers.perforceWrapper as p4Wrapper
import BlueHole.blenderUtils.exportUtils2 as exportUtils2
import BlueHole.blenderUtils.filterUtils as filterUtils
import BlueHole.blenderUtils.addon as addon
import BlueHole.envUtils.envUtils2 as envUtils2


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

# Start of File Debug Message
debugUtils.print_debug_msg('\nLoading Directories Menu and Operators...', show_verbose)


# ----------------------------------------------------------------------------------------------------------------------
# MENUS

# Directories Menu
class BLUE_HOLE_MT_directories(bpy.types.Menu):
    bl_label = loc_str('directory_and_hierarchy')

    def draw(self, context):
        layout = self.layout
        layout.operator(SceneAddAssetHierarchy.bl_idname, icon='OUTLINER')

        # Environment Folders
        test_a = os.path.exists(addon.preference().environment.sc_path) or os.path.exists(addon.preference().environment.sc_path_alternate) or os.path.exists(addon.preference().environment.sc_path_mac) or os.path.exists(addon.preference().environment.sc_path_mac_alternate)
        test_b = os.path.exists(addon.preference().general.unity_assets_path) or os.path.exists(addon.preference().general.unity_assets_path_mac)
        test_c = addon.preference().sourcecontrol.source_control_enable and addon.preference().sourcecontrol.source_control_solution == 'perforce'
        if test_a or test_b or test_c:
            layout.separator()
            show_label('ENVIRONMENT', layout)
            if test_a:
                layout.operator(OpenSourceContentPath.bl_idname, icon='FILE_FOLDER')
            if test_b:
                layout.operator(OpenUnityAssetsPath.bl_idname, icon='FILE_FOLDER')
            if test_c:
                layout.operator(OpenP4WorkspaceRootFolder.bl_idname, icon='FILE_FOLDER')

        layout.separator()
        show_label('SOURCE ASSET', layout)
        layout.operator(OpenRootFolder.bl_idname, icon='FILE_FOLDER')
        layout.operator(OpenReferencesFolder.bl_idname, icon='FILE_FOLDER')
        layout.operator(OpenResourcesFolder.bl_idname, icon='FILE_FOLDER')
        layout.operator(OpenSpeedTreeMeshesFolder.bl_idname, icon='FILE_FOLDER')
        layout.operator(OpenFinalFolder.bl_idname, icon='FILE_FOLDER')
        layout.separator()
        show_label('CONFIG', layout)
        layout.operator(OpenUserResourcePath.bl_idname, icon='FILE_FOLDER')
        # Draw additional operators from the active environment (if available)
        envUtils.draw_current_env_menu_items('globalDirectories', layout)


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class SceneAddAssetHierarchy(bpy.types.Operator):

    bl_idname = "wm.bh_scene_add_asset_hierarchy"
    bl_label = "Add Asset Hierarchy"
    bl_description = 'Add Asset Hierarchy of given name to scene, in which objects are placed.'

    settings: bpy.props.EnumProperty(
        name = 'Settings',
        description = 'Settings to display',
        items = [('NAMEGEN', 'Easy Name Generator', 'Creates hierarchy name matching naming convention, preventing user error.'),
                 ('MANUAL', 'Manual Name Entry', 'Creates hierarchy matching user-given name, regardless if it matches naming conventions or not.')],
        default = 'NAMEGEN')

    preview: bpy.props.EnumProperty(name='Preview',items=[('PREVIEW', 'Preview', 'Preview name of Hierarchies that will be created.')], default='PREVIEW')

    # TYPE and their index position (see env_variables.ini > ObjectHierarchyStructure > prefixes)
    hierarchy_types = {'Mesh Asset': 0, 'Mesh Kit Asset': 1, 'Skeletal Mesh': 2}
    prefix_items = []
    for key in hierarchy_types.keys():
        prefix_items.append((key, key, ''))
    asset_type: bpy.props.EnumProperty(name='Type',
                                        description='The selected type of mesh. Affects the hierarchy name\'s prefix',
                                        items=prefix_items)

    # NAME
    asset_name: bpy.props.StringProperty(name='Name',
                                          description='Name of the asset for which the hierarchy is created. Will be the center part of the hierarchy name',
                                          default='InsertName')

    # VERSION BATCH
    version_batch: bpy.props.BoolProperty(name='Batch',
                                           description='When enabled, allows the creation of multiple hierarchies in one go',
                                           default=False)

    # VERSION (SINGLE)
    version_suffix: bpy.props.IntProperty(name='Number',
                                           description='Version (number) of the hierarchy. Affects the hierarchy name\'s suffix',
                                           default=1)

    # VERSION SUFFIX_START
    version_suffix_start: bpy.props.IntProperty(name='Number (Start)',
                                                 description='When using batch mode, defines the first version (number) to create',
                                                 default=1)

    # VERSION SUFFIX_END
    version_suffix_end: bpy.props.IntProperty(name='Number (End)',
                                               description='When using batch mode, defines the last version (number) to create',
                                               default=1)

    # VERSION (LETTER)
    version_suffix_letter: bpy.props.StringProperty(name='Letter',
                                                     description='Letter(s) suffix at end-of-name.',
                                                     default='')

    # INCLUDE DEFAULT MESH
    include_default_mesh: bpy.props.BoolProperty(name='Include Default Mesh',
                                                  description='Whether to include the default icosphere mesh as part of the hierarchy',
                                                  default=False)

    # DISPLAY EMPTY OBJECTS AS ARROWS
    dsp_empty_obj_arrows: bpy.props.BoolProperty(name='Display as Arrows',
                                                  description='When set to true, display Empty Objects as XYZ Arrows',
                                                  default=True)

    # INCLUDE SELECTED OBJECTS
    include_selected_obj: bpy.props.BoolProperty(name='Include Selection in Render',
                                                  description='Whether to parent currently selected objects as part of the hierarchy.',
                                                  default=True)

    def execute(self, context):
        objectUtils.add_asset_hierarchy(self.result_hierarchy_lst(),
                                        self.include_default_mesh,
                                        self.include_selected_obj,
                                        self.dsp_empty_obj_arrows)
        return {'FINISHED'}

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        column = layout.column(align=True)
        row = column.row(align=True)
        row.prop(self, 'settings', expand=True)

        # DISPLAY PARAMETERS

        # Easy Name Generator Specific
        if self.settings == 'NAMEGEN':
            # Create box for prefix
            box = layout.box()
            box.label(text='Prefix')
            column = box.column()
            row = column.row()
            row.prop(self, "asset_type")

        box = layout.box()
        box.label(text='Name')
        column = box.column()
        row = column.row()
        row.prop(self, "asset_name")

        # Easy Name Generator Specific
        if self.settings == 'NAMEGEN':
            # Create box for suffix
            box = layout.box()
            box.label(text='Suffix')
            column = box.column()
            row = column.row()
            row.prop(self, "version_batch")
            if self.version_batch:
                row = column.row()
                row.prop(self, "version_suffix_start")
                row = column.row()
                row.prop(self, "version_suffix_end")
            else:
                row = column.row()
                row.prop(self, "version_suffix")
                row = column.row()
                row.prop(self, "version_suffix_letter")

        # DISPLAY LIST OF HIERARCHIES TO CREATE
        hierarchy_to_create_lst = self.result_hierarchy_lst()
        box = layout.box()
        column = box.column()

        row = column.row()
        row.prop(self, 'preview', expand=True)
        box.label(text=hierarchy_to_create_lst[0])
        if addon.preference().environment.create_element_render:
            box.label(text='   ↳ ' + addon.preference().environment.asset_hierarchy_empty_object_meshes)
        if addon.preference().environment.create_element_collision:
            box.label(text='   ↳ ' + addon.preference().environment.asset_hierarchy_empty_object_collisions)
        if addon.preference().environment.create_element_sockets:
            box.label(text='   ↳ ' + addon.preference().environment.asset_hierarchy_empty_object_sockets)
        if len(hierarchy_to_create_lst) > 1:
            row = column.row()
            box.label(text='...')
            row = column.row()
            box.label(text=hierarchy_to_create_lst[-1])

        # DISPLAY ADVANCED OPTIONS
        box = layout.box()
        box.label(text='Advanced Options')
        column = box.column()
        row = column.row()
        row.prop(self, "include_default_mesh")
        row.prop(self, "dsp_empty_obj_arrows")
        row = column.row()
        if len(hierarchy_to_create_lst) == 1 and addon.preference().environment.create_element_render:
            row.prop(self, 'include_selected_obj')

        # for hierarchy in hierarchy_to_create_lst:
        #     row = column.row()
        #     box.label(text=hierarchy)

    def result_hierarchy_lst(self):
        """
        Find full name of hierarchies to create, from given parameters.
        """
        result_hierarchy_lst = []
        if self.settings == 'NAMEGEN':
            if self.version_batch:
                for item in range(self.version_suffix_start, self.version_suffix_end + 1):
                    result_hierarchy_name = ''
                    for key, value in self.hierarchy_types.items():
                        if key in self.asset_type:
                            result_hierarchy_name += exportUtils2.get_hierarchy_prefix_lst()[value]
                    result_hierarchy_name += self.asset_name
                    result_hierarchy_name += '_' + str(format(item, '02'))
                    result_hierarchy_lst.append(result_hierarchy_name)
            else:
                result_hierarchy_name = ''
                for key, value in self.hierarchy_types.items():
                    if key in self.asset_type:
                        result_hierarchy_name += exportUtils2.get_hierarchy_prefix_lst()[value]
                result_hierarchy_name += self.asset_name
                result_hierarchy_name += '_' + str(format(self.version_suffix, '02'))
                if len(self.version_suffix_letter) > 0:
                    result_hierarchy_name += '' + self.version_suffix_letter
                result_hierarchy_lst.append(result_hierarchy_name)
        elif self.settings == 'MANUAL':
            result_hierarchy_lst.append(self.asset_name)

        # Return list of hierarchies
        return result_hierarchy_lst

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


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
classes = (SceneAddAssetHierarchy,
           OpenFinalFolder,
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


# Register
def register():
    # Register Menu
    bpy.utils.register_class(BLUE_HOLE_MT_directories)
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    # Unregister Menu
    bpy.utils.unregister_class(BLUE_HOLE_MT_directories)
    # Unregister Operators
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators


# ----------------------------------------------------------------------------------------------------------------------
# End of File Debug Message
debugUtils.print_debug_msg('Directories Menu and Operators Loaded!', show_verbose)
