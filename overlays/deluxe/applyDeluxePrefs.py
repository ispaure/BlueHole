"""
Apply Blue Hole Deluxe Preferences
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


import sys
from typing import *
from pathlib import Path
from ...blenderUtils import blenderFile
from ...Lib.commonUtils.debugUtils import *
from ...Lib.commonUtils.uiUtils import *
from ...Lib.commonUtils import fileUtils


# ----------------------------------------------------------------------------------------------------------------------
# CODE


def apply_deluxe_prefs():
    """ Applies the Deluxe Blue Hole Preferences, by overwriting the userpref.blend and keymaps file. """

    # Leave an out for the user.
    if not warning_bh_deluxe():
        return False

    # Debugging Info listing paths
    userpref_source: Path = get_payload_dir() / 'userpref.blend'
    userpref_dest: Path = blenderFile.get_userpref_path()
    key_cfg_source: Path = get_payload_dir() / 'keyconfig' / 'BH_Keymaps.py'
    key_cfg_dest: Path = Path(blenderFile.get_keyconfig_path(), 'BH_Keymaps.py')
    msg = (f'UserPref Source: "{userpref_source}"\n'
           f'UserPref Destination: "{userpref_dest}"\n'
           f'Keymap Source: "{key_cfg_source}"\n'
           f'Keymap Destination: "{key_cfg_dest}"\n')
    log(Severity.INFO, 'Applying Blue Hole Deluxe Preferences', msg)

    # Overwrite the files
    fileUtils.copy_file(userpref_source, userpref_dest)
    fileUtils.copy_file(key_cfg_source, key_cfg_dest)

    # Say that operation was done and Blender will terminate
    notice_blender_closure()
    sys.exit()


def get_payload_dir():
    return Path(__file__).parent / 'payload'


def warning_bh_deluxe() -> bool:
    msg = ('You are about to apply the Blue Hole DELUXE preferences.\n\n'
           'IMPORTANT: This action will OVERWRITE YOUR CURRENT BLENDER SETTINGS ("userpref.blend" file). '
           'If you wish to preserve your existing preferences, please create a backup before continuing.\n\n'
           'After installation, you will be prompted to close Blender. Ensure all work is saved now before proceeding.'
           '\n\n'
           'Do you want to continue?')
    return display_msg_box_ok_cancel('WARNING: APPLY BLUE HOLE DELUXE PREFERENCES', msg)


def notice_blender_closure():
    msg = ('Blue Hole DELUXE preferences have been installed successfully. \n\n'
           'Blender will now close to complete the installation. \n\n'
           'Please restart Blender to experience the DELUXE configuration.')
    log(Severity.INFO, 'BLUE HOLE DELUXE', msg, popup=True)
