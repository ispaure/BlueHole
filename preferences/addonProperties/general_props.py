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
from ...Lib.commonUtils.osUtils import *
from ..prefs import *
from ...environment import envManager
from ..addon_keymap import find_pie_menu_keymap, PIE_GLOBAL_IMPORT_EXPORT

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

class GeneralPG(bpy.types.PropertyGroup):
    # Get list of environments
    env_enum_prop_lst = envManager.get_env_lst_enum_property()

    # Active Environment
    active_environment: EnumProperty(
        name="Active Environment",
        description="Defines the project directory structure.",
        items=env_enum_prop_lst,
        default='default'
    )


def _draw_pie_menu_keymap(column, context, menu_idname: str, label: str):
    """
    Draw one real Blender keymap entry for the given pie menu.
    """
    kc, km, kmi = find_pie_menu_keymap(menu_idname, keymap_name='3D View')

    if kc is None or km is None or kmi is None:
        row = column.row()
        row.label(text=f'{label}: shortcut not found.', icon='ERROR')
        return

    row = column.row()
    row.label(text=label)

    column.context_pointer_set('keymap', km)
    rna_keymap_ui.draw_kmi([], kc, km, kmi, column, 0)


def draw(preference, context, layout):
    """
    Draw general addon settings.
    """
    box = layout.box()
    column = box.column()

    row = column.row()
    row.label(text='General Blue Hole addon settings.')

    row = column.row()
    row.label(text='These settings apply to the addon itself rather than a specific environment.')

    # -------------------------------------------------------------------------------------------------
    # PIE MENUS
    # -------------------------------------------------------------------------------------------------
    box_pie = column.box()
    column_pie = box_pie.column()

    row = column_pie.row()
    row.label(text='Pie Menus')

    row = column_pie.row()
    row.label(text='Edit Blue Hole shortcut bindings directly from here.')

    _draw_pie_menu_keymap(
        column_pie,
        context,
        menu_idname=PIE_GLOBAL_IMPORT_EXPORT,
        label='Global Import / Export'
    )