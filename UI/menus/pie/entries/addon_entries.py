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
from .....Lib.commonUtils.debugUtils import *
from .....preferences.prefs import *
from .....operators import export_send_ops
from .....blenderUtils import blenderFile


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU BUTTON


# ----------------------------------------------------------------------------------------------------------------------
# SCENE


def add_asset_hierarchy(pie):
    if prefs().container.enable_asset_hierarchy_container:
        pie.operator("wm.bh_scene_add_asset_hierarchy")
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            "wm.bh_scene_add_asset_hierarchy",
            text="Hierarchy Containers disabled in Preferences",
            icon='ERROR'
        )
        return


def add_asset_collection(pie):
    if prefs().container.enable_asset_collection_container:
        pie.operator("wm.bh_scene_add_asset_collection")
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            "wm.bh_scene_add_asset_collection",
            text="Collection Containers disabled in Preferences",
            icon='ERROR'
        )
        return


def add_asset_mesh(pie):
    if prefs().container.enable_asset_mesh_container:
        pie.operator("wm.bh_scene_add_asset_mesh")
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            "wm.bh_scene_add_asset_mesh",
            text="Mesh Containers disabled in Preferences",
            icon='ERROR'
        )
        return


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

    if blenderFile.has_blend_filepath():
        pie.operator(
            "wm.bh_dir_open_speedtree_msh",
            text="Open SPEEDTREE MSH Folder",
            icon='FILEBROWSER'
        )
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            "wm.bh_dir_open_speedtree_msh",
            text="Save .blend file to open Scene folders",
            icon='ERROR'
        )


def open_dir_final(pie):
    if blenderFile.has_blend_filepath():
        pie.operator(
            "wm.bh_dir_open_final",
            text="Open FINAL Folder",
            icon='FILEBROWSER'
        )
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            "wm.bh_dir_open_final",
            text="Save .blend file to open Scene folders",
            icon='ERROR'
        )


def open_dir_scene(pie):
    if blenderFile.has_blend_filepath():
        pie.operator(
            "wm.bh_dir_open_scene",
            text="Open SCENE Folder",
            icon='FILEBROWSER'
        )
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            "wm.bh_dir_open_scene",
            text="Save .blend file to open Scene folders",
            icon='ERROR'
        )


def open_dir_res(pie):
    if blenderFile.has_blend_filepath():
        pie.operator(
            "wm.bh_dir_open_resources",
            text="Open RESOURCES Folder",
            icon='FILEBROWSER'
        )
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            "wm.bh_dir_open_resources",
            text="Save .blend file to open Scene folders",
            icon='ERROR'
        )


def open_dir_user_res(pie):
    pie.operator("wm.bh_dir_open_user_resource", text="Open USER RESOURCE PATH", icon='FILE_BLEND')


def open_dir_ref(pie):
    pie.operator("wm.bh_dir_open_references", text="Open REFERENCES Folder", icon='FILEBROWSER')


# ----------------------------------------------------------------------------------------------------------------------
# EXPORT


