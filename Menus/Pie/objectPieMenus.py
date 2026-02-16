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
from ...commonUtils.debugUtils import *
from ...blenderUtils import filterUtils, addonUtils
from .utilities import *
from .Button import hardopsPieButton, blenderPieButton, machin3PieButton, interactiveToolsPieButton


# ----------------------------------------------------------------------------------------------------------------------
# USER DEFINED SETTINGS

name = filename = os.path.basename(__file__)


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENUS


# Context: 3D Viewport (Object Mode)
# Hotkey: Shift+RMB
class MT_pie_object_tool(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_object_tool"
    bl_label = "Blue Hole: Object > Tools (Modifiers)"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        hardopsPieButton.lattice(pie)
        # 6 - RIGHT
        hardopsPieButton.array(pie)
        # 2 - BOTTOM
        hardopsPieButton.modifier_toggle(pie)
        # 8 - TOP
        open_pie_menu(pie, MT_pie_object_tool_more.bl_idname, 'Modifiers Options...')
        # 7 - TOP - LEFT
        blenderPieButton.mod_weighted_nrm(pie)
        # 9 - TOP - RIGHT
        hardopsPieButton.twist_array(pie)
        # 3 - BOTTOM - LEFT
        hardopsPieButton.subdiv_modifier(pie)
        # 1 - BOTTOM - RIGHT
        hardopsPieButton.radial_array(pie)


# No Hotkey; Submenu
class MT_pie_object_tool_more(bpy.types.Menu):
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
        hardopsPieButton.apply_modifier(pie)
        # 8 - TOP
        blenderPieButton.link_transfer_data(pie)
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
class MT_pie_object_hide(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_object_hide"
    bl_label = "Blue Hole: Object > Hide"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        blenderPieButton.object_reveal_all(pie)
        # 6 - RIGHT
        machin3PieButton.isolate_selection_toggle(pie)
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        blenderPieButton.object_hide_selection(pie)
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
class MT_pie_object_action(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_object_action"
    bl_label = "Blue Hole: Object > Action"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        blenderPieButton.clear_location(pie)
        # 6 - RIGHT
        blenderPieButton.object_join(pie)
        # 2 - BOTTOM
        open_pie_menu(pie, MT_pie_object_action_more.bl_idname, 'More...')
        # 8 - TOP
        open_pie_menu(pie, MT_pie_object_action_select.bl_idname, 'Select...')
        # 7 - TOP - LEFT
        blenderPieButton.apply_transform(pie)
        # 9 - TOP - RIGHT
        interactiveToolsPieButton.quick_pivot_setup(pie)
        # 1 - BOTTOM - LEFT
        blenderPieButton.clear_parent(pie)
        # 3 - BOTTOM - RIGHT
        blenderPieButton.make_parent(pie)


# No Hotkey; Submenu
class MT_pie_object_action_select(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_object_action_select"
    bl_label = "Blue Hole: Object > Action > Select"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        blenderPieButton.select_children_recursive(pie)
        # 6 - RIGHT
        blenderPieButton.select_parent(pie)
        # 2 - BOTTOM
        blenderPieButton.object_select_all(pie)
        # 8 - TOP
        blenderPieButton.select_grouped(pie)
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# No Hotkey; Submenu
class MT_pie_object_action_more(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_object_action_more"
    bl_label = "Blue Hole: Object > Action > More"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        blenderPieButton.clean_mesh(pie)
        # 6 - RIGHT
        hardopsPieButton.apply_modifier_2(pie)
        # 2 - BOTTOM
        blenderPieButton.make_instances_real(pie)
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        blenderPieButton.convert_to_curves(pie)
        # 9 - TOP - RIGHT
        blenderPieButton.convert_to_mesh(pie)
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (MT_pie_object_hide,
           MT_pie_object_tool,
           MT_pie_object_tool_more,
           MT_pie_object_action,
           MT_pie_object_action_select,
           MT_pie_object_action_more)


def register():
    log(Severity.DEBUG, name, 'Registering')
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    log(Severity.DEBUG, name, 'Unregistering')
    for cls in classes:
        bpy.utils.unregister_class(cls)
