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

# System
from typing import *
from pathlib import Path

# Blue Hole
from ...blenderUtils import blenderFile
from ...Lib.commonUtils.debugUtils import *
from ...preferences.prefs import *
from ...Lib.commonUtils.wrappers import cmdShellWrapper
from ...Lib.commonUtils import fileUtils
from ...Lib.commonUtils.osUtils import *

# ----------------------------------------------------------------------------------------------------------------------
# USER DEFINED VARIABLES

tool_name = 'Blue Hole [Perforce Wrapper]'
show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def p4_fstat_dict(file_path_string, silent_mode=False) -> Optional[List[Dict[str, str]]]:
    """
    Get p4 fstat results, cleaned as an array of dicts (1 dict per item)
    """

    # If file_path isn't enclosed in quotation marks, enclose.
    if '"' not in file_path_string[0]:
        file_path_string = '"' + file_path_string + '"'

    # Get status of files
    result_array = exec_p4_command("p4 fstat {}".format(file_path_string))

    result_dicts_lst = []
    result_dict = {}

    # Transform status of files in easily understood dict
    for i in result_array:
        if 'Your session has expired, please login again' in i:
            if not silent_mode:
                msg = 'Your session has expired. Please login again from Perforce. Aborting!'
                log(Severity.ERROR, tool_name, msg, popup=True)
            return None
        elif ' - no such file(s).' in i:
            result_dict = {'clientFile': i.replace(' - no such file(s).', '')}
            result_dicts_lst.append(result_dict)
            result_dict = {}
        elif ' - file(s) not in client view.' in i:
            result_dict = {'clientFile': i.replace(' - file(s) not in client view.', ''), 'notInClientView': True}
            result_dicts_lst.append(result_dict)
            result_dict = {}
        else:
            i = i.replace('... ', '')
            if len(i) > 0:
                split_i = i.split(' ')
                split_i_up_to_last = ''
                split_i_length = len(split_i)
                for idx, value in enumerate(split_i):
                    if idx > 0:
                        if idx < split_i_length - 1:
                            split_i_up_to_last += value + ' '
                        else:
                            split_i_up_to_last += value
                result_dict[split_i[0]] = split_i_up_to_last
            else:
                result_dicts_lst.append(result_dict)
                result_dict = {}

    return result_dicts_lst


def set_p4_env_settings():
    """
    Set Environment Variables, if configured in User Preferences
    """
    print('Initialize set P4 environment settings')

    # If Source Control is enabled in the Preferences
    if prefs().sourcecontrol.source_control_enable and prefs().sourcecontrol.source_control_solution == 'perforce':
        print('Attempting to set P4 environment settings')
        # If platform is Windows
        match get_os():
            case OS.WIN:
                # If preference set to "Override Environment Settings"
                if prefs().sourcecontrol.win32_env_override:
                    print('Override environment settings is ON')
                    cmd_str = 'p4 set P4USER=' + prefs().sourcecontrol.macos_env_setting_p4user
                    exec_p4_command(cmd_str)
                    cmd_str = 'p4 set P4PORT=' + prefs().sourcecontrol.macos_env_setting_p4port
                    exec_p4_command(cmd_str)
                    cmd_str = 'p4 set P4CLIENT=' + prefs().sourcecontrol.macos_env_setting_p4client
                    exec_p4_command(cmd_str)
            case OS.MAC:
                # If Platform is MacOS, Set automatically as the MacOS P4V Client doesn't have Environment Settings.
                cmd_str = 'p4 set P4USER=' + prefs().sourcecontrol.macos_env_setting_p4user
                exec_p4_command(cmd_str)
                cmd_str = 'p4 set P4PORT=' + prefs().sourcecontrol.macos_env_setting_p4port
                exec_p4_command(cmd_str)
                cmd_str = 'p4 set P4CLIENT=' + prefs().sourcecontrol.macos_env_setting_p4client
                exec_p4_command(cmd_str)
            case OS.LINUX:
                # If Platform is Linux, Set automatically as the MacOS P4V Client doesn't have Environment Settings.
                cmd_str = 'p4 set P4USER=' + prefs().sourcecontrol.linux_env_setting_p4user
                exec_p4_command(cmd_str)
                cmd_str = 'p4 set P4PORT=' + prefs().sourcecontrol.linux_env_setting_p4port
                exec_p4_command(cmd_str)
                cmd_str = 'p4 set P4CLIENT=' + prefs().sourcecontrol.linux_env_setting_p4client
                exec_p4_command(cmd_str)


