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


# Exact ordinary Deluxe rows; source order reverses the merged reference order.
# 92a7039705de2b45a0588e10374abc4e0f035051c795ea9c103791f905ef0c5d
DELUXE_UV_SELECT_CIRCLE_FALLBACK_SELECT_CIRCLE_RIGHTMOUSE_CLICK_DRAG_ANY_CTRL = OperatorAction(
    operator='uv.select_circle', text='UV Select Circle (fallback)', props={'wait_for_input': False, 'mode': 'SUB'},
    keymap_bindings=(KeymapBinding(
        keymap_name='Image Editor Tool: Uv, Select Circle (fallback)', space_type='IMAGE_EDITOR',
        key='RIGHTMOUSE', value='CLICK_DRAG', ctrl=True),),
)

# dc1f8f23cd102dcfe2bc4fe2f6b8c0aa13881c75cb947cce60e75d5b24e6edc1
DELUXE_UV_SELECT_CIRCLE_FALLBACK_SELECT_CIRCLE_RIGHTMOUSE_CLICK_DRAG_ANY_OSKEY = OperatorAction(
    operator='uv.select_circle', text='UV Select Circle (fallback)', props={'wait_for_input': False, 'mode': 'SUB'},
    keymap_bindings=(KeymapBinding(
        keymap_name='Image Editor Tool: Uv, Select Circle (fallback)', space_type='IMAGE_EDITOR',
        key='RIGHTMOUSE', value='CLICK_DRAG', oskey=True),),
)

# e0a16ccd3f8f3ddbc61c3da5aa90aecac16e1300a4eb7b43d4b022d762e52939
DELUXE_UV_SELECT_CIRCLE_FALLBACK_SELECT_CIRCLE_RIGHTMOUSE_CLICK_DRAG_ANY_SHIFT = OperatorAction(
    operator='uv.select_circle', text='UV Select Circle (fallback)', props={'wait_for_input': False, 'mode': 'ADD'},
    keymap_bindings=(KeymapBinding(
        keymap_name='Image Editor Tool: Uv, Select Circle (fallback)', space_type='IMAGE_EDITOR',
        key='RIGHTMOUSE', value='CLICK_DRAG', shift=True),),
)

# 2ed8a85dcb09992dc6546c894b6f704f5882c2183cb4d1c96ac1a665ba3c6dbc
DELUXE_UV_SELECT_CIRCLE_FALLBACK_SELECT_CIRCLE_RIGHTMOUSE_CLICK_DRAG_ANY = OperatorAction(
    operator='uv.select_circle', text='UV Select Circle (fallback)', props={'wait_for_input': False},
    keymap_bindings=(KeymapBinding(
        keymap_name='Image Editor Tool: Uv, Select Circle (fallback)', space_type='IMAGE_EDITOR',
        key='RIGHTMOUSE', value='CLICK_DRAG'),),
)

# a7abdb0f1a76a33e484bc02febb2b5cb9a4bf9502e1a5a0a1c1ed2ee736e22c1
DELUXE_SELECT_CIRCLE_FALLBACK_SELECT_CIRCLE_RIGHTMOUSE_CLICK_DRAG_ANY_CTRL = OperatorAction(
    operator='view3d.select_circle', text='Select Circle (fallback)', props={'wait_for_input': False, 'mode': 'SUB'},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Select Circle (fallback)', space_type='VIEW_3D',
        key='RIGHTMOUSE', value='CLICK_DRAG', ctrl=True),),
)

# 7fc3ba226f32b930e4353fe72a7969cb36cd337d65892409fe36d2df9efad4f5
DELUXE_SELECT_CIRCLE_FALLBACK_SELECT_CIRCLE_RIGHTMOUSE_CLICK_DRAG_ANY_OSKEY = OperatorAction(
    operator='view3d.select_circle', text='Select Circle (fallback)', props={'wait_for_input': False, 'mode': 'SUB'},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Select Circle (fallback)', space_type='VIEW_3D',
        key='RIGHTMOUSE', value='CLICK_DRAG', oskey=True),),
)

# ec35cef734a1d37ca52f86c49d84a2926f2edf50f31a11afdc35f4c1bd656082
DELUXE_SELECT_CIRCLE_FALLBACK_SELECT_CIRCLE_RIGHTMOUSE_CLICK_DRAG_ANY_SHIFT = OperatorAction(
    operator='view3d.select_circle', text='Select Circle (fallback)', props={'wait_for_input': False, 'mode': 'ADD'},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Select Circle (fallback)', space_type='VIEW_3D',
        key='RIGHTMOUSE', value='CLICK_DRAG', shift=True),),
)

# 44692afb55e6f42196d8f7d04c6395271b307cd4aac003b0a4675e3a30c98037
DELUXE_SELECT_CIRCLE_FALLBACK_SELECT_CIRCLE_RIGHTMOUSE_CLICK_DRAG_ANY = OperatorAction(
    operator='view3d.select_circle', text='Select Circle (fallback)', props={'wait_for_input': False},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Select Circle (fallback)', space_type='VIEW_3D',
        key='RIGHTMOUSE', value='CLICK_DRAG'),),
)

SELECTION_CIRCLE_ACTIONS.extend([
    DELUXE_UV_SELECT_CIRCLE_FALLBACK_SELECT_CIRCLE_RIGHTMOUSE_CLICK_DRAG_ANY_CTRL,
    DELUXE_UV_SELECT_CIRCLE_FALLBACK_SELECT_CIRCLE_RIGHTMOUSE_CLICK_DRAG_ANY_OSKEY,
    DELUXE_UV_SELECT_CIRCLE_FALLBACK_SELECT_CIRCLE_RIGHTMOUSE_CLICK_DRAG_ANY_SHIFT,
    DELUXE_UV_SELECT_CIRCLE_FALLBACK_SELECT_CIRCLE_RIGHTMOUSE_CLICK_DRAG_ANY,
    DELUXE_SELECT_CIRCLE_FALLBACK_SELECT_CIRCLE_RIGHTMOUSE_CLICK_DRAG_ANY_CTRL,
    DELUXE_SELECT_CIRCLE_FALLBACK_SELECT_CIRCLE_RIGHTMOUSE_CLICK_DRAG_ANY_OSKEY,
    DELUXE_SELECT_CIRCLE_FALLBACK_SELECT_CIRCLE_RIGHTMOUSE_CLICK_DRAG_ANY_SHIFT,
    DELUXE_SELECT_CIRCLE_FALLBACK_SELECT_CIRCLE_RIGHTMOUSE_CLICK_DRAG_ANY,
])
