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
    props={
        'type': 'TOP',
        'relative': True,
    },
    keymap_bindings=_shift_alt_left_mouse_click_drag_north_bindings('3D View', space_type='VIEW_3D')
)

NAVIGATION_3D_VIEW_AXIS_BOTTOM = OperatorAction(
    operator='view3d.view_axis',
    props={
        'type': 'BOTTOM',
        'relative': True,
    },
    keymap_bindings=_shift_alt_left_mouse_click_drag_south_bindings('3D View', space_type='VIEW_3D')
)

NAVIGATION_3D_VIEW_AXIS_LEFT = OperatorAction(
    operator='view3d.view_axis',
    props={
        'type': 'LEFT',
        'relative': True,
    },
    keymap_bindings=_shift_alt_left_mouse_click_drag_west_bindings('3D View', space_type='VIEW_3D')
)

NAVIGATION_3D_VIEW_AXIS_RIGHT = OperatorAction(
    operator='view3d.view_axis',
    props={
        'type': 'RIGHT',
        'relative': True,
    },
    keymap_bindings=_shift_alt_left_mouse_click_drag_east_bindings('3D View', space_type='VIEW_3D')
)

NAVIGATION_3D_VIEW_AXIS_FRONT = OperatorAction(
    operator='view3d.view_axis',
    props={
        'type': 'FRONT',
        'relative': True,
    },
    keymap_bindings=_shift_alt_front_view_bindings('3D View', space_type='VIEW_3D')
)

# ----------------------------------------------------------------------------------------------------------------------
# ACTION LIST

NAVIGATION_VIEWPORT_AXIS_ACTIONS: list[OperatorAction] = [
    NAVIGATION_3D_VIEW_AXIS_TOP,
    NAVIGATION_3D_VIEW_AXIS_BOTTOM,
    NAVIGATION_3D_VIEW_AXIS_LEFT,
    NAVIGATION_3D_VIEW_AXIS_RIGHT,
    NAVIGATION_3D_VIEW_AXIS_FRONT,
]


def get_navigation_viewport_axis_actions() -> list[OperatorAction]:
    """
    Return all declared Blue Hole navigation viewport axis operator actions.
    """
    return NAVIGATION_VIEWPORT_AXIS_ACTIONS
