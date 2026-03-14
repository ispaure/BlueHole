"""
Shared UI helpers for displaying Blue Hole keymaps in addon preferences.
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
import rna_keymap_ui

from ...operators_handling.operator_action import OperatorAction
from ...keymaps.keymap_utils import get_keyconfig_sequence

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def group_actions_by_keymap(actions: list[OperatorAction]) -> dict[str, list[OperatorAction]]:
    """
    Group OperatorActions by keymap_name while preserving declaration order.
    """
    grouped: dict[str, list[OperatorAction]] = {}

    for action in actions:
        for binding in action.keymap_bindings:
            grouped.setdefault(binding.keymap_name, []).append(action)

    return grouped


# ----------------------------------------------------------------------------------------------------------------------


def find_action_keymap(
        action: OperatorAction,
        keymap_name: str | None = None,
        check_user: bool = True,
        check_addon: bool = True,
        check_default: bool = False
):
    """
    Find the real Blender keymap item for an OperatorAction.

    Returns:
        (kc, km, kmi) or (None, None, None)
    """

    keyconfigs_to_check = get_keyconfig_sequence(
        check_user=check_user,
        check_addon=check_addon,
        check_default=check_default,
    )

    preferred_keymap_names = []

    if keymap_name is not None:
        preferred_keymap_names.append(keymap_name)
    else:
        preferred_keymap_names.extend(binding.keymap_name for binding in action.keymap_bindings)

    action_idname = action.get_idname()
    action_props = action.get_props(None)

    for kc in keyconfigs_to_check:

        for km_name in preferred_keymap_names:
            km = kc.keymaps.get(km_name)
            if km is None:
                continue

            for kmi in km.keymap_items:

                if kmi.idname != action_idname:
                    continue

                matches = True

                for prop_name, prop_value in action_props.items():
                    if getattr(kmi.properties, prop_name, None) != prop_value:
                        matches = False
                        break

                if matches:
                    return kc, km, kmi

        for km in kc.keymaps:

            for kmi in km.keymap_items:

                if kmi.idname != action_idname:
                    continue

                matches = True

                for prop_name, prop_value in action_props.items():
                    if getattr(kmi.properties, prop_name, None) != prop_value:
                        matches = False
                        break

                if matches:
                    return kc, km, kmi

    return None, None, None


# ----------------------------------------------------------------------------------------------------------------------


def draw_action_keymap(column, action: OperatorAction, keymap_name: str, label: str | None = None):
    """
    Draw the real Blender keymap UI for an OperatorAction.
    """

    kc, km, kmi = find_action_keymap(action, keymap_name=keymap_name)

    if label is None:
        label = action.text or action.get_idname()

    if kc is None or km is None or kmi is None:
        row = column.row()
        row.label(text=f'{label}: shortcut not found.', icon='ERROR')
        return

    row = column.row()
    row.label(text=label)

    column.context_pointer_set('keymap', km)

    rna_keymap_ui.draw_kmi([], kc, km, kmi, column, 0)


def draw_action_feature_keymaps(
        column,
        feature_owner,
        feature_prop_name: str,
        actions: list[OperatorAction],
        label_fn=None,
):
    """
    Draw a keymap feature toggle and its grouped keymap entries.

    feature_owner:
        The PropertyGroup instance holding the BoolProperty.

    feature_prop_name:
        The BoolProperty name on feature_owner.

    actions:
        OperatorAction list to display.

    label_fn:
        Optional callable: fn(action) -> str
        If omitted, action.text or action.get_idname() is used.
    """
    row = column.row()
    row.prop(feature_owner, feature_prop_name)

    if not getattr(feature_owner, feature_prop_name):
        feature_label = feature_owner.bl_rna.properties[feature_prop_name].name
        row = column.row()
        row.label(text=f'{feature_label} shortcuts are currently disabled.')
        return

    row = column.row()
    row.label(text='Edit shortcut bindings here.')

    grouped_actions = group_actions_by_keymap(actions)

    for keymap_name, action_list in grouped_actions.items():

        box_section = column.box()
        column_section = box_section.column()

        row = column_section.row()
        row.label(text=keymap_name.upper())

        for action in action_list:
            resolved_label = label_fn(action) if label_fn is not None else (action.text or action.get_idname())

            draw_action_keymap(
                column_section,
                action=action,
                keymap_name=keymap_name,
                label=resolved_label
            )
