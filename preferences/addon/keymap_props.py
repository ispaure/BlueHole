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

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def _update_keymaps(self, context):
    from ...keymaps import keymaps_register
    keymaps_register.refresh()


class KeymapPG(bpy.types.PropertyGroup):

    enable_keymaps: BoolProperty(
        name='Enable Deluxe Keymaps',
        description='Enable Deluxe shortcuts using the saved Blue Hole catalog',
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
        return

    if not settings.deluxe_configured:
        column_keymap.alignment = 'LEFT'
        column_keymap.operator('wm.bh_apply_deluxe_prefs', text='Enable Deluxe Keymaps')
        return

    if not keymaps_register.runtime_keymaps_allowed(context, settings):
        return

    from .keymaps import deluxe_editor

    deluxe_editor.draw(context, column_keymap, settings)

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


classes = (KeymapPG,)


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
