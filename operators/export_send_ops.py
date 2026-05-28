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
from bpy.props import BoolProperty, EnumProperty, StringProperty

# Blue Hole
from typing import Optional, Type

from ..blenderUtils.export.assetHierarchy.containerGroup import AssetHierarchyContainerGroup
from ..blenderUtils.export.assetCollection.containerGroup import AssetCollectionContainerGroup
from ..blenderUtils.export.assetMesh.containerGroup import AssetMeshContainerGroup
from ..blenderUtils.export.exportSettingsPresets import *
from ..blenderUtils.export.looseMesh.containerGroup import batch_export_loose_mesh
from ..blenderUtils.export.model import containerUtils
from ..preferences.prefs import *
from ..unrealUtils import communicateUnreal

# ----------------------------------------------------------------------------------------------------------------------
# INTERNAL HELPERS


def _build_confirm_send_all_dialog(
    *,
    preset: ExportSettingsPreset,
    groups: list[Type],
    send: bool,
    confirm_title: Optional[str],
    confirm_msg: Optional[str],
) -> tuple[str, str]:
    """
    Auto-build confirm dialog strings if not explicitly provided.
    Only used when send_all=True.

    send=True  -> "Send"
    send=False -> "Export"
    """
    engine = preset.name  # e.g. "UNREAL", "UNITY"
    verb = "Send" if send else "Export"

    # If caller provided both, trust them as-is.
    if confirm_title is not None and confirm_msg is not None:
        return confirm_title, confirm_msg

    # Title
    title = confirm_title or f"{engine} {verb}"

    # Message override (if provided)
    if confirm_msg:
        return title, confirm_msg

    # Helper: get display name from container group class
    def _group_name(cls: Type) -> str:
        return getattr(cls, "CONTAINERS_NAME", cls.__name__)

    if not groups:
        msg = f"No container types selected. Nothing will be {verb.lower()}ed."
        return title, msg

    if len(groups) == 1:
        group_label = _group_name(groups[0])
        msg = f"Do you really want to {verb.lower()} ALL {group_label} for {engine}? Press OK to confirm."
        return title, msg

    group_labels = ", ".join(_group_name(g) for g in groups)
    msg = f"Do you really want to {verb.lower()} ALL of these for {engine}? ({group_labels}) Press OK to confirm."
    return title, msg


def _export_asset_container_no_confirm(
    *,
    preset: ExportSettingsPreset,
    container_group_cls: Type,
    send_all: bool,
    send: bool,
    silent_if_empty: bool,
    bypass_sc: bool = False,
) -> set[str]:
    """
    Shared implementation for exporting/sending Asset Containers without confirmation.
    Confirmation is handled once at the operator level.

    send=True  -> send to engine (bridge)
    send=False -> export only
    """
    export_settings = get_export_settings(preset)

    container_group = container_group_cls(export_settings)
    if send_all:
        container_group.set_containers_from_scene(silent_if_empty=silent_if_empty)
    else:
        container_group.set_containers_from_selection(silent_if_empty=silent_if_empty)

    container_group.export_proc(send=send, bypass_sc=bypass_sc)
    return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# MEGA OPERATOR

class BH_OT_export_containers(bpy.types.Operator):
    bl_idname = "wm.bh_send_containers"
    bl_label = "Export/Send Containers"
    bl_description = "Master Operator for Export/Send Operations"

    # --- Core behavior ---
    send_all: BoolProperty(
        name="Send All",
        description="Use containers from the entire scene (otherwise from selection)",
        default=False,
    )

    send: BoolProperty(
        name="Send",
        description="When enabled, sends to the engine. When disabled, exports only.",
        default=False,
    )

    export_preset: EnumProperty(
        name="Export Preset",
        description="Target export preset",
        items=[
            ('UNREAL', "Unreal", "Use Unreal export preset"),
            ('UNITY', "Unity", "Use Unity export preset"),
            ('GODOT', "Godot", "Use Godot export preset")
        ],
        default='UNREAL',
    )

    # --- Container type selection ---
    include_hierarchy: BoolProperty(
        name="Asset Hierarchy",
        description="Include Asset Hierarchy containers",
        default=True,
    )
    include_collection: BoolProperty(
        name="Asset Collection",
        description="Include Asset Collection containers",
        default=True,
    )
    include_mesh: BoolProperty(
        name="Asset Mesh",
        description="Include Asset Mesh containers",
        default=True,
    )

    # Optional overrides (usually leave blank and let it auto-build)
    confirm_title: StringProperty(
        name="Confirm Title",
        description="Optional override confirmation title",
        default="",
    )
    confirm_msg: StringProperty(
        name="Confirm Message",
        description="Optional override confirmation message",
        default="",
    )

    @classmethod
    def build_ui_label(
        cls,
        *,
        export_preset: str,
        send_all: bool,
        send: bool,
        include_hierarchy: bool,
        include_collection: bool,
        include_mesh: bool,
    ) -> str:
        """
        Build a dynamic UI button label based on operator-like inputs.
        Intended to be called from Panels/Menus before creating the operator button.
        """
        engine = export_preset.upper()
        scope = "*ALL*" if send_all else "Selected"
        verb = "Send" if send else "Export"
        to_or_for = "to" if send else "for"

        parts: list[str] = []
        if prefs().container.enable_asset_hierarchy_container and include_hierarchy:
            parts.append(getattr(AssetHierarchyContainerGroup, "CONTAINERS_NAME", "Asset Hierarchies"))
        if prefs().container.enable_asset_collection_container and include_collection:
            parts.append(getattr(AssetCollectionContainerGroup, "CONTAINERS_NAME", "Asset Collections"))
        if prefs().container.enable_asset_mesh_container and include_mesh:
            parts.append(getattr(AssetMeshContainerGroup, "CONTAINERS_NAME", "Asset Meshes"))

        if not parts:
            what = "Nothing"
        elif len(parts) == 3:
            what = "Asset Containers"
        else:
            what = " + ".join(parts)

        return f"{verb} {scope} ({what}) {to_or_for} {engine}"

    def execute(self, context):

        # Map enum -> preset
        match self.export_preset:
            case 'UNREAL':
                preset = ExportSettingsPreset.UNREAL
            case 'UNITY':
                preset = ExportSettingsPreset.UNITY
            case 'GODOT':
                preset = ExportSettingsPreset.GODOT
            case _:
                log(Severity.CRITICAL, self.bl_idname, 'Invalid Value on "Export Preset" Parameter')
                return {'CANCELLED'}

        # Which container group classes are included
        groups = containerUtils.get_container_groups(
            include_hierarchy=self.include_hierarchy,
            include_collection=self.include_collection,
            include_mesh=self.include_mesh
        )

        if not groups:
            log(Severity.ERROR, self.bl_label, "No container types selected.", popup=True)
            return {'CANCELLED'}

        # Confirm once (only when operating on ALL containers from the scene)
        if self.send_all:
            title, msg = _build_confirm_send_all_dialog(
                preset=preset,
                groups=groups,
                send=self.send,
                confirm_title=self.confirm_title or None,
                confirm_msg=self.confirm_msg or None,
            )
            if not uiUtils.display_msg_box_ok_cancel(title, msg):
                return {'CANCELLED'}

        # Run all selected container types
        silent_if_empty = len(groups) > 1
        for group_cls in groups:
            res = _export_asset_container_no_confirm(
                preset=preset,
                container_group_cls=group_cls,
                send_all=self.send_all,
                send=self.send,
                silent_if_empty=silent_if_empty,
                bypass_sc=False,
            )
            if res == {'CANCELLED'}:
                return res

        return {'FINISHED'}


class BH_OT_debug_unreal_exec_nodes(bpy.types.Operator):
    bl_idname = "wm.bh_debug_unreal_exec_nodes"
    bl_label = "Debug - Unreal Remote Execution Nodes"
    bl_description = "Searches for Unreal Remote Execution Nodes using multicast discovery."

    def execute(self, context):
        communicateUnreal.debug_remote_nodes()
        return {'FINISHED'}


class BatchExportSelectedToFinal(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_final"
    bl_label = 'Batch Export (Selection) to FINAL Folder'
    bl_description = 'Batch exports selected meshes using their names as file names in the FINAL Folder'

    def execute(self, context):
        batch_export_loose_mesh(prefs().directory.sc_dir_struct_final)
        return {'FINISHED'}


class BatchExportSelectedToResources(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_resources"
    bl_label = 'Batch Export (Selection) to RESOURCES Folder'

    def execute(self, context):
        batch_export_loose_mesh(prefs().directory.sc_dir_struct_resources)
        return {'FINISHED'}


class BatchExportSelectedToSpeedTree_FBX(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_speedtree_fbx"
    bl_label = 'Batch Export (Selection) to SPEEDTREE Folder'
    bl_description = 'Batch exports selected meshes using their names as file names in the SPEEDTREE MSH Folder'

    def execute(self, context):
        batch_export_loose_mesh(prefs().directory.sc_dir_struct_st)
        return {'FINISHED'}


class BatchExportSelectedToSpeedtreeLR_FBX(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_speedtree_lr_fbx"
    bl_label = 'Batch Export (Selection) to SPEEDTREE-LR Folder'
    bl_description = 'Batch exports selected meshes using their names as file names in the SPEEDTREE MSH -> LR Folder'

    def execute(self, context):
        batch_export_loose_mesh(prefs().directory.sc_dir_struct_st_lr)
        return {'FINISHED'}


class BatchExportSelectedToSpeedtreeHR_FBX(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_speedtree_hr_fbx"
    bl_label = 'Batch Export (Selection) to SPEEDTREE-HR Folder'
    bl_description = 'Batch exports selected meshes using their names as file names in the SPEEDTREE MSH -> HR Folder'

    def execute(self, context):
        batch_export_loose_mesh(prefs().directory.sc_dir_struct_st_hr)
        return {'FINISHED'}


class BatchExportSelectedToBakeFBX(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_bake_fbx"
    bl_label = 'Batch Export (Selection) to BAKE Folder'
    bl_description = 'Batch exports selected meshes using their names as file names in the MSH BAKE Folder'

    def execute(self, context):
        batch_export_loose_mesh(prefs().directory.sc_dir_struct_msh_bake)
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

classes = (
    BH_OT_export_containers,
    BatchExportSelectedToSpeedTree_FBX,
    BatchExportSelectedToSpeedtreeLR_FBX,
    BatchExportSelectedToSpeedtreeHR_FBX,
    BatchExportSelectedToFinal,
    BatchExportSelectedToBakeFBX,
    BatchExportSelectedToResources,
    BH_OT_debug_unreal_exec_nodes,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)