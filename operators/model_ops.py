"""
Modeling Operators
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


# IMPORT
class WM_OT_MergeLast(bpy.types.Operator):
    """
    Custom operator for this because the option is not always available which may break the Pie Menus
    """
    bl_idname = "wm.bh_merge_last"
    bl_label = "Merge Last"
    bl_options = {'INTERNAL'}

    def execute(self, _context):
        try:
            bpy.ops.mesh.merge(type='LAST')
        except:
            bpy.ops.mesh.merge()
        return {'FINISHED'}


class OBJECT_OT_BH_FaceSelectOrPose(bpy.types.Operator):
    """Enter face selection on a mesh or Pose Mode on an armature"""
    bl_idname = "object.bh_face_select_or_pose"
    bl_label = "Face Select / Pose Mode"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None and obj.type in {'MESH', 'ARMATURE'}
                and bpy.ops.object.mode_set.poll())

    def execute(self, context):
        if context.active_object.type == 'MESH':
            return bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode={'FACE'})
        return bpy.ops.object.mode_set(mode='POSE')


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister

classes = (
    WM_OT_MergeLast,
    OBJECT_OT_BH_FaceSelectOrPose,
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

