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

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def _update_enable_pie_menus(self, context):
    from ...keymaps import keymaps_register
    keymaps_register.refresh()


class PiePG(bpy.types.PropertyGroup):

    enable_pie_menus: BoolProperty(
        name="Enable Pie Menus",
        description="Enable Blue Hole pie menu shortcuts",
        default=False,
        update=_update_enable_pie_menus
    )
    enable_editor_pie_shortcuts: BoolProperty(
        name='Enable Editor Pie Shortcuts',
        description='Enable additional Blender editor pie shortcuts',
        default=True,
        update=_update_enable_pie_menus,
    )


def draw(preference, context, layout):
    from ...keymaps import keymaps_register

    # -------------------------------------------------------------------------------------------------
    # PIE MENUS
    # -------------------------------------------------------------------------------------------------
    column_pie = layout.column()
    settings = preference.keymap
    if not (settings.deluxe_configured and settings.enable_keymaps
            and keymaps_register.runtime_keymaps_allowed(context, settings)):
        column_pie.label(text='Enable keymaps in Blue Hole’s Keymaps panel.', icon='INFO')
        return

    column_pie.prop(preference.pie, 'enable_pie_menus')
    column_pie.prop(preference.pie, 'enable_editor_pie_shortcuts')
    column_pie.label(text='Edit pie shortcuts in Keymaps under the Pie category.')


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

def register():
    bpy.utils.register_class(PiePG)


def unregister():
    bpy.utils.unregister_class(PiePG)
