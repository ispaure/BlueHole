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


def _alt_left_mouse_bindings(
        keymap_name: str,
        space_type: str = 'EMPTY',
        region_type: str = 'WINDOW'
) -> tuple[KeymapBinding, ...]:
    """
    Return the default Blue Hole keymap bindings for an Alt + Left Mouse style action.
    """
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='LEFTMOUSE',
            alt=True,
        ),
    )


def _alt_middle_mouse_bindings(
        keymap_name: str,
        space_type: str = 'EMPTY',
        region_type: str = 'WINDOW'
) -> tuple[KeymapBinding, ...]:
    """
    Return the default Blue Hole keymap bindings for an Alt + Middle Mouse style action.
    """
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='MIDDLEMOUSE',
            alt=True,
        ),
    )


def _alt_right_mouse_bindings(
        keymap_name: str,
        space_type: str = 'EMPTY',
        region_type: str = 'WINDOW'
) -> tuple[KeymapBinding, ...]:
    """
    Return the default Blue Hole keymap bindings for an Alt + Right Mouse style action.
    """
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
    """
    Return the default Blue Hole keymap bindings for a Mouse Wheel Left style action.
    """
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
    """
    Return the default Blue Hole keymap bindings for a Mouse Wheel Right style action.
    """
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
    """
    Return the default Blue Hole keymap bindings for an Alt + Mouse Wheel Out style action.
    """
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
    """
    Return the default Blue Hole keymap bindings for an Alt + Mouse Wheel In style action.
    """
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


# View2D

# TODO: Fix - Does not get added at all in the Keymap for some reason
NAVIGATION_VIEW2D_PAN_ALT_LEFT_MOUSE = OperatorAction(
    operator='view2d.pan',
    keymap_bindings=_alt_left_mouse_bindings('View2D')
)

NAVIGATION_VIEW2D_PAN_ALT_MIDDLE_MOUSE = OperatorAction(
    operator='view2d.pan',
    keymap_bindings=_alt_middle_mouse_bindings('View2D')
)

NAVIGATION_VIEW2D_ZOOM_ALT_RIGHT_MOUSE = OperatorAction(
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

NAVIGATION_VIEW2D_ZOOM_OUT_ALT_WHEEL_OUT = OperatorAction(
    operator='view2d.zoom_out',
    keymap_bindings=_alt_wheel_down_bindings('View2D')
)

NAVIGATION_VIEW2D_ZOOM_IN_ALT_WHEEL_IN = OperatorAction(
    operator='view2d.zoom_in',
    keymap_bindings=_alt_wheel_up_bindings('View2D')
)

# View2D Buttons List
# NOTE:
# This mirrors the intended View2D behavior for consistency.
# The scroll left/right and wheel zoom in/out additions are not yet fully validated in this context.
# Roll back these extra bindings if they do not behave as intended.

# TODO: Fix - Does not get added at all in the Keymap for some reason
NAVIGATION_VIEW2D_BUTTONS_LIST_PAN_ALT_LEFT_MOUSE = OperatorAction(
    operator='view2d.pan',
    keymap_bindings=_alt_left_mouse_bindings('View2D Buttons List')
)

NAVIGATION_VIEW2D_BUTTONS_LIST_PAN_ALT_MIDDLE_MOUSE = OperatorAction(
    operator='view2d.pan',
    keymap_bindings=_alt_middle_mouse_bindings('View2D Buttons List')
)

NAVIGATION_VIEW2D_BUTTONS_LIST_ZOOM_ALT_RIGHT_MOUSE = OperatorAction(
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

NAVIGATION_VIEW2D_BUTTONS_LIST_ZOOM_OUT_ALT_WHEEL_OUT = OperatorAction(
    operator='view2d.zoom_out',
    keymap_bindings=_alt_wheel_down_bindings('View2D Buttons List')
)

NAVIGATION_VIEW2D_BUTTONS_LIST_ZOOM_IN_ALT_WHEEL_IN = OperatorAction(
    operator='view2d.zoom_in',
    keymap_bindings=_alt_wheel_up_bindings('View2D Buttons List')
)

# 3D View
NAVIGATION_3D_VIEW_PAN_WHEEL_LEFT = OperatorAction(
    operator='view3d.view_pan',
    props={
        'type': 'PANLEFT',
    },
    keymap_bindings=_wheel_left_bindings('3D View', space_type='VIEW_3D')
)

NAVIGATION_3D_VIEW_PAN_WHEEL_RIGHT = OperatorAction(
    operator='view3d.view_pan',
    props={
        'type': 'PANRIGHT',
    },
    keymap_bindings=_wheel_right_bindings('3D View', space_type='VIEW_3D')
)

NAVIGATION_3D_VIEW_MOVE_ALT_MIDDLE_MOUSE = OperatorAction(
    operator='view3d.move',
    keymap_bindings=_alt_middle_mouse_bindings('3D View', space_type='VIEW_3D')
)

NAVIGATION_3D_VIEW_ROTATE_ALT_LEFT_MOUSE = OperatorAction(
    operator='view3d.rotate',
    keymap_bindings=_alt_left_mouse_bindings('3D View', space_type='VIEW_3D')
)

NAVIGATION_3D_VIEW_ZOOM_ALT_RIGHT_MOUSE = OperatorAction(
    operator='view3d.zoom',
    keymap_bindings=_alt_right_mouse_bindings('3D View', space_type='VIEW_3D')
)

# Image

# TODO: Fix - Does not get added at all in the Keymap for some reason
NAVIGATION_IMAGE_PAN_ALT_LEFT_MOUSE = OperatorAction(
    operator='image.view_pan',
    keymap_bindings=_alt_left_mouse_bindings('Image', space_type='IMAGE_EDITOR')
)

NAVIGATION_IMAGE_PAN_ALT_MIDDLE_MOUSE = OperatorAction(
    operator='image.view_pan',
    keymap_bindings=_alt_middle_mouse_bindings('Image', space_type='IMAGE_EDITOR')
)

NAVIGATION_IMAGE_ZOOM_ALT_RIGHT_MOUSE = OperatorAction(
    operator='image.view_zoom',
    keymap_bindings=_alt_right_mouse_bindings('Image', space_type='IMAGE_EDITOR')
)

# Clip Editor
# NOTE:
# Industry Compatible does not appear to override the default Clip Editor pan/zoom behavior here.
# These bindings are being added intentionally for consistency with the other viewport navigation contexts.
# Roll them back if Clip Editor behavior feels wrong or conflicts with expected defaults.

# TODO: Fix - Does not get added at all in the Keymap for some reason
NAVIGATION_CLIP_EDITOR_PAN_ALT_LEFT_MOUSE = OperatorAction(
    operator='clip.view_pan',
    keymap_bindings=_alt_left_mouse_bindings('Clip Editor', space_type='CLIP_EDITOR')
)

NAVIGATION_CLIP_EDITOR_PAN_ALT_MIDDLE_MOUSE = OperatorAction(
    operator='clip.view_pan',
    keymap_bindings=_alt_middle_mouse_bindings('Clip Editor', space_type='CLIP_EDITOR')
)

NAVIGATION_CLIP_EDITOR_ZOOM_ALT_RIGHT_MOUSE = OperatorAction(
    operator='clip.view_zoom',
    keymap_bindings=_alt_right_mouse_bindings('Clip Editor', space_type='CLIP_EDITOR')
)

# ----------------------------------------------------------------------------------------------------------------------
# ACTION LIST

NAVIGATION_VIEWPORT_ACTIONS: list[OperatorAction] = [
    NAVIGATION_VIEW2D_PAN_ALT_LEFT_MOUSE,
    NAVIGATION_VIEW2D_PAN_ALT_MIDDLE_MOUSE,
    NAVIGATION_VIEW2D_ZOOM_ALT_RIGHT_MOUSE,
    NAVIGATION_VIEW2D_SCROLL_LEFT,
    NAVIGATION_VIEW2D_SCROLL_RIGHT,
    NAVIGATION_VIEW2D_ZOOM_OUT_ALT_WHEEL_OUT,
    NAVIGATION_VIEW2D_ZOOM_IN_ALT_WHEEL_IN,

    NAVIGATION_VIEW2D_BUTTONS_LIST_PAN_ALT_LEFT_MOUSE,
    NAVIGATION_VIEW2D_BUTTONS_LIST_PAN_ALT_MIDDLE_MOUSE,
    NAVIGATION_VIEW2D_BUTTONS_LIST_ZOOM_ALT_RIGHT_MOUSE,
    NAVIGATION_VIEW2D_BUTTONS_LIST_SCROLL_LEFT,
    NAVIGATION_VIEW2D_BUTTONS_LIST_SCROLL_RIGHT,
    NAVIGATION_VIEW2D_BUTTONS_LIST_ZOOM_OUT_ALT_WHEEL_OUT,
    NAVIGATION_VIEW2D_BUTTONS_LIST_ZOOM_IN_ALT_WHEEL_IN,

    NAVIGATION_3D_VIEW_PAN_WHEEL_LEFT,
    NAVIGATION_3D_VIEW_PAN_WHEEL_RIGHT,
    NAVIGATION_3D_VIEW_MOVE_ALT_MIDDLE_MOUSE,
    NAVIGATION_3D_VIEW_ROTATE_ALT_LEFT_MOUSE,
    NAVIGATION_3D_VIEW_ZOOM_ALT_RIGHT_MOUSE,

    NAVIGATION_IMAGE_PAN_ALT_LEFT_MOUSE,
    NAVIGATION_IMAGE_PAN_ALT_MIDDLE_MOUSE,
    NAVIGATION_IMAGE_ZOOM_ALT_RIGHT_MOUSE,

    NAVIGATION_CLIP_EDITOR_PAN_ALT_LEFT_MOUSE,
    NAVIGATION_CLIP_EDITOR_PAN_ALT_MIDDLE_MOUSE,
    NAVIGATION_CLIP_EDITOR_ZOOM_ALT_RIGHT_MOUSE,
]


def get_navigation_viewport_actions() -> list[OperatorAction]:
    """
    Return all declared Blue Hole navigation viewport operator actions.
    """
    return NAVIGATION_VIEWPORT_ACTIONS
