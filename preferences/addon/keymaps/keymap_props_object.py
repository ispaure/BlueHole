"""
Object keymap preferences for Blue Hole.
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

from ....actions.actions.keymaps.object import OBJECT_KEYMAP_GROUPS, get_object_group_actions
from .keymap_props_modeling_ui import draw_modeling_keymaps


def _update_keymaps(self, context):
    from ....keymaps import keymaps_register
    keymaps_register.refresh()


class ObjectKeymapPG(bpy.types.PropertyGroup):

    enable_object_keymaps: BoolProperty(
        name='Enable Object Keymaps',
        description='Enable Blue Hole object keymaps',
        default=True,
        update=_update_keymaps,
    )

    enable_object_mode_shortcuts: BoolProperty(
        name='Enable Mode Switching',
        description='Switch object and edit modes',
        default=True,
        update=_update_keymaps,
    )

    enable_object_action_shortcuts: BoolProperty(
        name='Enable Object Actions',
        description='Use object shortcuts such as Delete and Join Groups',
        default=True,
        update=_update_keymaps,
    )

    # Retain the saved IDs of the original placeholder groups.
    enable_object_selection_shortcuts: BoolProperty(default=True)
    enable_object_tool_shortcuts: BoolProperty(default=True)


def draw(preference, context, layout):
    preferences = preference.keymap.object
    column = layout.column()
    column.prop(preferences, 'enable_object_keymaps')
    if not preferences.enable_object_keymaps:
        return

    for group, toggle in OBJECT_KEYMAP_GROUPS.items():
        draw_modeling_keymaps(column, preferences, toggle, get_object_group_actions(group))
