"""
Adds Blue Hole Blender Operators [Help]
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
import BlueHole.blenderUtils.fileUtils as fileUtils
import BlueHole.blenderUtils.debugUtils as debugUtils
from BlueHole.blenderUtils.languageUtils import loc_str as loc_str
from BlueHole.blenderUtils.uiUtils import show_label as show_label
import BlueHole.envUtils.envUtils as envUtils
import BlueHole.blenderUtils.configUtils as configUtils


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

# Start of File Debug Message
debugUtils.print_debug_msg('\nLoading Help Menu and Operators...', show_verbose)

# ----------------------------------------------------------------------------------------------------------------------
# MENUS


class BLUE_HOLE_MT_help(bpy.types.Menu):
    bl_label = loc_str('help_n_updates')

    def draw(self, context):
        layout = self.layout

        # Show Documentation Section
        show_label('DOCUMENTATION', layout)
        layout.operator(OpenGuide.bl_idname, icon='URL')
        layout.operator(OpenKeymapsList.bl_idname, icon='URL')
        layout.operator(OpenPieMenusList.bl_idname, icon='URL')

        # Show Submit Feedback Button
        layout.separator()
        layout.operator(SubmitFeedback.bl_idname, icon='WINDOW')
        layout.operator(JoinBHDiscord.bl_idname, icon='FUND')

        layout.separator()
        # Draw additional operators from the active environment (if available)
        envUtils.draw_current_env_menu_items('globalHelp', layout)


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS

class OpenGuide(bpy.types.Operator):

    bl_idname = "wm.bh_help_open_guide"
    bl_label = 'Website'
    bl_description = 'Opens the Blue Hole Official Website'

    def execute(self, context):
        url = configUtils.get_url_db_value('BlueHoleWebsite', 'home')
        fileUtils.open_url(url)
        return {'FINISHED'}


class OpenKeymapsList(bpy.types.Operator):

    bl_idname = "wm.bh_help_open_keymaps_list"
    bl_label = 'Keymaps List [Deluxe Only]'
    bl_description = 'Opens the Keymaps List (Only available to Blue Hole Deluxe Users)'

    def execute(self, context):
        url = configUtils.get_url_db_value('BlueHoleWebsite', 'keymaps')
        fileUtils.open_url(url)
        return {'FINISHED'}


class OpenPieMenusList(bpy.types.Operator):

    bl_idname = "wm.bh_help_open_pie_menus_list"
    bl_label = 'Pie Menus List [Deluxe Only]'
    bl_description = 'Opens the Pie Menus List (Only available to Blue Hole Deluxe Users with Pie Menu Editor addon)'

    def execute(self, context):
        url = configUtils.get_url_db_value('BlueHoleWebsite', 'pie_menus')
        fileUtils.open_url(url)
        return {'FINISHED'}


class SubmitFeedback(bpy.types.Operator):

    bl_idname = "wm.bh_help_submit_feedback"
    bl_label = 'Give Feedback'
    bl_description = 'Send an email to Marc-André Voyer with feedback on Blue Hole'

    def execute(self, context):
        url = configUtils.get_url_db_value('Contact', 'mail')
        fileUtils.open_url(url)
        return {'FINISHED'}


class JoinBHDiscord(bpy.types.Operator):

    bl_idname = "wm.bh_join_bh_discord"
    bl_label = 'Join the Blue Hole Discord'
    bl_description = 'Opens a link to join the Blue Hole Discord Group'

    def execute(self, context):
        url = configUtils.get_url_db_value('Contact', 'discord')
        fileUtils.open_url(url)
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (OpenGuide,
           OpenKeymapsList,
           OpenPieMenusList,
           SubmitFeedback,
           JoinBHDiscord)


# Register
def register():
    # Register Menu
    bpy.utils.register_class(BLUE_HOLE_MT_help)
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    # Unregister Menu
    bpy.utils.unregister_class(BLUE_HOLE_MT_help)
    # Unregister Operators
    for cls in classes:
        bpy.utils.unregister_class(cls)


# ----------------------------------------------------------------------------------------------------------------------
# End of File Debug Message
debugUtils.print_debug_msg('Help Menu and Operators Loaded!', show_verbose)
