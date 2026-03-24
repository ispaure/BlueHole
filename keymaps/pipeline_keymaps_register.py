"""
Registration and runtime management for Blue Hole pipeline keymaps.
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
from ..actions.actions.keymaps.pipeline_actions import get_pipeline_actions
from ..actions.actions.keymaps.pipeline.obligatory import get_obligatory_pipeline_actions
from ..preferences.prefs import prefs

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

KEYMAP_CATEGORY = 'Pipeline'

# ----------------------------------------------------------------------------------------------------------------------
# RUNTIME STORAGE

registered_pipeline_keymaps = []

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def get_enabled_pipeline_actions():
    """
    Return the list of pipeline actions that should currently be registered.
    """
    actions = []

    # Always include obligatory pipeline actions (e.g. custom Save As...)
    actions.extend(get_obligatory_pipeline_actions())

    if not prefs().keymap.enable_keymaps:
        return actions

    if not prefs().keymap.pipeline.enable_pipeline_keymaps:
        return actions

    actions.extend(get_pipeline_actions())
    return actions


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register() -> int:
    unregister()

    actions = get_enabled_pipeline_actions()

    registered_count = 0

    for action in actions:
        new_keymaps = ensure_action_keymaps(action)
        registered_pipeline_keymaps.extend(new_keymaps)
        registered_count += len(new_keymaps)

    return registered_count


def unregister():
    unregister_registered_keymaps(registered_pipeline_keymaps)
