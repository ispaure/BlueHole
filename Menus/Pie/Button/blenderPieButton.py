"""
Pie Menu operators pertaining to Blender (Vanilla). These do not rely on external resources.
"""

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
# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU BUTTON


# ----------------------------------------------------------------------------------------------------------------------
# OBJECT


def add_light_probe(pie):
    pie.separator()
    # TODO: Make this one work again
    # pie.operator("object.lightprobe_add", text="Light Probe", icon='LIGHTPROBE_GRID').type = 'GRID'


def add_light_point(pie):
    pie.operator("object.light_add", text="Point", icon='LIGHT_POINT').type = 'POINT'


def add_light_spot(pie):
    pie.operator("object.light_add", text="Spot", icon='LIGHT_SPOT').type = 'SPOT'


def add_light_area(pie):
    pie.operator("object.light_add", text="Area", icon='LIGHT_AREA').type = 'AREA'


def add_light_sun(pie):
    pie.operator("object.light_add", text="Sun", icon='LIGHT_SUN').type = 'SUN'


def add_text(pie):
    pie.operator("object.text_add", text="Text", icon='OUTLINER_OB_FONT')


def load_ref_img(pie):
    pie.operator("object.load_reference_image", text="Reference Image", icon='IMAGE_REFERENCE')


def mod_weighted_nrm(pie):
    pie.operator("object.modifier_add", text="Weighted Normal", icon='NORMALS_VERTEX_FACE').type = 'WEIGHTED_NORMAL'


def link_transfer_data(pie):
    pie.operator("object.make_links_data", text="Link/Transfer Data", icon='NETWORK_DRIVE').type = 'MODIFIERS'


def object_reveal_all(pie):
    pie.operator("object.hide_view_clear", text="Reveal Hidden [All]").select = True


def object_hide_selection(pie):
    pie.operator("object.hide_view_set", text="Hide Selection")


def clear_location(pie):
    pie.operator("object.location_clear", text="Clear Location", icon='FILE_REFRESH').clear_delta = False


def object_join(pie):
    pie.operator("object.join", text="Join", icon='SELECT_EXTEND')


def apply_transform(pie):
    button = pie.operator("object.transform_apply", text="Apply Object Transform", icon='MOD_DATA_TRANSFER')
    button.location = True
    button.rotation = True
    button.scale = True


def clear_parent(pie):
    pie.operator("object.parent_clear", text="Clear Parent", icon='LAYER_USED').type = 'CLEAR_KEEP_TRANSFORM'


def make_parent(pie):
    button_2 = pie.operator("object.parent_set", text="Make Parent", icon='CON_TRACKTO')
    button_2.type = 'OBJECT'
    button_2.keep_transform = True


def select_children_recursive(pie):
    pie.operator("object.select_grouped", text="Select Children", icon='PARTICLE_DATA').type = 'CHILDREN_RECURSIVE'


def select_parent(pie):
    pie.operator("object.select_grouped", text="Select Parent", icon='DRIVER').type = 'PARENT'


def select_grouped(pie):
    pie.operator("object.select_grouped", text="Select Grouped", icon='GROUP').type = 'COLLECTION'


def object_select_all(pie):
    # TODO: Check if this does Invert, I don't think it does unless add at end .action = 'INVERT'
    pie.operator("object.select_all", text="Invert", icon='OVERLAY')


def make_instances_real(pie):
    pie.operator("object.duplicates_make_real", text="Make Instances Real", icon='UNLINKED')


def convert_to_curves(pie):
    pie.operator("object.convert", text="Convert to Curve", icon='MOD_CURVE').target = 'CURVE'


def convert_to_mesh(pie):
    pie.operator("object.convert", text="Convert to Mesh", icon='OUTLINER_OB_CURVE').target = 'MESH'

# ----------------------------------------------------------------------------------------------------------------------
# CURVE


def add_nurbs_path(pie):
    pie.operator("curve.primitive_nurbs_path_add", text="Path", icon='CURVE_PATH')


def add_bezier_curve(pie):
    pie.operator("curve.primitive_bezier_curve_add", text="Bezier", icon='CURVE_BEZCURVE')


def add_bezier_circle(pie):
    pie.operator("curve.primitive_bezier_circle_add", text="Bezier Circle", icon='CURVE_BEZCIRCLE')


