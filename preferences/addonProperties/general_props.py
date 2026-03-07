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
from bpy.props import *
from ...Lib.commonUtils.osUtils import *
from ..prefs import *
from ...environment import envManager

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


def _is_pie_menu_bound(menu_idname: str) -> bool:
    """
    Returns True if the given pie menu is bound to any active keymap item.

    Checks for wm.call_menu_pie operators whose 'name' property matches
    the provided menu idname.
    """
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user

    if kc is None:
        return False

    for km in kc.keymaps:
        for kmi in km.keymap_items:
            if kmi.idname != 'wm.call_menu_pie':
                continue

            if not kmi.active:
                continue

            if getattr(kmi.properties, 'name', None) == menu_idname:
                return True

    return False


def _draw_pie_menu_status_row(column, menu_idname: str, label: str):
    """
    Draw one row showing whether a pie menu currently has a keybinding.
    """
    is_bound = _is_pie_menu_bound(menu_idname)

    row = column.row(align=True)
    row.label(text=label)

    if is_bound:
        row.label(text='Bound', icon='CHECKMARK')
    else:
        row.label(text='Not Bound', icon='ERROR')


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
    row.label(text='Shows whether each Blue Hole pie menu is currently bound to a shortcut.')

    _draw_pie_menu_status_row(
        column_pie,
        menu_idname="BLUEHOLE_MT_pie_global_import_export",
        label='Global Import / Export'
    )
