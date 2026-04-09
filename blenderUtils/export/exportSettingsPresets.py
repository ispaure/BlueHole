"""
Export settings presets for Asset Hierarchy exports.

Introduced in January 2026 alongside the exportUtils3 refactor.
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

from enum import Enum

from ...Lib.commonUtils.debugUtils import *
from ...environment import envPathResolver
from ...preferences.prefs import *
from .. import projectUtils
from .exportSettings import *

# ----------------------------------------------------------------------------------------------------------------------
# CODE


class ExportSettingsPreset(Enum):
    UNREAL = "Unreal"
    UNITY = "Unity"
    GODOT = "Godot"


def get_export_settings(preset: ExportSettingsPreset) -> ExportSettings:
    """
    Resolve the ExportSettings for the given preset.

    This is evaluated at call time instead of plugin initialization
    because preferences and environment paths may change during runtime.
    """

    match preset:

        case ExportSettingsPreset.UNITY:
            export_settings = ExportSettings(
                # NAME
                name="Unity",

                # EXPORT OPTIONS
                exp_format="FBX",
                exp_dir=envPathResolver.get_unity_exp_dir_path(),
                zero_root_transform=prefs().bridge.unity_bridge_zero_root_transform,

                # INCLUDED ELEMENTS
                include_render=prefs().container.create_element_render,
                include_collision=prefs().container.create_element_collision,
                include_socket=prefs().container.create_element_sockets,

                # FBX SPECIFIC OPTIONS
                axis_up=prefs().bridge.unity_up_axis,
                axis_fwd=prefs().bridge.unity_forward_axis,
                mesh_smooth_type="OFF",
                bake_anim=prefs().bridge.unity_bridge_include_animation,
                apply_scale_options="FBX_SCALE_UNITS",
                rename_collisions_for_ue=False,

                # ENGINE
                engine=Engine.UNITY,
            )

        case ExportSettingsPreset.UNREAL:
            export_settings = ExportSettings(
                # NAME
                name="Unreal",

                # EXPORT OPTIONS
                exp_format="FBX",
                exp_dir=projectUtils.get_project_sub_dir(prefs().directory.sc_dir_struct_final),
                zero_root_transform=prefs().bridge.ue_bridge_zero_root_transform,

                # INCLUDED ELEMENTS
                include_render=prefs().container.create_element_render,
                include_collision=prefs().container.create_element_collision,
                include_socket=prefs().container.create_element_sockets,

                # FBX SPECIFIC OPTIONS
                axis_up="Z",
                axis_fwd="-Y",
                mesh_smooth_type="OFF",
                bake_anim=prefs().bridge.ue_bridge_include_animation,
                apply_scale_options="FBX_SCALE_NONE",
                rename_collisions_for_ue=True,

                # ENGINE
                engine=Engine.UNREAL,
            )

        case ExportSettingsPreset.GODOT:
            export_settings = ExportSettings(
                # NAME
                name="Godot",

                # EXPORT OPTIONS
                exp_format=prefs().bridge.godot_export_format.upper(),
                exp_dir=projectUtils.get_project_sub_dir(prefs().directory.sc_dir_struct_final),
                zero_root_transform=prefs().bridge.godot_bridge_zero_root_transform,

                # INCLUDED ELEMENTS
                include_render=prefs().container.create_element_render,
                include_collision=prefs().container.create_element_collision,
                include_socket=prefs().container.create_element_sockets,

                # FBX SPECIFIC OPTIONS
                axis_up=prefs().bridge.godot_up_axis,
                axis_fwd=prefs().bridge.godot_forward_axis,
                mesh_smooth_type="OFF",
                bake_anim=prefs().bridge.godot_bridge_include_animation,
                apply_scale_options="FBX_SCALE_UNITS",
                rename_collisions_for_ue=False,

                # ENGINE
                engine=Engine.GODOT,
            )

        case _:
            log(Severity.CRITICAL, "ExportSettingsPreset", "Requested invalid ExportSettingsPreset")

    return export_settings
