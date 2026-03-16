"""
Operators that did not fit in another category
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
from ..blenderUtils.operatorUtils import op_exists
from ..preferences.prefs import prefs

# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class WM_OT_BH_TranslateAutoConstraint(bpy.types.Operator):
    """Translate using Auto Constraint if available, otherwise default Translate"""
    bl_idname = "wm.bh_translate_auto_constraint"
    bl_label = "Blue Hole: Translate"
    bl_description = "Set autoConstraint Translate Tool, Else Blender's Translate."
    bl_options = {'INTERNAL'}

    def execute(self, context):
        if prefs().keymap.transform.enable_transform_tools_modal_autoconstraint and op_exists('transform.translate_auto_constraint'):
            bpy.ops.transform.translate_auto_constraint('INVOKE_DEFAULT')
        else:
            bpy.ops.transform.translate('INVOKE_DEFAULT')

        return {'FINISHED'}


class WM_OT_BH_RotateAutoConstraint(bpy.types.Operator):
    """Translate using Auto Constraint if available, otherwise default Translate"""
    bl_idname = "wm.bh_rotate_auto_constraint"
    bl_label = "Blue Hole: Rotate"
    bl_description = "Set autoConstraint Rotate Tool, Else Blender's Rotate."
    bl_options = {'INTERNAL'}

    def execute(self, context):
        if prefs().keymap.transform.enable_transform_tools_modal_autoconstraint and op_exists('transform.rotate_auto_constraint'):
            bpy.ops.transform.rotate_auto_constraint('INVOKE_DEFAULT')
        else:
            bpy.ops.transform.rotate('INVOKE_DEFAULT')

        return {'FINISHED'}


class WM_OT_BH_ResizeAutoConstraint(bpy.types.Operator):
    """Translate using Auto Constraint if available, otherwise default Translate"""
    bl_idname = "wm.bh_resize_auto_constraint"
    bl_label = "Blue Hole: Resize"
    bl_description = "Set autoConstraint Resize Tool, Else Blender's Resize."
    bl_options = {'INTERNAL'}

    def execute(self, context):
        if prefs().keymap.transform.enable_transform_tools_modal_autoconstraint and op_exists('transform.resize_auto_constraint'):
            bpy.ops.transform.resize_auto_constraint('INVOKE_DEFAULT')
        else:
            bpy.ops.transform.resize('INVOKE_DEFAULT')

        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


# List of classes to register/unregister
classes = (
    WM_OT_BH_TranslateAutoConstraint,
    WM_OT_BH_RotateAutoConstraint,
    WM_OT_BH_ResizeAutoConstraint
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
