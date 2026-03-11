"""
Register and unregister all menu modules.
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

from . import (
    VIEW3D_MT_add
)

# ----------------------------------------------------------------------------------------------------------------------
# MODULES

APPEND_MENU_MODULES = (
    VIEW3D_MT_add,
)

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():

    # Register Append Menus
    for menu in APPEND_MENU_MODULES:
        menu.register()


# Unregister
def unregister():
    # Unregister Append Menus
    for menu in APPEND_MENU_MODULES:
        menu.unregister()
