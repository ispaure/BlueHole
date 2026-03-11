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


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister

classes = (
    WM_OT_MergeLast,
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

