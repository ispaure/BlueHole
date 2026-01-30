"""
This loads up the Blue Hole Preferences [Help & Update] Section
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS

import bpy
from bpy.props import *

import BlueHole.blenderUtils.configUtils as configUtils
from BlueHole.preferences.prefsCls import *


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

class bc(bpy.types.PropertyGroup):

    # UPDATES -----------------------------------------------------------------------------------------

    # Auto Updates
    auto_update_addon: BoolProperty(name = 'When enabled, addon will update automatically on startup if needed.',
                                    default = False)

    update_version_lst = [('Addon-Only', 'Addon-Only', ''), ('Deluxe', 'Deluxe', '')]

    # Forward Axis
    update_version: EnumProperty(name="Update Version",
                                 description="Defines the version to use when auto-updating.",
                                 items=update_version_lst,
                                 default='Addon-Only'
                                 )


def label_row(path, prop, row, label=''):
    row.label(text=label)
    row.prop(path, prop, text='')


def draw(preference, context, layout):

    # Support
    box = layout.box()
    box.label(text="Support Links:")
    column = box.column()
    row = column.row()
    row.operator("wm.bh_open_url", text='Guide').url = configUtils.get_url_db_value('BlueHoleWebsite', 'home')
    row.operator("wm.bh_open_url", text='Keymaps').url = configUtils.get_url_db_value('BlueHoleWebsite', 'keymaps')
    row.operator("wm.bh_open_url", text='Pie Menus').url = configUtils.get_url_db_value('BlueHoleWebsite', 'pie_menus')
    row = column.row()
    row.operator("wm.bh_help_submit_feedback", text='Submit Feedback', icon='WINDOW')
    row.operator("wm.bh_join_bh_discord", text='Join the Blue Hole Discord', icon='FUND')

    # Updates
    box = layout.box()
    box.label(text="Updates (Coming soon):")
    column = box.column()
    # General options
    row = column.row()
    row.prop(preference.help_n_update, 'auto_update_addon', text='Automatic Updates')
    row.enabled = False
    if prefs().help_n_update.auto_update_addon:
        row.prop(preference.help_n_update, 'update_version', text='Version')
    layout.operator('wm.bh_install_addon_only', icon='URL')
    layout.operator("wm.bh_install_deluxe", icon='URL')
