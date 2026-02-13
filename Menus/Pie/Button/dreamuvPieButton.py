"""
Pie Menu operators pertaining to the DreamUV Addon
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


def hotspotter(pie):
    if addonUtils.is_addon_enabled_and_loaded('DreamUV') or addonUtils.is_addon_enabled_and_loaded('Blender_DreamUV-master'):
        pie.operator("view3d.dreamuv_hotspotter", text="HotSpotter", icon='UV_DATA')
    else:
        pie.operator("wm.disabled_addon_dreamuv", text="Can't Show; DreamUV add-on disabled!!!", icon='ERROR')
