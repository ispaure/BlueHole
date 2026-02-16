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
from ...Lib.commonUtils.debugUtils import *
from .Button.sculptPieButton import *
from .utilities import *


# ----------------------------------------------------------------------------------------------------------------------
# USER DEFINED SETTINGS

name = filename = os.path.basename(__file__)


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENUS


# Context: 3D Viewport Sculpt
# Hotkey: Shift+RMB
class MT_pie_sculpt_tool(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_sculpt_tool"
    bl_label = "Blue Hole: Sculpt > General"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        open_pie_menu(pie, MT_pie_sculpt_tool_FlattenPinch.bl_idname, 'Flatten/Pinch...', 'TRIA_LEFT')
        # 6 - RIGHT
        pie.separator()
        # 2 - BOTTOM
        open_pie_menu(pie, MT_pie_sculpt_tool_Grab.bl_idname, 'Grab...', 'TRIA_DOWN')
        # 8 - TOP
        open_pie_menu(pie, MT_pie_sculpt_tool_clayblob.bl_idname, 'Clay/Blob...', 'TRIA_UP')
        # 7 - TOP LEFT
        pie.separator()
        # 9 - TOP RIGHT
        open_pie_menu(pie, MT_pie_sculpt_tool_Draw.bl_idname, 'Draw...')
        # 1 - BOTTOM LEFT
        open_pie_menu(pie, MT_pie_sculpt_tool_Misc.bl_idname, 'Misc...')
        # 3 - BOTTOM RIGHT
        pie.separator()


# No Hotkey; Submenu
class MT_pie_sculpt_tool_clayblob(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_sculpt_tool_clayblob"
    bl_label = "Blue Hole: Sculpt > General > Clay/Blob"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        brush(pie, BlenderBrush.BLOB)
        # 6 - RIGHT
        brush(pie, BlenderBrush.CLAY_THUMB)
        # 2 - BOTTOM
        brush(pie, BlenderBrush.CLAY_STRIPS)
        # 8 - TOP
        brush(pie, BlenderBrush.CLAY)
        # 7 - TOP LEFT
        brush(pie, BlenderBrush.LAYER)
        # 9 - TOP RIGHT
        brush(pie, BlenderBrush.FILL_DEEPEN)
        # 1 - BOTTOM LEFT
        pie.separator()
        # 3 - BOTTOM RIGHT
        pie.separator()


# No Hotkey; Submenu
class MT_pie_sculpt_tool_Draw(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_sculpt_tool_draw"
    bl_label = "Blue Hole: Sculpt > General > Draw"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        brush(pie, BlenderBrush.DRAW)
        # 6 - RIGHT
        brush(pie, BlenderBrush.DRAW_SHARP)
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        pie.separator()
        # 7 - TOP LEFT
        pie.separator()
        # 9 - TOP RIGHT
        pie.separator()
        # 1 - BOTTOM LEFT
        pie.separator()
        # 3 - BOTTOM RIGHT
        pie.separator()


# No Hotkey; Submenu
class MT_pie_sculpt_tool_FlattenPinch(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_sculpt_tool_flattenpinch"
    bl_label = "Blue Hole: Sculpt > General > Flatten/Pinch"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        brush(pie, BlenderBrush.FLATTEN_CONTRAST)
        # 6 - RIGHT
        brush(pie, BlenderBrush.SCRAPE_MULTIPLANE)
        # 2 - BOTTOM
        brush(pie, BlenderBrush.SMOOTH)
        # 8 - TOP
        brush(pie, BlenderBrush.BOUNDARY)
        # 7 - TOP LEFT
        brush(pie, BlenderBrush.PINCH_MAGNIFY)
        # 9 - TOP RIGHT
        brush(pie, BlenderBrush.SCRAPE_FILL)
        # 1 - BOTTOM LEFT
        brush(pie, BlenderBrush.PLATEAU)
        # 3 - BOTTOM RIGHT
        brush(pie, BlenderBrush.TRIM)



# No Hotkey; Submenu
class MT_pie_sculpt_tool_Grab(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_sculpt_tool_grab"
    bl_label = "Blue Hole: Sculpt > General > Grab"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        brush(pie, BlenderBrush.ELASTIC_GRAB)
        # 6 - RIGHT
        brush(pie, BlenderBrush.ELASTIC_SNAKE_HOOK)
        # 2 - BOTTOM
        open_pie_menu(pie, MT_pie_sculpt_tool_NudgeThumb.bl_idname, 'Nudge/Thumb...', 'TRIA_DOWN')
        # 8 - TOP
        brush(pie, BlenderBrush.GRAB_SILHOUETTE)
        # 7 - TOP LEFT
        brush(pie, BlenderBrush.GRAB)
        # 9 - TOP RIGHT
        brush(pie, BlenderBrush.CLAY_STRIPS)
        # 1 - BOTTOM LEFT
        brush(pie, BlenderBrush.GRAB_2D)
        # 3 - BOTTOM RIGHT
        brush(pie, BlenderBrush.SNAKE_HOOK)


# No Hotkey; Submenu
class MT_pie_sculpt_tool_NudgeThumb(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_sculpt_tool_nudgethumb"
    bl_label = "Blue Hole: Sculpt > General > Grab > Nudge/Thumb"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        pie.separator()
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        pie.separator()
        # 7 - TOP LEFT
        pie.separator()
        # 9 - TOP RIGHT
        pie.separator()
        # 1 - BOTTOM LEFT
        brush(pie, BlenderBrush.NUDGE)
        # 3 - BOTTOM RIGHT
        brush(pie, BlenderBrush.THUMB)


# No Hotkey; Submenu
class MT_pie_sculpt_tool_Misc(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_sculpt_tool_misc"
    bl_label = "Blue Hole: Sculpt > General > Misc"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        brush(pie, BlenderBrush.RELAX_PINCH)
        # 6 - RIGHT
        brush(pie, BlenderBrush.RELAX_SLIDE)
        # 2 - BOTTOM
        brush(pie, BlenderBrush.TWIST)
        # 8 - TOP
        brush(pie, BlenderBrush.DENSITY)
        # 7 - TOP LEFT
        brush(pie, BlenderBrush.ERASE_MULTIRES_DISPLACEMENT)
        # 9 - TOP RIGHT
        brush(pie, BlenderBrush.FACE_SET_PAINT)
        # 1 - BOTTOM LEFT
        brush(pie, BlenderBrush.MASK)
        # 3 - BOTTOM RIGHT
        brush(pie, BlenderBrush.SMEAR_MULTIRES_DISPLACEMENT)


# Context: 3D Viewport Sculpt
# Hotkey: Ctrl+RMB
class MT_pie_sculpt_action(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_sculpt_action"
    bl_label = "Blue Hole: Sculpt > Paint"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        brush(pie, BlenderBrush.PAINT_SOFT)
        # 6 - RIGHT
        brush(pie, BlenderBrush.PAINT_HARD)
        # 2 - BOTTOM
        open_pie_menu(pie, MT_pie_sculpt_action_Blend.bl_idname, 'Blend/Blur...', 'TRIA_DOWN')
        # 8 - TOP
        brush(pie, BlenderBrush.PAINT_SQUARE)
        # 7 - TOP - LEFT
        brush(pie, BlenderBrush.SHARPEN)
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        brush(pie, BlenderBrush.PAINT_SOFT_PRESSURE)
        # 3 - BOTTOM - RIGHT
        brush(pie, BlenderBrush.PAINT_HARD_PRESSURE)


# No Hotkey; Submenu
class MT_pie_sculpt_action_Blend(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_sculpt_action_blend"
    bl_label = "Blue Hole: Sculpt > Paint > Blend"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        brush(pie, BlenderBrush.AIRBRUSH)
        # 6 - RIGHT
        brush(pie, BlenderBrush.BLEND_HARD)
        # 2 - BOTTOM
        brush(pie, BlenderBrush.SMEAR)
        # 8 - TOP
        brush(pie, BlenderBrush.PAINT_BLEND)
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        brush(pie, BlenderBrush.BLEND_SQUARE)
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        brush(pie, BlenderBrush.BLEND_SOFT)


# Context: 3D Viewport Sculpt
# Hotkey: Ctrl+Alt+Shift+RMB
class MT_pie_sculpt_simulation(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_sculpt_simulation"
    bl_label = "Blue Hole: Sculpt > Simulation"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        open_pie_menu(pie, MT_pie_sculpt_simulation_ExpandContract.bl_idname, 'Expand/Contract...', 'TRIA_LEFT')
        # 6 - RIGHT
        brush(pie, BlenderBrush.GRAB_CLOTH)
        # 2 - BOTTOM
        brush(pie, BlenderBrush.PINCH_POINT_CLOTH)
        # 8 - TOP
        brush(pie, BlenderBrush.GRAB_CLOTH)
        # 7 - TOP - LEFT
        brush(pie, BlenderBrush.GRAB_PLANAR_CLOTH)
        # 9 - TOP - RIGHT
        brush(pie, BlenderBrush.GRAB_RANDOM_CLOTH)
        # 1 - BOTTOM - LEFT
        open_pie_menu(pie, MT_pie_sculpt_simulation_BendStretchTwist.bl_idname, 'Bend/Stretch/Twist...')
        # 3 - BOTTOM - RIGHT
        brush(pie, BlenderBrush.PINCH_FOLDS_CLOTH)


# No Hotkey; Submenu
class MT_pie_sculpt_simulation_BendStretchTwist(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_sculpt_simulation_bendstretchtwist"
    bl_label = "Blue Hole: Sculpt > Simulation > Bend/Stretch/Twist"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        brush(pie, BlenderBrush.BEND_BOUNDARY_CLOTH)
        # 6 - RIGHT
        brush(pie, BlenderBrush.BEND_TWIST_CLOTH)
        # 2 - BOTTOM
        brush(pie, BlenderBrush.STRETCH_MOVE_CLOTH)
        # 8 - TOP
        brush(pie, BlenderBrush.TWIST_BOUNDARY_CLOTH)
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# No Hotkey; Submenu
class MT_pie_sculpt_simulation_ExpandContract(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_sculpt_simulation_expandcontract"
    bl_label = "Blue Hole: Sculpt > Simulation > Expand/Contract"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        brush(pie, BlenderBrush.EXPAND_CONTRACT_CLOTH)
        # 6 - RIGHT
        brush(pie, BlenderBrush.INFLATE_CLOTH)
        # 2 - BOTTOM
        brush(pie, BlenderBrush.PUSH_CLOTH)
        # 8 - TOP
        pie.separator()
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
classes = (MT_pie_sculpt_tool,
           MT_pie_sculpt_tool_Draw,
           MT_pie_sculpt_tool_Grab,
           MT_pie_sculpt_tool_clayblob,
           MT_pie_sculpt_tool_NudgeThumb,
           MT_pie_sculpt_tool_FlattenPinch,
           MT_pie_sculpt_tool_Misc,
           MT_pie_sculpt_action,
           MT_pie_sculpt_action_Blend,
           MT_pie_sculpt_simulation,
           MT_pie_sculpt_simulation_BendStretchTwist,
           MT_pie_sculpt_simulation_ExpandContract)


def register():
    log(Severity.DEBUG, name, 'Registering')
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    log(Severity.DEBUG, name, 'Unregistering')
    for cls in classes:
        bpy.utils.unregister_class(cls)
