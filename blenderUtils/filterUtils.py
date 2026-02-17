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
import platform
from . import blenderFile, objectUtils, projectUtils
from ..wrappers import perforceWrapper
from ..Lib.commonUtils.debugUtils import *
from ..environment import envPathResolver
from ..preferences.prefs import *
from enum import Enum
from ..Lib.commonUtils.osUtils import *

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def filter_source_control():
    if prefs().sc.source_control_enable:
        return True
    else:
        return False


def check_blend_location_in_dir_structure():
    """
    Validates if yes or not the currently opened scene is in the right sub-folder according to DirectoryStructure in
    env_variables.ini
    """

    expected_location_on_disk = str(Path(projectUtils.get_project_sub_dir(prefs().env.sc_dir_struct_scenes),
                                         blenderFile.get_blend_file_name() + '.blend'
                                         ))
    blend_location_on_disk = blenderFile.get_blend_file_path()
    if expected_location_on_disk.replace('\\', '/') == blend_location_on_disk.replace('\\', '/'):
        return True
    else:
        return False


def check_addon_loaded(addon_name):
    return addon_utils.check(addon_name)[1]


def check_tests(script_name,
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
    Performs a series of tests and returns a warning and false result if something fails. Normally ran at beginning of
    a script to determine whether it should attempt to run or not.
    :param script_name: Name of script that is attempting the checks. This will show up as the title of the message
                        box should an exception occur.
    :type script_name: str
    :param check_blend_exist: Check to see if currently opened blend file is saved on disk
    :type check_blend_exist: bool
    :param check_blend_loc_in_dir_structure: Check to see if currently opened blend file is saved in right location
                                                  in regards to the DirectoryStructure of the current environment.
    :type check_blend_loc_in_dir_structure: bool
    :param check_selection_not_empty: Check to see if there is at least one item selected
    :type check_selection_not_empty: bool
    :param check_source_control_enable: Check to see if source control is enabled
    :type check_source_control_enable: bool
    :param check_source_control_connection: Check to see if connection can be established to source control
    :type check_source_control_connection: bool
    :param check_source_content_root_path_exist: Check to see if Source Content Root Path Exists as specified
    :type check_source_content_root_path_exist: bool
    :param check_blend_in_source_content: Check to see if the Blender file is within Source Content
    :type check_blend_in_source_content: bool
    :param check_unity_assets_path_exist: Check to see if Unity Project's Assets Path Exists
    :type check_unity_assets_path_exist: bool
    :param silent_mode: If silent mode is true, do not show dialog box on errors.
    :type silent_mode: bool
    """

    # ERROR DIALOGUES
    def dialog_check_blend_exist():
        if silent_mode is False:
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
        if silent_mode is False:
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
        if silent_mode is False:
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
                    if prefs().sc.win32_env_override:
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
        if silent_mode is False:
            specified_sub_folder = prefs().env.sc_dir_struct_scenes

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

    # Check if Blend exists
    if check_blend_exist:
        if len(blenderFile.get_blend_file_path()) == 0:
            log(Severity.ERROR, script_name, 'Check Blend Exist Failed')
            dialog_check_blend_exist()
            return False
        log(Severity.DEBUG, script_name, 'Check Blend Exist Succeeded!')

    # Check if Blend scene in proper sub-folder
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
        if not filter_source_control():
            log(Severity.ERROR, script_name, 'Check Source Control Enabled: Failed')
            dialog_source_control_enable()
            return False
        log(Severity.DEBUG, script_name, 'Check Source Control Enabled: Succeeded')

    # Check source control connection
    if check_source_control_connection:
        p4_info_cls = perforceWrapper.P4Info()
        if p4_info_cls.status is False:
            log(Severity.ERROR, script_name, 'Check Source Control Connection: Failed')
            dialog_source_control_connection()
            return False
        log(Severity.DEBUG, script_name, 'Check Source Control: Succeeded')

    # Attempt to get valid source content path
    if check_source_content_root_path_exist or check_blend_in_source_content:
        sc_path = envPathResolver.get_valid_sc_dir_path()
    else:
        sc_path = None

    # Check Source Content Root Path Exists
    if check_source_content_root_path_exist:
        if not sc_path:
            display_path_error_source_content(sc_path)
            return False

    # Check Blender File is within Source Content
    if check_blend_in_source_content:
        if not sc_path:
            display_path_error_source_content(sc_path)
            return False
        sc_path_str = str(sc_path)

        blend_path = str(Path(blenderFile.get_blend_directory_path()))
        if sc_path_str not in blend_path:
            display_path_error_blend(sc_path, blend_path)
            return False

    # Check that Unity Asset's Path Exists
    if check_unity_assets_path_exist:
        unity_asset_path = envPathResolver.get_valid_unity_asset_dir_path()

        if not unity_asset_path:
            display_path_error_unity_assets(unity_asset_path)
            return False

    # Reached the end, so return True
    return True
