"""
General addon-wide Blue Hole keymap preferences.
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

from . import (
    keymap_props_mesh,
    keymap_props_navigation,
    keymap_props_object,
    keymap_props_pipeline,
    keymap_props_sculpt,
    keymap_props_selection,
    keymap_props_uv,
)

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# DRAW MODULE LOOKUP

_KEYMAP_DRAW_MODULES = {
    'SELECTION': keymap_props_selection,
    'NAVIGATION': keymap_props_navigation,
    'OBJECT': keymap_props_object,
    'MESH': keymap_props_mesh,
    'UV': keymap_props_uv,
    'SCULPT': keymap_props_sculpt,
    'PIPELINE': keymap_props_pipeline,
}

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def _update_enable_keymaps(self, context):
    """
    Enable or disable Blue Hole mesh keymaps.
    """
    # TODO: Replace with the real register module once it exists.
    # Example:
    # from ...keymaps.mesh import mesh_keymaps_register <- Need to update this for this situation.
    #
    # if self.enable_keymaps:
    #     keymaps_register.register()
    # else:
    #     keymaps_register.unregister()
    pass


class KeymapPG(bpy.types.PropertyGroup):

    keymap_settings: EnumProperty(
        name='Keymap Settings',
        description='Keymap settings to display',
        items=[
            ('SELECTION', 'Selection', ''),
            ('NAVIGATION', 'Navigation', ''),
            ('OBJECT', 'Object', ''),
            ('MESH', 'Mesh', ''),
            ('UV', 'UV', ''),
            ('SCULPT', 'Sculpt', ''),
            ('PIPELINE', 'Pipeline', ''),
        ],
        default='SELECTION'
    )

    selection: PointerProperty(type=keymap_props_selection.SelectionKeymapPG)
    navigation: PointerProperty(type=keymap_props_navigation.NavigationKeymapPG)
    object: PointerProperty(type=keymap_props_object.ObjectKeymapPG)
    mesh: PointerProperty(type=keymap_props_mesh.MeshKeymapPG)
    uv: PointerProperty(type=keymap_props_uv.UVKeymapPG)
    sculpt: PointerProperty(type=keymap_props_sculpt.SculptKeymapPG)
    pipeline: PointerProperty(type=keymap_props_pipeline.PipelineKeymapPG)

    enable_keymaps: BoolProperty(
        name='Enable Keymaps',
        description='Enable Blue Hole keymaps',
        default=False,
        update=_update_enable_keymaps
    )


def draw(preference, context, layout):
    # -------------------------------------------------------------------------------------------------
    # KEYMAPS
    # -------------------------------------------------------------------------------------------------
    box_keymap = layout.box()
    column_keymap = box_keymap.column()

    row = column_keymap.row()
    row.prop(preference.keymap, 'enable_keymaps')

    if not preference.keymap.enable_keymaps:
        row = column_keymap.row()
        row.label(text='Keymaps are currently disabled.')
        return

    row = column_keymap.row(align=True)
    row.prop(preference.keymap, 'keymap_settings', expand=True)

    module = _KEYMAP_DRAW_MODULES.get(preference.keymap.keymap_settings)

    if module is None:
        row = column_keymap.row()
        row.label(text=f'Unknown keymap settings panel: {preference.keymap.keymap_settings}')
        return

    module.draw(preference, context, column_keymap)
