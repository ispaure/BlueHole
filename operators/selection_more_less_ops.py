"""Guarded editor selection operations for the Deluxe More/Less feature."""

import bpy


def _selection_operator(context, more):
    area, region = context.area, context.region
    if area is None or region is None or region.type != 'WINDOW':
        return None
    space = area.spaces.active
    suffix = 'select_more' if more else 'select_less'
    if area.type == 'DOPESHEET_EDITOR' and space.mode == 'DOPESHEET':
        return getattr(bpy.ops.action, suffix)
    if area.type == 'GRAPH_EDITOR' and space.mode == 'FCURVES':
        return getattr(bpy.ops.graph, suffix)
    if (area.type == 'NODE_EDITOR' and area.ui_type == 'CompositorNodeTree'
            and getattr(space, 'edit_tree', None) is not None):
        return bpy.ops.node.select_linked_to if more else bpy.ops.node.select_linked_from
    if area.type == 'SEQUENCE_EDITOR' and space.view_type == 'SEQUENCER':
        return getattr(bpy.ops.sequencer, suffix)
    return None


def _execute(context, more):
    operator = _selection_operator(context, more)
    if operator is None or not operator.poll():
        return {'PASS_THROUGH'}
    return operator('EXEC_DEFAULT')


class WM_OT_BH_editor_select_more(bpy.types.Operator):
    bl_idname = 'wm.bh_editor_select_more'
    bl_label = 'Grow Editor Selection'
    bl_description = 'Grow selection in supported animation, node and sequence editors'

    @classmethod
    def poll(cls, context):
        operator = _selection_operator(context, True)
        return bool(operator is not None and operator.poll())

    def execute(self, context):
        return _execute(context, True)


class WM_OT_BH_editor_select_less(bpy.types.Operator):
    bl_idname = 'wm.bh_editor_select_less'
    bl_label = 'Shrink Editor Selection'
    bl_description = 'Shrink selection in supported animation, node and sequence editors'

    @classmethod
    def poll(cls, context):
        operator = _selection_operator(context, False)
        return bool(operator is not None and operator.poll())

    def execute(self, context):
        return _execute(context, False)


def _uv_selection_operator(context, more):
    area, region = context.area, context.region
    if (area is None or area.type != 'IMAGE_EDITOR' or area.ui_type != 'UV'
            or region is None or region.type != 'WINDOW'):
        return None
    return bpy.ops.uv.select_more if more else bpy.ops.uv.select_less


def _execute_uv(context, more):
    operator = _uv_selection_operator(context, more)
    if operator is None or not operator.poll():
        return {'PASS_THROUGH'}
    return operator('EXEC_DEFAULT')


class WM_OT_BH_uv_select_more(bpy.types.Operator):
    bl_idname = 'wm.bh_uv_select_more'
    bl_label = 'Grow UV Selection'
    bl_description = 'Grow UV selection while preserving arrow behavior outside the UV editor'

    @classmethod
    def poll(cls, context):
        operator = _uv_selection_operator(context, True)
        return bool(operator is not None and operator.poll())

    def execute(self, context):
        return _execute_uv(context, True)


class WM_OT_BH_uv_select_less(bpy.types.Operator):
    bl_idname = 'wm.bh_uv_select_less'
    bl_label = 'Shrink UV Selection'
    bl_description = 'Shrink UV selection while preserving arrow behavior outside the UV editor'

    @classmethod
    def poll(cls, context):
        operator = _uv_selection_operator(context, False)
        return bool(operator is not None and operator.poll())

    def execute(self, context):
        return _execute_uv(context, False)


classes = (WM_OT_BH_editor_select_more, WM_OT_BH_editor_select_less,
           WM_OT_BH_uv_select_more, WM_OT_BH_uv_select_less)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
