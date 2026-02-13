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
from ....blenderUtils.debugUtils import *
from ....preferences.prefs import *


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


def if_available_open_workspace_or_source_root(pie):
    if prefs().sc.source_control_enable and prefs().sc.source_control_solution == 'perforce':
        pie.operator("wm.bh_dir_open_workspace_root", text="Open WORKSPACE ROOT Folder", icon='FILEBROWSER')
    elif os.path.exists(prefs().general.unity_assets_path) or os.path.exists(prefs().general.unity_assets_path_mac) or os.path.exists(prefs().general.unity_assets_path_linux):
        pie.operator('wm.bh_dir_open_unity_assets_current_exp_dir', text="Open UNITY ASSETS CURRENT EXPORT Folder",
                     icon='FILEBROWSER')
    elif os.path.exists(prefs().env.sc_path) or os.path.exists(prefs().env.sc_path_alternate) or os.path.exists(prefs().env.sc_path_mac) or os.path.exists(prefs().env.sc_path_mac_alternate) or os.path.exists(prefs().env.sc_path_linux) or os.path.exists(prefs().env.sc_path_linux_alternate):
        pie.operator("wm.bh_dir_open_source_content_root_dir", text="Open SOURCECONTENT ROOT Folder", icon='FILEBROWSER')
    else:
        pie.separator()


def open_dir_speedtree(pie):
    pie.operator("wm.bh_dir_open_speedtree_msh", text="Open SPEEDTREE MSH Folder", icon='FILEBROWSER')


def open_dir_final(pie):
    pie.operator("wm.bh_dir_open_final", text="Open FINAL Folder", icon='FILEBROWSER')


def open_scene_final(pie):
    pie.operator("wm.bh_dir_open_scene", text="Open SCENE Folder", icon='FILEBROWSER')


def open_dir_res(pie):
    pie.operator("wm.bh_dir_open_resources", text="Open RESOURCES Folder", icon='FILEBROWSER')


def open_dir_user_res(pie):
    pie.operator("wm.bh_dir_open_user_resource", text="Open USER RESOURCE PATH", icon='FILE_BLEND')


def open_dir_ref(pie):
    pie.operator("wm.bh_dir_open_references", text="Open REFERENCES Folder", icon='FILEBROWSER')


# ----------------------------------------------------------------------------------------------------------------------
# EXPORT


# ----------------------------------------------------------------------------------------------------------------------
# SEND


def send_unreal_all(pie):
    pie.operator("wm.bh_send_unreal", text="Send *ALL* (Asset Hierarchies) to Unreal", icon='UV_SYNC_SELECT')


def send_unreal_selected(pie):
    pie.operator("wm.bh_send_selected_unreal", text="Send Selected (Asset Hierarchies) to Unreal", icon='UV_SYNC_SELECT')


def send_unity_all(pie):
    pie.operator("wm.bh_send_unity", text="Send *ALL* (Asset Hierarchies) to Unity", icon='UV_SYNC_SELECT')


def send_unity_selected(pie):
    pie.operator("wm.bh_send_selected_unity", text="Send Selected (Asset Hierarchies) to Unity", icon='UV_SYNC_SELECT')


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


