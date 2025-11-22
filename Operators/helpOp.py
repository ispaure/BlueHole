"""
Operators for help resources
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
# IMPORTS


import bpy
import BlueHole.blenderUtils.fileUtils as fileUtils
import BlueHole.blenderUtils.configUtils as configUtils


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


class SendToUnityDoc(bpy.types.Operator):

    bl_idname = "wm.bh_send_unity_doc"
    bl_label = '[[[[ ' + 'UNITY' + ' ]]]]'
    bl_description = 'Opens the Documentation for the Blender to Unity Bridge'

    def execute(self, context):
        fileUtils.open_url(configUtils.get_url_db_value('Tutorial', 'unity_bridge'))
        return{'FINISHED'}


class SendToUnrealDoc(bpy.types.Operator):

    bl_idname = "wm.bh_send_unreal_doc"
    bl_label = '[[[[ ' + 'UNREAL' + ' ]]]]'
    bl_description = 'Opens the documentation for the Blender to Unreal Bridge'

    def execute(self, context):
        fileUtils.open_url(configUtils.get_url_db_value('Tutorial', 'unreal_bridge'))
        return{'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (OpenGuide,
           OpenKeymapsList,
           OpenPieMenusList,
           SubmitFeedback,
           JoinBHDiscord,
           SendToUnityDoc,
           SendToUnrealDoc)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators
