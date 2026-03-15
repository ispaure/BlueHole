"""
Navigation viewport keymap operator actions for Blue Hole.
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


def _alt_left_middle_mouse_bindings(
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
            alt=True,
        ),
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='MIDDLEMOUSE',
            alt=True,
        ),
    )


def _alt_middle_mouse_bindings(
        keymap_name: str,
        space_type: str = 'EMPTY',
        region_type: str = 'WINDOW'
) -> tuple[KeymapBinding, ...]:
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='MIDDLEMOUSE',
            alt=True,
        ),
    )


def _alt_left_mouse_bindings(
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
            alt=True,
        ),
    )


def _alt_right_mouse_bindings(
        keymap_name: str,
        space_type: str = 'EMPTY',
        region_type: str = 'WINDOW'
) -> tuple[KeymapBinding, ...]:
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='RIGHTMOUSE',
            alt=True,
        ),
    )


def _wheel_left_bindings(
        keymap_name: str,
        space_type: str = 'EMPTY',
        region_type: str = 'WINDOW'
) -> tuple[KeymapBinding, ...]:
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='WHEELLEFTMOUSE',
        ),
    )


def _wheel_right_bindings(
        keymap_name: str,
        space_type: str = 'EMPTY',
        region_type: str = 'WINDOW'
) -> tuple[KeymapBinding, ...]:
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='WHEELRIGHTMOUSE',
        ),
    )


def _alt_wheel_down_bindings(
        keymap_name: str,
        space_type: str = 'EMPTY',
        region_type: str = 'WINDOW'
) -> tuple[KeymapBinding, ...]:
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='WHEELDOWNMOUSE',
            alt=True,
        ),
    )


def _alt_wheel_up_bindings(
        keymap_name: str,
        space_type: str = 'EMPTY',
        region_type: str = 'WINDOW'
) -> tuple[KeymapBinding, ...]:
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='WHEELUPMOUSE',
            alt=True,
        ),
    )


# ----------------------------------------------------------------------------------------------------------------------
# FEATURE: NAVIGATION VIEWPORT


# -------------------------------------------------------------------------------------------------
# View2D
# -------------------------------------------------------------------------------------------------

NAVIGATION_VIEW2D_PAN = OperatorAction(
    operator='view2d.pan',
    keymap_bindings=_alt_left_middle_mouse_bindings('View2D')
)

NAVIGATION_VIEW2D_ZOOM = OperatorAction(
    operator='view2d.zoom',
    keymap_bindings=_alt_right_mouse_bindings('View2D')
)

NAVIGATION_VIEW2D_SCROLL_LEFT = OperatorAction(
    operator='view2d.scroll_left',
    keymap_bindings=_wheel_left_bindings('View2D')
)

NAVIGATION_VIEW2D_SCROLL_RIGHT = OperatorAction(
    operator='view2d.scroll_right',
    keymap_bindings=_wheel_right_bindings('View2D')
)

NAVIGATION_VIEW2D_ZOOM_OUT = OperatorAction(
    operator='view2d.zoom_out',
    keymap_bindings=_alt_wheel_down_bindings('View2D')
)

NAVIGATION_VIEW2D_ZOOM_IN = OperatorAction(
    operator='view2d.zoom_in',
    keymap_bindings=_alt_wheel_up_bindings('View2D')
)


# -------------------------------------------------------------------------------------------------
# View2D Buttons List
# -------------------------------------------------------------------------------------------------

NAVIGATION_VIEW2D_BUTTONS_LIST_PAN = OperatorAction(
    operator='view2d.pan',
    keymap_bindings=_alt_left_middle_mouse_bindings('View2D Buttons List')
)

NAVIGATION_VIEW2D_BUTTONS_LIST_ZOOM = OperatorAction(
    operator='view2d.zoom',
    keymap_bindings=_alt_right_mouse_bindings('View2D Buttons List')
)

NAVIGATION_VIEW2D_BUTTONS_LIST_SCROLL_LEFT = OperatorAction(
    operator='view2d.scroll_left',
    keymap_bindings=_wheel_left_bindings('View2D Buttons List')
)

NAVIGATION_VIEW2D_BUTTONS_LIST_SCROLL_RIGHT = OperatorAction(
    operator='view2d.scroll_right',
    keymap_bindings=_wheel_right_bindings('View2D Buttons List')
)

NAVIGATION_VIEW2D_BUTTONS_LIST_ZOOM_OUT = OperatorAction(
    operator='view2d.zoom_out',
    keymap_bindings=_alt_wheel_down_bindings('View2D Buttons List')
)

NAVIGATION_VIEW2D_BUTTONS_LIST_ZOOM_IN = OperatorAction(
    operator='view2d.zoom_in',
    keymap_bindings=_alt_wheel_up_bindings('View2D Buttons List')
)


# -------------------------------------------------------------------------------------------------
# 3D View
# -------------------------------------------------------------------------------------------------

NAVIGATION_3D_VIEW_PAN_LEFT = OperatorAction(
    operator='view3d.view_pan',
    props={'type': 'PANLEFT'},
    keymap_bindings=_wheel_left_bindings('3D View', space_type='VIEW_3D')
)

NAVIGATION_3D_VIEW_PAN_RIGHT = OperatorAction(
    operator='view3d.view_pan',
    props={'type': 'PANRIGHT'},
    keymap_bindings=_wheel_right_bindings('3D View', space_type='VIEW_3D')
)

NAVIGATION_3D_VIEW_MOVE = OperatorAction(
    operator='view3d.move',
    keymap_bindings=_alt_middle_mouse_bindings('3D View', space_type='VIEW_3D')
)

NAVIGATION_3D_VIEW_ROTATE = OperatorAction(
    operator='view3d.rotate',
    keymap_bindings=_alt_left_mouse_bindings('3D View', space_type='VIEW_3D')
)

NAVIGATION_3D_VIEW_ZOOM = OperatorAction(
    operator='view3d.zoom',
    keymap_bindings=_alt_right_mouse_bindings('3D View', space_type='VIEW_3D')
)


# -------------------------------------------------------------------------------------------------
# Image Editor
# -------------------------------------------------------------------------------------------------

NAVIGATION_IMAGE_PAN = OperatorAction(
    operator='image.view_pan',
    keymap_bindings=_alt_left_middle_mouse_bindings('Image', space_type='IMAGE_EDITOR')
)

NAVIGATION_IMAGE_ZOOM = OperatorAction(
    operator='image.view_zoom',
    keymap_bindings=_alt_right_mouse_bindings('Image', space_type='IMAGE_EDITOR')
)


# -------------------------------------------------------------------------------------------------
# Clip Editor
# -------------------------------------------------------------------------------------------------

NAVIGATION_CLIP_EDITOR_PAN = OperatorAction(
    operator='clip.view_pan',
    keymap_bindings=_alt_left_middle_mouse_bindings('Clip Editor', space_type='CLIP_EDITOR')
)

NAVIGATION_CLIP_EDITOR_ZOOM = OperatorAction(
    operator='clip.view_zoom',
    keymap_bindings=_alt_right_mouse_bindings('Clip Editor', space_type='CLIP_EDITOR')
)


# ----------------------------------------------------------------------------------------------------------------------
# ACTION LIST

NAVIGATION_VIEWPORT_MOVEMENT_ACTIONS: list[OperatorAction] = [

    NAVIGATION_VIEW2D_PAN,
    NAVIGATION_VIEW2D_ZOOM,
    NAVIGATION_VIEW2D_SCROLL_LEFT,
    NAVIGATION_VIEW2D_SCROLL_RIGHT,
    NAVIGATION_VIEW2D_ZOOM_OUT,
    NAVIGATION_VIEW2D_ZOOM_IN,

    NAVIGATION_VIEW2D_BUTTONS_LIST_PAN,
    NAVIGATION_VIEW2D_BUTTONS_LIST_ZOOM,
    NAVIGATION_VIEW2D_BUTTONS_LIST_SCROLL_LEFT,
    NAVIGATION_VIEW2D_BUTTONS_LIST_SCROLL_RIGHT,
    NAVIGATION_VIEW2D_BUTTONS_LIST_ZOOM_OUT,
    NAVIGATION_VIEW2D_BUTTONS_LIST_ZOOM_IN,

    NAVIGATION_3D_VIEW_PAN_LEFT,
    NAVIGATION_3D_VIEW_PAN_RIGHT,
    NAVIGATION_3D_VIEW_MOVE,
    NAVIGATION_3D_VIEW_ROTATE,
    NAVIGATION_3D_VIEW_ZOOM,

    NAVIGATION_IMAGE_PAN,
    NAVIGATION_IMAGE_ZOOM,

    NAVIGATION_CLIP_EDITOR_PAN,
    NAVIGATION_CLIP_EDITOR_ZOOM,
]


def get_navigation_viewport_movement_actions() -> list[OperatorAction]:
    """
    Return all declared Blue Hole navigation viewport operator actions.
    """
    return NAVIGATION_VIEWPORT_MOVEMENT_ACTIONS
