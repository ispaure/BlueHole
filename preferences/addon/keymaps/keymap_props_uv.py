"""
UV keymap preferences for Blue Hole.
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

from ....actions.actions.keymaps.uv import UV_KEYMAP_GROUPS, get_uv_group_actions
from .keymap_props_modeling_ui import draw_modeling_keymaps


def _update_keymaps(self, context):
    from ....keymaps import keymaps_register
    keymaps_register.refresh()


class UVKeymapPG(bpy.types.PropertyGroup):

    enable_uv_keymaps: BoolProperty(
        name='Enable UV Keymaps',
        description='Enable Blue Hole UV keymaps',
        default=True,
        update=_update_keymaps,
    )

    enable_uv_selection_shortcuts: BoolProperty(
        name='Enable UV Selection Shortcuts',
        description='Use UV loop, linked and Tweak selection shortcuts',
        default=True,
        update=_update_keymaps,
    )

    enable_uv_tool_shortcuts: BoolProperty(
        name='Enable UV Tool Shortcuts',
        description='Use UV Box tool and cursor shortcuts',
        default=True,
        update=_update_keymaps,
    )

    enable_uv_action_shortcuts: BoolProperty(
        name='Enable UV Action Shortcuts',
        description='Use UV hide and fit shortcuts',
        default=True,
        update=_update_keymaps,
    )


def draw(preference, context, layout):
    preferences = preference.keymap.uv
    column = layout.column()
    column.prop(preferences, 'enable_uv_keymaps')
    if not preferences.enable_uv_keymaps:
        return

    for group, toggle in UV_KEYMAP_GROUPS.items():
        draw_modeling_keymaps(column, preferences, toggle, get_uv_group_actions(group))
