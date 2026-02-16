"""
Update description
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

# System
from typing import *
from pathlib import Path

# Blue Hole
from ..Lib.commonUtils.debugUtils import *
from ..blenderUtils import blenderFile
from ..preferences.prefs import *
from ..Lib.commonUtils.osUtils import *

# ----------------------------------------------------------------------------------------------------------------------
# CODE


env_tool_name = filename = os.path.basename(__file__)


def get_dir_path_if_valid(path_def: str, path_str: str, quiet: bool) -> Optional[Path]:

    # Validate something other than default has been set.
    if len(path_str) == 0 or path_str.startswith('<'):
        msg = (f'{path_def} Path "{path_str}" is undefined. It is required for the bridges to game '
               f'engines. Navigate to Blender Blue Hole settings and define a Source Content Path.')
        log(Severity.CRITICAL, env_tool_name, msg, popup=not quiet)
        return None

    # Validate the path exists
    if not os.path.exists(path_str):
        msg = (f'{path_def} Path "{path_str}" does not correspond to a valid path on disk. '
               f'Navigate to Blender Blue Hole settings and define a valid Source Content Path.')
        log(Severity.CRITICAL, env_tool_name, msg, popup=not quiet)
        return None

    # Validate the path is not pointing to a file
    if os.path.isfile(path_str):
        msg = (f'{path_def} Path "{path_str}" points to a file, not a directory. Navigate to '
               f'Blender Blue Hole settings and define a Source Content Path that points to a directory.')
        log(Severity.CRITICAL, env_tool_name, msg, popup=not quiet)
        return None

    # Passed the Checks -- Return the Path!
    return Path(path_str)


def get_valid_sc_dir_path(quiet: bool = False) -> Optional[Path]:
    """Attempts to get a valid source content path from the current Blue Hole settings, regardless of OS"""
    path_def = 'Source Content'
    match get_os():
        case OS.WIN:
            sc_path_to_attempt_lst = [prefs().env.sc_path,
                                      prefs().env.sc_path_alternate]
        case OS.MAC:
            sc_path_to_attempt_lst = [prefs().env.sc_path_mac,
                                      prefs().env.sc_path_mac_alternate]
        case OS.LINUX:
            sc_path_to_attempt_lst = [prefs().env.sc_path_linux,
                                      prefs().env.sc_path_linux_alternate]

    # Attempt to get the source content path from the available options
    for sc_path in sc_path_to_attempt_lst:
        result = get_dir_path_if_valid(path_def, sc_path, quiet)
        if result:
            return result

    # If got here without able to return, no path was valid
    error_msg = (f'Unable to find a valid {path_def} Path in Blue Hole settings, which is required for the '
                 'bridges to game engines. See log for more details.')
    log(Severity.CRITICAL, env_tool_name, error_msg, popup=not quiet)
    return None

# ----------------------------------------------------------------------------------------------------------------------
# UNITY


def get_valid_unity_asset_dir_path(quiet: bool = False) -> Optional[Path]:
    """Attempts to get a valid unity asset path from the current Blue Hole settings, regardless of OS"""
    path_def = 'Unity Assets'

    match get_os():
        case OS.WIN:
            unity_asset_path = prefs().general.unity_assets_path
        case OS.MAC:
            unity_asset_path = prefs().general.unity_assets_path_mac
        case OS.LINUX:
            unity_asset_path = prefs().general.unity_assets_path_linux

    # Attempt to get the unity asset path from the available options
    result = get_dir_path_if_valid(path_def, unity_asset_path, quiet)
    if result:
        return result

    # If got here without able to return, no path was valid
    error_msg = (f'Unable to find a valid {path_def} Path in Blue Hole settings, which is required for the '
                 'bridge to Unity. See log for more details.')
    log(Severity.CRITICAL, env_tool_name, error_msg, popup=quiet)
    return None


def get_unity_exp_dir_path(quiet: bool = False) -> Optional[Path]:
    """
    Gets the Unity export path within Assets folder, so it mirrors the Source Content path.
    This is quite old code now, and I don't really test Blue Hole on Unity anymore, so I left this untouched
    instead of refactoring it, in fear of it causing any difference in results.
    """
    # EXPORT OPTIONS
    # Export Format

    # Determine Export Directory
    blend_dir_path = blenderFile.get_blend_directory_path()

    # Get sc path
    sc_path = get_valid_sc_dir_path(quiet)
    if not sc_path:
        return None
    else:
        sc_path_str = str(sc_path)

    # Get unity assets path
    unity_asset_path = get_valid_unity_asset_dir_path(quiet)
    if not unity_asset_path:
        return None
    else:
        unity_asset_path_str = str(unity_asset_path)

    # Ensure most chances of swap
    sc_path_str = sc_path_str.replace('\\', '/')
    unity_asset_path_str = unity_asset_path_str.replace('\\', '/')
    blend_dir_path = blend_dir_path.replace('\\', '/')

    # Swap
    exp_dir = blend_dir_path.replace(sc_path_str, unity_asset_path_str)

    # Normalize Path for OS
    return Path(exp_dir)
