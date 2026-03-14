"""
Sculpt keymap preferences for Blue Hole.
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


def _update_enable_sculpt_keymaps(self, context):
    """
    Enable or disable Blue Hole sculpt keymaps.
    """
    # TODO: Replace with the real register module once it exists.
    # Example:
    # from ...keymaps.sculpt import sculpt_keymaps_register
    #
    # if self.enable_sculpt_keymaps:
    #     sculpt_keymaps_register.register()
    # else:
    #     sculpt_keymaps_register.unregister()
    pass


class SculptKeymapPG(bpy.types.PropertyGroup):

    enable_sculpt_keymaps: BoolProperty(
        name='Enable Sculpt Keymaps',
        description='Enable Blue Hole sculpt keymaps',
        default=False,
        update=_update_enable_sculpt_keymaps
    )

    enable_sculpt_tool_shortcuts: BoolProperty(
        name='Enable Sculpt Tool Shortcuts',
        description='Enable Blue Hole sculpt tool shortcuts',
        default=False,
        # update=_update_enable_sculpt_tool_shortcuts
    )

    enable_sculpt_action_shortcuts: BoolProperty(
        name='Enable Sculpt Action Shortcuts',
        description='Enable Blue Hole sculpt action shortcuts',
        default=False,
        # update=_update_enable_sculpt_action_shortcuts
    )

    enable_sculpt_simulation_shortcuts: BoolProperty(
        name='Enable Sculpt Simulation Shortcuts',
        description='Enable Blue Hole sculpt simulation shortcuts',
        default=False,
        # update=_update_enable_sculpt_simulation_shortcuts
    )


def draw(preference, context, layout):
    # -------------------------------------------------------------------------------------------------
    # SCULPT KEYMAPS
    # -------------------------------------------------------------------------------------------------
    box_sculpt = layout.box()
    column_sculpt = box_sculpt.column()

    row = column_sculpt.row()
    row.prop(preference.keymap.sculpt, 'enable_sculpt_keymaps')

    if not preference.keymap.sculpt.enable_sculpt_keymaps:
        row = column_sculpt.row()
        row.label(text='Sculpt keymaps are currently disabled.')
        return

    row = column_sculpt.row()
    row.prop(preference.keymap.sculpt, 'enable_sculpt_tool_shortcuts')

    row = column_sculpt.row()
    row.prop(preference.keymap.sculpt, 'enable_sculpt_action_shortcuts')

    row = column_sculpt.row()
    row.prop(preference.keymap.sculpt, 'enable_sculpt_simulation_shortcuts')

    row = column_sculpt.row()
    row.label(text='Sculpt keymap settings will appear here.')
