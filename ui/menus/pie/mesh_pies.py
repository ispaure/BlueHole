# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = 'MIT License'
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'


# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS

import os
import bpy

from ....Lib.commonUtils.debugUtils import *
from ....operators.model_ops import WM_OT_MergeLast
from ....actions.operator_action import draw_operator_action
from ....actions.actions import pie_actions
from .entries import blender_entries
from .entries.third_party import (
    hardops_entries,
    angle_tool_entries,
    machin3_entries,
    interactivetools_entries,
    zenuv_entries,
    dreamuv_entries,
)


# ----------------------------------------------------------------------------------------------------------------------
# USER DEFINED SETTINGS

name = filename = os.path.basename(__file__)


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENUS


# Context: 3D Viewport (Mesh)
# Hotkey: Shift + S + Drag Mouse in any direction
class BLUEHOLE_MT_pie_mesh_hide(bpy.types.Menu):
    bl_idname = 'BLUEHOLE_MT_pie_mesh_hide'
    bl_label = 'Blue Hole Pie Menu: Mesh > Hide'

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        blender_entries.mesh_reveal_all(pie)
        # 6 - RIGHT
        blender_entries.mesh_isolate_selection(pie)
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        blender_entries.mesh_hide_selection(pie)
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# Context: 3D Viewport (Mesh)
# Hotkey: Shift + RMB
# Changes options displayed if Vertex/Edge/Face Mode
class BLUEHOLE_MT_pie_mesh_tool(bpy.types.Menu):
    bl_idname = 'BLUEHOLE_MT_pie_mesh_tool'
    bl_label = 'Blue Hole: Mesh > Tools'

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        # TODO: Says no parameter vertex_only, will need to fix this.
        blender_entries.mesh_bevel(pie)
        # 6 - RIGHT
        blender_entries.extrude_move_normal(pie)
        # 2 - BOTTOM
        blender_entries.mesh_inset_faces(pie)
        # 8 - TOP
        blender_entries.loop_cut_slide(pie)
        # 7 - TOP - LEFT
        blender_entries.mesh_knife_tool(pie)
        # pie.operator(WM_OT_CustomKnifeTool.bl_idname, text="Knife Topology Tool", icon='SNAP_MIDPOINT')
        # 9 - TOP - RIGHT
        blender_entries.extrude_move_shrink_fatten(pie)
        # 1 - BOTTOM - LEFT
        blender_entries.bridge_edge_loops(pie)
        # 3 - BOTTOM - RIGHT
        blender_entries.shrink_fatten(pie)


# Context: 3D Viewport (Mesh)
# Hotkey: Ctrl + RMB
class BLUEHOLE_MT_pie_mesh_action(bpy.types.Menu):
    bl_idname = 'BLUEHOLE_MT_pie_mesh_action'
    bl_label = 'Blue Hole: Mesh > Action'

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        active_select_mode = tuple(bpy.context.scene.tool_settings.mesh_select_mode)

        # Vertex Menu
        if active_select_mode == (True, False, False):
            # 4 - LEFT
            pie.operator(WM_OT_MergeLast.bl_idname)
            # 6 - RIGHT
            blender_entries.merge_center(pie)
            # 2 - BOTTOM
            draw_operator_action(pie, pie_actions.PIE_VERTEX_ACTION_MORE, context, text='More...')
            # 8 - TOP
            draw_operator_action(pie, pie_actions.PIE_VERTEX_ACTION_SELECT, context, text='Select...')
            # 7 - TOP - LEFT
            machin3_entries.straighten(pie)
            # 9 - TOP - RIGHT
            interactivetools_entries.quick_pivot_setup(pie)
            # 1 - BOTTOM - LEFT
            blender_entries.remove_doubles(pie)
            # 3 - BOTTOM - RIGHT
            blender_entries.vert_connect_path(pie)

        # Edge Menu
        if active_select_mode == (False, True, False):
            # 4 - LEFT
            blender_entries.edge_split(pie)
            # 6 - RIGHT
            blender_entries.edge_crease(pie)
            # 2 - BOTTOM
            draw_operator_action(pie, pie_actions.PIE_EDGE_ACTION_MORE, context, text='More...')
            # 8 - TOP
            draw_operator_action(pie, pie_actions.PIE_EDGE_ACTION_SELECT, context, text='Select...')
            # 7 - TOP - LEFT
            blender_entries.fill_grid(pie)
            # 9 - TOP - RIGHT
            interactivetools_entries.quick_pivot_setup(pie)
            # 1 - BOTTOM - LEFT
            blender_entries.clear_sharp(pie)
            # 3 - BOTTOM - RIGHT
            blender_entries.mark_sharp(pie)

        # Face Menu
        if active_select_mode == (False, False, True):
            # 4 - LEFT
            blender_entries.mesh_split(pie)
            # 6 - RIGHT
            blender_entries.mesh_separate(pie)
            # 2 - BOTTOM
            draw_operator_action(pie, pie_actions.PIE_FACE_ACTION_MORE, context, text='More...')
            # 8 - TOP
            draw_operator_action(pie, pie_actions.PIE_FACE_ACTION_SELECT, context, text='Select...')
            # 7 - TOP - LEFT
            interactivetools_entries.quick_lattice(pie)
            # 9 - TOP - RIGHT
            interactivetools_entries.quick_pivot_setup(pie)
            # 1 - BOTTOM - LEFT
            blender_entries.merge_by_distance(pie)
            # 3 - BOTTOM - RIGHT
            blender_entries.separate_loose_parts(pie)


