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


def trigger_unreal_import(file_path_source: str) -> bool | set[str]:
    """
    Send an import command to Unreal from the given source file path.
    Uses a custom override operator when enabled, otherwise uses Blue Hole's default Unreal import.
    """
    if prefs().bridge.ue_enable_send_override and prefs().bridge.ue_op_send_override:
        msg = f'Using Unreal Import Override: "{prefs().bridge.ue_op_send_override}"'
        log(Severity.WARNING, send_ue_name, msg)
        return trigger_unreal_import_override(file_path_source)
    else:
        msg = 'Using Blue Hole default Unreal import.'
        log(Severity.INFO, send_ue_name, msg)
        return trigger_unreal_import_default(file_path_source)


def trigger_unreal_import_default(file_path_source: str) -> bool:
    """
    Send an import command to Unreal from the given source file path.

    :param file_path_source: Source file to import
    """

    def display_path_error_blend(sc_path, blend_path):
        err_msg = (
            f'{send_ue_name} validation failed.\n\n'
            f'What went wrong:\n'
            f'The currently opened Blender file is not located within the configured Source Content directory. '
            f'Blender files must reside inside the Source Content folder to be exported.\n\n'
            f'What to do:\n'
            f'Move the Blender file into the Source Content folder, or update the Source Content path '
            f'in the Environment Settings (Structure tab).\n\n'
            f'Configured Source Content path:\n'
            f'"{sc_path}"\n\n'
            f'Current Blender file path:\n'
            f'"{blend_path}"'
        )
        log(Severity.CRITICAL, send_ue_name, err_msg, popup=True)

    # Validate Source Content path from env_variables.ini and ensure the current .blend file is within it.
    sc_path = get_valid_source_content_path()

    if not sc_path:
        display_path_error_source_content(sc_path)
        return False

    sc_path_str = str(sc_path)

    if not filterUtils.check_tests('Export Asset Hierarchy', check_blend_exist=True):
        return False

    blend_path = str(Path(blenderFile.get_blend_directory_path()))
    if sc_path_str not in blend_path:
        display_path_error_blend(sc_path_str, blend_path)
        return False

    file_path_dest = file_path_source.replace(sc_path_str, '/Game')

    msg = f'Triggering Unreal import of source file: "{file_path_source}" to "{file_path_dest}".'
    log(Severity.DEBUG, send_ue_name, msg)

    result = import_asset(str(Path(file_path_source)), str(Path(file_path_dest)))

    if result == {'CANCELLED'}:
        return result

    if not result:
        log(Severity.CRITICAL, send_ue_name, 'Command did not succeed!')
        return False

    log(Severity.DEBUG, send_ue_name, 'Command succeeded!')
    return True


def import_asset(file_path_source: str, file_path_dest: str) -> bool | set[str]:
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

            # Check for an import failure if needed
            f'if {False}:',
            f'\tgame_asset = unreal.load_asset(r"{file_path_dest}")',
            f'\tif not game_asset:',
            f'\t\traise RuntimeError("Multiple roots are found in the bone hierarchy. Unreal will only support a single root bone.")',
        ])
    )

    if result == {'CANCELLED'}:
        return result

    if not result:
        return False

    if communicateUnreal.unreal_response:
        if communicateUnreal.unreal_response['result'] != 'None':
            communicateUnreal.display_cannot_connect_unreal_error()
            return False

    return True
