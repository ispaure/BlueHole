"""
Pipeline keymap operator actions for Blue Hole.
Acts as the public entry point for all pipeline-related keymap actions.
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

from .pipeline import get_all_pipeline_actions

# ----------------------------------------------------------------------------------------------------------------------
# PUBLIC API


def get_pipeline_actions():
    """
    Return all pipeline OperatorAction objects.
    """
    return get_all_pipeline_actions()


PIPELINE_ACTIONS = get_pipeline_actions()
