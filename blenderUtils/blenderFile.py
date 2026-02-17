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

from distutils.dir_util import copy_tree
import bpy
from shutil import rmtree
from ..Lib.commonUtils.debugUtils import *
from ..environment import envManager
from typing import *
from ..Lib.commonUtils.osUtils import *
from pathlib import Path


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

def get_blend_file_path():
    """
    Get the file path of the currently opened file.
    :return: Path of the currently opened scene.
    :rtype: str
    """
    return bpy.data.filepath


def open_blend_file(file_path):
    """
    Opens the Blender file at given path
    """
    bpy.ops.wm.open_mainfile(filepath=file_path)


def save_blend_file_at_path(file_path):
    """
    Saves the currently opened scene at given path
    """
    bpy.ops.wm.save_as_mainfile(filepath=file_path)


def create_blend_file():
    """
    Creates a new blend file
    """
    bpy.ops.scene.new(type='EMPTY')


def create_blend_file_at_path(file_path):
    """
    Creates a new blend file and saves it at path
    """
    create_blend_file()
    save_blend_file_at_path(file_path)


def get_blend_file_name():
    """
    Returns the currently opened blend file name (excl. extension)
    :rtype: str
    """
    path_path = Path(get_blend_file_path())
    return path_path.stem


def get_blend_directory_path():
    """
    Get the directory path of the currently opened file.
    :return: Path of the currently opened scene.
    :rtype: str
    """
    file_path = bpy.data.filepath
    directory_path = os.path.dirname(file_path)
    return directory_path


def get_resource_path_user():
    """
    Get the current resource path, which is %AppData%/Blender Foundation/Blender/<version#>
    :return: Resource Path
    :rtype: str
    """
    return bpy.utils.resource_path('USER')


def get_resource_path_local():
    """
    Get the current resource path, which is <BlenderSoftwareFolder>/<version#>
    """
    return bpy.utils.resource_path('LOCAL')


def truncate_n_append_str(original_str, truncate_str, append_str) -> str:
    """
    Truncates a string by the length of another string and appends another string at the end
    :param original_str: String to truncate
    :type original_str: str
    :param truncate_str: Use this string's length to truncate
    :type truncate_str: str
    :param append_str: String to append at the end
    :type append_str: str
    :rtype: str
    """
    print('TRUNCATE AND APPEND')
    print('originalstr: ' + original_str)
    print('truncatestr: ' + truncate_str)
    print('appendstr: ' + append_str)
    if len(truncate_str) != 0:
        return_str = original_str[:-len(truncate_str)]
    else:
        return_str = original_str
    result = str(Path(return_str, append_str))
    print('result: ' + result)
    return result


def get_addons_path():
    """
    Get directory path where all add-ons are located.
    :rtype: str
    """
    addons_path = Path(get_resource_path_user(), 'scripts', 'addons')
    return str(addons_path)


def get_extensions_path():
    return Path(get_resource_path_user(), 'extensions')


def get_blue_hole_user_addon_path() -> Optional[str]:
    """
    Get the root directory of the BlueHole addon installation.
    Works regardless of symlinks, zip installs, or extension installs.
    """

    module_name = __package__.split('.')[0]  # "BlueHole"

    module = sys.modules.get(module_name)

    if module and hasattr(module, "__file__"):
        path_str = str(Path(module.__file__).resolve().parent)
        log(Severity.DEBUG, 'fileUtils.get_blue_hole_user_addon_path', f'Addon path: "{path_str}"')
        return path_str

    return None

def get_url_cfg_path() -> Path:
    """
    Returns the url database file path, which contains URLs for Blue Hole website, doc and tutorials.
    """
    return Path(get_blue_hole_user_addon_path(), 'url_database.ini')


def get_blue_hole_themes_path() -> str:
    """
    Get directory path of Blue Hole Themes
    :rtype: str
    """
    themes_path = Path(get_blue_hole_user_addon_path(), 'UI', 'themes')
    return str(themes_path)


def get_blue_hole_localization_file_path() -> str:
    localization_file_path = Path(get_blue_hole_user_addon_path(), 'Localization', 'localization.csv')
    return str(localization_file_path)


def get_blue_hole_user_env_files_path() -> Path:
    """
    Get the environments path in Blue Hole (AppData)
    :rtype: str
    """
    return Path(get_blue_hole_user_addon_path(), 'envFiles')


def get_blue_hole_local_env_files_path() -> str:
    """
    Get the environments path in Blue Hole (Blender install dir)
    :rtype: str
    """
    env_path = Path(get_resource_path_local(), 'BlueHoleLocalEnv')
    return str(env_path)


def get_current_env_var_path():
    """
    Get the config file path for the current environment.
    :rtype: str
    """
    return envManager.get_env_from_prefs_active_env().env_variables_path


def get_default_env_path():
    """
    Get the default environment path.
    :rtype: str
    """
    return envManager.get_default_env().path


def get_default_env_var_path():
    """
    Get the config file path for the default environment
    """
    return envManager.get_default_env().env_variables_path


def get_default_env_msh_guides_path():
    return Path(envManager.get_default_env().path, 'msh_scale_guides')


def write_file(file_path, write_str):
    """
    Creates a file (if not created yet) and writes to it
    :param file_path: Path to write to
    :type file_path: str
    :param write_str: String to write
    :type write_str: str
    """
    # Get folder in which the file is
    file_dir = Path(file_path).parent

    # Create directory to store file in, if not created yet
    Path(file_dir).mkdir(parents=True, exist_ok=True)

    # Write to the file
    f = open(file_path, 'w+')
    f.write(write_str)
    f.close()


def is_path_valid(path):
    """Determines if path given is valid"""
    if os.path.isdir(path):
        return True
    else:
        return False


def is_file_path_valid(path):
    """Determines if file path given is valid"""
    if os.path.isfile(path):
        return True
    else:
        return False


def copy_dir(source_dir: Union[str, Path], destination_dir: Union[str, Path]):
    """
    Copies a directory (incl. its underlying hierarchy from source to destination
    :param source_dir: Source Directory
    :type source_dir: str
    :param destination_dir: Destination Directory
    :type destination_dir: str
    """

    # Ensure type is str before doing copytree, else it'll fail
    if isinstance(source_dir, Path):
        source_dir = str(source_dir)
    if isinstance(destination_dir, Path):
        destination_dir = str(destination_dir)

    copy_tree(source_dir, destination_dir)


def string_to_bool(string):
    """
    Expects a string, either "true" or "false" and returns a boolean matching else None
    """
    if string == 'true':
        return True
    elif string == 'false':
        return False
    else:
        return None


def bool_to_string(bool_value):
    """
    Expects a bool, and returns a string matching (either "true" or "false")
    """
    if bool_value:
        return 'true'
    else:
        return 'false'


def delete_dir(dir_path: Union[str, Path], debug_mode=False):
    """
    Delete a directory. Be careful when using this function! Test before with a print to see what will be deleted!
    :param dir_path: Directory to delete
    :type dir_path: str
    :param debug_mode: When set to true, doesn't delete but prints to the console what would have been deleted.
    :type debug_mode: bool
    :return:
    """
    if debug_mode:
        log(Severity.DEBUG, 'fileUtils.py', f'Would have deleted: "{dir_path}"')
    else:
        rmtree(str(dir_path))


def terminate_blender():
    """
    Shuts down Blender application
    """
    sys.exit(1)


def get_computer_name():
    """Gets the computer name (only works on Windows)"""
    return os.environ['COMPUTERNAME']
