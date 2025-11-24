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
import os
from BlueHole.blenderUtils.debugUtils import *
import BlueHole.blenderUtils.addonUtils as addonUtils


# ----------------------------------------------------------------------------------------------------------------------
# USER DEFINED SETTINGS

name = filename = os.path.basename(__file__)


# ----------------------------------------------------------------------------------------------------------------------
# OPERATOR


class WM_OT_CustomKnifeTool(bpy.types.Operator):
    """Activates the Custom Knife Tool"""
    # TODO: Change this into a normal pie.operator using the knowledge I have gained since.
    bl_idname = "wm.bh_custom_knife_tool"
    bl_label = ""
    bl_options = {'INTERNAL'}

    def execute(self, _context):
        bpy.ops.mesh.knife_tool('INVOKE_DEFAULT',
                                use_occlude_geometry=True,
                                only_selected=False,
                                xray=True,
                                visible_measurements='NONE',
                                angle_snapping='NONE',
                                angle_snapping_increment=0.261799,
                                wait_for_input=True)
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
        pie.operator("mesh.reveal", text="Reveal Hidden [All]")
        # 6 - RIGHT
        pie.operator("mesh.hide", text="Isolate Selection").unselected = True
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        pie.operator("mesh.hide", text="Hide Selection").unselected = False
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
        pie.operator("mesh.bevel", text="Bevel", icon='MOD_BEVEL')
        # pie.operator("mesh.bevel", text="Bevel", icon='MOD_BEVEL').vertex_only = False
        # 6 - RIGHT
        pie.operator("view3d.edit_mesh_extrude_move_normal", text="Extrude and Move on Normals", icon='FACESEL')
        # 2 - BOTTOM
        pie.operator("mesh.inset", text="Inset Faces", icon='SHAPEKEY_DATA')
        # 8 - TOP
        pie.operator("mesh.loopcut_slide", text="Loop Cut and Slide", icon='MOD_MULTIRES')
        # 7 - TOP - LEFT
        # pie.operator("mesh.knife_tool", text="Knife Topology Tool", icon='SNAP_MIDPOINT')
        pie.operator(WM_OT_CustomKnifeTool.bl_idname, text="Knife Topology Tool", icon='SNAP_MIDPOINT')
        # 9 - TOP - RIGHT
        pie.operator("view3d.edit_mesh_extrude_move_shrink_fatten", text="Extrude and Move on Individual Normals", icon='MOD_SOLIDIFY')
        # 1 - BOTTOM - LEFT
        pie.operator("mesh.bridge_edge_loops", text="Bridge Edge Loops", icon='CLIPUV_DEHLT')
        # 3 - BOTTOM - RIGHT
        pie.operator("transform.shrink_fatten", text="Shrink/Fatten", icon='MOD_EXPLODE')


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
            pie.operator("wm.bh_merge_last", text="Merge Last", icon='PARTICLES')
            # 6 - RIGHT
            pie.operator("mesh.merge", text="Merge to Center", icon='FREEZE').type = 'CENTER'
            # 2 - BOTTOM
            pie.operator("wm.call_menu_pie", text="More...").name = MT_pie_vertex_action_more.bl_idname
            # 8 - TOP
            pie.operator("wm.call_menu_pie", text="Select...").name = MT_pie_vertex_action_select.bl_idname
            # 7 - TOP - LEFT
            if addonUtils.is_addon_enabled_and_loaded('MACHIN3tools'):
                pie.operator("machin3.straighten", text="Straighten", icon='THREE_DOTS')
            else:
                pie.operator("wm.disabled_addon_machin3tools", text="Can't Show; MACHIN3tools add-on disabled!!!", icon='ERROR')
            # 9 - TOP - RIGHT
            if addonUtils.is_addon_enabled_and_loaded('interactivetoolsblender'):
                pie.operator("mesh.quick_pivot", text="Quick Pivot Setup", icon='ORIENTATION_GLOBAL')
            else:
                pie.operator("wm.disabled_addon_interactive_tools", text="Can't Show; InteractiveTools add-on disabled!!!", icon='ERROR')
            # 1 - BOTTOM - LEFT
            pie.operator("mesh.remove_doubles", text="Merge by Distance", icon='AUTOMERGE_ON')
            # 3 - BOTTOM - RIGHT
            pie.operator("mesh.vert_connect_path", text="Connect Path", icon='CON_TRACKTO')

        # Edge Menu
        if active_select_mode == (False, True, False):
            # 4 - LEFT
            pie.operator("mesh.edge_split", text="Edge Split", icon='SCULPTMODE_HLT')
            # 6 - RIGHT
            pie.operator("transform.edge_crease", text="Edge Crease", icon='PARTICLE_PATH')
            # 2 - BOTTOM
            pie.operator("wm.call_menu_pie", text="More...").name = MT_pie_edge_action_more.bl_idname
            # 8 - TOP
            pie.operator("wm.call_menu_pie", text="Select...").name = MT_pie_edge_action_select.bl_idname
            # 7 - TOP - LEFT
            pie.operator("mesh.fill_grid", text="Grid Fill", icon='SHAPEKEY_DATA')
            # 9 - TOP - RIGHT
            if addonUtils.is_addon_enabled_and_loaded('interactivetoolsblender'):
                pie.operator("mesh.quick_pivot", text="Quick Pivot Setup", icon='ORIENTATION_GLOBAL')
            else:
                pie.operator("wm.disabled_addon_interactive_tools", text="Can't Show; InteractiveTools add-on disabled!!!", icon='ERROR')
            # 1 - BOTTOM - LEFT
            pie.operator("mesh.mark_sharp", text="Clear Sharp", icon='NORMALS_FACE').clear = True
            # 3 - BOTTOM - RIGHT
            pie.operator("mesh.mark_sharp", text="Mark Sharp", icon='NORMALS_VERTEX_FACE').clear = False

        # Face Menu
        if active_select_mode == (False, False, True):
            # 4 - LEFT
            pie.operator("mesh.split", text="Split", icon='MOD_PHYSICS')
            # 6 - RIGHT
            pie.operator("mesh.separate", text="Separate", icon='MOD_PHYSICS').type = 'SELECTED'
            # 2 - BOTTOM
            pie.operator("wm.call_menu_pie", text="More...").name = MT_pie_face_action_more.bl_idname
            # 8 - TOP
            pie.operator("wm.call_menu_pie", text="Select...").name = MT_pie_face_action_select.bl_idname
            # 7 - TOP - LEFT
            if addonUtils.is_addon_enabled_and_loaded('interactivetoolsblender'):
                pie.operator("mesh.quick_lattice", text="Quick Lattice", icon='OUTLINER_DATA_LATTICE')
            else:
                pie.operator("wm.disabled_addon_interactive_tools", text="Can't Show; InteractiveTools add-on disabled!!!", icon='ERROR')
            # 9 - TOP - RIGHT
            if addonUtils.is_addon_enabled_and_loaded('interactivetoolsblender'):
                pie.operator("mesh.quick_pivot", text="Quick Pivot Setup", icon='ORIENTATION_GLOBAL')
            else:
                pie.operator("wm.disabled_addon_interactive_tools", text="Can't Show; InteractiveTools add-on disabled!!!", icon='ERROR')
            # 1 - BOTTOM - LEFT
            pie.operator("mesh.remove_doubles", text="Merge by Distance", icon='AUTOMERGE_ON')
            # 3 - BOTTOM - RIGHT
            pie.operator("mesh.separate", text="Separate Loose Parts", icon='OUTLINER_DATA_LATTICE').type = 'LOOSE'


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
        pie.operator("mesh.select_all", text="Invert", icon='OVERLAY').action = 'INVERT'
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.operator("mesh.select_loose", text="Loose Geometry", icon='MOD_BUILD')
        # 3 - BOTTOM - RIGHT
        pie.operator("mesh.select_random", text="Random", icon='GROUP_VERTEX')


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
        pie.operator("mesh.symmetrize", text="Symmetrize", icon='MESH_MONKEY')
        # 2 - BOTTOM
        if addonUtils.is_addon_enabled_and_loaded('interactivetoolsblender'):
            pie.operator("mesh.quick_flatten", text="Quick Flatten", icon='FILE_TICK').mode = 1
        else:
            pie.operator("wm.disabled_addon_interactive_tools", text="Can't Show; InteractiveTools add-on disabled!!!", icon='ERROR')
        # 8 - TOP
        pie.operator("transform.tosphere", text="To Sphere", icon='MOD_SUBSURF')
        # 7 - TOP - LEFT
        if addonUtils.is_addon_enabled_and_loaded('interactivetoolsblender'):
            pie.operator("mesh.quick_lattice", text="Quick Lattice", icon='OUTLINER_DATA_LATTICE')
        else:
            pie.operator("wm.disabled_addon_interactive_tools", text="Can't Show; InteractiveTools add-on disabled!!!", icon='ERROR')
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.operator('view3d.vertcircle', text='Vertex to Circle')


