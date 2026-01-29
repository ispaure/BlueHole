"""
Function(s) related to the exports to Unity
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
import os
from pathlib import Path
from typing import *
from dataclasses import dataclass
from enum import Enum

# Blender
import bpy

# Blue Hole
import BlueHole.blenderUtils.sourceControlUtils as scUtils
from BlueHole.blenderUtils.debugUtils import *
import BlueHole.blenderUtils.sceneUtils as sceneUtils
import BlueHole.blenderUtils.objectUtils as oUtils
import BlueHole.blenderUtils.fileUtils as fileUtils
import BlueHole.envUtils.projectUtils as projectUtils
import BlueHole.blenderUtils.addon as addon
import BlueHole.blenderUtils.filterUtils as filterUtils
import BlueHole.blenderUtils.objectUtils as objectUtils
import BlueHole.blenderUtils.sendUnreal as sendUnreal
import BlueHole.blenderUtils.configUtils as configUtils
import BlueHole.Utils.env as env

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def get_unity_exp_dir_path(quiet: bool = False) -> Optional[Path]:
    """
    Gets the Unity export path within Assets folder, so it mirrors the Source Content path.
    This is quite old code now, and I don't really test Blue Hole on Unity anymore, so I left this untouched
    instead of refactoring it, in fear of it causing any difference in results.
    """
    # EXPORT OPTIONS
    # Export Format

    # Determine Export Directory
    blend_dir_path = fileUtils.get_blend_directory_path()

    # Blue Hole Prefs Class
    bh_prefs_cls = env.BlueHolePrefs()

    # Get sc path
    sc_path = bh_prefs_cls.get_valid_sc_dir_path(quiet)
    if not sc_path:
        return None
    else:
        sc_path_str = str(sc_path)

    # Get unity assets path
    unity_asset_path = bh_prefs_cls.get_valid_unity_asset_dir_path(quiet)
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
