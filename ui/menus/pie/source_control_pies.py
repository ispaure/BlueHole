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

# Blender
import bpy

# Blue Hole
from ....Lib.commonUtils.debugUtils import *
from .entries import addon_entries

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

TOOL_NAME = 'source_control_pies'

# ----------------------------------------------------------------------------------------------------------------------
# PIE MENUS


# Pie Global-Import/Export
class BLUEHOLE_MT_pie_global_source_control(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_source_control"
    bl_label = "Blue Hole: Source Control"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        pie.separator()
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        addon_entries.perforce_checkout(pie)
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        addon_entries.perforce_server_info(pie)
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

classes = (
    BLUEHOLE_MT_pie_global_source_control,
)


def register():
    log(Severity.DEBUG, TOOL_NAME, 'Registering...')

    for cls in classes:
        bpy.utils.register_class(cls)
        log(Severity.DEBUG, TOOL_NAME, f'Registered: {cls.__name__}')

    log(Severity.DEBUG, TOOL_NAME, 'Registration complete')


def unregister():
    log(Severity.DEBUG, TOOL_NAME, 'Unregistering...')

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        log(Severity.DEBUG, TOOL_NAME, f'Unregistered: {cls.__name__}')

    log(Severity.DEBUG, TOOL_NAME, 'Unregistration complete')
