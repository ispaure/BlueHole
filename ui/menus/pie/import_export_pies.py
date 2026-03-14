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
from ....Lib.commonUtils.debugUtils import *
from ....preferences.prefs import *
from ....operators_handling.operator_action import draw_operator_action
from ....operators_handling.actions import pie_actions
from .entries import addon_entries

# ----------------------------------------------------------------------------------------------------------------------
# USER DEFINED SETTINGS

name = filename = os.path.basename(__file__)


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENUS


# Pie Global-Import/Export
class BLUEHOLE_MT_pie_global_import_export(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_import_export"
    bl_label = "Blue Hole: Import/Export"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        addon_entries.send_all_asset_containers(pie)
        # 6 - RIGHT
        addon_entries.send_selected_asset_containers(pie)
        # 2 - BOTTOM
        draw_operator_action(pie, pie_actions.PIE_GLOBAL_EXTRA, context, text='More...')
        # 8 - TOP
        draw_operator_action(pie, pie_actions.PIE_GLOBAL_DIRS, context, text='Open Directories...')
        # 7 - TOP - LEFT
        if prefs().sc.source_control_enable:
            match prefs().sc.source_control_solution:
                case 'perforce':
                    draw_operator_action(pie, pie_actions.PIE_GLOBAL_SOURCE_CONTROL, context, text='Source Control (Perforce)...', icon='CHECKMARK')
                case 'plastic-scm':
                    draw_operator_action(pie, pie_actions.PIE_GLOBAL_SOURCE_CONTROL, context, text='Source Control (Plastic SCM)...', icon='CHECKMARK')
                case 'git':
                    draw_operator_action(pie, pie_actions.PIE_GLOBAL_SOURCE_CONTROL, context, text='Source Control (Git)...', icon='CHECKMARK')
        else:
            addon_entries.sc_disabled(pie)
        # 9 - TOP - RIGHT
        draw_operator_action(pie, pie_actions.PIE_ADD_ASSET_CONTAINER, context, text='Asset Containers...')
        # 1 - BOTTOM - LEFT
        addon_entries.batch_export_selection_resource_folder(pie)
        # 3 - BOTTOM - RIGHT
        pie.separator()


# Pie Global-Import/Export
class BLUEHOLE_MT_pie_global_extra(bpy.types.Menu):
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
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (
    BLUEHOLE_MT_pie_global_import_export,
    BLUEHOLE_MT_pie_global_extra,
)


def register():
    log(Severity.DEBUG, name, 'Registering')
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    log(Severity.DEBUG, name, 'Unregistering')
    for cls in classes:
        bpy.utils.unregister_class(cls)
