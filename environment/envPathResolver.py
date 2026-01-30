"""
Update description
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

# System
from typing import *
from pathlib import Path

# Blue Hole
from BlueHole.blenderUtils.debugUtils import *
import BlueHole.blenderUtils.filterUtils as filterUtils
from BlueHole.preferences.prefs import *

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

    if filterUtils.filter_platform('win'):
        sc_path_to_attempt_lst = [prefs().env.sc_path,
                                  prefs().env.sc_path_alternate]
    elif filterUtils.filter_platform('mac'):
        sc_path_to_attempt_lst = [prefs().env.sc_path_mac,
                                  prefs().env.sc_path_mac_alternate]
    else:
        msg_os = 'Invalid OS! Blue Hole only supports Windows & macOS at the moment.'
        log(Severity.CRITICAL, env_tool_name, msg_os)
        return None

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


def get_valid_unity_asset_dir_path(quiet: bool = False) -> Optional[Path]:
    """Attempts to get a valid unity asset path from the current Blue Hole settings, regardless of OS"""
    path_def = 'Unity Assets'

    if filterUtils.filter_platform('win'):
        unity_asset_path = prefs().general.unity_assets_path
    elif filterUtils.filter_platform('mac'):
        unity_asset_path = prefs().general.unity_assets_path_mac
    else:
        msg_os = 'Invalid OS! Blue Hole only supports Windows & macOS at the moment.'
        log(Severity.CRITICAL, env_tool_name, msg_os)
        return None

    # Attempt to get the unity asset path from the available options
    result = get_dir_path_if_valid(path_def, unity_asset_path, quiet)
    if result:
        return result

    # If got here without able to return, no path was valid
    error_msg = (f'Unable to find a valid {path_def} Path in Blue Hole settings, which is required for the '
                 'bridge to Unity. See log for more details.')
    log(Severity.CRITICAL, env_tool_name, error_msg, popup=quiet)
    return None
