"""
File utilities for Blue Hole
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

from distutils.dir_util import copy_tree
from pathlib import Path
from typing import *

import bpy

from ..Lib.commonUtils.debugUtils import *
from ..Lib.commonUtils.osUtils import *
from ..environment import envManager

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def get_blend_file_path() -> str:
    """
    Get the file path of the currently opened file.
    """
    return bpy.data.filepath


def has_blend_filepath() -> bool:
    """
    Determine whether the current .blend file has a saved file path.
    """
    return get_blend_file_path() != ""


def get_blend_file_name() -> str:
    """
    Return the currently opened blend file name (excluding extension).
    """
    return Path(get_blend_file_path()).stem


def get_blend_directory_path() -> str:
    """
    Get the directory path of the currently opened file.
    """
    return os.path.dirname(bpy.data.filepath)


def get_resource_path_user() -> str:
    """
    Get the current resource path, which is %AppData%/Blender Foundation/Blender/<version#>
    """
    return bpy.utils.resource_path('USER')


def truncate_n_append_str(original_str: str, truncate_str: str, append_str: str) -> str:
    """
    Truncate a string by the length of another string and append a new string at the end.

    :param original_str: String to truncate
    :param truncate_str: Use this string's length to truncate
    :param append_str: String to append at the end
    """
    return_str = original_str[:-len(truncate_str)] if truncate_str else original_str
    return str(Path(return_str, append_str))


def get_presets_path() -> Path:
    """
    Get the Blender presets directory.
    """
    return Path(get_resource_path_user(), 'scripts', 'presets')


def get_keyconfig_path() -> Path:
    """
    Get the Blender keyconfig presets directory.
    """
    return get_presets_path() / 'keyconfig'


def get_userpref_path() -> Path:
    """
    Get the path of the user's userpref.blend file.
    """
    return Path(get_resource_path_user(), 'config', 'userpref.blend')


def get_blue_hole_user_addon_path() -> Path:
    """
    Get the root directory of the Blue Hole add-on installation.
    Works regardless of symlinks, zip installs, or extension installs.
    """
    module_name = __package__.split('.')[0]
    module = sys.modules.get(module_name)

    if module and hasattr(module, "__file__"):
        return Path(module.__file__).resolve().parent

    log(Severity.CRITICAL, 'get_blue_hole_user_addon_path', 'Could not find this current addon\'s path!')


def get_url_cfg_path() -> Path:
    """
    Return the URL database file path, which contains URLs for the Blue Hole website, documentation, and tutorials.
    """
    return get_blue_hole_user_addon_path() / 'url_database.ini'


def get_blue_hole_themes_path() -> str:
    """
    Get the directory path of Blue Hole themes.
    """
    return str(get_blue_hole_user_addon_path() / 'ui' / 'themes')


def get_blue_hole_user_env_files_path() -> Path:
    """
    Get the environments path in Blue Hole.
    """
    return get_blue_hole_user_addon_path() / 'envFiles'


def get_blue_hole_lib_path() -> Path:
    """
    Get the Blue Hole Lib directory path.
    """
    return get_blue_hole_user_addon_path() / 'Lib'


def get_current_env_var_path():
    """
    Get the config file path for the current environment.
    """
    return envManager.get_env_from_prefs_active_env().env_variables_path


def get_default_env_var_path():
    """
    Get the config file path for the default environment.
    """
    return envManager.get_default_env().env_variables_path


def get_default_env_msh_guides_path() -> Path:
    """
    Get the msh_scale_guides directory path for the default environment.
    """
    return Path(envManager.get_env_from_prefs_active_env().path, 'msh_scale_guides')


def copy_dir(source_dir: Union[str, Path], destination_dir: Union[str, Path]) -> None:
    """
    Copy a directory, including its underlying hierarchy, from source to destination.

    :param source_dir: Source directory
    :param destination_dir: Destination directory
    """
    copy_tree(str(source_dir), str(destination_dir))


def string_to_bool(string) -> Optional[bool]:
    """
    Expect a string, either "true" or "false", and return the matching boolean. Otherwise return None.
    """
    if string == 'true':
        return True
    if string == 'false':
        return False
    return None


def bool_to_string(bool_value) -> str:
    """
    Expect a bool and return the matching string, either "true" or "false".
    """
    return 'true' if bool_value else 'false'


def terminate_blender() -> None:
    """
    Shut down the Blender application.
    """
    sys.exit(1)
