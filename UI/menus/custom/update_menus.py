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
from ....operators import other_ops

# ----------------------------------------------------------------------------------------------------------------------
# MENUS


class BLUE_HOLE_MT_update_deluxe(bpy.types.Menu):
    bl_label = "Updates & Deluxe"
    bl_idname = "BLUE_HOLE_MT_update_deluxe"

    def draw(self, context):
        layout = self.layout
        layout.operator(other_ops.WM_OT_Apply_Deluxe_Prefs.bl_idname)


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (
    BLUE_HOLE_MT_update_deluxe,
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
