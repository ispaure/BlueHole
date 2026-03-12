"""
User Interface (UI) functions for Blue Hole.
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://github.com/ispaure/BlueHole

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS

from pathlib import Path

import bpy

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def show_label(label_text, layout):
    layout.label(text='【 ' + label_text + ' 】', icon='KEYTYPE_EXTREME_VEC')


def set_theme(name):
    """
    Set Blender to the chosen theme.

    :param name: Name of the theme file (without extension)
    """
    # Import locally to avoid circular imports
    from .blenderFile import get_blue_hole_themes_path

    theme_file_path = str(Path(get_blue_hole_themes_path()) / f'{name}.xml')

    bpy.ops.script.execute_preset(
        filepath=theme_file_path,
        menu_idname='USERPREF_MT_interface_theme_presets',
    )
