"""
Pie menu operator actions for Blue Hole.
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

from ..operator_action import OperatorAction, KeymapBinding, pie_menu_action

from ...ui.menus.pie import (
    add_pies,
    curve_pies,
    directories_pies,
    global_pies,
    import_export_pies,
    mesh_pies,
    object_pies,
    sculpt_pies,
    uv_pies,
)

# ----------------------------------------------------------------------------------------------------------------------
# WINDOW

PIE_GLOBAL_HELP = pie_menu_action(
    global_pies.BLUEHOLE_MT_pie_global_help,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='Window',
            space_type='EMPTY',
            key='F1',
        ),
    )
)

PIE_GLOBAL_DIRS = pie_menu_action(
    directories_pies.BLUEHOLE_MT_pie_global_dirs,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='Window',
            space_type='EMPTY',
            key='F3',
        ),
    )
)

PIE_GLOBAL_IMPORT_EXPORT_WINDOW = pie_menu_action(
    import_export_pies.BLUEHOLE_MT_pie_global_import_export,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='Window',
            space_type='EMPTY',
            key='RIGHTMOUSE',
            ctrl=True,
            shift=True,
            alt=True,
        ),
    )
)

# ----------------------------------------------------------------------------------------------------------------------
# OBJECT MODE

PIE_OBJECT_ACTION = pie_menu_action(
    object_pies.BLUEHOLE_MT_pie_object_action,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='Object Mode',
            space_type='EMPTY',
            key='RIGHTMOUSE',
            ctrl=True,
        ),
    )
)

PIE_OBJECT_TOOL = pie_menu_action(
    object_pies.BLUEHOLE_MT_pie_object_tool,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='Object Mode',
            space_type='EMPTY',
            key='RIGHTMOUSE',
            shift=True,
        ),
    )
)

PIE_OBJECT_HIDE = pie_menu_action(
    object_pies.BLUEHOLE_MT_pie_object_hide,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='Object Mode',
            space_type='EMPTY',
            key='S',
            value='CLICK_DRAG',
            shift=True,
        ),
    )
)

PIE_GLOBAL_IMPORT_EXPORT_OBJECT = pie_menu_action(
    import_export_pies.BLUEHOLE_MT_pie_global_import_export,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='Object Mode',
            space_type='EMPTY',
            key='RIGHTMOUSE',
            ctrl=True,
            shift=True,
            alt=True,
        ),
    )
)

# ----------------------------------------------------------------------------------------------------------------------
# MESH

PIE_MESH_ACTION = pie_menu_action(
    mesh_pies.BLUEHOLE_MT_pie_mesh_action,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='Mesh',
            space_type='EMPTY',
            key='RIGHTMOUSE',
            ctrl=True,
        ),
    )
)

PIE_MESH_TOOL = pie_menu_action(
    mesh_pies.BLUEHOLE_MT_pie_mesh_tool,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='Mesh',
            space_type='EMPTY',
            key='RIGHTMOUSE',
            shift=True,
        ),
    )
)

PIE_MESH_HIDE = pie_menu_action(
    mesh_pies.BLUEHOLE_MT_pie_mesh_hide,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='Mesh',
            space_type='EMPTY',
            key='S',
            value='CLICK_DRAG',
            shift=True,
        ),
    )
)

PIE_MESH_ACTION_UVSPECIAL = pie_menu_action(
    uv_pies.BLUEHOLE_MT_pie_mesh_action_uvspecial,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='Mesh',
            space_type='EMPTY',
            key='RIGHTMOUSE',
            ctrl=True,
            shift=True,
            alt=True,
        ),
    )
)

# ----------------------------------------------------------------------------------------------------------------------
# 3D VIEW

PIE_ADD = pie_menu_action(
    add_pies.BLUEHOLE_MT_pie_add,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='3D View',
            space_type='VIEW_3D',
            key='A',
            value='CLICK_DRAG',
            shift=True,
        ),
    )
)

# ----------------------------------------------------------------------------------------------------------------------
# UV EDITOR

PIE_UV_CURSOR = pie_menu_action(
    uv_pies.BLUEHOLE_MT_pie_UV_cursor,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='UV Editor',
            space_type='EMPTY',
            key='RIGHTMOUSE',
            ctrl=True,
            shift=True,
        ),
    )
)

PIE_UV_ACTION_UVSPECIAL = pie_menu_action(
    uv_pies.BLUEHOLE_MT_pie_UV_action_uvspecial,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='UV Editor',
            space_type='EMPTY',
            key='RIGHTMOUSE',
            ctrl=True,
            shift=True,
            alt=True,
        ),
    )
)

PIE_UV_TOOL = pie_menu_action(
    uv_pies.BLUEHOLE_MT_pie_UV_tool,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='UV Editor',
            space_type='EMPTY',
            key='RIGHTMOUSE',
            shift=True,
        ),
    )
)

PIE_UV_ACTION = pie_menu_action(
    uv_pies.BLUEHOLE_MT_pie_UV_action,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='UV Editor',
            space_type='EMPTY',
            key='RIGHTMOUSE',
            ctrl=True,
        ),
    )
)

# ----------------------------------------------------------------------------------------------------------------------
# CURVE

PIE_CURVE_TOOL = pie_menu_action(
    curve_pies.BLUEHOLE_MT_pie_curve_tool,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='Curve',
            space_type='EMPTY',
            key='RIGHTMOUSE',
            shift=True,
        ),
    )
)

PIE_CURVE_ACTION = pie_menu_action(
    curve_pies.BLUEHOLE_MT_pie_curve_action,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='Curve',
            space_type='EMPTY',
            key='RIGHTMOUSE',
            ctrl=True,
        ),
    )
)

PIE_CURVE_HIDE = pie_menu_action(
    curve_pies.BLUEHOLE_MT_pie_curve_hide,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='Curve',
            space_type='EMPTY',
            key='S',
            shift=True,
            repeat=True,
        ),
    )
)

# ----------------------------------------------------------------------------------------------------------------------
# SCULPT

PIE_SCULPT_ACTION = pie_menu_action(
    sculpt_pies.BLUEHOLE_MT_pie_sculpt_action,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='Sculpt',
            space_type='EMPTY',
            key='RIGHTMOUSE',
            ctrl=True,
        ),
    )
)

PIE_SCULPT_TOOL = pie_menu_action(
    sculpt_pies.BLUEHOLE_MT_pie_sculpt_tool,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='Sculpt',
            space_type='EMPTY',
            key='RIGHTMOUSE',
            shift=True,
        ),
    )
)

PIE_SCULPT_SIMULATION = pie_menu_action(
    sculpt_pies.BLUEHOLE_MT_pie_sculpt_simulation,
    keymap_bindings=(
        KeymapBinding(
            keymap_name='Sculpt',
            space_type='EMPTY',
            key='RIGHTMOUSE',
            ctrl=True,
            shift=True,
            alt=True,
        ),
    )
)

# ----------------------------------------------------------------------------------------------------------------------
# ALL PIE ACTIONS

PIE_ACTIONS: list[OperatorAction] = [
    PIE_GLOBAL_HELP,
    PIE_GLOBAL_DIRS,
    PIE_GLOBAL_IMPORT_EXPORT_WINDOW,

    PIE_OBJECT_ACTION,
    PIE_OBJECT_TOOL,
    PIE_OBJECT_HIDE,
    PIE_GLOBAL_IMPORT_EXPORT_OBJECT,

    PIE_MESH_ACTION,
    PIE_MESH_TOOL,
    PIE_MESH_HIDE,
    PIE_MESH_ACTION_UVSPECIAL,

    PIE_ADD,

    PIE_UV_CURSOR,
    PIE_UV_ACTION_UVSPECIAL,
    PIE_UV_TOOL,
    PIE_UV_ACTION,

    PIE_CURVE_TOOL,
    PIE_CURVE_ACTION,
    PIE_CURVE_HIDE,

    PIE_SCULPT_ACTION,
    PIE_SCULPT_TOOL,
    PIE_SCULPT_SIMULATION,
]


def get_all_pie_actions() -> list[OperatorAction]:
    """
    Return all declared Blue Hole pie menu operator actions.
    """
    return PIE_ACTIONS
