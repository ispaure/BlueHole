# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'


# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS

import bpy
from BlueHole.blenderUtils.debugUtils import *
import os
from BlueHole.Menus.Pie.Button import blenderPieButton, machin3PieButton


# ----------------------------------------------------------------------------------------------------------------------
# USER DEFINED SETTINGS

name = filename = os.path.basename(__file__)


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENUS


# Context: 3D Viewport (Global)
# Hotkey: Shift + A + Drag Mouse in any direction
class MT_pie_add(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_add"
    bl_label = "Blue Hole: Add"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        blenderPieButton.add_cylinder(pie)
        # 6 - RIGHT
        blenderPieButton.add_cube(pie)
        # 2 - BOTTOM
        pie.operator("wm.call_menu_pie", text="More...").name = MT_pie_add_more.bl_idname
        # 8 - TOP
        blenderPieButton.add_sphere(pie)
        # 7 - TOP - LEFT
        machin3PieButton.add_quadsphere()
        # 9 - TOP - RIGHT
        blenderPieButton.add_plane(pie)
        # 1 - BOTTOM - LEFT
        blenderPieButton.add_nurbs_path(pie)
        # 3 - BOTTOM - RIGHT
        blenderPieButton.add_bezier_curve(pie)


# No Hotkey; Submenu
class MT_pie_add_more(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_add_more"
    bl_label = "Blue Hole: Add > More"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        blenderPieButton.add_light_point(pie)
        # 6 - RIGHT
        blenderPieButton.add_light_spot(pie)
        # 2 - BOTTOM
        blenderPieButton.add_text(pie)
        # 8 - TOP
        blenderPieButton.add_light_area(pie)
        # 7 - TOP - LEFT
        blenderPieButton.add_light_probe(pie)
        # 9 - TOP - RIGHT
        blenderPieButton.add_light_sun(pie)
        # 1 - BOTTOM - LEFT
        blenderPieButton.load_ref_img(pie)
        # 3 - BOTTOM - RIGHT
        blenderPieButton.add_bezier_circle(pie)


classes = (MT_pie_add,
           MT_pie_add_more)


def register():
    log(Severity.DEBUG, name, 'Registering')
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    log(Severity.DEBUG, name, 'Unregistering')
    for cls in classes:
        bpy.utils.unregister_class(cls)
