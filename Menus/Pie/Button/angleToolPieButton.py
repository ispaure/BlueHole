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
from ....blenderUtils import addonUtils


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU BUTTON


def mesh_angle(pie):
    if addonUtils.is_addon_enabled_and_loaded('angle_tool'):
        pie.operator("mesh.angle_tool", text="Mesh Angle")
    else:
        pie.operator("wm.disabled_addon_mesh_angle", text="Can't Show; Angle Tool add-on disabled!!!", icon='ERROR')
