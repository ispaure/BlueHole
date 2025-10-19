# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "GNU General Public License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

import os
import sys
import enum
from datetime import datetime


# Settings
log_file = False
include_time = False  # Show absolute time
use_time_delta = True  # Show time since last debug message
verbose_debug = True  # Show debug-level entries

# Global variable to track last timestamp
last_timestamp = None

# Enable ANSI escape codes on Windows CMD
if sys.platform.startswith("win"):
    os.system("")


def print_debug_msg(message, verbose_debug):
    """
    LEGACY, PLEASE REPLACE WITH LOG WHENEVER POSSIBLE
    Prints a message if verbose is True.
    :param message: Message to print
    :type message: str
    :param verbose_debug: Defines if message is printed or not.
    :type verbose_debug: bool
    """
    if verbose_debug:
        print(message)


class Severity(enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DebugLogger:
    def __init__(self, log_file="debug.log"):
        self.log_file = log_file

    def log_debug(self, severity: Severity, title: str, message: str, popup: bool = False):
        if severity == Severity.DEBUG and not verbose_debug:
            return

        global last_timestamp

        # Format the log message
        current_time = datetime.now()
        if include_time:
            timestamp = current_time.strftime("%H:%M:%S")
        elif use_time_delta:
            if last_timestamp is None:
                delta_str = '0.000s'
            else:
                delta = (current_time - last_timestamp).total_seconds()
                delta_str = f'{delta:.3f}s'
            timestamp = delta_str
        else:
            timestamp = ''

        last_timestamp = current_time

        skip_char = ' ' if timestamp else ''

        popup_title = f"{timestamp}{skip_char}[{severity.value}] {title}"

        if '\n' not in message:
            full_message_for_print = f"{timestamp}{skip_char}[{severity.value}] {title}: {message}"
        else:
            full_message = (f"{timestamp}{skip_char}[{severity.value}] {title}\n"
                            f"{message}")
            # line skips always put text a bit further on line
            num_spaces = len(timestamp) + len(f'{severity.value}') + 3 + len(skip_char)
            space_str = ' ' * num_spaces
            full_message_for_print = full_message.replace('\n', f'\n{space_str}')
            full_message_for_print += '\n'

        # Print message with colors
        if severity is Severity.DEBUG:
            colored_msg = f'\033[90m{full_message_for_print}\033[0m'
        elif severity is Severity.INFO:
            colored_msg = full_message_for_print
        elif severity is Severity.WARNING:
            colored_msg = f'\033[33m{full_message_for_print}\033[0m'
        elif severity is Severity.ERROR:
            colored_msg = f'\033[31m{full_message_for_print}\033[0m'
        elif severity is Severity.CRITICAL:
            colored_msg = f'\033[41;37m{full_message_for_print}\033[0m'
        else:
            colored_msg = full_message_for_print

        # Print to console
        print(colored_msg)

        # Append to log file (If turned ON)
        if log_file:
            with open(self.log_file, "a") as log_item:
                log_item.write(full_message_for_print + "\n")

        # If popup, show popup
        if popup:
            try:
                import BlueHole.blenderUtils.uiUtils as uiUtils
                uiUtils.show_dialog_box(title, message)
            except Exception:
                print('Could not load uiUtils!')

        # If Critical, end application
        if severity == Severity.CRITICAL:
            sys.exit(1)


# Create a singleton instance of the logger
logger_instance = DebugLogger()

# Alias for the log_debug method
log = logger_instance.log_debug
