"""Click and box selection bindings from the Deluxe reference."""

from ....operator_action import KeymapBinding, OperatorAction


# Exact ordinary Deluxe rows; source order reverses the merged reference order.
# ac5981ba17b4e3a48dc23fa51cdbc6e401b4ff10561f28af79feca5deece4567
DELUXE_WEIGHT_PAINT_SELECT_LEFTMOUSE_PRESS_ANY_CTRL = OperatorAction(
    operator='view3d.select', text='Weight Paint', props={},
    keymap_bindings=(KeymapBinding(
        keymap_name='Weight Paint', space_type='EMPTY',
        key='LEFTMOUSE', ctrl=True),),
)

# 49b3885cf9a2e5349064008da0b14aed1868a09241c5a98a4f2ba6fee97dd83a
DELUXE_WEIGHT_PAINT_SELECT_LEFTMOUSE_PRESS_ANY_OSKEY = OperatorAction(
    operator='view3d.select', text='Weight Paint', props={},
    keymap_bindings=(KeymapBinding(
        keymap_name='Weight Paint', space_type='EMPTY',
        key='LEFTMOUSE', oskey=True),),
)

# d7fc62a0a019529f9554ca26539348dca401f4cc598926cb05a76e05fec27068
DELUXE_UV_TWEAK_SELECT_LEFTMOUSE_PRESS_ANY = OperatorAction(
    operator='uv.select', text='UV Tweak', props={'deselect_all': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='Image Editor Tool: Uv, Tweak', space_type='IMAGE_EDITOR',
        key='LEFTMOUSE'),),
)

# 30a77ec81c2e833653a17f00083c6ca759afc3dbde6897b1a1f5b35d47a6aece
DELUXE_UV_TWEAK_FALLBACK_SELECT_LEFTMOUSE_PRESS_ANY = OperatorAction(
    operator='uv.select', text='UV Tweak (fallback)', props={'deselect_all': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='Image Editor Tool: Uv, Tweak (fallback)', space_type='IMAGE_EDITOR',
        key='LEFTMOUSE'),),
)

# a93f6fc5872027b0dc80be1747bf599d6013febf8c8ef3c5e9aa29642c5d4d98
DELUXE_UV_SELECT_BOX_FALLBACK_SELECT_BOX_RIGHTMOUSE_CLICK_DRAG_ANY_CTRL = OperatorAction(
    operator='uv.select_box', text='UV Select Box (fallback)', props={'mode': 'SUB'},
    keymap_bindings=(KeymapBinding(
        keymap_name='Image Editor Tool: Uv, Select Box (fallback)', space_type='IMAGE_EDITOR',
        key='RIGHTMOUSE', value='CLICK_DRAG', ctrl=True),),
)

# d8be63c7eb0147a512889f23d423a58562752ba8516730f7fdb11409f794e0c8
DELUXE_UV_SELECT_BOX_FALLBACK_SELECT_BOX_RIGHTMOUSE_CLICK_DRAG_ANY_OSKEY = OperatorAction(
    operator='uv.select_box', text='UV Select Box (fallback)', props={'mode': 'SUB'},
    keymap_bindings=(KeymapBinding(
        keymap_name='Image Editor Tool: Uv, Select Box (fallback)', space_type='IMAGE_EDITOR',
        key='RIGHTMOUSE', value='CLICK_DRAG', oskey=True),),
)

# 1849aa1a60ed68999ae073d9f74cd6ebec307c35c8e8012a84810ee737b978ff
DELUXE_UV_SELECT_BOX_FALLBACK_SELECT_BOX_RIGHTMOUSE_CLICK_DRAG_ANY_SHIFT = OperatorAction(
    operator='uv.select_box', text='UV Select Box (fallback)', props={'mode': 'ADD'},
    keymap_bindings=(KeymapBinding(
        keymap_name='Image Editor Tool: Uv, Select Box (fallback)', space_type='IMAGE_EDITOR',
        key='RIGHTMOUSE', value='CLICK_DRAG', shift=True),),
)

# 0977fa3b1bec3fa3cc36a746422d0e63cdddc8600b40bce2b7a624fc2dcfd763
DELUXE_UV_SELECT_BOX_FALLBACK_SELECT_BOX_RIGHTMOUSE_CLICK_DRAG_ANY = OperatorAction(
    operator='uv.select_box', text='UV Select Box (fallback)', props={},
    keymap_bindings=(KeymapBinding(
        keymap_name='Image Editor Tool: Uv, Select Box (fallback)', space_type='IMAGE_EDITOR',
        key='RIGHTMOUSE', value='CLICK_DRAG'),),
)

# 725039f48e3f530d2754e960958a47323fbeebbbcc63fcbe458d072ad2332805
DELUXE_TWEAK_SELECT_LEFTMOUSE_PRESS_ANY = OperatorAction(
    operator='view3d.select', text='Tweak', props={'deselect_all': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Tweak', space_type='VIEW_3D',
        key='LEFTMOUSE'),),
)

SELECTION_BASIC_ACTIONS = [
    DELUXE_WEIGHT_PAINT_SELECT_LEFTMOUSE_PRESS_ANY_CTRL,
    DELUXE_WEIGHT_PAINT_SELECT_LEFTMOUSE_PRESS_ANY_OSKEY,
    DELUXE_UV_TWEAK_SELECT_LEFTMOUSE_PRESS_ANY,
    DELUXE_UV_TWEAK_FALLBACK_SELECT_LEFTMOUSE_PRESS_ANY,
    DELUXE_UV_SELECT_BOX_FALLBACK_SELECT_BOX_RIGHTMOUSE_CLICK_DRAG_ANY_CTRL,
    DELUXE_UV_SELECT_BOX_FALLBACK_SELECT_BOX_RIGHTMOUSE_CLICK_DRAG_ANY_OSKEY,
    DELUXE_UV_SELECT_BOX_FALLBACK_SELECT_BOX_RIGHTMOUSE_CLICK_DRAG_ANY_SHIFT,
    DELUXE_UV_SELECT_BOX_FALLBACK_SELECT_BOX_RIGHTMOUSE_CLICK_DRAG_ANY,
    DELUXE_TWEAK_SELECT_LEFTMOUSE_PRESS_ANY,
]


def get_selection_basic_actions():
    return SELECTION_BASIC_ACTIONS
