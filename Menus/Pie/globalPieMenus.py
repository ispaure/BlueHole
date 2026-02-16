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

# System
import os

# Blender
import bpy

# Blue Hole
from ...Lib.commonUtils.debugUtils import *
from ...preferences.prefs import *
from .Button import blueHolePieButton
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
        blueHolePieButton.open_keymaps_list(pie)
        # 2 - BOTTOM
        blueHolePieButton.submit_feedback(pie)
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        blueHolePieButton.open_guide(pie)
        # 1 - BOTTOM - LEFT
        open_pie_menu(pie, MT_pie_global_theme.bl_idname, 'Themes...', 'IMAGE_RGB')
        # 3 - BOTTOM - RIGHT
        blueHolePieButton.open_pie_menus_list(pie)


# Pie Global-Theme
class MT_pie_global_theme(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_theme"
    bl_label = "Blue Hole: Theme"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        blueHolePieButton.apply_theme_zen_light(pie)
        # 6 - RIGHT
        blueHolePieButton.apply_theme_zen_dark(pie)
        # 2 - BOTTOM
        blueHolePieButton.apply_theme_sky(pie)
        # 8 - TOP
        blueHolePieButton.apply_theme_modo(pie)
        # 7 - TOP - LEFT
        blueHolePieButton.apply_theme_blender_light(pie)
        # 9 - TOP - RIGHT
        blueHolePieButton.apply_theme_blender_dark(pie)
        # 1 - BOTTOM - LEFT
        blueHolePieButton.apply_theme_white(pie)
        # 3 - BOTTOM - RIGHT
        blueHolePieButton.apply_theme_deep_grey(pie)


# Pie Global-Directories
class MT_pie_global_dirs(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_dirs"
    bl_label = "Blue Hole: Directories"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        blueHolePieButton.if_available_open_workspace_or_source_root(pie)
        # 6 - RIGHT
        blueHolePieButton.open_dir_speedtree(pie)
        # 2 - BOTTOM
        blueHolePieButton.open_dir_final(pie)
        # 8 - TOP
        blueHolePieButton.open_scene_final(pie)
        # 7 - TOP - LEFT
        blueHolePieButton.add_asset_hierarchy(pie)
        # 9 - TOP - RIGHT
        blueHolePieButton.open_dir_res(pie)
        # 1 - BOTTOM - LEFT
        blueHolePieButton.open_dir_user_res(pie)
        # 3 - BOTTOM - RIGHT
        blueHolePieButton.open_dir_ref(pie)


# Pie Global-Import/Export
class MT_pie_global_import_export(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_import_export"
    bl_label = "Blue Hole: Import/Export"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        open_pie_menu(pie, MT_pie_global_extra.bl_idname, 'Extra...')
        # 6 - RIGHT
        open_pie_menu(pie, MT_pie_global_export.bl_idname, 'Export...', 'EXPORT')
        # 2 - BOTTOM
        open_pie_menu(pie, MT_pie_global_send.bl_idname, 'Send...', 'UV_SYNC_SELECT')
        # 8 - TOP
        if prefs().sc.source_control_enable:
            match prefs().sc.source_control_solution:
                case 'perforce':
                    open_pie_menu(pie, MT_pie_global_source_control.bl_idname, 'Source Control (Perforce)...', 'CHECKMARK')
                case 'plastic-scm':
                    open_pie_menu(pie, MT_pie_global_source_control.bl_idname, 'Source Control (Plastic SCM)...', 'CHECKMARK')
                case 'git':
                    open_pie_menu(pie, MT_pie_global_source_control.bl_idname, 'Source Control (Git)...', 'CHECKMARK')
        else:
            pie.operator("wm.disabled_source_control", text="Can't Show; Source Control disabled!!!", icon='ERROR')
        # 7 - TOP - LEFT
        open_pie_menu(pie, MT_pie_global_dirs.bl_idname, 'Open Directories...')
        # 9 - TOP - RIGHT
        blueHolePieButton.add_asset_hierarchy(pie)
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# Pie Global-Import/Export
class MT_pie_global_extra(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_extra"
    bl_label = "Blue Hole: Extra"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        pie.separator()
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        # TODO: Check if this works in vanilla - probably needs an addon and added to "if addon enabled" workflow
        op = pie.operator('wm.tool_set_by_id', text='Select Box X-Ray')
        op.name = 'object_tool.select_box_xray'
        # 3 - BOTTOM - RIGHT
        pie.separator()


# Pie Global-Import/Export
class MT_pie_global_export(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_export"
    bl_label = "Blue Hole: Export"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        pie.separator()
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# Pie Global-Send
class MT_pie_global_send(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_send"
    bl_label = "Blue Hole: Send"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        blueHolePieButton.send_unreal_all(pie)
        # 6 - RIGHT
        blueHolePieButton.send_unity_all(pie)
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        blueHolePieButton.send_unreal_selected(pie)
        # 3 - BOTTOM - RIGHT
        blueHolePieButton.send_unity_selected(pie)


# Pie Global-Source Control
class MT_pie_global_source_control(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_source_control"
    bl_label = "Blue Hole: Source Control"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        pie.separator()
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        blueHolePieButton.perforce_checkout(pie)
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        blueHolePieButton.perforce_server_info(pie)
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


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
        blueHolePieButton.order_st_hubert(pie)
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        blueHolePieButton.order_uber_eats(pie)
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
classes = (MT_pie_global_help,
           MT_pie_global_theme,
           MT_pie_global_dirs,
           MT_pie_global_import_export,
           MT_pie_global_export,
           MT_pie_global_send,
           MT_pie_global_source_control,
           MT_pie_global_order,
           MT_pie_global_extra)


def register():
    log(Severity.DEBUG, name, 'Registering')
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    log(Severity.DEBUG, name, 'Unregistering')
    for cls in classes:
        bpy.utils.unregister_class(cls)
