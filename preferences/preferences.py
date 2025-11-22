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

import os
from pathlib import Path

import bpy
from bpy.props import *
from bpy.types import Operator, AddonPreferences

from . import general, sourcecontrol, help_n_update, environment
import BlueHole.envUtils.envUtils as envUtils
import BlueHole.blenderUtils.addon as addon

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

# Dictionary of environments with preferences file
env_preferences = {}

# Get list of environments
env_lst = envUtils.get_env_dict()

# # Add entries to dictionary if preferences file was found
# for env, value in env_lst.items():
#     imp_module_path = str(Path(value + '/env_preferences.py'))
#     if os.path.exists(imp_module_path):
#         print_debug_msg('Environment "' + env + '" does have a preference file. Loading it...', show_verbose)
#         env_preferences[env] = importUtils.import_python_module_absolute_path(imp_module_path).bc
#         # env_preferences[env] = importlib.import_module(imp_module_path).bc
#         print_debug_msg('Preference file loaded!', show_verbose)
#     else:
#         print_debug_msg('Environment "' + env + '" does not have a preferences file.', show_verbose)


class BlueHole(AddonPreferences):
    bl_idname = 'BlueHole'
    print(__package__)

    settings: EnumProperty(
        name = 'Settings',
        description = 'Settings to display',
        items = [('ENVIRONMENT', 'Structure', ''),
                 ('GENERAL', 'Bridges', ''),
                 ('SOURCECONTROL', 'Source Control', ''),
                 ('HELP_N_UPDATE', 'Help & Updates', '')],
        default = 'ENVIRONMENT')

    general: PointerProperty(type=general.bc)
    environment: PointerProperty(type=environment.bc)
    sourcecontrol: PointerProperty(type=sourcecontrol.bc)
    help_n_update: PointerProperty(type=help_n_update.bc)

    # For environments with known preference files:
    for key, value in env_preferences.items():
        if key == 'c3_prod':
            c3_prod: PointerProperty(type=value)

    def draw(self, context):
        # layout = self.layout
        # layout.label(text="This is a preferences view for our add-on")
        # layout.prop(self, "filepath")
        # layout.prop(self, "number")
        # layout.prop(self, "boolean")
        layout = self.layout

        # Set Active Environment
        box = layout.box()
        msg = "Active Environment: " + addon.preference().environment.active_environment
        column = box.column()
        row = column.row()
        row.label(text=msg.upper())
        row = column.row()
        row.operator('wm.set_active_environment', text='Set Active Env.', icon='PRESET')
        row.operator('wm.add_environment', text='Create Env.', icon='PRESET_NEW')
        if len(envUtils.get_env_lst_enum_property(exclude_default=True)) > 0:
            row.operator('wm.delete_environment', text='Delete Env.', icon='REMOVE')
        if addon.preference().environment.active_environment == 'default':
            row = column.row()
            row.label(text='The settings for the default environment are locked.')
            row = column.row()
            row.label(text='Create or set a different active environment to edit settings.')

        # Show tabs
        column = layout.column(align=True)
        row = column.row(align=True)
        row.prop(self, 'settings', expand=True)

        box = column.box()
        globals()[self.settings.lower()].draw(self, context, box)

        # Keep trying to update the preference file
        envUtils.write_env_ini_from_bh_prefs()


classes = (general.bc,  # Need to make sure sub bc are before others
           environment.bc,
           sourcecontrol.bc,
           help_n_update.bc,
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
    for cls in classes:
        bpy.utils.unregister_class(cls)
