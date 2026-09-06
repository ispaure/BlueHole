"""
Blue Hole Menus
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

# System
import os

# Blender
import bpy
from pathlib import Path

# Blue Hole
from ....blenderUtils import blenderFile
from ....Lib.commonUtils import fileUtils, dirUtils
from ....blenderUtils.uiUtils import show_label
from ....operators import import_ops
from ....Lib.commonUtils.debugUtils import *
from typing import List

# ----------------------------------------------------------------------------------------------------------------------
# MENUS


class BLUE_HOLE_MT_import(bpy.types.Menu):
    bl_label = "Import"
    bl_idname = "BLUE_HOLE_MT_import"

    def draw(self, context):
        layout = self.layout
        show_label('SCALE GUIDES', layout)

        # Get list of meshes in the current environment meshes folder
        guide_mesh_dir_path: Path = blenderFile.get_default_env_msh_guides_path()
        if os.path.isdir(str(guide_mesh_dir_path)):
            layout.separator()

            # Get list of .FBX files in dir
            file_lst: List[fileUtils.File] = dirUtils.Directory(guide_mesh_dir_path).list_files(recursive=False, filter_extension='fbx')

            for file in file_lst:
                op = layout.operator(import_ops.ImportMeshFBXOBJ.bl_idname,
                                     text=file.file_name,
                                     icon='IMPORT')
                op.import_path_str = str(file.path)
        else:
            msg = (f'Folder path "{guide_mesh_dir_path}" is inaccessible, defaulting to default environment\'s '
                   f'scale meshes.')
            log(Severity.WARNING, 'Import Menu', msg)

            # layout.menu("BLUE_HOLE_MT_import_scale_guides")
            layout.separator()
            layout.operator(import_ops.ImportGuide_5_6_ScaleMan.bl_idname, icon='IMPORT')
            layout.operator(import_ops.ImportGuide_5_10_ScaleMan.bl_idname, icon='IMPORT')
            layout.operator(import_ops.ImportGuide_5_10_ScaleManCasual.bl_idname, icon='IMPORT')
            layout.operator(import_ops.ImportGuide_5_10_ScaleManSitting.bl_idname, icon='IMPORT')
            layout.operator(import_ops.ImportGuide_6_1_ScaleMan.bl_idname, icon='IMPORT')


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (
    BLUE_HOLE_MT_import,
)


# Register
def register():
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
