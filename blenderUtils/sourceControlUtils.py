"""
Main point of contact for source control scripts. They might get redirected to the proper source control solutions
afterwards.
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

# Blue Hole
from ..wrappers import perforceWrapper as p4Wrapper
from . import filterUtils
from ..preferences.prefs import *

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def sc_check_blend(blend_file_path: str, allow_sync, silent_mode=False):
    """
    Checks out the currently opened scene. Depending on solution, will redirect
    """
    if filterUtils.filter_source_control():
        if prefs().sc.source_control_solution == 'perforce':

            # Tests normally done later, don't know if I really need this here?! Already bypassing non-existing scenes by default.
            # # Just bypass if scene is not on disk (regardless of silent mode)
            # result = filterUtils.check_tests('Checkout Blender Scene',
            #                                  check_blend_exist=True,
            #                                  silent_mode=True)
            # if not result:
            #     return False
            #
            # # -------------------------------------------------------------------------------
            # # NEW METHOD
            # result = filterUtils.check_tests('Checkout Blender Scene',
            #                                  check_blend_exist=True,
            #                                  check_source_control_enable=True,
            #                                  silent_mode=silent_mode)
            # if not result:
            #     return False

            # NEW METHOD KEEPING OLD BEHAVIOR
            blend_p4_file = p4Wrapper.BlendP4File(client_file=blend_file_path)
            blend_p4_file.open_blend_for_edit(allow_sync, silent_mode)

        elif prefs().sc.source_control_solution == 'plastic-scm':
            return True  # By default, there is nothing to do for plastic SCM to do its job
        elif prefs().sc.source_control_solution == 'git':
            return True  # By default, there is nothing to do for GIT to do its job
    else:
        if not silent_mode:
            p4Wrapper.source_control_disabled_dialog()
        return True


def sc_dialog_box_info():
    if filterUtils.filter_source_control():
        if prefs().sc.source_control_solution == 'perforce':
            p4Wrapper.dialog_box_p4_info()
        elif prefs().sc.source_control_solution == 'plastic-scm':
            return False  # TODO: Plastic SCM should show server info!
        elif prefs().sc.source_control_solution == 'git':
            return False  # TODO: Source Control - Git integration
    else:
        p4Wrapper.source_control_disabled_dialog()
