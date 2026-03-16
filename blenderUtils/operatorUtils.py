# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'


# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS

import bpy

# ----------------------------------------------------------------------------------------------------------------------
# HELPER FUNCTIONS


def op_exists(op_idname: str) -> bool:
    """
    True if operator idname like 'hops.mod_lattice' is registered.
    """
    try:
        cat, name = op_idname.split(".", 1)
        op = getattr(getattr(bpy.ops, cat), name)
        op.get_rna_type()   # raises if not registered
        return True
    except Exception:
        return False
