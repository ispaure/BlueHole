"""
This loads up the Blue Hole Preferences Section (Hosting all Preferences)
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
from bpy.types import AddonPreferences

from .props import general_props, environment_props, sourcecontrol_props, help_update_props
from ..environment import envManager

# Import your new prefs API (adjust module path if yours is named differently)
from .prefs import prefs

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE

# Dictionary of environments with preferences file
env_preferences = {}

# Explicit mapping: enum key -> module with a draw() function
_DRAW_MODULES = {
    "ENVIRONMENT": environment_props,
    "GENERAL": general_props,
    "SOURCECONTROL": sourcecontrol_props,
    "HELP_N_UPDATE": help_update_props,
}


class BlueHole(AddonPreferences):
    bl_idname = 'BlueHole'
    _prefs_visible = False

    settings: EnumProperty(
        name='Settings',
        description='Settings to display',
        items=[
            ('ENVIRONMENT', 'Structure', ''),
            ('GENERAL', 'Bridges', ''),
            ('SOURCECONTROL', 'Source Control', ''),
            ('HELP_N_UPDATE', 'Help & Updates', ''),
        ],
        default='ENVIRONMENT'
    )

    general: PointerProperty(type=general_props.GeneralPG)
    environment: PointerProperty(type=environment_props.EnvironmentPG)
    sourcecontrol: PointerProperty(type=sourcecontrol_props.SourceControlPG)
    help_n_update: PointerProperty(type=help_update_props.HelpUpdatePG)

    # For environments with known preference files:
    for key, value in env_preferences.items():
        if key == 'c3_prod':
            c3_prod: PointerProperty(type=value)

    def draw(self, context):
        BlueHole._prefs_visible = True
        layout = self.layout

        # Set Active Environment
        box = layout.box()
        msg = "Active Environment: " + prefs().env.active_environment
        column = box.column()
        row = column.row()
        row.label(text=msg.upper())
        row = column.row()
        row.operator('wm.set_active_environment', text='Set Active Env.', icon='PRESET')
        row.operator('wm.add_environment', text='Create Env.', icon='PRESET_NEW')
        if len(envManager.get_env_lst_enum_property(exclude_default=True)) > 0:
            row.operator('wm.delete_environment', text='Delete Env.', icon='REMOVE')
        if prefs().env.active_environment == 'default':
            row = column.row()
            row.label(text='The settings for the default environment are locked.')
            row = column.row()
            row.label(text='Create or set a different active environment to edit settings.')

        # Show tabs
        column = layout.column(align=True)
        row = column.row(align=True)
        row.prop(self, 'settings', expand=True)

        # Draw selected panel
        box = column.box()
        module = _DRAW_MODULES.get(self.settings)
        if module is None:
            box.label(text=f'Unknown settings panel: {self.settings}')
            return

        module.draw(self, context, box)


classes = (
    general_props.GeneralPG,        # sub PropertyGroups before others
    environment_props.EnvironmentPG,
    sourcecontrol_props.SourceControlPG,
    help_update_props.HelpUpdatePG,
    BlueHole
)


# Registration
def register():
    for key, val in env_preferences.items():
        bpy.utils.register_class(val)
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for key, val in env_preferences.items():
        bpy.utils.unregister_class(val)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
