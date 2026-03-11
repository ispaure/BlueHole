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
from ....Lib.commonUtils.debugUtils import *
from .entries import addon_entries
from .utilities import *

# ----------------------------------------------------------------------------------------------------------------------
# USER DEFINED SETTINGS

name = filename = os.path.basename(__file__)


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENUS


# Pie Global-Help
class MT_pie_global_help(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_help"
    bl_label = "Blue Hole: Help"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        addon_entries.open_keymaps_list(pie)
        # 2 - BOTTOM
        addon_entries.submit_feedback(pie)
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        addon_entries.open_guide(pie)
        # 1 - BOTTOM - LEFT
        open_pie_menu(pie, MT_pie_global_theme, text='Themes...', icon='IMAGE_RGB')
        # 3 - BOTTOM - RIGHT
        addon_entries.open_pie_menus_list(pie)


# Pie Global-Theme
class MT_pie_global_theme(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_theme"
    bl_label = "Blue Hole: Theme"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        addon_entries.apply_theme_zen_light(pie)
        # 6 - RIGHT
        addon_entries.apply_theme_zen_dark(pie)
        # 2 - BOTTOM
        addon_entries.apply_theme_sky(pie)
        # 8 - TOP
        addon_entries.apply_theme_modo(pie)
        # 7 - TOP - LEFT
        addon_entries.apply_theme_blender_light(pie)
        # 9 - TOP - RIGHT
        addon_entries.apply_theme_blender_dark(pie)
        # 1 - BOTTOM - LEFT
        addon_entries.apply_theme_white(pie)
        # 3 - BOTTOM - RIGHT
        addon_entries.apply_theme_deep_grey(pie)

# Pie Global-Order
class MT_pie_global_order(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_order"
    bl_label = "Blue Hole: Order"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        addon_entries.order_st_hubert(pie)
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        addon_entries.order_uber_eats(pie)
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (
    MT_pie_global_help,
    MT_pie_global_theme,
    MT_pie_global_order,
)


def register():
    log(Severity.DEBUG, name, 'Registering')
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    log(Severity.DEBUG, name, 'Unregistering')
    for cls in classes:
        bpy.utils.unregister_class(cls)
