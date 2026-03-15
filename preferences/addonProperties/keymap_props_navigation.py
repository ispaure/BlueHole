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

    enable_navigation_view_framing: BoolProperty(
        name='Enable View Framing Shortcuts',
        description='Enable Blue Hole view framing shortcuts',
        default=True,
        # update=_update_enable_navigation_view_framing
    )

    active_navigation_keymap_tab: EnumProperty(
        name='Navigation Keymap Tab',
        description='Active navigation keymap feature tab',
        items=[
            ('VIEWPORT', 'Viewport', ''),
            ('VIEW_FRAMING', 'View Framing', ''),
        ],
        default='VIEWPORT'
    )


def _draw_navigation_tab_buttons(column, preference):
    """
    Draw the navigation feature tab buttons.
    """
    row = column.row(align=True)

    current_tab = preference.keymap.navigation.active_navigation_keymap_tab

    op = row.operator(
        "wm.bh_set_active_prefs_tab",
        text="Viewport",
        depress=(current_tab == 'VIEWPORT')
    )
    op.prop_path = "keymap.navigation.active_navigation_keymap_tab"
    op.tab = "VIEWPORT"

    op = row.operator(
        "wm.bh_set_active_prefs_tab",
        text="View Framing",
        depress=(current_tab == 'VIEW_FRAMING')
    )
    op.prop_path = "keymap.navigation.active_navigation_keymap_tab"
    op.tab = "VIEW_FRAMING"


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

    _draw_navigation_tab_buttons(column_navigation, preference)

    if preference.keymap.navigation.active_navigation_keymap_tab == 'VIEWPORT':
        row = column_navigation.row()
        row.prop(preference.keymap.navigation, 'enable_navigation_viewport_shortcuts')

    elif preference.keymap.navigation.active_navigation_keymap_tab == 'VIEW_FRAMING':
        row = column_navigation.row()
        row.prop(preference.keymap.navigation, 'enable_navigation_view_framing')

    row = column_navigation.row()
    row.label(text='Navigation keymap settings will appear here.')
