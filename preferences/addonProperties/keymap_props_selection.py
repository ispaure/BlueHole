"""
Selection keymap preferences for Blue Hole.
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
import bpy

from bpy.props import *

from ...operators_handling.actions.keymaps.selection.selection_more_less import get_selection_more_less_actions
from bpy.props import *
from .keymap_ui_utils import draw_action_feature_keymaps

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def _update_keymaps(self, context):
    from ...keymaps import keymaps_register
    keymaps_register.refresh()


class SelectionKeymapPG(bpy.types.PropertyGroup):

    enable_selection_keymaps: BoolProperty(
        name='Enable Selection Keymaps',
        description='Enable Blue Hole selection keymaps',
        default=True,
        update=_update_keymaps
    )

    enable_selection_more_less: BoolProperty(
        name='Enable Select Less / More',
        description='Enable Blue Hole "Select Less / More" shortcuts',
        default=True,
        update=_update_keymaps
    )


def draw(preference, context, layout):
    # -------------------------------------------------------------------------------------------------
    # SELECTION KEYMAPS
    # -------------------------------------------------------------------------------------------------
    box_selection = layout.box()
    column_selection = box_selection.column()

    row = column_selection.row()
    row.prop(preference.keymap.selection, 'enable_selection_keymaps')

    if not preference.keymap.selection.enable_selection_keymaps:
        row = column_selection.row()
        row.label(text='Selection keymaps are currently disabled.')
        return

    draw_action_feature_keymaps(
        column=column_selection,
        feature_owner=preference.keymap.selection,
        feature_prop_name='enable_selection_more_less',
        actions=get_selection_more_less_actions(),
    )