class P4UserWorkspace:
    def __init__(self):
        self.computername = None
        self.username = None
        self.workspace = None


def create_p4_user_workspace_cls(computer_name, username, workspace):
    p4userws_cls = P4UserWorkspace()
    p4userws_cls.computername = computer_name
    p4userws_cls.username = username
    p4userws_cls.workspace = workspace
    return p4userws_cls


def create_empty_binary_file(file_path):
    """
    Creates an empty binary file at desired filepath, if it does not exist yet.
    It's important it's binary, else Perforce may treat it as a text file and when it gets
    stomped by a .blend/.fbx file it will export in a way that backfires.
    """
    # Create directory (if it doesn't exist yet)
    Path(os.path.dirname(file_path)).mkdir(parents=True, exist_ok=True)
    # Create File
    if not os.path.isfile(file_path):
        fileUtils.copy_file(blenderFile.get_blue_hole_lib_path() / 'binary_template.bin', file_path)
        # with open(file_path, 'w') as fp:
        #     pass


def get_p4_macos_path() -> str:
    return f'{prefs().sourcecontrol.p4v_app_path_mac}/Contents/Resources/p4_parallel'  # Complete to get p4_parallel path


def get_p4_linux_path() -> str:
    return prefs().sourcecontrol.p4_parallel_path_linux


def exec_p4_command(command: str):
    """
    Execute Perforce commands. Based on cmdShellWrapper's exec_cmd,
    but with a few specific things to ensure proper functioning on macOS and Linux.
    """

    # Ensures this is used for Perforce commands, else raise exception and recommend using wrapper directly.
    if not command.startswith('p4 '):
        msg = (
            f'Perforce command execution failed.\n\n'
            f'What went wrong:\n'
            f'exec_p4_command can only execute Perforce commands that start with "p4 ". '
            f'Received: "{command}"\n\n'
            f'What to do:\n'
            f'Call cmdShellWrapper.exec_cmd for non-Perforce commands, or pass a valid Perforce command '
            f'(for example: "p4 info").'
        )
        log(Severity.CRITICAL, 'Perforce Command', msg)

    # Resolve P4 Path (macOS & Linux need to be pointed to p4_parallel file)
    p4_path: str = {OS.WIN: 'p4', OS.MAC: get_p4_macos_path(), OS.LINUX: get_p4_linux_path()}[get_os()]

    match get_os():
        case OS.MAC | OS.LINUX:
            # p4_parallel path needs to be valid
            if not os.path.isfile(p4_path):
                msg = (
                    f'Perforce command execution failed.\n\n'
                    f'What went wrong:\n'
                    f'The Perforce executable path is invalid:\n'
                    f'"{p4_path}"\n\n'
                    f'What to do:\n'
                    f'Ensure Perforce is installed and that the Perforce executable is available at the path above. '
                    f'If needed, update the Perforce path in the Blue Hole Addon Settings (Source Control tab).\n\n'
                    f'Perforce operation aborted.'
                )
                log(Severity.CRITICAL, 'Perforce Command', msg)

            # Set permissions
            file_cls = fileUtils.File(Path(p4_path))
            file_cls.set_executable_permission()

            # Replace p4 in command with the path (in quotes)
            command = f'"{p4_path}"{command[2:]}'

    # Execute the command
    return cmdShellWrapper.exec_cmd(command, time_out=15)
