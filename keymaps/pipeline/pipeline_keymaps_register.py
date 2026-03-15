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

from ...Lib.commonUtils.debugUtils import *
from ..keymap_action_utils import ensure_action_keymaps
from ...operators_handling.operator_action import unregister_registered_keymaps
from ...operators_handling.actions.keymaps.pipeline_actions import get_pipeline_actions
from ...preferences.prefs import prefs

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

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

    if not prefs().keymap.pipeline.enable_pipeline_keymaps:
        return actions

    actions.extend(get_pipeline_actions())
    return actions


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
    unregister()

    actions = get_enabled_pipeline_actions()
    if not actions:
        return

    log(Severity.INFO, 'Blue Hole Pipeline Keymaps', 'Registering pipeline keymaps...')

    for action in actions:
        registered_pipeline_keymaps.extend(ensure_action_keymaps(action))

    log(Severity.INFO, 'Blue Hole Pipeline Keymaps', 'Registering pipeline keymaps completed!')


def unregister():
    unregister_registered_keymaps(registered_pipeline_keymaps)
