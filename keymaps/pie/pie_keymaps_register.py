"""
Registration and runtime management for Blue Hole pie menu keymaps.
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

from ..keymap_action_utils import ensure_action_keymaps
from ...actions.operator_action import unregister_registered_keymaps
from ...actions.actions.pie_actions import PIE_ACTIONS
from ...preferences.prefs import prefs

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

KEYMAP_CATEGORY = 'Pie'

# ----------------------------------------------------------------------------------------------------------------------
# RUNTIME STORAGE

registered_pie_keymaps = []

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register() -> int:
    unregister()

    if not prefs().pie.enable_pie_menus:
        return 0

    registered_count = 0

    for action in PIE_ACTIONS:
        new_keymaps = ensure_action_keymaps(KEYMAP_CATEGORY, action)
        registered_pie_keymaps.extend(new_keymaps)
        registered_count += len(new_keymaps)

    return registered_count


def unregister():
    unregister_registered_keymaps(registered_pie_keymaps)
