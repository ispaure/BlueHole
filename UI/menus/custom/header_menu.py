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
from ....preferences.prefs import *
from ....blenderUtils import blenderFile
from . import (
    containers_menu,
    directories_menu,
    export_send_menus,
    help_menu,
    import_menu,
    misc_menu,
    source_control_menu,
    update_menus,
)

# ----------------------------------------------------------------------------------------------------------------------
# MENUS

header_bh_name = '𝐁𝐋𝐔𝐄 𝐇𝐎𝐋𝐄'


# Header Blue Hole Menu
class BLUE_HOLE_MT_top_menu(bpy.types.Menu):
    bl_label = header_bh_name
    bl_idname = "BLUE_HOLE_MT_top_menu"

    def draw(self, context):

        self.bl_label = f'{header_bh_name} [' + str(prefs().general.active_environment.lower()) + ']'
        layout = self.layout
        layout.operator('wm.set_active_environment')
        layout.menu(directories_menu.BLUE_HOLE_MT_directories.bl_idname, icon='FILE_FOLDER')
        layout.menu(containers_menu.BLUE_HOLE_MT_containers.bl_idname, icon='OUTLINER')

        layout.separator()

        # Export/Send only when engine selected AND scene saved
        engine_ok = prefs().bridge.active_game_engine != 'disabled'
        scene_saved = blenderFile.has_blend_filepath()
        if engine_ok and scene_saved:
            layout.menu(export_send_menus.BLUE_HOLE_MT_send.bl_idname, text=export_send_menus.BLUE_HOLE_MT_send.build_ui_label(), icon='UV_SYNC_SELECT')
            layout.menu(export_send_menus.BLUE_HOLE_MT_export.bl_idname, text='Export (to DIRECTORY)', icon='EXPORT')
        elif not scene_saved:
            col = layout.column()
            col.enabled = False
            col.operator(
                "wm.bh_disabled_notice",
                text="Save .blend file to Export/Send",
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

        layout.menu(import_menu.BLUE_HOLE_MT_import.bl_idname, icon='IMPORT')
        # layout.menu("BLUE_HOLE_MT_import_export")
        if prefs().sc.source_control_enable:
            layout.menu(source_control_menu.BLUE_HOLE_MT_source_control.bl_idname, icon='CHECKMARK')
        layout.menu(misc_menu.BLUE_HOLE_MT_misc.bl_idname)

        layout.separator()

        layout.menu(help_menu.BLUE_HOLE_MT_help.bl_idname, icon='HELP')
        layout.menu(update_menus.BLUE_HOLE_MT_update_deluxe.bl_idname, icon='UV_SYNC_SELECT')

    def menu_draw(self, context):
        self.layout.menu("BLUE_HOLE_MT_top_menu")


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


# Register
def register():
    bpy.utils.register_class(BLUE_HOLE_MT_top_menu)
    bpy.types.TOPBAR_MT_editor_menus.append(BLUE_HOLE_MT_top_menu.menu_draw)


# Unregister
def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(BLUE_HOLE_MT_top_menu.menu_draw)
    bpy.utils.unregister_class(BLUE_HOLE_MT_top_menu)
