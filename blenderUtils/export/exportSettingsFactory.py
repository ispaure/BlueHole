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
from typing import *

# Blue Hole
from BlueHole.preferences.prefs import *
import BlueHole.blenderUtils.projectUtils as projectUtils
from BlueHole.blenderUtils.export.exportSettings import *

# ----------------------------------------------------------------------------------------------------------------------
# CODE


class ExportSettingsFactory:
    """ Create an ExportSettings class from a dictionary. Kept for legacy / keep existing behavior. """
    @staticmethod
    def from_dict(preset: Mapping[str, Any], *, engine: Engine) -> ExportSettings:
        included = preset.get("Included Elements", {})

        export_set_cls = ExportSettings(
            # EXPORT OPTIONS
            exp_format=preset.get("Format", "FBX"),
            exp_dir=preset.get("Export Directory", projectUtils.get_project_sub_dir("path_resources")),
            zero_root_transform=preset.get("Zero Root Transform", False),

            # INCLUDED ELEMENTS
            include_render=included.get("Render", prefs().env.create_element_render),
            include_collision=included.get("Collision", prefs().env.create_element_collision),
            include_socket=included.get("Socket", prefs().env.create_element_sockets),

            # FBX SPECIFIC OPTIONS
            axis_up=preset.get("Axis Up", "Z"),
            axis_fwd=preset.get("Axis Forward", "-Y"),
            mesh_smooth_type=preset.get("Mesh Smooth Type", "OFF"),
            bake_anim=preset.get("Bake Animation", prefs().general.ue_bridge_include_animation),
            apply_scale_options=preset.get("Apply Scale Option", "FBX_SCALE_NONE"),
            rename_collisions_for_ue=preset.get("Rename Collisions for UE", False),

            engine=engine)
        return export_set_cls
