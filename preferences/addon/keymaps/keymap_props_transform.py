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

from ....actions.actions.keymaps.transform.transform_tools_modal import get_transform_tools_modal_actions
from ....actions.actions.keymaps.transform.transform_tools_gizmo import get_transform_tools_gizmo_actions
from .keymap_ui_utils import draw_action_feature_keymaps
from ....blenderUtils.operatorUtils import op_exists

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

    enable_transform_tools_modal: BoolProperty(
        name='Enable Transform Tools (Modal)',
        description='Transform Tools (Modal)',
        default=True,
        update=_update_keymaps
    )

    enable_transform_tools_modal_autoconstraint: BoolProperty(
        name='Enable autoConstraints whilst using Transform Modals in 3D View (Requires "autoConstraints" add-on)',
        description='Turns on AutoConstraint whilst using Transform Modals in 3D View (Requires "autoConstraints" add-on)',
        default=True
    )

    enable_transform_tools_gizmo: BoolProperty(
        name='Enable Transform Tools (Gizmo)',
        description='Transform Tools (Gizmo)',
        default=True,
        update=_update_keymaps
    )

    enable_transform_orientation_shortcuts: BoolProperty(
        name='Enable Transform Orientation',
        description='Transform Orientation',
        default=True,
        update=_update_keymaps
    )

    enable_transform_action_shortcuts: BoolProperty(
        name='Enable Transform Actions',
        description='Transform Actions',
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

    active_transform_tools_tab: EnumProperty(
        name='Transform Tools Tab',
        description='Active transform tools feature tab',
        items=[
            ('MODAL', 'Modal', ''),
            ('GIZMO', 'Gizmo', ''),
        ],
        default='MODAL'
    )


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

    row = column_transform.row()
    row.prop(preference.keymap.transform, 'active_transform_keymap_tab', expand=True)

    if preference.keymap.transform.active_transform_keymap_tab == 'TOOLS':

        row = column_transform.row()
        row.prop(preference.keymap.transform, 'active_transform_tools_tab', expand=True)

        if preference.keymap.transform.active_transform_tools_tab == 'MODAL':
            draw_action_feature_keymaps(
                column=column_transform,
                feature_owner=preference.keymap.transform,
                feature_prop_name='enable_transform_tools_modal',
                actions=get_transform_tools_modal_actions(),
            )
            if preference.keymap.transform.enable_transform_tools_modal:
                row = column_transform.row()
                row.prop(preference.keymap.transform, 'enable_transform_tools_modal_autoconstraint', expand=True)
                row.enabled = op_exists('transform.translate_auto_constraint')

        elif preference.keymap.transform.active_transform_tools_tab == 'GIZMO':
            draw_action_feature_keymaps(
                column=column_transform,
                feature_owner=preference.keymap.transform,
                feature_prop_name='enable_transform_tools_gizmo',
                actions=get_transform_tools_gizmo_actions(),
            )

    elif preference.keymap.transform.active_transform_keymap_tab == 'ORIENTATION':
        row = column_transform.row()
        row.prop(preference.keymap.transform, 'enable_transform_orientation_shortcuts')

    elif preference.keymap.transform.active_transform_keymap_tab == 'ACTIONS':
        row = column_transform.row()
        row.prop(preference.keymap.transform, 'enable_transform_action_shortcuts')
