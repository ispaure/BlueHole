"""Selection All / None keymap actions for the UV Editor."""

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = 'MIT License'
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

from ....operator_action import KeymapBinding, OperatorAction


# Binding comments cite the reviewed full rows in deluxe-baseline-2026-11-12-v1.
SELECTION_UV_SELECT_ALL = OperatorAction(
    operator='uv.select_all',
    text='Select All',
    props={'action': 'SELECT'},
    keymap_bindings=(
        # 18f7a532a4022c38749eed86f917b8c341de08618c84541affbe0b92690dea37
        KeymapBinding(keymap_name='UV Editor', space_type='EMPTY', key='A', ctrl=True),
        # 0e2e39eb0d50831c6f87106840dae8f823c7ec0db0ec91bab997385ec725ae8e
        KeymapBinding(keymap_name='UV Editor', space_type='EMPTY', key='A', oskey=True),
    ),
)

SELECTION_UV_DESELECT_ALL = OperatorAction(
    operator='uv.select_all',
    text='Deselect All',
    props={'action': 'DESELECT'},
    keymap_bindings=(
        # f92a635f5fc477b89c7bd3e0a02908aa33d920f3e1a5ce72f91c5b9064d917e8
        KeymapBinding(keymap_name='UV Editor', space_type='EMPTY', key='A', shift=True, ctrl=True),
        # fc77c97bf954e20548f91caf8abf9f03afb7dea9fa1da443c7b49c0f506d00df
        KeymapBinding(keymap_name='UV Editor', space_type='EMPTY', key='A', shift=True, oskey=True),
    ),
)

SELECTION_ALL_NONE_ACTIONS: list[OperatorAction] = [
    SELECTION_UV_SELECT_ALL,
    SELECTION_UV_DESELECT_ALL,
]


def get_selection_all_none_actions() -> list[OperatorAction]:
    """Return all declared Selection All / None actions."""
    return SELECTION_ALL_NONE_ACTIONS
