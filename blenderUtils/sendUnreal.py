"""
Trigger import command to Unreal.
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

from pathlib import Path

import time

from BlueHole.blenderUtils.debugUtils import print_debug_msg as print_debug_msg
import BlueHole.blenderUtils.fileUtils as fileUtils
from BlueHole.blenderUtils.uiUtils import show_dialog_box as show_dialog_box
import BlueHole.blenderUtils.addon as addon
import BlueHole.blenderUtils.filterUtils as filterUtils
import BlueHole.Lib.send2ue.dependencies.remote_execution as remote_execution
import BlueHole.blenderUtils.exportUtils2 as exportUtils2
import BlueHole.Utils.env as env


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

unreal_response = ''


def trigger_unreal_import(file_path_source):
    """
    Send import command to Unreal (from file path source, to destination)
    :param file_path_source: Source file to import
    :type file_path_source: str
    """

    def display_path_error_source_content(path):
        err_msg = ('The Source Content directory path specified in the active environment\'s env_variables.ini file '
                   'is invalid. Please create said directory or edit env_variables.ini to match your '
                   f'Source Content folder.\n\nAttempted path: "{path}"')
        show_dialog_box('Blender to Unreal Bridge', err_msg)

    def display_path_error_blend(sc_path, blend_path):
        err_msg = ('The currently opened Blender file is not located within the Source Content directory path '
                   'specified in the active environment\'s env_variables.ini file. Please move your blender file '
                   'or edit the Source Content path from env_variables.ini.\n\nExpected blender path to be '
                   f'within: "{sc_path}"'
                   f'\nFound blender path to be: "{blend_path}"')
        show_dialog_box('Blender to Unreal Bridge', err_msg)

    # ------------------------------------------------------------------------------------------------------------------
    # VALIDATE ENV_VARIABLES.INI has valid SourceContent path for Unreal Bridge,
    # and that current .blend file is within.

    # Get SourceContent's directory path from env_variables.ini
    # (the root of where blender files and assets are saved)
    sc_path = env.BlueHolePrefs().get_valid_sc_dir_path()

    # Validate this path is valid, else throw error
    if not sc_path:
        display_path_error_source_content(sc_path)
        return False
    else:
        sc_path_str = str(sc_path)

    # Validate that currently opened blend file has location on disk.
    check_result = filterUtils.check_tests('Export Asset Hierarchy',
                                           check_blend_exist=True)
    if not check_result:
        return False

    # Validate currently opened blend file is within SourceContent
    blend_path = str(Path(fileUtils.get_blend_directory_path()))
    if sc_path_str not in blend_path:
        display_path_error_blend(sc_path_str, blend_path)
        return False

    # ------------------------------------------------------------------------------------------------------------------
    # Know everything is valid, send command to Unreal.

    file_path_dest = file_path_source.replace(sc_path_str, '/Game')

    msg = 'Triggering Unreal import of source file: "{source}" to "{destination}".'.format(source=file_path_source,
                                                                                           destination=file_path_dest)
    print_debug_msg(msg, show_verbose)

    result = import_asset(str(Path(file_path_source)), str(Path(file_path_dest)))
    if not result:
        return False

    print_debug_msg('Command succeeded!', show_verbose)

    return True


def display_cannot_connect_unreal_error():
    msg = 'Blender is not able to communicate with Unreal.' \
          '\n\nPlease make sure:' \
          '\n1)Unreal Editor is opened and has a project loaded.' \
          '\n2)You have followed the setup instructions on the Blue Hole website for the Unreal bridge.'
    show_dialog_box('Blender to Unreal Bridge', msg)


def import_asset(file_path_source, file_path_dest):
    """
    This function imports an asset to unreal based on the asset data in the provided dictionary.

    :param dict asset_data: A dictionary of import parameters.
    :param object properties: The property group that contains variables that maintain the addon's correct state.
    """
    # start a connection to the engine that lets you send python strings
    remote_exec = remote_execution.RemoteExecution()
    remote_exec.start()
    # Fetch properties
    print_debug_msg('Fetching properties...', show_verbose)

    # Was it a skeletal?
    sk_prefix = exportUtils2.get_hierarchy_prefix_lst()[2]
    if sk_prefix == file_path_source.split('/')[-1][0:len(sk_prefix)]:
        print_debug_msg('Export is a skeletal mesh.', show_verbose)
        is_skeletal = True
    else:
        print_debug_msg('Export is not a skeletal mesh.', show_verbose)
        is_skeletal = False

    # Is importing animations?
    include_animation = addon.preference().general.ue_bridge_include_animation

    # Make sure \\ on paths
    file_path_source = file_path_source.replace('\\', '\\\\')
    file_path_dest = file_path_dest.replace('\\', '/')

    file_path_dest = file_path_dest[0:-len(file_path_dest.split('/')[-1])]

    # send over the python code as a string
    run_unreal_python_commands(
        remote_exec,
        '\n'.join([
            f'import_task = unreal.AssetImportTask()',
            f'import_task.filename = r"{file_path_source}"',
            f'import_task.destination_path = r"{file_path_dest}"',
            f'import_task.automated = {addon.preference().general.ue_automated}',
            f'import_task.replace_existing = True',
            f'options = unreal.FbxImportUI()',
            f'options.auto_compute_lod_distances = False',
            f'options.lod_number = 0',
            f'options.import_as_skeletal = {is_skeletal}',
            f'options.import_animations = {include_animation}',
            f'options.import_materials = {addon.preference().general.ue_import_materials}',
            f'options.import_textures = {addon.preference().general.ue_import_textures}',
            f'options.import_mesh = {True}',
            f'options.static_mesh_import_data.generate_lightmap_u_vs = False',
            f'options.lod_distance0 = 1.0',

            # if this is a skeletal mesh import
            f'if {is_skeletal}:',
            f'\toptions.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH',
            f'\toptions.skeletal_mesh_import_data.import_mesh_lo_ds = {False}',

            # if this is an static mesh import
            f'if {not is_skeletal}:',
            f'\toptions.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH',
            f'\toptions.static_mesh_import_data.import_mesh_lo_ds = {False}',

            # if this is an animation import
            f'if {include_animation}:',
            f'\tskeleton_asset = unreal.load_asset(r"{file_path_dest}")',

            # if a skeleton can be loaded from the provided path
            f'\tif skeleton_asset:',
            f'\t\toptions.set_editor_property("skeleton", skeleton_asset)',
            f'\t\toptions.set_editor_property("original_import_type", unreal.FBXImportType.FBXIT_ANIMATION)',
            f'\t\toptions.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)',
            f'\t\toptions.anim_sequence_import_data.set_editor_property("preserve_local_transform", True)',
            f'\telse:',
            f'\t\traise RuntimeError("Unreal could not find a skeleton here: {file_path_dest}")',

            # assign the options object to the import task and import the asset
            f'import_task.options = options',
            f'unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([import_task])',

            # check for a that the game asset imported correctly if the import object name as is False
            f'if {False}:',
            f'\tgame_asset = unreal.load_asset(r"{file_path_dest}")',
            f'\tif not game_asset:',
            f'\t\traise RuntimeError("Multiple roots are found in the bone hierarchy. Unreal will only support a single root bone.")',
        ]))

    # if there is an error report it
    if unreal_response:
        if unreal_response['result'] != 'None':
            display_cannot_connect_unreal_error()
            return False
    return True


def run_unreal_python_commands(remote_exec, commands, failed_connection_attempts=0):
    """
    This function finds the open unreal editor with remote connection enabled, and sends it python commands.

    :param object remote_exec: A RemoteExecution instance.
    :param str commands: A formatted string of python commands that will be run by the engine.
    :param int failed_connection_attempts: A counter that keeps track of how many times an editor connection attempt
    was made.
    """
    # wait a tenth of a second before attempting to connect
    time.sleep(0.1)
    try:
        # default ue remote connection address 239.0.0.1:6766
        for node in remote_exec.remote_nodes:
            remote_exec.open_command_connection(node.get("node_id"))

        # if a connection is made
        if remote_exec.has_command_connection():
            # run the import commands and save the response in the global unreal_response variable
            global unreal_response
            unreal_response = remote_exec.run_command(commands, unattended=False)

        # otherwise make an other attempt to connect to the engine
        else:
            if failed_connection_attempts < 10:
                run_unreal_python_commands(remote_exec, commands, failed_connection_attempts + 1)
            else:
                remote_exec.stop()
                display_cannot_connect_unreal_error()
                return False

    # shutdown the connection
    finally:
        remote_exec.stop()
    return True
