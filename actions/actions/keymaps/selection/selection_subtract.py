"""Ordinary Ctrl-click selection subtraction."""

from ....operator_action import KeymapBinding, OperatorAction


SELECTION_OBJECT_SUBTRACT = OperatorAction(
    operator='view3d.select',
    text='Subtract Selection',
    props={'deselect': True, 'center': False, 'object': False},
    keymap_bindings=(
        # 8674bcb4d856346f287980fd961ade31095f1165d1f6e25725e4c06b81f582f3
        KeymapBinding(keymap_name='3D View', space_type='VIEW_3D',
                      key='LEFTMOUSE', value='CLICK', ctrl=True),
    ),
)

SELECTION_SUBTRACT_ACTIONS = [SELECTION_OBJECT_SUBTRACT]


def get_selection_subtract_actions():
    return SELECTION_SUBTRACT_ACTIONS
