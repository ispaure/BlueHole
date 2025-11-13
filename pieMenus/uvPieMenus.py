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

        # # Previous Pie Menu
        # # 4 - LEFT
        # if validate_uv_toolkit_and_on_version_2():
        #     pie.operator("uv.toolkit_center_cursor_and_frame_all", text=" to Origin and Frame", icon='PIVOT_CURSOR')
        # else:
        #     pie.separator()
        # # 6 - RIGHT
        # pie.operator("uv.snap_selected", text=" to Cursor", icon='RESTRICT_SELECT_OFF').target = 'CURSOR'
        # # 2 - BOTTOM
        # pie.separator()
        # # 8 - TOP
        # pie.separator()
        # # 7 - TOP - LEFT
        # pie.operator("uv.snap_cursor", text=" to Selected", icon='PIVOT_CURSOR').target = 'SELECTED'
        # # 9 - TOP - RIGHT
        # pie.operator("uv.snap_selected", text=" to Cursor (Offset)", icon='RESTRICT_SELECT_OFF').target = 'CURSOR_OFFSET'
        # # 1 - BOTTOM - LEFT
        # pie.operator("uv.snap_cursor", text=" to Pixel", icon='PIVOT_CURSOR').target = 'PIXELS'
        # # 3 - BOTTOM - RIGHT
        # pie.operator("uv.snap_selected", text=" to Pixel", icon='RESTRICT_SELECT_OFF')

        # New Pie Menu Nov 2025
        # 4 - LEFT
        if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
            op = pie.operator("uv.zenuv_unwrap_constraint", text="Relax Along U")
            op.influence_mode = 'ISLAND'
            op.axis = 'U'
            op.constraint_method = 'AXIS'
            op.urp_method = 'ANGLE_BASED'
        else:
            pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')
        # 6 - RIGHT
        pie.separator()
        # 2 - BOTTOM
        pie.operator("wm.disabled_addon_zen_uv", text="Not Working. Sorry!", icon='ERROR')
        # TODO: This is unorthodox. See if there is a way to make this work (it does in Pie Menu Editor for some reason) It's not an operator.
        # try:
        #     pie.operator("C.scene.zen_uv.ui.uv_tool.select_trim", text="Trim Select Mode")
        # except:
        #     pie.operator("wm.disabled_addon_zen_uv", text="Not Working. Sorry!", icon='ERROR')
        # 8 - TOP
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
        # 7 - TOP - LEFT
        if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
            pie.operator("uv.zenuv_scale_in_trim", text="Fix Trim Loop").op_tr_scale_positive_only = (0.8999999761581421, 1.0)
        else:
            pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')
        # 9 - TOP - RIGHT
        if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
            pie.operator("uv.zenuv_world_orient", text="World Orient", icon='ORIENTATION_NORMAL')
        else:
            pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')
        # 1 - BOTTOM - LEFT
        if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
            pie.operator("uv.zenuv_quadrify", text="Quadrify", icon='MOD_TRIANGULATE')
        else:
            pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')
        # 3 - BOTTOM - RIGHT
        if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
            pie.operator("uv.zuv_activate_tool", text="Activate Trim Tool", icon='UV').mode = 'ACTIVATE'
        else:
            pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')


