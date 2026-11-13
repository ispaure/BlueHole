"""
Mesh keymap preferences for Blue Hole.
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

import bpy
from bpy.props import BoolProperty

from ....actions.actions.keymaps.mesh import MESH_KEYMAP_GROUPS, get_mesh_group_actions
from .keymap_props_modeling_ui import draw_modeling_keymaps


def _update_keymaps(self, context):
    from ....keymaps import keymaps_register
    keymaps_register.refresh()


class MeshKeymapPG(bpy.types.PropertyGroup):

    enable_mesh_keymaps: BoolProperty(
        name='Enable Mesh Keymaps',
        description='Enable Blue Hole mesh keymaps',
        default=True,
        update=_update_keymaps,
    )

    enable_mesh_modeling_shortcuts: BoolProperty(
        name='Enable Modeling Shortcuts',
        description='Use mesh modeling shortcuts',
        default=True,
        update=_update_keymaps,
    )

    enable_mesh_tool_shortcuts: BoolProperty(
        name='Enable Mesh Tool Shortcuts',
        description='Use additional shortcuts in Edit Mesh tools',
        default=True,
        update=_update_keymaps,
    )

    # Selection More / Less is supplied by the Selection category.
    enable_mesh_selection_grow_shrink: BoolProperty(default=True)


def draw(preference, context, layout):
    preferences = preference.keymap.mesh
    column = layout.column()
    column.prop(preferences, 'enable_mesh_keymaps')
    if not preferences.enable_mesh_keymaps:
        return

    for group, toggle in MESH_KEYMAP_GROUPS.items():
        draw_modeling_keymaps(column, preferences, toggle, get_mesh_group_actions(group))
