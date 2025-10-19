# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "GNU General Public License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

from BlueHole.blenderUtils.debugUtils import print_debug_msg as print_debug_msg
import BlueHole.blenderUtils.addon as addon
import BlueHole.blenderUtils.exportUtils2 as exportUtils2


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

import bpy
from bpy.types import (
        Menu,
        Operator,
        )
import os


# Pie Global-Help
class PIE_MT_Global_Help(Menu):
    bl_idname = "PIE_MT_global_help"
    bl_label = "Blue Hole: Help"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        pie.operator("wm.bh_help_open_keymaps_list", text="Keymaps List", icon='URL')
        # 2 - BOTTOM
        pie.operator("wm.bh_help_submit_feedback", text="Submit Feedback", icon='FUND')
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.operator("wm.bh_help_open_guide", text="Online Guide", icon='HELP')
        # 1 - BOTTOM - LEFT
        pie.menu("PIE_MT_global_theme", text="Themes", icon='IMAGE_RGB')
        # 3 - BOTTOM - RIGHT
        pie.operator("wm.bh_help_open_pie_menus_list", text="Pie Menus List", icon='URL')


# Pie Global-Theme
class PIE_MT_Global_Theme(Menu):
    bl_idname = "PIE_MT_global_theme"
    bl_label = "Blue Hole: Theme"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("wm.bh_theme_zen", text="Zen Light")
        # 6 - RIGHT
        pie.operator("wm.bh_theme_zendark", text="Zen Dark")
        # 2 - BOTTOM
        pie.operator("wm.bh_theme_sky", text="Sky")
        # 8 - TOP
        pie.operator("wm.bh_theme_modo", text="Modo")
        # 7 - TOP - LEFT
        pie.operator("wm.bh_theme_blender_light", text="Blender Light")
        # 9 - TOP - RIGHT
        pie.operator("wm.bh_theme_blender_dark", text="Blender Dark")
        # 1 - BOTTOM - LEFT
        pie.operator("wm.bh_theme_white", text="White")
        # 3 - BOTTOM - RIGHT
        pie.operator("wm.bh_theme_deep_grey", text="Deep Grey")


# Pie Global-Directories
class PIE_MT_Global_Directories(Menu):
    bl_idname = "PIE_MT_global_directories"
    bl_label = "Blue Hole: Directories"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        if addon.preference().sourcecontrol.source_control_enable and addon.preference().sourcecontrol.source_control_solution == 'perforce':
            pie.operator("wm.bh_dir_open_workspace_root", text="Open WORKSPACE ROOT Folder", icon='FILEBROWSER')
        elif os.path.exists(exportUtils2.get_unity_exp_path()):
            pie.operator('wm.bh_dir_open_unity_assets_current_exp_dir', text="Open UNITY ASSETS CURRENT EXPORT Folder", icon='FILEBROWSER')
        elif os.path.exists(addon.preference().environment.sc_path) or os.path.exists(addon.preference().environment.sc_path_alternate) or os.path.exists(addon.preference().environment.sc_path_mac) or os.path.exists(addon.preference().environment.sc_path_mac_alternate):
            pie.operator("wm.bh_dir_open_source_content_root_dir", text="Open SOURCECONTENT ROOT Folder", icon='FILEBROWSER')
        else:
            pie.separator()
        # 6 - RIGHT
        pie.operator("wm.bh_dir_open_speedtree_msh", text="Open SPEEDTREE MSH Folder", icon='FILEBROWSER')
        # 2 - BOTTOM
        pie.operator("wm.bh_dir_open_final", text="Open FINAL Folder", icon='FILEBROWSER')
        # 8 - TOP
        pie.operator("wm.bh_dir_open_root", text="Open ROOT Folder", icon='FILEBROWSER')
        # 7 - TOP - LEFT
        pie.operator("wm.bh_scene_add_asset_hierarchy", text="Add ASSET HIERARCHY", icon='OUTLINER')
        # 9 - TOP - RIGHT
        pie.operator("wm.bh_dir_open_resources", text="Open RESOURCES Folder", icon='FILEBROWSER')
        # 1 - BOTTOM - LEFT
        pie.operator("wm.bh_dir_open_user_resource", text="Open USER RESOURCE PATH", icon='FILE_BLEND')
        # 3 - BOTTOM - RIGHT
        pie.operator("wm.bh_dir_open_references", text="Open REFERENCES Folder", icon='FILEBROWSER')


