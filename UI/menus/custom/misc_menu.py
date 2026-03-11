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

# ----------------------------------------------------------------------------------------------------------------------
# MENUS


class BLUE_HOLE_MT_misc(bpy.types.Menu):
    bl_label = 'Misc'
    bl_idname = "BLUE_HOLE_MT_misc"

    def draw(self, context):
        layout = self.layout
        layout.menu("BLUE_HOLE_MT_sort")
        layout.menu("BLUE_HOLE_MT_themes", icon='IMAGE_RGB_ALPHA')
        layout.menu("BLUE_HOLE_MT_food_delivery", icon='TEMP')
        layout.menu("BLUE_HOLE_MT_music", icon='SOUND')


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (
    BLUE_HOLE_MT_misc,
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
