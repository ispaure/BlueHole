"""
Pie Menu operators pertaining to Machin3.
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

addon_name = 'MACHIN3tools'  # Name of addon to display if button cannot be loaded.


def add_quadsphere(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "machin3.quadsphere",
        text="Quadsphere",
        icon='MESH_UVSPHERE')


def straighten(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "machin3.straighten",
        text="Straighten",
        icon='THREE_DOTS')


def isolate_selection_toggle(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "machin3.focus",
        text="Isolate Selection [Toggle]",
        props={"method": 'LOCAL_VIEW'})
