"""
Pie Menu operators pertaining to HardOps
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

# Blue Hole
from ..utilities import *


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU BUTTON

addon_name = 'Hard Ops'  # Name of addon to display if button cannot be loaded.


def quick_pipe(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "hops.edge2curve",
        text="Quick Pipe",
        icon='OUTLINER_OB_GREASEPENCIL')


def twist_array(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "hops.array_twist",
        text="Twist Array",
        icon='ALIASED')


def lattice(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "hops.mod_lattice",
        text="Lattice",
        icon='MOD_LATTICE')


def subdiv_modifier(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "hops.mod_subdivision",
        text="Add Subdivision Modifier",
        icon='MOD_SUBSURF')


def radial_array(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "hops.radial_array",
        text="Radial Array",
        icon='OUTLINER_DATA_POINTCLOUD')


def array(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "hops.st3_array",
        text="Array",
        icon='MOD_ARRAY')


def modifier_toggle(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "hops.bool_toggle_viewport",
        text="Modifier Toggle",
        icon='QUIT',
        props={"all_modifiers": True})


def apply_modifier(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "hops.mod_apply",
        text="Apply Modifier",
        icon='OUTPUT')


# TODO: Investigate why there is two of this, maybe one is an old command. they both have a button in use in UI
def apply_modifier_2(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "hops.apply_modifiers",
        text="Apply Modifiers",
        icon='MODIFIER_DATA')


def clean_mesh(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "view3d.clean_mesh",
        text="Clean",
        icon='SHADERFX')


def vertex_to_circle(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        'view3d.vertcircle',
        text='Vertex to Circle')
