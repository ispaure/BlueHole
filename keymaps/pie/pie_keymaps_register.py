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

from ...Lib.commonUtils.debugUtils import *
from ..keymap_utils import get_addon_keyconfig
from ..keymap_action_utils import ensure_action_keymaps
from ...actions.operator_action import unregister_registered_keymaps
from ...actions.actions.pie_actions import PIE_ACTIONS
from ...preferences.prefs import prefs

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# RUNTIME STORAGE

registered_pie_keymaps = []

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
    unregister()

    if not prefs().pie.enable_pie_menus:
        return

    log(Severity.INFO, 'Blue Hole Pie Keymaps', 'Registering pie keymaps...')

    for action in PIE_ACTIONS:
        registered_pie_keymaps.extend(ensure_action_keymaps(action))

    log(Severity.INFO, 'Blue Hole Pie Keymaps', 'Registering pie keymaps completed!')


def unregister():
    unregister_registered_keymaps(registered_pie_keymaps)
