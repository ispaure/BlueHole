"""
Mesh keymap action modules.
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
MESH_KEYMAP_GROUPS = {
    'modeling': 'enable_mesh_modeling_shortcuts',
    'tools': 'enable_mesh_tool_shortcuts',
}

# The runtime appends source items. Blender prepends those items to each merged
# map, so declaration order within each map is the reverse of the reference.
_MESH_CATALOG = (
    # 20006917fb115bfe4e7a77704e45835b603cdc5f4ef12abe1f0af93dabd592e7
    ('tools', OperatorAction(
        operator='mesh.spin', text='Spin Duplicates',
        props={'dupli': True},
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Edit Mesh, Spin Duplicates', 'VIEW_3D', 'MIDDLEMOUSE'),),
    )),
    # d8cd023df47ab29c27794bf7fb85cca435353afef589c51a168aec12af7ef25f
    ('tools', OperatorAction(
        operator='mesh.vertices_smooth',
        props={'wait_for_input': False},
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Edit Mesh, Smooth', 'VIEW_3D', 'MIDDLEMOUSE'),),
    )),
    # c833011a50ab1d50fee6fc1becbe33896236874ef3dfbcfb5e69c46f08ac430f
    ('tools', OperatorAction(
        operator='mesh.spin',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Edit Mesh, Spin', 'VIEW_3D', 'MIDDLEMOUSE'),),
    )),
    # 6d050b91822f66544249fbea9b6e35973de6eab2b6ef802eb2beb16963fe1072
    ('tools', OperatorAction(
        operator='mesh.polybuild_delete_at_cursor',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Edit Mesh, Poly Build', 'VIEW_3D', 'MIDDLEMOUSE', value='CLICK', shift=True),),
    )),
    # 54cc7bae276824b03606263b36075be9aa7567d03d86171b63064c24024d55e3
    ('tools', OperatorAction(
        operator='mesh.bisect',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Edit Mesh, Bisect', 'VIEW_3D', 'MIDDLEMOUSE'),),
    )),
    # 4b3de21b3ab1ee655736a60b3618826ff279e2c3909e22f060fa20a3e3bc8eab
    ('tools', OperatorAction(
        operator='mesh.knife_tool',
        props={'wait_for_input': False},
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Edit Mesh, Knife', 'VIEW_3D', 'MIDDLEMOUSE'),),
    )),
    # 8aa820727c50f64243e143e68a15b3e8b78ef313cf054c1437e46fcbf0d8189e
    ('tools', OperatorAction(
        operator='mesh.bevel',
        props={'release_confirm': True},
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Edit Mesh, Bevel', 'VIEW_3D', 'MIDDLEMOUSE'),),
    )),
    # 450f04a4e645b136d511d6d1cee1d5b6d9c5122e6c28234a5a56d6654dd33bbf
    ('tools', OperatorAction(
        operator='mesh.inset',
        props={'release_confirm': True},
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Edit Mesh, Inset Faces', 'VIEW_3D', 'MIDDLEMOUSE'),),
    )),
    # d6599cf4a5a469492aac3e2c5435a2c904b2b000b33a3849bc6d7072acd38a87
    ('tools', OperatorAction(
        operator='mesh.dupli_extrude_cursor',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Edit Mesh, Extrude to Cursor', 'VIEW_3D', 'MIDDLEMOUSE'),),
    )),
    # 8bce3a1fb349dd222c49b6912946d61ee4ea10e13cb59b681cc10bd6e4300c51
    ('modeling', OperatorAction(
        operator='mesh.smart_delete',
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'D', alt=True, repeat=True),),
    )),
)


def get_all_mesh_actions():
    """Return the complete mesh keymap catalog in source order."""
    return tuple(action for _, action in _MESH_CATALOG)


def get_mesh_group_actions(group):
    """Return the editable actions for one preference group."""
    return tuple(action for feature, action in reversed(_MESH_CATALOG) if feature == group)


def get_enabled_mesh_catalog(preferences):
    """Filter registration by group while preserving source order."""
    return [action for group, action in _MESH_CATALOG
            if getattr(preferences, MESH_KEYMAP_GROUPS[group])]
