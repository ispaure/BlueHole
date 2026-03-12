"""
Environment manager utilities for Blue Hole.
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

from ..blenderUtils import blenderFile
from ..Lib.commonUtils.debugUtils import *
from ..preferences.prefs import *
from .model import Environment

# ----------------------------------------------------------------------------------------------------------------------
# CODE


env_tool_name = filename = os.path.basename(__file__)


def get_env_from_prefs_active_env() -> Environment:
    """
    Get the Environment instance matching the environment currently active in Blue Hole preferences.
    """
    env_name = prefs().general.active_environment
    return Environment(env_name)


def set_pref_current_env(env_name: str):
    """
    Set the current active environment from a name string.
    """
    prefs().general.active_environment = env_name


def get_default_env():
    """
    Get the default environment.
    """
    return Environment('default')


def set_env_to_default():
    """
    Set the active environment to the default environment.
    """
    log(Severity.DEBUG, env_tool_name, 'Setting Active Environment to Default')
    prefs().general.active_environment = 'default'


def if_current_env_missing_set_default():
    """
    Set the active environment to default if the current environment is missing or invalid.
    """

    def current_env_exists():
        current_env = prefs().general.active_environment

        # If active_environment is empty, Blue Hole was most likely newly installed.
        if len(current_env) == 0:
            msg = 'Current Env is Unset (0 char length)'
            log(Severity.ERROR, env_tool_name, msg)
            return False

        # If an environment is set, verify that its env_variables.ini file exists on disk.
        env_cls = Environment(current_env)
        if not os.path.isfile(env_cls.env_variables_path):
            msg = f'Current ({env_cls.name}) Env\'s env_variables.ini file is missing from disk!'
            log(Severity.ERROR, env_tool_name, msg)
            return False

        return True

    if not current_env_exists():
        set_env_to_default()


def get_env_dict() -> Dict[str, Environment]:
    """
    Return a deterministic map of environment name to Environment instance.

    Only directories inside the Blue Hole environment folder are included.
    """
    env_dir = Path(blenderFile.get_blue_hole_user_env_files_path())

    if not env_dir.exists():
        return {}

    env_names: List[str] = [
        p.name
        for p in env_dir.iterdir()
        if p.is_dir() and not p.name.startswith('.') and '.' not in p.name
    ]
    env_names.sort(key=lambda s: s.casefold())

    return {name: Environment(name) for name in env_names}


def get_env_lst_enum_property(exclude_default: bool = False):
    """
    Return environments formatted for use in a Blender EnumProperty.

    Each item is a tuple: (identifier, name, description)

    :param exclude_default: If True, omit the "default" environment
    :return: List of enum tuples
    """
    env_dict = get_env_dict()
    enum_items = []

    for env_name in env_dict.keys():
        if exclude_default and env_name == 'default':
            continue

        enum_items.append((env_name, env_name, ''))

    return enum_items
