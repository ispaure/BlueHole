# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "GNU General Public License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

from BlueHole.blenderUtils.debugUtils import print_debug_msg as print_debug_msg

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

import bpy
from bpy.types import (
        Menu,
        Operator,
        )
import os


class PIE_MT_Add(Menu):
    bl_idname = "PIE_MT_add"
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
        pie.operator("wm.call_menu_pie", text="More...").name = 'PIE_MT_global_add_more'
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


class PIE_MT_Add_More(Menu):
    bl_idname = "PIE_MT_global_add_more"
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


classes = (
    PIE_MT_Add,
    PIE_MT_Add_More
    )

addon_keymaps = []


def register():
    for cls in classes:
        print_debug_msg('Loading Pie Menu: ' + cls.bl_idname, show_verbose)
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
