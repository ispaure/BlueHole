"""
Main point of contact for source control scripts. Calls are redirected to the proper source control solution as needed.
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

from ..preferences.prefs import *
from ..Lib.commonUtils.debugUtils import *
from ..wrappers.perforce.p4_file import BlendP4File
from ..wrappers.perforce.p4_info import P4Info

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def source_control_disabled_dialog():
    """
    Dialog box warns the user source control is currently disabled in Blue Hole preferences.
    """
    message = 'Disregarding Source Control stuff: Source Control is disabled in the Blue Hole addon settings.'
    log(Severity.DEBUG, 'Blue Hole', message)


def sc_check_blend(blend_file_path: str, allow_sync, silent_mode=False):
    """
    Check the currently opened scene against the active source control solution.
    """
    if not prefs().sourcecontrol.source_control_enable:
        if not silent_mode:
            source_control_disabled_dialog()
        return True

    if prefs().sourcecontrol.source_control_solution == 'perforce':
        # New method keeping old behavior.
        blend_p4_file = BlendP4File(client_file=blend_file_path)
        blend_p4_file.open_blend_for_edit(allow_sync, silent_mode)
    elif prefs().sourcecontrol.source_control_solution == 'plastic-scm':
        return True  # By default, there is nothing to do for Plastic SCM to do its job
    elif prefs().sourcecontrol.source_control_solution == 'git':
        return True  # By default, there is nothing to do for Git to do its job


def sc_dialog_box_info():
    """
    Display source control info for the active source control solution.
    """
    if not prefs().sourcecontrol.source_control_enable:
        source_control_disabled_dialog()
        return

    if prefs().sourcecontrol.source_control_solution == 'perforce':
        P4Info().dialog_box_p4_info()
    elif prefs().sourcecontrol.source_control_solution == 'plastic-scm':
        return False  # TODO: Plastic SCM should show server info!
    elif prefs().sourcecontrol.source_control_solution == 'git':
        return False  # TODO: Source Control - Git integration
