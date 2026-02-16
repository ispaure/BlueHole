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

from typing import *

# ----------------------------------------------------------------------------------------------------------------------
# HELPER FUNCTIONS


def open_pie_menu(pie, name: str, text: str, icon: Optional[str]=None):
    # This method opens a small line, not a regular pie menu
    # if icon is not None:
    #     pie.menu(name, text=text, icon=icon)
    # else:
    #     pie.menu(name, text=text)

    # This method opens up a proper pie menu
    if icon is not None:
        pie.operator("wm.call_menu_pie", text=text, icon=icon).name = name
    else:
        pie.operator("wm.call_menu_pie", text=text).name = name