# No Hotkey; Submenu
class MT_pie_edge_action_select(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_edge_action_select"
    bl_label = "Blue Hole: Edge > Action > Select"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("mesh.smart_select_ring", text="Smart Ring", icon='ALIGN_FLUSH')
        # 6 - RIGHT
        pie.operator("mesh.edges_select_sharp", text="Sharp Edges", icon='SHARPCURVE')
        # 2 - BOTTOM
        pie.operator("mesh.select_all", text="Invert", icon='OVERLAY').action = 'INVERT'
        # 8 - TOP
        pie.operator("mesh.smart_select_loop", text="Smart Loop", icon='ALIGN_JUSTIFY')
        # 7 - TOP - LEFT
        pie.operator("mesh.loop_to_region", text="Loop Inner-Region", icon='SNAP_FACE')
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
        pie.operator("mesh.edge_rotate", text="Rotate Selected Edge", icon='LOOP_BACK').use_ccw = True
        # 6 - RIGHT
        pie.operator("mesh.edge_rotate", text="Rotate Selected Edge", icon='LOOP_FORWARDS').use_ccw = False
        # 2 - BOTTOM
        if addonUtils.is_addon_enabled_and_loaded('hardops') or addonUtils.is_addon_enabled_and_loaded('HOps'):
            # TODO: Find equivalent if HardOps not installed
            pie.operator("hops.edge2curve", text="Quick Pipe", icon='OUTLINER_OB_GREASEPENCIL')
        else:
            pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')
        # 8 - TOP
        if addonUtils.is_addon_enabled_and_loaded('angle_tool'):
            pie.operator("mesh.angle_tool", text="Mesh Angle")
        else:
            pie.operator("wm.disabled_addon_mesh_angle", text="Can't Show; Mesh Angle add-on disabled!!!", icon='ERROR')
        # 7 - TOP - LEFT
        pie.operator("mesh.merge", text="Collapse").type = 'COLLAPSE'
        # 9 - TOP - RIGHT
        pie.operator("mesh.subdivide_edgering", text="Subdivide Edge-Ring", icon='MOD_MULTIRES')
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
        pie.operator("mesh.select_random", text="Random", icon='GROUP_VERTEX')
        # 6 - RIGHT
        pie.operator("mesh.faces_select_linked_flat", text="Linked Flat Faces", icon='SELECT_EXTEND')
        # 2 - BOTTOM
        pie.operator("mesh.select_all", text="Invert", icon='OVERLAY').action = 'INVERT'
        # 8 - TOP
        pie.operator("mesh.region_to_loop", text="Boundary Loop", icon='MATPLANE')
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.operator("mesh.select_loose", text="Loose Geometry", icon='MOD_BUILD')
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
        pie.operator("mesh.unsubdivide", text="Un-Subdivide", icon='MATPLANE')
        # 6 - RIGHT
        pie.operator("mesh.subdivide", text="Subdivide", icon='MESH_GRID')
        # 2 - BOTTOM
        pie.operator("mesh.flip_normals", text="Flip", icon='MOD_UVPROJECT')
        # 8 - TOP
        pie.operator('mesh.poke', text='Poke Face')
        # pie.operator("mesh.customdata_custom_splitnormals_clear", text="Clear Custom Split Normals Data", icon='HOLDOUT_OFF')
        # 7 - TOP - LEFT
        pie.operator("mesh.normals_make_consistent", text="Recalculate Normals Outside", icon='MOD_NORMALEDIT').inside = False
        # 9 - TOP - RIGHT
        pie.operator("mesh.normals_make_consistent", text="Recalculate Normals Inside", icon='MOD_NORMALEDIT').inside = True
        # 1 - BOTTOM - LEFT
        button = pie.operator("mesh.quads_convert_to_tris", text="Triangulate Faces", icon='MOD_TRIANGULATE')
        button.quad_method = 'BEAUTY'
        button.ngon_method = 'BEAUTY'
        # 3 - BOTTOM - RIGHT
        pie.operator("mesh.tris_convert_to_quads", text="Tris to Quads", icon='MOD_WIREFRAME')


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (WM_OT_CustomKnifeTool,
           MT_pie_mesh_hide,
           MT_pie_mesh_tool,
           MT_pie_mesh_action,
           MT_pie_vertex_action_more,
           MT_pie_vertex_action_select,
           MT_pie_edge_action_more,
           MT_pie_edge_action_select,
           MT_pie_face_action_more,
           MT_pie_face_action_select)


def register():
    log(Severity.DEBUG, name, 'Registering')
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    log(Severity.DEBUG, name, 'Unregistering')
    for cls in classes:
        bpy.utils.unregister_class(cls)
