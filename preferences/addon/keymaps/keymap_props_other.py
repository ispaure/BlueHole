"""Preferences for editor and global shortcuts in Other."""

import bpy
from bpy.props import BoolProperty

from ....actions.actions.keymaps.other_actions import OTHER_ACTIONS
from .keymap_props_modeling_ui import draw_modeling_keymaps


def _update_keymaps(self, context):
    from ....keymaps import keymaps_register
    keymaps_register.refresh()


class OtherKeymapPG(bpy.types.PropertyGroup):

    enable_other_keymaps: BoolProperty(
        name='Enable Other Keymaps',
        description='Enable additional editor and global shortcuts',
        default=True,
        update=_update_keymaps,
    )


def draw(preference, context, layout):
    draw_modeling_keymaps(layout.column(), preference.keymap.other,
                          'enable_other_keymaps', reversed(OTHER_ACTIONS))
