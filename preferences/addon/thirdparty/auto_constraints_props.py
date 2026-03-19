"""
Auto Constraints add-on preferences.
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


class AutoConstraintsPG(bpy.types.PropertyGroup):
    enable_transform_tools_modal_autoconstraint: BoolProperty(
        name='Enable Auto Constraints in 3D View (Keymaps → Transform → Modal)',
        description='Turns on AutoConstraint whilst using Transform Modals in 3D View (Requires "autoConstraints" add-on)',
        default=True
    )


def draw(preference, context, layout):
    """
    Draw Auto Constraints add-on settings.
    """
    column = layout.column()

    addon_loaded = op_exists('transform.translate_auto_constraint')

    # -------------------------------------------------------------------------------------------------
    # ADD-ON STATUS (NO BOX)
    # -------------------------------------------------------------------------------------------------
    row = column.row()
    row.label(text='Add-on Status')

    if addon_loaded:
        row.label(text='Loaded', icon='CHECKMARK')
    else:
        row.label(text='Not loaded (Requires "autoConstraints" add-on)', icon='ERROR')
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

    transform_keymaps_ready = (
        prefs().keymap.transform.enable_transform_keymaps and
        prefs().keymap.transform.enable_transform_tools_modal
    )

    if not transform_keymaps_ready:
        row = box.row()
        row.label(
            text='Requires Transform keymaps and Transform Tools (Modal) to be enabled.',
            icon='ERROR'
        )

    row = box.row()
    row.enabled = transform_keymaps_ready
    row.prop(preference.thirdparty.auto_constraints, 'enable_transform_tools_modal_autoconstraint')


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

classes = (
    AutoConstraintsPG,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
