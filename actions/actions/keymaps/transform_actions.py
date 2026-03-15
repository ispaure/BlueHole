"""
Transform keymap operator actions for Blue Hole.
Acts as the public entry point for all Transform-related keymap actions.
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

from .transform import get_all_transform_actions

# ----------------------------------------------------------------------------------------------------------------------
# PUBLIC API


def get_transform_actions():
    """
    Return all UV OperatorAction objects.
    """
    return get_all_transform_actions()


UV_ACTIONS = get_transform_actions()
