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
from BlueHole.blenderUtils.debugUtils import *
import BlueHole.blenderUtils.addon as addon
import BlueHole.blenderUtils.exportUnity as exportUnity
import os


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
        pie.menu(MT_pie_global_theme.bl_idname, text="Themes...", icon='IMAGE_RGB')
        # 3 - BOTTOM - RIGHT
        pie.operator("wm.bh_help_open_pie_menus_list", text="Pie Menus List", icon='URL')


# Pie Global-Theme
class MT_pie_global_theme(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_theme"
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
class MT_pie_global_dirs(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_dirs"
    bl_label = "Blue Hole: Directories"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        if addon.preference().sourcecontrol.source_control_enable and addon.preference().sourcecontrol.source_control_solution == 'perforce':
            pie.operator("wm.bh_dir_open_workspace_root", text="Open WORKSPACE ROOT Folder", icon='FILEBROWSER')
        elif exportUnity.get_unity_exp_dir_path(quiet=True) is not None and os.path.exists(str(exportUnity.get_unity_exp_dir_path(quiet=True))):
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
class MT_pie_global_import_export(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_import_export"
    bl_label = "Blue Hole: Import/Export"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("wm.call_menu_pie", text="Extra...").name = MT_pie_global_extra.bl_idname
        # 6 - RIGHT
        pie.operator("wm.call_menu_pie", text="Export...", icon='EXPORT').name = MT_pie_global_export.bl_idname
        # 2 - BOTTOM
        pie.operator("wm.call_menu_pie", text="Send...", icon='UV_SYNC_SELECT').name = MT_pie_global_send.bl_idname
        # 8 - TOP
        if addon.preference().sourcecontrol.source_control_enable:
            if addon.preference().sourcecontrol.source_control_solution == 'perforce':
                pie.operator("wm.call_menu_pie", text="Source Control (Perforce)...", icon='CHECKMARK').name = MT_pie_global_source_control.bl_idname
            if addon.preference().sourcecontrol.source_control_solution == 'plastic-scm':
                pie.operator("wm.call_menu_pie", text="Source Control (Plastic SCM)...", icon='CHECKMARK').name = MT_pie_global_source_control.bl_idname
            if addon.preference().sourcecontrol.source_control_solution == 'git':
                pie.operator("wm.call_menu_pie", text="Source Control (Git)...", icon='CHECKMARK').name = MT_pie_global_source_control.bl_idname
        else:
            pie.operator("wm.disabled_source_control", text="Can't Show; Source Control disabled!!!", icon='ERROR')
        # 7 - TOP - LEFT
        pie.operator("wm.call_menu_pie", text="Open Directories...").name = MT_pie_global_dirs.bl_idname
        # 9 - TOP - RIGHT
        pie.operator('wm.bh_scene_add_asset_hierarchy', text='Add Asset Hierarchy')
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
        op = pie.operator('wm.tool_set_by_id', text='Select Box X-Ray')
        op.name = 'object_tool.select_box_xray'
        # 3 - BOTTOM - RIGHT
        pie.operator("arp.arp_export_fbx_panel", text='Auto-Rig Pro FBX Export')


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
class MT_pie_global_send(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_send"
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
class MT_pie_global_order(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_order"
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
