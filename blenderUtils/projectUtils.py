"""
Open directories within the project.
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

from . import blenderFile, filterUtils
from ..Lib.commonUtils import fileUtils
from ..preferences.prefs import *

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def get_project_sub_dir(path_append) -> Path:
    """
    Get a project subdirectory based on the currently opened Blender scene.

    :param path_append: Directory to get. Must be an entry from the "DirectoryStructure"
        section of env_variables.ini.
    """
    blend_directory_path = blenderFile.get_blend_directory_path()

    # Remove the configured Scenes subdirectory from the current blend path,
    # then append the requested project subdirectory.
    path_remove = prefs().directory.sc_dir_struct_scenes
    project_sub_dir: str = blenderFile.truncate_n_append_str(blend_directory_path, path_remove, path_append)

    # Create the folder if it does not already exist.
    project_sub_dir_path = Path(project_sub_dir)
    project_sub_dir_path.mkdir(parents=True, exist_ok=True)

    return project_sub_dir_path


def open_project_sub_dir(path_append):
    """
    Open a project subdirectory for the currently opened Blender scene.

    :param path_append: Directory to open. Must be an entry from the "DirectoryStructure"
        section of env_variables.ini.
    """
    if not filterUtils.check_tests(
        'Open Asset Directory',
        check_blend_exist=True,
        check_blend_loc_in_dir_structure=True,
    ):
        return False

    dir_to_open = get_project_sub_dir(path_append)
    fileUtils.open_dir_path(dir_to_open)
