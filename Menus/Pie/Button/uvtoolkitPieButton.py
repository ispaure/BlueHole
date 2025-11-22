"""
Pie Menus pertaining to the UV Toolkit Addon (NOTE: Pending Deprecation)
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
from BlueHole.blenderUtils import filterUtils as filterUtils
from BlueHole.blenderUtils import fileUtils as fileUtils

# ----------------------------------------------------------------------------------------------------------------------
# MISC


def validate_uv_toolkit_and_on_version_2():
    # Validate UV Toolkit is enabled
    if addonUtils.is_addon_enabled_and_loaded('uv_toolkit'):
        # Validate version of UV Toolkit is 2.0, by looking for a file that is only in version 2.0
        # Reason for this is there are big changes between free and paid and links in menu only work in paid.
        file_pth_only_2 = fileUtils.get_resource_path_user() + '/scripts/addons/uv_toolkit/operators/export_setting.py'
        if fileUtils.is_file_path_valid(file_pth_only_2):
            return True
    return False


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU BUTTON


def split_faces(pie):
    if addonUtils.is_addon_enabled_and_loaded('uv_toolkit'):
        pie.operator("uv.toolkit_split_faces_move", text="Split Faces", icon='MOD_PHYSICS')
    else:
        pie.operator("wm.disabled_addon_uv_toolkit", text="Can't Show; UV Toolkit add-on disabled!!!", icon='ERROR')


def unwrap_selected(pie):
    if addonUtils.is_addon_enabled_and_loaded('uv_toolkit'):
        pie.operator("uv.toolkit_unwrap_selected", text="Unwrap Selected", icon='UV')
    else:
        pie.operator("wm.disabled_addon_uv_toolkit", text="Can't Show; UV Toolkit add-on disabled!!!", icon='ERROR')


def orient_islands(pie):
    if addonUtils.is_addon_enabled_and_loaded('uv_toolkit'):
        pie.operator("uv.toolkit_orient_islands", text="Orient Islands", icon='ORIENTATION_VIEW')
    else:
        pie.operator("wm.disabled_addon_uv_toolkit", text="Can't Show; UV Toolkit add-on disabled!!!", icon='ERROR')


def straighten_uv(pie):
    if addonUtils.is_addon_enabled_and_loaded('uv_toolkit'):
        op = pie.operator("uv.toolkit_straighten", text="Straighten UVs", icon='SEQ_STRIP_DUPLICATE')
        op.gridify = False
    else:
        pie.operator("wm.disabled_addon_uv_toolkit", text="Can't Show; UV Toolkit add-on disabled!!!", icon='ERROR')


def center_cursor_frame_all_req_ver_2(pie):
    if validate_uv_toolkit_and_on_version_2():
        pie.operator("uv.toolkit_center_cursor_and_frame_all", text=" to Origin and Frame", icon='PIVOT_CURSOR')
    else:
        pie.operator("wm.disabled_addon_uv_toolkit", text="Can't Show; UV Toolkit add-on disabled!!!", icon='ERROR')
