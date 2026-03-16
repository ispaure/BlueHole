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
from .....operators.box_xray_ops import WM_OT_BH_tool_select_box_xray

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
            value='CLICK',
        ),
    )

# ----------------------------------------------------------------------------------------------------------------------
# FEATURE: SELECTION TOOL SWITCH


# Object Mode
SELECTION_TOOL_SWITCH_OBJECT = OperatorAction(
    operator=WM_OT_BH_tool_select_box_xray,
    keymap_bindings=_selection_tool_switch_bindings('Object Mode')
)

# Curve
SELECTION_TOOL_SWITCH_CURVE = OperatorAction(
    operator=WM_OT_BH_tool_select_box_xray,
    keymap_bindings=_selection_tool_switch_bindings('Curve')
)

# Curves
SELECTION_TOOL_SWITCH_CURVES = OperatorAction(
    operator=WM_OT_BH_tool_select_box_xray,
    keymap_bindings=_selection_tool_switch_bindings('Curves')
)

# Mesh
SELECTION_TOOL_SWITCH_MESH = OperatorAction(
    operator=WM_OT_BH_tool_select_box_xray,
    keymap_bindings=_selection_tool_switch_bindings('Mesh')

)

# ----------------------------------------------------------------------------------------------------------------------
# ACTION LIST

SELECTION_TOOL_SWITCH_ACTIONS: list[OperatorAction] = [
    SELECTION_TOOL_SWITCH_OBJECT,
    SELECTION_TOOL_SWITCH_CURVE,
    SELECTION_TOOL_SWITCH_CURVES,
    SELECTION_TOOL_SWITCH_MESH,
]


def get_selection_tool_switch_actions() -> list[OperatorAction]:
    """
    Return all declared Blue Hole selection tool switching operator actions.
    """
    return SELECTION_TOOL_SWITCH_ACTIONS
