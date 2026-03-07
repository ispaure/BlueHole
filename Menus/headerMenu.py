"""
This loads up the Blue Hole Header Menu in Blender.
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
from ..preferences.prefs import *
from ..blenderUtils import blenderFile
from .menu import BLUE_HOLE_MT_export, BLUE_HOLE_MT_send

# ----------------------------------------------------------------------------------------------------------------------
# MENUS

header_bh_name = '𝐁𝐋𝐔𝐄 𝐇𝐎𝐋𝐄'


# Header Blue Hole Menu
class BLUE_HOLE_MT_top_menu(bpy.types.Menu):
    bl_label = header_bh_name

    def draw(self, context):

        self.bl_label = f'{header_bh_name} [' + str(prefs().general.active_environment.lower()) + ']'
        layout = self.layout
        layout.operator('wm.set_active_environment')
        layout.menu("BLUE_HOLE_MT_directories", icon='FILE_FOLDER')
        layout.menu("BLUE_HOLE_MT_containers", icon='OUTLINER')

        layout.separator()

        # Export/Send only when engine selected AND scene saved
        engine_ok = prefs().bridge.active_game_engine != 'disabled'
        scene_saved = blenderFile.has_blend_filepath()
        if engine_ok and scene_saved:
            layout.menu("BLUE_HOLE_MT_send", text=BLUE_HOLE_MT_send.build_ui_label(), icon='UV_SYNC_SELECT')
            layout.menu("BLUE_HOLE_MT_export", text='Export (to DIRECTORY)', icon='EXPORT')
        elif not scene_saved:
            col = layout.column()
            col.enabled = False
            col.operator(
                "wm.bh_disabled_notice",
                text="Save the .blend file to Export/Send",
                icon='ERROR'
            )
        elif not engine_ok:
            col = layout.column()
            col.enabled = False
            col.operator(
                "wm.bh_disabled_notice",
                text="Select a Game Engine to Export/Send",
                icon='ERROR'
            )
        layout.separator()

        layout.menu("BLUE_HOLE_MT_import", icon='IMPORT')
        # layout.menu("BLUE_HOLE_MT_import_export")
        if prefs().sc.source_control_enable:
            layout.menu("BLUE_HOLE_MT_source_control", icon='CHECKMARK')
        layout.menu("BLUE_HOLE_MT_misc")

        layout.separator()

        layout.menu("BLUE_HOLE_MT_help", icon='HELP')
        layout.menu("BLUE_HOLE_MT_update_deluxe", icon='UV_SYNC_SELECT')

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
        layout.menu("BLUE_HOLE_MT_sort")
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
