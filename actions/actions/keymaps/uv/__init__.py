"""
UV keymap action modules.
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

from ....operator_action import KeymapBinding, OperatorAction

# Display groups and the corresponding default-on feature switches.
UV_KEYMAP_GROUPS = {
    'selection': 'enable_uv_selection_shortcuts',
    'tools': 'enable_uv_tool_shortcuts',
    'actions': 'enable_uv_action_shortcuts',
}

# The runtime appends source items. Blender prepends those items to each merged
# map, so declaration order within each map is the reverse of the reference.
_UV_CATALOG = (
    # 797016483738b7c44213ce8949adee9466a5c1482832f8d34b928657015665f9
    ('selection', OperatorAction(
        operator='uv.select', text='Extend UV Tweak Selection',
        props={'extend': True},
        keymap_bindings=(KeymapBinding(
            'Image Editor Tool: Uv, Tweak (fallback)', 'IMAGE_EDITOR', 'RIGHTMOUSE', shift=True),),
    )),
    # 31d610f08818ec7acff104b540013dcb8083d522e1494e45293aed9f43e9c0a8
    ('selection', OperatorAction(
        operator='uv.select', text='UV Tweak Selection',
        props={'deselect_all': True},
        keymap_bindings=(KeymapBinding(
            'Image Editor Tool: Uv, Tweak (fallback)', 'IMAGE_EDITOR', 'RIGHTMOUSE'),),
    )),
    # 297b76f0871515c3a602f5a7423e5573ab4e2b8f762599397c5e00fb16ca57b6
    ('tools', OperatorAction(
        operator='uv.snap_cursor', text='Snap Cursor to Selected UVs',
        props={'target': 'SELECTED'},
        keymap_bindings=(KeymapBinding(
            'UV Editor', 'EMPTY', 'WHEELRIGHTMOUSE', shift=True, ctrl=True),),
    )),
    # 7efb92c43cf38ad343951a6316f6a5251c41c63e8f36ac5db375c2d88e78da65
    ('tools', OperatorAction(
        operator='uv.zenuv_move_cursor_to', text='Move Cursor to UV Area (Zen UV)',
        props={'influence': 'UV_AREA',
               'island_pivot': 'tl',
               'position': (0.0, 0.0),
               'tile_number': 1001},
        keymap_bindings=(KeymapBinding(
            'UV Editor', 'EMPTY', 'WHEELLEFTMOUSE', shift=True, ctrl=True),),
    )),
    # 6a7a77ba23548cef2dec48b16e530194135e6035beb5929f897e39346be86928
    ('actions', OperatorAction(
        operator='uv.zenuv_fit_to_trim', text='Fit to Trim (Zen UV)',
        props={'auto_unwrap': False,
               'fit_mode': 'TO_TRIM_T',
               'influence_mode': 'ISLAND',
               'influence_mode_faces': False,
               'info_message': '',
               'match_rotation': False,
               'op_align_to': 'cen',
               'op_fit_axis': 'AUTO',
               'op_keep_proportion': True,
               'op_order': 'ONE_BY_ONE',
               'op_padding': 0.0},
        keymap_bindings=(KeymapBinding(
            'UV Editor', 'EMPTY', 'MIDDLEMOUSE', shift=True, ctrl=True, alt=True, repeat=True),),
    )),
    # 3c73547c2b700fb14d4ca9b93320a557cef7f95d8c4b0b18b689c8134caab810
    ('tools', OperatorAction(
        operator='uv.cursor_set', text='Set UV Cursor',
        keymap_bindings=(KeymapBinding(
            'UV Editor', 'EMPTY', 'MIDDLEMOUSE', shift=True, ctrl=True),),
    )),
    # dcb6f79c6815728316fd55deb37520342ecd6616eb4b5f8aeb6d25fe8b7fd16e
    ('tools', OperatorAction(
        operator='uv.snap_cursor', text='Snap Cursor to Selected UVs',
        props={'target': 'SELECTED'},
        keymap_bindings=(KeymapBinding(
            'UV Editor', 'EMPTY', 'WHEELUPMOUSE', shift=True, ctrl=True),),
    )),
    # aba49cd61706f407686fbb1a1d8add0f45a29d2e6c863a4e1c95543ff36ce6d3
    ('selection', OperatorAction(
        operator='uv.select_linked_pick', text='Deselect Linked UVs',
        props={'extend': True, 'deselect': True},
        keymap_bindings=(KeymapBinding(
            'UV Editor', 'EMPTY', 'LEFTMOUSE', value='DOUBLE_CLICK', ctrl=True),),
    )),
    # 51527e5a764271307189138a0a1e1fd1f39358faa5c180ec70af846b49c3eebd
    ('selection', OperatorAction(
        operator='uv.select_linked_pick', text='Extend Linked UV Selection',
        props={'extend': True, 'deselect': False},
        keymap_bindings=(KeymapBinding(
            'UV Editor', 'EMPTY', 'LEFTMOUSE', value='DOUBLE_CLICK', shift=True),),
    )),
    # 760e8d5e05afd1ab0afb175e64f56c724eb05227a9d7d83f9e451672077ae8ea
    ('selection', OperatorAction(
        operator='uv.select_linked_pick', text='Select Linked UVs',
        props={'extend': False, 'deselect': False},
        keymap_bindings=(KeymapBinding(
            'UV Editor', 'EMPTY', 'LEFTMOUSE', value='DOUBLE_CLICK'),),
    )),
    # 2cc296fd06d5bf974968ac07da759dec261c268a1dd598c61175b5b4f11e7f65
    ('tools', OperatorAction(
        operator='wm.tool_set_by_id', text='Select Box Tool on Release',
        props={'name': 'builtin.select_box', 'cycle': False},
        keymap_bindings=(KeymapBinding(
            'UV Editor', 'EMPTY', 'Q', value='RELEASE'),),
    )),
    # 5cd2afd24dcb993de0c225921c2f69d83dbd583fc10135d98675b8c1db1412e0
    ('actions', OperatorAction(
        operator='uv.hide', text='Hide Selected UVs',
        props={'unselected': False},
        keymap_bindings=(KeymapBinding(
            'UV Editor', 'EMPTY', 'H', ctrl=True),),
    )),
    # 5fccd93d8aaf46c90ef18b42dc08a3e5d9babfb4263350b867b8c2dcf76b39fd
    ('selection', OperatorAction(
        operator='uv.select_loop', text='Select UV Loop',
        props={'extend': False},
        keymap_bindings=(KeymapBinding(
            'UV Editor', 'EMPTY', 'LEFTMOUSE', value='DOUBLE_CLICK', alt=True),),
    )),
    # 4be43c65802782650d9b12591136efbc6aa3bd962b6c0b77b96e059c2fac8c40
    ('selection', OperatorAction(
        operator='uv.select_loop', text='Extend UV Loop Selection',
        props={'extend': True},
        keymap_bindings=(KeymapBinding(
            'UV Editor', 'EMPTY', 'LEFTMOUSE', value='DOUBLE_CLICK', shift=True, alt=True),),
    )),
    # 4e2dc6fd4bdf26e2c0269c8384d35da4826c1a0f5d698621dabde8752cdacfa4
    ('tools', OperatorAction(
        operator='uv.cursor_set', text='Set UV Cursor',
        keymap_bindings=(KeymapBinding(
            'Image Editor Tool: Uv, Cursor', 'IMAGE_EDITOR', 'MIDDLEMOUSE'),),
    )),
)


def get_all_uv_actions():
    """Return the complete UV keymap catalog in source order."""
    return tuple(action for _, action in _UV_CATALOG)


def get_uv_group_actions(group):
    """Return the editable actions for one preference group."""
    return tuple(action for feature, action in reversed(_UV_CATALOG) if feature == group)


def get_enabled_uv_catalog(preferences):
    """Filter registration by group while preserving source order."""
    return [action for group, action in _UV_CATALOG
            if getattr(preferences, UV_KEYMAP_GROUPS[group])]