class PIE_MT_UV_Tools(Menu):
    bl_idname = "PIE_MT_uv_tools"
    bl_label = "Blue Hole: UV > Tools"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # # Previous Pie Menu
        # if validate_uv_toolkit_and_on_version_2():
        #     # 4 - LEFT
        #     pie.operator("uv.toolkit_split_faces_move", text="Split Faces", icon='MOD_PHYSICS')
        #     # 6 - RIGHT
        #     pie.operator("uv.stitch", text="Stitch", icon='AUTOMERGE_ON')
        #     # 2 - BOTTOM
        #     pie.operator("uv.smart_project", text="Smart UV Project", icon='MOD_UVPROJECT')
        #     # 8 - TOP
        #     pie.operator("uv.toolkit_unwrap_selected", text="Unwrap Selected", icon='UV')
        #     # 7 - TOP - LEFT
        #     pie.operator("uv.toolkit_unwrap_selected", text="Unwrap", icon='GROUP_UVS')
        #     # 9 - TOP - RIGHT
        #     pie.operator("uv.toolkit_orient_islands", text="Orient Islands", icon='ORIENTATION_VIEW')
        #     # 1 - BOTTOM - LEFT
        #     pie.operator("uv.follow_active_quads", text="Follow Active Quads", icon='UV_FACESEL')
        #     # 3 - BOTTOM - RIGHT
        #     pie.operator("uv.toolkit_straighten", text="Straighten UVs", icon='SEQ_STRIP_DUPLICATE').gridify = False
        # else:
        #     # 4 - LEFT
        #     pie.separator()
        #     # 6 - RIGHT
        #     pie.operator("uv.stitch", text="Stitch", icon='AUTOMERGE_ON')
        #     # 2 - BOTTOM
        #     pie.operator("uv.smart_project", text="Smart UV Project", icon='MOD_UVPROJECT')
        #     # 8 - TOP
        #     pie.separator()
        #     # 7 - TOP - LEFT
        #     pie.separator()
        #     # 9 - TOP - RIGHT
        #     pie.separator()
        #     # 1 - BOTTOM - LEFT
        #     pie.operator("uv.follow_active_quads", text="Follow Active Quads", icon='UV_FACESEL')
        #     # 3 - BOTTOM - RIGHT
        #     pie.separator()

        # New Pie Menu Nov 2025
        # 4 - LEFT
        pie.operator("mesh.mark_seam", text="Clear Seam", icon='CANCEL_LARGE').clear = True
        # 6 - RIGHT
        pie.operator("mesh.mark_seam", text="Mark Seam", icon='CHECKBOX_HLT').clear = False
        # 2 - BOTTOM
        if addonUtils.is_addon_enabled_and_loaded('DreamUV') or addonUtils.is_addon_enabled_and_loaded('Blender_DreamUV-master'):
            pie.operator("view3d.dreamuv_hotspotter", text="HotSpot", icon='UV_DATA')
        else:
            pie.operator("wm.disabled_addon_dreamuv", text="Can't Show; DreamUV add-on disabled!!!", icon='ERROR')
        # 8 - TOP
        if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
            op = pie.operator("uv.zenuv_fit_to_trim", text="Fit to Trim", icon='MOD_UVPROJECT')
            op.auto_unwrap = True
            op.influence_mode_faces = True
            op.op_keep_proportion = True
            op.match_rotation = True
        else:
            pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')
        # 7 - TOP - LEFT
        if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
            pie.operator("uv.zenuv_scale_in_trim", text="Fix Trim Loop").op_tr_scale_positive_only = (0.8999999761581421, 1.0)
        else:
            pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')
        # 9 - TOP - RIGHT
        if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
            pie.operator("uv.zenuv_auto_mark", text="Mark by Angle", icon='NORMALS_VERTEX_FACE')
        else:
            pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')
        # 1 - BOTTOM - LEFT
        if addonUtils.is_addon_enabled_and_loaded('ZenUV'):
            # TODO: This requires ministry of flat. Does not seem to work on macOS, maybe windows too? Investigate.
            try:
                pie.operator("uv.zenuv_auto_uv_unwrap", text="Auto Unwrap", icon='MOD_TRIANGULATE').mark_seam_edges = False
            except:
                pie.operator("wm.disabled_addon_zen_uv", text="Ministry of Flat not Working. Sorry!", icon='ERROR')
        else:
            pie.operator("wm.disabled_addon_zen_uv", text="Can't Show; Zen UV add-on disabled!!!", icon='ERROR')
        # 3 - BOTTOM - RIGHT
        pie.operator("uv.unwrap", text="Unwrap", icon='UV').method = 'CONFORMAL'


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
