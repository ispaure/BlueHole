"""
Registration and runtime management for Blue Hole mesh keymaps.
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

from ...Lib.commonUtils.debugUtils import *
from ..keymap_utils import get_addon_keyconfig
from ...operators_handling.operator_action import (
    register_operator_action_keymaps,
    remove_matching_action_kmis,
    unregister_registered_keymaps,
)
from ...operators_handling.actions.keymaps.mesh_actions import get_mesh_actions
from ...preferences.prefs import prefs

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# RUNTIME STORAGE

registered_mesh_keymaps = []

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def remove_existing_action_keymaps_from_keyconfig(kc, action):
    """
    Remove existing keymap items for this action from the given keyconfig.
    """
    if kc is None:
        return

    for binding in action.keymap_bindings:
        km = kc.keymaps.get(binding.keymap_name)
        if km is None:
            continue

        remove_matching_action_kmis(km, action)


def ensure_action_keymaps(action):
    """
    Ensure all keymap bindings for this action exist in Blender's addon keyconfig.
    """
    if not action.keymap_bindings:
        return []

    kc = get_addon_keyconfig()
    if kc is None:
        return []

    remove_existing_action_keymaps_from_keyconfig(kc, action)
    return register_operator_action_keymaps(kc, action)


def get_enabled_mesh_actions():
    """
    Return the list of mesh actions that should currently be registered.
    """
    actions = []

    if not prefs().keymap.mesh.enable_mesh_keymaps:
        return actions

    actions.extend(get_mesh_actions())
    return actions


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
    unregister()

    actions = get_enabled_mesh_actions()
    if not actions:
        return

    log(Severity.INFO, 'Blue Hole Mesh Keymaps', 'Registering mesh keymaps...')

    for action in actions:
        registered_mesh_keymaps.extend(ensure_action_keymaps(action))

    log(Severity.INFO, 'Blue Hole Mesh Keymaps', 'Registering mesh keymaps completed!')


def unregister():
    unregister_registered_keymaps(registered_mesh_keymaps)
