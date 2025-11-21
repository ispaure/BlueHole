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
from BlueHole.blenderUtils import filterUtils as filterUtils
from BlueHole.blenderUtils import fileUtils as fileUtils
import BlueHole.blenderUtils.addonUtils as addonUtils


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


# ----------------------------------------------------------------------------------------------------------------------
# MISC

def validate_uv_toolkit_and_on_version_2():
    # Validate UV Toolkit is enabled
    if filterUtils.check_addon_loaded('uv_toolkit'):
        # Validate version of UV Toolkit is 2.0, by looking for a file that is only in version 2.0
        # Reason for this is there are big changes between free and paid and links in menu only work in paid.
        file_pth_only_2 = fileUtils.get_resource_path_user() + '/scripts/addons/uv_toolkit/operators/export_setting.py'
        if fileUtils.is_file_path_valid(file_pth_only_2):
            return True
    return False


# ----------------------------------------------------------------------------------------------------------------------
# Buttons with actions


def button_activate_trim_tool(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        try:
            pie.operator("zuv.set_trim_tool", text="Select Trim Tool", icon='QUIT')
        except:
            pie.operator("wm.disabled_addon_zen_uv", text="Not Working. Sorry!", icon='ERROR')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_zen_uv_fix_trim_loop(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        op = pie.operator("uv.zenuv_scale_in_trim", text="Fix Trim Loop", icon='MESH_CYLINDER')
        op.op_tr_scale_positive_only = (0.9, 1.0)
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_fit_to_trim(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        op = pie.operator("uv.zenuv_fit_to_trim", text="Fit to Trim", icon='MOD_UVPROJECT')
        op.auto_unwrap = False
        op.influence_mode_faces = False
        op.op_keep_proportion = False
        op.match_rotation = False
        op.op_order = 'ONE_BY_ONE'
        op.fit_mode = 'TO_TRIM_T'
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_fit_to_trim_2(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        op = pie.operator("uv.zenuv_fit_to_trim", text="Fit to Trim", icon='MOD_UVPROJECT')
        op.auto_unwrap = False
        op.influence_mode_faces = False
        op.op_keep_proportion = False
        op.match_rotation = True
        op.op_order = 'ONE_BY_ONE'
        op.fit_mode = 'TO_TRIM_T'
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_quadrify(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_quadrify", text="Quadrify", icon='MOD_TRIANGULATE')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_world_orient(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_world_orient", text="World Orient", icon='ORIENTATION_NORMAL')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_zen_unwrap(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        op = pie.operator('uv.zenuv_unwrap', text='Zen Unwrap', icon='UV')
        op.action = 'DEFAULT'
        op.ProcessingMode = 'SEL_ONLY'
        op.packAfUnwrap = False
        op.MarkUnwrapped = False


def button_pack_islands(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        op = pie.operator('uv.zenuv_pack', text='Pack Islands', icon='MOD_BUILD')
        op.display_uv = True
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_relax_along_u(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        op = pie.operator("uv.zenuv_unwrap_constraint", text="Relax Along U", icon='AREA_SWAP')
        op.influence_mode = 'ISLAND'
        op.axis = 'U'
        op.constraint_method = 'AXIS'
        op.urp_method = 'ANGLE_BASED'
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_zen_uv_auto_unwrap(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        # TODO: This requires ministry of flat. Does not seem to work on macOS, maybe windows too? Investigate.
        try:
            op = pie.operator("uv.zenuv_auto_uv_unwrap", text="Auto Unwrap", icon='SHADERFX')
            op.mark_seam_edges = False
        except:
            pie.operator("wm.disabled_addon_zen_uv", text="Ministry of Flat not Working. Sorry!", icon='ERROR')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_zen_uv_mark_by_angle(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_auto_mark", text="Mark by Angle", icon='NORMALS_VERTEX_FACE')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_dreamuv_hotspotter(pie):
    if addonUtils.is_addon_enabled_and_loaded('DreamUV') or addonUtils.is_addon_enabled_and_loaded('Blender_DreamUV-master'):
        pie.operator("view3d.dreamuv_hotspotter", text="HotSpot", icon='UV_DATA')
    else:
        pie.operator("wm.disabled_addon_dreamuv", text="Can't Show; DreamUV add-on disabled!!!", icon='ERROR')


def button_zen_uv_relax(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_relax", text="Relax", icon='OUTLINER_OB_ARMATURE')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_zen_uv_quick_mirror(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        op = pie.operator("uv.zenuv_flip", text="Quick Mirror", icon='MOD_MIRROR')
        op.flip_direction = 'HORIZONTAL'
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_zen_uv_quick_fit(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        op = pie.operator("uv.zenuv_fit", text="Quick Fit", icon='CON_OBJECTSOLVER')
        op.fit_mode = 'UV_AREA'
        op.op_fit_axis = 'AUTO'
        op.op_padding = 0.0
        op.op_keep_proportion = True
        op.match_rotation = False
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_zen_uv_quick_rotate(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        op = pie.operator("uv.zenuv_rotate", text="Quick Rotate", icon='LOOP_FORWARDS')
        op.rotation_mode = 'DIRECTION'
        op.direction = 'CW'
        op.tr_rot_inc = 90
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_zen_uv_merge_verts(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_merge_uv_verts", text="Merge UV Verts", icon='AUTOMERGE_ON')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_zen_uv_match_stitch(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_match_stitch", text="Match & Stitch", icon='AREA_JOIN_LEFT')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')

def button_zen_uv_texture_density_get(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_get_texel_density", text="Get Texture Density", icon='IMPORT')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')

def button_zen_uv_texture_density_set(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        op = pie.operator("uv.zenuv_set_texel_density", text="Set Texture Density", icon='EXPORT')
        op.global_mode = True
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')

def button_zen_uv_select_stretched_faces(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_select_stretched_faces", text="Select Stretched Faces", icon='VIEW_PERSPECTIVE')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_zen_uv_select_flipped_islands(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_select_flipped", text="Select Flipped Islands", icon='SETTINGS')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_zen_uv_select_similar_islands(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_select_similar", text="Select Similar Islands", icon='OUTLINER_OB_POINTCLOUD')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_zen_uv_select_interseams_loop(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_select_loop", text="Select Interseams Loop", icon='MOD_LENGTH')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_zen_uv_select_uv_borders(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_select_uv_borders", text="Select UV Borders", icon='OBJECT_HIDDEN')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_zen_uv_select_seams_edges(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("mesh.zenuv_select_seams", text="Select Seams Edges", icon='MATSPHERE')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_zen_uv_select_split_edges(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_select_splits_edges", text="Select Splits Edges", icon='MOD_PHYSICS')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_zen_uv_select_overlapped_islands(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_select_uv_overlap", text="Select Overlapped Islands", icon='OVERLAY')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def button_uv_toolkit_split_faces(pie):
    if addonUtils.is_addon_enabled_and_loaded('uv_toolkit'):
        pie.operator("uv.toolkit_split_faces_move", text="Split Faces", icon='MOD_PHYSICS')
    else:
        pie.operator("wm.disabled_addon_uv_toolkit", text="Can't Show; UV Toolkit add-on disabled!!!", icon='ERROR')


def button_uv_toolkit_unwrap_selected(pie):
    if addonUtils.is_addon_enabled_and_loaded('uv_toolkit'):
        pie.operator("uv.toolkit_unwrap_selected", text="Unwrap Selected", icon='UV')
    else:
        pie.operator("wm.disabled_addon_uv_toolkit", text="Can't Show; UV Toolkit add-on disabled!!!", icon='ERROR')


def button_uv_toolkit_orient_islands(pie):
    if addonUtils.is_addon_enabled_and_loaded('uv_toolkit'):
        pie.operator("uv.toolkit_orient_islands", text="Orient Islands", icon='ORIENTATION_VIEW')
    else:
        pie.operator("wm.disabled_addon_uv_toolkit", text="Can't Show; UV Toolkit add-on disabled!!!", icon='ERROR')


def button_uv_toolkit_straighten_uv(pie):
    if addonUtils.is_addon_enabled_and_loaded('uv_toolkit'):
        op = pie.operator("uv.toolkit_straighten", text="Straighten UVs", icon='SEQ_STRIP_DUPLICATE')
        op.gridify = False
    else:
        pie.operator("wm.disabled_addon_uv_toolkit", text="Can't Show; UV Toolkit add-on disabled!!!", icon='ERROR')


def button_uv_toolkit_ver_2_center_cursor_frame_all(pie):
    if validate_uv_toolkit_and_on_version_2():
        pie.operator("uv.toolkit_center_cursor_and_frame_all", text=" to Origin and Frame", icon='PIVOT_CURSOR')
    else:
        pie.operator("wm.disabled_addon_uv_toolkit", text="Can't Show; UV Toolkit add-on disabled!!!", icon='ERROR')


def button_clear_seam(pie):
    op = pie.operator("mesh.mark_seam", text="Clear Seam", icon='CANCEL_LARGE')
    op.clear = True


def button_mark_seam(pie):
    op = pie.operator("mesh.mark_seam", text="Mark Seam", icon='CHECKMARK')
    op.clear = False


def button_uv_stitch(pie):
    pie.operator("uv.stitch", text="Stitch", icon='AUTOMERGE_ON')


def button_follow_active_quads(pie):
    pie.operator("uv.follow_active_quads", text="Follow Active Quads", icon='UV_FACESEL')


def button_uv_smart_project(pie):
    pie.operator("uv.smart_project", text="Smart UV Project", icon='UV_VERTEXSEL')


def button_snap_selected_to_cursor(pie):
    op = pie.operator("uv.snap_selected", text=" to Cursor", icon='RESTRICT_SELECT_OFF')
    op.target = 'CURSOR'


def button_snap_cursor_to_selected(pie):
    op = pie.operator("uv.snap_cursor", text=" to Selected", icon='PIVOT_CURSOR')
    op.target = 'SELECTED'


def button_snap_selected_to_cursor_offset(pie):
    op = pie.operator("uv.snap_selected", text=" to Cursor (Offset)", icon='RESTRICT_SELECT_OFF')
    op.target = 'CURSOR_OFFSET'


def button_snap_cursor_to_pixel(pie):
    op = pie.operator("uv.snap_cursor", text=" to Pixel", icon='PIVOT_CURSOR')
    op.target = 'PIXELS'


def button_snap_selected_to_pixel(pie):
    pie.operator("uv.snap_selected", text=" to Pixel", icon='RESTRICT_SELECT_OFF')


def button_uv_cube_project(pie):
    pie.operator("uv.cube_project", text='Cube Projection')


def button_uv_split_island(pie):
    pie.operator('uv.select_split', text='Split Island', icon='MOD_PHYSICS')

# ----------------------------------------------------------------------------------------------------------------------
# Menus laid out


# 2D UV Editor Viewport Ctrl+Shift+Right-Click
class PIE_MT_UV_Cursor(Menu):
    bl_idname = "PIE_MT_uv_cursor"  # named wrong
    bl_label = "Blue Hole: UV > Cursor"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        button_uv_toolkit_ver_2_center_cursor_frame_all(pie)
        # 6 - RIGHT
        button_snap_selected_to_cursor(pie)
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        button_snap_cursor_to_selected(pie)
        # 9 - TOP - RIGHT
        button_snap_selected_to_cursor_offset(pie)
        # 1 - BOTTOM - LEFT
        button_snap_cursor_to_pixel(pie)
        # 3 - BOTTOM - RIGHT
        button_snap_selected_to_pixel(pie)


# 2D UV Editor Viewport Shift+Right-Click
class PIE_MT_UV_Tools(Menu):
    bl_idname = "PIE_MT_uv_tools"  # named wrong
    bl_label = "Blue Hole: UV > Tools"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # # OLD VERSION
        # # 4 - LEFT
        # button_uv_toolkit_ver_2_center_cursor_frame_all(pie)
        # # 6 - RIGHT
        # button_snap_selected_to_cursor(pie)
        # # 2 - BOTTOM
        # pie.separator()
        # # 8 - TOP
        # pie.separator()
        # # 7 - TOP - LEFT
        # button_snap_cursor_to_selected(pie)
        # # 9 - TOP - RIGHT
        # button_snap_selected_to_cursor_offset(pie)
        # # 1 - BOTTOM - LEFT
        # button_snap_cursor_to_pixel(pie)
        # # 3 - BOTTOM - RIGHT
        # button_snap_selected_to_pixel(pie)

        # New version End of November 2025
        # 4 - LEFT
        button_uv_smart_project(pie)
        # 6 - RIGHT
        button_zen_uv_relax(pie)
        # 2 - BOTTOM
        button_zen_unwrap(pie)
        # 8 - TOP
        button_zen_uv_quick_rotate(pie)
        # 7 - TOP - LEFT
        button_zen_uv_quick_mirror(pie)
        # 9 - TOP - RIGHT
        button_zen_uv_quick_fit(pie)
        # 1 - BOTTOM - LEFT
        button_zen_uv_auto_unwrap(pie)
        # 3 - BOTTOM - RIGHT
        button_relax_along_u(pie)


# 2D UV Editor Viewport Ctrl+Right-Click
class PIE_MT_UV_Action(Menu):
    bl_idname = "PIE_MT_uv_action"  # named wrong
    bl_label = "Blue Hole: UV > Action"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # New version end of november 2025
        # 4 - LEFT
        button_quadrify(pie)
        # 6 - RIGHT
        button_world_orient(pie)
        # 2 - BOTTOM
        button_zen_uv_merge_verts(pie)
        # 8 - TOP
        pie.operator("wm.call_menu_pie", text="Select...", icon='TRIA_UP').name = 'PIE_MT_uv_action_select'
        # 7 - TOP - LEFT
        button_zen_uv_texture_density_get(pie)
        # 9 - TOP - RIGHT
        button_zen_uv_texture_density_set(pie)
        # 1 - BOTTOM - LEFT
        button_uv_split_island(pie)
        # 3 - BOTTOM - RIGHT
        button_uv_stitch(pie)


class PIE_MT_UV_Action_Select(Menu):
    bl_idname = "PIE_MT_uv_action_select"  # named wrong
    bl_label = "Blue Hole: UV > Action > Select"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # New menu end of nov 2025
        # 4 - LEFT
        button_zen_uv_select_stretched_faces(pie)
        # 6 - RIGHT
        button_zen_uv_select_flipped_islands(pie)
        # 2 - BOTTOM
        button_zen_uv_select_similar_islands(pie)
        # 8 - TOP
        button_zen_uv_select_interseams_loop(pie)
        # 7 - TOP - LEFT
        button_zen_uv_select_uv_borders(pie)
        # 9 - TOP - RIGHT
        button_zen_uv_select_seams_edges(pie)
        # 1 - BOTTOM - LEFT
        button_zen_uv_select_split_edges(pie)
        # 3 - BOTTOM - RIGHT
        button_zen_uv_select_overlapped_islands(pie)


# 2D UV Editor Viewport Ctrl+Alt+Shift+Right-Click
class PIE_MT_UV_Action_Special(Menu):
    bl_idname = "PIE_MT_uv_action_special"  # named wrong
    bl_label = "Blue Hole: UV > Action (Special)"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # New Pie Menu Nov 2025
        # 4 - LEFT
        button_quadrify(pie)
        # 6 - RIGHT
        button_world_orient(pie)
        # 2 - BOTTOM
        button_zen_unwrap(pie)
        # 8 - TOP
        button_activate_trim_tool(pie)
        # 7 - TOP - LEFT
        button_zen_uv_fix_trim_loop(pie)
        # 9 - TOP - RIGHT
        button_fit_to_trim(pie)
        # 1 - BOTTOM - LEFT
        button_pack_islands(pie)
        # 3 - BOTTOM - RIGHT
        button_relax_along_u(pie)


# 3D Viewport (Vertex/Edge/Vert) Ctrl+Alt+Shift+Right-Click
class PIE_MT_UV_Mesh_Action_UVSpecial(Menu):
    bl_idname = "PIE_MT_mesh_action_uvspecial"  # named wrong
    bl_label = "Blue Hole: Mesh > Action (UV Special)"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # New Pie Menu Nov 2025
        # 4 - LEFT
        button_clear_seam(pie)
        # 6 - RIGHT
        button_mark_seam(pie)
        # 2 - BOTTOM
        button_zen_unwrap(pie)
        # 8 - TOP
        button_dreamuv_hotspotter(pie)
        # 7 - TOP - LEFT
        button_zen_uv_fix_trim_loop(pie)
        # 9 - TOP - RIGHT
        button_fit_to_trim_2(pie)
        # 1 - BOTTOM - LEFT
        button_zen_uv_auto_unwrap(pie)
        # 3 - BOTTOM - RIGHT
        button_zen_uv_mark_by_angle(pie)
        # Removed option
        # pie.operator("uv.unwrap", text="Unwrap", icon='UV').method = 'CONFORMAL'


classes = (PIE_MT_UV_Cursor,
           PIE_MT_UV_Tools,
           PIE_MT_UV_Action,
           PIE_MT_UV_Action_Select,
           PIE_MT_UV_Action_Special,
           PIE_MT_UV_Mesh_Action_UVSpecial)

addon_keymaps = []


def register():
    for cls in classes:
        print_debug_msg('Loading Pie Menu: ' + cls.bl_idname, show_verbose)
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
