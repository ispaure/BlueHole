"""
Registration and runtime management for Blue Hole navigation keymaps.
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

from .keymap_utils import get_addon_keyconfig
from ..actions.operator_action import register_operator_action_keymaps, remove_matching_action_kmis

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# RUNTIME STORAGE

registered_navigation_keymaps = []

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
