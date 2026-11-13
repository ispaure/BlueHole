"""
Selection keymap action modules.
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

from .selection_more_less import SELECTION_MORE_LESS_ACTIONS
from .selection_all_none import SELECTION_ALL_NONE_ACTIONS
from .selection_circle import SELECTION_CIRCLE_ACTIONS
from .selection_subtract import SELECTION_SUBTRACT_ACTIONS

# ----------------------------------------------------------------------------------------------------------------------
# ACTION GROUPS

_SELECTION_ACTIONS = (
    *SELECTION_MORE_LESS_ACTIONS,
    *SELECTION_ALL_NONE_ACTIONS,
    *SELECTION_CIRCLE_ACTIONS,
    *SELECTION_SUBTRACT_ACTIONS,
)

# ----------------------------------------------------------------------------------------------------------------------
# PUBLIC API


def get_all_selection_actions():
    """
    Return all selection-related OperatorAction objects.
    """
    return _SELECTION_ACTIONS
