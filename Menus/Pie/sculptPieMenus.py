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


class PIE_MT_Sculpt_Tools(Menu):
    bl_idname = "PIE_MT_sculpt_tools"
    bl_label = "Blue Hole: Sculpt > Tools"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("wm.tool_set_by_id", text="Grab", icon='BRUSH_GRAB').name = 'builtin_brush.Grab'
        # 6 - RIGHT
        pie.operator("wm.tool_set_by_id", text="Clay Buildup", icon='BRUSH_CLAY').name = 'builtin_brush.Clay Strips'
        # 2 - BOTTOM
        pie.operator("wm.tool_set_by_id", text="Flatten", icon='BRUSH_FLATTEN').name = 'builtin_brush.Flatten'
        # 8 - TOP
        pie.operator("wm.tool_set_by_id", text="Draw", icon='BRUSH_SCULPT_DRAW').name = 'builtin_brush.Draw'
        # 7 - TOP - LEFT
        pie.operator("wm.tool_set_by_id", text="Pose", icon='BRUSH_ROTATE').name = 'builtin_brush.Pose'
        # 9 - TOP - RIGHT
        pie.operator("wm.tool_set_by_id", text="Clay Stips", icon='BRUSH_CLAY_STRIPS').name = 'builtin_brush.Clay Strips'
        # 1 - BOTTOM - LEFT
        pie.operator("wm.tool_set_by_id", text="Scrape", icon='BRUSH_SCRAPE').name = 'builtin_brush.Scrape'
        # 3 - BOTTOM - RIGHT
        pie.operator("wm.tool_set_by_id", text="Clay", icon='BRUSH_CLAY_STRIPS').name = 'builtin_brush.Clay'


class PIE_MT_Sculpt_Actions(Menu):
    bl_idname = "PIE_MT_sculpt_actions"
    bl_label = "Blue Hole: Sculpt > Actions"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("wm.tool_set_by_id", text="Slide Brush", icon='MOD_WAVE').name = 'builtin_brush.Slide Relax'
        # 6 - RIGHT
        pie.operator("wm.tool_set_by_id", text="Mask Brush").name = 'builtin_brush.Mask'
        # 2 - BOTTOM
        pie.operator("wm.tool_set_by_id", text="Cloth Brush", icon='MOD_CLOTH').name = 'builtin_brush.Cloth'
        # 8 - TOP
        pie.operator("wm.tool_set_by_id", text="Simplify Brush", icon='STYLUS_PRESSURE').name = 'builtin_brush.Simplify'
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


classes = (
    PIE_MT_Sculpt_Tools,
    PIE_MT_Sculpt_Actions
    )

addon_keymaps = []


def register():
    for cls in classes:
        print_debug_msg('Loading Pie Menu: ' + cls.bl_idname, show_verbose)
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
