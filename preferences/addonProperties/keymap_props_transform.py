"""
Transform keymap preferences for Blue Hole.
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
from ...operators_handling.actions.keymaps.transform.transform_tools import get_transform_tools_actions
from .keymap_ui_utils import draw_action_feature_keymaps

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def _update_keymaps(self, context):
    from ...keymaps import keymaps_register
    keymaps_register.refresh()


class TransformKeymapPG(bpy.types.PropertyGroup):

    enable_transform_keymaps: BoolProperty(
        name='Enable Transform Keymaps',
        description='Enable Blue Hole transform keymaps',
        default=True,
        update=_update_keymaps
    )

    enable_transform_tool_shortcuts: BoolProperty(
        name='Enable Transform Tools (Translate, Rotate, Resize & Gizmo Equivalents)',
        description='Transform Tools',
        default=True,
        update=_update_keymaps
    )

    enable_transform_orientation_shortcuts: BoolProperty(
        name='Enable Transform Orientation Shortcuts',
        description='Enable Blue Hole transform orientation shortcuts',
        default=True,
        update=_update_keymaps
    )

    enable_transform_action_shortcuts: BoolProperty(
        name='Enable Transform Action Shortcuts',
        description='Enable Blue Hole transform action shortcuts',
        default=True,
        update=_update_keymaps
    )

    active_transform_keymap_tab: EnumProperty(
        name='Transform Keymap Tab',
        description='Active transform keymap feature tab',
        items=[
            ('TOOLS', 'Tools', ''),
            ('ORIENTATION', 'Orientation', ''),
            ('ACTIONS', 'Actions', ''),
        ],
        default='TOOLS'
    )


def _draw_transform_tab_buttons(column, preference):
    """
    Draw the transform feature tab buttons.
    """
    row = column.row(align=True)

    current_tab = preference.keymap.transform.active_transform_keymap_tab

    op = row.operator(
        "wm.bh_set_active_prefs_tab",
        text="Tools",
        depress=(current_tab == 'TOOLS')
    )
    op.prop_path = "keymap.transform.active_transform_keymap_tab"
    op.tab = "TOOLS"

    op = row.operator(
        "wm.bh_set_active_prefs_tab",
        text="Orientation",
        depress=(current_tab == 'ORIENTATION')
    )
    op.prop_path = "keymap.transform.active_transform_keymap_tab"
    op.tab = "ORIENTATION"

    op = row.operator(
        "wm.bh_set_active_prefs_tab",
        text="Actions",
        depress=(current_tab == 'ACTIONS')
    )
    op.prop_path = "keymap.transform.active_transform_keymap_tab"
    op.tab = "ACTIONS"


def draw(preference, context, layout):
    # -------------------------------------------------------------------------------------------------
    # TRANSFORM KEYMAPS
    # -------------------------------------------------------------------------------------------------
    box_transform = layout.box()
    column_transform = box_transform.column()

    row = column_transform.row()
    row.prop(preference.keymap.transform, 'enable_transform_keymaps')

    if not preference.keymap.transform.enable_transform_keymaps:
        row = column_transform.row()
        row.label(text='Transform keymaps are currently disabled.')
        return

    _draw_transform_tab_buttons(column_transform, preference)

    if preference.keymap.transform.active_transform_keymap_tab == 'TOOLS':
        draw_action_feature_keymaps(
            column=column_transform,
            feature_owner=preference.keymap.transform,
            feature_prop_name='enable_transform_tool_shortcuts',
            actions=get_transform_tools_actions(),
        )

    elif preference.keymap.transform.active_transform_keymap_tab == 'ORIENTATION':
        row = column_transform.row()
        row.prop(preference.keymap.transform, 'enable_transform_orientation_shortcuts')

    elif preference.keymap.transform.active_transform_keymap_tab == 'ACTIONS':
        row = column_transform.row()
        row.prop(preference.keymap.transform, 'enable_transform_action_shortcuts')
