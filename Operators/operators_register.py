"""
Register and unregister all operator modules.
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
    add_ops,
    box_xray_ops,
    directory_ops,
    environment_ops,
    export_send_ops,
    external_addon_ops,
    food_ops,
    help_ops,
    import_ops,
    music_ops,
    other_ops,
    save_ops,
    sort_ops,
    source_control_ops,
    theme_ops,
)

# ----------------------------------------------------------------------------------------------------------------------
# MODULES

OPERATOR_MODULES = (
    add_ops,
    box_xray_ops,
    directory_ops,
    environment_ops,
    export_send_ops,
    external_addon_ops,
    food_ops,
    help_ops,
    import_ops,
    music_ops,
    other_ops,
    save_ops,
    sort_ops,
    source_control_ops,
    theme_ops,
)

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
    for module in OPERATOR_MODULES:
        module.register()


def unregister():
    for module in reversed(OPERATOR_MODULES):
        module.unregister()
