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

import os
import bpy

from ....Lib.commonUtils.debugUtils import *
from ....actions.operator_action import draw_operator_action
from ....actions.actions import pie_actions
from .entries import blender_entries
from .entries.third_party import hardops_entries, machin3_entries, interactivetools_entries


# ----------------------------------------------------------------------------------------------------------------------
# USER DEFINED SETTINGS

name = filename = os.path.basename(__file__)


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENUS


# Context: 3D Viewport (Object Mode)
# Hotkey: Shift+RMB
class BLUEHOLE_MT_pie_object_tool(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_object_tool"
    bl_label = "Blue Hole: Object > Tools (Modifiers)"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        hardops_entries.lattice(pie)
        # 6 - RIGHT
        hardops_entries.array(pie)
        # 2 - BOTTOM
        hardops_entries.modifier_toggle(pie)
        # 8 - TOP
        draw_operator_action(pie, pie_actions.PIE_OBJECT_TOOL_MORE, context, text='Modifiers Options...')
        # 7 - TOP - LEFT
        blender_entries.mod_weighted_nrm(pie)
        # 9 - TOP - RIGHT
        hardops_entries.twist_array(pie)
        # 3 - BOTTOM - LEFT
        hardops_entries.subdiv_modifier(pie)
        # 1 - BOTTOM - RIGHT
        hardops_entries.radial_array(pie)


# No Hotkey; Submenu
class BLUEHOLE_MT_pie_object_tool_more(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_object_tool_more"
    bl_label = "Blue Hole: Object > Tools (Modifiers) > More"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        pie.separator()
        # 2 - BOTTOM
        hardops_entries.apply_modifier(pie)
        # 8 - TOP
        blender_entries.link_transfer_data(pie)
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 3 - BOTTOM - LEFT
        pie.separator()
        # 1 - BOTTOM - RIGHT
        pie.separator()


# Context: 3D Viewport (Mesh)
# Hotkey: Shift + S + Drag Mouse in any direction
class BLUEHOLE_MT_pie_object_hide(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_object_hide"
    bl_label = "Blue Hole: Object > Hide"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        blender_entries.object_reveal_all(pie)
        # 6 - RIGHT
        machin3_entries.isolate_selection_toggle(pie)
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        blender_entries.object_hide_selection(pie)
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# Context: 3D Viewport (Object Mode)
# Hotkey: Ctrl+RMB
class BLUEHOLE_MT_pie_object_action(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_object_action"
    bl_label = "Blue Hole: Object > Action"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        blender_entries.clear_location(pie)
        # 6 - RIGHT
        blender_entries.object_join(pie)
        # 2 - BOTTOM
        draw_operator_action(pie, pie_actions.PIE_OBJECT_ACTION_MORE, context, text='More...')
        # 8 - TOP
        draw_operator_action(pie, pie_actions.PIE_OBJECT_ACTION_SELECT, context, text='Select...')
        # 7 - TOP - LEFT
        blender_entries.apply_transform(pie)
        # 9 - TOP - RIGHT
        interactivetools_entries.quick_pivot_setup(pie)
        # 1 - BOTTOM - LEFT
        blender_entries.clear_parent(pie)
        # 3 - BOTTOM - RIGHT
        blender_entries.make_parent(pie)


# No Hotkey; Submenu
class BLUEHOLE_MT_pie_object_action_select(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_object_action_select"
    bl_label = "Blue Hole: Object > Action > Select"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        blender_entries.select_children_recursive(pie)
        # 6 - RIGHT
        blender_entries.select_parent(pie)
        # 2 - BOTTOM
        blender_entries.object_invert(pie)
        # 8 - TOP
        blender_entries.select_grouped(pie)
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# No Hotkey; Submenu
class BLUEHOLE_MT_pie_object_action_more(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_object_action_more"
    bl_label = "Blue Hole: Object > Action > More"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        hardops_entries.clean_mesh(pie)
        # 6 - RIGHT
        hardops_entries.apply_modifier_2(pie)
        # 2 - BOTTOM
        blender_entries.make_instances_real(pie)
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        blender_entries.convert_to_curves(pie)
        # 9 - TOP - RIGHT
        blender_entries.convert_to_mesh(pie)
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (
    BLUEHOLE_MT_pie_object_hide,
    BLUEHOLE_MT_pie_object_tool,
    BLUEHOLE_MT_pie_object_tool_more,
    BLUEHOLE_MT_pie_object_action,
    BLUEHOLE_MT_pie_object_action_select,
    BLUEHOLE_MT_pie_object_action_more,
)


def register():
    log(Severity.DEBUG, name, 'Registering')
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    log(Severity.DEBUG, name, 'Unregistering')
    for cls in classes:
        bpy.utils.unregister_class(cls)
