# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

import BlueHole.pieMenus.globalPieMenus as globalPieMenus
import BlueHole.pieMenus.meshPieMenus as meshPieMenus
import BlueHole.pieMenus.objectPieMenus as objectPieMenus
import BlueHole.pieMenus.uvPieMenus as uvPieMenus
import BlueHole.pieMenus.curvePieMenus as curvePieMenus
import BlueHole.pieMenus.sculptPieMenus as sculptPieMenus
import BlueHole.pieMenus.addPieMenus as addPieMenus


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE


# ----------------------------------------------------------------------------------------------------------------------


pie_menus_cls_lst = (globalPieMenus,
                     meshPieMenus,
                     objectPieMenus,
                     uvPieMenus,
                     curvePieMenus,
                     sculptPieMenus,
                     addPieMenus)

def register():
    for pie_menu_cls in pie_menus_cls_lst:
        pie_menu_cls.register()


def unregister():
    for pie_menu_cls in pie_menus_cls_lst:
        pie_menu_cls.unregister()
