"""
Third-party add-ons preferences.
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

from .thirdparty import (
    auto_constraints_props,
    x_ray_selection_tools_props,
)

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# DRAW MODULE LOOKUP

_ADDON_DRAW_MODULES = {
    'AUTO_CONSTRAINTS': auto_constraints_props,
    'XRAY_SELECTION_TOOLS': x_ray_selection_tools_props,
}

# ----------------------------------------------------------------------------------------------------------------------
# CODE


class ThirdPartyPG(bpy.types.PropertyGroup):

    addon_settings: EnumProperty(
        name='Add-on Settings',
        description='Third-party add-on settings to display',
        items=[
            ('AUTO_CONSTRAINTS', 'Auto Constraints', ''),
            ('XRAY_SELECTION_TOOLS', 'X-Ray Selection Tools', ''),
        ],
        default='AUTO_CONSTRAINTS'
    )

    auto_constraints: PointerProperty(type=auto_constraints_props.AutoConstraintsPG)
    x_ray_selection_tools: PointerProperty(type=x_ray_selection_tools_props.XRaySelectionToolsPG)


def draw(preference, context, layout):
    """
    Draw third-party add-on settings.
    """
    column = layout.column()

    row = column.row()
    row.label(text='Third-party add-on settings.')

    row = column.row()
    row.label(text='These settings apply to supported third-party add-ons.')

    row = column.row(align=True)
    row.prop(preference.thirdparty, 'addon_settings', expand=True)

    module = _ADDON_DRAW_MODULES.get(preference.thirdparty.addon_settings)

    if module is None:
        row = column.row()
        row.label(text=f'Unknown add-on settings panel: {preference.thirdparty.addon_settings}')
        return

    module.draw(preference, context, column)


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

classes = (
    # Third-Party Add-on Modules
    auto_constraints_props,
    x_ray_selection_tools_props,
)


def register():
    for cls in classes:
        cls.register()

    bpy.utils.register_class(ThirdPartyPG)


def unregister():
    bpy.utils.unregister_class(ThirdPartyPG)

    for cls in reversed(classes):
        cls.unregister()
