"""
Selection tool switching keymap operator actions for Blue Hole.

This feature ensures that pressing Q always switches the user
back to a selection tool (Box Select or XRay Box Select when available).
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
from .....operators.box_xray_ops import *

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def _selection_tool_switch_bindings(
        keymap_name: str,
        space_type: str = 'EMPTY',
        region_type: str = 'WINDOW'
) -> tuple[KeymapBinding, ...]:
    """
    Return the default Blue Hole keymap bindings for selection tool switching.
    """
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='Q',
            value='PRESS',
        ),
    )


def _box_select_tool_action(keymap_name: str, space_type: str = 'EMPTY') -> OperatorAction:
    return OperatorAction(
        operator='wm.tool_set_by_id',
        text='Select Box Tool',
        props={'name': 'builtin.select_box', 'cycle': True},
        keymap_bindings=_selection_tool_switch_bindings(keymap_name, space_type),
    )

# ----------------------------------------------------------------------------------------------------------------------
# FEATURE: SELECTION TOOL SWITCH


# Object Mode
SELECTION_TOOL_SWITCH_OBJECT = OperatorAction(
    operator=WM_OT_BH_tool_select_box_xray_object,
    keymap_bindings=_selection_tool_switch_bindings('Object Mode')
)

# Curve
SELECTION_TOOL_SWITCH_CURVE = OperatorAction(
    operator=WM_OT_BH_tool_select_box_xray_curve,
    keymap_bindings=_selection_tool_switch_bindings('Curve')
)

# Curves
SELECTION_TOOL_SWITCH_CURVES = OperatorAction(
    operator=WM_OT_BH_tool_select_box_xray_curves,
    keymap_bindings=_selection_tool_switch_bindings('Curves')
)

# Mesh
SELECTION_TOOL_SWITCH_MESH = OperatorAction(
    operator=WM_OT_BH_tool_select_box_xray_mesh,
    keymap_bindings=_selection_tool_switch_bindings('Mesh')

)

# 75c4bbefab8e3cc7a898801350b900eae9aceea836329b236df37a0c14952850
SELECTION_TOOL_SWITCH_IMAGE = _box_select_tool_action('Image', 'IMAGE_EDITOR')

# a15ff41f58e3a58fe77ab5d970e06f238a62dbb08e41283277d47c86e2c3a489
SELECTION_TOOL_SWITCH_IMAGE_PAINT = _box_select_tool_action('Image Paint')

# e818d7f7e379627bc1cc8078ed75e4ae089ee3b87e4ab12e61c9c5de8d6d7111
SELECTION_TOOL_SWITCH_VERTEX_PAINT = _box_select_tool_action('Vertex Paint')

# d5bb12b4ca2bf2a3ad36a8cdbbfa98483b61ec2fe1f85e83699dfcd49bd6571c
SELECTION_TOOL_SWITCH_WEIGHT_PAINT = _box_select_tool_action('Weight Paint')

# ----------------------------------------------------------------------------------------------------------------------
# ACTION LIST

SELECTION_TOOL_SWITCH_ACTIONS: list[OperatorAction] = [
    SELECTION_TOOL_SWITCH_OBJECT,
    SELECTION_TOOL_SWITCH_CURVE,
    SELECTION_TOOL_SWITCH_CURVES,
    SELECTION_TOOL_SWITCH_MESH,
    SELECTION_TOOL_SWITCH_IMAGE,
    SELECTION_TOOL_SWITCH_IMAGE_PAINT,
    SELECTION_TOOL_SWITCH_VERTEX_PAINT,
    SELECTION_TOOL_SWITCH_WEIGHT_PAINT,
]


def get_selection_tool_switch_actions() -> list[OperatorAction]:
    """
    Return all declared Blue Hole selection tool switching operator actions.
    """
    return SELECTION_TOOL_SWITCH_ACTIONS


# Exact ordinary Deluxe rows; source order reverses the merged reference order.
# bb1eb3f8dd9726854e0a572adfcd9b762c8eaed94fee78ab96fd5e996fbdc06e
DELUXE_3D_VIEW_GENERIC_TOOL_SET_BY_ID_BUTTON4MOUSE_CLICK_ANY = OperatorAction(
    operator='wm.tool_set_by_id', text='3D View Generic', props={'name': 'builtin.select_box'},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Generic', space_type='VIEW_3D',
        key='BUTTON4MOUSE', value='CLICK'),),
)

SELECTION_TOOL_SWITCH_ACTIONS.extend([
    DELUXE_3D_VIEW_GENERIC_TOOL_SET_BY_ID_BUTTON4MOUSE_CLICK_ANY,
])
