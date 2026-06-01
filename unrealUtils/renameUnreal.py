"""
Trigger rename command to Unreal.
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

from pathlib import Path

from ..preferences.prefs import *
from .overrides.ue_rename_override import trigger_unreal_rename_override
from ..Lib.commonUtils.debugUtils import *
from ..wrappers.sourceContentPath import get_valid_source_content_path, display_path_error_source_content
from . import communicateUnreal

# ----------------------------------------------------------------------------------------------------------------------
# CODE

rename_ue_name = 'Blue Hole Rename in Unreal'


def trigger_unreal_rename(old_uasset_path: Path, new_uasset_path: Path) -> bool | set[str]:
    """
    Rename/move an Unreal asset using its .uasset path on disk.
    Uses a custom override operator when enabled, otherwise uses Blue Hole's default Unreal rename.
    """
    unreal_source_path, unreal_destination_path = get_unreal_rename_paths(old_uasset_path, new_uasset_path)

    if not unreal_source_path or not unreal_destination_path:
        return False

    if prefs().bridge.ue_enable_rename_override and prefs().bridge.ue_op_rename_override:
        msg = f'Using Unreal Rename Override: "{prefs().bridge.ue_op_rename_override}"'
        log(Severity.WARNING, rename_ue_name, msg)
        return trigger_unreal_rename_override(unreal_source_path=unreal_source_path, unreal_destination_path=unreal_destination_path)
    else:
        msg = 'Using Blue Hole default Unreal rename.'
        log(Severity.INFO, rename_ue_name, msg)
        return trigger_unreal_rename_default(unreal_source_path, unreal_destination_path)


def get_unreal_rename_paths(old_uasset_path: Path, new_uasset_path: Path) -> tuple[str | None, str | None]:
    sc_path = get_valid_source_content_path()

    if not sc_path:
        display_path_error_source_content(sc_path)
        return None, None

    # Convert Source Content path to Unreal Content path.
    content_path = sc_path.parent / 'Content'

    old_game_path = str(old_uasset_path).replace(str(content_path), '/Game')
    new_game_path = str(new_uasset_path).replace(str(content_path), '/Game')

    old_game_path = old_game_path.replace('\\', '/').replace('.uasset', '')
    new_game_path = new_game_path.replace('\\', '/').replace('.uasset', '')

    return old_game_path, new_game_path


def trigger_unreal_rename_default(unreal_source_path: str, unreal_destination_path: str) -> bool | set[str]:
    msg = f'Renaming Unreal asset: "{unreal_source_path}" -> "{unreal_destination_path}".'
    log(Severity.DEBUG, rename_ue_name, msg)

    return _rename_asset(unreal_source_path, unreal_destination_path)


def _rename_asset(old_game_path: str, new_game_path: str) -> bool | set[str]:
    new_asset_name = new_game_path.split('/')[-1]
    new_package_path = '/'.join(new_game_path.split('/')[:-1])

    result = communicateUnreal.run_unreal_python_commands(
        '\n'.join([
            f'old_asset_path = r"{old_game_path}"',
            f'new_package_path = r"{new_package_path}"',
            f'new_asset_name = r"{new_asset_name}"',
            f'asset = unreal.load_asset(old_asset_path)',
            f'if not asset:',
            f'\traise RuntimeError(f"Unreal could not find asset to rename: {{old_asset_path}}")',
            f'asset_tools = unreal.AssetToolsHelpers.get_asset_tools()',
            f'rename_data = unreal.AssetRenameData(asset, new_package_path, new_asset_name)',
            f'result = asset_tools.rename_assets([rename_data])',
            f'if not result:',
            f'\traise RuntimeError(f"Unreal failed to rename asset: {{old_asset_path}} -> {{new_package_path}}/{{new_asset_name}}")',
            f'unreal.EditorAssetLibrary.save_directory(new_package_path)',
        ])
    )

    if result == {'CANCELLED'}:
        return result

    if not result:
        return False

    if communicateUnreal.unreal_response:
        if communicateUnreal.unreal_response['result'] != 'None':
            communicateUnreal.display_cannot_connect_unreal_error()
            return False

    return True
