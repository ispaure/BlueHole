"""
Operators that did not fit in another category
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

# Blender
import bpy
from bpy.props import *
from ..commonUtils.webUtils import open_url

# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class WM_OT_URLOpen(bpy.types.Operator):
    """Open a website in the web-browser"""
    bl_idname = "wm.bh_open_url"
    bl_label = ""
    bl_options = {'INTERNAL'}

    url: StringProperty(
        name="URL",
        description="URL to open",
    )

    def execute(self, _context):
        open_url(self.url)
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
# classes = (WM_OT_URLOpen,
#            BH_OT_MOD_Decimate)


def register():
    bpy.utils.register_class(WM_OT_URLOpen)
    # for cls in classes:
    #     bpy.utils.register_class(cls)


# Unregister
def unregister():
    bpy.utils.unregister_class(WM_OT_URLOpen)
    # for cls in classes:
    #     bpy.utils.unregister_class(cls)  # Unregister Operators
