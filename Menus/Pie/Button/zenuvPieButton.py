"""
Pie Menu operators pertaining to ZenUV Addon.
"""

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

import BlueHole.blenderUtils.addonUtils as addonUtils

# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU BUTTON


def select_trim_tool(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        try:
            pie.operator("zuv.set_trim_tool", text="Select Trim Tool", icon='QUIT')
        except:
            pie.operator("wm.disabled_addon_zen_uv", text="Not Working. Sorry!", icon='ERROR')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def fix_trim_loop(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        op = pie.operator("uv.zenuv_scale_in_trim", text="Fix Trim Loop", icon='MESH_CYLINDER')
        op.op_tr_scale_positive_only = (0.9, 1.0)
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def fit_to_trim_1(pie):
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


def git_to_trim_2(pie):
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


def quadrify(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_quadrify", text="Quadrify", icon='MOD_TRIANGULATE')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def world_orient(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_world_orient", text="World Orient", icon='ORIENTATION_NORMAL')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def zen_unwrap(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        op = pie.operator('uv.zenuv_unwrap', text='Zen Unwrap', icon='UV')
        op.action = 'DEFAULT'
        op.ProcessingMode = 'SEL_ONLY'
        op.packAfUnwrap = False
        op.MarkUnwrapped = False


def pack_islands(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        op = pie.operator('uv.zenuv_pack', text='Pack Islands', icon='MOD_BUILD')
        op.display_uv = True
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def relax_along_u(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        op = pie.operator("uv.zenuv_unwrap_constraint", text="Relax Along U", icon='AREA_SWAP')
        op.influence_mode = 'ISLAND'
        op.axis = 'U'
        op.constraint_method = 'AXIS'
        op.urp_method = 'ANGLE_BASED'
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def auto_unwrap(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        # TODO: This requires ministry of flat. Does not seem to work on macOS, maybe windows too? Investigate.
        try:
            op = pie.operator("uv.zenuv_auto_uv_unwrap", text="Auto Unwrap", icon='SHADERFX')
            op.mark_seam_edges = False
        except:
            pie.operator("wm.disabled_addon_zen_uv", text="Ministry of Flat not Working. Sorry!", icon='ERROR')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def mark_by_angle(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_auto_mark", text="Mark by Angle", icon='NORMALS_VERTEX_FACE')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def relax(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_relax", text="Relax", icon='OUTLINER_OB_ARMATURE')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def quick_mirror(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        op = pie.operator("uv.zenuv_flip", text="Quick Mirror", icon='MOD_MIRROR')
        op.flip_direction = 'HORIZONTAL'
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def quick_fit(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        op = pie.operator("uv.zenuv_fit", text="Quick Fit", icon='CON_OBJECTSOLVER')
        op.fit_mode = 'UV_AREA'
        op.op_fit_axis = 'AUTO'
        op.op_padding = 0.0
        op.op_keep_proportion = True
        op.match_rotation = False
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def quick_rotate(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        op = pie.operator("uv.zenuv_rotate", text="Quick Rotate", icon='LOOP_FORWARDS')
        op.rotation_mode = 'DIRECTION'
        op.direction = 'CW'
        op.tr_rot_inc = 90
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def merge_verts(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_merge_uv_verts", text="Merge UV Verts", icon='AUTOMERGE_ON')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def match_stitch(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_match_stitch", text="Match & Stitch", icon='AREA_JOIN_LEFT')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def get_tx_density(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_get_texel_density", text="Get Texture Density", icon='IMPORT')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def set_tx_density(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        op = pie.operator("uv.zenuv_set_texel_density", text="Set Texture Density", icon='EXPORT')
        op.global_mode = True
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def select_stretched_faces(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_select_stretched_faces", text="Select Stretched Faces", icon='VIEW_PERSPECTIVE')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def select_flipped_islands(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_select_flipped", text="Select Flipped Islands", icon='SETTINGS')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def select_similar_islands(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_select_similar", text="Select Similar Islands", icon='OUTLINER_OB_POINTCLOUD')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def select_interseams_loop(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_select_loop", text="Select Interseams Loop", icon='MOD_LENGTH')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def select_uv_borders(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_select_uv_borders", text="Select UV Borders", icon='OBJECT_HIDDEN')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def select_seams_edges(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("mesh.zenuv_select_seams", text="Select Seams Edges", icon='MATSPHERE')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def select_split_edges(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_select_splits_edges", text="Select Splits Edges", icon='MOD_PHYSICS')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


def select_overlapped_islands(pie):
    if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
        pie.operator("uv.zenuv_select_uv_overlap", text="Select Overlapped Islands", icon='OVERLAY')
    else:
        pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')
