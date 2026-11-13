"""
Transform gizmo keymap operator actions for Blue Hole.
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

from ....operator_action import OperatorAction, KeymapBinding

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


# Blender merges these mode maps by their EMPTY space, including UV Editor.
def _builtin_move_bindings(keymap_name: str) -> tuple[KeymapBinding, ...]:
    """
    Return the default Blue Hole keymap bindings for the built-in Move gizmo tool.
    """
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type='EMPTY',
            key='W',
            shift=True,
        ),
    )


def _builtin_rotate_bindings(keymap_name: str) -> tuple[KeymapBinding, ...]:
    """
    Return the default Blue Hole keymap bindings for the built-in Rotate gizmo tool.
    """
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type='EMPTY',
            key='E',
            shift=True,
        ),
    )


def _builtin_scale_bindings(keymap_name: str) -> tuple[KeymapBinding, ...]:
    """
    Return the default Blue Hole keymap bindings for the built-in Scale gizmo tool.
    """
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type='EMPTY',
            key='R',
            shift=True,
        ),
    )

# ----------------------------------------------------------------------------------------------------------------------
# FEATURE: GIZMO TRANSFORM TOOLS (BUILTIN)

# MOVE
TRANSFORM_TOOL_POSE_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Pose')
)

TRANSFORM_TOOL_OBJECT_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Object Mode')
)

TRANSFORM_TOOL_CURVE_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Curve')
)

TRANSFORM_TOOL_CURVES_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Curves')
)

TRANSFORM_TOOL_MESH_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Mesh')
)

TRANSFORM_TOOL_ARMATURE_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Armature')
)

TRANSFORM_TOOL_METABALL_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Metaball')
)

TRANSFORM_TOOL_LATTICE_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Lattice')
)

TRANSFORM_TOOL_UV_EDITOR_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('UV Editor')
)

TRANSFORM_TOOL_GREASE_PENCIL_EDIT_MODE_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Grease Pencil Edit Mode')
)

# ROTATE
TRANSFORM_TOOL_POSE_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Pose')
)

TRANSFORM_TOOL_OBJECT_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Object Mode')
)

TRANSFORM_TOOL_CURVE_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Curve')
)

TRANSFORM_TOOL_CURVES_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Curves')
)

TRANSFORM_TOOL_MESH_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Mesh')
)

TRANSFORM_TOOL_ARMATURE_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Armature')
)

TRANSFORM_TOOL_METABALL_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Metaball')
)

TRANSFORM_TOOL_LATTICE_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Lattice')
)

TRANSFORM_TOOL_UV_EDITOR_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('UV Editor')
)

TRANSFORM_TOOL_GREASE_PENCIL_EDIT_MODE_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Grease Pencil Edit Mode')
)

# SCALE
TRANSFORM_TOOL_POSE_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Pose')
)

TRANSFORM_TOOL_OBJECT_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Object Mode')
)

TRANSFORM_TOOL_CURVE_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Curve')
)

TRANSFORM_TOOL_CURVES_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Curves')
)

TRANSFORM_TOOL_MESH_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Mesh')
)

TRANSFORM_TOOL_ARMATURE_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Armature')
)

TRANSFORM_TOOL_METABALL_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Metaball')
)

TRANSFORM_TOOL_LATTICE_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Lattice')
)

TRANSFORM_TOOL_UV_EDITOR_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('UV Editor')
)

TRANSFORM_TOOL_GREASE_PENCIL_EDIT_MODE_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Grease Pencil Edit Mode')
)

TRANSFORM_TOOL_IMAGE_TRANSFORM = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Transform Tool (Gizmo)',
    props={'name': 'builtin.transform', 'cycle': True},
    keymap_bindings=(
        # 318ab4227e9699b1b4279142e4c99a612fec5ebf27e2f6a663adb07e6c88a02d
        KeymapBinding(keymap_name='Image', space_type='IMAGE_EDITOR', key='W'),
        # ba40873fbf25c357c6c711911eaa483711dba3a101390e753d9e7d2eabcce1a6
        KeymapBinding(keymap_name='Image', space_type='IMAGE_EDITOR', key='E'),
        # ff57544c10325e3984fef99805970ba7d3fa9d4bc93e6aa1e388e7f21b22e749
        KeymapBinding(keymap_name='Image', space_type='IMAGE_EDITOR', key='R'),
    ),
)

TRANSFORM_TOOL_UV_EDITOR_TRANSFORM = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Transform Tool (Gizmo)',
    props={'name': 'builtin.transform', 'cycle': True},
    keymap_bindings=(
        # 06f22b2be115a9adbc05174de8e78048c60c241aa07f6a6ff0e357df503ab717
        KeymapBinding(keymap_name='UV Editor', space_type='EMPTY', key='T'),
    ),
)

# ----------------------------------------------------------------------------------------------------------------------
# ACTION LIST

TRANSFORM_TOOLS_GIZMO_ACTIONS: list[OperatorAction] = [
    TRANSFORM_TOOL_POSE_MOVE,
    TRANSFORM_TOOL_OBJECT_MOVE,
    TRANSFORM_TOOL_CURVE_MOVE,
    TRANSFORM_TOOL_CURVES_MOVE,
    TRANSFORM_TOOL_MESH_MOVE,
    TRANSFORM_TOOL_ARMATURE_MOVE,
    TRANSFORM_TOOL_METABALL_MOVE,
    TRANSFORM_TOOL_LATTICE_MOVE,
    TRANSFORM_TOOL_UV_EDITOR_MOVE,
    TRANSFORM_TOOL_GREASE_PENCIL_EDIT_MODE_MOVE,

    TRANSFORM_TOOL_POSE_ROTATE,
    TRANSFORM_TOOL_OBJECT_ROTATE,
    TRANSFORM_TOOL_CURVE_ROTATE,
    TRANSFORM_TOOL_CURVES_ROTATE,
    TRANSFORM_TOOL_MESH_ROTATE,
    TRANSFORM_TOOL_ARMATURE_ROTATE,
    TRANSFORM_TOOL_METABALL_ROTATE,
    TRANSFORM_TOOL_LATTICE_ROTATE,
    TRANSFORM_TOOL_UV_EDITOR_ROTATE,
    TRANSFORM_TOOL_GREASE_PENCIL_EDIT_MODE_ROTATE,

    TRANSFORM_TOOL_POSE_SCALE,
    TRANSFORM_TOOL_OBJECT_SCALE,
    TRANSFORM_TOOL_CURVE_SCALE,
    TRANSFORM_TOOL_CURVES_SCALE,
    TRANSFORM_TOOL_MESH_SCALE,
    TRANSFORM_TOOL_ARMATURE_SCALE,
    TRANSFORM_TOOL_METABALL_SCALE,
    TRANSFORM_TOOL_LATTICE_SCALE,
    TRANSFORM_TOOL_UV_EDITOR_SCALE,
    TRANSFORM_TOOL_GREASE_PENCIL_EDIT_MODE_SCALE,

    TRANSFORM_TOOL_IMAGE_TRANSFORM,
    TRANSFORM_TOOL_UV_EDITOR_TRANSFORM,
]


def get_transform_tools_gizmo_actions() -> list[OperatorAction]:
    """
    Return all declared Blue Hole transform gizmo operator actions.
    """
    return TRANSFORM_TOOLS_GIZMO_ACTIONS
