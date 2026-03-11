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

from .pie import pie_keymap
from ..preferences.prefs import prefs

# ----------------------------------------------------------------------------------------------------------------------
# CODE

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
    try:
        if prefs().pie.enable_pie_menus:
            pie_keymap.register()
    except Exception:
        pass


def unregister():
    pie_keymap.unregister()
