"""Register Other shortcuts in their declared Blender maps."""

from .keymap_action_utils import ensure_action_keymaps
from ..actions.actions.keymaps.other_actions import OTHER_ACTIONS
from ..actions.operator_action import unregister_registered_keymaps
from ..preferences.prefs import prefs

KEYMAP_CATEGORY = 'Other'
registered_other_keymaps = []


def register():
    unregister()
    if prefs().keymap.other.enable_other_keymaps:
        for action in OTHER_ACTIONS:
            registered_other_keymaps.extend(ensure_action_keymaps(KEYMAP_CATEGORY, action))
    return len(registered_other_keymaps)


def unregister():
    count = len(registered_other_keymaps)
    unregister_registered_keymaps(registered_other_keymaps)
    return count
