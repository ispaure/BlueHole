"""
Adds Blue Hole Blender Operators [Open]
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "GNU General Public License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

import bpy

import BlueHole.blenderUtils.debugUtils as debugUtils
import BlueHole.envUtils.envUtils as envUtils


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

# Start of File Debug Message
debugUtils.print_debug_msg('\nLoading Open Menu and Operators...', show_verbose)


# ----------------------------------------------------------------------------------------------------------------------
# MENUS

class BLUE_HOLE_MT_open(bpy.types.Menu):
    bl_label = "Open"

    def draw(self, context):
        layout = self.layout
        # Draw additional operators from the active environment (if available)
        envUtils.draw_current_env_menu_items('globalOpen', layout)


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class OpenNull(bpy.types.Operator):

    bl_idname = "wm.bh_open_null"
    bl_label = " "
    bl_description = "Does nothing"

    def execute(self, context):
        pass
        return {'FINISHED'}


class OpenNull2(bpy.types.Operator):

    bl_idname = "wm.bh_open_null2"
    bl_label = " "
    bl_description = "Does nothing"

    def execute(self, context):
        pass
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (OpenNull2,
           OpenNull
           )


# Register
def register():
    # Register Menu
    bpy.utils.register_class(BLUE_HOLE_MT_open)
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    # Unregister Menu
    bpy.utils.unregister_class(BLUE_HOLE_MT_open)
    # Unregister Operators
    for cls in classes:
        bpy.utils.unregister_class(cls)


# ----------------------------------------------------------------------------------------------------------------------
# End of File Debug Message
debugUtils.print_debug_msg('Open Menu and Operators Loaded!', show_verbose)
