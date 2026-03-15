"""
Registration and runtime management for Blue Hole UV keymaps.
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
from ..actions.actions.keymaps.uv_actions import get_uv_actions
from ..preferences.prefs import prefs

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# RUNTIME STORAGE

registered_uv_keymaps = []

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def get_enabled_uv_actions():
    """
    Return the list of UV actions that should currently be registered.
    """
    actions = []

    if not prefs().keymap.uv.enable_uv_keymaps:
        return actions

    actions.extend(get_uv_actions())
    return actions


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
    unregister()

    actions = get_enabled_uv_actions()
    if not actions:
        return

    log(Severity.INFO, 'Blue Hole UV Keymaps', 'Registering UV keymaps...')

    for action in actions:
        registered_uv_keymaps.extend(ensure_action_keymaps(action))

    log(Severity.INFO, 'Blue Hole UV Keymaps', 'Registering UV keymaps completed!')


def unregister():
    unregister_registered_keymaps(registered_uv_keymaps)
