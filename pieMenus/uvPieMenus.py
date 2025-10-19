# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "GNU General Public License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

from BlueHole.blenderUtils.debugUtils import print_debug_msg as print_debug_msg
from BlueHole.blenderUtils import filterUtils as filterUtils
from BlueHole.blenderUtils import fileUtils as fileUtils


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


def validate_uv_toolkit_and_on_version_2():
    # Validate UV Toolkit is enabled
    if filterUtils.check_addon_loaded('uv_toolkit'):
        # Validate version of UV Toolkit is 2.0, by looking for a file that is only in version 2.0
        # Reason for this is there are big changes between free and paid and links in menu only work in paid.
        file_pth_only_2 = fileUtils.get_resource_path_user() + '/scripts/addons/uv_toolkit/operators/export_setting.py'
        if fileUtils.is_file_path_valid(file_pth_only_2):
            return True
    return False


class PIE_MT_UV_Cursor(Menu):
    bl_idname = "PIE_MT_uv_cursor"
    bl_label = "Blue Hole: UV > Cursor"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        if validate_uv_toolkit_and_on_version_2():
            pie.operator("uv.toolkit_center_cursor_and_frame_all", text=" to Origin and Frame", icon='PIVOT_CURSOR')
        else:
            pie.separator()
        # 6 - RIGHT
        pie.operator("uv.snap_selected", text=" to Cursor", icon='RESTRICT_SELECT_OFF').target = 'CURSOR'
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        pie.operator("uv.snap_cursor", text=" to Selected", icon='PIVOT_CURSOR').target = 'SELECTED'
        # 9 - TOP - RIGHT
        pie.operator("uv.snap_selected", text=" to Cursor (Offset)", icon='RESTRICT_SELECT_OFF').target = 'CURSOR_OFFSET'
        # 1 - BOTTOM - LEFT
        pie.operator("uv.snap_cursor", text=" to Pixel", icon='PIVOT_CURSOR').target = 'PIXELS'
        # 3 - BOTTOM - RIGHT
        pie.operator("uv.snap_selected", text=" to Pixel", icon='RESTRICT_SELECT_OFF')


class PIE_MT_UV_Tools(Menu):
    bl_idname = "PIE_MT_uv_tools"
    bl_label = "Blue Hole: UV > Tools"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        if validate_uv_toolkit_and_on_version_2():
            # 4 - LEFT
            pie.operator("uv.toolkit_split_faces_move", text="Split Faces", icon='MOD_PHYSICS')
            # 6 - RIGHT
            pie.operator("uv.stitch", text="Stitch", icon='AUTOMERGE_ON')
            # 2 - BOTTOM
            pie.operator("uv.smart_project", text="Smart UV Project", icon='MOD_UVPROJECT')
            # 8 - TOP
            pie.operator("uv.toolkit_unwrap_selected", text="Unwrap Selected", icon='UV')
            # 7 - TOP - LEFT
            pie.operator("uv.toolkit_unwrap_selected", text="Unwrap", icon='GROUP_UVS')
            # 9 - TOP - RIGHT
            pie.operator("uv.toolkit_orient_islands", text="Orient Islands", icon='ORIENTATION_VIEW')
            # 1 - BOTTOM - LEFT
            pie.operator("uv.follow_active_quads", text="Follow Active Quads", icon='UV_FACESEL')
            # 3 - BOTTOM - RIGHT
            pie.operator("uv.toolkit_straighten", text="Straighten UVs", icon='SEQ_STRIP_DUPLICATE').gridify = False
        else:
            # TODO: Fill Pie Menu with options when UV Toolkit is not available
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.operator("uv.stitch", text="Stitch", icon='AUTOMERGE_ON')
            # 2 - BOTTOM
            pie.operator("uv.smart_project", text="Smart UV Project", icon='MOD_UVPROJECT')
            # 8 - TOP
            pie.separator()
            # 7 - TOP - LEFT
            pie.separator()
            # 9 - TOP - RIGHT
            pie.separator()
            # 1 - BOTTOM - LEFT
            pie.operator("uv.follow_active_quads", text="Follow Active Quads", icon='UV_FACESEL')
            # 3 - BOTTOM - RIGHT
            pie.separator()


classes = (
    PIE_MT_UV_Cursor,
    PIE_MT_UV_Tools
    )

addon_keymaps = []


def register():
    for cls in classes:
        print_debug_msg('Loading Pie Menu: ' + cls.bl_idname, show_verbose)
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
