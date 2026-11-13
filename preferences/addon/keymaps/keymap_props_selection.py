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

from ....blenderUtils.operatorUtils import op_exists
from ....actions.actions.keymaps.selection.selection_more_less import get_selection_more_less_actions
from ....actions.actions.keymaps.selection.selection_tool_switch import get_selection_tool_switch_actions
from ....actions.actions.keymaps.selection.selection_all_none import get_selection_all_none_actions
from ....actions.actions.keymaps.selection.selection_circle import get_selection_circle_actions
from ....actions.actions.keymaps.selection.selection_subtract import get_selection_subtract_actions
from ....actions.actions.keymaps.selection.selection_extend import get_selection_extend_actions
from .keymap_ui_utils import draw_action_feature_keymaps

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def _update_keymaps(self, context):
    from ....keymaps import keymaps_register
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
        description='"Select Less / More"',
        default=True,
        update=_update_keymaps
    )

    enable_selection_tool_switch: BoolProperty(
        name='Enable Selection Tool Switch',
        description='"Selection Tool Switch"',
        default=True,
        update=_update_keymaps
    )

    enable_selection_all_none: BoolProperty(
        name='Enable Select All / None',
        description='Enable shortcuts to select or deselect all UVs',
        default=True,
        update=_update_keymaps
    )

    enable_selection_circle: BoolProperty(
        name='Enable Circle Selection',
        description='Enable Circle Selection shortcuts in the 3D View and UV Editor',
        default=True,
        update=_update_keymaps
    )

    enable_selection_subtract: BoolProperty(
        name='Enable Subtract Selection',
        description='Ctrl-click to remove an item from the selection',
        default=True,
        update=_update_keymaps
    )

    enable_selection_extend: BoolProperty(
        name='Enable Extend Selection',
        description='Add items to the selection by their centers',
        default=True,
        update=_update_keymaps
    )

    active_selection_keymap_tab: EnumProperty(
        name='Selection Keymap Tab',
        description='Active selection keymap feature tab',
        items=[
            ('MORE_LESS', 'Select Less / More', ''),
            ('TOOL_SWITCH', 'Tool Switch', ''),
            ('ALL_NONE', 'Select All / None', ''),
            ('CIRCLE', 'Circle Selection', ''),
            ('SUBTRACT', 'Subtract Selection', ''),
            ('EXTEND', 'Extend Selection', ''),
        ],
        default='MORE_LESS'
    )


def draw(preference, context, layout):
    # -------------------------------------------------------------------------------------------------
    # SELECTION KEYMAPS
    # -------------------------------------------------------------------------------------------------
    column_selection = layout.column()

    row = column_selection.row()
    row.prop(preference.keymap.selection, 'enable_selection_keymaps')

    if not preference.keymap.selection.enable_selection_keymaps:
        row = column_selection.row()
        row.label(text='Selection keymaps are currently disabled.')
        return

    row = column_selection.row()
    row.prop(preference.keymap.selection, 'active_selection_keymap_tab', expand=True)

    if preference.keymap.selection.active_selection_keymap_tab == 'MORE_LESS':
        draw_action_feature_keymaps(
            column=column_selection,
            feature_owner=preference.keymap.selection,
            feature_prop_name='enable_selection_more_less',
            actions=get_selection_more_less_actions(),
        )

    elif preference.keymap.selection.active_selection_keymap_tab == 'TOOL_SWITCH':
        draw_action_feature_keymaps(
            column=column_selection,
            feature_owner=preference.keymap.selection,
            feature_prop_name='enable_selection_tool_switch',
            actions=get_selection_tool_switch_actions(),
        )

    elif preference.keymap.selection.active_selection_keymap_tab == 'ALL_NONE':
        draw_action_feature_keymaps(
            column=column_selection,
            feature_owner=preference.keymap.selection,
            feature_prop_name='enable_selection_all_none',
            actions=get_selection_all_none_actions(),
        )

    elif preference.keymap.selection.active_selection_keymap_tab == 'CIRCLE':
        draw_action_feature_keymaps(
            column=column_selection,
            feature_owner=preference.keymap.selection,
            feature_prop_name='enable_selection_circle',
            actions=get_selection_circle_actions(),
        )

    elif preference.keymap.selection.active_selection_keymap_tab == 'SUBTRACT':
        draw_action_feature_keymaps(
            column=column_selection,
            feature_owner=preference.keymap.selection,
            feature_prop_name='enable_selection_subtract',
            actions=get_selection_subtract_actions(),
        )

    elif preference.keymap.selection.active_selection_keymap_tab == 'EXTEND':
        draw_action_feature_keymaps(
            column=column_selection,
            feature_owner=preference.keymap.selection,
            feature_prop_name='enable_selection_extend',
            actions=get_selection_extend_actions(),
        )
