"""
Pie Menu operators pertaining to InteractiveToolsBlender
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

from ..utilities import *

# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU BUTTON

addon_name = 'InteractiveTools'  # Name of addon to display if button cannot be loaded.


def quick_pivot_setup(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "mesh.quick_pivot",
        text="Quick Pivot Setup",
        icon='ORIENTATION_GLOBAL')


def quick_lattice(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "mesh.quick_lattice",
        text="Quick Lattice",
        icon='OUTLINER_DATA_LATTICE')


def quick_flatten(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "mesh.quick_flatten",
        text="Quick Flatten",
        icon='FILE_TICK',
        props={"mode": 1})


def smart_select_ring(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "mesh.smart_select_ring",
        text="Smart Ring",
        icon='ALIGN_FLUSH'
    )


def smart_select_loop(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "mesh.smart_select_loop",
        text="Smart Loop",
        icon='ALIGN_JUSTIFY'
    )
