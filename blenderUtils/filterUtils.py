"""
Filter utilities for Blue Hole.
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

import addon_utils
from pathlib import Path

from . import blenderFile, objectUtils, projectUtils
from ..Lib.commonUtils.debugUtils import *
from ..Lib.commonUtils.osUtils import *
from ..environment import envPathResolver
from ..preferences.prefs import *
from ..wrappers.perforce.p4_info import P4Info
from ..wrappers.sourceContentPath import get_valid_source_content_path

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def filter_source_control():
    return prefs().sourcecontrol.source_control_enable


def check_blend_location_in_dir_structure():
    """
    Validate whether the currently opened scene is in the correct sub-folder according to DirectoryStructure in
    env_variables.ini.
    """
    expected_location_on_disk = str(
        Path(
            projectUtils.get_project_sub_dir(prefs().directory.sc_dir_struct_scenes),
            blenderFile.get_blend_file_name() + '.blend',
        )
    )
    blend_location_on_disk = blenderFile.get_blend_file_path()

    return expected_location_on_disk.replace('\\', '/') == blend_location_on_disk.replace('\\', '/')


def check_addon_loaded(addon_name):
    return addon_utils.check(addon_name)[1]


def check_tests(script_name, *,
                check_blend_exist=False,
                check_blend_loc_in_dir_structure=False,
                check_selection_not_empty=False,
                check_source_control_enable=False,
                check_source_control_connection=False,
                check_source_content_root_path_exist=False,
                check_blend_in_source_content=False,
                check_unity_assets_path_exist=False,
                silent_mode=False
                ):
    """
    Perform a series of tests and return False if any validation fails.

    This is normally run at the beginning of a script to determine whether it should proceed.

    :param script_name: Name of the script attempting the checks. This appears as the title of the message box if an
        exception occurs.
    :param check_blend_exist: Check whether the currently opened blend file is saved on disk.
    :param check_blend_loc_in_dir_structure: Check whether the currently opened blend file is saved in the correct
        location according to the DirectoryStructure of the current environment.
    :param check_selection_not_empty: Check whether at least one object is selected.
    :param check_source_control_enable: Check whether source control is enabled.
    :param check_source_control_connection: Check whether a connection can be established to source control.
    :param check_source_content_root_path_exist: Check whether the Source Content Root Path exists.
    :param check_blend_in_source_content: Check whether the Blender file is within Source Content.
    :param check_unity_assets_path_exist: Check whether the Unity project's Assets path exists.
    :param silent_mode: If True, do not show dialog boxes on errors.
    """

    # ERROR DIALOGUES
    def dialog_check_blend_exist():
        if not silent_mode:
            msg = (
                f'{script_name} validation failed.\n\n'
                f'What went wrong:\n'
                f'The current Blender scene has not been saved to disk. Unsaved scenes cannot be processed.\n\n'
                f'What to do:\n'
                f'Save the Blender file, then run the operation again.\n\n'
                f'Operation aborted.'
            )
            log(Severity.CRITICAL, script_name, msg, popup=not silent_mode)

    def dialog_check_selection_not_empty():
        if not silent_mode:
            msg = (
                f'{script_name} validation failed.\n\n'
                f'What went wrong:\n'
                f'No objects are currently selected. This operation requires at least one selected object.\n\n'
                f'What to do:\n'
                f'Select one or more objects, then run the operation again.\n\n'
                f'Operation aborted.'
            )
            log(Severity.CRITICAL, script_name, msg, popup=not silent_mode)

    def dialog_source_control_enable():
        if not silent_mode:
            msg = (
                f'{script_name} validation failed.\n\n'
                f'What went wrong:\n'
                f'Source Control is currently disabled in the Blue Hole Add-on Settings.\n\n'
                f'What to do:\n'
                f'Enable Source Control in the Blue Hole Add-on Settings, then run the operation again.\n\n'
                f'Operation aborted.'
            )
            log(Severity.CRITICAL, script_name, msg, popup=not silent_mode)

    def dialog_source_control_connection():
        if not silent_mode:
            match get_os():
                case OS.WIN:
                    if prefs().sourcecontrol.win32_env_override:
                        msg = (
                            f'{script_name} connection failed.\n\n'
                            f'What went wrong:\n'
                            f'Blue Hole could not connect to the Perforce server using the configured override settings.\n\n'
                            f'What to do:\n'
                            f'Verify your network and VPN connection, and ensure the Server, User, and Workspace '
                            f'fields in the Blue Hole Add-on Settings (Source Control tab) are correct.\n\n'
                            f'Note: You are currently using Override P4V Environment Settings.'
                        )
                    else:
                        msg = (
                            f'{script_name} connection failed.\n\n'
                            f'What went wrong:\n'
                            f'Blue Hole could not connect to the Perforce server.\n\n'
                            f'What to do:\n'
                            f'Verify your network and VPN connection, and ensure your Perforce Environment Settings '
                            f'are correctly configured in P4V or in the Blue Hole Add-on Settings (Source Control tab).\n\n'
                            f'Note: You may enable "Override P4V Environment Settings" in the Blue Hole Add-on Settings '
                            f'to manually configure the connection.'
                        )

                case OS.MAC | OS.LINUX:
                    msg = (
                        f'{script_name} connection failed.\n\n'
                        f'What went wrong:\n'
                        f'Blue Hole could not connect to the Perforce server.\n\n'
                        f'What to do:\n'
                        f'Verify your network and VPN connection, and ensure the Server, User, and Workspace fields '
                        f'are correctly configured in the Blue Hole Add-on Settings (Source Control tab).'
                    )

            log(Severity.CRITICAL, script_name, msg, popup=not silent_mode)

    def dialog_check_blend_location_in_dir_structure():
        if not silent_mode:
            specified_sub_folder = prefs().directory.sc_dir_struct_scenes

            msg = (
                f'{script_name} validation failed.\n\n'
                f'What went wrong:\n'
                f'The currently opened Blender file is not located in the required Scenes directory defined '
                f'in the Environment Settings.\n\n'
                f'What to do:\n'
                f'Move the Blender file into the correct Scenes directory, or update the Environment Settings '
                f'to match your project\'s directory structure.\n\n'
                f'Configured Scenes directory:\n'
                f'"{specified_sub_folder}"'
            )

            log(Severity.CRITICAL, script_name, msg, popup=not silent_mode)

    def display_path_error_source_content(path):
        msg = (
            f'{script_name} validation failed.\n\n'
            f'What went wrong:\n'
            f'The configured Source Content Root Path could not be accessed. The directory may not exist or is not reachable.\n\n'
            f'What to do:\n'
            f'Create the directory, or update the Environment Settings to point to a valid Source Content folder.\n\n'
            f'Configured Source Content Root Path:\n'
            f'"{path}"'
        )
        log(Severity.CRITICAL, script_name, msg, popup=not silent_mode)

    def display_path_error_unity_assets(path):
        msg = (
            f'{script_name} validation failed.\n\n'
            f'What went wrong:\n'
            f'The configured Unity Assets path could not be accessed. The directory may not exist or is not reachable.\n\n'
            f'What to do:\n'
            f'Create the directory, or update the Environment Settings to point to your Unity project\'s Assets folder.\n\n'
            f'Configured Unity Assets path:\n'
            f'"{path}"\n\n'
            f'Example Unity Assets path:\n'
            f'"C:\\YourUnityProject\\Assets\\"'
        )
        log(Severity.CRITICAL, script_name, msg, popup=not silent_mode)

    def display_path_error_blend(sc_path_seek, blend_path_found):
        msg = (
            f'{script_name} validation failed.\n\n'
            f'What went wrong:\n'
            f'The opened Blender file is not located within the configured Source Content directory. '
            f'This is required to mirror the folder structure into the Unity project during export.\n\n'
            f'What to do:\n'
            f'Move the Blender file into the Source Content directory, or update the Environment Settings '
            f'to point to the correct Source Content folder.\n\n'
            f'Configured Source Content path:\n'
            f'"{sc_path_seek}"\n\n'
            f'Current Blender file path:\n'
            f'"{blend_path_found}"'
        )
        log(Severity.CRITICAL, script_name, msg, popup=not silent_mode)

    # Check if blend exists
    if check_blend_exist:
        if len(blenderFile.get_blend_file_path()) == 0:
            log(Severity.ERROR, script_name, 'Check Blend Exist Failed')
            dialog_check_blend_exist()
            return False
        log(Severity.DEBUG, script_name, 'Check Blend Exist Succeeded!')

    # Check if blend scene is in the proper sub-folder
    if check_blend_loc_in_dir_structure:
        check_result = check_blend_location_in_dir_structure()
        if not check_result:
            log(Severity.ERROR, script_name, 'Check Blend Location in Directory Structure Failed')
            dialog_check_blend_location_in_dir_structure()
            return False
        log(Severity.DEBUG, script_name, 'Check Blend Location in Directory Structure Succeeded')

    # Check if selection is not empty
    if check_selection_not_empty:
        if len(objectUtils.get_selection()) == 0:
            log(Severity.ERROR, script_name, 'Check Selection not Empty Failed')
            dialog_check_selection_not_empty()
            return False
        log(Severity.DEBUG, script_name, 'Check Selection not Empty Succeeded')

    # Check if source control is enabled
    if check_source_control_enable:
        if not prefs().sourcecontrol.source_control_enable:
            log(Severity.ERROR, script_name, 'Check Source Control Enabled: Failed')
            dialog_source_control_enable()
            return False
        log(Severity.DEBUG, script_name, 'Check Source Control Enabled: Succeeded')

    # Check source control connection
    if check_source_control_connection:
        p4_info_cls = P4Info()
        if p4_info_cls.status is False:
            log(Severity.ERROR, script_name, 'Check Source Control Connection: Failed')
            dialog_source_control_connection()
            return False
        log(Severity.DEBUG, script_name, 'Check Source Control: Succeeded')

    # Attempt to get valid source content path
    if check_source_content_root_path_exist or check_blend_in_source_content:
        sc_path = get_valid_source_content_path()
    else:
        sc_path = None

    # Check Source Content Root Path exists
    if check_source_content_root_path_exist:
        if not sc_path:
            display_path_error_source_content(sc_path)
            return False

    # Check Blender file is within Source Content
    if check_blend_in_source_content:
        if not sc_path:
            display_path_error_source_content(sc_path)
            return False

        match get_os():
            case OS.WIN:
                sc_path_str = str(sc_path).lower()
                blend_path = str(Path(blenderFile.get_blend_directory_path())).lower()
            case OS.MAC | OS.LINUX:
                sc_path_str = str(sc_path)
                blend_path = str(Path(blenderFile.get_blend_directory_path()))

        if not blend_path.startswith(sc_path_str):
            display_path_error_blend(sc_path, blend_path)
            return False

    # Check that Unity Assets path exists
    if check_unity_assets_path_exist:
        unity_asset_path = envPathResolver.get_valid_unity_asset_dir_path()

        if not unity_asset_path:
            display_path_error_unity_assets(unity_asset_path)
            return False

    return True
