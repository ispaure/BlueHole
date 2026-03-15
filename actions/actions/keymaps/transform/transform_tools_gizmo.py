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


def _builtin_move_bindings(keymap_name: str, space_type: str = 'VIEW_3D', region_type: str = 'WINDOW') -> tuple[KeymapBinding, ...]:
    """
    Return the default Blue Hole keymap bindings for the built-in Move gizmo tool.
    """
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='W',
            shift=True,
        ),
    )


def _builtin_rotate_bindings(keymap_name: str, space_type: str = 'VIEW_3D', region_type: str = 'WINDOW') -> tuple[KeymapBinding, ...]:
    """
    Return the default Blue Hole keymap bindings for the built-in Rotate gizmo tool.
    """
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='E',
            shift=True,
        ),
    )


def _builtin_scale_bindings(keymap_name: str, space_type: str = 'VIEW_3D', region_type: str = 'WINDOW') -> tuple[KeymapBinding, ...]:
    """
    Return the default Blue Hole keymap bindings for the built-in Scale gizmo tool.
    """
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
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
    keymap_bindings=_builtin_move_bindings('Pose', space_type='VIEW_3D')
)

TRANSFORM_TOOL_OBJECT_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Object Mode', space_type='VIEW_3D')
)

TRANSFORM_TOOL_CURVE_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Curve', space_type='VIEW_3D')
)

TRANSFORM_TOOL_CURVES_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Curves', space_type='VIEW_3D')
)

TRANSFORM_TOOL_MESH_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Mesh', space_type='VIEW_3D')
)

TRANSFORM_TOOL_ARMATURE_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Armature', space_type='VIEW_3D')
)

TRANSFORM_TOOL_METABALL_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Metaball', space_type='VIEW_3D')
)

TRANSFORM_TOOL_LATTICE_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Lattice', space_type='VIEW_3D')
)

TRANSFORM_TOOL_UV_EDITOR_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('UV Editor', space_type='IMAGE_EDITOR')
)

TRANSFORM_TOOL_GREASE_PENCIL_EDIT_MODE_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Move Tool (Gizmo)',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Grease Pencil Edit Mode', space_type='VIEW_3D')
)

# ROTATE
TRANSFORM_TOOL_POSE_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Pose', space_type='VIEW_3D')
)

TRANSFORM_TOOL_OBJECT_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Object Mode', space_type='VIEW_3D')
)

TRANSFORM_TOOL_CURVE_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Curve', space_type='VIEW_3D')
)

TRANSFORM_TOOL_CURVES_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Curves', space_type='VIEW_3D')
)

TRANSFORM_TOOL_MESH_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Mesh', space_type='VIEW_3D')
)

TRANSFORM_TOOL_ARMATURE_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Armature', space_type='VIEW_3D')
)

TRANSFORM_TOOL_METABALL_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Metaball', space_type='VIEW_3D')
)

TRANSFORM_TOOL_LATTICE_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Lattice', space_type='VIEW_3D')
)

TRANSFORM_TOOL_UV_EDITOR_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('UV Editor', space_type='IMAGE_EDITOR')
)

TRANSFORM_TOOL_GREASE_PENCIL_EDIT_MODE_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Rotate Tool (Gizmo)',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Grease Pencil Edit Mode', space_type='VIEW_3D')
)

# SCALE
TRANSFORM_TOOL_POSE_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Pose', space_type='VIEW_3D')
)

TRANSFORM_TOOL_OBJECT_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Object Mode', space_type='VIEW_3D')
)

TRANSFORM_TOOL_CURVE_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Curve', space_type='VIEW_3D')
)

TRANSFORM_TOOL_CURVES_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Curves', space_type='VIEW_3D')
)

TRANSFORM_TOOL_MESH_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Mesh', space_type='VIEW_3D')
)

TRANSFORM_TOOL_ARMATURE_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Armature', space_type='VIEW_3D')
)

TRANSFORM_TOOL_METABALL_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Metaball', space_type='VIEW_3D')
)

TRANSFORM_TOOL_LATTICE_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Lattice', space_type='VIEW_3D')
)

TRANSFORM_TOOL_UV_EDITOR_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('UV Editor', space_type='IMAGE_EDITOR')
)

TRANSFORM_TOOL_GREASE_PENCIL_EDIT_MODE_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    text='Scale Tool (Gizmo)',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Grease Pencil Edit Mode', space_type='VIEW_3D')
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
]


def get_transform_tools_gizmo_actions() -> list[OperatorAction]:
    """
    Return all declared Blue Hole transform gizmo operator actions.
    """
    return TRANSFORM_TOOLS_GIZMO_ACTIONS
