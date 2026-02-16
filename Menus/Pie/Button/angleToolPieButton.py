"""
Pie Menu operators pertaining to Angle Tool
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

addon_name = 'Angle Tool / Mesh Angle'  # Name of addon to display if button cannot be loaded.


def mesh_angle(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "mesh.angle_tool",
        text="Mesh Angle")
