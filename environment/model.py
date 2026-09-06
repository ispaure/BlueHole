"""
Environment data models and INI synchronization utilities for Blue Hole.
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
from typing import *

from ..Lib.commonUtils import configUtils
from ..Lib.commonUtils import fileUtils, dirUtils
from ..Lib.commonUtils.debugUtils import *
from ..blenderUtils import blenderFile
from ..preferences.prefs import *
from . import envManager

# ----------------------------------------------------------------------------------------------------------------------
# CODE


env_tool_name = filename = os.path.basename(__file__)


class Setting:
    """
    A single Blue Hole setting that maps a Blender preference path to an .ini value.
    """

    def __init__(self, pref_path: str, ini_section: str, ini_value: str, var_type: Type[Union[str, int, float, bool]]):
        self.pref_path: str = pref_path
        self.ini_section: str = ini_section
        self.ini_value: str = ini_value
        self.var_type: Type[Union[str, int, float, bool]] = var_type

    def __config_section_map_from_path_else_default_env(self, section, value, path):
        """
        Read a value from the provided environment .ini file, falling back to the default environment if needed.
        """
        return_value = configUtils.config_section_map(path, section, value)
        if return_value is not None:
            return return_value

        return_value = configUtils.config_section_map(blenderFile.get_default_env_var_path(), section, value)
        if return_value is None:
            msg = (
                'Could not find value {value} in section {section} in either the current env config file or the '
                'default. Please add missing value to one of those files.'
            ).format(value=value, section=section)
            log(Severity.ERROR, env_tool_name, msg)

        return return_value

    def set_pref_from_ini(self, path: Path):
        """
        Read the value from the .ini file and set it into the Blender preference dynamically.
        """
        # Get value from .ini
        ini_val_str = self.__config_section_map_from_path_else_default_env(self.ini_section, self.ini_value, path)

        # Convert to the correct type
        if self.var_type == bool:
            val = blenderFile.string_to_bool(ini_val_str)
        elif self.var_type == int:
            val = int(ini_val_str)
        elif self.var_type == float:
            val = float(ini_val_str)
        else:
            val = ini_val_str

        # Resolve the Blender preference object dynamically
        pref_obj = prefs().prefs
        attrs = self.pref_path.split(".")
        for attr in attrs[:-1]:
            pref_obj = getattr(pref_obj, attr)

        # Set the final attribute
        setattr(pref_obj, attrs[-1], val)

    def set_ini_from_pref(self, pref_obj, path: Path, show_verbose=False):
        """
        Write the value from the Blender preference to the .ini file, preserving the existing logic.

        Uses the provided path instead of the default current environment path.
        """
        # Get the current preference dynamically
        for attr in self.pref_path.split(".")[:-1]:
            pref_obj = getattr(pref_obj, attr)
        val = getattr(pref_obj, self.pref_path.split(".")[-1])

        # Convert bools to string if needed
        if self.var_type == bool:
            val_str = blenderFile.bool_to_string(val)
        else:
            val_str = str(val)

        # Debug message
        if show_verbose:
            msg = f'Evaluating [{self.ini_section}]: {self.ini_value} which ultimately should be: {val_str}'
            log(Severity.DEBUG, env_tool_name, msg)

        # Check if key exists in current environment
        current_val = configUtils.config_section_map(path, self.ini_section, self.ini_value)
        default_val = configUtils.config_section_map(blenderFile.get_default_env_var_path(), self.ini_section, self.ini_value)

        if current_val is None:
            if val_str == default_val:
                if show_verbose:
                    msg = 'Default config already stores same value. Ignore!'
                    log(Severity.DEBUG, env_tool_name, msg)
            else:
                msg = 'Value missing in active env, different from default. Adding to env_variables.ini.'
                log(Severity.WARNING, env_tool_name, msg)
                configUtils.config_add_variable(path, self.ini_section, self.ini_value, val_str)
        else:
            if val_str == current_val:
                if show_verbose:
                    msg = 'Value in env_variables.ini remains unchanged. Skipping.'
                    log(Severity.DEBUG, env_tool_name, msg)
            else:
                msg = 'Value in env_variables.ini has changed. Updating.'
                log(Severity.WARNING, env_tool_name, msg)
                configUtils.config_set_variable(path, self.ini_section, self.ini_value, val_str)


class Environment:
    """
    A Blue Hole environment containing multiple mapped settings.
    """

    def __init__(self, name: str):
        self.name: str = name
        self.path: Path = Path(blenderFile.get_blue_hole_user_env_files_path(), name)
        self.env_variables_path: Path = Path(self.path, 'env_variables.ini')
        self.setting_lst: List[Setting] = []
        self.__initialize_setting_lst()

    def __initialize_setting_lst(self):
        """
        Add the mapped settings to the environment's setting list.
        """
        from .mapping import bridge_setting_lst, container_setting_lst, directory_setting_lst, source_control_setting_lst

        self.setting_lst += directory_setting_lst
        self.setting_lst += bridge_setting_lst
        self.setting_lst += container_setting_lst
        self.setting_lst += source_control_setting_lst

    def set_pref_from_ini(self):
        """
        Apply this environment's .ini values to Blender preferences.
        """
        log(Severity.DEBUG, 'Environment', 'Setting preferences from .INI file')
        for setting in self.setting_lst:
            setting.set_pref_from_ini(self.env_variables_path)

    def set_ini_from_pref(self, pref_obj):
        """
        Write Blender preference values back into this environment's .ini file.
        """
        # TODO: Optimize this by caching env_variables.ini / configparser so it does not read the file repeatedly.
        for setting in self.setting_lst:
            setting.set_ini_from_pref(pref_obj, self.env_variables_path)

    def __delete_dir(self):
        """
        Delete this environment directory from disk.
        """
        dirUtils.Directory(self.path).delete()

    def delete_env(self):
        """
        Delete this environment from disk.
        """
        # Delete the environment folder on disk
        self.__delete_dir()

        # If the deleted environment was active, switch back to default and reload its settings.
        if self.name == envManager.get_env_from_prefs_active_env().name:
            msg = f'Deleted Environment "{self.name}" was active. Setting the default environment as active instead.'
            log(Severity.WARNING, env_tool_name, msg)
            envManager.set_env_to_default()
            current_env_cls = envManager.get_env_from_prefs_active_env()
            current_env_cls.set_pref_from_ini()

        # Terminate Blender process
        # TODO: Find a way to refresh active_environment in BlueHole.preferences.environment.bc.active_environment
        msg = 'Terminating Blender on Environment Deletion'
        log(Severity.INFO, env_tool_name, msg)
        blenderFile.terminate_blender()

    def add_env(self, source_env):
        """
        Create a new environment based on an existing environment.
        """
        # Check whether the environment can be added

        if len(self.name) == 0:
            msg = 'Cannot add new environment because it does not have a name. Aborting!'
            log(Severity.ERROR, env_tool_name, msg, popup=True)
            return False

        if len(self.name) > 30:
            msg = (
                f'Cannot add environment named: "{self.name}" because its character length '
                f'exceeds 30 characters. Aborting!'
            )
            log(Severity.ERROR, env_tool_name, msg, popup=True)
            return False

        if self.name in envManager.get_env_dict().keys():
            msg = (
                f'Cannot add environment named: "{self.name}" because one with the same name '
                'already exists. Aborting!'
            )
            log(Severity.ERROR, env_tool_name, msg, popup=True)
            return False

        log(Severity.INFO, env_tool_name, f'Adding New Environment "{self.name}" based on "{source_env.name}"')

        blenderFile.copy_dir(source_env.path, self.path)

        # Terminate Blender process
        # TODO: Find a way to refresh active_environment in BlueHole.preferences.environment.bc.active_environment
        msg = 'Terminating Blender on Environment Addition'
        log(Severity.INFO, env_tool_name, msg)
        blenderFile.terminate_blender()
        return True
