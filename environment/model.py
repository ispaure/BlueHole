"""
Write description here
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
from typing import *
from pathlib import Path

# Blue Hole
from ..blenderUtils import fileUtils, configUtils
from ..blenderUtils.debugUtils import *
from ..preferences.prefs import *
from . import envManager

# ----------------------------------------------------------------------------------------------------------------------
# CODE


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
        # Import mappings
        from .mapping import general_setting_lst, environment_setting_lst, source_control_setting_lst

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
        if self.name == envManager.get_env_from_prefs_active_env().name:
            msg = f'Deleted Environment "{self.name}" was active. Setting the default environment as active instead.'
            log(Severity.WARNING, env_tool_name, msg)
            envManager.set_env_to_default()
            current_env_cls = envManager.get_env_from_prefs_active_env()
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
        if self.name in envManager.get_env_dict().keys():
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
