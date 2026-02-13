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
# IMPORTS

# System
from pathlib import Path

# Blue Hole
from . import fileUtils, configUtils, filterUtils
from ..preferences.prefs import *


# ----------------------------------------------------------------------------------------------------------------------
# CODE


def get_project_sub_dir(path_append) -> Path:
    """
    Gets desired project directory (based on project from the opened Blender scene)
    :param path_append: Specifies directory to get. Has to be an entry of
                        env_variables.ini under "DirectoryStructure" section.
    :type path_append: str
    """
    # Find currently opened .blend directory path
    blend_directory_path = fileUtils.get_blend_directory_path()

    # Remove 'path_scenes' from directory, since path_scenes contains
    # the location of the subdirectory in which the .blend file resides
    path_remove = prefs().env.sc_dir_struct_scenes
    # This gets us to the root of the project directory

    # Append the path we desire to browse into, which was the argument fed to this function.
    path_append = configUtils.get_current_env_cfg_value("AssetDirectoryStructure", path_append)

    # Apply the two modifications (truncate & append) we just wrote about to the original .blend file path
    project_sub_dir: str = fileUtils.truncate_n_append_str(blend_directory_path, path_remove, path_append)

    # If folder path hadn't been created already, make it.
    # Useful in preventing bugs where user haven't created their folders yet.
    project_sub_dir_path: Path = Path(project_sub_dir)
    project_sub_dir_path.mkdir(parents=True, exist_ok=True)

    return project_sub_dir_path


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
    dir_to_open = get_project_sub_dir(path_append)

    # If valid, open the filepath.
    fileUtils.open_dir_path(dir_to_open)
