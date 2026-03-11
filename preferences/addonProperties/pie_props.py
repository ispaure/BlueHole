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
from ..addon_keymap import find_pie_menu_keymap, get_all_pie_menu_defs, PieKeymapDef

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

def _update_enable_pie_menus(self, context):
    """
    Enable or disable Blue Hole pie menu keymaps.
    """
    from .. import addon_keymap

    if self.enable_pie_menus:
        addon_keymap.register()
    else:
        addon_keymap.unregister()


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
        row.label(text='Pie menu shortcuts are currently disabled.')
        return

    row = column_pie.row()
    row.label(text='Edit Blue Hole shortcut bindings directly from here.')

    grouped_pie_defs = _group_pie_defs_by_keymap()

    for keymap_name, pie_defs in grouped_pie_defs.items():

        box_section = column_pie.box()
        column_section = box_section.column()

        row = column_section.row()
        row.label(text=keymap_name.upper())

        for pie_def in pie_defs:
            _draw_pie_menu_keymap(
                column_section,
                menu_idname=pie_def.menu_idname,
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


def _group_pie_defs_by_keymap() -> dict[str, list[PieKeymapDef]]:
    """
    Group pie menu definitions by keymap_name while preserving declaration order.
    """
    grouped: dict[str, list[PieKeymapDef]] = {}

    for pie_def in get_all_pie_menu_defs():
        keymap_name = pie_def.keymap_name
        grouped.setdefault(keymap_name, []).append(pie_def)

    return grouped


def _draw_pie_menu_keymap(column, menu_idname: str, keymap_name: str):
    """
    Draw one real Blender keymap entry for the given pie menu.
    """
    kc, km, kmi = find_pie_menu_keymap(menu_idname, keymap_name=keymap_name)
    label = _get_menu_label(menu_idname)

    if kc is None or km is None or kmi is None:
        row = column.row()
        row.label(text=f'{label}: shortcut not found.', icon='ERROR')
        return

    row = column.row()
    row.label(text=label)

    column.context_pointer_set('keymap', km)
    rna_keymap_ui.draw_kmi([], kc, km, kmi, column, 0)
