"""
Import utilities for Blue Hole.
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

from . import blenderFile

# ----------------------------------------------------------------------------------------------------------------------
# CODE

# TODO: Add additional environment-specific mesh guides.


def import_fbx_obj(import_path: str) -> None:
    """
    Import a mesh file as either FBX or OBJ based on its file extension.
    """
    file_ext = import_path.split('.')[-1]

    if 'fbx' in file_ext.lower():
        bpy.ops.import_scene.fbx(filepath=import_path)
    else:
        bpy.ops.wm.obj_import(filepath=import_path)


def import_default_env_scale_guide(mesh_name: str) -> None:
    """
    Import a scale guide mesh from the default environment mesh guides directory.
    """
    import_path = str(Path(blenderFile.get_default_env_msh_guides_path(), mesh_name))
    import_fbx_obj(import_path)
