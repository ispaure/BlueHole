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

import os
import importlib
from pathlib import Path
import importlib.util as importlib_util

import bpy

import BlueHole.blenderUtils.fileUtils as fileUtils
from BlueHole.blenderUtils.debugUtils import print_debug_msg as print_debug_msg


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


def import_python_module(module_path):
    """
    Imports module of given module_path. If module could not be found, return None
    :param module_path: Path to module, as it would normally be given ('.')
    :type module_path: str
    """

    if os.path.exists(Path(fileUtils.get_addons_path() + '/' + module_path.replace('.', '/') + '.py')):
        print_debug_msg('File exists! Importing module...', show_verbose)
        imported_module = importlib.import_module(module_path)
        print_debug_msg('Imported module!', show_verbose)
        return imported_module
    else:
        print_debug_msg('Warning! Module does not exist.', show_verbose)
        return None


def import_python_module_absolute_path(path):
    """
    Import python file at absolute path.
    """
    if os.path.exists(path):
        print_debug_msg('File exists! Importing module...', show_verbose)
        spec = importlib_util.spec_from_file_location('module', path)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        print_debug_msg('Imported module2!', show_verbose)
        return foo
    else:
        print_debug_msg('Warning! Module does not exist: ' + path, show_verbose)
        return None
