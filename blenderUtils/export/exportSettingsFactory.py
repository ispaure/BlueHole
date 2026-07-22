"""
Factory utilities for creating ExportSettings instances from preset dictionaries.

Introduced alongside the exportUtils3 refactor (January 2026).
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

from dataclasses import dataclass
from enum import Enum
from typing import *

from ...preferences.prefs import *
from .. import projectUtils
from .exportSettings import *

# ----------------------------------------------------------------------------------------------------------------------
# CODE


class ExportSettingsFactory:
    """
    Create an ExportSettings instance from a dictionary preset.

    This factory is kept for legacy compatibility and preserves existing behavior.
    """

    @staticmethod
    def from_dict(preset: Mapping[str, Any], *, engine: Engine) -> ExportSettings:

        included = preset.get("Included Elements", {})

        export_set_cls = ExportSettings(
            # EXPORT OPTIONS
            exp_format=preset.get("Format", "FBX"),
            exp_dir=preset.get(
                "Export Directory",
                projectUtils.get_project_sub_dir(prefs().directory.sc_dir_struct_final),
            ),
            zero_root_transform=preset.get("Zero Root Transform", False),

            # INCLUDED ELEMENTS
            include_render=included.get("Render", prefs().container.create_element_render),
            include_collision=included.get("Collision", prefs().container.create_element_collision),
            include_socket=included.get("Socket", prefs().container.create_element_sockets),

            # FBX SPECIFIC OPTIONS
            axis_up=preset.get("Axis Up", "Z"),
            axis_fwd=preset.get("Axis Forward", "-Y"),
            mesh_smooth_type=preset.get("Mesh Smooth Type", "OFF"),
            bake_anim=preset.get("Bake Animation", prefs().bridge.ue_bridge_include_animation),
            apply_scale_options=preset.get("Apply Scale Option", "FBX_SCALE_NONE"),
            rename_collisions_for_ue=preset.get("Rename Collisions for UE", False),
            use_mesh_modifiers=preset.get("Use Mesh Modifiers", True),

            engine=engine,
        )

        return export_set_cls
