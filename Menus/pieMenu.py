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


# Addon
from .Pie import globalPieMenus, meshPieMenus, objectPieMenus, uvPieMenus, curvePieMenus, sculptPieMenus, addPieMenus


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
pie_menu_file_lst = (globalPieMenus,
                     meshPieMenus,
                     objectPieMenus,
                     uvPieMenus,
                     curvePieMenus,
                     sculptPieMenus,
                     addPieMenus)


# Register
def register():
    # Register Operators
    for pie_menu_file in pie_menu_file_lst:
        pie_menu_file.register()


# Unregister
def unregister():
    for pie_menu_file in pie_menu_file_lst:
        pie_menu_file.unregister()
