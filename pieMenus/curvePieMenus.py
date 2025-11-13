# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "MIT License"
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


class PIE_MT_Curve_Action(Menu):
    bl_idname = "PIE_MT_curve_action"
    bl_label = "Blue Hole: Curve > Action"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("curve.split", text="Split", icon='FCURVE')
        # 6 - RIGHT
        pie.operator("curve.separate", text="Separate", icon='OUTLINER_OB_CURVE')
        # 2 - BOTTOM
        pie.operator("curve.dissolve_verts", text="Dissolve Vertices", icon='GHOST_DISABLED')
        # 8 - TOP
        pie.operator("curve.smooth_radius", text="Smooth Curve Radius", icon='FULLSCREEN_EXIT')
        # 7 - TOP - LEFT
        pie.operator("curve.normals_make_consistent", text="Recalculate Handles", icon='HANDLE_FREE')
        # 9 - TOP - RIGHT
        pie.operator("curve.handle_type_set", text="Set Handle Linear", icon='HANDLE_ALIGNED').type = 'ALIGNED'
        # 1 - BOTTOM - LEFT
        pie.operator("curve.switch_direction", text="Switch Direction", icon='CURVE_PATH')
        # 3 - BOTTOM - RIGHT
        pie.operator("curve.cyclic_toggle", text="Toggle Cyclic", icon='CURVE_NCIRCLE')


class PIE_MT_Curve_Tools(Menu):
    bl_idname = "PIE_MT_curve_tools"
    bl_label = "Blue Hole: Curve > Tools"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("curve.make_segment", text="Make Segment", icon='OUTLINER_DATA_CURVE')
        # 6 - RIGHT
        pie.operator("curve.extrude_move", text="Extrude Curve and Move", icon='CURVE_BEZCURVE')
        # 2 - BOTTOM
        pie.operator("curve.smooth", text="Smooth", icon='MOD_OFFSET')
        # 8 - TOP
        pie.operator("curvetools.bezier_points_fillet", text="Bezier points Fillet", icon='CURVE_NCURVE')
        # 7 - TOP - LEFT
        pie.operator("transform.tilt", text="Tilt", icon='ORIENTATION_GIMBAL')
        # 9 - TOP - RIGHT
        pie.operator("transform.transform", text="Scale", icon='ORIENTATION_LOCAL').mode = 'CURVE_SHRINKFATTEN'
        # 1 - BOTTOM - LEFT
        pie.operator("curve.decimate", text="Decimate Curve", icon='IPO_LINEAR')
        # 3 - BOTTOM - RIGHT
        pie.operator("curve.subdivide", text="Subdivide", icon='PARTICLE_POINT')


class PIE_MT_Curve_Hide(Menu):
    bl_idname = "PIE_MT_curve_hide"
    bl_label = "Blue Hole: Curve > Hide"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("curve.reveal", text="Reveal Hidden [All]")
        # 6 - RIGHT
        pie.operator("curve.hide", text="Isolate Selection").unselected = True
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        pie.operator("curve.hide", text="Hide Selection").unselected = False
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


classes = (
    PIE_MT_Curve_Action,
    PIE_MT_Curve_Tools,
    PIE_MT_Curve_Hide
    )

addon_keymaps = []


def register():
    for cls in classes:
        print_debug_msg('Loading Pie Menu: ' + cls.bl_idname, show_verbose)
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
