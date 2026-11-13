"""Preferences for optional Pipeline shortcuts."""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://github.com/ispaure/BlueHole

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

import bpy
from bpy.props import BoolProperty

from ....actions.actions.keymaps.pipeline import PIPELINE_KEYMAP_GROUPS, get_pipeline_group_actions
from .keymap_props_modeling_ui import draw_modeling_keymaps


def _update_keymaps(self, context):
    from ....keymaps import keymaps_register
    keymaps_register.refresh()


class PipelineKeymapPG(bpy.types.PropertyGroup):

    enable_pipeline_keymaps: BoolProperty(
        name='Enable Optional Pipeline Keymaps',
        default=True,
        update=_update_keymaps,
    )
    enable_pipeline_export_shortcuts: BoolProperty(
        name='Enable Export Shortcuts',
        default=True,
        update=_update_keymaps,
    )

    # Preserve saved IDs of the former placeholders.
    enable_pipeline_send_shortcuts: BoolProperty(default=True)
    enable_pipeline_container_shortcuts: BoolProperty(default=True)


def draw(preference, context, layout):
    settings = preference.keymap.pipeline
    column = layout.column()
    column.prop(settings, 'enable_pipeline_keymaps')
    if settings.enable_pipeline_keymaps:
        for group, toggle in PIPELINE_KEYMAP_GROUPS.items():
            draw_modeling_keymaps(column, settings, toggle, get_pipeline_group_actions(group))
    column.label(text='Blue Hole Save As is available in Blender Preferences → Keymap.')
