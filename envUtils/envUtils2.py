"""
This is part of a great refactoring effort to make creating and editing environments more intuitive to end users.

I am planning to have environments still saved with same data as .ini files (as to not put project-specific info in
the Blender configuration file). But have users be able to toggle environment and edit the fields from within
Blender preferences (and have that saved to the .ini files).

OK so after much thought, this is how I'll have to go about this

*Button Set Active Environment*
    -When triggered, sets the value of the current env. to whatever is wanted.
    -Load that environment's settings in the Blender settings (and if not found, defaults to the default - preventing
    bugs as parameters gets added, unless they'd keep name and change type; unlikely).

*Draw function on loop in settings*
    -Will get the values from the current environment properties (as well as current env. and write to file)
    -That way it keeps writing changes to file, but will always have existing settings before writing as set environment
    will have been done before changes.

*Will need to test heavily but that should work and make it much simpler for users*
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

import BlueHole.blenderUtils.uiUtils as uiUtils
import BlueHole.envUtils.envUtils as envUtils
import BlueHole.blenderUtils.fileUtils as fileUtils
import BlueHole.blenderUtils.filterUtils as filterUtils
from pathlib import Path
import BlueHole.blenderUtils.addon as addon
import os
from BlueHole.blenderUtils.debugUtils import *


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE


def delete_env(env):
    """
    Deletes an environment on disk
    """
    delete_path = envUtils.get_env_dict()[env]
    print_debug_msg('Deleting folder at: "{}"'.format(delete_path), show_verbose)
    fileUtils.delete_dir(delete_path)
    # TODO: Find a way I don't need to be this drastic to refresh the active environments.
    # TODO: I'd need to be able to refresh a property within a blender operator
    fileUtils.terminate_blender()
    return True


def add_env(env_name, based_on_env):
    """
    Creates a new environment based on an existing one
    """
    tool_name = 'Add Environment Tool'

    env_name = env_name.replace(' ', '_').replace('.', '_')
    print_debug_msg('Adding new environment named: ' + env_name, show_verbose)
    print_debug_msg('New environment based on: ' + based_on_env, show_verbose)
    if len(env_name) == 0:
        msg = 'Cannot add new environment because it does not have a name. Aborting!'
        uiUtils.show_dialog_box(tool_name, msg)
        return False
    elif env_name in envUtils.get_env_dict().keys():
        msg = 'Cannot add environment named: "{}" because one with the same name ' \
              'already exists. Aborting!'.format(env_name)
        uiUtils.show_dialog_box(tool_name, msg)
        return False
    elif len(env_name) > 30:
        msg = 'Cannot add environment named: "{}" because its character length ' \
              'exceeds 30 characters. Aborting!'.format(env_name)
        uiUtils.show_dialog_box(tool_name, msg)
        return False
    else:
        reference_path = envUtils.get_env_dict()[based_on_env]
        new_env_path = reference_path[0:-len(based_on_env)] + env_name
        print_debug_msg('Copying folder from "{}" to "{}".'.format(reference_path, new_env_path), show_verbose)
        fileUtils.copy_dir(reference_path, new_env_path)
        # Terminate Blender Process
        # TODO: Find a way I don't need to be this drastic to refresh the active environments.
        # TODO: I'd need to be able to refresh a property within a blender operator
        fileUtils.terminate_blender()
        return True


def get_valid_sc_path():
    """Attempts to get a valid source content path from the current environment, regardless of OS"""
    if filterUtils.filter_platform('win'):
        if os.path.exists(str(Path(addon.preference().environment.sc_path))):
            return str(Path(addon.preference().environment.sc_path))
        elif os.path.exists(str(Path(addon.preference().environment.sc_path_alternate))):
            return str(Path(addon.preference().environment.sc_path_alternate))
        else:
            return 'Path does not exist'
    elif filterUtils.filter_platform('mac'):
        if os.path.exists(str(Path(addon.preference().environment.sc_path_mac))):
            return str(Path(addon.preference().environment.sc_path_mac))
        elif os.path.exists(str(Path(addon.preference().environment.sc_path_mac_alternate))):
            return str(Path(addon.preference().environment.sc_path_mac_alternate))
        else:
            return 'Path does not exist'
    else:
        return 'Wrong OS is set! Go to envUtils2.py and fix if you want linux support'


def set_environment(env_name: str):
    msg = f'Setting Current Environment to: "{env_name}"'
    log(Severity.INFO, 'envUtils2', msg)
    addon.preference().environment.active_environment = env_name


def get_environment() -> str:
    current_env = addon.preference().environment.active_environment
    msg = f'Fetching current environment name from preferences: "{current_env}"'
    log(Severity.INFO, 'get_environment', msg)
    return current_env

