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
        if prefs().thirdparty.auto_constraints.enable_transform_tools_modal_autoconstraint and op_exists('transform.translate_auto_constraint'):
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
        if prefs().thirdparty.auto_constraints.enable_transform_tools_modal_autoconstraint and op_exists('transform.rotate_auto_constraint'):
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
        if prefs().thirdparty.auto_constraints.enable_transform_tools_modal_autoconstraint and op_exists('transform.resize_auto_constraint'):
            bpy.ops.transform.resize_auto_constraint('INVOKE_DEFAULT')
        else:
            bpy.ops.transform.resize('INVOKE_DEFAULT')

        return {'FINISHED'}


class UV_OT_BH_PlaceAndMoveCursor(bpy.types.Operator):
    """Place the UV cursor at the press and let Blender drag it until release"""
    bl_idname = "uv.bh_place_and_move_cursor"
    bl_label = "Place and Move UV Cursor"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH'
                and context.area is not None and context.area.ui_type == 'UV'
                and context.region is not None and context.region.type == 'WINDOW'
                and bpy.ops.uv.cursor_set.poll() and bpy.ops.transform.translate.poll())

    def invoke(self, context, event):
        location = context.region.view2d.region_to_view(event.mouse_region_x, event.mouse_region_y)
        if 'FINISHED' not in bpy.ops.uv.cursor_set('EXEC_DEFAULT', location=location):
            return {'CANCELLED'}

        result = bpy.ops.transform.translate(
            'INVOKE_DEFAULT', cursor_transform=True, release_confirm=True)
        # Translate owns the modal handler and consumes the release.
        return {'FINISHED'} if 'RUNNING_MODAL' in result else {'CANCELLED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


# List of classes to register/unregister
classes = (
    WM_OT_BH_TranslateAutoConstraint,
    WM_OT_BH_RotateAutoConstraint,
    WM_OT_BH_ResizeAutoConstraint,
    UV_OT_BH_PlaceAndMoveCursor,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
