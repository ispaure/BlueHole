"""
Pie Menu operators pertaining to the UV Toolkit Addon (NOTE: Pending Deprecation)
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

# ----------------------------------------------------------------------------------------------------------------------
# MISC

addon_name = 'UV Toolkit (Version 2+)'  # Name of addon to display if button cannot be loaded.


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU BUTTON


def split_faces(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.toolkit_split_faces_move",
        text="Split Faces",
        icon='MOD_PHYSICS')


def unwrap_selected(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.toolkit_unwrap_selected",
        text="Unwrap Selected",
        icon='UV')


def orient_islands(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.toolkit_orient_islands",
        text="Orient Islands",
        icon='ORIENTATION_VIEW')


def straighten_uv(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.toolkit_straighten",
        text="Straighten UVs",
        icon='SEQ_STRIP_DUPLICATE',
        props={"gridify": False})


def center_cursor_frame_all_req_ver_2(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "uv.toolkit_center_cursor_and_frame_all",
        text=" to Origin and Frame",
        icon='PIVOT_CURSOR')