def batch_export_selection_resource_folder(pie):

    if blenderFile.has_blend_filepath():
        pie.operator(
            "wm.bh_batch_export_select_to_resources"
        )
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            "wm.bh_batch_export_select_to_resources",
            text="Save the .blend file to Export",
            icon='ERROR'
        )


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

    enabled_hierarchy = prefs().container.enable_asset_hierarchy_container
    enabled_collection = prefs().container.enable_asset_collection_container
    enabled_mesh = prefs().container.enable_asset_mesh_container
    any_enabled = enabled_hierarchy or enabled_collection or enabled_mesh

    # All Containers - All in Scene
    label = export_send_ops.BH_OT_export_containers.build_ui_label(
        export_preset=export_preset,
        send_all=True,
        send=True,
        include_hierarchy=True,
        include_collection=True,
        include_mesh=True,
    )

    if not blenderFile.has_blend_filepath():
        col = pie.column()
        col.enabled = False
        col.operator(
            export_send_ops.BH_OT_export_containers.bl_idname,
            text="Save the .blend file to Send",
            icon='ERROR'
        )
        return

    if not any_enabled:
        col = pie.column()
        col.enabled = False
        col.operator(
            export_send_ops.BH_OT_export_containers.bl_idname,
            text="All Asset Containers disabled in Preferences",
            icon='ERROR'
        )
        return

    op = pie.operator(export_send_ops.BH_OT_export_containers.bl_idname, text=label, icon='UV_SYNC_SELECT')
    op.export_preset = export_preset
    op.send_all = True
    op.send = True
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

    enabled_hierarchy = prefs().container.enable_asset_hierarchy_container
    enabled_collection = prefs().container.enable_asset_collection_container
    enabled_mesh = prefs().container.enable_asset_mesh_container
    any_enabled = enabled_hierarchy or enabled_collection or enabled_mesh

    # All Containers - In Selection
    label = export_send_ops.BH_OT_export_containers.build_ui_label(
        export_preset=export_preset,
        send_all=False,
        send=True,
        include_hierarchy=True,
        include_collection=True,
        include_mesh=True,
    )

    if not blenderFile.has_blend_filepath():
        col = pie.column()
        col.enabled = False
        col.operator(
            export_send_ops.BH_OT_export_containers.bl_idname,
            text="Save the .blend file to Send",
            icon='ERROR'
        )
        return

    if not any_enabled:
        col = pie.column()
        col.enabled = False
        col.operator(
            export_send_ops.BH_OT_export_containers.bl_idname,
            text="All Asset Containers disabled in Preferences",
            icon='ERROR'
        )
        return

    op = pie.operator(export_send_ops.BH_OT_export_containers.bl_idname, text=label, icon='UV_SYNC_SELECT')
    op.export_preset = export_preset
    op.send_all = False
    op.send = True
    op.include_hierarchy = True
    op.include_collection = True
    op.include_mesh = True


def export_hierarchy_all(pie):

    if not blenderFile.has_blend_filepath():
        col = pie.column()
        col.enabled = False
        col.operator(
            "wm.bh_export_all_hierarchies",
            text="Save the .blend file to Export",
            icon='ERROR'
        )
        return

    if not prefs().container.enable_asset_hierarchy_container:
        col = pie.column()
        col.enabled = False
        col.operator(
            "wm.bh_export_all_hierarchies",
            text="All Asset Containers disabled in Preferences",
            icon='ERROR'
        )
        return

    pie.operator(
        "wm.bh_export_all_hierarchies",
        icon='UV_SYNC_SELECT'
    )


def export_hierarchy_selected(pie):

    if not blenderFile.has_blend_filepath():
        col = pie.column()
        col.enabled = False
        col.operator(
            "wm.bh_export_select_hierarchies",
            text="Save the .blend file to Export",
            icon='ERROR'
        )
        return

    if not prefs().container.enable_asset_hierarchy_container:
        col = pie.column()
        col.enabled = False
        col.operator(
            "wm.bh_export_select_hierarchies",
            text="All Asset Containers disabled in Preferences",
            icon='ERROR'
        )
        return

    pie.operator(
        "wm.bh_export_select_hierarchies",
        icon='UV_SYNC_SELECT'
    )


# ----------------------------------------------------------------------------------------------------------------------
# SOURCE CONTROL


def perforce_checkout(pie):

    if blenderFile.has_blend_filepath():
        pie.operator(
            "wm.bh_p4_check_out_blend",
            text="Check Out Current Blend Scene",
            icon='CHECKMARK'
        )
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            "wm.bh_p4_check_out_blend",
            text="Save .blend file to enable checkout",
            icon='ERROR'
        )


def perforce_server_info(pie):
    pie.operator("wm.bh_p4_display_server_info", text="Display Server Info", icon='INFO')


def sc_disabled(pie):
    col = pie.column()
    col.enabled = False
    col.operator(
        "wm.disabled_source_control",
        text="Can't Show; Source Control disabled!!!",
        icon='ERROR'
    )


# ----------------------------------------------------------------------------------------------------------------------
# ORDER


def order_st_hubert(pie):
    pie.operator("wm.bh_foodorder_sthubert", text="Order St-Hubert", icon='MOD_TIME')


def order_uber_eats(pie):
    pie.operator("wm.bh_foodorder_ubereats", text="Order Uber Eats", icon='MOD_TIME')


