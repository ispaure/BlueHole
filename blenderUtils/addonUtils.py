# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://github.com/ispaure/BlueHole

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

import bpy
import addon_utils
from . import fileUtils
from pathlib import Path
from typing import *


def is_addon_enabled_in_prefs(module_name: str) -> bool:
    if module_name in bpy.context.preferences.addons:
        return True
    elif f'bl_ext.user_default.{module_name}' in bpy.context.preferences.addons:
        return True
    return False


def get_extension_profile(module_name: str) -> Union[str, None]:
    for name, addon in bpy.context.preferences.addons.items():
        if name.count('.') == 2:
            if module_name == name.split('.')[-1]:
                return name.split('.')[1]
    return None


def is_addon_on_disk(module_name: str) -> bool:
    if any(m.__name__ == module_name for m in addon_utils.modules()):
        return True
    else:
        # Get extension profile for the addon (if loaded)
        extension_profile = get_extension_profile(module_name)
        if extension_profile is None:  # If there isn't a found extension profile, no need to pry further
            return False
        else:
            extension_path = Path(fileUtils.get_extensions_path(), extension_profile, module_name)
            if fileUtils.is_path_valid(extension_path):
                return True
            else:
                return False


def addon_utils_check_incl_profile(module_name: str):
    extension_profile = get_extension_profile(module_name)
    if extension_profile is not None:
        return addon_utils.check(f'bl_ext.{extension_profile}.{module_name}')
    else:
        return addon_utils.check(module_name)


def is_addon_enabled_and_loaded(module_name: str) -> bool:

    # enabled in user prefs?
    enabled_in_prefs = is_addon_enabled_in_prefs(module_name)

    enabled_flag, loaded_flag = addon_utils_check_incl_profile(module_name)

    # still present on disk? (module list is built from the add-ons folders)
    exists_on_disk = is_addon_on_disk(module_name)

    # We require: marked enabled, actually loaded (registered), and still exists
    return bool(enabled_in_prefs and enabled_flag and loaded_flag and exists_on_disk)


def print_enabled_addon_lst():
    print('List of enabled addons:')
    for name, addon in bpy.context.preferences.addons.items():
        print(name, addon)
