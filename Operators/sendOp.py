"""
Operators for send to engines
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://github.com/ispaure/BlueHole

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS

# Blender
import bpy

# Blue Hole
from typing import Optional, Type

from ..blenderUtils.export.exportSettingsPresets import *
from ..blenderUtils.export.assetHierarchy.containerGroup import AssetHierarchyContainerGroup
from ..blenderUtils.export.assetCollection.containerGroup import AssetCollectionContainerGroup
from ..blenderUtils.export.assetMesh.containerGroup import AssetMeshContainerGroup
from ..Lib.commonUtils import uiUtils

# ----------------------------------------------------------------------------------------------------------------------
# INTERNAL HELPERS


def _send_asset_container(
    preset: ExportSettingsPreset,
    container_group_cls: Type,
    send_all: bool,
    *,
    confirm_title: Optional[str] = None,
    confirm_msg: Optional[str] = None,
) -> set[str]:
    """
    Shared implementation for sending Asset Containers.

    preset: Export settings preset (UNREAL / UNITY)
    container_group_cls: one of
        - AssetHierarchyContainerGroup
        - AssetCollectionContainerGroup
        - AssetMeshContainerGroup
    send_all: True => containers from scene (+ confirmation)
              False => containers from selection (no confirmation)
    """
    if send_all:
        title = confirm_title or "Confirm Send"
        msg = confirm_msg or "Do you want to continue?"
        if not uiUtils.display_msg_box_ok_cancel(title, msg):
            return {'CANCELLED'}

    export_settings = get_export_settings(preset)

    container_group = container_group_cls(export_settings)
    if send_all:
        container_group.set_containers_from_scene()
    else:
        container_group.set_containers_from_selection()

    container_group.export_proc(send=True, bypass_sc=False)
    return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS (Wrappers - keep existing bl_idname)
# NOTE: bl_idname values below follow your existing naming pattern for hierarchies.
#       Adjust the new ones if you already have established ids for Collection/Mesh.


# ----------------------------
# ASSET HIERARCHIES
# ----------------------------

class SendAllHierarchiesToUnity(bpy.types.Operator):
    bl_idname = "wm.bh_send_unity"
    bl_label = "Send *ALL* (Asset Hierarchies) to UNITY"
    bl_description = 'Sends all asset hierarchies to Unity'

    def execute(self, context):
        return _send_asset_container(
            ExportSettingsPreset.UNITY,
            AssetHierarchyContainerGroup,
            send_all=True,
            confirm_title='Unity Export',
            confirm_msg='Do you really want to send *ALL* Asset Hierarchies to Unity? Press OK to confirm.',
        )


class SendSelectedHierarchiesToUnity(bpy.types.Operator):
    bl_idname = "wm.bh_send_selected_unity"
    bl_label = "Send Selected (Asset Hierarchies) to UNITY"
    bl_description = 'Sends selected asset hierarchies to Unity'

    def execute(self, context):
        return _send_asset_container(
            ExportSettingsPreset.UNITY,
            AssetHierarchyContainerGroup,
            send_all=False,
        )


class SendAllHierarchiesToUnreal(bpy.types.Operator):
    bl_idname = "wm.bh_send_unreal"
    bl_label = "Send *ALL* (Asset Hierarchies) to UNREAL"
    bl_description = 'Sends all asset hierarchies to Unreal'

    def execute(self, context):
        return _send_asset_container(
            ExportSettingsPreset.UNREAL,
            AssetHierarchyContainerGroup,
            send_all=True,
            confirm_title='Unreal Export',
            confirm_msg='Do you really want to send *ALL* Asset Hierarchies to Unreal? Press OK to confirm.',
        )


class SendSelectedHierarchiesToUnreal(bpy.types.Operator):
    bl_idname = "wm.bh_send_selected_unreal"
    bl_label = "Send Selected (Asset Hierarchies) to UNREAL"
    bl_description = 'Sends selected asset hierarchies to Unreal'

    def execute(self, context):
        return _send_asset_container(
            ExportSettingsPreset.UNREAL,
            AssetHierarchyContainerGroup,
            send_all=False,
        )


# ----------------------------
# ASSET COLLECTIONS
# ----------------------------

class SendAllCollectionsToUnity(bpy.types.Operator):
    bl_idname = "wm.bh_send_collection_unity"
    bl_label = "Send *ALL* (Asset Collections) to UNITY"
    bl_description = 'Sends all asset collections to Unity'

    def execute(self, context):
        return _send_asset_container(
            ExportSettingsPreset.UNITY,
            AssetCollectionContainerGroup,
            send_all=True,
            confirm_title='Unity Export',
            confirm_msg='Do you really want to send *ALL* Asset Collections to Unity? Press OK to confirm.',
        )


class SendSelectedCollectionsToUnity(bpy.types.Operator):
    bl_idname = "wm.bh_send_selected_collection_unity"
    bl_label = "Send Selected (Asset Collections) to UNITY"
    bl_description = 'Sends selected asset collections to Unity'

    def execute(self, context):
        return _send_asset_container(
            ExportSettingsPreset.UNITY,
            AssetCollectionContainerGroup,
            send_all=False,
        )


class SendAllCollectionsToUnreal(bpy.types.Operator):
    bl_idname = "wm.bh_send_collection_unreal"
    bl_label = "Send *ALL* (Asset Collections) to UNREAL"
    bl_description = 'Sends all asset collections to Unreal'

    def execute(self, context):
        return _send_asset_container(
            ExportSettingsPreset.UNREAL,
            AssetCollectionContainerGroup,
            send_all=True,
            confirm_title='Unreal Export',
            confirm_msg='Do you really want to send *ALL* Asset Collections to Unreal? Press OK to confirm.',
        )


class SendSelectedCollectionsToUnreal(bpy.types.Operator):
    bl_idname = "wm.bh_send_selected_collection_unreal"
    bl_label = "Send Selected (Asset Collections) to UNREAL"
    bl_description = 'Sends selected asset collections to Unreal'

    def execute(self, context):
        return _send_asset_container(
            ExportSettingsPreset.UNREAL,
            AssetCollectionContainerGroup,
            send_all=False,
        )


# ----------------------------
# ASSET MESHES
# ----------------------------

class SendAllMeshesToUnity(bpy.types.Operator):
    bl_idname = "wm.bh_send_mesh_unity"
    bl_label = "Send *ALL* (Asset Meshes) to UNITY"
    bl_description = 'Sends all asset meshes to Unity'

    def execute(self, context):
        return _send_asset_container(
            ExportSettingsPreset.UNITY,
            AssetMeshContainerGroup,
            send_all=True,
            confirm_title='Unity Export',
            confirm_msg='Do you really want to send *ALL* Asset Meshes to Unity? Press OK to confirm.',
        )


class SendSelectedMeshesToUnity(bpy.types.Operator):
    bl_idname = "wm.bh_send_selected_mesh_unity"
    bl_label = "Send Selected (Asset Meshes) to UNITY"
    bl_description = 'Sends selected asset meshes to Unity'

    def execute(self, context):
        return _send_asset_container(
            ExportSettingsPreset.UNITY,
            AssetMeshContainerGroup,
            send_all=False,
        )


class SendAllMeshesToUnreal(bpy.types.Operator):
    bl_idname = "wm.bh_send_mesh_unreal"
    bl_label = "Send *ALL* (Asset Meshes) to UNREAL"
    bl_description = 'Sends all asset meshes to Unreal'

    def execute(self, context):
        return _send_asset_container(
            ExportSettingsPreset.UNREAL,
            AssetMeshContainerGroup,
            send_all=True,
            confirm_title='Unreal Export',
            confirm_msg='Do you really want to send *ALL* Asset Meshes to Unreal? Press OK to confirm.',
        )


class SendSelectedMeshesToUnreal(bpy.types.Operator):
    bl_idname = "wm.bh_send_selected_mesh_unreal"
    bl_label = "Send Selected (Asset Meshes) to UNREAL"
    bl_description = 'Sends selected asset meshes to Unreal'

    def execute(self, context):
        return _send_asset_container(
            ExportSettingsPreset.UNREAL,
            AssetMeshContainerGroup,
            send_all=False,
        )


# ----------------------------
# ALL TYPES (Hierarchies + Collections + Meshes)
# ----------------------------

class SendAllContainersToUnity(bpy.types.Operator):
    bl_idname = "wm.bh_send_all_containers_unity"
    bl_label = "Send *ALL* (All Container Types) to UNITY"
    bl_description = "Sends *ALL* Asset Hierarchies, Asset Collections, and Asset Meshes to Unity"

    def execute(self, context):
        # Hierarchies
        _send_asset_container(
            ExportSettingsPreset.UNITY,
            AssetHierarchyContainerGroup,
            send_all=True,
            confirm_title='Unity Export',
            confirm_msg='Do you really want to send *ALL* Asset Hierarchies to Unity? Press OK to confirm.',
        )

        # Collections
        _send_asset_container(
            ExportSettingsPreset.UNITY,
            AssetCollectionContainerGroup,
            send_all=True,
            confirm_title='Unity Export',
            confirm_msg='Do you really want to send *ALL* Asset Collections to Unity? Press OK to confirm.',
        )

        # Meshes
        _send_asset_container(
            ExportSettingsPreset.UNITY,
            AssetMeshContainerGroup,
            send_all=True,
            confirm_title='Unity Export',
            confirm_msg='Do you really want to send *ALL* Asset Meshes to Unity? Press OK to confirm.',
        )

        return {'FINISHED'}


class SendSelectedContainersToUnity(bpy.types.Operator):
    bl_idname = "wm.bh_send_selected_all_containers_unity"
    bl_label = "Send Selected (All Container Types) to UNITY"
    bl_description = "Sends selected Asset Hierarchies, Asset Collections, and Asset Meshes to Unity"

    def execute(self, context):
        # Hierarchies
        _send_asset_container(
            ExportSettingsPreset.UNITY,
            AssetHierarchyContainerGroup,
            send_all=False,
        )

        # Collections
        _send_asset_container(
            ExportSettingsPreset.UNITY,
            AssetCollectionContainerGroup,
            send_all=False,
        )

        # Meshes
        _send_asset_container(
            ExportSettingsPreset.UNITY,
            AssetMeshContainerGroup,
            send_all=False,
        )

        return {'FINISHED'}


class SendAllContainersToUnreal(bpy.types.Operator):
    bl_idname = "wm.bh_send_all_containers_unreal"
    bl_label = "Send *ALL* (All Container Types) to UNREAL"
    bl_description = "Sends *ALL* Asset Hierarchies, Asset Collections, and Asset Meshes to Unreal"

    def execute(self, context):
        # Hierarchies
        _send_asset_container(
            ExportSettingsPreset.UNREAL,
            AssetHierarchyContainerGroup,
            send_all=True,
            confirm_title='Unreal Export',
            confirm_msg='Do you really want to send *ALL* Asset Hierarchies to Unreal? Press OK to confirm.',
        )

        # Collections
        _send_asset_container(
            ExportSettingsPreset.UNREAL,
            AssetCollectionContainerGroup,
            send_all=True,
            confirm_title='Unreal Export',
            confirm_msg='Do you really want to send *ALL* Asset Collections to Unreal? Press OK to confirm.',
        )

        # Meshes
        _send_asset_container(
            ExportSettingsPreset.UNREAL,
            AssetMeshContainerGroup,
            send_all=True,
            confirm_title='Unreal Export',
            confirm_msg='Do you really want to send *ALL* Asset Meshes to Unreal? Press OK to confirm.',
        )

        return {'FINISHED'}


class SendSelectedContainersToUnreal(bpy.types.Operator):
    bl_idname = "wm.bh_send_selected_all_containers_unreal"
    bl_label = "Send Selected (All Container Types) to UNREAL"
    bl_description = "Sends selected Asset Hierarchies, Asset Collections, and Asset Meshes to Unreal"

    def execute(self, context):
        # Hierarchies
        _send_asset_container(
            ExportSettingsPreset.UNREAL,
            AssetHierarchyContainerGroup,
            send_all=False,
        )

        # Collections
        _send_asset_container(
            ExportSettingsPreset.UNREAL,
            AssetCollectionContainerGroup,
            send_all=False,
        )

        # Meshes
        _send_asset_container(
            ExportSettingsPreset.UNREAL,
            AssetMeshContainerGroup,
            send_all=False,
        )

        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

classes = (
    # Hierarchies
    SendAllHierarchiesToUnity,
    SendSelectedHierarchiesToUnity,
    SendAllHierarchiesToUnreal,
    SendSelectedHierarchiesToUnreal,

    # Collections
    SendAllCollectionsToUnity,
    SendSelectedCollectionsToUnity,
    SendAllCollectionsToUnreal,
    SendSelectedCollectionsToUnreal,

    # Meshes
    SendAllMeshesToUnity,
    SendSelectedMeshesToUnity,
    SendAllMeshesToUnreal,
    SendSelectedMeshesToUnreal,

    # All
    SendAllContainersToUnity,
    SendSelectedContainersToUnity,
    SendAllContainersToUnreal,
    SendSelectedContainersToUnreal,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
