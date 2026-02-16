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

from ..utilities import *

# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU BUTTON

addon_name = 'DreamUV'  # Name of addon to display if button cannot be loaded.


def hotspotter(pie):
    pie_op_or_disabled(
        pie,
        addon_name,
        "view3d.dreamuv_hotspotter",
        text="HotSpotter",
        icon='UV_DATA'
    )
