"""
Language utilities for Blue Hole (allowing translation of Blue Hole in multiple languages)
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "GNU General Public License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

import csv

from bpy.app.translations import locale

import BlueHole.blenderUtils.fileUtils as fileUtils


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

# Import proper
if locale in ['ja_JP']:
    blender_locale = 2
elif locale in ['fr_FR']:
    blender_locale = 1
else:
    blender_locale = 0


def loc_str(key):
    """
    The brains of localization for Blue Hole. Returns the localized string from a given key. If
    not localized yet, returns the English equivalent (which is always localized)
    """

    # TODO: Fully localize the Blue Hole plugin.

    localized_dict = {}
    localized_file_path = fileUtils.get_blue_hole_localization_file_path()

    with open(localized_file_path, mode='r', encoding='utf-8') as localized_file:
        reader = csv.reader(localized_file, delimiter='|')
        for row in reader:
            localized_dict[row[0]] = [row[1], row[2], row[3]]

    return localized_dict[key][blender_locale]
