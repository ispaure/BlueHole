"""
Operators for source control related things.
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
from bpy.props import *
from bpy_extras.io_utils import ExportHelper

# Blue Hole
from ..blenderUtils import sourceControlUtils, callbacks

# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class BHSaveAsMainfile(bpy.types.Operator, ExportHelper):
    bl_idname = "wm.bh_save_as_mainfile"
    bl_label = "Save As"
    bl_description = "Save the current Blender file with Blue Hole Source Control integration"

    filename_ext = ".blend"
    filter_glob: StringProperty(default="*.blend", options={'HIDDEN'})

    copy: BoolProperty(
        name="Save Copy",
        description="Save a copy of the file",
        default=False
    )

    check_existing: BoolProperty(
        name="Check Existing",
        description="Warn if the target file already exists",
        default=True
    )

    compress: BoolProperty(
        name="Compress",
        description="Write compressed blend file",
        default=False
    )

    relative_remap: BoolProperty(
        name="Remap Relative Paths",
        description="Remap relative paths when saving to a new location",
        default=True
    )

    def execute(self, context):

        blend_path = self.filepath

        sourceControlUtils.sc_check_blend(blend_path, allow_sync=False, silent_mode=False)

        callbacks.SKIP_NEXT_SAVE_PRE_SC_CHECK = True

        return bpy.ops.wm.save_as_mainfile(
            'EXEC_DEFAULT',
            filepath=blend_path,
            copy=self.copy,
            check_existing=self.check_existing,
            compress=self.compress,
            relative_remap=self.relative_remap,
        )


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (
    BHSaveAsMainfile,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators
