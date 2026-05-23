"""
Blue Hole Outliner Menus
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

import bpy
from typing import List, Optional
from pathlib import Path
from ....Lib.commonUtils.debugUtils import *
from ....blenderUtils import blenderFile
from ....blenderUtils.export import exportSettingsPresets
from ....blenderUtils.export.model.container import ContainerDummy
from ....operators import rename_ops, external_addon_ops
from ....preferences.prefs import prefs
from ....wrappers.sourceContentPath import get_valid_source_content_path


# ----------------------------------------------------------------------------------------------------------------------
# CODE

def draw_blue_hole_outliner_object_menu(self, context):
    layout = self.layout

    # ------------------------------------------------------------------------------------------------------------------
    # CHECK: BLEND FILE MUST BE SAVED
    #
    # Unreal rename operations depend on resolved project/export paths.
    # If the .blend file has never been saved, those paths may not be reliable.
    # In that case, do not show the Unreal rename section at all.

    if not blenderFile.has_blend_filepath():
        return

    # ------------------------------------------------------------------------------------------------------------------
    # CHECK: ACTIVE GAME ENGINE MUST BE UNREAL
    #
    # This menu item is only relevant when Blue Hole is configured for Unreal.
    # For other engines, do not show the Unreal rename section at all.

    if prefs().bridge.active_game_engine != 'unreal':
        return

    # ------------------------------------------------------------------------------------------------------------------
    # CHECK: ACTIVE OBJECT MUST EXIST
    #
    # The Outliner menu can be opened in contexts where no object is active.
    # If no object is available, there is nothing to evaluate or rename.

    obj = context.active_object

    if obj is None:
        return

    # ------------------------------------------------------------------------------------------------------------------
    # RESOLVE: ASSET HIERARCHY ROOT
    #
    # The user may right-click a child object inside an Asset Hierarchy.
    # Unreal rename is only allowed at the Asset Hierarchy root level,
    # so walk up the parent chain and evaluate/rename the top-most object.

    root_obj = obj

    while root_obj.parent is not None:
        root_obj = root_obj.parent

    # ------------------------------------------------------------------------------------------------------------------
    # CHECK: ROOT OBJECT MUST USE A VALID ASSET HIERARCHY PREFIX
    #
    # Only known Asset Hierarchy root prefixes can be renamed in Unreal.
    # If the root object does not match one of these prefixes, show a disabled warning entry.

    ah_prefix_lst: List[str] = [
        prefs().container.asset_hierarchy_struct_prefix_static_mesh,
        prefs().container.asset_hierarchy_struct_prefix_static_mesh_kit,
        prefs().container.asset_hierarchy_struct_prefix_skeletal_mesh,
    ]

    valid_prefix = any(root_obj.name.startswith(prefix) for prefix in ah_prefix_lst)

    layout.separator()

    if not valid_prefix:
        col = layout.column()
        col.enabled = False

        valid_prefix_str = ', '.join(ah_prefix_lst)

        col.operator(
            external_addon_ops.BH_OT_disabled_notice.bl_idname,
            text=f'Cannot rename in Unreal: name must start with {valid_prefix_str}',
            icon='ERROR'
        )

        return

    # ------------------------------------------------------------------------------------------------------------------
    # CHECK: SOURCE CONTENT PATH IS SET/EXISTS
    sc_path: Optional[Path] = get_valid_source_content_path()
    if sc_path is None:
        col = layout.column()
        col.enabled = False
        col.operator(
            external_addon_ops.BH_OT_disabled_notice.bl_idname,
            text='Cannot rename in Unreal: Source Content Path not Valid',
            icon='ERROR'
        )

        return

    # ------------------------------------------------------------------------------------------------------------------
    # RESOLVE: EXPECTED UNREAL .UASSET PATH
    #
    # Build a lightweight/dummy container for the root object so we can resolve where the matching Unreal asset
    # should exist on disk. This does not export anything; it is only used for path resolution.

    export_settings = exportSettingsPresets.get_export_settings(
        exportSettingsPresets.ExportSettingsPreset.UNREAL
    )

    container = ContainerDummy(root_obj, export_settings)

    uasset_path = container.get_path_uasset()

    # ------------------------------------------------------------------------------------------------------------------
    # CHECK: MATCHING .UASSET FILE MUST EXIST
    #
    # The Blender tool should only offer "Rename in Unreal" if there is already an Unreal asset at the expected path.
    # Otherwise, renaming in Blender would not map cleanly to an existing Unreal asset.

    if uasset_path is None or not uasset_path.is_file():
        msg = (
            f'"{root_obj.name}" does not have an expected .uasset file'
            f' "{uasset_path}" and therefore cannot be renamed in Unreal using the Blender tool.'
        )

        log(Severity.WARNING, 'Rename in Outliner and Unreal', msg)

        col = layout.column()
        col.enabled = False

        col.operator(
            external_addon_ops.BH_OT_disabled_notice.bl_idname,
            text='Cannot rename in Unreal: matching .uasset was not found',
            icon='ERROR'
        )

        return

    # ------------------------------------------------------------------------------------------------------------------
    # ADD MENU ITEM: RENAME IN BLENDER + UNREAL
    #
    # Use INVOKE_DEFAULT so the operator opens its rename prompt instead of executing immediately.

    layout.operator_context = 'INVOKE_DEFAULT'

    layout.operator(
        rename_ops.BH_OT_rename_in_outliner_and_unreal.bl_idname,
        icon='GREASEPENCIL'
    )


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

def register():
    bpy.types.OUTLINER_MT_object.append(draw_blue_hole_outliner_object_menu)


def unregister():
    bpy.types.OUTLINER_MT_object.remove(draw_blue_hole_outliner_object_menu)
