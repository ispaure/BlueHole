"""
This is the refactored version of the Environments system of Blue Hole (November 2025)
It aids to streamline the logic of Blue Hole's Environments
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

from typing import *
from pathlib import Path
import BlueHole.blenderUtils.fileUtils as fileUtils
import BlueHole.blenderUtils.configUtils as configUtils
from BlueHole.blenderUtils.debugUtils import *
import BlueHole.blenderUtils.filterUtils as filterUtils
from BlueHole.preferences.prefsCls import *


# ----------------------------------------------------------------------------------------------------------------------
# Environment code


env_tool_name = filename = os.path.basename(__file__)


class Setting:
    """
    A setting parameter stored in Blue Hole
    """
    def __init__(self, pref_path: str, ini_section: str, ini_value: str, var_type: Type[Union[str, int, float, bool]]):
        self.pref_path: str = pref_path       # e.g., "environment.sc_path"
        self.ini_section: str = ini_section
        self.ini_value: str = ini_value
        self.var_type: Type[Union[str, int, float, bool]] = var_type

    def __config_section_map_from_path_else_default_env(self, section, value, path):

        # Attempt to get value from path
        return_value = configUtils.config_section_map(section, value, path)
        if return_value is not None:
            return return_value

        # Attempt to get value from default environment's path
        return_value = configUtils.config_section_map(section, value, fileUtils.get_default_env_var_path())
        if return_value is None:
            msg = 'Could not find value {value} in section {section} in either the current env config file or the ' \
                  'default. Please add missing value to one of those files.'.format(value=value, section=section)
            log(Severity.ERROR, env_tool_name, msg)
        return return_value

    def set_pref_from_ini(self, path: Path):
        """
        Reads the value from the INI and sets it into the Blender preference dynamically.
        """
        # 1. Get value from INI
        ini_val_str = self.__config_section_map_from_path_else_default_env(self.ini_section, self.ini_value, path)

        # 2. Convert to the correct type
        if self.var_type == bool:
            val = fileUtils.string_to_bool(ini_val_str)
        elif self.var_type == int:
            val = int(ini_val_str)
        elif self.var_type == float:
            val = float(ini_val_str)
        else:
            val = ini_val_str  # default: str

        # 3. Resolve the Blender preference object dynamically
        pref_obj = prefs().prefs  # always fresh
        attrs = self.pref_path.split(".")
        for attr in attrs[:-1]:
            pref_obj = getattr(pref_obj, attr)

        # 4. Set the final attribute
        setattr(pref_obj, attrs[-1], val)

    def set_ini_from_pref(self, pref_obj, path: Path, show_verbose=False):
        """
        Writes the value from Blender preference to the INI file, preserving your old logic.
        Uses the provided path instead of the default current environment path.
        """
        # 1. Get the current preference dynamically
        for attr in self.pref_path.split(".")[:-1]:
            pref_obj = getattr(pref_obj, attr)
        val = getattr(pref_obj, self.pref_path.split(".")[-1])
        # 2. Convert bools to string if needed
        if self.var_type == bool:
            val_str = fileUtils.bool_to_string(val)
        else:
            val_str = str(val)
        # 3. Debug message
        if show_verbose:
            msg = f'Evaluating [{self.ini_section}]: {self.ini_value} which ultimately should be: {val_str}'
            log(Severity.DEBUG, env_tool_name, msg)
        # 4. Check if key exists in current environment
        current_val = configUtils.config_section_map(self.ini_section, self.ini_value, str(path))
        default_val = configUtils.config_section_map(self.ini_section, self.ini_value, fileUtils.get_default_env_var_path())
        if current_val is None:
            if val_str == default_val:
                if show_verbose:
                    msg = 'Default config already stores same value. Ignore!'
                    log(Severity.DEBUG, env_tool_name, msg)
            else:
                msg = f'Value missing in active env, different from default. Adding to env_variables.ini.'
                log(Severity.WARNING, env_tool_name, msg)
                configUtils.config_add_variable(self.ini_section, self.ini_value, val_str, str(path))
        else:
            if val_str == current_val:
                if show_verbose:
                    msg = 'Value in env_variables.ini remains unchanged. Skipping.'
                    log(Severity.DEBUG, env_tool_name, msg)
            else:
                msg = 'Value in env_variables.ini has changed. Updating.'
                log(Severity.WARNING, env_tool_name, msg)
                configUtils.config_set_variable(self.ini_section, self.ini_value, val_str, path)


general_setting_lst = [
    # ------------------- General -------------------
    Setting(pref_path='general.unity_assets_path', ini_section='SendAssetHierarchiesToUnity', ini_value='unity_assets_path', var_type=str),
    Setting(pref_path='general.unity_assets_path_mac', ini_section='SendAssetHierarchiesToUnity', ini_value='unity_assets_path_mac', var_type=str),
    Setting(pref_path='general.unity_forward_axis', ini_section='SendAssetHierarchiesToUnity', ini_value='forward_axis', var_type=str),
    Setting(pref_path='general.unity_up_axis', ini_section='SendAssetHierarchiesToUnity', ini_value='up_axis', var_type=str),
    Setting(pref_path='general.exp_select_zero_root_transform', ini_section='ExportBatchSelectionToFBX', ini_value='zero_root_transform', var_type=bool),
    Setting(pref_path='general.ue_bridge_zero_root_transform', ini_section='SendAssetHierarchiesToUnreal', ini_value='zero_root_transform', var_type=bool),
    Setting(pref_path='general.ue_bridge_include_animation', ini_section='SendAssetHierarchiesToUnreal', ini_value='include_animation', var_type=bool),
    Setting(pref_path='general.unity_bridge_zero_root_transform', ini_section='SendAssetHierarchiesToUnity', ini_value='zero_root_transform', var_type=bool),
    Setting(pref_path='general.unity_bridge_include_animation', ini_section='SendAssetHierarchiesToUnity', ini_value='include_animation', var_type=bool),
    Setting(pref_path='general.ue_automated', ini_section='SendAssetHierarchiesToUnreal', ini_value='is_automated', var_type=bool),
    Setting(pref_path='general.ue_import_materials', ini_section='SendAssetHierarchiesToUnreal', ini_value='import_materials', var_type=bool),
    Setting(pref_path='general.ue_import_textures', ini_section='SendAssetHierarchiesToUnreal', ini_value='import_textures', var_type=bool),
]

environment_setting_lst = [
    # ------------------- Environment -------------------
    Setting(pref_path='environment.sc_path', ini_section='SourceContent', ini_value='sc_root_path', var_type=str),
    Setting(pref_path='environment.sc_path_alternate', ini_section='SourceContent', ini_value='sc_root_path_alternate', var_type=str),
    Setting(pref_path='environment.sc_path_mac', ini_section='SourceContent', ini_value='sc_root_path_mac', var_type=str),
    Setting(pref_path='environment.sc_path_mac_alternate', ini_section='SourceContent', ini_value='sc_root_path_mac_alternate', var_type=str),
    Setting(pref_path='environment.sc_dir_struct_scenes', ini_section='AssetDirectoryStructure', ini_value='path_scenes', var_type=str),
    Setting(pref_path='environment.sc_dir_struct_resources', ini_section='AssetDirectoryStructure', ini_value='path_resources', var_type=str),
    Setting(pref_path='environment.sc_dir_struct_st', ini_section='AssetDirectoryStructure', ini_value='path_speedtree_msh', var_type=str),
    Setting(pref_path='environment.sc_dir_struct_st_hr', ini_section='AssetDirectoryStructure', ini_value='path_speedtree_msh_hr', var_type=str),
    Setting(pref_path='environment.sc_dir_struct_st_lr', ini_section='AssetDirectoryStructure', ini_value='path_speedtree_msh_lr', var_type=str),
    Setting(pref_path='environment.sc_dir_struct_ref', ini_section='AssetDirectoryStructure', ini_value='path_references', var_type=str),
    Setting(pref_path='environment.sc_dir_struct_final', ini_section='AssetDirectoryStructure', ini_value='path_final', var_type=str),
    Setting(pref_path='environment.sc_dir_struct_msh_bake', ini_section='AssetDirectoryStructure', ini_value='path_mshbake', var_type=str),
    Setting(pref_path='environment.asset_hierarchy_struct_prefix_static_mesh', ini_section='AssetHierarchyStructure', ini_value='prefix_static_mesh', var_type=str),
    Setting(pref_path='environment.asset_hierarchy_struct_prefix_static_mesh_kit', ini_section='AssetHierarchyStructure', ini_value='prefix_static_mesh_kit', var_type=str),
    Setting(pref_path='environment.asset_hierarchy_struct_prefix_skeletal_mesh', ini_section='AssetHierarchyStructure', ini_value='prefix_skeletal_mesh', var_type=str),
    Setting(pref_path='environment.asset_hierarchy_empty_object_meshes', ini_section='AssetHierarchyStructure', ini_value='null_render', var_type=str),
    Setting(pref_path='environment.asset_hierarchy_empty_object_collisions', ini_section='AssetHierarchyStructure', ini_value='null_collision', var_type=str),
    Setting(pref_path='environment.asset_hierarchy_empty_object_sockets', ini_section='AssetHierarchyStructure', ini_value='null_socket', var_type=str),
    Setting(pref_path='environment.create_element_render', ini_section='AssetHierarchyStructure', ini_value='create_null_render', var_type=bool),
    Setting(pref_path='environment.create_element_collision', ini_section='AssetHierarchyStructure', ini_value='create_null_collision', var_type=bool),
    Setting(pref_path='environment.create_element_sockets', ini_section='AssetHierarchyStructure', ini_value='create_null_socket', var_type=bool),
    Setting(pref_path='environment.exclude_element_if_no_child', ini_section='AssetHierarchyStructure', ini_value='exclude_null_if_no_child', var_type=bool),
]

source_control_setting_lst = [
    # ------------------- SourceControl -------------------
    Setting(pref_path='sourcecontrol.win32_env_setting_p4port', ini_section='Perforce', ini_value='win32_env_setting_p4port', var_type=str),
    Setting(pref_path='sourcecontrol.win32_env_setting_p4user', ini_section='Perforce', ini_value='win32_env_setting_p4user', var_type=str),
    Setting(pref_path='sourcecontrol.win32_env_setting_p4client', ini_section='Perforce', ini_value='win32_env_setting_p4client', var_type=str),
    Setting(pref_path='sourcecontrol.macos_env_setting_p4port', ini_section='Perforce', ini_value='macos_env_setting_p4port', var_type=str),
    Setting(pref_path='sourcecontrol.macos_env_setting_p4user', ini_section='Perforce', ini_value='macos_env_setting_p4user', var_type=str),
    Setting(pref_path='sourcecontrol.macos_env_setting_p4client', ini_section='Perforce', ini_value='macos_env_setting_p4client', var_type=str),
    Setting(pref_path='sourcecontrol.source_control_solution', ini_section='SourceControl', ini_value='solution', var_type=str),
    Setting(pref_path='sourcecontrol.source_control_enable', ini_section='SourceControl', ini_value='enable', var_type=bool),
    Setting(pref_path='sourcecontrol.source_control_error_aborts_exp', ini_section='SourceControl', ini_value='abort_export_on_error', var_type=bool),
    Setting(pref_path='sourcecontrol.win32_env_override', ini_section='Perforce', ini_value='override_env_setting', var_type=bool),
]


class Environment:
    """
    A blue hole environment which has multiple settings
    """
    def __init__(self, name: str):
        self.name: str = name
        self.path: Path = Path(fileUtils.get_blue_hole_user_env_files_path(), name)
        self.env_variables_path: Path = Path(self.path, 'env_variables.ini')
        self.setting_lst: List[Setting] = []
        self.__initialize_setting_lst()

    def __initialize_setting_lst(self):

        """
        Add the Settings to the environment's list
        """

        # Add Setting Lists
        self.setting_lst += general_setting_lst
        self.setting_lst += environment_setting_lst
        self.setting_lst += source_control_setting_lst

    def set_pref_from_ini(self):
        for setting in self.setting_lst:
            setting.set_pref_from_ini(self.env_variables_path)

    def set_ini_from_pref(self, pref_obj):
        # TODO: Optimize this by caching the env_variables.ini / configparser so it doesn't read the file like 50 times in the loop
        for setting in self.setting_lst:
            setting.set_ini_from_pref(pref_obj, self.env_variables_path)

    def __delete_dir(self):
        fileUtils.delete_dir(self.path)

    def delete_env(self):
        """
        Deletes an environment on disk
        """

        # Delete the environment folder on disk
        self.__delete_dir()

        # If the deleted environment corresponds to the active one, set default with default settings
        if self.name == get_env_from_prefs_active_env().name:
            msg = f'Deleted Environment "{self.name}" was active. Setting the default environment as active instead.'
            log(Severity.WARNING, env_tool_name, msg)
            set_env_to_default()
            current_env_cls = get_env_from_prefs_active_env()
            current_env_cls.set_pref_from_ini()

        # Terminate Blender Process
        # TODO: Find a way to refresh active_environment in BlueHole.preferences.environment.bc.active_environment
        msg = f'Terminating Blender on Environment Deletion'
        log(Severity.INFO, env_tool_name, msg)
        fileUtils.terminate_blender()

    def add_env(self, source_env):
        """
        Creates a new environment based on an existing one (source_env)
        """

        # CHECKS IF ENVIRONMENT CAN BE ADDED

        # If name has no length
        if len(self.name) == 0:
            msg = 'Cannot add new environment because it does not have a name. Aborting!'
            log(Severity.ERROR, env_tool_name, msg, popup=True)
            return False

        # If name's length exceeds 30 in length
        if len(self.name) > 30:
            msg = (f'Cannot add environment named: "{self.name}" because its character length '
                   f'exceeds 30 characters. Aborting!')
            log(Severity.ERROR, env_tool_name, msg, popup=True)
            return False

        # If name is already in list
        if self.name in get_env_dict().keys():
            msg = (f'Cannot add environment named: "{self.name}" because one with the same name '
                   'already exists. Aborting!')
            log(Severity.ERROR, env_tool_name, msg, popup=True)
            return False

        # CAN BE ADDED!
        log(Severity.INFO, env_tool_name, f'Adding New Environment "{self.name}" based on "{source_env.name}"')

        fileUtils.copy_dir(source_env.path, self.path)

        # Terminate Blender Process
        # TODO: Find a way to refresh active_environment in BlueHole.preferences.environment.bc.active_environment
        msg = f'Terminating Blender on Environment Addition'
        log(Severity.INFO, env_tool_name, msg)
        fileUtils.terminate_blender()
        return True


class BlueHolePrefs:
    """
    Utilities related to Blue Hole Preferences
    """
    def __init__(self):
        pass

    def __get_dir_path_if_valid(self, path_def: str, path_str: str, quiet: bool) -> Optional[Path]:

        # Validate something other than default has been set.
        if len(path_str) == 0 or path_str.startswith('<'):
            msg = (f'{path_def} Path "{path_str}" is undefined. It is required for the bridges to game '
                   f'engines. Navigate to Blender Blue Hole settings and define a Source Content Path.')
            log(Severity.CRITICAL, env_tool_name, msg, popup=not quiet)
            return None

        # Validate the path exists
        if not os.path.exists(path_str):
            msg = (f'{path_def} Path "{path_str}" does not correspond to a valid path on disk. '
                   f'Navigate to Blender Blue Hole settings and define a valid Source Content Path.')
            log(Severity.CRITICAL, env_tool_name, msg, popup=not quiet)
            return None

        # Validate the path is not pointing to a file
        if os.path.isfile(path_str):
            msg = (f'{path_def} Path "{path_str}" points to a file, not a directory. Navigate to '
                   f'Blender Blue Hole settings and define a Source Content Path that points to a directory.')
            log(Severity.CRITICAL, env_tool_name, msg, popup=not quiet)
            return None

        # Passed the Checks -- Return the Path!
        return Path(path_str)

    def get_valid_sc_dir_path(self, quiet: bool = False) -> Optional[Path]:
        """Attempts to get a valid source content path from the current Blue Hole settings, regardless of OS"""
        path_def = 'Source Content'

        if filterUtils.filter_platform('win'):
            sc_path_to_attempt_lst = [prefs().env.sc_path,
                                      prefs().env.sc_path_alternate]
        elif filterUtils.filter_platform('mac'):
            sc_path_to_attempt_lst = [prefs().env.sc_path_mac,
                                      prefs().env.sc_path_mac_alternate]
        else:
            msg_os = 'Invalid OS! Blue Hole only supports Windows & macOS at the moment.'
            log(Severity.CRITICAL, env_tool_name, msg_os)
            return None

        # Attempt to get the source content path from the available options
        for sc_path in sc_path_to_attempt_lst:
            result = self.__get_dir_path_if_valid(path_def, sc_path, quiet)
            if result:
                return result

        # If got here without able to return, no path was valid
        error_msg = (f'Unable to find a valid {path_def} Path in Blue Hole settings, which is required for the '
                     'bridges to game engines. See log for more details.')
        log(Severity.CRITICAL, env_tool_name, error_msg, popup=not quiet)
        return None

    def get_valid_unity_asset_dir_path(self, quiet: bool = False) -> Optional[Path]:
        """Attempts to get a valid unity asset path from the current Blue Hole settings, regardless of OS"""
        path_def = 'Unity Assets'

        if filterUtils.filter_platform('win'):
            unity_asset_path = prefs().general.unity_assets_path
        elif filterUtils.filter_platform('mac'):
            unity_asset_path = prefs().general.unity_assets_path_mac
        else:
            msg_os = 'Invalid OS! Blue Hole only supports Windows & macOS at the moment.'
            log(Severity.CRITICAL, env_tool_name, msg_os)
            return None

        # Attempt to get the unity asset path from the available options
        result = self.__get_dir_path_if_valid(path_def, unity_asset_path, quiet)
        if result:
            return result

        # If got here without able to return, no path was valid
        error_msg = (f'Unable to find a valid {path_def} Path in Blue Hole settings, which is required for the '
                     'bridge to Unity. See log for more details.')
        log(Severity.CRITICAL, env_tool_name, error_msg, popup=quiet)
        return None


def get_env_from_prefs_active_env() -> Environment:
    """
    Gets an Environment class that matches the current one that's active (per the Blender Blue Hole Preferences)
    """
    env_name = prefs().env.active_environment
    return Environment(env_name)


def set_pref_current_env(env_name: str):
    """
    Sets the current environment from a name string
    """
    prefs().env.active_environment = env_name


def get_default_env():
    return Environment('default')


def set_env_to_default():
    log(Severity.DEBUG, env_tool_name, 'Setting Active Environment to Default')
    prefs().env.active_environment = 'default'


def if_current_env_missing_set_default():
    def current_env_exists():
        current_env = prefs().env.active_environment

        # If length of active_environment field is 0, Blue Hole was most likely newly installed (need to set to default)
        if len(current_env) == 0:
            msg = 'Current Env is Unset (0 char length)'
            log(Severity.ERROR, env_tool_name, msg)
            return False

        # If there is length, see if env_variables.ini file exists on disk for that environment
        env_cls = Environment(current_env)
        if not os.path.isfile(env_cls.env_variables_path):
            msg = f'Current ({env_cls.name}) Env\'s env_variables.ini file is missing from disk!'
            log(Severity.ERROR, env_tool_name, msg)
            return False

        # Environment exists
        return True

    if not current_env_exists():
        set_env_to_default()


def get_env_dict() -> Dict[str, Environment]:
    """
    Deterministic map: environment name -> Environment instance.
    Only includes directories in the BlueHole env folder.
    """
    env_dir = Path(fileUtils.get_blue_hole_user_env_files_path())

    if not env_dir.exists():
        return {}

    # Filter directories: no hidden or dotted names
    env_names: List[str] = [
        p.name
        for p in env_dir.iterdir()
        if p.is_dir() and not p.name.startswith('.') and '.' not in p.name
    ]
    env_names.sort(key=lambda s: s.casefold())  # case-insensitive sort

    # Return a dict of name -> Environment instance
    return {name: Environment(name) for name in env_names}


def get_env_lst_enum_property(exclude_default=False):
    """
    Get list of all environments, as can be used by an enum property.
    """
    return [
        (env, env, '')
        for env in get_env_dict().keys()
        if not (exclude_default and env == 'default')
    ]
