"""
Blue Hole scripts to execute commands from CMD shell (Windows) or the terminal (MacOS & Linux)
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "GNU General Public License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

import subprocess
import time
from pathlib import Path

import BlueHole.blenderUtils.filterUtils as filterUtils
import BlueHole.blenderUtils.fileUtils as fileUtils
from BlueHole.blenderUtils.debugUtils import print_debug_msg as print_debug_msg


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

def get_p4_macos_path():
    return str(Path(fileUtils.get_blue_hole_user_addon_path() + '/Lib/p4'))


def exec_cmd(command):
    """
    Execute command from CMD shell (Windows) or the terminal (MacOS & Linux)
    :param command: Command to execute
    :type command: str
    :return: List of lines are returned
    :rtype: lst of str
    """

    def terminate_p_open(p_open_to_close):
        """
        Close Popen subprocess
        :param p_open_to_close: Popen to close
        :type p_open_to_close: subprocess.Popen
        """
        p_open_to_close.stderr.close()
        p_open_to_close.stdout.close()
        if p_open_to_close.stdin is not None:
            p_open_to_close.stdin.close()

    def clean_output_line(line_str):
        """
        Clean output lines so they only keep relevant information.
        """
        decoded_line = line_str.decode()
        cleaned_line = decoded_line.rstrip('\n')  # Remove n from end of line
        cleaned_line = cleaned_line.rstrip('\r')  # Remove r from end of line
        print_debug_msg(cleaned_line, show_verbose)  # Print line (if debug)
        return cleaned_line

    # Time out value (in milliseconds)
    time_out = 15

    # If using MacOS, P4 is not recognized (even if part of path) unless Blender is opened with the terminal window
    # shown. Because of that, let's substitute "p4" with the path where "p4" resides in Blue Hole.
    if 'p4' == command[0:2] and filterUtils.filter_platform('mac'):
        new_p4_path = get_p4_macos_path()
        command = '"' + new_p4_path + '"' + command[2:]

        # Set permissions for executable in case it will be needed later
        exec_cmd('chmod +x ' + new_p4_path)

    # If debug, print command that was sent
    print_debug_msg('Initiating Execute Shell Command procedure.', show_verbose)
    print_debug_msg('Command to send:', show_verbose)
    print_debug_msg(command, show_verbose)

    # Open subprocess, until all output is received.
    p_open = subprocess.Popen(command,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             stdin=None)

    # Run loop for as long as receive new lines
    output_lines = []
    loop_begin_time = time.time()
    stdout_lst = []
    stderr_lst = []

    while True:
        # Status, whether it's finished shelling out results or not.
        status = p_open.poll()
        p_open.stdout.flush()

        # Standard output
        stdout = p_open.stdout.readlines()
        # Standard error
        stderr = p_open.stderr.readlines()

        if len(stdout) > 0:
            stdout_lst += stdout
        if len(stderr) > 0:
            stderr_lst += stderr

        # There is new output. Reset counter to current time.
        if stderr or stdout:
            loop_begin_time = time.time()

        # If finished
        if status is not None:  # When status is not None, has finished sending results.
            output_lines = stdout_lst + stderr_lst
            terminate_p_open(p_open)  # Terminate open process
            break

        # If took too long, break off from the while loop
        now = time.time()
        if now - loop_begin_time > time_out:
            terminate_p_open(p_open)
            break

    # If debug, print result
    print_debug_msg('Output lines:', show_verbose)

    # Clean the output lines
    output_lines_cleaned = []
    for line in output_lines:
        output_lines_cleaned.append(clean_output_line(line))  # Append clean line to result

    # Return result
    return output_lines_cleaned
