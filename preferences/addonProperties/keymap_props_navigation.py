"""
Navigation keymap preferences for Blue Hole.
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


def _update_enable_navigation_keymaps(self, context):
    """
    Enable or disable Blue Hole navigation keymaps.
    """
    # TODO: Replace with the real register module once it exists.
    # Example:
    # from ...keymaps.navigation import navigation_keymaps_register
    #
    # if self.enable_navigation_keymaps:
    #     navigation_keymaps_register.register()
    # else:
    #     navigation_keymaps_register.unregister()
    pass


class NavigationKeymapPG(bpy.types.PropertyGroup):

    enable_navigation_keymaps: BoolProperty(
        name='Enable Navigation Keymaps',
        description='Enable Blue Hole navigation keymaps',
        default=True,
        update=_update_enable_navigation_keymaps
    )

    enable_navigation_viewport_shortcuts: BoolProperty(
        name='Enable Viewport Navigation Shortcuts',
        description='Enable Blue Hole viewport navigation shortcuts',
        default=True,
        # update=_update_enable_navigation_viewport_shortcuts
    )

    enable_navigation_selection_wheel: BoolProperty(
        name='Enable Selection Wheel Navigation',
        description='Enable Blue Hole wheel-based selection navigation shortcuts',
        default=True,
        # update=_update_enable_navigation_selection_wheel
    )


def draw(preference, context, layout):
    # -------------------------------------------------------------------------------------------------
    # NAVIGATION KEYMAPS
    # -------------------------------------------------------------------------------------------------
    box_navigation = layout.box()
    column_navigation = box_navigation.column()

    row = column_navigation.row()
    row.prop(preference.keymap.navigation, 'enable_navigation_keymaps')

    if not preference.keymap.navigation.enable_navigation_keymaps:
        row = column_navigation.row()
        row.label(text='Navigation keymaps are currently disabled.')
        return

    row = column_navigation.row()
    row.prop(preference.keymap.navigation, 'enable_navigation_viewport_shortcuts')

    row = column_navigation.row()
    row.prop(preference.keymap.navigation, 'enable_navigation_selection_wheel')

    row = column_navigation.row()
    row.label(text='Navigation keymap settings will appear here.')
