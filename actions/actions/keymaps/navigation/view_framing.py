"""Navigation View Framing actions for the 3D View and Image Editor."""

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = 'MIT License'
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

from ....operator_action import KeymapBinding, OperatorAction


def _frame_bindings(
        keymap_name: str,
        space_type: str,
        key: str,
        vertical_wheel: str,
        horizontal_wheel: str,
) -> tuple[KeymapBinding, ...]:
    return (
        KeymapBinding(keymap_name=keymap_name, space_type=space_type, key=key),
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            key=vertical_wheel,
            shift=True,
            alt=True,
        ),
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            key=horizontal_wheel,
            shift=True,
            alt=True,
        ),
    )


# Binding comments cite the reviewed full rows in deluxe-baseline-2026-11-12-v1.
NAVIGATION_3D_VIEW_FRAME_SELECTED = OperatorAction(
    operator='view3d.view_selected',
    text='Frame Selected',
    props={'use_all_regions': False},
    keymap_bindings=_frame_bindings(
        '3D View', 'VIEW_3D',
        # 5ddc9654fc9d8dc2f2ed7afd21032b52ee06ffa1b290ead75cc30d662e3dbb21
        key='F',
        # d23d99c09a2c29942fa23f85fa4311b4206251b27ccd29ebec216ff005919c49
        vertical_wheel='WHEELUPMOUSE',
        # 4b508edb846741603ea365f625946e1426b96f1968cf52efdf310edf209917ae
        horizontal_wheel='WHEELRIGHTMOUSE',
    ),
)

NAVIGATION_3D_VIEW_FRAME_SELECTED_ALL_REGIONS = OperatorAction(
    operator='view3d.view_selected',
    text='Frame Selected in All Regions',
    props={'use_all_regions': True},
    keymap_bindings=(
        # c59a83b7bb1c2d1ed5f6637e43cfaafb20c8a7c2c27445750d30963d4791a0c6
        KeymapBinding(keymap_name='3D View', space_type='VIEW_3D', key='F', shift=True),
    ),
)

NAVIGATION_3D_VIEW_FRAME_ALL = OperatorAction(
    operator='view3d.view_all',
    text='Frame All',
    props={'center': False, 'use_all_regions': False},
    keymap_bindings=_frame_bindings(
        '3D View', 'VIEW_3D',
        # 38a81ee57f77e42a3019c75be83916f829ca1a40e1838fe08632014de9eadf6c
        key='A',
        # 4b75006949b2232e6d9677b856b9eb0af1a758a60bdc140cd3ad01269f35b427
        vertical_wheel='WHEELDOWNMOUSE',
        # f1b001e7a3d02ade59e105c82d3cc1ea1e8d191afada7b23d83181524ed0b680
        horizontal_wheel='WHEELLEFTMOUSE',
    ),
)

NAVIGATION_IMAGE_FRAME_SELECTED = OperatorAction(
    operator='image.view_selected',
    text='Frame Selected',
    keymap_bindings=_frame_bindings(
        'Image', 'IMAGE_EDITOR',
        # cfd89dd2f73dbd8a84092727005b9cd5bb3e95a6d51ba6a268a78865a4519fe7
        key='F',
        # 76e9b72f268687d8f88fb0b4b3765eaf5db36622e8768c0b2086de816406cb49
        vertical_wheel='WHEELUPMOUSE',
        # 818cab8bfca455cedfe75472338037544fc905a974173d30ee77baa11441f155
        horizontal_wheel='WHEELRIGHTMOUSE',
    ),
)

NAVIGATION_IMAGE_FRAME_ALL = OperatorAction(
    operator='image.view_all',
    text='Frame All',
    props={'fit_view': False},
    keymap_bindings=_frame_bindings(
        'Image', 'IMAGE_EDITOR',
        # 4d5203eeb62fedbfff7308eddf532619e2d2cb242006d1fde883e00675af6037
        key='A',
        # 08eb0ffb2a0d810ff836fb8c6b86b29e60bbd8ffd3854d30e2a5891425c47e47
        vertical_wheel='WHEELDOWNMOUSE',
        # b1c4e65516a1edfaeb88ae928fb789f032cd476e211672702f1b8b7d9f740874
        horizontal_wheel='WHEELLEFTMOUSE',
    ),
)

NAVIGATION_3D_VIEW_LOCAL_VIEW = OperatorAction(
    operator='view3d.localview',
    text='Toggle Local View',
    props={'frame_selected': True},
    keymap_bindings=(
        # 62d31f078d497b73967dd785c682a5a6840c9d4c81ddd82e1b43208fd6714e15
        KeymapBinding(keymap_name='3D View', space_type='VIEW_3D', key='I', shift=True),
    ),
)

NAVIGATION_VIEW_FRAMING_ACTIONS: list[OperatorAction] = [
    NAVIGATION_3D_VIEW_FRAME_SELECTED,
    NAVIGATION_3D_VIEW_FRAME_SELECTED_ALL_REGIONS,
    NAVIGATION_3D_VIEW_FRAME_ALL,
    NAVIGATION_IMAGE_FRAME_SELECTED,
    NAVIGATION_IMAGE_FRAME_ALL,
    NAVIGATION_3D_VIEW_LOCAL_VIEW,
]


def get_navigation_view_framing_actions() -> list[OperatorAction]:
    """Return all declared navigation View Framing actions."""
    return NAVIGATION_VIEW_FRAMING_ACTIONS
