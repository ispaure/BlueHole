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
import time
from ..Lib.send2ue.dependencies import remote_execution
from ..Lib.commonUtils.debugUtils import *

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


def run_unreal_python_commands(remote_exec, commands, failed_connection_attempts=0, silent: bool = False):
    """
    Find the open Unreal Editor with remote connection enabled and send it Python commands.

    :param remote_exec: A RemoteExecution instance
    :param commands: A formatted string of Python commands to run in the engine
    :param failed_connection_attempts: Counter tracking how many connection attempts were made
    """
    time.sleep(0.1)

    try:
        for node in remote_exec.remote_nodes:
            remote_exec.open_command_connection(node.get("node_id"))

        if remote_exec.has_command_connection():
            global unreal_response
            unreal_response = remote_exec.run_command(commands, unattended=False)
        else:
            if failed_connection_attempts < 10:
                run_unreal_python_commands(remote_exec, commands, failed_connection_attempts + 1)
            else:
                remote_exec.stop()
                display_cannot_connect_unreal_error(silent=silent)
                return False
    finally:
        remote_exec.stop()

    return True


def test_unreal_connection(silent: bool = True) -> bool:
    """
    Minimal Unreal remote execution connectivity test.
    """
    remote_exec = remote_execution.RemoteExecution()
    remote_exec.start()

    run_unreal_python_commands(
        remote_exec,
        'print("UNREAL_REMOTE_OK")',
        silent=silent
    )

    if unreal_response:
        return True
    else:
        return False


def debug_remote_nodes():
    remote_exec = remote_execution.RemoteExecution()
    remote_exec.start()

    import time
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
