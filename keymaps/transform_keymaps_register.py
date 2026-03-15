"""
Registration and runtime management for Blue Hole transform keymaps.
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

from ..Lib.commonUtils.debugUtils import *
from .keymap_action_utils import ensure_action_keymaps
from ..actions.operator_action import unregister_registered_keymaps
from ..actions.actions.keymaps.transform.transform_tools_gizmo import get_transform_tools_gizmo_actions
from ..actions.actions.keymaps.transform.transform_tools_modal import get_transform_tools_modal_actions
from ..preferences.prefs import prefs

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# RUNTIME STORAGE

registered_transform_keymaps = []

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def get_enabled_transform_actions():
    """
    Return the list of transform actions that should currently be registered.
    """
    actions = []

    if not prefs().keymap.enable_keymaps:
        return actions

    if not prefs().keymap.transform.enable_transform_keymaps:
        return actions

    if prefs().keymap.transform.enable_transform_tools_gizmo:
        actions.extend(get_transform_tools_gizmo_actions())

    if prefs().keymap.transform.enable_transform_tools_modal:
        actions.extend(get_transform_tools_modal_actions())

    return actions


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
    unregister()

    actions = get_enabled_transform_actions()
    if not actions:
        return

    log(Severity.INFO, 'Blue Hole transform Keymaps', 'Registering transform keymaps...')

    for action in actions:
        registered_transform_keymaps.extend(ensure_action_keymaps(action))

    log(Severity.INFO, 'Blue Hole transform Keymaps', 'Registering transform keymaps completed!')


def unregister():
    unregister_registered_keymaps(registered_transform_keymaps)
