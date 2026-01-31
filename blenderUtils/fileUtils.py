"""
File utilities for Blue Hole
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

import subprocess
import webbrowser
from pathlib import Path
import zipfile
from shutil import copyfile
from distutils.dir_util import copy_tree
import bpy
from shutil import rmtree
from BlueHole.blenderUtils.debugUtils import *
import BlueHole.blenderUtils.filterUtils as filterUtils
import BlueHole.environment.envManager as envManager
from typing import *
from BlueHole.blenderUtils.platformUtils import *
import stat


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


def open_dir_path(dir_path: Union[str, Path]):
    """
    Opens the directory path that is given as a string
    :param dir_path: Directory to open
    :type dir_path: str
    """
    str_dir_path = str(dir_path)
    if os.path.isdir(str_dir_path):  # Validate string is in fact a path
        if sys.platform == "win32":
            os.startfile(str_dir_path)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, str_dir_path])
    else:
        print('ERROR: UNABLE TO OPEN PROJECT DIRECTORY.'
              '\nAttempted path: ' + str_dir_path)


def open_url(url):
    """
    Opens URL in web browser
    :param url: URL
    :type url: str
    """
    webbrowser.open(url)


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
    Get directory path of Blue Hole Addon in %AppData%
    :rtype: str
    """

    # New method to resolve path (resolves symlinks; preferred)
    current_dir = Path(__file__).resolve().parent

    # Iterate upward through all parent directories (including root)
    for parent in [current_dir, *current_dir.parents]:
        if parent.name == "BlueHole":
            blue_hole_addon_path = parent
            break
    else:
        blue_hole_addon_path = None  # only reached if "BlueHole" wasn't found

    # # OLD METHOD: DOES NOT RESOLVE SYMLINKS, LESS PREFERRED.
    # blue_hole_addon_path = Path(get_resource_path_user() + "/scripts/addons/BlueHole")

    return str(blue_hole_addon_path)


def get_bh_url_db_file_path() -> str:
    """
    Returns the url database file path, which contains URLs for Blue Hole website, doc and tutorials.
    """
    return str(Path(get_blue_hole_user_addon_path(), 'url_database.ini'))


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


def get_file_path_list(dir_name):
    """
    Returns list of all files under a specific directory.
    :param dir_name: Directory in which to look under
    :type dir_name: str
    :rtype: lst
    """
    # create a list of file and subdirectories
    # names in the given directory
    list_of_files = os.listdir(dir_name)
    all_files = list()
    # Iterate over all the entries
    for entry in list_of_files:
        # Create full path
        full_path = os.path.join(dir_name, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(full_path):
            all_files = all_files + get_file_path_list(full_path)
        else:
            all_files.append(full_path)
    return all_files


def get_dirs_path_list(dir_path):
    """
    Returns a list of valid directory paths within a directory
    :param dir_path: Directory in which to look for directories
    :type dir_path: str
    :rtype: lst
    """
    dir_path_lst = []
    # Get list of items within a directory
    atlas_sub_dir_item_lst = os.listdir(dir_path)
    # Create a path from items within the directory, and if they are a directory, add them to the directories list.
    for item in atlas_sub_dir_item_lst:
        item_dir = dir_path + '/' + item
        if os.path.isdir(item_dir):
            dir_path_lst.append(item_dir)
    return dir_path_lst


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


def read_file(file_path):
    """
    Returns each line of a text file as part of a list
    :param file_path: File path to read
    :type file_path: str
    :rtype: lst
    """
    f = open(file_path, 'r')
    return f.read().splitlines()


def zip_file(source, destination):
    """
    Create a zip file from the source to the destination.
    :param source: Source path to compress
    :type source: str
    :param destination: Destination path of compressed archive (incl. extension)
    :type destination: str
    """
    def make_zipfile(output_filename, source_dir):
        relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
        with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
            for root, dirs, files in os.walk(source_dir):
                # add directory (needed for empty dirs)
                zip.write(root, os.path.relpath(root, relroot))
                for file in files:
                    filename = os.path.join(root, file)
                    if os.path.isfile(filename):  # regular files only
                        arcname = os.path.join(os.path.relpath(root, relroot), file)
                        zip.write(filename, arcname)
    make_zipfile(destination, source)


def unzip_file(source_file, destination_dir):
    """
    Extracts zip file to desired location.
    :param source_file: Path to file to extract.
    :type source_file: str
    :param destination_dir: Directory to extract into.
    :type destination_dir: str
    """
    with zipfile.ZipFile(source_file, 'r') as zip_ref:
        zip_ref.extractall(destination_dir)


def copy_file(source, destination):
    """
    Copies file from source to destination.
    """
    copyfile(source, destination)


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

def get_os_split_char() -> str:
    match filterUtils.get_platform():
        case filterUtils.OS.WIN:
            return '\\'
        case filterUtils.OS.MAC | filterUtils.OS.LINUX:
            return '/'

def ensure_file_writable_if_exists(file_path: str | Path) -> bool:
    """
    Ensures the file is writable by the owner, without removing any
    existing permissions.

    Returns False if the file does not exist.
    Raises PermissionError / OSError on failure.
    """
    p = Path(file_path)

    if not p.exists() or not p.is_file():
        return False

    match get_platform():
        case OS.MAC | OS.LINUX:
            st = os.stat(p)
            if not (st.st_mode & stat.S_IWUSR):
                os.chmod(p, st.st_mode | stat.S_IWUSR)

        case OS.WIN:
            # Best-effort: clear read-only attribute
            st = os.stat(p)
            if not (st.st_mode & stat.S_IWRITE):
                os.chmod(p, st.st_mode | stat.S_IWRITE)

        case _:
            raise RuntimeError("Unsupported OS")

    return True


def get_user_home_dir() -> Path:
    """
    Get the current user's home directory
    """
    match get_platform():
        case OS.WIN | OS.MAC:
            return Path.home()
        case OS.LINUX:
            return Path.home()
            # import pwd
            # user = os.getenv("USER")  # Prefer real user
            # home_dir = Path(pwd.getpwnam(user).pw_dir if user else os.path.expanduser("~"))
            # return home_dir
