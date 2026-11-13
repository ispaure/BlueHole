"""
Object keymap action modules.
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
OBJECT_KEYMAP_GROUPS = {
    'modes': 'enable_object_mode_shortcuts',
    'actions': 'enable_object_action_shortcuts',
}

# The runtime appends source items. Blender prepends those items to each merged
# map, so declaration order within each map is the reverse of the reference.
_OBJECT_CATALOG = (
    # 6dce890f85a7057a2258bba3a156a0ea3d1841685d5bbe8af11db4da403d54c5
    ('actions', OperatorAction(
        operator='object.delete',
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'D', shift=True, alt=True, repeat=True),),
    )),
    # 0c6c9a982fc006ddb1a3662d075c3809ef2bc4b159bcbddc3f50b3ac3ff1e8d8
    ('actions', OperatorAction(
        operator='object.join_group_override', text='Join Groups',
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'J', ctrl=True),),
    )),
    # 066e2ffee7beebe46ae572d0ce9b6b2dc978527f99c3dccefc3460fa9b6cd0e5
    ('modes', OperatorAction(
        operator='object.transfer_mode',
        props={'use_flash_on_transfer': True},
        keymap_bindings=(KeymapBinding(
            'Object Non-modal', 'EMPTY', 'Q', alt=True, repeat=True),),
    )),
    # b190790c8f0da357a622febcff7396e565e5e62cec74ce4cdf13380fab14a825
    ('modes', OperatorAction(
        operator='object.mode_set', text='Enter Texture Paint Mode',
        props={'mode': 'TEXTURE_PAINT'},
        keymap_bindings=(KeymapBinding(
            'Object Non-modal', 'EMPTY', 'EIGHT'),),
    )),
    # 4851793d333d6f1e8d276e49a8940d82a4f92551a37a987e009cba5af377fcfa
    ('modes', OperatorAction(
        operator='object.mode_set', text='Enter Weight Paint Mode',
        props={'mode': 'WEIGHT_PAINT'},
        keymap_bindings=(KeymapBinding(
            'Object Non-modal', 'EMPTY', 'SEVEN'),),
    )),
    # 36df371e571aeb68f0dae75c0bbcd47897d7d9c2b6e1650851bd48fb35a87f07
    ('modes', OperatorAction(
        operator='object.mode_set', text='Enter Vertex Paint Mode',
        props={'mode': 'VERTEX_PAINT'},
        keymap_bindings=(KeymapBinding(
            'Object Non-modal', 'EMPTY', 'SIX'),),
    )),
    # 2ad26ab8df169cdad4260da5079b279334d38da38d9c562f1983aec8fc7ad078
    ('modes', OperatorAction(
        operator='object.mode_set', text='Enter Sculpt Mode',
        props={'mode': 'SCULPT'},
        keymap_bindings=(KeymapBinding(
            'Object Non-modal', 'EMPTY', 'FIVE'),),
    )),
    # ebc3996c3a5a233bc905d55e208a529b4aa5a173105d7c0ee048b24a6aa950ab
    ('modes', OperatorAction(
        operator='object.mode_set', text='Enter Object Mode',
        props={'mode': 'OBJECT'},
        keymap_bindings=(KeymapBinding(
            'Object Non-modal', 'EMPTY', 'FOUR'),),
    )),
    # c558fb5e3f165503e6cc11ad75931342528f0bb5c64188dcad7831da065e22e9
    ('modes', OperatorAction(
        operator='object.mode_set_with_submode', text='Edit Mesh Edges',
        props={'mode': 'EDIT', 'mesh_select_mode': ('EDGE',)},
        keymap_bindings=(KeymapBinding(
            'Object Non-modal', 'EMPTY', 'TWO'),),
    )),
    # 78d6fc1ba806253e9067beaf4d8b0c698dfb80e31844d3196907c95e5c4bb706
    ('modes', OperatorAction(
        operator='object.mode_set_with_submode', text='Edit Mesh Vertices',
        props={'mode': 'EDIT', 'mesh_select_mode': ('VERT',)},
        keymap_bindings=(KeymapBinding(
            'Object Non-modal', 'EMPTY', 'ONE'),),
    )),
    # 0dac693d5b64bc40d4e33e5807f238af17f74f0a05e77d6b2b992273fd3c33ae
    ('modes', OperatorAction(
        operator='object.mode_set', text='Enter Pose Mode',
        props={'mode': 'POSE'},
        keymap_bindings=(KeymapBinding(
            'Object Non-modal', 'EMPTY', 'THREE'),),
    )),
    # 385d1d258877e4f9f923a89cffc1fc1d9bd7b90ea353353116621eeb05c9224d
    ('modes', OperatorAction(
        operator='object.mode_set', text='Exit Edit Mode',
        keymap_bindings=(KeymapBinding(
            'Font', 'EMPTY', 'TAB'),),
    )),
    # 795a983eacf3b01d3740c30e98f0b0e34a0f9758fc5bc55e2fe7f3ff1ad96ff2
    ('modes', OperatorAction(
        operator='object.mode_set', text='Exit Edit Mode',
        keymap_bindings=(KeymapBinding(
            'Font', 'EMPTY', 'ESC'),),
    )),
    # 3005ad823c394d8b9d5cdf304c94872d822ee8f95e2ecf6db7df3d62dd65953b
    ('modes', OperatorAction(
        operator='object.mode_set', text='Exit Edit Mode',
        props={'mode': 'OBJECT', 'toggle': False},
        keymap_bindings=(KeymapBinding(
            'Curves', 'EMPTY', 'TAB'),),
    )),
)


def get_all_object_actions():
    """Return the complete object keymap catalog in source order."""
    return tuple(action for _, action in _OBJECT_CATALOG)


def get_object_group_actions(group):
    """Return the editable actions for one preference group."""
    return tuple(action for feature, action in reversed(_OBJECT_CATALOG) if feature == group)


def get_enabled_object_catalog(preferences):
    """Filter registration by group while preserving source order."""
    return [action for group, action in _OBJECT_CATALOG
            if getattr(preferences, OBJECT_KEYMAP_GROUPS[group])]
