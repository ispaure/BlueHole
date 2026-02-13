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
import BlueHole.blenderUtils.addonUtils as addonUtils


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU BUTTON

def quick_pipe(pie):
    if addonUtils.is_addon_enabled_and_loaded('hardops') or addonUtils.is_addon_enabled_and_loaded('HOps'):
        # TODO: Find equivalent if HardOps not installed
        pie.operator("hops.edge2curve", text="Quick Pipe", icon='OUTLINER_OB_GREASEPENCIL')
    else:
        pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')
