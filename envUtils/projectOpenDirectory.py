"""
Open Directory within project.
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

import BlueHole.blenderUtils.fileUtils as fileUtils
import BlueHole.envUtils.projectUtils as projectUtils
import BlueHole.blenderUtils.filterUtils as filterUtils


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

def open_project_sub_dir(path_append):
    """
    Opens desired project directory of currently opened Blender scene
    :param path_append: Specifies directory to open. Has to be an entry of
                        env_variables.ini under "DirectoryStructure" section.
    :type path_append: str
    """

    # Initial checks
    check_result = filterUtils.check_tests('Open Asset Directory',
                                           check_blend_exist=True,
                                           check_blend_loc_in_dir_structure=True)
    if not check_result:
        return False

    # Get path of desired sub project directory
    dir_to_open = projectUtils.get_project_sub_dir(path_append)

    # If valid, open the filepath.
    fileUtils.open_dir_path(dir_to_open)
