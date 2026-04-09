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
from .....blenderUtils import blenderFile

from .....operators import (
    add_ops,
    food_ops,
    help_ops,
    theme_ops,
    directory_ops,
    export_send_ops,
    source_control_ops,
)


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU BUTTON


# ----------------------------------------------------------------------------------------------------------------------
# SCENE


def add_asset_hierarchy(pie):
    if prefs().container.enable_asset_hierarchy_container:
        pie.operator(add_ops.SceneAddAssetHierarchy.bl_idname)
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            add_ops.SceneAddAssetHierarchy.bl_idname,
            text="Hierarchy Containers disabled in Preferences",
            icon='ERROR'
        )
        return


def add_asset_collection(pie):
    if prefs().container.enable_asset_collection_container:
        pie.operator(add_ops.SceneAddAssetCollection.bl_idname)
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            add_ops.SceneAddAssetCollection.bl_idname,
            text="Collection Containers disabled in Preferences",
            icon='ERROR'
        )
        return


def add_asset_mesh(pie):
    if prefs().container.enable_asset_mesh_container:
        pie.operator(add_ops.SceneAddAssetMesh.bl_idname)
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            add_ops.SceneAddAssetMesh.bl_idname,
            text="Mesh Containers disabled in Preferences",
            icon='ERROR'
        )
        return


# ----------------------------------------------------------------------------------------------------------------------
# SUPPORT


def open_keymaps_list(pie):
    pie.operator(help_ops.OpenKeymapsList.bl_idname, text="Keymaps List", icon='URL')


def submit_feedback(pie):
    pie.operator(help_ops.SubmitFeedback.bl_idname, text="Submit Feedback", icon='FUND')


def open_guide(pie):
    pie.operator(help_ops.OpenGuide.bl_idname, text="Online Guide", icon='HELP')


def open_pie_menus_list(pie):
    pie.operator(help_ops.OpenPieMenusList.bl_idname, text="Pie Menus List", icon='URL')


# ----------------------------------------------------------------------------------------------------------------------
# THEMES


def apply_theme_zen_light(pie):
    pie.operator(theme_ops.SetThemeZen.bl_idname, text="Zen Light")


def apply_theme_zen_dark(pie):
    pie.operator(theme_ops.SetThemeZenDark.bl_idname, text="Zen Dark")


def apply_theme_sky(pie):
    pie.operator(theme_ops.SetThemeSky.bl_idname, text="Sky")


def apply_theme_modo(pie):
    pie.operator(theme_ops.SetThemeMODO.bl_idname, text="Modo")


def apply_theme_blender_light(pie):
    pie.operator(theme_ops.SetThemeBlenderLight.bl_idname, text="Blender Light")


def apply_theme_blender_dark(pie):
    pie.operator(theme_ops.SetThemeBlenderDark.bl_idname, text="Blender Dark")


def apply_theme_white(pie):
    pie.operator(theme_ops.SetThemeWhite.bl_idname, text="White")


def apply_theme_deep_grey(pie):
    pie.operator(theme_ops.SetThemeDeepGrey.bl_idname, text="Deep Grey")


# ----------------------------------------------------------------------------------------------------------------------
# DIRECTORIES


def open_workspace_root(pie):
    pie.operator(directory_ops.OpenP4WorkspaceRootFolder.bl_idname, text="Open WORKSPACE ROOT Folder", icon='FILEBROWSER')


def open_unity_assets(pie):
    pie.operator(directory_ops.OpenUnityAssetsCurrentExportPath.bl_idname, text="Open UNITY ASSETS CURRENT EXPORT Folder", icon='FILEBROWSER')


def open_godot_export_path(pie):
    pie.operator(directory_ops.OpenGodotCurrentExportPath.bl_idname, text="Open GODOT CURRENT EXPORT Folder", icon='FILEBROWSER')


def open_source_content(pie):
    pie.operator(directory_ops.OpenSourceContentPath.bl_idname, text="Open SOURCECONTENT ROOT Folder", icon='FILEBROWSER')


