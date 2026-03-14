"""
Pie menu operator actions for Blue Hole.

Notes
-----
- These actions represent "open pie menu" calls (wm.call_menu_pie).
- Some pies are only sub-menus and therefore have NO KeymapBinding.
- PIE_ACTIONS includes ALL pie actions (with or without keymaps).
- Keymap registration should skip actions where action.keymap_bindings is empty.
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
    source_control_pies,
    uv_pies,
)

# ----------------------------------------------------------------------------------------------------------------------
# ADD PIES

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

# Submenu (no hotkey by default)
PIE_ADD_MORE = pie_menu_action(add_pies.BLUEHOLE_MT_pie_add_more)
PIE_ADD_ASSET_CONTAINER = pie_menu_action(add_pies.BLUEHOLE_MT_pie_add_asset_container)

# ----------------------------------------------------------------------------------------------------------------------
# CURVE PIES

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
# DIRECTORIES / GLOBAL (WINDOW)

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

# Submenus (no hotkey by default)
PIE_GLOBAL_THEME = pie_menu_action(global_pies.BLUEHOLE_MT_pie_global_theme)
PIE_GLOBAL_ORDER = pie_menu_action(global_pies.BLUEHOLE_MT_pie_global_order)

# ----------------------------------------------------------------------------------------------------------------------
# IMPORT / EXPORT

PIE_GLOBAL_IMPORT_EXPORT = pie_menu_action(
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

# Submenu (no hotkey by default)
PIE_GLOBAL_EXTRA = pie_menu_action(import_export_pies.BLUEHOLE_MT_pie_global_extra)

# ----------------------------------------------------------------------------------------------------------------------
# MESH PIES

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

PIE_MESH_ACTION_UVSPECIAL = pie_menu_action(
    mesh_pies.BLUEHOLE_MT_pie_mesh_action_uvspecial,
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

# Submenus (no hotkey by default)
PIE_VERTEX_ACTION_SELECT = pie_menu_action(mesh_pies.BLUEHOLE_MT_pie_vertex_action_select)
PIE_VERTEX_ACTION_MORE = pie_menu_action(mesh_pies.BLUEHOLE_MT_pie_vertex_action_more)

PIE_EDGE_ACTION_SELECT = pie_menu_action(mesh_pies.BLUEHOLE_MT_pie_edge_action_select)
PIE_EDGE_ACTION_MORE = pie_menu_action(mesh_pies.BLUEHOLE_MT_pie_edge_action_more)

PIE_FACE_ACTION_SELECT = pie_menu_action(mesh_pies.BLUEHOLE_MT_pie_face_action_select)
PIE_FACE_ACTION_MORE = pie_menu_action(mesh_pies.BLUEHOLE_MT_pie_face_action_more)

# ----------------------------------------------------------------------------------------------------------------------
# OBJECT PIES

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

# Submenu (no hotkey by default)
PIE_OBJECT_TOOL_MORE = pie_menu_action(object_pies.BLUEHOLE_MT_pie_object_tool_more)

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

# Submenus (no hotkey by default)
PIE_OBJECT_ACTION_SELECT = pie_menu_action(object_pies.BLUEHOLE_MT_pie_object_action_select)
PIE_OBJECT_ACTION_MORE = pie_menu_action(object_pies.BLUEHOLE_MT_pie_object_action_more)

# ----------------------------------------------------------------------------------------------------------------------
# SCULPT PIES

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

# Submenus (no hotkey by default)
PIE_SCULPT_TOOL_CLAYBLOB = pie_menu_action(sculpt_pies.BLUEHOLE_MT_pie_sculpt_tool_clayblob)
PIE_SCULPT_TOOL_DRAW = pie_menu_action(sculpt_pies.BLUEHOLE_MT_pie_sculpt_tool_draw)
PIE_SCULPT_TOOL_FLATTENPINCH = pie_menu_action(sculpt_pies.BLUEHOLE_MT_pie_sculpt_tool_flattenpinch)
PIE_SCULPT_TOOL_GRAB = pie_menu_action(sculpt_pies.BLUEHOLE_MT_pie_sculpt_tool_grab)
PIE_SCULPT_TOOL_NUDGETHUMB = pie_menu_action(sculpt_pies.BLUEHOLE_MT_pie_sculpt_tool_nudgethumb)
PIE_SCULPT_TOOL_MISC = pie_menu_action(sculpt_pies.BLUEHOLE_MT_pie_sculpt_tool_misc)

PIE_SCULPT_ACTION_BLEND = pie_menu_action(sculpt_pies.BLUEHOLE_MT_pie_sculpt_action_blend)

PIE_SCULPT_SIMULATION_BENDSTRETCHTWIST = pie_menu_action(
    sculpt_pies.BLUEHOLE_MT_pie_sculpt_simulation_bendstretchtwist
)
PIE_SCULPT_SIMULATION_EXPANDCONTRACT = pie_menu_action(
    sculpt_pies.BLUEHOLE_MT_pie_sculpt_simulation_expandcontract
)

# ----------------------------------------------------------------------------------------------------------------------
# SOURCE CONTROL PIES

PIE_GLOBAL_SOURCE_CONTROL = pie_menu_action(source_control_pies.BLUEHOLE_MT_pie_global_source_control)

# ----------------------------------------------------------------------------------------------------------------------
# UV PIES

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


# Submenus (no hotkey by default)
PIE_UV_ACTION_SELECT = pie_menu_action(uv_pies.BLUEHOLE_MT_pie_UV_action_select)

# ----------------------------------------------------------------------------------------------------------------------
# ALL PIE ACTIONS
#
# This list is the single source of truth for "pie-opening actions".
# Keymap registration should skip actions with no keymap_bindings.

PIE_ACTIONS: list[OperatorAction] = [
    # ADD
    PIE_ADD,
    PIE_ADD_MORE,
    PIE_ADD_ASSET_CONTAINER,

    # CURVE
    PIE_CURVE_ACTION,
    PIE_CURVE_TOOL,
    PIE_CURVE_HIDE,

    # GLOBAL / WINDOW
    PIE_GLOBAL_HELP,
    PIE_GLOBAL_DIRS,
    PIE_GLOBAL_THEME,
    PIE_GLOBAL_ORDER,

    # IMPORT / EXPORT
    PIE_GLOBAL_IMPORT_EXPORT,
    PIE_GLOBAL_EXTRA,

    # MESH
    PIE_MESH_HIDE,
    PIE_MESH_TOOL,
    PIE_MESH_ACTION,
    PIE_MESH_ACTION_UVSPECIAL,
    PIE_VERTEX_ACTION_SELECT,
    PIE_VERTEX_ACTION_MORE,
    PIE_EDGE_ACTION_SELECT,
    PIE_EDGE_ACTION_MORE,
    PIE_FACE_ACTION_SELECT,
    PIE_FACE_ACTION_MORE,

    # OBJECT
    PIE_OBJECT_TOOL,
    PIE_OBJECT_TOOL_MORE,
    PIE_OBJECT_HIDE,
    PIE_OBJECT_ACTION,
    PIE_OBJECT_ACTION_SELECT,
    PIE_OBJECT_ACTION_MORE,

    # SCULPT
    PIE_SCULPT_TOOL,
    PIE_SCULPT_TOOL_CLAYBLOB,
    PIE_SCULPT_TOOL_DRAW,
    PIE_SCULPT_TOOL_FLATTENPINCH,
    PIE_SCULPT_TOOL_GRAB,
    PIE_SCULPT_TOOL_NUDGETHUMB,
    PIE_SCULPT_TOOL_MISC,
    PIE_SCULPT_ACTION,
    PIE_SCULPT_ACTION_BLEND,
    PIE_SCULPT_SIMULATION,
    PIE_SCULPT_SIMULATION_BENDSTRETCHTWIST,
    PIE_SCULPT_SIMULATION_EXPANDCONTRACT,

    # SOURCE CONTROL
    PIE_GLOBAL_SOURCE_CONTROL,

    # UV
    PIE_UV_CURSOR,
    PIE_UV_TOOL,
    PIE_UV_ACTION,
    PIE_UV_ACTION_SELECT,
    PIE_UV_ACTION_UVSPECIAL,
]


def get_all_pie_actions() -> list[OperatorAction]:
    """
    Return all declared Blue Hole pie menu operator actions.
    """
    return PIE_ACTIONS
