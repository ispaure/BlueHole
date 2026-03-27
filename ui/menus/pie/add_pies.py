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

from ....Lib.commonUtils.debugUtils import *
from ....actions.operator_action import draw_operator_action
from ....actions.actions import pie_actions

from .entries import blender_entries, addon_entries
from .entries.third_party import machin3_entries

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

TOOL_NAME = 'add_pies'

# ----------------------------------------------------------------------------------------------------------------------
# PIE MENUS


# Context: 3D Viewport (Global)
# Hotkey: Shift + A + Drag Mouse in any direction
class BLUEHOLE_MT_pie_add(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_add"
    bl_label = "Blue Hole: Add"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        blender_entries.add_cylinder(pie)
        # 6 - RIGHT
        blender_entries.add_cube(pie)
        # 2 - BOTTOM
        draw_operator_action(pie, pie_actions.PIE_ADD_MORE, context, text='More...')
        # 8 - TOP
        blender_entries.add_sphere(pie)
        # 7 - TOP - LEFT
        machin3_entries.add_quadsphere(pie)
        # 9 - TOP - RIGHT
        draw_operator_action(pie, pie_actions.PIE_ADD_ASSET_CONTAINER, context, text='Asset Containers...')
        # 1 - BOTTOM - LEFT
        blender_entries.add_plane(pie)
        # blender_entries.add_nurbs_path(pie) TODO: Find new spot for this one
        # 3 - BOTTOM - RIGHT
        blender_entries.add_bezier_curve(pie)


# No Hotkey; Submenu
class BLUEHOLE_MT_pie_add_more(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_add_more"
    bl_label = "Blue Hole: Add > More"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        blender_entries.add_light_point(pie)
        # 6 - RIGHT
        blender_entries.add_light_spot(pie)
        # 2 - BOTTOM
        blender_entries.add_text(pie)
        # 8 - TOP
        blender_entries.add_light_area(pie)
        # 7 - TOP - LEFT
        blender_entries.add_light_probe(pie)
        # 9 - TOP - RIGHT
        blender_entries.add_light_sun(pie)
        # 1 - BOTTOM - LEFT
        blender_entries.load_ref_img(pie)
        # 3 - BOTTOM - RIGHT
        blender_entries.add_bezier_circle(pie)


class BLUEHOLE_MT_pie_add_asset_container(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_add_asset_container"
    bl_label = "Asset Containers"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        addon_entries.add_asset_hierarchy(pie)
        # 2 - BOTTOM
        addon_entries.add_asset_mesh(pie)
        # 8 - TOP
        addon_entries.add_asset_collection(pie)
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


classes = (
    BLUEHOLE_MT_pie_add,
    BLUEHOLE_MT_pie_add_more,
    BLUEHOLE_MT_pie_add_asset_container,
)


def register():
    log(Severity.DEBUG, TOOL_NAME, 'Registering...')

    for cls in classes:
        bpy.utils.register_class(cls)
        log(Severity.DEBUG, TOOL_NAME, f'Registered: {cls.__name__}')

    log(Severity.DEBUG, TOOL_NAME, 'Registration complete')


def unregister():
    log(Severity.DEBUG, TOOL_NAME, 'Unregistering...')

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        log(Severity.DEBUG, TOOL_NAME, f'Unregistered: {cls.__name__}')

    log(Severity.DEBUG, TOOL_NAME, 'Unregistration complete')
