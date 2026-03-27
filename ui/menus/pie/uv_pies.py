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

from ....Lib.commonUtils.debugUtils import *
from ....debug.debug_flags import *
from ....actions.operator_action import draw_operator_action
from ....actions.actions import pie_actions
from .entries import blender_entries
from .entries.third_party import uvtoolkit_entries, zenuv_entries

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

TOOL_NAME = 'UV'

# ----------------------------------------------------------------------------------------------------------------------
# PIE MENUS


# Context: 2D UV Editor Viewport
# Hotkey: Ctrl+Shift+RMB
class BLUEHOLE_MT_pie_UV_cursor(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_UV_cursor"  # named wrong
    bl_label = "Blue Hole: UV > Cursor"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        uvtoolkit_entries.center_cursor_frame_all_req_ver_2(pie)
        # 6 - RIGHT
        blender_entries.snap_select_to_cursor(pie)
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        blender_entries.snap_cursor_to_select(pie)
        # 9 - TOP - RIGHT
        blender_entries.snap_select_to_cursor_offset(pie)
        # 1 - BOTTOM - LEFT
        blender_entries.snap_cursor_to_pixel(pie)
        # 3 - BOTTOM - RIGHT
        blender_entries.snap_selected_to_pixel(pie)


# Context: 2D UV Editor Viewport
# Hotkey: Shift+RMB
class BLUEHOLE_MT_pie_UV_tool(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_UV_tool"  # named wrong
    bl_label = "Blue Hole: UV > Tools"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        blender_entries.smart_project(pie)
        # 6 - RIGHT
        zenuv_entries.relax(pie)
        # 2 - BOTTOM
        blender_entries.uv_unwrap_conformal(pie)
        # 8 - TOP
        zenuv_entries.quick_rotate(pie)
        # 7 - TOP - LEFT
        zenuv_entries.quick_mirror(pie)
        # 9 - TOP - RIGHT
        zenuv_entries.quick_fit(pie)
        # 1 - BOTTOM - LEFT
        zenuv_entries.auto_unwrap(pie)
        # 3 - BOTTOM - RIGHT
        zenuv_entries.relax_along_u(pie)


# Context: 2D UV Editor Viewport
# Hotkey: Ctrl+RMB
class BLUEHOLE_MT_pie_UV_action(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_UV_action"  # named wrong
    bl_label = "Blue Hole: UV > Action"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        zenuv_entries.quadrify(pie)
        # 6 - RIGHT
        zenuv_entries.world_orient(pie)
        # 2 - BOTTOM
        zenuv_entries.merge_verts(pie)
        # 8 - TOP
        draw_operator_action(pie, pie_actions.PIE_UV_ACTION_SELECT, context, text='Select...', icon='TRIA_UP')
        # 7 - TOP - LEFT
        zenuv_entries.get_tx_density(pie)
        # 9 - TOP - RIGHT
        zenuv_entries.set_tx_density(pie)
        # 1 - BOTTOM - LEFT
        blender_entries.uv_split_island(pie)
        # 3 - BOTTOM - RIGHT
        blender_entries.uv_stitch(pie)


# No Hotkey; Submenu
class BLUEHOLE_MT_pie_UV_action_select(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_UV_action_select"  # named wrong
    bl_label = "Blue Hole: UV > Action > Select"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        zenuv_entries.select_stretched_faces(pie)
        # 6 - RIGHT
        zenuv_entries.select_flipped_islands(pie)
        # 2 - BOTTOM
        zenuv_entries.select_similar_islands(pie)
        # 8 - TOP
        zenuv_entries.select_interseams_loop(pie)
        # 7 - TOP - LEFT
        zenuv_entries.select_uv_borders(pie)
        # 9 - TOP - RIGHT
        zenuv_entries.select_seams_edges(pie)
        # 1 - BOTTOM - LEFT
        zenuv_entries.select_split_edges(pie)
        # 3 - BOTTOM - RIGHT
        zenuv_entries.select_overlapped_islands(pie)


# Context: 2D UV Editor Viewport
# Hotkey: Ctrl+Alt+Shift+RMB
class BLUEHOLE_MT_pie_UV_action_uvspecial(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_UV_action_uvspecial"  # named wrong
    bl_label = "Blue Hole: UV > Action (Special)"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        zenuv_entries.quadrify(pie)
        # 6 - RIGHT
        zenuv_entries.world_orient(pie)
        # 2 - BOTTOM
        blender_entries.uv_unwrap_conformal(pie)
        # 8 - TOP
        zenuv_entries.select_trim_tool(pie)
        # 7 - TOP - LEFT
        zenuv_entries.fix_trim_loop(pie)
        # 9 - TOP - RIGHT
        zenuv_entries.fit_to_trim_1(pie)
        # 1 - BOTTOM - LEFT
        zenuv_entries.pack_islands(pie)
        # 3 - BOTTOM - RIGHT
        zenuv_entries.relax_along_u(pie)


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

classes = (
    BLUEHOLE_MT_pie_UV_cursor,
    BLUEHOLE_MT_pie_UV_tool,
    BLUEHOLE_MT_pie_UV_action,
    BLUEHOLE_MT_pie_UV_action_select,
    BLUEHOLE_MT_pie_UV_action_uvspecial,
)


def register():
    log(Severity.DEBUG, f'{TOOL_NAME} Pie Menus', 'Registering...')

    for cls in classes:
        bpy.utils.register_class(cls)
        if is_verbose(VERBOSE_UI):
            log(Severity.DEBUG, f'{TOOL_NAME} Pie Menus', f'Registered: {cls.__name__}')

    log(Severity.DEBUG, f'{TOOL_NAME} Pie Menus', 'Registration complete')


def unregister():
    log(Severity.DEBUG, f'{TOOL_NAME} Pie Menus', 'Unregistering...')

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        if is_verbose(VERBOSE_UI):
            log(Severity.DEBUG, f'{TOOL_NAME} Pie Menus', f'Unregistered: {cls.__name__}')

    log(Severity.DEBUG, f'{TOOL_NAME} Pie Menus', 'Unregistration complete')
