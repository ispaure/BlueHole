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

from .custom import custom_menus_register
from .append import append_menus_register
from .override import override_menus_register
from .pie import pies_register

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
    custom_menus_register.register()
    append_menus_register.register()
    override_menus_register.register()
    pies_register.register()


# Unregister
def unregister():
    custom_menus_register.unregister()
    append_menus_register.unregister()
    override_menus_register.unregister()
    pies_register.unregister()
