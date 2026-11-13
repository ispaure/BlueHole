"""
Navigation viewport axis keymap operator actions for Blue Hole.
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

from ....operator_action import OperatorAction, KeymapBinding

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def _shift_alt_left_mouse_click_drag_north_bindings(
        keymap_name: str,
        space_type: str = 'EMPTY',
        region_type: str = 'WINDOW'
) -> tuple[KeymapBinding, ...]:
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='LEFTMOUSE',
            value='CLICK_DRAG',
            shift=True,
            alt=True,
            direction='NORTH',
        ),
    )


def _shift_alt_left_mouse_click_drag_south_bindings(
        keymap_name: str,
        space_type: str = 'EMPTY',
        region_type: str = 'WINDOW'
) -> tuple[KeymapBinding, ...]:
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='LEFTMOUSE',
            value='CLICK_DRAG',
            shift=True,
            alt=True,
            direction='SOUTH',
        ),
    )


def _shift_alt_left_mouse_click_drag_west_bindings(
        keymap_name: str,
        space_type: str = 'EMPTY',
        region_type: str = 'WINDOW'
) -> tuple[KeymapBinding, ...]:
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='LEFTMOUSE',
            value='CLICK_DRAG',
            shift=True,
            alt=True,
            direction='WEST',
        ),
    )


def _shift_alt_left_mouse_click_drag_east_bindings(
        keymap_name: str,
        space_type: str = 'EMPTY',
        region_type: str = 'WINDOW'
) -> tuple[KeymapBinding, ...]:
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='LEFTMOUSE',
            value='CLICK_DRAG',
            shift=True,
            alt=True,
            direction='EAST',
        ),
    )


def _shift_alt_front_view_bindings(
        keymap_name: str,
        space_type: str = 'EMPTY',
        region_type: str = 'WINDOW'
) -> tuple[KeymapBinding, ...]:
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='LEFTMOUSE',
            value='CLICK_DRAG',
            shift=True,
            alt=True,
        ),
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='MIDDLEMOUSE',
            value='CLICK_DRAG',
            shift=True,
            alt=True,
        ),
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='MIDDLEMOUSE',
            value='CLICK',
            shift=True,
            alt=True,
        ),
    )

# ----------------------------------------------------------------------------------------------------------------------
# FEATURE: NAVIGATION VIEWPORT AXIS

# -------------------------------------------------------------------------------------------------
# 3D View
# -------------------------------------------------------------------------------------------------

NAVIGATION_3D_VIEW_AXIS_TOP = OperatorAction(
    operator='view3d.view_axis',
    text='View Axis (Top View)',
    props={
        'type': 'TOP',
        'relative': True,
    },
    keymap_bindings=_shift_alt_left_mouse_click_drag_north_bindings('3D View', space_type='VIEW_3D')
)

NAVIGATION_3D_VIEW_AXIS_BOTTOM = OperatorAction(
    operator='view3d.view_axis',
    text='View Axis (Bottom View)',
    props={
        'type': 'BOTTOM',
        'relative': True,
    },
    keymap_bindings=_shift_alt_left_mouse_click_drag_south_bindings('3D View', space_type='VIEW_3D')
)

NAVIGATION_3D_VIEW_AXIS_LEFT = OperatorAction(
    operator='view3d.view_axis',
    text='View Axis (Left View)',
    props={
        'type': 'LEFT',
        'relative': True,
    },
    keymap_bindings=_shift_alt_left_mouse_click_drag_west_bindings('3D View', space_type='VIEW_3D')
)

NAVIGATION_3D_VIEW_AXIS_RIGHT = OperatorAction(
    operator='view3d.view_axis',
    text='View Axis (Right View)',
    props={
        'type': 'RIGHT',
        'relative': True,
    },
    keymap_bindings=_shift_alt_left_mouse_click_drag_east_bindings('3D View', space_type='VIEW_3D')
)

NAVIGATION_3D_VIEW_AXIS_FRONT = OperatorAction(
    operator='view3d.view_axis',
    text='View Axis (Front View)',
    props={
        'type': 'FRONT',
        'relative': True,
    },
    keymap_bindings=_shift_alt_front_view_bindings('3D View', space_type='VIEW_3D')
)

NAVIGATION_3D_VIEW_AXIS_ABSOLUTE_BACK = OperatorAction(
    operator='view3d.view_axis',
    text='View Axis (Absolute Back View)',
    props={'type': 'BACK', 'relative': False, 'align_active': False},
    keymap_bindings=(
        # 2ae7de8b565d9c03fc45535896de07dc97af7ebed6ce9357fa324e1ea8187219
        KeymapBinding(keymap_name='3D View', space_type='VIEW_3D', key='F1', ctrl=True),
        # 3ee7001bf2f7f96dae4711948f76694b1c3ceb57aef1db6f96d9c2949b6b8b99
        KeymapBinding(keymap_name='3D View', space_type='VIEW_3D', key='F1', oskey=True),
    ),
)

NAVIGATION_3D_VIEW_AXIS_ABSOLUTE_LEFT = OperatorAction(
    operator='view3d.view_axis',
    text='View Axis (Absolute Left View)',
    props={'type': 'LEFT', 'relative': False, 'align_active': False},
    keymap_bindings=(
        # aa588d20ab030355215e945cdf7ea42dd7e386dfdefb93728ffdbbfb7ba4e6d8
        KeymapBinding(keymap_name='3D View', space_type='VIEW_3D', key='F2', ctrl=True),
        # c0d9e2aa23b51664bb6a7f52439f47fe4ca359575c1da6fcb2bd33afa7dd0d3a
        KeymapBinding(keymap_name='3D View', space_type='VIEW_3D', key='F2', oskey=True),
    ),
)

NAVIGATION_3D_VIEW_AXIS_ABSOLUTE_BOTTOM = OperatorAction(
    operator='view3d.view_axis',
    text='View Axis (Absolute Bottom View)',
    props={'type': 'BOTTOM', 'relative': False, 'align_active': False},
    keymap_bindings=(
        # ac571b681410e5ce9d989bed48844639b1711b4fbc3493c1d7480ed47c0b363e
        KeymapBinding(keymap_name='3D View', space_type='VIEW_3D', key='F3', ctrl=True),
        # 73b312d55cdc6a757ca15ccaa51cdd75ecf21fe184ddad45db575af78c6fcf97
        KeymapBinding(keymap_name='3D View', space_type='VIEW_3D', key='F3', oskey=True),
    ),
)

# ----------------------------------------------------------------------------------------------------------------------
# ACTION LIST

NAVIGATION_VIEWPORT_AXIS_ACTIONS: list[OperatorAction] = [
    NAVIGATION_3D_VIEW_AXIS_TOP,
    NAVIGATION_3D_VIEW_AXIS_BOTTOM,
    NAVIGATION_3D_VIEW_AXIS_LEFT,
    NAVIGATION_3D_VIEW_AXIS_RIGHT,
    NAVIGATION_3D_VIEW_AXIS_FRONT,
    NAVIGATION_3D_VIEW_AXIS_ABSOLUTE_BACK,
    NAVIGATION_3D_VIEW_AXIS_ABSOLUTE_LEFT,
    NAVIGATION_3D_VIEW_AXIS_ABSOLUTE_BOTTOM,
]


def get_navigation_viewport_axis_actions() -> list[OperatorAction]:
    """
    Return all declared Blue Hole navigation viewport axis operator actions.
    """
    return NAVIGATION_VIEWPORT_AXIS_ACTIONS
