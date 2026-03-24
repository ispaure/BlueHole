"""
Registration and runtime management for Blue Hole selection keymaps.
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
from ..actions.actions.keymaps.selection.selection_more_less import get_selection_more_less_actions
from ..actions.actions.keymaps.selection.selection_tool_switch import get_selection_tool_switch_actions
from ..preferences.prefs import prefs

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

KEYMAP_CATEGORY = 'Selection'

# ----------------------------------------------------------------------------------------------------------------------
# RUNTIME STORAGE

registered_selection_keymaps = []

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def get_enabled_selection_actions():
    """
    Return the list of selection actions that should currently be registered.
    """
    actions = []

    if not prefs().keymap.enable_keymaps:
        return actions

    if not prefs().keymap.selection.enable_selection_keymaps:
        return actions

    if prefs().keymap.selection.enable_selection_more_less:
        actions.extend(get_selection_more_less_actions())

    if prefs().keymap.selection.enable_selection_tool_switch:
        actions.extend(get_selection_tool_switch_actions())

    return actions


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register() -> int:
    unregister()

    actions = get_enabled_selection_actions()

    registered_count = 0

    for action in actions:
        new_keymaps = ensure_action_keymaps(action)
        registered_selection_keymaps.extend(new_keymaps)
        registered_count += len(new_keymaps)

    return registered_count


def unregister():
    unregister_registered_keymaps(registered_selection_keymaps)