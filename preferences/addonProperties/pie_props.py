"""
General addon-wide Blue Hole preferences.
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

from bpy.props import *

from ...operators_handling.actions.pie_actions import PIE_ACTIONS
from ...operators_handling.operator_action import OperatorAction
from ...keymaps.keymap_utils import get_keyconfig_sequence

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

def _update_enable_pie_menus(self, context):
    """
    Enable or disable Blue Hole pie menu keymaps.
    """
    from ...keymaps.pie import pie_keymaps_register

    if self.enable_pie_menus:
        pie_keymaps_register.register()
    else:
        pie_keymaps_register.unregister()


class PiePG(bpy.types.PropertyGroup):

    enable_pie_menus: BoolProperty(
        name="Enable Pie Menus",
        description="Enable Blue Hole pie menu shortcuts",
        default=False,
        update=_update_enable_pie_menus
    )


def draw(preference, context, layout):
    # -------------------------------------------------------------------------------------------------
    # PIE MENUS
    # -------------------------------------------------------------------------------------------------
    box_pie = layout.box()
    column_pie = box_pie.column()

    row = column_pie.row()
    row.prop(preference.pie, 'enable_pie_menus')

    if not preference.pie.enable_pie_menus:
        row = column_pie.row()
        row.label(text='Pie Menus are currently disabled.')
        return

    row = column_pie.row()
    row.label(text='Edit Blue Hole shortcut bindings directly from here.')

    grouped_pie_actions = _group_pie_actions_by_keymap()

    for keymap_name, pie_actions in grouped_pie_actions.items():

        box_section = column_pie.box()
        column_section = box_section.column()

        row = column_section.row()
        row.label(text=keymap_name.upper())

        for action in pie_actions:
            _draw_pie_menu_keymap(
                column_section,
                action=action,
                keymap_name=keymap_name
            )


def _get_menu_label(menu_idname: str) -> str:
    """
    Return a display label for a menu from its Blender bl_label.
    Falls back to a cleaned version of the bl_idname if not found.
    """
    menu_cls = getattr(bpy.types, menu_idname, None)
    if menu_cls is not None:
        bl_label = getattr(menu_cls, 'bl_label', '')
        if bl_label:
            return bl_label

    fallback = menu_idname
    fallback = fallback.replace('BLUEHOLE_MT_pie_', '')
    fallback = fallback.replace('_', ' ')
    return fallback.title()


def _get_pie_menu_idname(action: OperatorAction) -> str:
    """
    Return the pie menu idname for a pie-menu OperatorAction.
    """
    return action.get_props(None).get('name', '')


def _group_pie_actions_by_keymap() -> dict[str, list[OperatorAction]]:
    """
    Group pie menu actions by keymap_name while preserving declaration order.
    """
    grouped: dict[str, list[OperatorAction]] = {}

    for action in PIE_ACTIONS:
        for binding in action.keymap_bindings:
            grouped.setdefault(binding.keymap_name, []).append(action)

    return grouped


def _find_action_keymap(
        action: OperatorAction,
        keymap_name: str | None = None,
        check_user: bool = True,
        check_addon: bool = True,
        check_default: bool = False
):
    """
    Find the real Blender keymap item for an OperatorAction.
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


def _draw_pie_menu_keymap(column, action: OperatorAction, keymap_name: str):
    """
    Draw one real Blender keymap entry for the given pie menu action.
    """
    kc, km, kmi = _find_action_keymap(action, keymap_name=keymap_name)
    label = _get_menu_label(_get_pie_menu_idname(action))

    if kc is None or km is None or kmi is None:
        row = column.row()
        row.label(text=f'{label}: shortcut not found.', icon='ERROR')
        return

    row = column.row()
    row.label(text=label)

    column.context_pointer_set('keymap', km)
    rna_keymap_ui.draw_kmi([], kc, km, kmi, column, 0)
