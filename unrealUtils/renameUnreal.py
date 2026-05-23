"""
Trigger import command to Unreal.
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

from ..Lib.commonUtils.debugUtils import *
from ..Lib.send2ue.dependencies import remote_execution
from ..wrappers.sourceContentPath import get_valid_source_content_path
from . import communicateUnreal

# ----------------------------------------------------------------------------------------------------------------------
# CODE

rename_ue_name = 'Blue Hole Rename in Unreal'


def trigger_unreal_rename(old_uasset_path: Path, new_uasset_path: Path) -> bool:
    """
    Rename/move an Unreal asset using its .uasset path on disk.

    :param old_uasset_path: Existing .uasset file path
    :param new_uasset_path: Target .uasset file path
    """
    sc_path = get_valid_source_content_path()

    if not sc_path:
        communicateUnreal.display_cannot_connect_unreal_error()
        return False

    content_path = sc_path.parent / 'Content'

    old_game_path = str(old_uasset_path).replace(str(content_path), '/Game')
    new_game_path = str(new_uasset_path).replace(str(content_path), '/Game')

    old_game_path = old_game_path.replace('\\', '/').replace('.uasset', '')
    new_game_path = new_game_path.replace('\\', '/').replace('.uasset', '')

    msg = f'Renaming Unreal asset: "{old_game_path}" -> "{new_game_path}".'
    log(Severity.DEBUG, rename_ue_name, msg)

    return rename_asset(old_game_path, new_game_path)


def rename_asset(old_game_path: str, new_game_path: str) -> bool:
    """
    Rename/move an Unreal asset.
    """
    remote_exec = remote_execution.RemoteExecution()
    remote_exec.start()
    old_game_path = old_game_path.replace('\\', '/')
    new_game_path = new_game_path.replace('\\', '/')
    new_asset_name = new_game_path.split('/')[-1]
    new_package_path = '/'.join(new_game_path.split('/')[:-1])
    communicateUnreal.run_unreal_python_commands(
        remote_exec,
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

    if communicateUnreal.unreal_response:
        if communicateUnreal.unreal_response['result'] != 'None':
            communicateUnreal.display_cannot_connect_unreal_error()
            return False

    return True
