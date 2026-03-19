"""
Blue Hole Menus
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

# Blue Hole
from ....operators import help_ops, source_control_ops, external_addon_ops
from ....preferences.prefs import *
from ....blenderUtils import blenderFile

# ----------------------------------------------------------------------------------------------------------------------
# MENUS


class BLUE_HOLE_MT_source_control(bpy.types.Menu):
    bl_label = "Source Control"
    bl_idname = "BLUE_HOLE_MT_source_control"

    def draw(self, context):
        layout = self.layout
        if prefs().sourcecontrol.source_control_solution == 'perforce':
            layout.operator(help_ops.PerforceDoc.bl_idname, icon='KEYTYPE_EXTREME_VEC')

            if blenderFile.has_blend_filepath():
                layout.operator(source_control_ops.P4CheckOutCurrentScene.bl_idname, icon='CHECKMARK')
            else:
                col = layout.column()
                col.enabled = False
                col.operator(
                    external_addon_ops.BH_OT_disabled_notice.bl_idname,
                    text='Save .blend file to enable checkout',
                    icon='ERROR'
                )

            layout.operator(source_control_ops.P4DisplayServerInfo.bl_idname, icon='INFO')


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (
    BLUE_HOLE_MT_source_control,
)


# Register
def register():
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
