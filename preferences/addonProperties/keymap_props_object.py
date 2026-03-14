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
from bpy.props import *

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def _update_enable_object_keymaps(self, context):
    """
    Enable or disable Blue Hole object keymaps.
    """
    # TODO: Replace with the real register module once it exists.
    # Example:
    # from ...keymaps.object import object_keymaps_register
    #
    # if self.enable_object_keymaps:
    #     object_keymaps_register.register()
    # else:
    #     object_keymaps_register.unregister()
    pass


class ObjectKeymapPG(bpy.types.PropertyGroup):

    enable_object_keymaps: BoolProperty(
        name='Enable Object Keymaps',
        description='Enable Blue Hole object keymaps',
        default=False,
        update=_update_enable_object_keymaps
    )

    enable_object_selection_shortcuts: BoolProperty(
        name='Enable Object Selection Shortcuts',
        description='Enable Blue Hole object selection shortcuts',
        default=False,
        # update=_update_enable_object_selection_shortcuts
    )

    enable_object_action_shortcuts: BoolProperty(
        name='Enable Object Action Shortcuts',
        description='Enable Blue Hole object action shortcuts',
        default=False,
        # update=_update_enable_object_action_shortcuts
    )

    enable_object_tool_shortcuts: BoolProperty(
        name='Enable Object Tool Shortcuts',
        description='Enable Blue Hole object tool shortcuts',
        default=False,
        # update=_update_enable_object_tool_shortcuts
    )


def draw(preference, context, layout):
    # -------------------------------------------------------------------------------------------------
    # OBJECT KEYMAPS
    # -------------------------------------------------------------------------------------------------
    box_object = layout.box()
    column_object = box_object.column()

    row = column_object.row()
    row.prop(preference.keymap.object, 'enable_object_keymaps')

    if not preference.keymap.object.enable_object_keymaps:
        row = column_object.row()
        row.label(text='Object keymaps are currently disabled.')
        return

    row = column_object.row()
    row.prop(preference.keymap.object, 'enable_object_selection_shortcuts')

    row = column_object.row()
    row.prop(preference.keymap.object, 'enable_object_action_shortcuts')

    row = column_object.row()
    row.prop(preference.keymap.object, 'enable_object_tool_shortcuts')

    row = column_object.row()
    row.label(text='Object keymap settings will appear here.')
