"""
This will register/unregister any scripts associated with Blue Hole's active environment
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "GNU General Public License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

from pathlib import Path
import os
import bpy
from typing import *
import BlueHole.blenderUtils.addon as addon
from BlueHole.blenderUtils.debugUtils import print_debug_msg as print_debug_msg
import BlueHole.blenderUtils.importUtils as importUtils
import BlueHole.blenderUtils.fileUtils as fileUtils
import BlueHole.blenderUtils.configUtils as configUtils
import BlueHole.wrappers.perforceWrapper as p4Wrapper
from BlueHole.blenderUtils.debugUtils import *


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = False


# ----------------------------------------------------------------------------------------------------------------------
# CODE

# Modules to attempt to register from environment
modules_lst = ['blenderOperators/globalDirectories',
               'blenderOperators/globalExport',
               'blenderOperators/globalFoodDelivery',
               'blenderOperators/globalHelp',
               'blenderOperators/globalImport',
               'blenderOperators/globalMusic',
               'blenderOperators/globalOpen',
               'blenderOperators/globalSend',
               'blenderOperators/globalSourceControl',
               'blenderOperators/globalSpeedTree',
               'blenderOperators/globalThemes']


def is_current_env_missing():
    active_env = addon.preference().environment.active_environment
    if len(active_env) == 0:
        log(Severity.WARNING, 'is_current_env_missing', 'Current environment is unset (0 char long)')
        return True
    supposed_env_file_cfg_path = Path(fileUtils.get_blue_hole_user_env_files_path(), active_env, 'env_variables.ini')
    if not os.path.isfile(str(supposed_env_file_cfg_path)):
        log(Severity.WARNING, 'is_current_env_missing', f'Current environment "{active_env}" env_variables.ini file is unreachable!')
        return True
    return False


def if_environment_missing_set_to_default():
    """
    If environment currently saved is no longer on disk, default to use default environment instead
    """
    if is_current_env_missing():
        log(Severity.WARNING, 'if_environment_missing_set_to_default', 'Environment was missing, setting to default!')
        addon.preference().environment.active_environment = 'default'
    else:
        msg = f'Environment "{addon.preference().environment.active_environment}" not missing; loading!'
        log(Severity.INFO, 'if_environment_missing_set_to_default', msg)


def register_current_env():
    """
    Registers current environment custom tools, if they are available.
    """

    # Sets Blue Hole preferences from current env's file
    set_bh_prefs_from_current_env_ini()

    # Determine path to current environment
    current_env_path = get_env_dict()[addon.preference().environment.active_environment]
    for module in modules_lst:
        # Determine path to menu .py file
        python_module_path = str(Path(current_env_path + '/scripts/' + module + '.py'))

        # Attempt to register modules
        imp_module = importUtils.import_python_module_absolute_path(python_module_path)
        if imp_module is not None:
            imp_module.register()

        # Attempt to set perforce settings for the environment
        p4Wrapper.set_p4_env_settings()


def unregister_current_env():
    """
    Unregisters current environment custom tools, if they are available.
    """
    # Determine path to current environment
    current_env_path = get_env_dict()[addon.preference().environment.active_environment]
    for module in modules_lst:
        # Determine path to menu .py file
        python_module_path = str(Path(current_env_path + '/scripts/' + module + '.py'))

        # Attempt to unregister modules
        imp_module = importUtils.import_python_module_absolute_path(python_module_path)
        if imp_module is not None:
            imp_module.unregister()


def draw_current_env_menu_items(menu, layout):
    """
    Draw additional menu items specific to the current environment, if these are available.
    """
    print_debug_msg('Executing draw_current_env_menu_items function', show_verbose)

    # Determine path to current environment
    current_env_path = get_env_dict()[addon.preference().environment.active_environment]
    # Determine path to menu .py file
    python_module_path = str(Path(current_env_path + '/scripts/blenderOperators/' + menu + '.py'))

    # Attempt to import module
    module = importUtils.import_python_module_absolute_path(python_module_path)

    # If module got loaded and is valid
    if module is not None:
        # Add separator at beginning, to delimit new items.
        layout.separator()
        # Draw additional items
        module.draw_menu_items(layout)


def get_env_dict() -> Dict[str, str]:
    """
    Deterministic map: environment name -> absolute path.
    Only includes directories in the BlueHole env folder.
    """
    env_dir = Path(fileUtils.get_blue_hole_user_env_files_path())

    if not env_dir.exists():
        return {}

    # Realize to list, filter dirs, then sort case-insensitively
    env_names: List[str] = [
        p.name
        for p in env_dir.iterdir()
        if p.is_dir() and not p.name.startswith('.') and '.' not in p.name
    ]
    env_names.sort(key=lambda s: s.casefold())  # or key=str.lower

    return {name: str(env_dir / name) for name in env_names}


def get_env_lst_enum_property(exclude_default=False):
    """
    Get list of all environments, as can be used by an enum property.
    """
    env_enum_property_lst = []
    for env in get_env_dict().keys():
        if exclude_default:
            if 'default' not in env:
                env_enum_property_lst.append((str(env), str(env), ''))
        else:
            env_enum_property_lst.append((str(env), str(env), ''))

    return env_enum_property_lst


def set_bh_prefs_from_current_env_ini():
    """
    Sets Blender's Addon Preferences for Blue Hole from the current environment's ini file.
    """
    print_debug_msg('Setting Blender\'s Addon Preferences for Blue Hole from the current environment\'s ini file.',
                    show_verbose)

    # Strings
    addon.preference().environment.sc_path = configUtils.get_current_env_cfg_value('SourceContent', 'sc_root_path')
    addon.preference().environment.sc_path_alternate = configUtils.get_current_env_cfg_value('SourceContent', 'sc_root_path_alternate')
    addon.preference().environment.sc_dir_struct_scenes = configUtils.get_current_env_cfg_value('AssetDirectoryStructure', 'path_scenes')
    addon.preference().environment.sc_dir_struct_resources = configUtils.get_current_env_cfg_value('AssetDirectoryStructure', 'path_resources')
    addon.preference().environment.sc_dir_struct_st = configUtils.get_current_env_cfg_value('AssetDirectoryStructure', 'path_speedtree_msh')
    addon.preference().environment.sc_dir_struct_st_hr = configUtils.get_current_env_cfg_value('AssetDirectoryStructure', 'path_speedtree_msh_hr')
    addon.preference().environment.sc_dir_struct_st_lr = configUtils.get_current_env_cfg_value('AssetDirectoryStructure', 'path_speedtree_msh_lr')
    addon.preference().environment.sc_dir_struct_ref = configUtils.get_current_env_cfg_value('AssetDirectoryStructure', 'path_references')
    addon.preference().environment.sc_dir_struct_final = configUtils.get_current_env_cfg_value('AssetDirectoryStructure', 'path_final')
    addon.preference().environment.sc_dir_struct_msh_bake = configUtils.get_current_env_cfg_value('AssetDirectoryStructure', 'path_mshbake')
    addon.preference().environment.asset_hierarchy_struct_prefix_static_mesh = configUtils.get_current_env_cfg_value('AssetHierarchyStructure', 'prefix_static_mesh')
    addon.preference().environment.asset_hierarchy_struct_prefix_static_mesh_kit = configUtils.get_current_env_cfg_value('AssetHierarchyStructure', 'prefix_static_mesh_kit')
    addon.preference().environment.asset_hierarchy_struct_prefix_skeletal_mesh = configUtils.get_current_env_cfg_value('AssetHierarchyStructure', 'prefix_skeletal_mesh')
    addon.preference().environment.asset_hierarchy_empty_object_meshes = configUtils.get_current_env_cfg_value('AssetHierarchyStructure', 'null_render')
    addon.preference().environment.asset_hierarchy_empty_object_collisions = configUtils.get_current_env_cfg_value('AssetHierarchyStructure', 'null_collision')
    addon.preference().environment.asset_hierarchy_empty_object_sockets = configUtils.get_current_env_cfg_value('AssetHierarchyStructure', 'null_socket')
    addon.preference().general.unity_assets_path = configUtils.get_current_env_cfg_value('SendAssetHierarchiesToUnity', 'unity_assets_path')
    addon.preference().sourcecontrol.win32_env_setting_P4PORT = configUtils.get_current_env_cfg_value('Perforce', 'win32_env_setting_p4port')
    addon.preference().sourcecontrol.win32_env_setting_P4USER = configUtils.get_current_env_cfg_value('Perforce', 'win32_env_setting_p4user')
    addon.preference().sourcecontrol.win32_env_setting_P4CLIENT = configUtils.get_current_env_cfg_value('Perforce', 'win32_env_setting_p4client')
    addon.preference().sourcecontrol.macos_env_setting_P4PORT = configUtils.get_current_env_cfg_value('Perforce', 'macos_env_setting_p4port')
    addon.preference().sourcecontrol.macos_env_setting_P4USER = configUtils.get_current_env_cfg_value('Perforce', 'macos_env_setting_p4user')
    addon.preference().sourcecontrol.macos_env_setting_P4CLIENT = configUtils.get_current_env_cfg_value('Perforce', 'macos_env_setting_p4client')
    addon.preference().environment.sc_path_mac = configUtils.get_current_env_cfg_value('SourceContent', 'sc_root_path_mac')
    addon.preference().environment.sc_path_mac_alternate = configUtils.get_current_env_cfg_value('SourceContent', 'sc_root_path_mac_alternate')
    addon.preference().general.unity_assets_path_mac = configUtils.get_current_env_cfg_value('SendAssetHierarchiesToUnity', 'unity_assets_path_mac')
    addon.preference().general.unity_forward_axis = configUtils.get_current_env_cfg_value('SendAssetHierarchiesToUnity', 'forward_axis')
    addon.preference().general.unity_up_axis = configUtils.get_current_env_cfg_value('SendAssetHierarchiesToUnity', 'up_axis')
    addon.preference().sourcecontrol.source_control_solution = configUtils.get_current_env_cfg_value('SourceControl', 'solution')
    addon.preference().sourcecontrol.override_mode = configUtils.get_current_env_cfg_value('Perforce', 'override_env_setting_mode')
    # Multi user strings
    addon.preference().sourcecontrol.env_setting_user01_computername = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user01_computername')
    addon.preference().sourcecontrol.env_setting_user01_user = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user01_user')
    addon.preference().sourcecontrol.env_setting_user01_workspace = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user01_workspace')
    addon.preference().sourcecontrol.env_setting_user02_computername = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user02_computername')
    addon.preference().sourcecontrol.env_setting_user02_user = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user02_user')
    addon.preference().sourcecontrol.env_setting_user02_workspace = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user02_workspace')
    addon.preference().sourcecontrol.env_setting_user03_computername = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user03_computername')
    addon.preference().sourcecontrol.env_setting_user03_user = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user03_user')
    addon.preference().sourcecontrol.env_setting_user03_workspace = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user03_workspace')
    addon.preference().sourcecontrol.env_setting_user04_computername = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user04_computername')
    addon.preference().sourcecontrol.env_setting_user04_user = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user04_user')
    addon.preference().sourcecontrol.env_setting_user04_workspace = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user04_workspace')
    addon.preference().sourcecontrol.env_setting_user05_computername = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user05_computername')
    addon.preference().sourcecontrol.env_setting_user05_user = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user05_user')
    addon.preference().sourcecontrol.env_setting_user05_workspace = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user05_workspace')
    addon.preference().sourcecontrol.env_setting_user06_computername = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user06_computername')
    addon.preference().sourcecontrol.env_setting_user06_user = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user06_user')
    addon.preference().sourcecontrol.env_setting_user06_workspace = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user06_workspace')
    addon.preference().sourcecontrol.env_setting_user07_computername = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user07_computername')
    addon.preference().sourcecontrol.env_setting_user07_user = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user07_user')
    addon.preference().sourcecontrol.env_setting_user07_workspace = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user07_workspace')
    addon.preference().sourcecontrol.env_setting_user08_computername = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user08_computername')
    addon.preference().sourcecontrol.env_setting_user08_user = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user08_user')
    addon.preference().sourcecontrol.env_setting_user08_workspace = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user08_workspace')
    addon.preference().sourcecontrol.env_setting_user09_computername = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user09_computername')
    addon.preference().sourcecontrol.env_setting_user09_user = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user09_user')
    addon.preference().sourcecontrol.env_setting_user09_workspace = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user09_workspace')
    addon.preference().sourcecontrol.env_setting_user10_computername = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user10_computername')
    addon.preference().sourcecontrol.env_setting_user10_user = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user10_user')
    addon.preference().sourcecontrol.env_setting_user10_workspace = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user10_workspace')
    addon.preference().sourcecontrol.env_setting_user11_computername = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user11_computername')
    addon.preference().sourcecontrol.env_setting_user11_user = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user11_user')
    addon.preference().sourcecontrol.env_setting_user11_workspace = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user11_workspace')
    addon.preference().sourcecontrol.env_setting_user12_computername = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user12_computername')
    addon.preference().sourcecontrol.env_setting_user12_user = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user12_user')
    addon.preference().sourcecontrol.env_setting_user12_workspace = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user12_workspace')
    addon.preference().sourcecontrol.env_setting_user13_computername = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user13_computername')
    addon.preference().sourcecontrol.env_setting_user13_user = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user13_user')
    addon.preference().sourcecontrol.env_setting_user13_workspace = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user13_workspace')
    addon.preference().sourcecontrol.env_setting_user14_computername = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user14_computername')
    addon.preference().sourcecontrol.env_setting_user14_user = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user14_user')
    addon.preference().sourcecontrol.env_setting_user14_workspace = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user14_workspace')
    addon.preference().sourcecontrol.env_setting_user15_computername = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user15_computername')
    addon.preference().sourcecontrol.env_setting_user15_user = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user15_user')
    addon.preference().sourcecontrol.env_setting_user15_workspace = configUtils.get_current_env_cfg_value('Perforce', 'env_setting_user15_workspace')

    # Booleans
    addon.preference().general.exp_select_zero_root_transform = fileUtils.string_to_bool(configUtils.get_current_env_cfg_value('ExportBatchSelectionToFBX', 'zero_root_transform'))
    addon.preference().general.ue_bridge_zero_root_transform = fileUtils.string_to_bool(configUtils.get_current_env_cfg_value('SendAssetHierarchiesToUnreal', 'zero_root_transform'))
    addon.preference().general.ue_bridge_include_animation = fileUtils.string_to_bool(configUtils.get_current_env_cfg_value('SendAssetHierarchiesToUnreal', 'include_animation'))
    addon.preference().general.unity_bridge_zero_root_transform = fileUtils.string_to_bool(configUtils.get_current_env_cfg_value('SendAssetHierarchiesToUnity', 'zero_root_transform'))
    addon.preference().general.unity_bridge_include_animation = fileUtils.string_to_bool(configUtils.get_current_env_cfg_value('SendAssetHierarchiesToUnity', 'include_animation'))
    addon.preference().sourcecontrol.source_control_enable = fileUtils.string_to_bool(configUtils.get_current_env_cfg_value('SourceControl', 'enable'))
    addon.preference().sourcecontrol.source_control_error_aborts_exp = fileUtils.string_to_bool(configUtils.get_current_env_cfg_value('SourceControl', 'abort_export_on_error'))
    addon.preference().sourcecontrol.win32_env_override = fileUtils.string_to_bool(configUtils.get_current_env_cfg_value('Perforce', 'override_env_setting'))
    addon.preference().general.ue_automated = fileUtils.string_to_bool(configUtils.get_current_env_cfg_value('SendAssetHierarchiesToUnreal', 'is_automated'))
    addon.preference().general.ue_import_materials = fileUtils.string_to_bool(configUtils.get_current_env_cfg_value('SendAssetHierarchiesToUnreal', 'import_materials'))
    addon.preference().general.ue_import_textures = fileUtils.string_to_bool(configUtils.get_current_env_cfg_value('SendAssetHierarchiesToUnreal', 'import_textures'))
    addon.preference().environment.create_element_render = fileUtils.string_to_bool(configUtils.get_current_env_cfg_value('AssetHierarchyStructure', 'create_null_render'))
    addon.preference().environment.create_element_collision = fileUtils.string_to_bool(configUtils.get_current_env_cfg_value('AssetHierarchyStructure', 'create_null_collision'))
    addon.preference().environment.create_element_sockets = fileUtils.string_to_bool(configUtils.get_current_env_cfg_value('AssetHierarchyStructure', 'create_null_socket'))
    addon.preference().environment.exclude_element_if_no_child = fileUtils.string_to_bool(configUtils.get_current_env_cfg_value('AssetHierarchyStructure', 'exclude_null_if_no_child'))


def write_env_ini_from_bh_prefs():
    """
    Sets the current environment's ini file from the current values stored in Blender's Addon Preferences for Blue Hole.
    """

    # ------------------------------------------------------------------------------------------------------------------

    """
    This is the lists of preferences from Blender's Addon Preferences for Blue Hole.
    It allows user's settings to get reflected in env_variables.ini file for the current environment.

    I wish I could use the same list for grabbing preferences from the ini file and setting them in Blender, but sadly
    it's not that easy. :poop_emoji:. Instead, need to maintain the function set_bh_prefs_from_current_env_ini function.

    So both are intended to have the same settings!
    """
    pref_string_lst = [[addon.preference().environment.sc_path, 'SourceContent', 'sc_root_path'],
                       [addon.preference().environment.sc_path_alternate, 'SourceContent', 'sc_root_path_alternate'],
                       [addon.preference().environment.sc_dir_struct_scenes, 'AssetDirectoryStructure', 'path_scenes'],
                       [addon.preference().environment.sc_dir_struct_resources, 'AssetDirectoryStructure', 'path_resources'],
                       [addon.preference().environment.sc_dir_struct_st, 'AssetDirectoryStructure', 'path_speedtree_msh'],
                       [addon.preference().environment.sc_dir_struct_st_hr, 'AssetDirectoryStructure', 'path_speedtree_msh_hr'],
                       [addon.preference().environment.sc_dir_struct_st_lr, 'AssetDirectoryStructure', 'path_speedtree_msh_lr'],
                       [addon.preference().environment.sc_dir_struct_ref, 'AssetDirectoryStructure', 'path_references'],
                       [addon.preference().environment.sc_dir_struct_final, 'AssetDirectoryStructure', 'path_final'],
                       [addon.preference().environment.sc_dir_struct_msh_bake, 'AssetDirectoryStructure', 'path_mshbake'],
                       [addon.preference().environment.asset_hierarchy_struct_prefix_static_mesh, 'AssetHierarchyStructure', 'prefix_static_mesh'],
                       [addon.preference().environment.asset_hierarchy_struct_prefix_static_mesh_kit, 'AssetHierarchyStructure', 'prefix_static_mesh_kit'],
                       [addon.preference().environment.asset_hierarchy_struct_prefix_skeletal_mesh, 'AssetHierarchyStructure', 'prefix_skeletal_mesh'],
                       [addon.preference().environment.asset_hierarchy_empty_object_meshes, 'AssetHierarchyStructure', 'null_render'],
                       [addon.preference().environment.asset_hierarchy_empty_object_collisions, 'AssetHierarchyStructure', 'null_collision'],
                       [addon.preference().environment.asset_hierarchy_empty_object_sockets, 'AssetHierarchyStructure', 'null_socket'],
                       [addon.preference().general.unity_assets_path, 'SendAssetHierarchiesToUnity', 'unity_assets_path'],
                       [addon.preference().sourcecontrol.win32_env_setting_P4PORT, 'Perforce', 'win32_env_setting_p4port'],
                       [addon.preference().sourcecontrol.win32_env_setting_P4USER, 'Perforce', 'win32_env_setting_p4user'],
                       [addon.preference().sourcecontrol.win32_env_setting_P4CLIENT, 'Perforce', 'win32_env_setting_p4client'],
                       [addon.preference().sourcecontrol.macos_env_setting_P4PORT, 'Perforce', 'macos_env_setting_p4port'],
                       [addon.preference().sourcecontrol.macos_env_setting_P4USER, 'Perforce', 'macos_env_setting_p4user'],
                       [addon.preference().sourcecontrol.macos_env_setting_P4CLIENT, 'Perforce', 'macos_env_setting_p4client'],
                       [addon.preference().environment.sc_path_mac, 'SourceContent', 'sc_root_path_mac'],
                       [addon.preference().environment.sc_path_mac_alternate, 'SourceContent', 'sc_root_path_mac_alternate'],
                       [addon.preference().general.unity_assets_path_mac, 'SendAssetHierarchiesToUnity', 'unity_assets_path_mac'],
                       [addon.preference().general.unity_forward_axis, 'SendAssetHierarchiesToUnity', 'forward_axis'],
                       [addon.preference().general.unity_up_axis, 'SendAssetHierarchiesToUnity', 'up_axis'],
                       [addon.preference().sourcecontrol.source_control_solution, 'SourceControl', 'solution'],
                       [addon.preference().sourcecontrol.override_mode, 'Perforce', 'override_env_setting_mode'],
                       [addon.preference().sourcecontrol.env_setting_user01_computername, 'Perforce', 'env_setting_user01_computername'],
                       [addon.preference().sourcecontrol.env_setting_user01_user, 'Perforce', 'env_setting_user01_user'],
                       [addon.preference().sourcecontrol.env_setting_user01_workspace, 'Perforce', 'env_setting_user01_workspace'],
                       [addon.preference().sourcecontrol.env_setting_user02_computername, 'Perforce', 'env_setting_user02_computername'],
                       [addon.preference().sourcecontrol.env_setting_user02_user, 'Perforce', 'env_setting_user02_user'],
                       [addon.preference().sourcecontrol.env_setting_user02_workspace, 'Perforce', 'env_setting_user02_workspace'],
                       [addon.preference().sourcecontrol.env_setting_user03_computername, 'Perforce', 'env_setting_user03_computername'],
                       [addon.preference().sourcecontrol.env_setting_user03_user, 'Perforce', 'env_setting_user03_user'],
                       [addon.preference().sourcecontrol.env_setting_user03_workspace, 'Perforce', 'env_setting_user03_workspace'],
                       [addon.preference().sourcecontrol.env_setting_user04_computername, 'Perforce', 'env_setting_user04_computername'],
                       [addon.preference().sourcecontrol.env_setting_user04_user, 'Perforce', 'env_setting_user04_user'],
                       [addon.preference().sourcecontrol.env_setting_user04_workspace, 'Perforce', 'env_setting_user04_workspace'],
                       [addon.preference().sourcecontrol.env_setting_user05_computername, 'Perforce', 'env_setting_user05_computername'],
                       [addon.preference().sourcecontrol.env_setting_user05_user, 'Perforce', 'env_setting_user05_user'],
                       [addon.preference().sourcecontrol.env_setting_user05_workspace, 'Perforce', 'env_setting_user05_workspace'],
                       [addon.preference().sourcecontrol.env_setting_user06_computername, 'Perforce', 'env_setting_user06_computername'],
                       [addon.preference().sourcecontrol.env_setting_user06_user, 'Perforce', 'env_setting_user06_user'],
                       [addon.preference().sourcecontrol.env_setting_user06_workspace, 'Perforce', 'env_setting_user06_workspace'],
                       [addon.preference().sourcecontrol.env_setting_user07_computername, 'Perforce', 'env_setting_user07_computername'],
                       [addon.preference().sourcecontrol.env_setting_user07_user, 'Perforce', 'env_setting_user07_user'],
                       [addon.preference().sourcecontrol.env_setting_user07_workspace, 'Perforce', 'env_setting_user07_workspace'],
                       [addon.preference().sourcecontrol.env_setting_user08_computername, 'Perforce', 'env_setting_user08_computername'],
                       [addon.preference().sourcecontrol.env_setting_user08_user, 'Perforce', 'env_setting_user08_user'],
                       [addon.preference().sourcecontrol.env_setting_user08_workspace, 'Perforce', 'env_setting_user08_workspace'],
                       [addon.preference().sourcecontrol.env_setting_user09_computername, 'Perforce', 'env_setting_user09_computername'],
                       [addon.preference().sourcecontrol.env_setting_user09_user, 'Perforce', 'env_setting_user09_user'],
                       [addon.preference().sourcecontrol.env_setting_user09_workspace, 'Perforce', 'env_setting_user09_workspace'],
                       [addon.preference().sourcecontrol.env_setting_user10_computername, 'Perforce', 'env_setting_user10_computername'],
                       [addon.preference().sourcecontrol.env_setting_user10_user, 'Perforce', 'env_setting_user10_user'],
                       [addon.preference().sourcecontrol.env_setting_user10_workspace, 'Perforce', 'env_setting_user10_workspace'],
                       [addon.preference().sourcecontrol.env_setting_user11_computername, 'Perforce', 'env_setting_user11_computername'],
                       [addon.preference().sourcecontrol.env_setting_user11_user, 'Perforce', 'env_setting_user11_user'],
                       [addon.preference().sourcecontrol.env_setting_user11_workspace, 'Perforce', 'env_setting_user11_workspace'],
                       [addon.preference().sourcecontrol.env_setting_user12_computername, 'Perforce', 'env_setting_user12_computername'],
                       [addon.preference().sourcecontrol.env_setting_user12_user, 'Perforce', 'env_setting_user12_user'],
                       [addon.preference().sourcecontrol.env_setting_user12_workspace, 'Perforce', 'env_setting_user12_workspace'],
                       [addon.preference().sourcecontrol.env_setting_user13_computername, 'Perforce', 'env_setting_user13_computername'],
                       [addon.preference().sourcecontrol.env_setting_user13_user, 'Perforce', 'env_setting_user13_user'],
                       [addon.preference().sourcecontrol.env_setting_user13_workspace, 'Perforce', 'env_setting_user13_workspace'],
                       [addon.preference().sourcecontrol.env_setting_user14_computername, 'Perforce', 'env_setting_user14_computername'],
                       [addon.preference().sourcecontrol.env_setting_user14_user, 'Perforce', 'env_setting_user14_user'],
                       [addon.preference().sourcecontrol.env_setting_user14_workspace, 'Perforce', 'env_setting_user14_workspace'],
                       [addon.preference().sourcecontrol.env_setting_user15_computername, 'Perforce', 'env_setting_user15_computername'],
                       [addon.preference().sourcecontrol.env_setting_user15_user, 'Perforce', 'env_setting_user15_user'],
                       [addon.preference().sourcecontrol.env_setting_user15_workspace, 'Perforce', 'env_setting_user15_workspace']
                       ]

    pref_bool_lst = [[addon.preference().general.exp_select_zero_root_transform, 'ExportBatchSelectionToFBX', 'zero_root_transform'],
                     [addon.preference().general.ue_bridge_zero_root_transform, 'SendAssetHierarchiesToUnreal', 'zero_root_transform'],
                     [addon.preference().general.ue_bridge_include_animation, 'SendAssetHierarchiesToUnreal', 'include_animation'],
                     [addon.preference().general.unity_bridge_zero_root_transform, 'SendAssetHierarchiesToUnity', 'zero_root_transform'],
                     [addon.preference().general.unity_bridge_include_animation, 'SendAssetHierarchiesToUnity', 'include_animation'],
                     [addon.preference().sourcecontrol.source_control_enable, 'SourceControl', 'enable'],
                     [addon.preference().sourcecontrol.source_control_error_aborts_exp, 'SourceControl', 'abort_export_on_error'],
                     [addon.preference().sourcecontrol.win32_env_override, 'Perforce', 'override_env_setting'],
                     [addon.preference().general.ue_automated, 'SendAssetHierarchiesToUnreal', 'is_automated'],
                     [addon.preference().general.ue_import_materials, 'SendAssetHierarchiesToUnreal', 'import_materials'],
                     [addon.preference().general.ue_import_textures, 'SendAssetHierarchiesToUnreal', 'import_textures'],
                     [addon.preference().environment.create_element_render, 'AssetHierarchyStructure', 'create_null_render'],
                     [addon.preference().environment.create_element_collision, 'AssetHierarchyStructure', 'create_null_collision'],
                     [addon.preference().environment.create_element_sockets, 'AssetHierarchyStructure', 'create_null_socket'],
                     [addon.preference().environment.exclude_element_if_no_child, 'AssetHierarchyStructure', 'exclude_null_if_no_child']
                     ]

    # ------------------------------------------------------------------------------------------------------------------

    msg = '\n\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!' \
          '\nSetting the current environment\'s ini file to variables from Blender\'s Addon Preferences for Blue Hole.'
    print_debug_msg(msg, show_verbose)

    # For every string parameter
    for pref_string in pref_string_lst:
        # Debug message
        msg = 'Evaluating [{section}]: {value} which needs to be: {output}'.format(section=pref_string[1],
                                                                                   value=pref_string[2],
                                                                                   output=pref_string[0])
        print_debug_msg(msg, show_verbose)

        # If value is missing from active environment, is it the default value? If so do nothing
        if configUtils.config_section_map(pref_string[1], pref_string[2], fileUtils.get_current_env_var_path()) is None:
            if pref_string[0] == configUtils.config_section_map(pref_string[1], pref_string[2], fileUtils.get_default_env_var_path()):
                print_debug_msg('Default config already stores same value. Ignore!', show_verbose)
            else:
                msg = 'Value not in active environment\'s env_variables.ini and is different than the default. ' \
                      'It needs to be added to the env_variable.ini file.'
                print_debug_msg(msg, show_verbose)
                configUtils.config_add_variable(pref_string[1], pref_string[2], pref_string[0], fileUtils.get_current_env_var_path())
        else:
            if pref_string[0] == configUtils.config_section_map(pref_string[1], pref_string[2], fileUtils.get_current_env_var_path()):
                msg = 'Value is in active environment\'s env_variable.ini. But it remains unchanged. ' \
                      'It does not need updating.'
                print_debug_msg(msg, show_verbose)
            else:
                msg = 'Value is in active environment\'s env_variables.ini. It has changed and needs updating'
                print_debug_msg(msg, show_verbose)
                configUtils.config_set_variable(pref_string[1], pref_string[2], pref_string[0], fileUtils.get_current_env_var_path())

    # For every boolean parameter
    for pref_bool in pref_bool_lst:
        # Debug message
        msg = 'Evaluating [{section}]: {value} which ' \
              'needs to be: {output}'.format(section=pref_bool[1],
                                             value=pref_bool[2],
                                             output=fileUtils.bool_to_string(pref_bool[0]))
        print_debug_msg(msg, show_verbose)

        # If value is missing from active environment, is it the default value? If so do nothing
        if configUtils.config_section_map(pref_bool[1], pref_bool[2], fileUtils.get_current_env_var_path()) is None:
            if fileUtils.bool_to_string(pref_bool[0]) == configUtils.config_section_map(pref_bool[1], pref_bool[2], fileUtils.get_default_env_var_path()):
                print_debug_msg('Default config already stores same value. Ignore!', show_verbose)
            else:
                msg = 'Value not in active environment\'s env_variables.ini and is different than the default. ' \
                      'It needs to be added to the env_variable.ini file.'
                print_debug_msg(msg, show_verbose)
                configUtils.config_add_variable(pref_bool[1], pref_bool[2], fileUtils.bool_to_string(pref_bool[0]), fileUtils.get_current_env_var_path())
        else:
            if fileUtils.bool_to_string(pref_bool[0]) == configUtils.config_section_map(pref_bool[1], pref_bool[2], fileUtils.get_current_env_var_path()):
                msg = 'Value is in active environment\'s env_variable.ini. But it remains unchanged. ' \
                      'It does not need updating.'
                print_debug_msg(msg, show_verbose)
            else:
                msg = 'Value is in active environment\'s env_variables.ini. It has changed and needs updating'
                print_debug_msg(msg, show_verbose)
                configUtils.config_set_variable(pref_bool[1], pref_bool[2], fileUtils.bool_to_string(pref_bool[0]), fileUtils.get_current_env_var_path())

