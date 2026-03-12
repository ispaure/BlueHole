"""
Scene utilities for Blue Hole.
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

import bpy

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def get_scene_obj_lst():
    """
    Gather the objects within the current scene.
    """
    return bpy.context.scene.collection.all_objects


def set_object_mode():
    """
    Set the mode to Object Mode, regardless of current context.
    """
    scene_lst = get_scene_obj_lst()
    scene_msh_amt = 0

    for obj in scene_lst:
        if 'MESH' in obj.type:
            scene_msh_amt += 1

    # If the scene is empty, Blender will throw an error when trying to switch mode.
    if scene_msh_amt > 0:
        try:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        except Exception:
            pass


def reset_scene():
    pass


def deselect_all():
    """
    Deselect everything in Object Mode.
    """
    bpy.ops.object.select_all(action='DESELECT')
