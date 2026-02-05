"""
Export Settings for Asset Hierarchy Exports. Created in January 2026, alongside the exportUtils3 refactor.
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
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# ----------------------------------------------------------------------------------------------------------------------
# CODE


class Engine(Enum):
    UNREAL = "Unreal"
    UNITY = "Unity"
    UNDEFINED = "Undefined"


@dataclass(frozen=True, kw_only=True)
class ExportSettings:
    # General Export Settings
    exp_dir: Path
    exp_format: str
    zero_root_transform: bool

    # Included Elements
    include_render: bool
    include_collision: bool
    include_socket: bool

    # FBX Specific Settings
    axis_up: str
    axis_fwd: str
    mesh_smooth_type: str
    bake_anim: bool
    apply_scale_options: str
    rename_collisions_for_ue: bool

    # Engine
    engine: Engine
