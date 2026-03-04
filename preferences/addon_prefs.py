"""
This loads up the Blue Hole Preferences Section (Hosting all Preferences)
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
from bpy.types import AddonPreferences

from .addonProperties import general_props, help_update_props
from .environmentProperties import bridge_props, container_props, directory_props, sourcecontrol_props
from ..environment import envManager

# Import your new prefs API (adjust module path if yours is named differently)
from .prefs import prefs, addon_module_name

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE


# Explicit mapping: enum key -> module with a draw() function
_DRAW_MODULES = {
    "DIRECTORY": directory_props,
    "CONTAINER": container_props,
    "BRIDGE": bridge_props,
    "SOURCECONTROL": sourcecontrol_props,
    "HELP_N_UPDATE": help_update_props,
}


class BlueHole(AddonPreferences):
    bl_idname = addon_module_name()
    _prefs_visible = False

    settings: EnumProperty(
        name='Settings',
        description='Settings to display',
        items=[
            ('DIRECTORY', 'Directory', ''),
            ('CONTAINER', 'Container', ''),
            ('BRIDGE', 'Bridge', ''),
            ('SOURCECONTROL', 'Source Control', ''),
            ('HELP_N_UPDATE', 'Help & Updates', ''),
        ],
        default='DIRECTORY'
    )

    general: PointerProperty(type=general_props.GeneralPG)
    help_n_update: PointerProperty(type=help_update_props.HelpUpdatePG)
    directory: PointerProperty(type=directory_props.DirectoryPG)
    container: PointerProperty(type=container_props.ContainerPG)
    bridge: PointerProperty(type=bridge_props.BridgePG)
    sourcecontrol: PointerProperty(type=sourcecontrol_props.SourceControlPG)

    def draw(self, context):
        BlueHole._prefs_visible = True
        layout = self.layout

        # Set Active Environment
        box = layout.box()
        msg = "Active Environment: " + prefs().general.active_environment
        column = box.column()
        row = column.row()
        row.label(text=msg.upper())
        row = column.row()
        row.operator('wm.set_active_environment', text='Set Active Env.', icon='PRESET')
        row.operator('wm.add_environment', text='Create Env.', icon='PRESET_NEW')
        if len(envManager.get_env_lst_enum_property(exclude_default=True)) > 0:
            row.operator('wm.delete_environment', text='Delete Env.', icon='REMOVE')
        if prefs().general.active_environment == 'default':
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
    help_update_props.HelpUpdatePG,
    directory_props.DirectoryPG,
    container_props.ContainerPG,
    bridge_props.BridgePG,
    sourcecontrol_props.SourceControlPG,
    BlueHole
)


# Registration
def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
