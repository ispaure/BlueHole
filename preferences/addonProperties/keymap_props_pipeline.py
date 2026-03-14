"""
Pipeline keymap preferences for Blue Hole.
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


def _update_enable_pipeline_keymaps(self, context):
    """
    Enable or disable Blue Hole pipeline keymaps.
    """
    # TODO: Replace with the real register module once it exists.
    # Example:
    # from ...keymaps.pipeline import pipeline_keymaps_register
    #
    # if self.enable_pipeline_keymaps:
    #     pipeline_keymaps_register.register()
    # else:
    #     pipeline_keymaps_register.unregister()
    pass


class PipelineKeymapPG(bpy.types.PropertyGroup):

    enable_pipeline_keymaps: BoolProperty(
        name='Enable Pipeline Keymaps',
        description='Enable Blue Hole pipeline keymaps',
        default=False,
        update=_update_enable_pipeline_keymaps
    )

    enable_pipeline_export_shortcuts: BoolProperty(
        name='Enable Export Shortcuts',
        description='Enable Blue Hole export shortcuts',
        default=False,
        # update=_update_enable_pipeline_export_shortcuts
    )

    enable_pipeline_send_shortcuts: BoolProperty(
        name='Enable Send Shortcuts',
        description='Enable Blue Hole send shortcuts',
        default=False,
        # update=_update_enable_pipeline_send_shortcuts
    )

    enable_pipeline_container_shortcuts: BoolProperty(
        name='Enable Container Shortcuts',
        description='Enable Blue Hole asset container shortcuts',
        default=False,
        # update=_update_enable_pipeline_container_shortcuts
    )


def draw(preference, context, layout):
    # -------------------------------------------------------------------------------------------------
    # PIPELINE KEYMAPS
    # -------------------------------------------------------------------------------------------------
    box_pipeline = layout.box()
    column_pipeline = box_pipeline.column()

    row = column_pipeline.row()
    row.prop(preference.keymap.pipeline, 'enable_pipeline_keymaps')

    if not preference.keymap.pipeline.enable_pipeline_keymaps:
        row = column_pipeline.row()
        row.label(text='Pipeline keymaps are currently disabled.')
        return

    row = column_pipeline.row()
    row.prop(preference.keymap.pipeline, 'enable_pipeline_export_shortcuts')

    row = column_pipeline.row()
    row.prop(preference.keymap.pipeline, 'enable_pipeline_send_shortcuts')

    row = column_pipeline.row()
    row.prop(preference.keymap.pipeline, 'enable_pipeline_container_shortcuts')

    row = column_pipeline.row()
    row.label(text='Pipeline keymap settings will appear here.')
