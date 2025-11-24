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
        button = pie.operator("mesh.primitive_cylinder_add", text="Cylinder", icon='MESH_CYLINDER')
        button.align = 'CURSOR'
        button.radius = 0.5
        button.depth = 1.0
        button.vertices = 32
        # 6 - RIGHT
        button_02 = pie.operator("mesh.primitive_cube_add", text="Cube", icon='MESH_CUBE')
        button_02.align = 'CURSOR'
        button_02.size = 1.0
        # 2 - BOTTOM
        pie.operator("wm.call_menu_pie", text="More...").name = MT_pie_add_more.bl_idname
        # 8 - TOP
        button_03 = pie.operator("mesh.primitive_uv_sphere_add", text="UV Sphere", icon='MATSPHERE')
        button_03.radius = 0.5
        # 7 - TOP - LEFT
        pie.operator("machin3.quadsphere", text="Quadsphere", icon='MESH_UVSPHERE')
        # 9 - TOP - RIGHT
        pie.operator("mesh.primitive_plane_add", text="Plane", icon='MESH_PLANE').size = 1.0
        # 1 - BOTTOM - LEFT
        pie.operator("curve.primitive_nurbs_path_add", text="Path", icon='CURVE_PATH')
        # 3 - BOTTOM - RIGHT
        pie.operator("curve.primitive_bezier_curve_add", text="Bezier", icon='CURVE_BEZCURVE')


# No Hotkey; Submenu
class MT_pie_add_more(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_add_more"
    bl_label = "Blue Hole: Add > More"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("object.light_add", text="Point", icon='LIGHT_POINT').type = 'POINT'
        # 6 - RIGHT
        pie.operator("object.light_add", text="Spot", icon='LIGHT_SPOT').type = 'SPOT'
        # 2 - BOTTOM
        pie.operator("object.text_add", text="Text", icon='OUTLINER_OB_FONT')
        # 8 - TOP
        pie.operator("object.light_add", text="Area", icon='LIGHT_AREA').type = 'AREA'
        # 7 - TOP - LEFT
        pie.separator()
        # TODO: Make this one work again
        # pie.operator("object.lightprobe_add", text="Light Probe", icon='LIGHTPROBE_GRID').type = 'GRID'
        # 9 - TOP - RIGHT
        pie.operator("object.light_add", text="Sun", icon='LIGHT_SUN').type = 'SUN'
        # 1 - BOTTOM - LEFT
        pie.operator("object.load_reference_image", text="Reference Image", icon='IMAGE_REFERENCE')
        # 3 - BOTTOM - RIGHT
        pie.operator("curve.primitive_bezier_circle_add", text="Bezier Circle", icon='CURVE_BEZCIRCLE')


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
