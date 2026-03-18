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

from ...actions.actions.pie_actions import PIE_ACTIONS
from ...actions.operator_action import OperatorAction
from .keymaps.keymap_ui_utils import draw_action_feature_keymaps

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
    column_pie = layout.column()

    draw_action_feature_keymaps(
        column=column_pie,
        feature_owner=preference.pie,
        feature_prop_name='enable_pie_menus',
        actions=PIE_ACTIONS,
        label_fn=lambda action: _get_menu_label(_get_pie_menu_idname(action)),
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


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

def register():
    bpy.utils.register_class(PiePG)


def unregister():
    bpy.utils.unregister_class(PiePG)