def split_curve(pie):
    pie.operator("curve.split", text="Split", icon='FCURVE')

def separate_curve(pie):
    pie.operator("curve.separate", text="Separate", icon='OUTLINER_OB_CURVE')


def dissolve_curve_vertices(pie):
    pie.operator("curve.dissolve_verts", text="Dissolve Vertices", icon='GHOST_DISABLED')


def smooth_curve_radius(pie):
    pie.operator("curve.smooth_radius", text="Smooth Curve Radius", icon='FULLSCREEN_EXIT')


def recalc_curve_handles(pie):
    pie.operator("curve.normals_make_consistent", text="Recalculate Handles", icon='HANDLE_FREE')


def set_handle_linear(pie):
    pie.operator("curve.handle_type_set", text="Set Handle Linear", icon='HANDLE_ALIGNED').type = 'ALIGNED'


def switch_curve_direction(pie):
    pie.operator("curve.switch_direction", text="Switch Direction", icon='CURVE_PATH')


def toggle_curve_cyclic(pie):
    pie.operator("curve.cyclic_toggle", text="Toggle Cyclic", icon='CURVE_NCIRCLE')


def curve_make_segment(pie):
    pie.operator("curve.make_segment", text="Make Segment", icon='OUTLINER_DATA_CURVE')


def curve_extrude_move(pie):
    pie.operator("curve.extrude_move", text="Extrude Curve and Move", icon='CURVE_BEZCURVE')


def curve_smooth(pie):
    pie.operator("curve.smooth", text="Smooth", icon='MOD_OFFSET')


def curve_separator(pie):
    pie.separator()


def curve_decimate(pie):
    pie.operator("curve.decimate", text="Decimate Curve", icon='IPO_LINEAR')


def curve_subdivide(pie):
    pie.operator("curve.subdivide", text="Subdivide", icon='PARTICLE_POINT')


def curve_reveal_all(pie):
    pie.operator("curve.reveal", text="Reveal Hidden [All]")


def curve_isolate_selection(pie):
    pie.operator("curve.hide", text="Isolate Selection").unselected = True


def curve_hide_selection(pie):
    pie.operator("curve.hide", text="Hide Selection").unselected = False


# ----------------------------------------------------------------------------------------------------------------------
# MESH

def clear_seam(pie):
    op = pie.operator("mesh.mark_seam", text="Clear Seam", icon='CANCEL_LARGE')
    op.clear = True


def mark_seam(pie):
    op = pie.operator("mesh.mark_seam", text="Mark Seam", icon='CHECKMARK')
    op.clear = False


def add_cylinder(pie):
    op = pie.operator("mesh.primitive_cylinder_add", text="Cylinder", icon='MESH_CYLINDER')
    op.align = 'CURSOR'
    op.radius = 0.5
    op.depth = 1.0
    op.vertices = 32


def add_cube(pie):
    op = pie.operator("mesh.primitive_cube_add", text="Cube", icon='MESH_CUBE')
    op.align = 'CURSOR'
    op.size = 1.0


def add_sphere(pie):
    op = pie.operator("mesh.primitive_uv_sphere_add", text="UV Sphere", icon='MATSPHERE')
    op.radius = 0.5


def add_plane(pie):
    pie.operator("mesh.primitive_plane_add", text="Plane", icon='MESH_PLANE').size = 1.0


def mesh_reveal_all(pie):
    pie.operator("mesh.reveal", text="Reveal Hidden [All]")


def mesh_isolate_selection(pie):
    pie.operator("mesh.hide", text="Isolate Selection").unselected = True


def mesh_hide_selection(pie):
    pie.operator("mesh.hide", text="Hide Selection").unselected = False


def mesh_inset_faces(pie):
    pie.operator("mesh.inset", text="Inset Faces", icon='SHAPEKEY_DATA')


def loop_cut_slide(pie):
    pie.operator("mesh.loopcut_slide", text="Loop Cut and Slide", icon='MOD_MULTIRES')


def bridge_edge_loops(pie):
    pie.operator("mesh.bridge_edge_loops", text="Bridge Edge Loops", icon='CLIPUV_DEHLT')


def mesh_bevel(pie):
    pie.operator("mesh.bevel", text="Bevel", icon='MOD_BEVEL')


