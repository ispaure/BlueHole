"""
Selection keymap operator actions for Blue Hole.
Acts as the public entry point for all selection-related keymap actions.
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

from .selection import get_all_selection_actions

# ----------------------------------------------------------------------------------------------------------------------
# PUBLIC API


def get_selection_actions():
    """
    Return all selection OperatorAction objects.
    """
    return get_all_selection_actions()


SELECTION_ACTIONS = get_selection_actions()
