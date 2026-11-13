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

from dataclasses import replace

from ..keymap_action_utils import ensure_action_keymaps
from .editor_actions import EDITOR_PIE_ACTIONS
from ...actions.operator_action import unregister_registered_keymaps
from ...actions.actions import pie_actions
from ...preferences.prefs import prefs

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

KEYMAP_CATEGORY = 'Pie'

# ----------------------------------------------------------------------------------------------------------------------
# RUNTIME STORAGE

registered_pie_keymaps = []

# These Blue Hole routes survive in the full merged reference. The ordinary
# Pie switch still offers the complete Blue Hole defaults outside Deluxe.
_REFERENCE_PIE_ACTIONS = (
    replace(pie_actions.PIE_GLOBAL_IMPORT_EXPORT, keymap_bindings=tuple(
        binding for binding in pie_actions.PIE_GLOBAL_IMPORT_EXPORT.keymap_bindings
        if binding.keymap_name == 'Window'
    )),
    pie_actions.PIE_GLOBAL_DIRS,
    pie_actions.PIE_GLOBAL_HELP,
    pie_actions.PIE_SCULPT_SIMULATION,
    pie_actions.PIE_SCULPT_ACTION,
    pie_actions.PIE_SCULPT_TOOL,
    pie_actions.PIE_ADD,
    pie_actions.PIE_UV_ACTION_UVSPECIAL,
    pie_actions.PIE_UV_ACTION,
    pie_actions.PIE_UV_TOOL,
    pie_actions.PIE_UV_CURSOR,
)


def get_blue_hole_pie_actions(deluxe_keymaps_enabled):
    return _REFERENCE_PIE_ACTIONS if deluxe_keymaps_enabled else pie_actions.PIE_ACTIONS

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def get_enabled_pie_actions():
    settings = prefs().pie
    if not settings.enable_pie_menus:
        return ()
    deluxe_keymaps_enabled = prefs().keymap.enable_keymaps
    actions = get_blue_hole_pie_actions(deluxe_keymaps_enabled)
    if deluxe_keymaps_enabled:
        # The source map is prepended in reverse order during merge.
        actions = tuple(reversed(actions))
    if deluxe_keymaps_enabled and settings.enable_editor_pie_shortcuts:
        actions = (*EDITOR_PIE_ACTIONS, *actions)
    return actions


def register() -> int:
    unregister()
    registered_count = 0

    for action in get_enabled_pie_actions():
        new_keymaps = ensure_action_keymaps(KEYMAP_CATEGORY, action)
        registered_pie_keymaps.extend(new_keymaps)
        registered_count += len(new_keymaps)

    return registered_count


def unregister() -> int:
    unregistered_count = len(registered_pie_keymaps)
    unregister_registered_keymaps(registered_pie_keymaps)
    return unregistered_count
