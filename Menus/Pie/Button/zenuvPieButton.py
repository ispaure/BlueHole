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

from ..utilities import *
from ....Lib.commonUtils.osUtils import *

# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU BUTTON

addon_name = 'ZenUV'  # Name of addon to display if button cannot be loaded.


# TODO: Not marked as disabled for some reason even without zenuv (but won't work, complex error message)
def select_trim_tool(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "zuv.set_trim_tool",
        text="Select Trim Tool",
        icon='QUIT'
    )


def fix_trim_loop(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_scale_in_trim",
        text="Fix Trim Loop",
        icon='MESH_CYLINDER',
        props={"op_tr_scale_positive_only": (0.9, 1.0)}
    )


def fit_to_trim_1(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_fit_to_trim",
        text="Fit to Trim",
        icon='MOD_UVPROJECT',
        props={
            "auto_unwrap": False,
            "influence_mode_faces": False,
            "op_keep_proportion": False,
            "match_rotation": False,
            "op_order": 'ONE_BY_ONE',
            "fit_mode": 'TO_TRIM_T'
        }
    )


def git_to_trim_2(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_fit_to_trim",
        text="Fit to Trim",
        icon='MOD_UVPROJECT',
        props={
            "auto_unwrap": False,
            "influence_mode_faces": False,
            "op_keep_proportion": False,
            "match_rotation": True,
            "op_order": 'ONE_BY_ONE',
            "fit_mode": 'TO_TRIM_T'
        }
    )


def quadrify(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_quadrify",
        text="Quadrify",
        icon='MOD_TRIANGULATE'
    )


def world_orient(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_world_orient",
        text="World Orient",
        icon='ORIENTATION_NORMAL'
    )


def zen_unwrap(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_unwrap",
        text="Zen Unwrap",
        icon='UV',
        props={
            "action": 'DEFAULT',
            "ProcessingMode": 'SEL_ONLY',
            "packAfUnwrap": False,
            "MarkUnwrapped": False
        }
    )


def pack_islands(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_pack",
        text="Pack Islands",
        icon='MOD_BUILD',
        props={"display_uv": True}
    )


def relax_along_u(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_unwrap_constraint",
        text="Relax Along U",
        icon='AREA_SWAP',
        props={
            "influence_mode": 'ISLAND',
            "axis": 'U',
            "constraint_method": 'AXIS',
            "urp_method": 'ANGLE_BASED'
        }
    )


def auto_unwrap(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_auto_uv_unwrap",
        text="Auto Unwrap",
        icon='SHADERFX',
        props={"mark_seam_edges": False},
        platform_lst=[OS.WIN]
    )


def mark_by_angle(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_auto_mark",
        text="Mark by Angle",
        icon='NORMALS_VERTEX_FACE'
    )


def relax(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_relax",
        text="Relax",
        icon='OUTLINER_OB_ARMATURE'
    )


def quick_mirror(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_flip",
        text="Quick Mirror",
        icon='MOD_MIRROR',
        props={"flip_direction": 'HORIZONTAL'}
    )


def quick_fit(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_fit",
        text="Quick Fit",
        icon='CON_OBJECTSOLVER',
        props={
            "fit_mode": 'UV_AREA',
            "op_fit_axis": 'AUTO',
            "op_padding": 0.0,
            "op_keep_proportion": True,
            "match_rotation": False
        }
    )


def quick_rotate(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_rotate",
        text="Quick Rotate",
        icon='LOOP_FORWARDS',
        props={
            "rotation_mode": 'DIRECTION',
            "direction": 'CW',
            "tr_rot_inc": 90
        }
    )


def merge_verts(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_merge_uv_verts",
        text="Merge UV Verts",
        icon='AUTOMERGE_ON'
    )


def match_stitch(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_match_stitch",
        text="Match & Stitch",
        icon='AREA_JOIN_LEFT'
    )


def get_tx_density(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_get_texel_density",
        text="Get Texture Density",
        icon='IMPORT'
    )


def set_tx_density(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_set_texel_density",
        text="Set Texture Density",
        icon='EXPORT',
        props={"global_mode": True}
    )


def select_stretched_faces(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_select_stretched_faces",
        text="Select Stretched Faces",
        icon='VIEW_PERSPECTIVE'
    )


def select_flipped_islands(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_select_flipped",
        text="Select Flipped Islands",
        icon='SETTINGS'
    )


def select_similar_islands(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_select_similar",
        text="Select Similar Islands",
        icon='OUTLINER_OB_POINTCLOUD'
    )


def select_interseams_loop(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_select_loop",
        text="Select Interseams Loop",
        icon='MOD_LENGTH'
    )


def select_uv_borders(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_select_uv_borders",
        text="Select UV Borders",
        icon='OBJECT_HIDDEN'
    )


def select_seams_edges(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "mesh.zenuv_select_seams",
        text="Select Seams Edges",
        icon='MATSPHERE'
    )


def select_split_edges(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_select_splits_edges",
        text="Select Splits Edges",
        icon='MOD_PHYSICS'
    )


def select_overlapped_islands(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.zenuv_select_uv_overlap",
        text="Select Overlapped Islands",
        icon='OVERLAY'
    )
