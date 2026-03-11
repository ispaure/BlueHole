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

import bpy
from ..custom.containers_menu import BLUE_HOLE_MT_containers


# ----------------------------------------------------------------------------------------------------------------------
# CODE
def draw_blue_hole_add_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.menu(BLUE_HOLE_MT_containers.bl_idname, icon='OUTLINER')


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

def register():
    bpy.types.VIEW3D_MT_add.prepend(draw_blue_hole_add_menu)


def unregister():
    bpy.types.VIEW3D_MT_add.remove(draw_blue_hole_add_menu)
