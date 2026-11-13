"""Ordinary additive object-center and UV selection."""

from ....operator_action import KeymapBinding, OperatorAction


SELECTION_OBJECT_EXTEND_BY_CENTER = OperatorAction(
    operator='view3d.select',
    text='Extend Selection by Center',
    props={'center': True, 'extend': True, 'toggle': True},
    keymap_bindings=(
        # fee4a4d6ed723ffaa6fff80bdf81c6a3449e33667c182ee2ec2019699bff7d6d
        KeymapBinding(keymap_name='3D View', space_type='VIEW_3D',
                      key='LEFTMOUSE', value='CLICK', shift=True, oskey=True),
    ),
)

SELECTION_UV_EXTEND = OperatorAction(
    operator='uv.select',
    text='Extend UV Selection',
    props={'extend': True},
    keymap_bindings=(
        # 0e8d690a0470457363cd15ff3448c54325c24261cae1dc525ebff9c3dd459f1d
        KeymapBinding(keymap_name='UV Editor', space_type='EMPTY',
                      key='LEFTMOUSE', value='CLICK', shift=True),
    ),
)

SELECTION_EXTEND_ACTIONS = [SELECTION_OBJECT_EXTEND_BY_CENTER, SELECTION_UV_EXTEND]


def get_selection_extend_actions():
    return SELECTION_EXTEND_ACTIONS
