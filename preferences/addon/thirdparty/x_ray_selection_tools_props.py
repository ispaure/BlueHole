"""
X-Ray Selection Tools add-on preferences.
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
from ...prefs import prefs
from ....blenderUtils.operatorUtils import op_exists

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE


class XRaySelectionToolsPG(bpy.types.PropertyGroup):
    enable_selection_tool_switch_box_x_ray: BoolProperty(
        name='Enable X-Ray (Keymaps → Selection → Tool Switch)',
        description='Enable X-Ray upon Selection Tool Switch (Requires "X-Ray Selection Tools" add-on)',
        default=True
    )


def draw(preference, context, layout):
    """
    Draw X-Ray Selection Tools add-on settings.
    """
    column = layout.column()

    addon_loaded = op_exists('mesh.select_box_xray')

    # -------------------------------------------------------------------------------------------------
    # ADD-ON STATUS (NO BOX)
    # -------------------------------------------------------------------------------------------------
    row = column.row()
    row.label(text='Add-on Status')

    if addon_loaded:
        row.label(text='Loaded', icon='CHECKMARK')
    else:
        row.label(text='Not loaded (Requires "X-Ray Selection Tools" add-on)', icon='ERROR')
        return

    # -------------------------------------------------------------------------------------------------
    # KEYMAPS
    # -------------------------------------------------------------------------------------------------
    box = column.box()

    row = box.row()
    row.label(text='KEYMAPS')

    if not prefs().keymap.enable_keymaps:
        row = box.row()
        row.label(text='Blue Hole keymaps must be enabled to show this section.', icon='ERROR')
        return

    selection_keymaps_ready = (
        prefs().keymap.selection.enable_selection_keymaps and
        prefs().keymap.selection.enable_selection_tool_switch
    )

    if not selection_keymaps_ready:
        row = box.row()
        row.label(
            text='Requires Selection keymaps and Selection Tool Switch to be enabled.',
            icon='ERROR'
        )

    row = box.row()
    row.enabled = selection_keymaps_ready
    row.prop(preference.thirdparty.x_ray_selection_tools, 'enable_selection_tool_switch_box_x_ray')


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

classes = (
    XRaySelectionToolsPG,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
