"""
Main point of contact for source control scripts. They might get redirected to the proper source control solutions
afterwards.
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

# Blue Hole
import BlueHole.wrappers.perforceWrapper as p4Wrapper
import BlueHole.blenderUtils.filterUtils as filterUtils
import BlueHole.blenderUtils.fileUtils as fileUtils
from BlueHole.preferences.prefs import *

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def sc_open_edit_file_path_lst(file_path_lst):
    """
    Depending on enabled source control solution, will redirect to proper source control solution
    """
    # CHECK IF SOURCE CONTROL IS ENABLED
    if filterUtils.filter_source_control():
        if prefs().sc.source_control_solution == 'perforce':
            p4_file_grp_cls = p4Wrapper.P4FileGroup()
            for file_path in file_path_lst:
                p4_file_grp_cls.append_p4_file_to_group_from_client_file(str(file_path))
            result = p4_file_grp_cls.open_for_edit()
            return result
        elif prefs().sc.source_control_solution == 'plastic-scm':
            return True  # By default there is nothing to do for plastic SCM to do its job
        elif prefs().sc.source_control_solution == 'git':
            return False  # TODO: Source Control - Git integration
    else:
        return True  # Return True since ran as intended (nothing to do; skip)


def sc_check_blend(silent_mode=False):
    """
    Checks out the currently opened scene. Depending on solution, will redirect
    """
    if filterUtils.filter_source_control():
        if prefs().sc.source_control_solution == 'perforce':
            # # OLD METHOD TO FULLY REMOVE LATER ONCE NEW ONE HAS BEEN THOROUGHLY TESTED
            # p4Utils.p4_check_blend(silent_mode)

            # Just bypass if scene is not on disk (regardless of silent mode)
            result = filterUtils.check_tests('Checkout Blender Scene',
                                             check_blend_exist=True,
                                             silent_mode=True)
            if not result:
                return False

            # -------------------------------------------------------------------------------
            # NEW METHOD
            result = filterUtils.check_tests('Checkout Blender Scene',
                                             check_blend_exist=True,
                                             check_source_control_enable=True,
                                             silent_mode=silent_mode)
            if not result:
                return False

            blend_file_path = fileUtils.get_blend_file_path()

            # NEW METHOD KEEPING OLD BEHAVIOR
            blend_p4_file = p4Wrapper.BlendP4File(client_file=blend_file_path)
            blend_p4_file.open_blend_for_edit(silent_mode)

            # # NEW METHOD GENERIC
            # p4_file_grp_cls = p4Wrapper.P4FileGroup()
            # p4_file_grp_cls.append_p4_file_to_group_from_client_file(blend_file_path)
            # result = p4_file_grp_cls.open_for_edit()
            # return result
            # --------------------------------------------------------------------------------

        elif prefs().sc.source_control_solution == 'plastic-scm':
            return True  # By default there is nothing to do for plastic SCM to do its job
        elif prefs().sc.source_control_solution == 'git':
            return False  # TODO: Source Control - Git integration
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
