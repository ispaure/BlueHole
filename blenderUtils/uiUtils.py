"""
User Interface (UI) Functions for Blue Hole
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
# IMPORTS

import ctypes
import textwrap
import sys
from pathlib import Path

# Blender
import bpy

# Blue Hole
import BlueHole.wrappers.cmdWrapper as cmdWrapper

# ----------------------------------------------------------------------------------------------------------------------
# CODE

def show_label(label_text, layout):
    layout.label(text='[[[[ ' + label_text + ' ]]]]', icon='KEYTYPE_EXTREME_VEC')


def set_theme(name):
    """
    Set Blender to the chosen theme.
    :param name: Name of the theme file to be set (without extension)
    :type name: str
    """
    # Import here only (if import at the top it causes cyclical issues)
    from BlueHole.blenderUtils.fileUtils import get_blue_hole_themes_path as get_blue_hole_themes_path
    # Determine .xml theme preset path, which is slightly different depending if Windows or Unix
    theme_file_path = str(Path(get_blue_hole_themes_path() + '/' + name + '.xml'))
    # Set Current theme as .xml theme preset path
    bpy.ops.script.execute_preset(filepath=theme_file_path, menu_idname='USERPREF_MT_interface_theme_presets')


def empty_fn():
    print('runningemptyfn')
    pass


def show_prompt(title, message, execute_fn=empty_fn):
    """
    Displays dialog box
    :param title: Dialog box title
    :type title: str
    :param message: Message to be shown in dialog box
    :type message: str
    :param execute_fn: (Optional) Function to execute if user presses "OK" button
    :type execute_fn: function
    """
    print('Showing dialog box.')

    class MbConstants:
        MB_OKCANCEL = 1
        IDCANCEL = 2
        IDOK = 1

    # Prevent escape sequences
    message = message.replace('\\n', '\n').replace('\\t', '\t')

    # Show Dialog Window (Windows) and return user input
    def show_prompt_windows(message, title):
        return ctypes.windll.user32.MessageBoxW(0, message, title, MbConstants.MB_OKCANCEL)

    # Show Dialog Window (MacOS) and return user input
    def show_prompt_macos(message, title):
        command_str = "osascript -e 'Tell application \"System Events\" to display dialog \"{message}\" with title \"{title}\"'".format(message=message, title=title)
        return_val = cmdWrapper.exec_cmd(command_str)
        return return_val

    # Since Blender API doesn't have proper message box that waits on user, we have to get a bit creative.

    if sys.platform == 'win32':  # Solution which only works on Windows
        rc = show_prompt_windows(message, title)
        if rc == MbConstants.IDOK:
            execute_fn()
            return True
        elif rc == MbConstants.IDCANCEL:
            return False
    else:
        message = message.replace('"', '')
        message = message.replace("'", '')
        if 'OK' in show_prompt_macos(message, title)[0]:
            execute_fn()
            return True
        else:
            return False


def show_message(title, message):
    """
    Displays a simple message box with an OK button.
    Pauses script until user presses OK.
    :param title: Dialog box title
    :type title: str
    :param message: Message to be shown in dialog box
    :type message: str
    """
    import sys
    import ctypes

    # Prevent escape sequences
    message = message.replace('\\n', '\n').replace('\\t', '\t')

    if sys.platform == 'win32':
        class MbConstants:
            MB_OK = 0
        ctypes.windll.user32.MessageBoxW(0, message, title, MbConstants.MB_OK)

    else:  # macOS
        message = message.replace('"', '').replace("'", '')
        import subprocess
        cmd = f"""osascript -e 'Tell application "System Events" to display dialog "{message}" with title "{title}" buttons {{"OK"}} default button "OK"'"""
        subprocess.run(cmd, shell=True)


def write_text(layout, text, width = 30, icon = "NONE"):
    col = layout.column(align = True)
    col.scale_y = 0.85
    prefix = " "
    for paragraph in text.split("\n"):
        for line in textwrap.wrap(paragraph, width):
            col.label(text=prefix + line, icon = icon)
            if icon != "NONE": prefix = "     "
            icon = "NONE"
