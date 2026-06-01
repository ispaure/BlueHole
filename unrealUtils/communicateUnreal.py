"""
Trigger commands to Unreal.
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

import time

from ..Lib.send2ue.dependencies import remote_execution
from ..Lib.commonUtils.debugUtils import *
from ..preferences.prefs import prefs
from .overrides.ue_exec_code_override import run_unreal_python_commands_override

# ----------------------------------------------------------------------------------------------------------------------
# CODE

unreal_response = ''
communicate_ue_name = 'Blue Hole Communicate to Unreal'


def display_cannot_connect_unreal_error(silent: bool = False):
    msg = (
        f'{communicate_ue_name} connection failed.\n\n'
        f'What went wrong:\n'
        f'Blender could not establish communication with Unreal Editor.\n\n'
        f'What to do:\n'
        f'Ensure Unreal Editor is open with a project loaded, and verify that the Blue Hole Unreal Bridge '
        f'is properly installed and configured. See Blue Hole website for details.\n\n'
        f'Unreal operation aborted.'
    )
    log(Severity.ERROR, communicate_ue_name, msg, popup=not silent)


def run_unreal_python_commands(commands: str, silent: bool = False) -> bool:
    """
    Send Python commands to Unreal.
    Uses a custom override operator when enabled, otherwise uses Blue Hole's default Unreal remote execution.
    """
    if prefs().bridge.ue_enable_exec_code_override and prefs().bridge.ue_op_exec_code_override:
        msg = f'Using Unreal Execute Code Override: "{prefs().bridge.ue_op_exec_code_override}"'
        log(Severity.WARNING, communicate_ue_name, msg)
        return run_unreal_python_commands_override(commands)
    else:
        msg = 'Using Blue Hole default Unreal remote execution.'
        log(Severity.INFO, communicate_ue_name, msg)
        return run_unreal_python_commands_default(commands, silent=silent)


def run_unreal_python_commands_default(commands: str, failed_connect_attempts: int = 0, silent: bool = False) -> bool:
    """
    Find the open Unreal Editor with remote connection enabled and send it Python commands.

    :param commands: A formatted string of Python commands to run in the engine
    :param failed_connect_attempts: Counter tracking how many connection attempts were made
    :param silent: If True, suppress popup errors
    """
    global unreal_response
    unreal_response = ''

    remote_exec = remote_execution.RemoteExecution()

    try:
        remote_exec.start()

        return _execute_remote_commands(
            remote_exec,
            commands,
            failed_connect_attempts=failed_connect_attempts,
            silent=silent,
        )

    except Exception as e:
        msg = f'Failed to run Unreal remote execution command: {e}'
        log(Severity.CRITICAL, communicate_ue_name, msg)
        display_cannot_connect_unreal_error(silent=silent)
        return False

    finally:
        try:
            remote_exec.stop()
        except Exception as e:
            msg = f'Failed to stop Unreal remote execution cleanly: {e}'
            log(Severity.WARNING, communicate_ue_name, msg)


def _execute_remote_commands(remote_exec, commands: str, failed_connect_attempts: int = 0, silent: bool = False) -> bool:
    """
    Execute Python commands through Unreal remote execution.

    :param remote_exec: A RemoteExecution instance
    :param commands: A formatted string of Python commands to run in the engine
    :param failed_connect_attempts: Counter tracking how many connection attempts were made
    :param silent: If True, suppress popup errors
    """

    time.sleep(0.1)

    for node in remote_exec.remote_nodes:
        remote_exec.open_command_connection(node.get("node_id"))

    if remote_exec.has_command_connection():
        global unreal_response
        unreal_response = remote_exec.run_command(commands, unattended=False)
        return True

    if failed_connect_attempts < 10:
        return _execute_remote_commands(
            remote_exec,
            commands,
            failed_connect_attempts=failed_connect_attempts + 1,
            silent=silent,
        )

    display_cannot_connect_unreal_error(silent=silent)
    return False


def test_unreal_connection(silent) -> bool:
    """
    Minimal Unreal remote execution connectivity test.
    """
    return run_unreal_python_commands('print("UNREAL_REMOTE_OK")', silent=silent)


def debug_remote_nodes():
    """
    Tries to discover unreal instances that can be connected to and displays to the user in a popup window.
    """
    remote_exec = remote_execution.RemoteExecution()
    remote_exec.start()

    time.sleep(2.0)

    remote_nodes = remote_exec.remote_nodes

    if not remote_nodes:
        log(
            Severity.WARNING,
            'Debug Remote Nodes',
            'No Unreal Remote Execution nodes were discovered.',
            popup=True
        )
        remote_exec.stop()
        return

    for i, node in enumerate(remote_nodes):
        msg = (
            f'=== Unreal Remote Node #{i + 1} ===\n'
            f'Node ID: {node.get("node_id", "Unknown")}\n'
            f'Project Name: {node.get("project_name", "Unknown")}\n'
            f'Project Path: {node.get("project_path", "Unknown")}\n'
            f'Engine Version: {node.get("engine_version", "Unknown")}\n'
            f'Command IP: {node.get("command_ip", "Unknown")}\n'
            f'Command Port: {node.get("command_port", "Unknown")}'
        )

        log(
            Severity.INFO,
            'Debug Remote Nodes',
            msg,
            popup=True
        )

    remote_exec.stop()
