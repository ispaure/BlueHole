"""
Import/Export Operators
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

# Blue Hole
from ..blenderUtils import objectUtils, importUtils
from ..blenderUtils.export.exportSettingsPresets import *
from ..blenderUtils.export.looseMesh.containerGroup import batch_export_loose_mesh
from ..blenderUtils.export.model.assetContainerGroup import get_hierarchy_prefix_lst
from ..preferences.prefs import *


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS

# EXPORT
class BatchExportSelectedToFinal(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_final"
    bl_label = 'Batch Export (Selection) to FINAL Folder'
    bl_description = 'Batch exports selected meshes using their names as file names in the FINAL Folder'

    def execute(self, context):
        batch_export_loose_mesh(prefs().directory.sc_dir_struct_final)
        return {'FINISHED'}


class BatchExportSelectedToResources(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_resources"
    bl_label = 'Batch Export (Selection) to RESOURCES Folder'

    def execute(self, context):
        batch_export_loose_mesh(prefs().directory.sc_dir_struct_resources)
        return {'FINISHED'}


class BatchExportSelectedToSpeedTree_FBX(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_speedtree_fbx"
    bl_label = 'Batch Export (Selection) to SPEEDTREE Folder'
    bl_description = 'Batch exports selected meshes using their names as file names in the SPEEDTREE MSH Folder'

    def execute(self, context):
        batch_export_loose_mesh(prefs().directory.sc_dir_struct_st)
        return {'FINISHED'}


class BatchExportSelectedToSpeedtreeLR_FBX(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_speedtree_lr_fbx"
    bl_label = 'Batch Export (Selection) to SPEEDTREE-LR Folder'
    bl_description = 'Batch exports selected meshes using their names as file names in the SPEEDTREE MSH -> LR Folder'

    def execute(self, context):
        batch_export_loose_mesh(prefs().directory.sc_dir_struct_st_lr)
        return {'FINISHED'}


class BatchExportSelectedToSpeedtreeHR_FBX(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_speedtree_hr_fbx"
    bl_label = 'Batch Export (Selection) to SPEEDTREE-HR Folder'
    bl_description = 'Batch exports selected meshes using their names as file names in the SPEEDTREE MSH -> HR Folder'

    def execute(self, context):
        batch_export_loose_mesh(prefs().directory.sc_dir_struct_st_hr)
        return {'FINISHED'}


class BatchExportSelectedToBakeFBX(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_bake_fbx"
    bl_label = 'Batch Export (Selection) to BAKE Folder'
    bl_description = 'Batch exports selected meshes using their names as file names in the MSH BAKE Folder'

    def execute(self, context):
        batch_export_loose_mesh(prefs().directory.sc_dir_struct_msh_bake)
        return {'FINISHED'}


# IMPORT
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
           BatchExportSelectedToSpeedTree_FBX,
           BatchExportSelectedToSpeedtreeLR_FBX,
           BatchExportSelectedToSpeedtreeHR_FBX,
           BatchExportSelectedToFinal,
           BatchExportSelectedToBakeFBX,
           BatchExportSelectedToResources)


def register():
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    # Unregister Operators
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators

