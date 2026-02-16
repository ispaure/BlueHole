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
from ...Lib.commonUtils.debugUtils import *
from .Button import blenderPieButton, hardopsPieButton, angleToolPieButton, machin3PieButton, interactiveToolsPieButton
from .utilities import *


# ----------------------------------------------------------------------------------------------------------------------
# USER DEFINED SETTINGS

name = filename = os.path.basename(__file__)


# ----------------------------------------------------------------------------------------------------------------------
# OPERATOR


# class WM_OT_CustomKnifeTool(bpy.types.Operator):
#     """Activates the Custom Knife Tool"""
#     # TODO: Change this into a normal pie.operator using the knowledge I have gained since.
#     bl_idname = "wm.bh_custom_knife_tool"
#     bl_label = ""
#     bl_options = {'INTERNAL'}
#
#     def execute(self, _context):
#         bpy.ops.mesh.knife_tool('INVOKE_DEFAULT',
#                                 use_occlude_geometry=True,
#                                 only_selected=False,
#                                 xray=True,
#                                 visible_measurements='NONE',
#                                 angle_snapping='NONE',
#                                 angle_snapping_increment=0.261799,
#                                 wait_for_input=True)
#         return {'FINISHED'}


class WM_OT_MergeLast(bpy.types.Operator):
    """
    Custom operator for this because the option is not always available which may break the Pie Menus
    """
    bl_idname = "wm.bh_merge_last"
    bl_label = "Merge Last"
    bl_options = {'INTERNAL'}

    def execute(self, _context):
        try:
            bpy.ops.mesh.merge(type='LAST')
        except:
            bpy.ops.mesh.merge()
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENUS


# Context: 3D Viewport (Mesh)
# Hotkey: Shift + S + Drag Mouse in any direction
class MT_pie_mesh_hide(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_mesh_hide"
    bl_label = "Blue Hole Pie Menu: Mesh > Hide"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        blenderPieButton.mesh_reveal_all(pie)
        # 6 - RIGHT
        blenderPieButton.mesh_isolate_selection(pie)
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        blenderPieButton.mesh_hide_selection(pie)
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
class MT_pie_mesh_tool(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_mesh_tool"
    bl_label = "Blue Hole: Mesh > Tools"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        # TODO: Says no parameter vertex_only, will need to fix this.
        blenderPieButton.mesh_bevel(pie)
        # 6 - RIGHT
        blenderPieButton.extrude_move_normal(pie)
        # 2 - BOTTOM
        blenderPieButton.mesh_inset_faces(pie)
        # 8 - TOP
        blenderPieButton.loop_cut_slide(pie)
        # 7 - TOP - LEFT
        blenderPieButton.mesh_knife_tool(pie)
        # pie.operator(WM_OT_CustomKnifeTool.bl_idname, text="Knife Topology Tool", icon='SNAP_MIDPOINT')
        # 9 - TOP - RIGHT
        blenderPieButton.extrude_move_shrink_fatten(pie)
        # 1 - BOTTOM - LEFT
        blenderPieButton.bridge_edge_loops(pie)
        # 3 - BOTTOM - RIGHT
        blenderPieButton.shrink_fatten(pie)


# Context: 3D Viewport (Mesh)
# Hotkey: Ctrl + RMB
class MT_pie_mesh_action(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_mesh_action"
    bl_label = "Blue Hole: Mesh > Action"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        active_select_mode = tuple(bpy.context.scene.tool_settings.mesh_select_mode)

        # Vertex Menu
        if active_select_mode == (True, False, False):
            # 4 - LEFT
            pie.operator(WM_OT_MergeLast.bl_idname)
            # 6 - RIGHT
            blenderPieButton.merge_center(pie)
            # 2 - BOTTOM
            open_pie_menu(pie, MT_pie_vertex_action_more.bl_idname, 'More...')
            # 8 - TOP
            open_pie_menu(pie, MT_pie_vertex_action_select.bl_idname, 'Select...')
            # 7 - TOP - LEFT
            machin3PieButton.straighten(pie)
            # 9 - TOP - RIGHT
            interactiveToolsPieButton.quick_pivot_setup(pie)
            # 1 - BOTTOM - LEFT
            blenderPieButton.remove_doubles(pie)
            # 3 - BOTTOM - RIGHT
            blenderPieButton.vert_connect_path(pie)

        # Edge Menu
        if active_select_mode == (False, True, False):
            # 4 - LEFT
            blenderPieButton.edge_split(pie)
            # 6 - RIGHT
            blenderPieButton.edge_crease(pie)
            # 2 - BOTTOM
            open_pie_menu(pie, MT_pie_edge_action_more.bl_idname, 'More...')
            # 8 - TOP
            open_pie_menu(pie, MT_pie_edge_action_select.bl_idname, 'Select...')
            # 7 - TOP - LEFT
            blenderPieButton.fill_grid(pie)
            # 9 - TOP - RIGHT
            interactiveToolsPieButton.quick_pivot_setup(pie)
            # 1 - BOTTOM - LEFT
            blenderPieButton.clear_sharp(pie)
            # 3 - BOTTOM - RIGHT
            blenderPieButton.mark_sharp(pie)

        # Face Menu
        if active_select_mode == (False, False, True):
            # 4 - LEFT
            blenderPieButton.mesh_split(pie)
            # 6 - RIGHT
            blenderPieButton.mesh_separate(pie)
            # 2 - BOTTOM
            open_pie_menu(pie, MT_pie_face_action_more.bl_idname, 'More...')
            # 8 - TOP
            open_pie_menu(pie, MT_pie_face_action_select.bl_idname, 'Select...')
            # 7 - TOP - LEFT
            interactiveToolsPieButton.quick_lattice(pie)
            # 9 - TOP - RIGHT
            interactiveToolsPieButton.quick_pivot_setup(pie)
            # 1 - BOTTOM - LEFT
            blenderPieButton.merge_by_distance(pie)
            # 3 - BOTTOM - RIGHT
            blenderPieButton.separate_loose_parts(pie)


# No Hotkey; Submenu
class MT_pie_vertex_action_select(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_vertex_action_select"
    bl_label = "Blue Hole: Vertex > Action > Select"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        pie.separator()
        # 2 - BOTTOM
        blenderPieButton.invert_select(pie)
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        blenderPieButton.select_loose_geo(pie)
        # 3 - BOTTOM - RIGHT
        blenderPieButton.select_random_face(pie)


# No Hotkey; Submenu
class MT_pie_vertex_action_more(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_vertex_action_more"
    bl_label = "Blue Hole: Vertex > Action > More"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        blenderPieButton.mesh_symmetrize(pie)
        # 2 - BOTTOM
        interactiveToolsPieButton.quick_flatten(pie)
        # 8 - TOP
        blenderPieButton.transform_to_sphere(pie)
        # 7 - TOP - LEFT
        interactiveToolsPieButton.quick_lattice(pie)
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        hardopsPieButton.vertex_to_circle(pie)


# No Hotkey; Submenu
class MT_pie_edge_action_select(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_edge_action_select"
    bl_label = "Blue Hole: Edge > Action > Select"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        interactiveToolsPieButton.smart_select_ring(pie)
        # 6 - RIGHT
        blenderPieButton.select_sharp(pie)
        # 2 - BOTTOM
        blenderPieButton.invert_select(pie)
        # 8 - TOP
        interactiveToolsPieButton.smart_select_loop(pie)
        # 7 - TOP - LEFT
        blenderPieButton.loop_inner_region(pie)
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# No Hotkey; Submenu
class MT_pie_edge_action_more(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_edge_action_more"
    bl_label = "Blue Hole: Edge > Action > More"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        blenderPieButton.rotate_selected_edge_ccw(pie)
        # 6 - RIGHT
        blenderPieButton.rotate_selected_edge(pie)
        # 2 - BOTTOM
        hardopsPieButton.quick_pipe(pie)
        # 8 - TOP
        angleToolPieButton.mesh_angle(pie)
        # 7 - TOP - LEFT
        blenderPieButton.collapse_edge(pie)
        # 9 - TOP - RIGHT
        blenderPieButton.subdivide_edge_ring(pie)
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# No Hotkey; Submenu
class MT_pie_face_action_select(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_face_action_select"
    bl_label = "Blue Hole: Face > Action > Select"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        blenderPieButton.select_random_face(pie)
        # 6 - RIGHT
        blenderPieButton.link_flat_faces(pie)
        # 2 - BOTTOM
        blenderPieButton.invert_select(pie)
        # 8 - TOP
        blenderPieButton.boundary_loop(pie)
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        blenderPieButton.select_loose_geo(pie)
        # 3 - BOTTOM - RIGHT
        pie.separator()


# No Hotkey; Submenu
class MT_pie_face_action_more(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_face_action_more"
    bl_label = "Blue Hole: Face > Action > More"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        blenderPieButton.unsubdivide(pie)
        # 6 - RIGHT
        blenderPieButton.subdivide(pie)
        # 2 - BOTTOM
        blenderPieButton.flip_normals(pie)
        # 8 - TOP
        blenderPieButton.poke_face(pie)
        # 7 - TOP - LEFT
        blenderPieButton.recalculate_normals_outside(pie)
        # 9 - TOP - RIGHT
        blenderPieButton.recalculate_normals_inside(pie)
        # 1 - BOTTOM - LEFT
        blenderPieButton.triangulate_faces(pie)
        # 3 - BOTTOM - RIGHT
        blenderPieButton.convert_tris_to_quads(pie)


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (MT_pie_mesh_hide,
           MT_pie_mesh_tool,
           MT_pie_mesh_action,
           MT_pie_vertex_action_more,
           MT_pie_vertex_action_select,
           MT_pie_edge_action_more,
           MT_pie_edge_action_select,
           MT_pie_face_action_more,
           # WM_OT_CustomKnifeTool,
           WM_OT_MergeLast,
           MT_pie_face_action_select)


def register():
    log(Severity.DEBUG, name, 'Registering')
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    log(Severity.DEBUG, name, 'Unregistering')
    for cls in classes:
        bpy.utils.unregister_class(cls)
