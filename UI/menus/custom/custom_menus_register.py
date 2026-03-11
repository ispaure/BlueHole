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
    containers_menu,
    directories_menu,
    export_send_menus,
    food_menu,
    help_menu,
    import_menu,
    misc_menu,
    music_menu,
    sort_menu,
    source_control_menu,
    theme_menu,
    update_menus,
    header_menu,
)


# ----------------------------------------------------------------------------------------------------------------------
# MODULES

CUSTOM_MENU_MODULES = (
    containers_menu,
    directories_menu,
    export_send_menus,
    food_menu,
    help_menu,
    import_menu,
    misc_menu,
    music_menu,
    sort_menu,
    source_control_menu,
    theme_menu,
    update_menus,
)

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
    # Register Custom Menus
    for menu in CUSTOM_MENU_MODULES:
        menu.register()
    # Register Header Menu
    header_menu.register()


# Unregister
def unregister():
    # Unregister Custom Menus
    for menu in CUSTOM_MENU_MODULES:
        menu.unregister()
    # Unregister Header Menu
    header_menu.unregister()
