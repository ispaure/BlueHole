"""Sculpt shortcut declarations."""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://github.com/ispaure/BlueHole

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

from ....operator_action import KeymapBinding, OperatorAction

SCULPT_KEYMAP_GROUPS = {
    'tools': 'enable_sculpt_tool_shortcuts',
    'controls': 'enable_sculpt_brush_controls',
    'masking': 'enable_sculpt_masking_shortcuts',
    'actions': 'enable_sculpt_action_shortcuts',
}

# Blender prepends add-on rows during merge. Register in reverse reference order
# so the merged map retains the order of these declarations.
_SCULPT_CATALOG = (
    ('masking', OperatorAction(
        operator='sculpt.face_set_edit',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Sculpt, Face Set Edit', 'VIEW_3D', 'MIDDLEMOUSE'),),
    )),
    ('actions', OperatorAction(
        operator='sculpt.mask_by_color',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Sculpt, Mask by Color', 'VIEW_3D', 'MIDDLEMOUSE'),),
    )),
    ('actions', OperatorAction(
        operator='sculpt.mask_by_color',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Sculpt, Mask by Color', 'VIEW_3D', 'MIDDLEMOUSE', value='ANY'),),
    )),
    ('actions', OperatorAction(
        operator='sculpt.project_line_gesture',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Sculpt, Line Project', 'VIEW_3D', 'MIDDLEMOUSE'),),
    )),
    ('actions', OperatorAction(
        operator='sculpt.trim_box_gesture',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Sculpt, Box Trim', 'VIEW_3D', 'MIDDLEMOUSE'),),
    )),
    ('masking', OperatorAction(
        operator='sculpt.face_set_box_gesture',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Sculpt, Box Face Set', 'VIEW_3D', 'MIDDLEMOUSE'),),
    )),
    ('masking', OperatorAction(
        operator='paint.hide_show',
        props={'action': 'SHOW'},
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Sculpt, Box Hide', 'VIEW_3D', 'MIDDLEMOUSE', ctrl=True),),
    )),
    ('masking', OperatorAction(
        operator='paint.hide_show',
        props={'action': 'SHOW'},
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Sculpt, Box Hide', 'VIEW_3D', 'MIDDLEMOUSE', oskey=True),),
    )),
    ('masking', OperatorAction(
        operator='paint.hide_show',
        props={'action': 'HIDE'},
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Sculpt, Box Hide', 'VIEW_3D', 'MIDDLEMOUSE'),),
    )),
    ('masking', OperatorAction(
        operator='paint.hide_show',
        props={'action': 'SHOW'},
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Sculpt, Box Hide', 'VIEW_3D', 'RIGHTMOUSE'),),
    )),
    ('masking', OperatorAction(
        operator='paint.mask_line_gesture',
        props={'value': 0.0},
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Sculpt, Line Mask', 'VIEW_3D', 'MIDDLEMOUSE', ctrl=True),),
    )),
    ('masking', OperatorAction(
        operator='paint.mask_line_gesture',
        props={'value': 0.0},
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Sculpt, Line Mask', 'VIEW_3D', 'MIDDLEMOUSE', oskey=True),),
    )),
    ('masking', OperatorAction(
        operator='paint.mask_line_gesture',
        props={'value': 1.0},
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Sculpt, Line Mask', 'VIEW_3D', 'MIDDLEMOUSE'),),
    )),
    ('masking', OperatorAction(
        operator='paint.mask_box_gesture',
        props={'value': 0.0},
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Sculpt, Box Mask', 'VIEW_3D', 'MIDDLEMOUSE', ctrl=True),),
    )),
    ('masking', OperatorAction(
        operator='paint.mask_box_gesture',
        props={'value': 0.0},
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Sculpt, Box Mask', 'VIEW_3D', 'MIDDLEMOUSE', oskey=True),),
    )),
    ('masking', OperatorAction(
        operator='paint.mask_box_gesture',
        props={'value': 1.0},
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Sculpt, Box Mask', 'VIEW_3D', 'MIDDLEMOUSE'),),
    )),
    ('controls', OperatorAction(
        operator='brush.scale_size',
        props={'scalar': 0.8999999761581421},
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'WHEELLEFTMOUSE', shift=True),),
    )),
    ('controls', OperatorAction(
        operator='brush.scale_size',
        props={'scalar': 1.1109999418258667},
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'WHEELRIGHTMOUSE', shift=True),),
    )),
    ('controls', OperatorAction(
        operator='wm.radial_control',
        props={'data_path_primary': 'tool_settings.sculpt.brush.strength',
               'data_path_secondary': 'tool_settings.unified_paint_settings.strength',
               'use_secondary': 'tool_settings.unified_paint_settings.use_unified_strength',
               'rotation_path': 'tool_settings.sculpt.brush.texture_slot.angle',
               'color_path': 'tool_settings.sculpt.brush.cursor_color_add',
               'fill_color_path': '',
               'fill_color_override_path': '',
               'fill_color_override_test_path': '',
               'zoom_path': '',
               'image_id': 'tool_settings.sculpt.brush',
               'release_confirm': True},
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'SPACE', ctrl=True, repeat=True),),
    )),
    ('controls', OperatorAction(
        operator='brush.scale_size',
        props={'scalar': 0.8999999761581421},
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'WHEELDOWNMOUSE', shift=True),),
    )),
    ('controls', OperatorAction(
        operator='brush.scale_size',
        props={'scalar': 1.1109999418258667},
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'WHEELUPMOUSE', shift=True),),
    )),
    ('tools', OperatorAction(
        operator='wm.tool_set_by_id',
        props={'name': 'builtin_brush.Draw'},
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'NONE', repeat=True),),
    )),
    ('controls', OperatorAction(
        operator='wm.call_panel',
        props={'name': 'VIEW3D_PT_sculpt_context_menu'},
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'RIGHTMOUSE', value='CLICK'),),
    )),
    ('controls', OperatorAction(
        operator='brush.stencil_control',
        props={'mode': 'TRANSLATION'},
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'RIGHTMOUSE', value='RELEASE'),),
    )),
    ('controls', OperatorAction(
        operator='wm.radial_control',
        props={'data_path_primary': 'tool_settings.sculpt.brush.strength',
               'data_path_secondary': 'tool_settings.unified_paint_settings.strength',
               'use_secondary': 'tool_settings.unified_paint_settings.use_unified_strength',
               'rotation_path': 'tool_settings.sculpt.brush.texture_slot.angle',
               'color_path': 'tool_settings.sculpt.brush.cursor_color_add',
               'fill_color_path': '',
               'fill_color_override_path': '',
               'fill_color_override_test_path': '',
               'zoom_path': '',
               'image_id': 'tool_settings.sculpt.brush',
               'secondary_tex': False},
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'U'),),
    )),
    ('actions', OperatorAction(
        operator='object.voxel_size_edit',
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'R', shift=True),),
    )),
    ('actions', OperatorAction(
        operator='object.quadriflow_remesh',
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'R', ctrl=True, alt=True),),
    )),
    ('actions', OperatorAction(
        operator='object.quadriflow_remesh',
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'R', alt=True, oskey=True),),
    )),
    ('actions', OperatorAction(
        operator='sculpt.dyntopo_detail_size_edit',
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'D', shift=True),),
    )),
    ('actions', OperatorAction(
        operator='sculpt.dynamic_topology_toggle',
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'D', ctrl=True),),
    )),
    ('actions', OperatorAction(
        operator='sculpt.dynamic_topology_toggle',
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'D', oskey=True),),
    )),
    ('masking', OperatorAction(
        operator='wm.context_toggle',
        props={'data_path': 'scene.tool_settings.sculpt.show_mask'},
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'M', ctrl=True),),
    )),
    ('masking', OperatorAction(
        operator='paint.mask_flood_fill',
        props={'mode': 'VALUE', 'value': 1.0},
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'A', shift=True, ctrl=True),),
    )),
    ('masking', OperatorAction(
        operator='paint.mask_flood_fill',
        props={'mode': 'VALUE', 'value': 1.0},
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'A', shift=True, oskey=True),),
    )),
    ('masking', OperatorAction(
        operator='paint.mask_flood_fill',
        props={'mode': 'VALUE', 'value': 0.0},
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'A', ctrl=True),),
    )),
    ('masking', OperatorAction(
        operator='paint.mask_flood_fill',
        props={'mode': 'VALUE', 'value': 0.0},
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'A', oskey=True),),
    )),
    ('masking', OperatorAction(
        operator='paint.hide_show',
        props={'action': 'HIDE'},
        keymap_bindings=(KeymapBinding(
            'Sculpt', 'EMPTY', 'H', ctrl=True),),
    )),
)


def get_all_sculpt_actions():
    return tuple(action for _, action in _SCULPT_CATALOG)


def get_sculpt_group_actions(group):
    return tuple(action for feature, action in reversed(_SCULPT_CATALOG) if feature == group)


def get_enabled_sculpt_catalog(preferences):
    return [action for group, action in _SCULPT_CATALOG
            if getattr(preferences, SCULPT_KEYMAP_GROUPS[group])]
