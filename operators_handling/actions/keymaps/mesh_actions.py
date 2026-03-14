"""
Mesh keymap operator actions for Blue Hole.
Acts as the public entry point for all mesh-related keymap actions.
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

from .mesh import get_all_mesh_actions

# ----------------------------------------------------------------------------------------------------------------------
# PUBLIC API


def get_mesh_actions():
    """
    Return all mesh OperatorAction objects.
    """
    return get_all_mesh_actions()


MESH_ACTIONS = get_mesh_actions()
