"""
Adds Blue Hole Blender Operators [Export]
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "GNU General Public License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

import bpy

import BlueHole.envUtils.projectExport as projectExport
import BlueHole.blenderUtils.debugUtils as debugUtils
from BlueHole.blenderUtils.languageUtils import loc_str as loc_str
import BlueHole.blenderUtils.uiUtils as uiUtils
import BlueHole.blenderUtils.exportUtils2 as exportUtils2
from BlueHole.blenderUtils.uiUtils import show_label as show_label
import BlueHole.blenderUtils.fileUtils as fileUtils
import BlueHole.envUtils.envUtils as envUtils
import BlueHole.blenderUtils.configUtils as configUtils


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

# Start of File Debug Message
debugUtils.print_debug_msg('\nLoading Export Menu and Operators...', show_verbose)


# ----------------------------------------------------------------------------------------------------------------------
# MENUS

class BLUE_HOLE_MT_export(bpy.types.Menu):
    bl_label = "Export (to Source Asset Dir.)"

    def draw(self, context):
        layout = self.layout
        show_label('FINAL Folder', layout)
        layout.operator(ExportAllHierarchiesToUE.bl_idname, icon='EXPORT')
        layout.operator(ExportSelectHierarchiesToUE.bl_idname, icon='EXPORT')
        layout.operator(BatchExportSelectedToFinal.bl_idname, icon='EXPORT')
        layout.separator()
        show_label('RESOURCES Folder', layout)
        layout.operator(BatchExportSelectedToResources.bl_idname, icon='EXPORT')
        layout.separator()
        layout.operator(BatchExportSelectedToSpeedTreeDoc.bl_idname, icon='KEYTYPE_EXTREME_VEC')
        layout.operator(BatchExportSelectedToSpeedTree_FBX.bl_idname, icon='EXPORT')
        layout.operator(BatchExportSelectedToSpeedtreeLR_FBX.bl_idname, icon='EXPORT')
        layout.operator(BatchExportSelectedToSpeedtreeHR_FBX.bl_idname, icon='EXPORT')
        # Draw additional operators from the active environment (if available)
        envUtils.draw_current_env_menu_items('globalExport', layout)


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


class BatchExportSelectedToSpeedTreeDoc(bpy.types.Operator):

    bl_idname = "wm.bh_export_speedtree_doc"
    bl_label = '[[[[ ' + 'SPEEDTREE FRONDS Folder' + ' ]]]]'
    bl_description = loc_str('open_doc_page')

    def execute(self, context):
        fileUtils.open_url(configUtils.get_url_db_value('Tutorial', 'speedtree_export'))
        return{'FINISHED'}


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


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (ExportAllHierarchiesToUE,
           ExportSelectHierarchiesToUE,
           BatchExportSelectedToSpeedTreeDoc,
           BatchExportSelectedToSpeedTree_FBX,
           BatchExportSelectedToSpeedtreeLR_FBX,
           BatchExportSelectedToSpeedtreeHR_FBX,
           BatchExportSelectedToFinal,
           BatchExportSelectedToBakeFBX,
           BatchExportSelectedToResources
           )


# Register
def register():
    # Register Menu
    bpy.utils.register_class(BLUE_HOLE_MT_export)
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    # Unregister Menu
    bpy.utils.unregister_class(BLUE_HOLE_MT_export)
    # Unregister Operators
    for cls in classes:
        bpy.utils.unregister_class(cls)


# ----------------------------------------------------------------------------------------------------------------------
# End of File Debug Message
debugUtils.print_debug_msg('Export Menu and Operators Loaded!', show_verbose)
