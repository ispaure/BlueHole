"""
Import utilities for Blue Hole
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

# System
from pathlib import Path

# Blender
import bpy

# Blue Hole
import BlueHole.blenderUtils.fileUtils as fileUtils


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = False


# ----------------------------------------------------------------------------------------------------------------------
# CODE

# TODO: Add additional environment-specific mesh guides.


def import_fbx_obj(import_path):
    # Determine if mesh is fbx or obj
    file_ext = import_path.split('.')[-1]
    if 'fbx' in file_ext.lower():
        bpy.ops.import_scene.fbx(filepath=import_path)  # Import mesh as FBX
    else:
        bpy.ops.wm.obj_import(filepath=import_path)  # Import mesh as OBJ


def import_default_env_scale_guide(mesh_name):

    # Get import path for the mesh
    import_path = str(Path(fileUtils.get_default_env_msh_guides_path(), mesh_name))

    # import fbx or obj, whatever mesh_name is
    import_fbx_obj(import_path)