def smart_select_ring(pie):
    pie.operator("mesh.smart_select_ring", text="Smart Ring", icon='ALIGN_FLUSH')


def smart_select_loop(pie):
    pie.operator("mesh.smart_select_loop", text="Smart Loop", icon='ALIGN_JUSTIFY')


def loop_inner_region(pie):
    pie.operator("mesh.loop_to_region", text="Loop Inner-Region", icon='SNAP_FACE')


def select_sharp(pie):
    pie.operator("mesh.edges_select_sharp", text="Sharp Edges", icon='SHARPCURVE')


def invert_select(pie):
    pie.operator("mesh.select_all", text="Invert", icon='OVERLAY').action = 'INVERT'


def rotate_selected_edge(pie):
    pie.operator("mesh.edge_rotate", text="Rotate Selected Edge", icon='LOOP_FORWARDS').use_ccw = False


def rotate_selected_edge_ccw(pie):
    pie.operator("mesh.edge_rotate", text="Rotate Selected Edge", icon='LOOP_BACK').use_ccw = True


def collapse_edge(pie):
    pie.operator("mesh.merge", text="Collapse").type = 'COLLAPSE'


def subdivide_edge_ring(pie):
    pie.operator("mesh.subdivide_edgering", text="Subdivide Edge-Ring", icon='MOD_MULTIRES')


def select_random_face(pie):
    pie.operator("mesh.select_random", text="Random", icon='GROUP_VERTEX')


def link_flat_faces(pie):
    pie.operator("mesh.faces_select_linked_flat", text="Linked Flat Faces", icon='SELECT_EXTEND')


def boundary_loop(pie):
    pie.operator("mesh.region_to_loop", text="Boundary Loop", icon='MATPLANE')


def select_loose_geo(pie):
    pie.operator("mesh.select_loose", text="Loose Geometry", icon='MOD_BUILD')


def subdivide(pie):
    pie.operator("mesh.subdivide", text="Subdivide", icon='MESH_GRID')


def unsubdivide(pie):
    pie.operator("mesh.unsubdivide", text="Un-Subdivide", icon='MATPLANE')


def flip_normals(pie):
    pie.operator("mesh.flip_normals", text="Flip", icon='MOD_UVPROJECT')


def poke_face(pie):
    pie.operator('mesh.poke', text='Poke Face')


def recalculate_normals_outside(pie):
    pie.operator("mesh.normals_make_consistent", text="Recalculate Normals Outside", icon='MOD_NORMALEDIT').inside = False


def recalculate_normals_inside(pie):
    pie.operator("mesh.normals_make_consistent", text="Recalculate Normals Inside", icon='MOD_NORMALEDIT').inside = True


def triangulate_faces(pie):
    op = pie.operator("mesh.quads_convert_to_tris", text="Triangulate Faces", icon='MOD_TRIANGULATE')
    op.quad_method = 'BEAUTY'
    op.ngon_method = 'BEAUTY'


def convert_tris_to_quads(pie):
    pie.operator("mesh.tris_convert_to_quads", text="Tris to Quads", icon='MOD_WIREFRAME')


def merge_center(pie):
    pie.operator("mesh.merge", text="Merge to Center", icon='FREEZE').type = 'CENTER'


def remove_doubles(pie):
    pie.operator("mesh.remove_doubles", text="Merge by Distance", icon='AUTOMERGE_ON')


def vert_connect_path(pie):
    pie.operator("mesh.vert_connect_path", text="Connect Path", icon='CON_TRACKTO')


def edge_split(pie):
    pie.operator("mesh.edge_split", text="Edge Split", icon='SCULPTMODE_HLT')


def fill_grid(pie):
    pie.operator("mesh.fill_grid", text="Grid Fill", icon='SHAPEKEY_DATA')


def clear_sharp(pie):
    pie.operator("mesh.mark_sharp", text="Clear Sharp", icon='NORMALS_FACE').clear = True


def mark_sharp(pie):
    pie.operator("mesh.mark_sharp", text="Mark Sharp", icon='NORMALS_VERTEX_FACE').clear = False


def mesh_split(pie):
    pie.operator("mesh.split", text="Split", icon='MOD_PHYSICS')


def mesh_separate(pie):
    pie.operator("mesh.separate", text="Separate", icon='MOD_PHYSICS').type = 'SELECTED'


