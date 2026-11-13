"""Circle Selection keymap actions for the 3D View and UV Editor."""

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = 'MIT License'
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

from ....operator_action import KeymapBinding, OperatorAction


# Binding comments cite the reviewed full rows in deluxe-baseline-2026-11-12-v1.
SELECTION_3D_VIEW_CIRCLE_ADD = OperatorAction(
    operator='view3d.select_circle',
    text='Circle Select (Add)',
    props={'mode': 'ADD', 'radius': 25, 'wait_for_input': True, 'x': 0, 'y': 0},
    keymap_bindings=(
        # 65179ade6ef40a7e2c328d1e13e5631d5bfcf4abe9a50300c4a2b9b6b7324995
        KeymapBinding(keymap_name='3D View Generic', space_type='VIEW_3D', key='MIDDLEMOUSE', shift=True),
    ),
)

SELECTION_3D_VIEW_CIRCLE_SUBTRACT = OperatorAction(
    operator='view3d.select_circle',
    text='Circle Select (Subtract)',
    props={'mode': 'SUB', 'radius': 25, 'wait_for_input': True, 'x': 0, 'y': 0},
    keymap_bindings=(
        # 5a02611f57e1d97cef92a9be7c758c0aa856622ea423d17c4e77aad95acae33a
        KeymapBinding(keymap_name='3D View Generic', space_type='VIEW_3D', key='MIDDLEMOUSE', ctrl=True),
    ),
)

SELECTION_UV_CIRCLE_ADD = OperatorAction(
    operator='uv.select_circle',
    text='Circle Select (Add)',
    props={'mode': 'ADD', 'radius': 25, 'wait_for_input': False, 'x': 0, 'y': 0},
    keymap_bindings=(
        # e516e0f4b047efd00bbe11076cb482c83b0419a0d3022ae2a46bfa4c15e5ed87
        KeymapBinding(keymap_name='UV Editor', space_type='EMPTY', key='MIDDLEMOUSE', shift=True),
    ),
)

SELECTION_UV_CIRCLE_SUBTRACT = OperatorAction(
    operator='uv.select_circle',
    text='Circle Select (Subtract)',
    props={'mode': 'SUB', 'radius': 25, 'wait_for_input': False, 'x': 0, 'y': 0},
    keymap_bindings=(
        # f128c452103b86698cd1165bf7360adbae5aaf916c49214787809bb2dae64141
        KeymapBinding(keymap_name='UV Editor', space_type='EMPTY', key='MIDDLEMOUSE', ctrl=True),
    ),
)

SELECTION_CIRCLE_ACTIONS: list[OperatorAction] = [
    SELECTION_3D_VIEW_CIRCLE_ADD,
    SELECTION_3D_VIEW_CIRCLE_SUBTRACT,
    SELECTION_UV_CIRCLE_ADD,
    SELECTION_UV_CIRCLE_SUBTRACT,
]


def get_selection_circle_actions() -> list[OperatorAction]:
    """Return all declared Circle Selection actions."""
    return SELECTION_CIRCLE_ACTIONS
