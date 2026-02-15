"""
Update description
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

# System
from typing import *
from pathlib import Path

# Blue Hole
from ..blenderUtils import fileUtils
from ..commonUtils.debugUtils import *
from ..preferences.prefs import *
from .model import Environment

# ----------------------------------------------------------------------------------------------------------------------
# CODE


env_tool_name = filename = os.path.basename(__file__)


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