# Context: 3D Viewport Mesh Edit (Vertex/Edge/Vert)
# Hotkey: Ctrl+Alt+Shift+RMB
class BLUEHOLE_MT_pie_mesh_action_uvspecial(bpy.types.Menu):
    bl_idname = 'BLUEHOLE_MT_pie_mesh_action_uvspecial'  # named wrong
    bl_label = 'Blue Hole: Mesh > Action (UV Special)'

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        blender_entries.clear_seam(pie)
        # 6 - RIGHT
        blender_entries.mark_seam(pie)
        # 2 - BOTTOM
        blender_entries.uv_unwrap_conformal(pie)
        # 8 - TOP
        dreamuv_entries.hotspotter(pie)
        # 7 - TOP - LEFT
        zenuv_entries.fix_trim_loop(pie)
        # 9 - TOP - RIGHT
        zenuv_entries.git_to_trim_2(pie)
        # 1 - BOTTOM - LEFT
        zenuv_entries.auto_unwrap(pie)
        # 3 - BOTTOM - RIGHT
        zenuv_entries.mark_by_angle(pie)


# No Hotkey; Submenu
class BLUEHOLE_MT_pie_vertex_action_select(bpy.types.Menu):
    bl_idname = 'BLUEHOLE_MT_pie_vertex_action_select'
    bl_label = 'Blue Hole: Vertex > Action > Select'

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        pie.separator()
        # 2 - BOTTOM
        blender_entries.invert_select(pie)
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        blender_entries.select_loose_geo(pie)
        # 3 - BOTTOM - RIGHT
        blender_entries.select_random_face(pie)


# No Hotkey; Submenu
class BLUEHOLE_MT_pie_vertex_action_more(bpy.types.Menu):
    bl_idname = 'BLUEHOLE_MT_pie_vertex_action_more'
    bl_label = 'Blue Hole: Vertex > Action > More'

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        blender_entries.mesh_symmetrize(pie)
        # 2 - BOTTOM
        interactivetools_entries.quick_flatten(pie)
        # 8 - TOP
        blender_entries.transform_to_sphere(pie)
        # 7 - TOP - LEFT
        interactivetools_entries.quick_lattice(pie)
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        hardops_entries.vertex_to_circle(pie)


# No Hotkey; Submenu
class BLUEHOLE_MT_pie_edge_action_select(bpy.types.Menu):
    bl_idname = 'BLUEHOLE_MT_pie_edge_action_select'
    bl_label = 'Blue Hole: Edge > Action > Select'

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        interactivetools_entries.smart_select_ring(pie)
        # 6 - RIGHT
        blender_entries.select_sharp(pie)
        # 2 - BOTTOM
        blender_entries.invert_select(pie)
        # 8 - TOP
        interactivetools_entries.smart_select_loop(pie)
        # 7 - TOP - LEFT
        blender_entries.loop_inner_region(pie)
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# No Hotkey; Submenu
class BLUEHOLE_MT_pie_edge_action_more(bpy.types.Menu):
    bl_idname = 'BLUEHOLE_MT_pie_edge_action_more'
    bl_label = 'Blue Hole: Edge > Action > More'

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        blender_entries.rotate_selected_edge_ccw(pie)
        # 6 - RIGHT
        blender_entries.rotate_selected_edge(pie)
        # 2 - BOTTOM
        hardops_entries.quick_pipe(pie)
        # 8 - TOP
        angle_tool_entries.mesh_angle(pie)
        # 7 - TOP - LEFT
        blender_entries.collapse_edge(pie)
        # 9 - TOP - RIGHT
        blender_entries.subdivide_edge_ring(pie)
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# No Hotkey; Submenu
class BLUEHOLE_MT_pie_face_action_select(bpy.types.Menu):
    bl_idname = 'BLUEHOLE_MT_pie_face_action_select'
    bl_label = 'Blue Hole: Face > Action > Select'

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        blender_entries.select_random_face(pie)
        # 6 - RIGHT
        blender_entries.link_flat_faces(pie)
        # 2 - BOTTOM
        blender_entries.invert_select(pie)
        # 8 - TOP
        blender_entries.boundary_loop(pie)
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        blender_entries.select_loose_geo(pie)
        # 3 - BOTTOM - RIGHT
        pie.separator()


# No Hotkey; Submenu
class BLUEHOLE_MT_pie_face_action_more(bpy.types.Menu):
    bl_idname = 'BLUEHOLE_MT_pie_face_action_more'
    bl_label = 'Blue Hole: Face > Action > More'

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        blender_entries.unsubdivide(pie)
        # 6 - RIGHT
        blender_entries.subdivide(pie)
        # 2 - BOTTOM
        blender_entries.flip_normals(pie)
        # 8 - TOP
        blender_entries.poke_face(pie)
        # 7 - TOP - LEFT
        blender_entries.recalculate_normals_outside(pie)
        # 9 - TOP - RIGHT
        blender_entries.recalculate_normals_inside(pie)
        # 1 - BOTTOM - LEFT
        blender_entries.triangulate_faces(pie)
        # 3 - BOTTOM - RIGHT
        blender_entries.convert_tris_to_quads(pie)


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (
    BLUEHOLE_MT_pie_mesh_hide,
    BLUEHOLE_MT_pie_mesh_tool,
    BLUEHOLE_MT_pie_mesh_action,
    BLUEHOLE_MT_pie_mesh_action_uvspecial,
    BLUEHOLE_MT_pie_vertex_action_more,
    BLUEHOLE_MT_pie_vertex_action_select,
    BLUEHOLE_MT_pie_edge_action_more,
    BLUEHOLE_MT_pie_edge_action_select,
    BLUEHOLE_MT_pie_face_action_more,
    BLUEHOLE_MT_pie_face_action_select,
)


def register():
    log(Severity.DEBUG, name, 'Registering')
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    log(Severity.DEBUG, name, 'Unregistering')
    for cls in classes:
        bpy.utils.unregister_class(cls)
