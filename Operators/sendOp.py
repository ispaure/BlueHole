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
from typing import *
from ..blenderUtils.export.exportSettingsPresets import *
from ..blenderUtils.export.assetHierarchy.containerGroup import AssetHierarchyContainerGroup
from ..blenderUtils.export.assetCollection.containerGroup import AssetCollectionContainerGroup
from ..blenderUtils.export.assetMesh.containerGroup import AssetMeshContainerGroup
from ..Lib.commonUtils import uiUtils

# ----------------------------------------------------------------------------------------------------------------------
# INTERNAL HELPERS


def _send_asset_container(preset: ExportSettingsPreset,
                          send_all: bool, *,
                          confirm_title: Optional[str] = None,
                          confirm_msg: Optional[str] = None
                          ) -> set[str]:
    """
    Shared implementation for sending Asset Hierarchies.

    preset: Export settings preset (UNREAL / UNITY)
    send_all: True => containers from scene (+ confirmation)
              False => containers from selection (no confirmation)
    """
    if send_all:
        title = confirm_title or "Confirm Send"
        msg = confirm_msg or "Do you want to continue?"
        if not uiUtils.display_msg_box_ok_cancel(title, msg):
            return {'CANCELLED'}

    export_settings = get_export_settings(preset)

    asset_hierarchies = AssetHierarchyContainerGroup(export_settings)
    if send_all:
        asset_hierarchies.set_containers_from_scene()
    else:
        asset_hierarchies.set_containers_from_selection()

    asset_hierarchies.export_proc(send=True, bypass_sc=False)
    return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS (Wrappers - keep existing bl_idname)


class SendAllHierarchiesToUnity(bpy.types.Operator):
    bl_idname = "wm.bh_send_unity"
    bl_label = "Send *ALL* (Asset Hierarchies) to UNITY"
    bl_description = 'Sends all asset hierarchies to Unity'

    def execute(self, context):
        return _send_asset_container(
            ExportSettingsPreset.UNITY,
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
            send_all=False
        )


class SendAllHierarchiesToUnreal(bpy.types.Operator):
    bl_idname = "wm.bh_send_unreal"
    bl_label = "Send *ALL* (Asset Hierarchies) to UNREAL"
    bl_description = 'Sends all asset hierarchies to Unreal'

    def execute(self, context):
        return _send_asset_container(
            ExportSettingsPreset.UNREAL,
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
            send_all=False
        )


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

classes = (
    SendAllHierarchiesToUnity,
    SendSelectedHierarchiesToUnity,
    SendAllHierarchiesToUnreal,
    SendSelectedHierarchiesToUnreal,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)