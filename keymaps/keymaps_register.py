"""
This manages the keymaps.
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

from .pie import pie_keymaps_register
from . import mesh_keymaps_register
from . import navigation_keymaps_register
from . import object_keymaps_register
from . import pipeline_keymaps_register
from . import sculpt_keymaps_register
from . import selection_keymaps_register
from . import transform_keymaps_register
from . import uv_keymaps_register

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

keymap_module_lst = (
    mesh_keymaps_register,
    navigation_keymaps_register,
    object_keymaps_register,
    pipeline_keymaps_register,
    sculpt_keymaps_register,
    selection_keymaps_register,
    transform_keymaps_register,
    uv_keymaps_register,
)


def register():

    # Register Keymaps
    for module in keymap_module_lst:
        module.register()

    # Register Pie Menus
    pie_keymaps_register.register()


def unregister():

    # Unregister Pie Menus
    pie_keymaps_register.unregister()

    # Unregister Keymaps
    for module in reversed(keymap_module_lst):
        module.unregister()


def refresh():
    unregister()
    register()
