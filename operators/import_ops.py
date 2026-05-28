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
from ..blenderUtils import importUtils

# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS

# EXPORT


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


class ImportMeshFBXOBJ(bpy.types.Operator):
    bl_idname = 'wm.bh_imp_scale_guide'
    bl_label = 'Import Scale Guide'

    import_path_str: bpy.props.StringProperty(name="")

    def execute(self, context):
        importUtils.import_fbx_obj(self.import_path_str)
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister

classes = (ImportGuide_5_6_ScaleMan,
           ImportGuide_5_10_ScaleMan,
           ImportGuide_5_10_ScaleManCasual,
           ImportGuide_5_10_ScaleManSitting,
           ImportGuide_6_1_ScaleMan,
           ImportMeshFBXOBJ,
           )


def register():
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    # Unregister Operators
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators

