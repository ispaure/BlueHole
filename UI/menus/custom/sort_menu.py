"""
Blue Hole Menus
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
from ....operators import sort_ops

# ----------------------------------------------------------------------------------------------------------------------
# MENUS


class BLUE_HOLE_MT_sort(bpy.types.Menu):
    bl_label = "Sort"
    bl_idname = "BLUE_HOLE_MT_sort"

    def draw(self, context):
        layout = self.layout
        layout.operator(sort_ops.SortSelectionOnWorldAxis.bl_idname)
        layout.operator(sort_ops.SearchReplaceNameSelection.bl_idname)
        layout.operator(sort_ops.BatchRenameSelection.bl_idname)
        layout.operator(sort_ops.FlipLastUnderscores.bl_idname)


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (
    BLUE_HOLE_MT_sort,
)


# Register
def register():
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
