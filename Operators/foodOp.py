"""
Operators to order food
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

# Blender
import bpy

# Blue Hole
from ..blenderUtils.fileUtils import open_url

# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class OrderStHubert(bpy.types.Operator):

    bl_idname = "wm.bh_foodorder_sthubert"
    bl_label = 'Order St-Hubert'

    def execute(self, context):
        open_url('http://www.st-hubert.com/index.fr.html')
        return {'FINISHED'}


class OrderUberEats(bpy.types.Operator):

    bl_idname = "wm.bh_foodorder_ubereats"
    bl_label = 'Order Uber Eats'

    def execute(self, context):
        open_url('http://www.ubereats.com')
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (OrderStHubert,
           OrderUberEats
           )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators
