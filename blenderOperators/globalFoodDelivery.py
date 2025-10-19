"""
Adds Blue Hole Blender Operators [Food Delivery]
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

import bpy

from BlueHole.blenderUtils.fileUtils import open_url
import BlueHole.blenderUtils.debugUtils as debugUtils
from BlueHole.blenderUtils.languageUtils import loc_str as loc_str
import BlueHole.envUtils.envUtils as envUtils


show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

# Start of File Debug Message
debugUtils.print_debug_msg('\nLoading Food Delivery Menu and Operators...', show_verbose)


# ----------------------------------------------------------------------------------------------------------------------
# MENUS

class BLUE_HOLE_MT_food_delivery(bpy.types.Menu):
    bl_label = loc_str('food_delivery')

    def draw(self, context):
        layout = self.layout
        for cls in classes:
            layout.operator(cls.bl_idname, icon='TEMP')
        # Draw additional operators from the active environment (if available)
        envUtils.draw_current_env_menu_items('globalFoodDelivery', layout)


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS

class OrderStHubert(bpy.types.Operator):

    bl_idname = "wm.bh_foodorder_sthubert"
    bl_label = loc_str('food_delivery_order_sthubert')

    def execute(self, context):
        open_url('http://www.st-hubert.com/index.fr.html')
        return {'FINISHED'}


class OrderUberEats(bpy.types.Operator):

    bl_idname = "wm.bh_foodorder_ubereats"
    bl_label = loc_str('food_delivery_order_uber_eats')

    def execute(self, context):
        open_url('http://www.ubereats.com')
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (OrderStHubert,
           OrderUberEats
           )


# Register
def register():
    # Register Menu
    bpy.utils.register_class(BLUE_HOLE_MT_food_delivery)
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    # Unregister Menu
    bpy.utils.unregister_class(BLUE_HOLE_MT_food_delivery)
    # Unregister Operators
    for cls in classes:
        bpy.utils.unregister_class(cls)


# ----------------------------------------------------------------------------------------------------------------------
# End of File Debug Message
debugUtils.print_debug_msg('Food Delivery Menu and Operators Loaded!', show_verbose)
