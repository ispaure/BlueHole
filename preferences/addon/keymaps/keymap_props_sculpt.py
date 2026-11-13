"""Preferences for Sculpt shortcuts."""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://github.com/ispaure/BlueHole

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

import bpy
from bpy.props import BoolProperty

from ....actions.actions.keymaps.sculpt import SCULPT_KEYMAP_GROUPS, get_sculpt_group_actions
from .keymap_props_modeling_ui import draw_modeling_keymaps


def _update_keymaps(self, context):
    from ....keymaps import keymaps_register
    keymaps_register.refresh()


class SculptKeymapPG(bpy.types.PropertyGroup):

    enable_sculpt_keymaps: BoolProperty(
        name='Enable Sculpt Keymaps',
        default=True,
        update=_update_keymaps,
    )
    enable_sculpt_tool_shortcuts: BoolProperty(
        name='Enable Sculpt Tool Shortcuts',
        default=True,
        update=_update_keymaps,
    )
    enable_sculpt_brush_controls: BoolProperty(
        name='Enable Brush Controls',
        default=True,
        update=_update_keymaps,
    )
    enable_sculpt_masking_shortcuts: BoolProperty(
        name='Enable Masking and Visibility',
        default=True,
        update=_update_keymaps,
    )
    enable_sculpt_action_shortcuts: BoolProperty(
        name='Enable Sculpt Actions',
        default=True,
        update=_update_keymaps,
    )

    # Preserve the saved ID of the former placeholder.
    enable_sculpt_simulation_shortcuts: BoolProperty(default=True)


def draw(preference, context, layout):
    settings = preference.keymap.sculpt
    column = layout.column()
    column.prop(settings, 'enable_sculpt_keymaps')
    if settings.enable_sculpt_keymaps:
        for group, toggle in SCULPT_KEYMAP_GROUPS.items():
            draw_modeling_keymaps(column, settings, toggle, get_sculpt_group_actions(group))
