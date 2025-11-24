"""
Import/Export Operators
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
import BlueHole.blenderUtils.objectUtils as objectUtils
import BlueHole.blenderUtils.exportUtils2 as exportUtils2
import BlueHole.blenderUtils.addon as addon
import BlueHole.envUtils.projectExport as projectExport
from BlueHole.blenderUtils.languageUtils import loc_str as loc_str
import BlueHole.blenderUtils.uiUtils as uiUtils
import BlueHole.blenderUtils.fileUtils as fileUtils
import BlueHole.blenderUtils.configUtils as configUtils
import BlueHole.blenderUtils.importUtils as importUtils


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class ExportAllHierarchiesToUE(bpy.types.Operator):

    bl_idname = "wm.bh_export_all_hierarchies_ue"
    bl_label = "Export (*ALL* Asset Hierarchies) to FINAL Folder for UNREAL"
    bl_description = 'Exports all hierarchies created with the "Add Asset Hierarchy" tool in FINAL Folder'

    def execute(self, context):
        msg = 'Do you really want to export *ALL* Asset Hierarchies? Press OK to confirm.'
        state = uiUtils.show_dialog_box('Unreal Export', msg)
        if state:
            exportUtils2.export_asset_hierarchies(selected_only=False,
                                                  preset='Unreal',
                                                  is_send=False,
                                                  skip_sc=False)
        return {'FINISHED'}


class ExportSelectHierarchiesToUE(bpy.types.Operator):

    bl_idname = "wm.bh_export_select_hierarchies_ue"
    bl_label = "Export (Selected Asset Hierarchies) to FINAL Folder for UNREAL"
    bl_description = 'Exports selected hierarchies created with the "Add Asset Hierarchy" tool in FINAL Folder'

    def execute(self, context):
        exportUtils2.export_asset_hierarchies(selected_only=True,
                                              preset='Unreal',
                                              is_send=False,
                                              skip_sc=False)
        return {'FINISHED'}


class BatchExportSelectedToFinal(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_final"
    bl_label = 'Batch Export (Selection) to FINAL Folder'

    def execute(self, context):
        projectExport.batch_export_selection_to_project_sub_dir('path_final')
        return {'FINISHED'}


class BatchExportSelectedToResources(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_resources"
    bl_label = 'Batch Export (Selection) to RESOURCES Folder'

    def execute(self, context):
        projectExport.batch_export_selection_to_project_sub_dir('path_resources')
        return {'FINISHED'}


class BatchExportSelectedToSpeedTree_FBX(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_speedtree_fbx"
    bl_label = loc_str('export_select_to_speedtree_fbx')
    bl_description = loc_str('export_select_to_speedtree_fbx_tt')

    def execute(self, context):
        projectExport.batch_export_selection_to_project_sub_dir('path_speedtree_msh')
        return {'FINISHED'}


class BatchExportSelectedToSpeedtreeLR_FBX(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_speedtree_lr_fbx"
    bl_label = loc_str('export_select_to_speedtree_fbx_lr')
    bl_description = loc_str('export_select_to_speedtree_fbx_lr_tt')

    def execute(self, context):
        projectExport.batch_export_selection_to_project_sub_dir('path_speedtree_msh_lr')
        return {'FINISHED'}


class BatchExportSelectedToSpeedtreeHR_FBX(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_speedtree_hr_fbx"
    bl_label = loc_str('export_select_to_speedtree_fbx_hr')
    bl_description = loc_str('export_select_to_speedtree_fbx_hr_tt')

    def execute(self, context):
        projectExport.batch_export_selection_to_project_sub_dir('path_speedtree_msh_hr')
        return {'FINISHED'}


class BatchExportSelectedToBakeFBX(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_bake_fbx"
    bl_label = loc_str('export_select_to_bake_fbx')
    bl_description = loc_str('export_select_to_bake_fbx_tt')

    def execute(self, context):
        projectExport.batch_export_selection_to_project_sub_dir('path_mshbake')
        return {'FINISHED'}


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


class ImportGuide_5_6_ScaleMan(bpy.types.Operator):

    bl_idname = "wm.bh_imp_guide_5_6_scaleman"
    bl_label = "Scaleman (5'6)"

    def execute(self, context):
        importUtils.import_default_env_scale_guide('5_6_scaleman.obj')
        return {'FINISHED'}


class ImportGuide_5_10_ScaleMan(bpy.types.Operator):

    bl_idname = "wm.bh_imp_guide_5_10_scaleman"
    bl_label = "Scaleman (5'10)"

    def execute(self, context):
        importUtils.import_default_env_scale_guide('5_10_scaleman.obj')
        return {'FINISHED'}


class ImportGuide_5_10_ScaleManCasual(bpy.types.Operator):

    bl_idname = "wm.bh_imp_guide_5_10_scaleman_casual"
    bl_label = "Scaleman (5'10) Casual"

    def execute(self, context):
        importUtils.import_default_env_scale_guide('5_10_scaleman_CasualPose.fbx')
        return {'FINISHED'}


class ImportGuide_5_10_ScaleManSitting(bpy.types.Operator):

    bl_idname = "wm.bh_imp_guide_5_10_scaleman_sitting"
    bl_label = "Scaleman (5'10) Sitting"

    def execute(self, context):
        importUtils.import_default_env_scale_guide('5_10_scaleman_SittingPose.fbx')
        return {'FINISHED'}


class ImportGuide_6_1_ScaleMan(bpy.types.Operator):

    bl_idname = "wm.bh_imp_guide_6_1_scaleman"
    bl_label = "Scaleman (6'1)"

    def execute(self, context):
        importUtils.import_default_env_scale_guide('6_1_scaleman.obj')
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister

classes = (ImportGuide_5_6_ScaleMan,
           ImportGuide_5_10_ScaleMan,
           ImportGuide_5_10_ScaleManCasual,
           ImportGuide_5_10_ScaleManSitting,
           ImportGuide_6_1_ScaleMan,
           ExportAllHierarchiesToUE,
           ExportSelectHierarchiesToUE,
           BatchExportSelectedToSpeedTree_FBX,
           BatchExportSelectedToSpeedtreeLR_FBX,
           BatchExportSelectedToSpeedtreeHR_FBX,
           BatchExportSelectedToFinal,
           BatchExportSelectedToBakeFBX,
           BatchExportSelectedToResources,
           SceneAddAssetHierarchy)


def register():
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    # Unregister Operators
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators

