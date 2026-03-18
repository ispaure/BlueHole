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

from ....actions.operator_action import OperatorAction
from ....keymaps.keymap_utils import get_keyconfig_sequence
from ....operators.ui_ops import WM_OT_BH_ToggleUISection, draw_action_feature_keymaps_dropdown_state

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def group_action_bindings_by_keymap(actions: list[OperatorAction]) -> dict[str, list[tuple[OperatorAction, int]]]:
    """
    Group declared OperatorAction bindings by keymap_name while preserving declaration order.

    Returns:
        dict[keymap_name, list[(action, binding_index)]]
    """
    grouped: dict[str, list[tuple[OperatorAction, int]]] = {}

    for action in actions:
        for binding_index, binding in enumerate(action.keymap_bindings):
            grouped.setdefault(binding.keymap_name, []).append((action, binding_index))

    return grouped


# ----------------------------------------------------------------------------------------------------------------------


def find_action_keymap_items(
        action: OperatorAction,
        keymap_name: str | None = None,
        check_user: bool = True,
        check_addon: bool = True,
        check_default: bool = False
) -> list[tuple]:
    """
    Find all real Blender keymap items for an OperatorAction.

    Returns:
        list[(kc, km, kmi)]
    """
    results = []

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
                    results.append((kc, km, kmi))

    return results


# ----------------------------------------------------------------------------------------------------------------------


def draw_action_binding_keymap(
        column,
        action: OperatorAction,
        keymap_name: str,
        binding_index: int,
        label: str | None = None
):
    """
    Draw the real Blender keymap UI for one declared binding slot of an OperatorAction.

    Matching is based on:
    - action operator idname
    - action properties
    - keymap name

    Then the binding_index selects which matching keymap item to draw.
    This allows edited user bindings to still display correctly without requiring
    the original declared key / modifier values to remain unchanged.
    """
    matches = find_action_keymap_items(action, keymap_name=keymap_name, check_user=False, check_default=False)

    if label is None:
        label = action.text or action.get_idname()

    if binding_index >= len(matches):
        row = column.row()
        row.label(text=f'{label}: shortcut not found.', icon='ERROR')
        return

    kc, km, kmi = matches[binding_index]

    row = column.row()
    row.label(text=label)

    column.context_pointer_set('keymap', km)
    rna_keymap_ui.draw_kmi([], kc, km, kmi, column, 0)


# ----------------------------------------------------------------------------------------------------------------------


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
        # Display warning if deactivated, I don't want that.
        # feature_label = feature_owner.bl_rna.properties[feature_prop_name].description
        # row = column.row()
        # row.label(text=f'{feature_label} shortcuts are currently disabled.', icon='ERROR')
        return

    dropdown_key = f'{type(feature_owner).__name__}.{feature_prop_name}'
    is_expanded = draw_action_feature_keymaps_dropdown_state.get(dropdown_key, False)

    box_toggle = column.box()
    column_toggle = box_toggle.column()

    row = column_toggle.row()
    icon = 'TRIA_DOWN' if is_expanded else 'TRIA_RIGHT'

    op = row.operator(
        WM_OT_BH_ToggleUISection.bl_idname,
        text='See Bindings',
        icon=icon,
        emboss=False
    )

    op.section_key = dropdown_key

    if not is_expanded:
        return

    row = column_toggle.row()
    row.label(text='View shortcut bindings here. Custom edits are not yet persistent.')

    grouped_action_bindings = group_action_bindings_by_keymap(actions)

    for keymap_name, action_binding_list in grouped_action_bindings.items():

        box_section = column_toggle.box()
        column_section = box_section.column()

        row = column_section.row()
        row.label(text=keymap_name.upper())

        for action, binding_index in action_binding_list:
            resolved_label = label_fn(action) if label_fn is not None else action.get_label()

            draw_action_binding_keymap(
                column_section,
                action=action,
                keymap_name=keymap_name,
                binding_index=binding_index,
                label=resolved_label
            )
