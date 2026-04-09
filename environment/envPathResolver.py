"""
Environment path resolver utilities for Blue Hole.
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
from typing import *

from ..Lib.commonUtils.debugUtils import *
from ..Lib.commonUtils.osUtils import *
from ..blenderUtils import blenderFile
from ..preferences.prefs import *
from ..wrappers.sourceContentPath import get_valid_source_content_path

# ----------------------------------------------------------------------------------------------------------------------
# CODE


env_tool_name = filename = os.path.basename(__file__)


def get_dir_path_if_valid(path_def: str, path_str: str, quiet: bool) -> Optional[Path]:
    """
    Validate a directory path string and return it as a Path if valid.
    """
    if len(path_str) == 0 or path_str.startswith('<'):
        msg = (
            f'{path_def} Path "{path_str}" is undefined. It is required for the bridges to game '
            f'engines. Navigate to Blender Blue Hole settings and define a Source Content Path.'
        )
        log(Severity.CRITICAL, env_tool_name, msg, popup=not quiet)
        return None

    if not os.path.exists(path_str):
        msg = (
            f'{path_def} Path "{path_str}" does not correspond to a valid path on disk. '
            f'Navigate to Blender Blue Hole settings and define a valid Source Content Path.'
        )
        log(Severity.CRITICAL, env_tool_name, msg, popup=not quiet)
        return None

    if os.path.isfile(path_str):
        msg = (
            f'{path_def} Path "{path_str}" points to a file, not a directory. Navigate to '
            f'Blender Blue Hole settings and define a Source Content Path that points to a directory.'
        )
        log(Severity.CRITICAL, env_tool_name, msg, popup=not quiet)
        return None

    return Path(path_str)


# ----------------------------------------------------------------------------------------------------------------------
# UNITY


def get_valid_unity_asset_dir_path(quiet: bool = False) -> Optional[Path]:
    """
    Attempt to get a valid Unity Assets path from the current Blue Hole settings, regardless of OS.
    """
    path_def = 'Unity Assets'

    match get_os():
        case OS.WIN:
            unity_asset_path = prefs().bridge.unity_assets_path
        case OS.MAC:
            unity_asset_path = prefs().bridge.unity_assets_path_mac
        case OS.LINUX:
            unity_asset_path = prefs().bridge.unity_assets_path_linux

    result = get_dir_path_if_valid(path_def, unity_asset_path, quiet)
    if result:
        return result

    error_msg = (
        f'Unable to find a valid {path_def} Path in Blue Hole settings, which is required for the '
        'bridge to Unity. See log for more details.'
    )
    log(Severity.CRITICAL, env_tool_name, error_msg, popup=not quiet)
    return None


def get_valid_godot_project_dir_path(quiet: bool = False) -> Optional[Path]:
    """
    Attempt to get a valid Godot Project Root Path from the current Blue Hole settings, regardless of OS.
    """
    path_def = 'Godot Project Root'

    match get_os():
        case OS.WIN:
            godot_project_root_path = prefs().bridge.godot_project_root_path
        case OS.MAC:
            godot_project_root_path = prefs().bridge.godot_project_root_path_mac
        case OS.LINUX:
            godot_project_root_path = prefs().bridge.godot_project_root_path_linux

    result = get_dir_path_if_valid(path_def, godot_project_root_path, quiet)
    if result:
        return result

    error_msg = (
        f'Unable to find a valid {path_def} Path in Blue Hole settings, which is required for the '
        'bridge to Godot. See log for more details.'
    )
    log(Severity.CRITICAL, env_tool_name, error_msg, popup=not quiet)
    return None


def get_unity_exp_dir_path(quiet: bool = False) -> Optional[Path]:
    """
    Get the Unity export path within the Assets folder so it mirrors the Source Content path.

    This is older code that has intentionally been left mostly untouched to avoid changing behavior.
    """
    blend_dir_path = blenderFile.get_blend_directory_path()

    sc_path = get_valid_source_content_path()
    if not sc_path:
        return None
    else:
        sc_path_str = str(sc_path)

    unity_asset_path = get_valid_unity_asset_dir_path(quiet)
    if not unity_asset_path:
        return None
    else:
        unity_asset_path_str = str(unity_asset_path)

    sc_path_str = sc_path_str.replace('\\', '/')
    unity_asset_path_str = unity_asset_path_str.replace('\\', '/')
    blend_dir_path = blend_dir_path.replace('\\', '/')

    exp_dir = blend_dir_path.replace(sc_path_str, unity_asset_path_str)

    return Path(exp_dir)


def get_godot_exp_dir_path(quiet: bool = False) -> Optional[Path]:
    """
    Get the Godot export path within the Assets folder so it mirrors the Source Content path.
    """
    blend_dir_path = blenderFile.get_blend_directory_path()

    sc_path = get_valid_source_content_path()
    if not sc_path:
        return None
    else:
        sc_path_str = str(sc_path)

    godot_root_path = get_valid_godot_project_dir_path(quiet)
    if not godot_root_path:
        return None
    else:
        godot_root_path_str = str(godot_root_path)

    sc_path_str = sc_path_str.replace('\\', '/')
    godot_root_path_str = godot_root_path_str.replace('\\', '/')
    blend_dir_path = blend_dir_path.replace('\\', '/')

    exp_dir = blend_dir_path.replace(sc_path_str, godot_root_path_str)

    return Path(exp_dir)
