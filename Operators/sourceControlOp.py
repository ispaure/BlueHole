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
from ..blenderUtils import sourceControlUtils, blenderFile, callbacks
from ..wrappers import perforceWrapper as p4Wrapper

# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class P4CheckOutCurrentScene(bpy.types.Operator):

    bl_idname = "wm.bh_p4_check_out_blend"
    bl_label = "Check Out Current Blend Scene"

    def execute(self, context):
        sourceControlUtils.sc_check_blend(blenderFile.get_blend_file_path())
        return {'FINISHED'}


class P4DisplayServerInfo(bpy.types.Operator):

    bl_idname = "wm.bh_p4_display_server_info"
    bl_label = "Display Server Info"

    def execute(self, context):
        sourceControlUtils.sc_dialog_box_info()
        return {'FINISHED'}


class WM_OT_SetP4EnvSettings(bpy.types.Operator):
    """Set Perforce Environment Settings"""
    bl_idname = "wm.bh_set_p4_env_settings"
    bl_label = "Set Perforce Environment Settings"
    bl_options = {'INTERNAL'}

    def execute(self, _context):
        p4Wrapper.set_p4_env_settings()
        return {'FINISHED'}


class WM_OT_disabled_source_control(bpy.types.Operator):
    bl_idname = "wm.disabled_source_control"
    bl_label = "Source Control is Disabled!"
    bl_description = "Source Control is required for this button."

    open_prefs: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        self.report({'WARNING'}, "Source Control is not enabled for this Environment. Enable it in Preferences > Add-ons > Blue Hole.")
        if self.open_prefs:
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {'CANCELLED'}


class BHSaveAsMainfile(bpy.types.Operator, ExportHelper):
    bl_idname = "wm.bh_save_as_mainfile"
    bl_label = "Save As (Blue Hole)"
    bl_description = "Save the current Blender file with Blue Hole source control checks"

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

        sourceControlUtils.sc_check_blend(blend_path, silent_mode=False)

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
classes = (P4CheckOutCurrentScene,
           P4DisplayServerInfo,
           WM_OT_SetP4EnvSettings,
           WM_OT_disabled_source_control,
           BHSaveAsMainfile
           )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators
