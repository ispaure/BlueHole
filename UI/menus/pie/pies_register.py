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


# Addon
from . import (
    add_pies,
    curve_pies,
    directories_pies,
    global_pies,
    import_export_pies,
    mesh_pies,
    object_pies,
    sculpt_pies,
    source_control_pies,
    uv_pies,
)


# ----------------------------------------------------------------------------------------------------------------------
# MODULES

PIE_MODULES = (
    add_pies,
    curve_pies,
    directories_pies,
    global_pies,
    import_export_pies,
    mesh_pies,
    object_pies,
    sculpt_pies,
    source_control_pies,
    uv_pies,
)


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


# Register
def register():
    # Register Pies
    for pie in PIE_MODULES:
        pie.register()


# Unregister
def unregister():
    # Unregister Pies
    for pie in PIE_MODULES:
        pie.unregister()
