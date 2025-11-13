"""
Adds Blue Hole Blender Operators [Source Control]
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

import bpy
import BlueHole.blenderUtils.sourceControlUtils as scUtils
import BlueHole.blenderUtils.debugUtils as debugUtils
import BlueHole.envUtils.envUtils as envUtils


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS

# Start of File Debug Message
debugUtils.print_debug_msg('\nLoading Source Control Menu and Operators...', show_verbose)


# ----------------------------------------------------------------------------------------------------------------------
# MENUS

class BLUE_HOLE_MT_source_control(bpy.types.Menu):
    bl_label = "Source Control"

    def draw(self, context):
        layout = self.layout
        layout.operator(P4CheckOutCurrentScene.bl_idname, icon = 'CHECKMARK')
        layout.operator(P4DisplayServerInfo.bl_idname, icon = 'INFO')
        # Draw additional operators from the active environment (if available)
        envUtils.draw_current_env_menu_items('globalSourceControl', layout)


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS

class P4CheckOutCurrentScene(bpy.types.Operator):

    bl_idname = "wm.bh_p4_check_out_blend"
    bl_label = "Check Out Current Blend Scene"

    def execute(self, context):
        scUtils.sc_check_blend()
        return {'FINISHED'}


class P4DisplayServerInfo(bpy.types.Operator):

    bl_idname = "wm.bh_p4_display_server_info"
    bl_label = "Display Server Info"

    def execute(self, context):
        scUtils.sc_dialog_box_info()
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (P4CheckOutCurrentScene,
           P4DisplayServerInfo
           )


# Register
def register():
    # Register Menu
    bpy.utils.register_class(BLUE_HOLE_MT_source_control)
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    # Unregister Menu
    bpy.utils.unregister_class(BLUE_HOLE_MT_source_control)
    # Unregister Operators
    for cls in classes:
        bpy.utils.unregister_class(cls)


# ----------------------------------------------------------------------------------------------------------------------
# End of File Debug Message
debugUtils.print_debug_msg('Source Control Menu and Operators Loaded!', show_verbose)
