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

# Import Addon Properties
from .addonProperties import (
    general_props,
    keymap_props,
    keymap_props_mesh,
    keymap_props_navigation,
    keymap_props_object,
    keymap_props_pipeline,
    keymap_props_sculpt,
    keymap_props_selection,
    keymap_props_transform,
    keymap_props_uv,
    pie_props,
    help_update_props)

# Import Environment Properties
from .environmentProperties import (
    bridge_props,
    container_props,
    directory_props,
    sourcecontrol_props)

from ..environment import envManager

from .prefs import prefs, addon_module_name

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE


# Explicit mapping: enum key -> module with a draw() function
_ENV_DRAW_MODULES = {
    "DIRECTORY": directory_props,
    "CONTAINER": container_props,
    "BRIDGE": bridge_props,
    "SOURCECONTROL": sourcecontrol_props,
}

_GENERAL_DRAW_MODULES = {
    "GENERAL": general_props,
    "PIE": pie_props,
    "KEYMAP": keymap_props,
    "HELP_N_UPDATE": help_update_props,
}


class BlueHole(AddonPreferences):
    bl_idname = addon_module_name()
    _prefs_visible = False

    main_settings: EnumProperty(
        name='Settings Category',
        description='Main settings category to display',
        items=[
            ('ENVIRONMENT', 'Environment Settings', ''),
            ('GENERAL_ADDON', 'Addon Settings', ''),
        ],
        default='ENVIRONMENT'
    )

    environment_settings: EnumProperty(
        name='Environment Settings',
        description='Environment settings to display',
        items=[
            ('DIRECTORY', 'Directory', ''),
            ('CONTAINER', 'Container', ''),
            ('BRIDGE', 'Send & Export', ''),
            ('SOURCECONTROL', 'Source Control', ''),
        ],
        default='DIRECTORY'
    )

    general_addon_settings: EnumProperty(
        name='General Addon Settings',
        description='General addon settings to display',
        items=[
            ('GENERAL', 'General Settings', ''),
            ('KEYMAP', 'Keymaps', ''),
            ('PIE', 'Pie Menus', ''),
            ('HELP_N_UPDATE', 'Help & Updates', ''),
        ],
        default='GENERAL'
    )

    general: PointerProperty(type=general_props.GeneralPG)
    keymap: PointerProperty(type=keymap_props.KeymapPG)
    pie: PointerProperty(type=pie_props.PiePG)
    help_n_update: PointerProperty(type=help_update_props.HelpUpdatePG)
    directory: PointerProperty(type=directory_props.DirectoryPG)
    container: PointerProperty(type=container_props.ContainerPG)
    bridge: PointerProperty(type=bridge_props.BridgePG)
    sourcecontrol: PointerProperty(type=sourcecontrol_props.SourceControlPG)

    def draw(self, context):
        BlueHole._prefs_visible = True
        layout = self.layout

        # Main section tabs
        column = layout.column(align=True)
        row = column.row(align=True)
        row.prop(self, 'main_settings', expand=True)

        # ------------------------------------------------------------------------------------------------------------------
        # ENVIRONMENT SETTINGS
        if self.main_settings == 'ENVIRONMENT':

            # One single box for all environment UI
            box = layout.box()
            column = box.column()

            msg = "Active Environment: " + prefs().general.active_environment
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

            # Environment sub-tabs inside the same box
            row = column.row(align=True)
            row.prop(self, 'environment_settings', expand=True)

            # Draw selected environment panel inside the same box
            module = _ENV_DRAW_MODULES.get(self.environment_settings)
            if module is None:
                column.label(text=f'Unknown environment settings panel: {self.environment_settings}')
                return

            module.draw(self, context, column)

        # ------------------------------------------------------------------------------------------------------------------
        # GENERAL ADDON SETTINGS
        elif self.main_settings == 'GENERAL_ADDON':

            # General addon sub-tabs
            column = layout.column(align=True)
            row = column.row(align=True)
            row.prop(self, 'general_addon_settings', expand=True)

            # Draw selected general addon panel
            box = column.box()
            module = _GENERAL_DRAW_MODULES.get(self.general_addon_settings)
            if module is None:
                box.label(text=f'Unknown general addon settings panel: {self.general_addon_settings}')
                return

            module.draw(self, context, box)

        else:
            box = layout.box()
            box.label(text=f'Unknown main settings category: {self.main_settings}')


classes = (

    # General Property Import First
    general_props.GeneralPG,

    # Keymap Sub-Properties Import Before Keymap
    keymap_props_selection.SelectionKeymapPG,
    keymap_props_navigation.NavigationKeymapPG,
    keymap_props_transform.TransformKeymapPG,
    keymap_props_object.ObjectKeymapPG,
    keymap_props_mesh.MeshKeymapPG,
    keymap_props_uv.UVKeymapPG,
    keymap_props_sculpt.SculptKeymapPG,
    keymap_props_pipeline.PipelineKeymapPG,

    keymap_props.KeymapPG,

    pie_props.PiePG,
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
