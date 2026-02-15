"""
Platform utilities for Blue Hole.
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
import platform
from enum import Enum


# ----------------------------------------------------------------------------------------------------------------------
# CODE


class OS(Enum):
    WIN = 'Windows'
    MAC = 'macOS'
    LINUX = 'Linux'


def get_platform() -> OS:
    system = platform.system()

    if system == 'Windows':
        return OS.WIN
    elif system == 'Darwin':  # macOS (Intel + Apple Silicon)
        return OS.MAC
    elif system == 'Linux':
        return OS.LINUX
    else:
        raise RuntimeError(f'Unsupported platform: {system}')