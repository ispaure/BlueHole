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
from ..actions.actions.keymaps.pipeline import get_enabled_pipeline_catalog
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
    # Always include obligatory pipeline actions (e.g. custom Save As...)
    actions = []

    settings = prefs().keymap
    if settings.enable_keymaps and settings.pipeline.enable_pipeline_keymaps:
        actions.extend(get_enabled_pipeline_catalog(settings.pipeline))
    actions.extend(get_obligatory_pipeline_actions())
    return actions


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register() -> int:
    return _register_actions(get_enabled_pipeline_actions())


def register_required() -> int:
    return _register_actions(get_obligatory_pipeline_actions())


def _register_actions(actions) -> int:
    unregister()
    registered_count = 0

    for action in actions:
        new_keymaps = ensure_action_keymaps(KEYMAP_CATEGORY, action)
        registered_pipeline_keymaps.extend(new_keymaps)
        registered_count += len(new_keymaps)

    return registered_count


def unregister() -> int:
    unregistered_count = len(registered_pipeline_keymaps)
    unregister_registered_keymaps(registered_pipeline_keymaps)
    return unregistered_count
