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

from ....blenderUtils import addonUtils

# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU BUTTON




def add_quadsphere(pie):
    pie.operator("machin3.quadsphere", text="Quadsphere", icon='MESH_UVSPHERE')


def straighten(pie):
    if addonUtils.is_addon_enabled_and_loaded('MACHIN3tools'):
        pie.operator("machin3.straighten", text="Straighten", icon='THREE_DOTS')
    else:
        pie.operator("wm.disabled_addon_machin3tools", text="Can't Show; MACHIN3tools add-on disabled!!!", icon='ERROR')

