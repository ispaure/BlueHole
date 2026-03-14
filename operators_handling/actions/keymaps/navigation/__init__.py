"""
Navigation keymap action modules.
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

# ----------------------------------------------------------------------------------------------------------------------
# ACTION GROUPS

_NAVIGATION_ACTIONS = (
)

# ----------------------------------------------------------------------------------------------------------------------
# PUBLIC API


def get_all_navigation_actions():
    """
    Return all navigation-related OperatorAction objects.
    """
    return _NAVIGATION_ACTIONS
