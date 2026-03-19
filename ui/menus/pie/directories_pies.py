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
import os

# Blue Hole
from ....Lib.commonUtils.debugUtils import *
from ....preferences.prefs import *
from .entries import addon_entries

# ----------------------------------------------------------------------------------------------------------------------
# USER DEFINED SETTINGS

name = filename = os.path.basename(__file__)


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENUS


class BLUEHOLE_MT_pie_global_dirs(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_dirs"
    bl_label = "Blue Hole: Directories"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        if prefs().sourcecontrol.source_control_enable and prefs().sourcecontrol.source_control_solution == 'perforce':
            addon_entries.open_workspace_root(pie)
        else:
            pie.separator()
        # 6 - RIGHT
        match prefs().bridge.active_game_engine:
            case 'unreal':
                addon_entries.open_source_content(pie)
            case 'unity':
                addon_entries.open_unity_assets(pie)
            case 'disabled':
                pie.separator()
        # 2 - BOTTOM
        addon_entries.open_dir_final(pie)
        # 8 - TOP
        addon_entries.open_dir_scene(pie)
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        addon_entries.open_dir_user_res(pie)
        # 3 - BOTTOM - RIGHT
        addon_entries.open_dir_res(pie)


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (
    BLUEHOLE_MT_pie_global_dirs,
)


def register():
    log(Severity.DEBUG, name, 'Registering')
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    log(Severity.DEBUG, name, 'Unregistering')
    for cls in classes:
        bpy.utils.unregister_class(cls)