def merge_by_distance(pie):
    pie.operator("mesh.remove_doubles", text="Merge by Distance", icon='AUTOMERGE_ON')


def separate_loose_parts(pie):
    pie.operator("mesh.separate", text="Separate Loose Parts", icon='OUTLINER_DATA_LATTICE').type = 'LOOSE'


def mesh_symmetrize(pie):
    pie.operator("mesh.symmetrize", text="Symmetrize", icon='MESH_MONKEY')


def mesh_knife_tool(pie):
    op = pie.operator('mesh.knife_tool', text="Knife Topology Tool", icon='SNAP_MIDPOINT')
    op.use_occlude_geometry = True
    op.only_selected = False
    op.xray = True
    op.visible_measurements = 'NONE'
    op.angle_snapping = 'NONE'
    op.angle_snapping_increment = 0.261799
    op.wait_for_input = True


# ----------------------------------------------------------------------------------------------------------------------
# UV

def uv_stitch(pie):
    pie.operator("uv.stitch", text="Stitch", icon='AUTOMERGE_ON')


def follow_active_quads(pie):
    pie.operator("uv.follow_active_quads", text="Follow Active Quads", icon='UV_FACESEL')


def smart_project(pie):
    pie.operator("uv.smart_project", text="Smart UV Project", icon='UV_VERTEXSEL')


def snap_select_to_cursor(pie):
    op = pie.operator("uv.snap_selected", text=" to Cursor", icon='RESTRICT_SELECT_OFF')
    op.target = 'CURSOR'


def snap_cursor_to_select(pie):
    op = pie.operator("uv.snap_cursor", text=" to Selected", icon='PIVOT_CURSOR')
    op.target = 'SELECTED'


def snap_select_to_cursor_offset(pie):
    op = pie.operator("uv.snap_selected", text=" to Cursor (Offset)", icon='RESTRICT_SELECT_OFF')
    op.target = 'CURSOR_OFFSET'


def snap_cursor_to_pixel(pie):
    op = pie.operator("uv.snap_cursor", text=" to Pixel", icon='PIVOT_CURSOR')
    op.target = 'PIXELS'


def snap_selected_to_pixel(pie):
    pie.operator("uv.snap_selected", text=" to Pixel", icon='RESTRICT_SELECT_OFF')


def uv_cube_project(pie):
    pie.operator("uv.cube_project", text='Cube Projection')


def uv_split_island(pie):
    pie.operator('uv.select_split', text='Split Island', icon='MOD_PHYSICS')


def uv_unwrap_conformal(pie):
    op = pie.operator('uv.unwrap', text='Unwrap Conformal', icon='UV')
    op.method = 'CONFORMAL'
    # more settings link: https://docs.blender.org/api/current/bpy.ops.uv.html


# ----------------------------------------------------------------------------------------------------------------------
# TRANSFORM


def transform_tilt(pie):
    pie.operator("transform.tilt", text="Tilt", icon='ORIENTATION_GIMBAL')


def transform_curve_scale(pie):
    pie.operator("transform.transform", text="Scale", icon='ORIENTATION_LOCAL').mode = 'CURVE_SHRINKFATTEN'


def shrink_fatten(pie):
    pie.operator("transform.shrink_fatten", text="Shrink/Fatten", icon='MOD_EXPLODE')


def edge_crease(pie):
    pie.operator("transform.edge_crease", text="Edge Crease", icon='PARTICLE_PATH')


def transform_to_sphere(pie):
    pie.operator("transform.tosphere", text="To Sphere", icon='MOD_SUBSURF')


# ----------------------------------------------------------------------------------------------------------------------
# VIEW3D

def extrude_move_normal(pie):
    pie.operator("view3d.edit_mesh_extrude_move_normal", text="Extrude and Move on Normals", icon='FACESEL')


def extrude_move_shrink_fatten(pie):
    pie.operator("view3d.edit_mesh_extrude_move_shrink_fatten", text="Extrude and Move on Individual Normals", icon='MOD_SOLIDIFY')


def vertex_to_circle(pie):
    pie.operator('view3d.vertcircle', text='Vertex to Circle')


def clean_mesh(pie):
    pie.operator("view3d.clean_mesh", text="Clean", icon='SHADERFX')


# ----------------------------------------------------------------------------------------------------------------------
# TRANSFORM
