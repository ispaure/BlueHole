"""
Filter utilities for Blue Hole.
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

import sys
import addon_utils
from pathlib import Path

import BlueHole.blenderUtils.addon as addon
import BlueHole.blenderUtils.fileUtils as fileUtils
import BlueHole.blenderUtils.objectUtils as objectUtils
import BlueHole.wrappers.perforceWrapper as p4Wrapper
import BlueHole.envUtils.projectUtils as projectUtils
from BlueHole.blenderUtils.debugUtils import *
import BlueHole.Utils.env as env


# ----------------------------------------------------------------------------------------------------------------------
# CODE

def filter_platform(platform):
    if platform == 'win':
        if sys.platform == 'win32':
            return True
        else:
            return False

    elif platform == 'mac':
        if sys.platform != 'win32':
            return True
        else:
            return False


def filter_source_control():
    if addon.preference().sourcecontrol.source_control_enable:
        return True
    else:
        return False


def check_blend_location_in_dir_structure():
    """
    Validates if yes or not the currently opened scene is in the right sub-folder according to DirectoryStructure in
    env_variables.ini
    """

    expected_location_on_disk = str(Path(projectUtils.get_project_sub_dir('path_scenes'),
                                         fileUtils.get_blend_file_name() + '.blend'
                                         ))
    blend_location_on_disk = fileUtils.get_blend_file_path()
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
            msg = 'Cannot execute script because Blender file is not saved on disk. Save Blender scene and try again.'
            log(Severity.CRITICAL, script_name, msg, popup=not silent_mode)

    def dialog_check_selection_not_empty():
        if silent_mode is False:
            msg = 'Cannot execute script because selection is empty. Select at least one element and try again.'
            log(Severity.CRITICAL, script_name, msg, popup=not silent_mode)

    def dialog_source_control_enable():
        if silent_mode is False:
            msg = 'Cannot execute script because Source Control is currently disabled in the Blue Hole Add-ons ' \
                  'settings. Enable it and try again.'
            log(Severity.CRITICAL, script_name, msg, popup=not silent_mode)

    def dialog_source_control_connection():
        if not silent_mode:
            if filter_platform('win'):
                if addon.preference().sourcecontrol.win32_env_override:
                    if addon.preference().sourcecontrol.override_mode == 'singleuser-workspace':
                        msg = 'Could not connect to Perforce Server! Check your Internet and VPN settings. If problem ' \
                              'persists, restart P4V. \n\nIf that doesn\'t fix the issue, you may need to reconfigure ' \
                              'Perforce Environment Settings. Since you are in override mode, do those steps:\n' \
                              '1. Open the Blender Preferences (Edit -> Preferences).\n' \
                              '2. Add-ons -> Blue Hole -> Source Control\n' \
                              '3. Check the "Override P4V Environment Settings" box\n' \
                              '4. Fill out the three fields (Server, User, Workspace)\n' \
                              '5. Click the Apply Override Settings'
                    elif addon.preference().sourcecontrol.override_mode == 'multiuser-workspace':
                        msg = 'Could not connect to Perforce Server! Check your Internet and VPN settings. If problem ' \
                              'persists, restart P4V. \n\nIf that doesn\'t fix the issue, you may need to reconfigure ' \
                              'Perforce Environment Settings.\n' \
                              '1. Open the P4V Application and log in.\n' \
                              '2. Connection (Header Menu) -> Environment Settings\n' \
                              '3. Uncheck the "Use Current Connection for Environment Settings".\n' \
                              '4. Fill out the three fields (Server, User, Workspace)\n' \
                              '5. Press "OK"\n\n' \
                              'If that still doesn\'t work (and because you are in multiuser-override mode), your settings in Blue Hole environment may be in conflict.:\n' \
                              '1. Open the Blender Preferences (Edit -> Preferences).\n' \
                              '2. Add-ons -> Blue Hole -> Source Control\n' \
                              '3. Check the "Override P4V Environment Settings" box\n' \
                              '4. See if there is an entry matching your computer name with wrong information and fix it\n' \
                              '5. Try again'
                    else:
                        msg = 'ERROR: WRONG SOURCECONTROL WORKSPACE TYPE'
                else:
                    msg = 'Could not connect to Perforce Server! Check your Internet and VPN settings. If problem ' \
                          'persists, restart P4V. \n\nIf that doesn\'t fix the issue, you may need to reconfigure ' \
                          'Perforce Environment Settings.\n' \
                          '1. Open the P4V Application and log in.\n' \
                          '2. Connection (Header Menu) -> Environment Settings\n' \
                          '3. Uncheck the "Use Current Connection for Environment Settings".\n' \
                          '4. Fill out the three fields (Server, User, Workspace)\n' \
                          '5. Press "OK"\n\n' \
                          'Alternatively:\n' \
                          '1. Open the Blender Preferences (Edit -> Preferences).\n' \
                          '2. Add-ons -> Blue Hole -> Source Control\n' \
                          '3. Check the "Override P4V Environment Settings" box\n' \
                          '4. Fill out the three fields (Server, User, Workspace)\n' \
                          '5. Try again'
            else:
                msg = 'Could not connect to Perforce Server! Check your Internet and VPN settings. If problem ' \
                      'persists, restart P4V. \n\nIf that doesn\'t fix the issue, you may need to reconfigure ' \
                      'Perforce Environment Settings.\n' \
                      '1. Open the Blender Preferences (Edit -> Preferences).\n' \
                      '2. Add-ons -> Blue Hole -> Source Control\n' \
                      '3. Fill out the three fields (Server, User, Workspace)'
            log(Severity.CRITICAL, script_name, msg, popup=not silent_mode)

    def dialog_check_blend_location_in_dir_structure():
        if silent_mode is False:
            msg = 'Cannot execute script because the currently opened Blender file is not located in the sub-folder ' \
                  'specified in the current environments Directory Structure: {sub_folder}. Please relocate the ' \
                  'file and try again.'
            specified_sub_folder = addon.preference().environment.sc_dir_struct_scenes
            msg = msg.format(sub_folder=specified_sub_folder)
            log(Severity.CRITICAL, script_name, msg, popup=not silent_mode)

    def display_path_error_source_content(path):
        msg = 'The Source Content Root Path specified in the Active Environment\'s preferences could ' \
              'not be reached: "{path}". Please create said directory or edit the Active Environment\'s preferences ' \
              'to point to an existing folder.'.format(path=str(path))
        log(Severity.CRITICAL, script_name, msg, popup=not silent_mode)

    def display_path_error_unity_assets(path):
        msg = 'The Unity Project\'s Assets Path specified in the Active Environment\'s preferences could ' \
              'not be reached: "{}". Please create said directory or edit the Active Environment\'s preferences ' \
              'to point to an existing Unity Assets folder. Example: "C:\\YourUnityProject\\Assets\\"'.format(str(path))
        log(Severity.CRITICAL, script_name, msg, popup=not silent_mode)

    def display_path_error_blend(sc_path_seek, blend_path_found):
        msg = 'The opened Blender scene file is not located within the Source Content directory path specified in ' \
              'the Active Environment\'s preferences. ' \
              '\n\nExpected Blender file within: "{sc_path}"\nFound Blender file at: "{blend_path}"' \
              '\n\nThis is required because the Send to Unity\'s script mirrors the folder structure from the ' \
              'Source Content Root Path to the Unity Project\'s Assets Path. Please move your Blender file or edit ' \
              'the Source Content Root Path in the Active Environment\'s ' \
              'preferences.'.format(sc_path=sc_path_seek, blend_path=blend_path_found)
        log(Severity.CRITICAL, script_name, msg, popup=not silent_mode)

    # Check if Blend exists
    if check_blend_exist:
        if len(fileUtils.get_blend_file_path()) == 0:
            log(Severity.CRITICAL, script_name, 'Check Blend Exist Failed')
            dialog_check_blend_exist()
            return False
        log(Severity.DEBUG, script_name, 'Check Blend Exist Succeeded!')

    # Check if Blend scene in proper sub-folder
    if check_blend_loc_in_dir_structure:
        check_result = check_blend_location_in_dir_structure()
        if not check_result:
            log(Severity.CRITICAL, script_name, 'Check Blend Location in Directory Structure Failed')
            dialog_check_blend_location_in_dir_structure()
            return False
        log(Severity.DEBUG, script_name, 'Check Blend Location in Directory Structure Succeeded')

    # Check if selection is not empty
    if check_selection_not_empty:
        if len(objectUtils.get_selection()) == 0:
            log(Severity.CRITICAL, script_name, 'Check Selection not Empty Failed')
            dialog_check_selection_not_empty()
            return False
        log(Severity.DEBUG, script_name, 'Check Selection not Empty Succeeded')

    # Check if source control is enabled
    if check_source_control_enable:
        if not filter_source_control():
            log(Severity.CRITICAL, script_name, 'Check Source Control Enabled: Failed')
            dialog_source_control_enable()
            return False
        log(Severity.DEBUG, script_name, 'Check Source Control Enabled: Succeeded')

    # Check source control connection
    if check_source_control_connection:
        p4_info_cls = p4Wrapper.P4Info()
        if p4_info_cls.status is False:
            log(Severity.CRITICAL, script_name, 'Check Source Control Connection: Failed')
            dialog_source_control_connection()
            return False
        log(Severity.DEBUG, script_name, 'Check Source Control: Succeeded')

    # Attempt to get valid source content path
    bh_prefs_cls = env.BlueHolePrefs()
    if check_source_content_root_path_exist or check_blend_in_source_content:
        sc_path = bh_prefs_cls.get_valid_sc_dir_path()
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

        blend_path = str(Path(fileUtils.get_blend_directory_path()))
        if sc_path_str not in blend_path:
            display_path_error_blend(sc_path, blend_path)
            return False

    # Check that Unity Asset's Path Exists
    if check_unity_assets_path_exist:
        unity_asset_path = bh_prefs_cls.get_valid_unity_asset_dir_path()

        if not unity_asset_path:
            display_path_error_unity_assets(unity_asset_path)
            return False

    # Reached the end, so return True
    return True
