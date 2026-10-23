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
from shutil import copyfile
from pathlib import Path
from tempfile import TemporaryDirectory
from ...blenderUtils import blenderFile
from ...Lib.commonUtils.runtime.diagnostics import log, Severity
from ...Lib.commonUtils.filesystem import files as fileUtils
from ...Lib.commonUtils import ui
from ...Lib.commonUtils.persistence import promote_path


# ----------------------------------------------------------------------------------------------------------------------
# CODE


TOOL_NAME = 'Applying Blue Hole Deluxe Preferences'


def _copy_and_verify(source: Path, destination: Path):
    """Verify private staging before publication, retaining previous settings."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix='.bluehole-preferences-', dir=destination.parent) as temporary:
        staged = Path(temporary) / destination.name
        log(Severity.INFO, TOOL_NAME, f'Staging "{source}" for "{destination}"')
        copyfile(source, staged)
        if staged.read_bytes() != source.read_bytes():
            raise OSError(f'Content verification failed for "{destination}"; '
                          'the staged file does not match the Deluxe payload.')

        if destination.exists():
            before_mode = destination.stat().st_mode
            fileUtils.File(destination).make_writable()
            log(Severity.INFO, TOOL_NAME,
                f'Made destination writable: "{destination}" '
                f'(mode {oct(before_mode)} -> {oct(destination.stat().st_mode)})')
        backup = promote_path(staged, destination)
        if backup is not None:
            log(Severity.INFO, TOOL_NAME, f'Recovery copy retained at "{backup}"')

    log(Severity.INFO, TOOL_NAME,
        f'Verified "{destination}" ({destination.stat().st_size} bytes)')


def apply_deluxe_prefs() -> bool:
    """ Applies the Deluxe Blue Hole Preferences, by overwriting the userpref.blend and keymaps file. """

    # Leave an out for the user.
    if not warning_bh_deluxe():
        log(Severity.INFO, TOOL_NAME, 'Cancelled by the user; no files copied.')
        return False

    verified = []
    stage = 'Resolving installation paths'
    try:
        copies = (
            (get_payload_dir() / 'userpref.blend', Path(blenderFile.get_userpref_path())),
            (get_payload_dir() / 'keyconfig' / 'BH_Keymaps.py',
             Path(blenderFile.get_keyconfig_path(), 'BH_Keymaps.py')),
        )
        # Check both payloads before overwriting either destination.
        for source, destination in copies:
            stage = f'Checking payload "{source}"'
            log(Severity.INFO, TOOL_NAME, f'Source: "{source}"\nDestination: "{destination}"')
            if not source.is_file() or source.stat().st_size == 0:
                raise OSError(f'Deluxe payload is missing or empty: "{source}"')

        for source, destination in copies:
            stage = f'Installing "{source}" to "{destination}"'
            _copy_and_verify(source, destination)
            verified.append(str(destination))

    except Exception as error:
        completed = '\n'.join(verified) if verified else 'None'
        msg = (f'Applying Deluxe preferences did not complete.\n\n'
               f'Step: {stage}\n'
               f'Error: {type(error).__name__}: {error}\n\n'
               f'Files copied and verified:\n{completed}\n\n'
               'Blender will remain open. Some files may already have been changed. '
               'Check the paths and folder permissions above. If a file is locked by another '
               'application, close that application and try again.')
        log(Severity.ERROR, TOOL_NAME, msg, popup=True)
        return False

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
    return ui.display_msg_box_ok_cancel('WARNING: APPLY BLUE HOLE DELUXE PREFERENCES', msg)


def notice_blender_closure():
    msg = ('Blue Hole DELUXE preferences have been installed successfully. \n\n'
           'Blender will now close to complete the installation. \n\n'
           'Please restart Blender to experience the DELUXE configuration.')
    log(Severity.INFO, 'BLUE HOLE DELUXE', msg, popup=True)
