"""
Registration and runtime management for Blue Hole mesh keymaps.
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

from .keymap_action_utils import ensure_action_keymaps
from .keymap_utils import drain_legacy
from ..actions.actions.keymaps.mesh import get_enabled_mesh_catalog
from ..preferences.prefs import prefs

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

KEYMAP_CATEGORY = 'Mesh'

# ----------------------------------------------------------------------------------------------------------------------
# RUNTIME STORAGE

registered_mesh_keymaps = []

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def get_enabled_mesh_actions():
    """
    Return the list of mesh actions that should currently be registered.
    """
    preferences = prefs().keymap
    if not preferences.enable_keymaps or not preferences.mesh.enable_mesh_keymaps:
        return []
    return get_enabled_mesh_catalog(preferences.mesh)


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register() -> int:
    unregister()

    actions = get_enabled_mesh_actions()

    registered_count = 0

    for action in actions:
        new_keymaps = ensure_action_keymaps(KEYMAP_CATEGORY, action)
        registered_mesh_keymaps.extend(new_keymaps)
        registered_count += len(new_keymaps)

    return registered_count


def unregister() -> int:
    unregistered_count = len(registered_mesh_keymaps)
    drain_legacy(KEYMAP_CATEGORY)
    registered_mesh_keymaps.clear()
    return unregistered_count
