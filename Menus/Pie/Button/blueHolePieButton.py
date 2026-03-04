"""
Pie Menu operators pertaining to Blender (Vanilla). These do not rely on external resources.
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

# Blue Hole
from ....Lib.commonUtils.debugUtils import *
from ....preferences.prefs import *
from ....Operators import sendOp


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU BUTTON


# ----------------------------------------------------------------------------------------------------------------------
# SCENE


def add_asset_hierarchy(pie):
    pie.operator("wm.bh_scene_add_asset_hierarchy", text="Add ASSET HIERARCHY", icon='OUTLINER')


# ----------------------------------------------------------------------------------------------------------------------
# SUPPORT


def open_keymaps_list(pie):
    pie.operator("wm.bh_help_open_keymaps_list", text="Keymaps List", icon='URL')


def submit_feedback(pie):
    pie.operator("wm.bh_help_submit_feedback", text="Submit Feedback", icon='FUND')


def open_guide(pie):
    pie.operator("wm.bh_help_open_guide", text="Online Guide", icon='HELP')


def open_pie_menus_list(pie):
    pie.operator("wm.bh_help_open_pie_menus_list", text="Pie Menus List", icon='URL')


# ----------------------------------------------------------------------------------------------------------------------
# THEMES


def apply_theme_zen_light(pie):
    pie.operator("wm.bh_theme_zen", text="Zen Light")


def apply_theme_zen_dark(pie):
    pie.operator("wm.bh_theme_zendark", text="Zen Dark")


def apply_theme_sky(pie):
    pie.operator("wm.bh_theme_sky", text="Sky")


def apply_theme_modo(pie):
    pie.operator("wm.bh_theme_modo", text="Modo")


def apply_theme_blender_light(pie):
    pie.operator("wm.bh_theme_blender_light", text="Blender Light")


def apply_theme_blender_dark(pie):
    pie.operator("wm.bh_theme_blender_dark", text="Blender Dark")


def apply_theme_white(pie):
    pie.operator("wm.bh_theme_white", text="White")


def apply_theme_deep_grey(pie):
    pie.operator("wm.bh_theme_deep_grey", text="Deep Grey")


# ----------------------------------------------------------------------------------------------------------------------
# DIRECTORIES


def open_workspace_root(pie):
    pie.operator("wm.bh_dir_open_workspace_root", text="Open WORKSPACE ROOT Folder", icon='FILEBROWSER')


def open_unity_assets(pie):
    pie.operator('wm.bh_dir_open_unity_assets_current_exp_dir', text="Open UNITY ASSETS CURRENT EXPORT Folder", icon='FILEBROWSER')


def open_source_content(pie):
    pie.operator("wm.bh_dir_open_source_content_root_dir", text="Open SOURCECONTENT ROOT Folder", icon='FILEBROWSER')


def open_dir_speedtree(pie):
    pie.operator("wm.bh_dir_open_speedtree_msh", text="Open SPEEDTREE MSH Folder", icon='FILEBROWSER')


def open_dir_final(pie):
    pie.operator("wm.bh_dir_open_final", text="Open FINAL Folder", icon='FILEBROWSER')


def open_dir_scene(pie):
    pie.operator("wm.bh_dir_open_scene", text="Open SCENE Folder", icon='FILEBROWSER')


def open_dir_res(pie):
    pie.operator("wm.bh_dir_open_resources", text="Open RESOURCES Folder", icon='FILEBROWSER')


def open_dir_user_res(pie):
    pie.operator("wm.bh_dir_open_user_resource", text="Open USER RESOURCE PATH", icon='FILE_BLEND')


def open_dir_ref(pie):
    pie.operator("wm.bh_dir_open_references", text="Open REFERENCES Folder", icon='FILEBROWSER')


# ----------------------------------------------------------------------------------------------------------------------
# EXPORT


def batch_export_selection_resource_folder(pie):
    pie.operator("wm.bh_batch_export_select_to_resources")


# ----------------------------------------------------------------------------------------------------------------------
# SEND


def send_all_asset_containers(pie):

    match prefs().bridge.active_game_engine:
        case 'unity':
            export_preset = 'UNITY'
        case 'unreal':
            export_preset = 'UNREAL'
        case _:
            log(Severity.CRITICAL, 'Blue Hole Pie Menu', 'Unsupported Active Game Engine')
            return

    # All Containers - All in Scene
    label = sendOp.BH_OT_send_containers.build_ui_label(
        export_preset=export_preset,
        send_all=True,
        include_hierarchy=True,
        include_collection=True,
        include_mesh=True,
    )
    op = pie.operator(sendOp.BH_OT_send_containers.bl_idname, text=label, icon='UV_SYNC_SELECT')
    op.export_preset = export_preset
    op.send_all = True
    op.include_hierarchy = True
    op.include_collection = True
    op.include_mesh = True


def send_selected_asset_containers(pie):
    match prefs().bridge.active_game_engine:
        case 'unity':
            export_preset = 'UNITY'
        case 'unreal':
            export_preset = 'UNREAL'
        case _:
            log(Severity.CRITICAL, 'Blue Hole Pie Menu', 'Unsupported Active Game Engine')
            return

        # All Containers - All in Scene
    label = sendOp.BH_OT_send_containers.build_ui_label(
        export_preset=export_preset,
        send_all=False,
        include_hierarchy=True,
        include_collection=True,
        include_mesh=True,
    )
    op = pie.operator(sendOp.BH_OT_send_containers.bl_idname, text=label, icon='UV_SYNC_SELECT')
    op.export_preset = export_preset
    op.send_all = False
    op.include_hierarchy = True
    op.include_collection = True
    op.include_mesh = True


def export_hierarchy_all(pie):
    pie.operator("wm.bh_export_all_hierarchies", icon='UV_SYNC_SELECT')


def export_hierarchy_selected(pie):
    pie.operator("wm.bh_export_select_hierarchies", icon='UV_SYNC_SELECT')


# ----------------------------------------------------------------------------------------------------------------------
# SOURCE CONTROL


def perforce_checkout(pie):
    pie.operator("wm.bh_p4_check_out_blend", text="Check Out Current Blend Scene", icon='CHECKMARK')


def perforce_server_info(pie):
    pie.operator("wm.bh_p4_display_server_info", text="Display Server Info", icon='INFO')


# ----------------------------------------------------------------------------------------------------------------------
# ORDER


def order_st_hubert(pie):
    pie.operator("wm.bh_foodorder_sthubert", text="Order St-Hubert", icon='MOD_TIME')


def order_uber_eats(pie):
    pie.operator("wm.bh_foodorder_ubereats", text="Order Uber Eats", icon='MOD_TIME')


