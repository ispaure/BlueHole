"""
Adds Blue Hole Blender Operators [Themes]
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

import BlueHole.blenderUtils.uiUtils as themeUtils
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
debugUtils.print_debug_msg('\nLoading Themes Menu and Operators...', show_verbose)


# ----------------------------------------------------------------------------------------------------------------------
# MENUS

class BLUE_HOLE_MT_themes(bpy.types.Menu):
    bl_label = "Themes"

    def draw(self, context):
        layout = self.layout
        for cls in classes:
            layout.operator(cls.bl_idname, icon='IMAGE_RGB_ALPHA')
        # Draw additional operators from the active environment (if available)
        envUtils.draw_current_env_menu_items('globalThemes', layout)


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS

class SetThemeBlenderDark(bpy.types.Operator):

    bl_idname = "wm.bh_theme_blender_dark"
    bl_label = "Dark"

    def execute(self, context):
        themeUtils.set_theme('blender_dark')
        return {'FINISHED'}


class SetThemeBlenderLight(bpy.types.Operator):

    bl_idname = "wm.bh_theme_blender_light"
    bl_label = "Light"

    def execute(self, context):
        themeUtils.set_theme('blender_light')
        return {'FINISHED'}


class SetThemeDeepGrey(bpy.types.Operator):

    bl_idname = "wm.bh_theme_deep_grey"
    bl_label = "Deep Grey"

    def execute(self, context):
        themeUtils.set_theme('deep_grey')
        return {'FINISHED'}


class SetThemeMODO(bpy.types.Operator):

    bl_idname = "wm.bh_theme_modo"
    bl_label = "MODO"

    def execute(self, context):
        themeUtils.set_theme('modo')
        return {'FINISHED'}


class SetThemeSky(bpy.types.Operator):

    bl_idname = "wm.bh_theme_sky"
    bl_label = "Sky"

    def execute(self, context):
        themeUtils.set_theme('sky')
        return {'FINISHED'}


class SetThemeWhite(bpy.types.Operator):

    bl_idname = "wm.bh_theme_white"
    bl_label = "White"

    def execute(self, context):
        themeUtils.set_theme('white')
        return {'FINISHED'}


class SetThemeZen(bpy.types.Operator):

    bl_idname = "wm.bh_theme_zen"
    bl_label = "Zen"

    def execute(self, context):
        themeUtils.set_theme('zen')
        return {'FINISHED'}


class SetThemeZenDark(bpy.types.Operator):

    bl_idname = "wm.bh_theme_zendark"
    bl_label = "Zen Dark"

    def execute(self, context):
        themeUtils.set_theme('zen_dark')
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


# Register
def register():
    # Register Menu
    bpy.utils.register_class(BLUE_HOLE_MT_themes)
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    # Unregister Menu
    bpy.utils.unregister_class(BLUE_HOLE_MT_themes)
    # Unregister Operators
    for cls in classes:
        bpy.utils.unregister_class(cls)


# ----------------------------------------------------------------------------------------------------------------------
# End of File Debug Message
debugUtils.print_debug_msg('Themes Menu and Operators Loaded!', show_verbose)
