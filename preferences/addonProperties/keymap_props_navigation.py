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

from ...actions.actions.keymaps.navigation.viewport_movement import get_navigation_viewport_movement_actions
from ...actions.actions.keymaps.navigation.viewport_axis import get_navigation_viewport_axis_actions
from .keymap_ui_utils import draw_action_feature_keymaps

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def _update_keymaps(self, context):
    from ...keymaps import keymaps_register
    keymaps_register.refresh()


class NavigationKeymapPG(bpy.types.PropertyGroup):

    enable_navigation_keymaps: BoolProperty(
        name='Enable Navigation Keymaps',
        description='Enable Blue Hole navigation keymaps',
        default=True,
        update=_update_keymaps
    )

    enable_navigation_viewport_movement: BoolProperty(
        name='Enable Viewport Movement',
        description='"Viewport Movement"',
        default=True,
        update=_update_keymaps
    )

    enable_navigation_viewport_axis: BoolProperty(
        name='Enable View Axis',
        description='"View Axis"',
        default=True,
        update=_update_keymaps
    )

    enable_navigation_view_framing: BoolProperty(
        name='Enable View Framing',
        description='"View Framing"',
        default=True,
        update=_update_keymaps
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

    active_navigation_viewport_tab: EnumProperty(
        name='Viewport Keymap Tab',
        description='Active viewport navigation feature tab',
        items=[
            ('MOVEMENT', 'Movement', ''),
            ('AXIS', 'Axis', ''),
        ],
        default='MOVEMENT'
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
    row.prop(preference.keymap.navigation, 'active_navigation_keymap_tab', expand=True)

    if preference.keymap.navigation.active_navigation_keymap_tab == 'VIEWPORT':

        row = column_navigation.row()
        row.prop(preference.keymap.navigation, 'active_navigation_viewport_tab', expand=True)

        if preference.keymap.navigation.active_navigation_viewport_tab == 'MOVEMENT':
            draw_action_feature_keymaps(
                column=column_navigation,
                feature_owner=preference.keymap.navigation,
                feature_prop_name='enable_navigation_viewport_movement',
                actions=get_navigation_viewport_movement_actions(),
            )

        elif preference.keymap.navigation.active_navigation_viewport_tab == 'AXIS':
            draw_action_feature_keymaps(
                column=column_navigation,
                feature_owner=preference.keymap.navigation,
                feature_prop_name='enable_navigation_viewport_axis',
                actions=get_navigation_viewport_axis_actions(),
            )

    elif preference.keymap.navigation.active_navigation_keymap_tab == 'VIEW_FRAMING':
        row = column_navigation.row()
        row.prop(preference.keymap.navigation, 'enable_navigation_view_framing')
