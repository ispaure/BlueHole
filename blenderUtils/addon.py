"""Define the addon name and locate its preferences."""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "GNU General Public License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

import bpy


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

# name = __name__.partition('.')[0]
name = 'BlueHole'


def preference():
    preference = bpy.context.preferences.addons[name].preferences
    return preference
