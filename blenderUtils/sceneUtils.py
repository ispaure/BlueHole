"""
Scene utilities for Blue Hole.
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

# Blender
import bpy

# ----------------------------------------------------------------------------------------------------------------------
# CODE

def get_scene_obj_lst():
    """
    Gather the list of objects within a scene
    """
    return bpy.context.scene.collection.all_objects


def set_object_mode():
    """
    Set the mode to object mode, regardless of current context
    """
    scene_lst = get_scene_obj_lst()
    scene_msh_amt = 0
    for obj in scene_lst:
        if 'MESH' in obj.type:
            scene_msh_amt += 1
    # If scene is empty, already in a sort-of object mode. Will throw error if try to set it.
    if scene_msh_amt > 0:
        try:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        except:
            pass


def reset_scene():
    pass


def deselect_all():
    """
    Deselects everything (for Object Mode)
    """
    bpy.ops.object.select_all(action='DESELECT')
