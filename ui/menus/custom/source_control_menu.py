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

# Blender
import bpy
import os
from typing import List

# Blue Hole
from ....operators import help_ops, source_control_ops, external_addon_ops
from ....preferences.prefs import *
from ....blenderUtils import blenderFile, projectUtils
from ....Lib.commonUtils import fileUtils
from ....operators import directory_ops

# ----------------------------------------------------------------------------------------------------------------------
# MENUS


class BLUE_HOLE_MT_source_control(bpy.types.Menu):
    bl_label = "Source Control"
    bl_idname = "BLUE_HOLE_MT_source_control"

    def draw(self, context):
        layout = self.layout
        if prefs().sourcecontrol.source_control_solution == 'perforce':
            layout.operator(help_ops.PerforceDoc.bl_idname, icon='KEYTYPE_EXTREME_VEC')

            if blenderFile.has_blend_filepath():
                layout.operator(source_control_ops.P4CheckOutCurrentScene.bl_idname, icon='CHECKMARK')
            else:
                col = layout.column()
                col.enabled = False
                col.operator(
                    external_addon_ops.BH_OT_disabled_notice.bl_idname,
                    text='Save .blend file to enable checkout',
                    icon='ERROR'
                )

            layout.operator(source_control_ops.P4DisplayServerInfo.bl_idname, icon='INFO')
            layout.separator()
            layout.menu(BLUE_HOLE_MT_perforce_debug_fstat.bl_idname, icon='HELP')


class BLUE_HOLE_MT_perforce_debug_fstat(bpy.types.Menu):
    bl_label = "Debug - Fstat"
    bl_idname = "BLUE_HOLE_MT_perforce_debug_fstat"

    def draw(self, context):
        layout = self.layout

        if not blenderFile.has_blend_filepath():
            col = layout.column()
            col.enabled = False
            col.operator(external_addon_ops.BH_OT_disabled_notice.bl_idname,
                         text='Save .blend file to enable fstat debug',
                         icon='ERROR')
        else:
            # Fstat for the current blender file
            op = layout.operator(source_control_ops.P4DisplayFileFstat.bl_idname, text='Blender Scene')
            op.file_path_str = blenderFile.get_blend_file_path()

            layout.separator()

            # Final dir
            final_dir = projectUtils.get_project_sub_dir(prefs().directory.sc_dir_struct_final)
            if not os.path.isdir(final_dir):
                col = layout.column()
                col.enabled = False
                col.operator(external_addon_ops.BH_OT_disabled_notice.bl_idname,
                             text='Make final dir to enable fstat debug.',
                             icon='ERROR')
            else:
                # Fstat for files in final folder
                layout.operator(directory_ops.OpenFinalFolder.bl_idname, icon='FILE_FOLDER')

                # List files
                file_lst: List[fileUtils.File] = fileUtils.get_file_list_from_path(final_dir,
                                                                                   recursive=False)

                for file in file_lst:
                    op = layout.operator(source_control_ops.P4DisplayFileFstat.bl_idname, text=file.file_name)
                    op.file_path_str = str(file.path)


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (
    BLUE_HOLE_MT_source_control,
    BLUE_HOLE_MT_perforce_debug_fstat,
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
