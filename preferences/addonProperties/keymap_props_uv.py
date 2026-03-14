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
from bpy.props import *

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def _update_enable_uv_keymaps(self, context):
    """
    Enable or disable Blue Hole UV keymaps.
    """
    # TODO: Replace with the real register module once it exists.
    # Example:
    # from ...keymaps.uv import uv_keymaps_register
    #
    # if self.enable_uv_keymaps:
    #     uv_keymaps_register.register()
    # else:
    #     uv_keymaps_register.unregister()
    pass


class UVKeymapPG(bpy.types.PropertyGroup):

    enable_uv_keymaps: BoolProperty(
        name='Enable UV Keymaps',
        description='Enable Blue Hole UV keymaps',
        default=False,
        update=_update_enable_uv_keymaps
    )

    enable_uv_selection_shortcuts: BoolProperty(
        name='Enable UV Selection Shortcuts',
        description='Enable Blue Hole UV selection shortcuts',
        default=False,
        # update=_update_enable_uv_selection_shortcuts
    )

    enable_uv_tool_shortcuts: BoolProperty(
        name='Enable UV Tool Shortcuts',
        description='Enable Blue Hole UV tool shortcuts',
        default=False,
        # update=_update_enable_uv_tool_shortcuts
    )

    enable_uv_action_shortcuts: BoolProperty(
        name='Enable UV Action Shortcuts',
        description='Enable Blue Hole UV action shortcuts',
        default=False,
        # update=_update_enable_uv_action_shortcuts
    )


def draw(preference, context, layout):
    # -------------------------------------------------------------------------------------------------
    # UV KEYMAPS
    # -------------------------------------------------------------------------------------------------
    box_uv = layout.box()
    column_uv = box_uv.column()

    row = column_uv.row()
    row.prop(preference.keymap.uv, 'enable_uv_keymaps')

    if not preference.keymap.uv.enable_uv_keymaps:
        row = column_uv.row()
        row.label(text='UV keymaps are currently disabled.')
        return

    row = column_uv.row()
    row.prop(preference.keymap.uv, 'enable_uv_selection_shortcuts')

    row = column_uv.row()
    row.prop(preference.keymap.uv, 'enable_uv_tool_shortcuts')

    row = column_uv.row()
    row.prop(preference.keymap.uv, 'enable_uv_action_shortcuts')

    row = column_uv.row()
    row.label(text='UV keymap settings will appear here.')
