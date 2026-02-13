"""
Operators for themes
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

# Blender
import bpy

# Blue Hole
from ..blenderUtils import uiUtils

# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class SetThemeBlenderDark(bpy.types.Operator):

    bl_idname = "wm.bh_theme_blender_dark"
    bl_label = "Dark"

    def execute(self, context):
        uiUtils.set_theme('blender_dark')
        return {'FINISHED'}


class SetThemeBlenderLight(bpy.types.Operator):

    bl_idname = "wm.bh_theme_blender_light"
    bl_label = "Light"

    def execute(self, context):
        uiUtils.set_theme('blender_light')
        return {'FINISHED'}


class SetThemeDeepGrey(bpy.types.Operator):

    bl_idname = "wm.bh_theme_deep_grey"
    bl_label = "Deep Grey"

    def execute(self, context):
        uiUtils.set_theme('deep_grey')
        return {'FINISHED'}


class SetThemeMODO(bpy.types.Operator):

    bl_idname = "wm.bh_theme_modo"
    bl_label = "MODO"

    def execute(self, context):
        uiUtils.set_theme('modo')
        return {'FINISHED'}


class SetThemeSky(bpy.types.Operator):

    bl_idname = "wm.bh_theme_sky"
    bl_label = "Sky"

    def execute(self, context):
        uiUtils.set_theme('sky')
        return {'FINISHED'}


class SetThemeWhite(bpy.types.Operator):

    bl_idname = "wm.bh_theme_white"
    bl_label = "White"

    def execute(self, context):
        uiUtils.set_theme('white')
        return {'FINISHED'}


class SetThemeZen(bpy.types.Operator):

    bl_idname = "wm.bh_theme_zen"
    bl_label = "Zen"

    def execute(self, context):
        uiUtils.set_theme('zen')
        return {'FINISHED'}


class SetThemeZenDark(bpy.types.Operator):

    bl_idname = "wm.bh_theme_zendark"
    bl_label = "Zen Dark"

    def execute(self, context):
        uiUtils.set_theme('zen_dark')
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (SetThemeBlenderDark,
           SetThemeBlenderLight,
           SetThemeDeepGrey,
           SetThemeMODO,
           SetThemeSky,
           SetThemeWhite,
           SetThemeZen,
           SetThemeZenDark
           )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators
