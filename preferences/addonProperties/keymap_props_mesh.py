"""
Mesh keymap preferences for Blue Hole.
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


def _update_enable_mesh_keymaps(self, context):
    """
    Enable or disable Blue Hole mesh keymaps.
    """
    # TODO: Replace with the real register module once it exists.
    # Example:
    # from ...keymaps.mesh import mesh_keymaps_register
    #
    # if self.enable_mesh_keymaps:
    #     mesh_keymaps_register.register()
    # else:
    #     mesh_keymaps_register.unregister()
    pass


class MeshKeymapPG(bpy.types.PropertyGroup):

    enable_mesh_keymaps: BoolProperty(
        name='Enable Mesh Keymaps',
        description='Enable Blue Hole mesh keymaps',
        default=True,
        update=_update_enable_mesh_keymaps
    )

    enable_mesh_selection_grow_shrink: BoolProperty(
        name='Enable Grow / Shrink Selection',
        description='Enable Blue Hole mesh selection grow and shrink shortcuts',
        default=True,
        # update=_update_enable_mesh_selection_grow_shrink
    )

    enable_mesh_modeling_shortcuts: BoolProperty(
        name='Enable Modeling Shortcuts',
        description='Enable Blue Hole mesh modeling shortcuts',
        default=True,
        # update=_update_enable_mesh_modeling_shortcuts
    )


def draw(preference, context, layout):
    # -------------------------------------------------------------------------------------------------
    # MESH KEYMAPS
    # -------------------------------------------------------------------------------------------------
    column_mesh = layout.column()

    row = column_mesh.row()
    row.prop(preference.keymap.mesh, 'enable_mesh_keymaps')

    if not preference.keymap.mesh.enable_mesh_keymaps:
        row = column_mesh.row()
        row.label(text='Mesh keymaps are currently disabled.')
        return

    row = column_mesh.row()
    row.prop(preference.keymap.mesh, 'enable_mesh_selection_grow_shrink')

    row = column_mesh.row()
    row.prop(preference.keymap.mesh, 'enable_mesh_modeling_shortcuts')

    row = column_mesh.row()
    row.label(text='Mesh keymap settings will appear here.')
