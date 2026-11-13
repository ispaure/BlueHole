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

from .keymaps import (
    keymap_props_mesh,
    keymap_props_navigation,
    keymap_props_object,
    keymap_props_other,
    keymap_props_pipeline,
    keymap_props_sculpt,
    keymap_props_selection,
    keymap_props_transform,
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
    'TRANSFORM': keymap_props_transform,
    'OBJECT': keymap_props_object,
    'MESH': keymap_props_mesh,
    'UV': keymap_props_uv,
    'SCULPT': keymap_props_sculpt,
    'PIPELINE': keymap_props_pipeline,
    'OTHER': keymap_props_other,
}
KEYMAP_CATEGORIES = tuple(name.lower() for name in _KEYMAP_DRAW_MODULES)

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def _update_keymaps(self, context):
    from ...keymaps import keymaps_register
    keymaps_register.refresh()


class KeymapPG(bpy.types.PropertyGroup):

    keymap_settings: EnumProperty(
        name='Keymap Settings',
        description='Keymap settings to display',
        items=[
            ('SELECTION', 'Selection', ''),
            ('NAVIGATION', 'Navigation', ''),
            ('TRANSFORM', 'Transform', ''),
            ('OBJECT', 'Object', ''),
            ('MESH', 'Mesh', ''),
            ('UV', 'UV', ''),
            ('SCULPT', 'Sculpt', ''),
            ('PIPELINE', 'Pipeline', ''),
            ('OTHER', 'Other', ''),
        ],
        default='SELECTION'
    )

    selection: PointerProperty(type=keymap_props_selection.SelectionKeymapPG)
    navigation: PointerProperty(type=keymap_props_navigation.NavigationKeymapPG)
    transform: PointerProperty(type=keymap_props_transform.TransformKeymapPG)
    object: PointerProperty(type=keymap_props_object.ObjectKeymapPG)
    mesh: PointerProperty(type=keymap_props_mesh.MeshKeymapPG)
    uv: PointerProperty(type=keymap_props_uv.UVKeymapPG)
    sculpt: PointerProperty(type=keymap_props_sculpt.SculptKeymapPG)
    pipeline: PointerProperty(type=keymap_props_pipeline.PipelineKeymapPG)
    other: PointerProperty(type=keymap_props_other.OtherKeymapPG)

    enable_keymaps: BoolProperty(
        name='Enable Keymaps',
        description='Enable Blue Hole keymaps',
        default=False,
        update=_update_keymaps
    )
    deluxe_configured: BoolProperty(default=False, options={'HIDDEN'})


def draw(preference, context, layout):
    from ...keymaps import keymaps_register

    # -------------------------------------------------------------------------------------------------
    # KEYMAPS
    # -------------------------------------------------------------------------------------------------
    column_keymap = layout.column()
    column_keymap.operator_context = 'INVOKE_DEFAULT'

    if not preference.keymap.deluxe_configured:
        column_keymap.operator('wm.bh_apply_deluxe_prefs')

    if not keymaps_register.runtime_keymaps_allowed(context, preference.keymap):
        column_keymap.label(text='Deluxe requires the Blender preset and a reviewed keymap setup.', icon='INFO')
        column_keymap.operator('wm.bh_backup_keymap_setup')
        return

    label = 'Enable Deluxe Keymaps' if preference.keymap.deluxe_configured else 'Enable Keymaps'
    column_keymap.prop(preference.keymap, 'enable_keymaps', text=label)

    if preference.keymap.deluxe_configured:
        column_keymap.operator('wm.bh_reset_deluxe_keymaps')
        column_keymap.prop(context.preferences.inputs, 'invert_mouse_zoom')

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

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


classes = (
    # Keymap Sub-Properties Import Before KeymapPG
    keymap_props_selection.SelectionKeymapPG,
    keymap_props_navigation.NavigationKeymapPG,
    keymap_props_transform.TransformKeymapPG,
    keymap_props_object.ObjectKeymapPG,
    keymap_props_mesh.MeshKeymapPG,
    keymap_props_uv.UVKeymapPG,
    keymap_props_sculpt.SculptKeymapPG,
    keymap_props_pipeline.PipelineKeymapPG,
    keymap_props_other.OtherKeymapPG,

    # Import KeymapPG last
    KeymapPG,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