def open_dir_speedtree(pie):

    if blenderFile.has_blend_filepath():
        pie.operator(
            directory_ops.OpenSpeedTreeMeshesFolder.bl_idname,
            text="Open SPEEDTREE MSH Folder",
            icon='FILEBROWSER'
        )
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            directory_ops.OpenSpeedTreeMeshesFolder.bl_idname,
            text="Save .blend file to open SPEEDTREE MSH directory",
            icon='ERROR'
        )


def open_dir_final(pie):
    if blenderFile.has_blend_filepath():
        pie.operator(
            directory_ops.OpenFinalFolder.bl_idname,
            text="Open FINAL Folder",
            icon='FILEBROWSER'
        )
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            directory_ops.OpenFinalFolder.bl_idname,
            text="Save .blend file to open FINAL directory",
            icon='ERROR'
        )


def open_dir_scene(pie):
    if blenderFile.has_blend_filepath():
        pie.operator(
            directory_ops.OpenSceneFolder.bl_idname,
            text="Open SCENE Folder",
            icon='FILEBROWSER'
        )
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            directory_ops.OpenSceneFolder.bl_idname,
            text="Save .blend file to open SCENE directory",
            icon='ERROR'
        )


def open_dir_res(pie):
    if blenderFile.has_blend_filepath():
        pie.operator(
            directory_ops.OpenResourcesFolder.bl_idname,
            text="Open RESOURCES Folder",
            icon='FILEBROWSER'
        )
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            directory_ops.OpenResourcesFolder.bl_idname,
            text="Save .blend file to open RESOURCES directory",
            icon='ERROR'
        )


def open_dir_user_res(pie):
    pie.operator(directory_ops.OpenUserResourcePath.bl_idname, text="Open USER RESOURCE PATH", icon='FILE_BLEND')


def open_dir_ref(pie):
    pie.operator(directory_ops.OpenReferencesFolder.bl_idname, text="Open REFERENCES Folder", icon='FILEBROWSER')


# ----------------------------------------------------------------------------------------------------------------------
# EXPORT


def batch_export_selection_resource_folder(pie):

    if blenderFile.has_blend_filepath():
        pie.operator(
            export_send_ops.BatchExportSelectedToResources.bl_idname
        )
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            export_send_ops.BatchExportSelectedToResources.bl_idname,
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
        case 'godot':
            export_preset = 'GODOT'
        case _:
            col = pie.column()
            col.enabled = False
            col.operator(
                export_send_ops.BH_OT_export_containers.bl_idname,
                text="Under Environment -> Send & Bridge, Set Engine to Unity or Unreal",
                icon='ERROR'
            )
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
        case 'godot':
            export_preset = 'GODOT'
        case _:
            col = pie.column()
            col.enabled = False
            col.operator(
                export_send_ops.BH_OT_export_containers.bl_idname,
                text="Under Environment -> Send & Bridge, Set Engine to Unity, Godot or Unreal",
                icon='ERROR'
            )
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


# ----------------------------------------------------------------------------------------------------------------------
# SOURCE CONTROL


def perforce_checkout(pie):

    if blenderFile.has_blend_filepath():
        pie.operator(
            source_control_ops.P4CheckOutCurrentScene.bl_idname,
            text="Check Out Current Blend Scene",
            icon='CHECKMARK'
        )
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            source_control_ops.P4CheckOutCurrentScene.bl_idname,
            text="Save .blend file to enable checkout",
            icon='ERROR'
        )


def perforce_server_info(pie):
    pie.operator(source_control_ops.P4DisplayServerInfo.bl_idname, text="Display Server Info", icon='INFO')


def sc_disabled(pie):
    col = pie.column()
    col.enabled = False
    col.operator(
        source_control_ops.WM_OT_disabled_source_control.bl_idname,
        text="Can't Show; Source Control disabled!!!",
        icon='ERROR'
    )


# ----------------------------------------------------------------------------------------------------------------------
# ORDER


def order_st_hubert(pie):
    pie.operator(food_ops.OrderStHubert.bl_idname, text="Order St-Hubert", icon='MOD_TIME')


def order_uber_eats(pie):
    pie.operator(food_ops.OrderUberEats.bl_idname, text="Order Uber Eats", icon='MOD_TIME')


