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
from BlueHole.Menus.Pie.Button import blenderPieButton
import os


# ----------------------------------------------------------------------------------------------------------------------
# USER DEFINED SETTINGS

name = filename = os.path.basename(__file__)


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENUS


# Context: 3D Viewport (Curve)
# Hotkey: Ctrl + RMB
class MT_pie_curve_action(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_curve_action"
    bl_label = "Blue Hole: Curve > Action"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        blenderPieButton.split_curve(pie)
        # 6 - RIGHT
        blenderPieButton.separate_curve(pie)
        # 2 - BOTTOM
        blenderPieButton.dissolve_curve_vertices(pie)
        # 8 - TOP
        blenderPieButton.smooth_curve_radius(pie)
        # 7 - TOP - LEFT
        blenderPieButton.recalc_curve_handles(pie)
        # 9 - TOP - RIGHT
        blenderPieButton.set_handle_linear(pie)
        # 1 - BOTTOM - LEFT
        blenderPieButton.switch_curve_direction(pie)
        # 3 - BOTTOM - RIGHT
        blenderPieButton.toggle_curve_cyclic(pie)


# Context: 3D Viewport (Curve)
# Hotkey: Shift + RMB
class MT_pie_curve_tool(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_curve_tool"
    bl_label = "Blue Hole: Curve > Tools"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        blenderPieButton.curve_make_segment(pie)
        # 6 - RIGHT
        blenderPieButton.curve_extrude_move(pie)
        # 2 - BOTTOM
        blenderPieButton.curve_smooth(pie)
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        blenderPieButton.transform_tilt(pie)
        # 9 - TOP - RIGHT
        blenderPieButton.transform_curve_scale(pie)
        # 1 - BOTTOM - LEFT
        blenderPieButton.curve_decimate(pie)
        # 3 - BOTTOM - RIGHT
        blenderPieButton.curve_subdivide(pie)


# Context: 3D Viewport (Curve)
# Hotkey: Shift + S + Drag Mouse in any direction
class MT_pie_curve_hide(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_curve_hide"
    bl_label = "Blue Hole: Curve > Hide"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        blenderPieButton.curve_reveal_all(pie)
        # 6 - RIGHT
        blenderPieButton.curve_isolate_selection(pie)
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        blenderPieButton.curve_hide_selection(pie)
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (MT_pie_curve_action,
           MT_pie_curve_tool,
           MT_pie_curve_hide)


def register():
    log(Severity.DEBUG, name, 'Registering')
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    log(Severity.DEBUG, name, 'Unregistering')
    for cls in classes:
        bpy.utils.unregister_class(cls)
