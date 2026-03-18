"""
General addon-wide Blue Hole preferences.
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
from ...environment import envManager

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

class GeneralPG(bpy.types.PropertyGroup):
    # Get list of environments
    env_enum_prop_lst = envManager.get_env_lst_enum_property()

    # Active Environment
    active_environment: EnumProperty(
        name="Active Environment",
        description="Defines the project directory structure.",
        items=env_enum_prop_lst,
        default='default'
    )


def draw(preference, context, layout):
    """
    Draw general addon settings.
    """
    column = layout.column()

    row = column.row()
    row.label(text='General Blue Hole addon settings.')

    row = column.row()
    row.label(text='These settings apply to the addon itself rather than a specific environment.')

    row = column.row()
    row.label(text='No option provided for now.')


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

def register():
    bpy.utils.register_class(GeneralPG)


def unregister():
    bpy.utils.unregister_class(GeneralPG)

