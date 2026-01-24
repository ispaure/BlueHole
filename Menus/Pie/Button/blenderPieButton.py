"""
Pie Menus pertaining to Blender (Vanilla). These do not rely on external resources.
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

# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU BUTTON


# ----------------------------------------------------------------------------------------------------------------------
# UV

def clear_seam(pie):
    op = pie.operator("mesh.mark_seam", text="Clear Seam", icon='CANCEL_LARGE')
    op.clear = True


def mark_seam(pie):
    op = pie.operator("mesh.mark_seam", text="Mark Seam", icon='CHECKMARK')
    op.clear = False


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
