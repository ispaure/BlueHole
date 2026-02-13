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

from ....blenderUtils import addonUtils

# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU BUTTON


def quick_pivot_setup(pie):
    if addonUtils.is_addon_enabled_and_loaded('interactivetoolsblender'):
        pie.operator("mesh.quick_pivot", text="Quick Pivot Setup", icon='ORIENTATION_GLOBAL')
    else:
        pie.operator("wm.disabled_addon_interactive_tools", text="Can't Show; InteractiveTools add-on disabled!!!", icon='ERROR')


def quick_lattice(pie):
    if addonUtils.is_addon_enabled_and_loaded('interactivetoolsblender'):
        pie.operator("mesh.quick_lattice", text="Quick Lattice", icon='OUTLINER_DATA_LATTICE')
    else:
        pie.operator("wm.disabled_addon_interactive_tools", text="Can't Show; InteractiveTools add-on disabled!!!", icon='ERROR')


def quick_flatten(pie):
    if addonUtils.is_addon_enabled_and_loaded('interactivetoolsblender'):
        pie.operator("mesh.quick_flatten", text="Quick Flatten", icon='FILE_TICK').mode = 1
    else:
        pie.operator("wm.disabled_addon_interactive_tools", text="Can't Show; InteractiveTools add-on disabled!!!",
                     icon='ERROR')
