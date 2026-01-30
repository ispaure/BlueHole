"""
This loads up the Blue Hole Header Menu in Blender.
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

from BlueHole.preferences.prefsCls import *

# ----------------------------------------------------------------------------------------------------------------------
# MENUS

bh_name = 'Blue Hole'


# Header Blue Hole Menu
class BLUE_HOLE_MT_top_menu(bpy.types.Menu):
    bl_label = f'{bh_name} [' + str(prefs().env.active_environment.lower()) + ']'

    def draw(self, context):
        # import BlueHole.__init__
        self.bl_label = f'{bh_name} [' + str(prefs().env.active_environment.lower()) + ']'
        layout = self.layout
        layout.operator('wm.set_active_environment')
        layout.menu("BLUE_HOLE_MT_help", icon='HELP')
        layout.separator()
        layout.menu("BLUE_HOLE_MT_directories", icon='OUTLINER')
        # layout.menu("BLUE_HOLE_MT_scene")
        layout.separator()
        layout.menu("BLUE_HOLE_MT_sort")
        layout.menu("BLUE_HOLE_MT_import", icon='IMPORT')
        layout.menu("BLUE_HOLE_MT_export", icon='EXPORT')
        layout.menu("BLUE_HOLE_MT_send", icon='UV_SYNC_SELECT')
        layout.separator()
        # layout.menu("BLUE_HOLE_MT_import_export")
        if prefs().sc.source_control_enable:
            layout.menu("BLUE_HOLE_MT_source_control", icon='CHECKMARK')
        layout.menu("BLUE_HOLE_MT_misc")

    def menu_draw(self, context):
        self.layout.menu("BLUE_HOLE_MT_top_menu")
        # self.layout.menu("BLUE_HOLE_MT_top_menu", icon='MOD_OCEAN')


# Import / Export Sub-Menu
class BLUE_HOLE_MT_import_export(bpy.types.Menu):
    bl_label = "Import/Export"

    def draw(self, context):
        layout = self.layout
        layout.menu("BLUE_HOLE_MT_import")
        layout.menu("BLUE_HOLE_MT_export")
        layout.menu("BLUE_HOLE_MT_send")
        layout.menu("BLUE_HOLE_MT_source_control")
        layout.menu("BLUE_HOLE_MT_open")


# Misc Sub-Menu
class BLUE_HOLE_MT_misc(bpy.types.Menu):
    bl_label = 'Misc'

    def draw(self, context):
        layout = self.layout
        layout.menu("BLUE_HOLE_MT_themes", icon='IMAGE_RGB_ALPHA')
        layout.menu("BLUE_HOLE_MT_food_delivery", icon='TEMP')
        layout.menu("BLUE_HOLE_MT_music", icon='SOUND')


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (BLUE_HOLE_MT_misc,
           BLUE_HOLE_MT_import_export,
           BLUE_HOLE_MT_top_menu
           )


# Register
def register():
    # bpy.utils.register_class(BLUE_HOLE_MT_top_menu)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(BLUE_HOLE_MT_top_menu.menu_draw)


# Unregister
def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(BLUE_HOLE_MT_top_menu.menu_draw)
    for cls in classes:
        bpy.utils.unregister_class(cls)