# Pie Global-Import/Export
class PIE_MT_Import_Export(Menu):
    bl_idname = "PIE_MT_global_import_export"
    bl_label = "Blue Hole: Import/Export"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.separator()
        # pie.menu("PIE_MT_global_import", text="Import...", icon='IMPORT')
        # 6 - RIGHT
        pie.operator("wm.call_menu_pie", text="Export...", icon='EXPORT').name = 'PIE_MT_global_export'
        # 2 - BOTTOM
        pie.operator("wm.call_menu_pie", text="Send...", icon='UV_SYNC_SELECT').name = 'PIE_MT_global_send'
        # 8 - TOP
        if addon.preference().sourcecontrol.source_control_enable:
            if addon.preference().sourcecontrol.source_control_solution == 'perforce':
                pie.operator("wm.call_menu_pie", text="Source Control (Perforce)...", icon='CHECKMARK').name = 'PIE_MT_global_source_control'
            if addon.preference().sourcecontrol.source_control_solution == 'plastic-scm':
                pie.operator("wm.call_menu_pie", text="Source Control (Plastic SCM)...", icon='CHECKMARK').name = 'PIE_MT_global_source_control'
            if addon.preference().sourcecontrol.source_control_solution == 'git':
                pie.operator("wm.call_menu_pie", text="Source Control (Git)...", icon='CHECKMARK').name = 'PIE_MT_global_source_control'
        else:
            pie.separator()
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# Pie Global-Import/Export
class PIE_MT_Export(Menu):
    bl_idname = "PIE_MT_global_export"
    bl_label = "Blue Hole: Export"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        pie.operator("wm.bh_batch_export_select_to_resources")
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
class PIE_MT_Send(Menu):
    bl_idname = "PIE_MT_global_send"
    bl_label = "Blue Hole: Send"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("wm.bh_send_unreal", text="Send *ALL* (Asset Hierarchies) to Unreal", icon='UV_SYNC_SELECT')
        # 6 - RIGHT
        pie.operator("wm.bh_send_unity", text="Send *ALL* (Asset Hierarchies) to Unity", icon='UV_SYNC_SELECT')
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.operator("wm.bh_send_selected_unreal", text="Send Selected (Asset Hierarchies) to Unreal", icon='UV_SYNC_SELECT')
        # 3 - BOTTOM - RIGHT
        pie.operator("wm.bh_send_selected_unity", text="Send Selected (Asset Hierarchies) to Unity", icon='UV_SYNC_SELECT')


# Pie Global-Source Control
class PIE_MT_Source_Control(Menu):
    bl_idname = "PIE_MT_global_source_control"
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
        pie.operator("wm.bh_p4_check_out_blend", text="Check Out Current Blend Scene", icon='CHECKMARK')
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.operator("wm.bh_p4_display_server_info", text="Display Server Info", icon='INFO')
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# Pie Global-Order
class PIE_MT_Order(Menu):
    bl_idname = "PIE_MT_global_order"
    bl_label = "Blue Hole: Order"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        pie.operator("wm.bh_foodorder_sthubert", text="Order St-Hubert", icon='MOD_TIME')
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        pie.operator("wm.bh_foodorder_ubereats", text="Order Uber Eats", icon='MOD_TIME')
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


classes = (
    PIE_MT_Global_Help,
    PIE_MT_Global_Theme,
    PIE_MT_Global_Directories,
    PIE_MT_Import_Export,
    PIE_MT_Export,
    PIE_MT_Send,
    PIE_MT_Source_Control,
    PIE_MT_Order
    )

addon_keymaps = []


def register():
    for cls in classes:
        print_debug_msg('Loading Pie Menu: ' + cls.bl_idname, show_verbose)
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
