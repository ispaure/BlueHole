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

# Blue Hole
from BlueHole.blenderUtils.exportUnity import *
from BlueHole.preferences.prefs import *
from BlueHole.envUtils import projectUtils

# ----------------------------------------------------------------------------------------------------------------------
# CODE


class Engine(Enum):
    UNREAL = "Unreal"
    UNITY = "Unity"
    UNDEFINED = "Undefined"


class ExportSettingsPreset(Enum):
    UNREAL = "Unreal"
    UNITY = "Unity"


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


def get_export_settings(preset: ExportSettingsPreset) -> ExportSettings:
    """
    Made this a get, because we need to get the correct settings at that specific point and not at initial plugin init.
    """
    match preset:
        case ExportSettingsPreset.UNITY:
            preset = ExportSettings(
                # EXPORT OPTIONS
                exp_format="FBX",
                exp_dir=get_unity_exp_dir_path(),
                zero_root_transform=prefs().general.unity_bridge_zero_root_transform,

                # INCLUDED ELEMENTS
                include_render=prefs().env.create_element_render,
                include_collision=prefs().env.create_element_collision,
                include_socket=prefs().env.create_element_sockets,

                # FBX SPECIFIC OPTIONS
                axis_up=prefs().general.unity_up_axis,
                axis_fwd=prefs().general.unity_forward_axis,
                mesh_smooth_type="OFF",
                bake_anim=prefs().general.unity_bridge_include_animation,
                apply_scale_options="FBX_SCALE_UNITS",
                rename_collisions_for_ue=False,

                # ENGINE
                engine=Engine.UNITY)

        case ExportSettingsPreset.UNREAL:
            preset = ExportSettings(
                # EXPORT OPTIONS
                exp_format="FBX",
                exp_dir=projectUtils.get_project_sub_dir("path_final"),
                zero_root_transform=prefs().general.ue_bridge_zero_root_transform,

                # INCLUDED ELEMENTS
                include_render=prefs().env.create_element_render,
                include_collision=prefs().env.create_element_collision,
                include_socket=prefs().env.create_element_sockets,

                # FBX SPECIFIC OPTIONS
                axis_up="Z",
                axis_fwd="-Y",
                mesh_smooth_type="OFF",
                bake_anim=prefs().general.ue_bridge_include_animation,
                apply_scale_options="FBX_SCALE_NONE",
                rename_collisions_for_ue=True,

                # ENGINE
                engine=Engine.UNREAL)
        case _:
            log(Severity.CRITICAL, 'ExportSettingsPreset', 'Requested invalid ExportSettingsPreset')

    return preset
