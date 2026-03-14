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
from bpy.props import *

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
        name='Enable More / Less Selection',
        description='Enable Blue Hole "Select More/Less" shortcuts',
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

    row = column_selection.row()
    row.prop(preference.keymap.selection, 'enable_selection_more_less')

    row = column_selection.row()
    row.label(text='Selection keymap settings will appear here.')
