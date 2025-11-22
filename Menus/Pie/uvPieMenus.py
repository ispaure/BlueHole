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
from .Button import blenderPieButton as blenderPieButton
from .Button import dreamuvPieButton as dreamuvPieButton
from .Button import uvtoolkitPieButton as uvtoolkitPieButton
from .Button import zenuvPieButton as zenuvPieButton


# ----------------------------------------------------------------------------------------------------------------------
# USER DEFINED SETTINGS

name = filename = os.path.basename(__file__)


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENUS


# Context: 2D UV Editor Viewport
# Hotkey: Ctrl+Shift+RMB
class MT_pie_UV_cursor(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_UV_cursor"  # named wrong
    bl_label = "Blue Hole: UV > Cursor"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        uvtoolkitPieButton.center_cursor_frame_all_req_ver_2(pie)
        # 6 - RIGHT
        blenderPieButton.snap_select_to_cursor(pie)
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        blenderPieButton.snap_cursor_to_select(pie)
        # 9 - TOP - RIGHT
        blenderPieButton.snap_select_to_cursor_offset(pie)
        # 1 - BOTTOM - LEFT
        blenderPieButton.snap_cursor_to_pixel(pie)
        # 3 - BOTTOM - RIGHT
        blenderPieButton.snap_selected_to_pixel(pie)


# Context: 2D UV Editor Viewport
# Hotkey: Shift+RMB
class MT_pie_UV_tool(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_UV_tool"  # named wrong
    bl_label = "Blue Hole: UV > Tools"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        blenderPieButton.smart_project(pie)
        # 6 - RIGHT
        zenuvPieButton.relax(pie)
        # 2 - BOTTOM
        zenuvPieButton.zen_unwrap(pie)
        # 8 - TOP
        zenuvPieButton.quick_rotate(pie)
        # 7 - TOP - LEFT
        zenuvPieButton.quick_mirror(pie)
        # 9 - TOP - RIGHT
        zenuvPieButton.quick_fit(pie)
        # 1 - BOTTOM - LEFT
        zenuvPieButton.auto_unwrap(pie)
        # 3 - BOTTOM - RIGHT
        zenuvPieButton.relax_along_u(pie)


# Context: 2D UV Editor Viewport
# Hotkey: Ctrl+RMB
class MT_pie_UV_action(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_UV_action"  # named wrong
    bl_label = "Blue Hole: UV > Action"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        zenuvPieButton.quadrify(pie)
        # 6 - RIGHT
        zenuvPieButton.world_orient(pie)
        # 2 - BOTTOM
        zenuvPieButton.merge_verts(pie)
        # 8 - TOP
        pie.operator("wm.call_menu_pie", text="Select...", icon='TRIA_UP').name = MT_pie_UV_action_select.bl_idname
        # 7 - TOP - LEFT
        zenuvPieButton.get_tx_density(pie)
        # 9 - TOP - RIGHT
        zenuvPieButton.set_tx_density(pie)
        # 1 - BOTTOM - LEFT
        blenderPieButton.uv_split_island(pie)
        # 3 - BOTTOM - RIGHT
        blenderPieButton.uv_stitch(pie)


# No Hotkey; Submenu
class MT_pie_UV_action_select(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_UV_action_select"  # named wrong
    bl_label = "Blue Hole: UV > Action > Select"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        zenuvPieButton.select_stretched_faces(pie)
        # 6 - RIGHT
        zenuvPieButton.select_flipped_islands(pie)
        # 2 - BOTTOM
        zenuvPieButton.select_similar_islands(pie)
        # 8 - TOP
        zenuvPieButton.select_interseams_loop(pie)
        # 7 - TOP - LEFT
        zenuvPieButton.select_uv_borders(pie)
        # 9 - TOP - RIGHT
        zenuvPieButton.select_seams_edges(pie)
        # 1 - BOTTOM - LEFT
        zenuvPieButton.select_split_edges(pie)
        # 3 - BOTTOM - RIGHT
        zenuvPieButton.select_overlapped_islands(pie)


# Context: 2D UV Editor Viewport
# Hotkey: Ctrl+Alt+Shift+RMB
class MT_pie_UV_action_uvspecial(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_UV_action_uvspecial"  # named wrong
    bl_label = "Blue Hole: UV > Action (Special)"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        zenuvPieButton.quadrify(pie)
        # 6 - RIGHT
        zenuvPieButton.world_orient(pie)
        # 2 - BOTTOM
        zenuvPieButton.zen_unwrap(pie)
        # 8 - TOP
        zenuvPieButton.select_trim_tool(pie)
        # 7 - TOP - LEFT
        zenuvPieButton.fix_trim_loop(pie)
        # 9 - TOP - RIGHT
        zenuvPieButton.fit_to_trim_1(pie)
        # 1 - BOTTOM - LEFT
        zenuvPieButton.pack_islands(pie)
        # 3 - BOTTOM - RIGHT
        zenuvPieButton.relax_along_u(pie)


# Context: 3D Viewport Mesh Edit (Vertex/Edge/Vert)
# Hotkey: Ctrl+Alt+Shift+RMB
class MT_pie_mesh_action_uvspecial(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_mesh_action_uvspecial"  # named wrong
    bl_label = "Blue Hole: Mesh > Action (UV Special)"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        blenderPieButton.clear_seam(pie)
        # 6 - RIGHT
        blenderPieButton.mark_seam(pie)
        # 2 - BOTTOM
        zenuvPieButton.zen_unwrap(pie)
        # 8 - TOP
        dreamuvPieButton.hotspotter(pie)
        # 7 - TOP - LEFT
        zenuvPieButton.fix_trim_loop(pie)
        # 9 - TOP - RIGHT
        zenuvPieButton.git_to_trim_2(pie)
        # 1 - BOTTOM - LEFT
        zenuvPieButton.auto_unwrap(pie)
        # 3 - BOTTOM - RIGHT
        zenuvPieButton.mark_by_angle(pie)


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (MT_pie_UV_cursor,
           MT_pie_UV_tool,
           MT_pie_UV_action,
           MT_pie_UV_action_select,
           MT_pie_UV_action_uvspecial,
           MT_pie_mesh_action_uvspecial)


def register():
    for cls in classes:
        log(Severity.DEBUG, name, 'Registering')
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        log(Severity.DEBUG, name, 'Unregistering')
        bpy.utils.unregister_class(cls)
