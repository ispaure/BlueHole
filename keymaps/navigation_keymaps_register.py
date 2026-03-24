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

from .keymap_action_utils import ensure_action_keymaps
from ..actions.operator_action import unregister_registered_keymaps
from ..actions.actions.keymaps.navigation.viewport_movement import get_navigation_viewport_movement_actions
from ..actions.actions.keymaps.navigation.viewport_axis import get_navigation_viewport_axis_actions
from ..preferences.prefs import prefs

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

KEYMAP_CATEGORY = 'Navigation'

# ----------------------------------------------------------------------------------------------------------------------
# RUNTIME STORAGE

registered_navigation_keymaps = []

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def get_enabled_navigation_actions():
    """
    Return the list of navigation actions that should currently be registered.
    """
    actions = []

    if not prefs().keymap.enable_keymaps:
        return actions

    if not prefs().keymap.navigation.enable_navigation_keymaps:
        return actions

    if prefs().keymap.navigation.enable_navigation_viewport_movement:
        actions.extend(get_navigation_viewport_movement_actions())

    if prefs().keymap.navigation.enable_navigation_viewport_axis:
        actions.extend(get_navigation_viewport_axis_actions())

    return actions


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register() -> int:
    unregister()

    actions = get_enabled_navigation_actions()

    registered_count = 0

    for action in actions:
        new_keymaps = ensure_action_keymaps(action)
        registered_navigation_keymaps.extend(new_keymaps)
        registered_count += len(new_keymaps)

    return registered_count


def unregister():
    unregister_registered_keymaps(registered_navigation_keymaps)
