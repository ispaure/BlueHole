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

KEYMAP_CATEGORIES = ('selection', 'navigation', 'transform', 'object', 'mesh',
                     'uv', 'sculpt', 'pipeline', 'other')

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def _update_keymaps(self, context):
    from ...keymaps import keymaps_register
    keymaps_register.refresh()


class KeymapPG(bpy.types.PropertyGroup):

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
    from ...overlays.deluxe.applyDeluxePrefs import uses_blender_keyconfig

    # -------------------------------------------------------------------------------------------------
    # KEYMAPS
    # -------------------------------------------------------------------------------------------------
    column_keymap = layout.column()
    column_keymap.operator_context = 'INVOKE_DEFAULT'

    settings = preference.keymap
    blender_preset = uses_blender_keyconfig(context.window_manager.keyconfigs)
    if not blender_preset:
        column_keymap.alignment = 'LEFT'
        column_keymap.label(text='Select the Blender preset in Preferences → Keymap to use the Blue Hole editor.', icon='INFO')
        column_keymap.operator('wm.bh_backup_keymap_setup')
        return

    if not settings.deluxe_configured:
        column_keymap.alignment = 'LEFT'
        label = 'Use Keymap Editor' if settings.enable_keymaps else 'Enable Keymaps'
        column_keymap.operator('wm.bh_apply_deluxe_prefs', text=label)
        return

    if not keymaps_register.runtime_keymaps_allowed(context, settings):
        return

    from .keymaps import deluxe_editor

    deluxe_editor.draw(context, column_keymap, settings)

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
    from .keymaps import deluxe_editor

    for cls in classes:
        bpy.utils.register_class(cls)
    deluxe_editor.register()


def unregister():
    from .keymaps import deluxe_editor

    deluxe_editor.unregister()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
