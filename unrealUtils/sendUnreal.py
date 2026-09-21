"""
Trigger import command to Unreal.
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

from ..Lib.commonUtils.debugUtils import *
from ..preferences.prefs import *
from ..wrappers.sourceContentPath import get_valid_source_content_path, display_path_error_source_content
from ..blenderUtils import blenderFile, filterUtils
from .overrides.ue_send_override import trigger_unreal_import_override
from . import communicateUnreal

# ----------------------------------------------------------------------------------------------------------------------
# CODE

send_ue_name = 'Blue Hole Bridge to Unreal'


def trigger_unreal_import(file_path_source: str) -> bool:
    """
    Send an import command to Unreal from the given source file path.

    When the custom send override is enabled, an operator IDName must be configured.
    Otherwise Blue Hole uses its default Unreal import implementation.
    """
    if prefs().bridge.ue_enable_send_override:
        operator_idname = prefs().bridge.ue_op_send_override.strip()

        if not operator_idname:
            msg = (
                'Unreal Import Override is enabled, but no operator IDName is configured.\n\n'
                'Expected an operator exposing a StringProperty named "path".'
            )
            log(Severity.CRITICAL, send_ue_name, msg, popup=True)
            return False

        msg = f'Using Unreal Import Override: "{operator_idname}"'
        log(Severity.WARNING, send_ue_name, msg)
        return trigger_unreal_import_override(file_path_source)

    msg = 'Using Blue Hole default Unreal import.'
    log(Severity.INFO, send_ue_name, msg)
    return trigger_unreal_import_default(file_path_source)


def trigger_unreal_import_default(file_path_source: str) -> bool:
    """
    Send an import command to Unreal from the given source file path.

    :param file_path_source: Source file to import
    """

    # Validate Source Content path from env_variables.ini and ensure the current .blend file is within it.
    sc_path = get_valid_source_content_path()

    if not sc_path:
        display_path_error_source_content(sc_path)
        return False

    sc_path_str = str(sc_path)

    if not filterUtils.check_tests('Export Asset Hierarchy', check_blend_exist=True, check_blend_in_source_content=True):
        return False

    file_path_dest = file_path_source.replace(sc_path_str, '/Game')

    msg = f'Triggering Unreal import of source file: "{file_path_source}" to "{file_path_dest}".'
    log(Severity.DEBUG, send_ue_name, msg)

    result = import_asset(str(Path(file_path_source)), str(Path(file_path_dest)))

    if not result:
        return False

    return True


def import_asset(file_path_source: str, file_path_dest: str) -> bool:
    """
    Import an asset into Unreal.
    """
    log(Severity.DEBUG, send_ue_name, 'Fetching Properties...')

    sk_prefix = prefs().container.asset_hierarchy_struct_prefix_skeletal_mesh
    if sk_prefix == file_path_source.split('/')[-1][0:len(sk_prefix)]:
        log(Severity.DEBUG, send_ue_name, 'Export is a Skeletal Mesh')
        is_skeletal = True
    else:
        log(Severity.DEBUG, send_ue_name, 'Export is a Static Mesh')
        is_skeletal = False

    include_animation = prefs().bridge.ue_bridge_include_animation

    recompute_normals = prefs().bridge.ue_recompute_normals
    recompute_tangents = prefs().bridge.ue_recompute_tangents
    compute_weighted_normals = prefs().bridge.ue_compute_weighted_normals

    enable_nanite = prefs().bridge.ue_enable_nanite
    nanite_keep_triangle_percent = prefs().bridge.ue_nanite_keep_triangle_percent
    nanite_trim_relative_error = prefs().bridge.ue_nanite_trim_relative_error
    nanite_fallback_target = prefs().bridge.ue_nanite_fallback_target

    file_path_source = file_path_source.replace('\\', '\\\\')
    file_path_dest = file_path_dest.replace('\\', '/')
    file_path_dest = file_path_dest[0:-len(file_path_dest.split('/')[-1])]

    result = communicateUnreal.run_unreal_python_commands(
        '\n'.join([
            f'import_task = unreal.AssetImportTask()',
            f'import_task.filename = r"{file_path_source}"',
            f'import_task.destination_path = r"{file_path_dest}"',
            f'import_task.automated = {prefs().bridge.ue_automated}',
            f'import_task.replace_existing = True',
            f'options = unreal.FbxImportUI()',
            f'options.auto_compute_lod_distances = False',
            f'options.lod_number = 0',
            f'options.import_as_skeletal = {is_skeletal}',
            f'options.import_animations = {include_animation}',
            f'options.import_materials = {prefs().bridge.ue_import_materials}',
            f'options.import_textures = {prefs().bridge.ue_import_textures}',
            f'options.import_mesh = {True}',
            f'options.static_mesh_import_data.generate_lightmap_u_vs = False',
            f'options.lod_distance0 = 1.0',

            # Skeletal mesh import
            f'if {is_skeletal}:',
            f'\toptions.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH',
            f'\toptions.skeletal_mesh_import_data.import_mesh_lo_ds = {False}',

            # Static mesh import
            f'if {not is_skeletal}:',
            f'\toptions.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH',
            f'\toptions.static_mesh_import_data.import_mesh_lo_ds = {False}',
            f'\toptions.static_mesh_import_data.set_editor_property("combine_meshes", True)',

            # Normal / tangent import mode.
            f'\tif {recompute_normals}:',
            f'\t\toptions.static_mesh_import_data.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_COMPUTE_NORMALS)',
            f'\telif {recompute_tangents}:',
            f'\t\toptions.static_mesh_import_data.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)',
            f'\telse:',
            f'\t\toptions.static_mesh_import_data.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)',

            f'\toptions.static_mesh_import_data.set_editor_property("compute_weighted_normals", {compute_weighted_normals})',

            # Unreal 5 only. Unreal 4 does not expose build_nanite.
            f'\tif hasattr(options.static_mesh_import_data, "build_nanite"):',
            f'\t\toptions.static_mesh_import_data.set_editor_property("build_nanite", {enable_nanite})',

            # Animation import
            f'if {include_animation}:',
            f'\tskeleton_asset = unreal.load_asset(r"{file_path_dest}")',

            f'\tif skeleton_asset:',
            f'\t\toptions.set_editor_property("skeleton", skeleton_asset)',
            f'\t\toptions.set_editor_property("original_import_type", unreal.FBXImportType.FBXIT_ANIMATION)',
            f'\t\toptions.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)',
            f'\t\toptions.anim_sequence_import_data.set_editor_property("preserve_local_transform", True)',
            f'\telse:',
            f'\t\traise RuntimeError("Unreal could not find a skeleton here: {file_path_dest}")',

            f'import_task.options = options',
            f'unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([import_task])',

            # Nanite sub-settings are applied only after a successful static-mesh import.
            # This whole block is skipped in Unreal 4 and whenever Nanite is disabled.
            f'if {not is_skeletal} and {enable_nanite} and hasattr(unreal, "StaticMeshEditorSubsystem"):',
            f'\tstatic_mesh_editor = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)',

            f'\tfor imported_object_path in import_task.imported_object_paths:',
            f'\t\timported_asset = unreal.load_asset(imported_object_path)',
            f'\t\tif not isinstance(imported_asset, unreal.StaticMesh):',
            f'\t\t\tcontinue',

            f'\t\tnanite_settings = static_mesh_editor.get_nanite_settings(imported_asset)',
            f'\t\tnanite_settings.set_editor_property("keep_percent_triangles", {nanite_keep_triangle_percent} / 100.0)',
            f'\t\tnanite_settings.set_editor_property("trim_relative_error", {nanite_trim_relative_error})',

            # Fallback Target is version-dependent, so only set it when both the enum and property exist.
            f'\t\tif hasattr(unreal, "NaniteFallbackTarget"):',
            f'\t\t\tfallback_target_map = {{',
            f'\t\t\t\t"percent_triangles": unreal.NaniteFallbackTarget.PERCENT_TRIANGLES,',
            f'\t\t\t\t"relative_error": unreal.NaniteFallbackTarget.RELATIVE_ERROR,',
            f'\t\t\t}}',
            f'\t\t\tfallback_target = fallback_target_map.get("{nanite_fallback_target}")',
            f'\t\t\tif fallback_target is not None:',
            f'\t\t\t\ttry:',
            f'\t\t\t\t\tnanite_settings.set_editor_property("fallback_target", fallback_target)',
            f'\t\t\t\texcept Exception:',
            f'\t\t\t\t\tpass',

            f'\t\tstatic_mesh_editor.set_nanite_settings(imported_asset, nanite_settings, True)',

            # Check for an import failure if needed
            f'if {False}:',
            f'\tgame_asset = unreal.load_asset(r"{file_path_dest}")',
            f'\tif not game_asset:',
            f'\t\traise RuntimeError("Multiple roots are found in the bone hierarchy. Unreal will only support a single root bone.")',
        ])
    )

    if not result:
        return False

    if communicateUnreal.unreal_response:
        if communicateUnreal.unreal_response['result'] != 'None':
            communicateUnreal.display_cannot_connect_unreal_error()
            return False

    return True
