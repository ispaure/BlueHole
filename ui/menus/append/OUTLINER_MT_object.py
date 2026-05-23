"""
Blue Hole Outliner Menus
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
from ....operators import rename_ops


# ----------------------------------------------------------------------------------------------------------------------
# CODE

def draw_blue_hole_outliner_object_menu(self, context):
    layout = self.layout

    obj = context.active_object

    if obj is None:
        return

    if not obj.name.startswith('SM_'):
        return

    layout.separator()
    layout.operator(
        rename_ops.BH_OT_rename_in_outliner_and_unreal.bl_idname,
        icon='GREASEPENCIL'
    )


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

def register():
    bpy.types.OUTLINER_MT_object.append(draw_blue_hole_outliner_object_menu)


def unregister():
    bpy.types.OUTLINER_MT_object.remove(draw_blue_hole_outliner_object_menu)