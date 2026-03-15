"""
Transform keymap operator actions for Blue Hole.
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


def _translate_bindings(keymap_name: str, space_type: str = 'EMPTY', region_type: str = 'WINDOW') -> tuple[KeymapBinding, ...]:
    """
    Return the default Blue Hole keymap bindings for a 'translate' style action.
    """
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='W',
        ),
    )


def _rotate_bindings(keymap_name: str, space_type: str = 'EMPTY', region_type: str = 'WINDOW') -> tuple[KeymapBinding, ...]:
    """
    Return the default Blue Hole keymap bindings for a 'rotate' style action.
    """
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='E',
        ),
    )


def _resize_bindings(keymap_name: str, space_type: str = 'EMPTY', region_type: str = 'WINDOW') -> tuple[KeymapBinding, ...]:
    """
    Return the default Blue Hole keymap bindings for a 'resize' style action.
    """
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='R',
        ),
    )


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
# FEATURE: TRANSFORM TOOLS (TRANSLATE)

# Paint Curve
TRANSFORM_TRANSLATE_PAINT_CURVE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Paint Curve')
)

# Pose
TRANSFORM_TRANSLATE_POSE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Pose')
)

# Object Mode
TRANSFORM_TRANSLATE_OBJECT_MODE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Object Mode')
)

# Curve
TRANSFORM_TRANSLATE_CURVE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Curve')
)

# Curves
TRANSFORM_TRANSLATE_CURVES = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Curves')
)

# Mesh
TRANSFORM_TRANSLATE_MESH = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Mesh')
)

# Armature
TRANSFORM_TRANSLATE_ARMATURE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Armature')
)

# Metaball
TRANSFORM_TRANSLATE_METABALL = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Metaball')
)

# Lattice
TRANSFORM_TRANSLATE_LATTICE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Lattice')
)

# Particle
TRANSFORM_TRANSLATE_PARTICLE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Particle')
)

# Point Cloud
TRANSFORM_TRANSLATE_POINT_CLOUD = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Point Cloud')
)

# Grease Pencil Edit Mode
TRANSFORM_TRANSLATE_GREASE_PENCIL_EDIT_MODE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Grease Pencil Edit Mode')
)

# UV Editor
TRANSFORM_TRANSLATE_UV_EDITOR = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('UV Editor')
)

# Mask Editing
TRANSFORM_TRANSLATE_MASK_EDITING = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Mask Editing')
)

# Graph Editor
TRANSFORM_TRANSLATE_GRAPH_EDITOR = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Graph Editor', space_type='GRAPH_EDITOR')
)

# Node Editor
TRANSFORM_TRANSLATE_NODE_EDITOR = OperatorAction(
    operator='transform.translate',
    props={
        'view2d_edge_pan': True,
    },
    keymap_bindings=_translate_bindings('Node Editor', space_type='NODE_EDITOR')
)

# Preview
TRANSFORM_TRANSLATE_PREVIEW = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Preview', space_type='SEQUENCE_EDITOR')
)

# Clip Editor
TRANSFORM_TRANSLATE_CLIP_EDITOR = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Clip Editor', space_type='CLIP_EDITOR')
)

# Clip Graph Editor
TRANSFORM_TRANSLATE_CLIP_GRAPH_EDITOR = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Clip Graph Editor', space_type='CLIP_EDITOR')
)

# ----------------------------------------------------------------------------------------------------------------------
# FEATURE: TRANSFORM TOOLS (ROTATE)

# Paint Curve
TRANSFORM_ROTATE_PAINT_CURVE = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('Paint Curve')
)

# Pose
TRANSFORM_ROTATE_POSE = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('Pose')
)

# Object Mode
TRANSFORM_ROTATE_OBJECT_MODE = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('Object Mode')
)

# Curve
TRANSFORM_ROTATE_CURVE = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('Curve')
)

# Curves
TRANSFORM_ROTATE_CURVES = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('Curves')
)

# Mesh
TRANSFORM_ROTATE_MESH = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('Mesh')
)

# Armature
TRANSFORM_ROTATE_ARMATURE = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('Armature')
)

# Metaball
TRANSFORM_ROTATE_METABALL = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('Metaball')
)

# Lattice
TRANSFORM_ROTATE_LATTICE = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('Lattice')
)

# Particle
TRANSFORM_ROTATE_PARTICLE = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('Particle')
)

# Point Cloud
TRANSFORM_ROTATE_POINT_CLOUD = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('Point Cloud')
)

# Grease Pencil Edit Mode
TRANSFORM_ROTATE_GREASE_PENCIL_EDIT_MODE = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('Grease Pencil Edit Mode')
)

# UV Editor
TRANSFORM_ROTATE_UV_EDITOR = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('UV Editor')
)

# Mask Editing
TRANSFORM_ROTATE_MASK_EDITING = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('Mask Editing')
)

# Graph Editor
TRANSFORM_ROTATE_GRAPH_EDITOR = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('Graph Editor', space_type='GRAPH_EDITOR')
)

# Node Editor
TRANSFORM_ROTATE_NODE_EDITOR = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('Node Editor', space_type='NODE_EDITOR')
)

# Preview
TRANSFORM_ROTATE_PREVIEW = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('Preview', space_type='SEQUENCE_EDITOR')
)

# Clip Editor
TRANSFORM_ROTATE_CLIP_EDITOR = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('Clip Editor', space_type='CLIP_EDITOR')
)

# Clip Graph Editor
TRANSFORM_ROTATE_CLIP_GRAPH_EDITOR = OperatorAction(
    operator='transform.rotate',
    keymap_bindings=_rotate_bindings('Clip Graph Editor', space_type='CLIP_EDITOR')
)

# ----------------------------------------------------------------------------------------------------------------------
# FEATURE: TRANSFORM TOOLS (RESIZE)

# Paint Curve
TRANSFORM_RESIZE_PAINT_CURVE = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('Paint Curve')
)

# Pose
TRANSFORM_RESIZE_POSE = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('Pose')
)

# Object Mode
TRANSFORM_RESIZE_OBJECT_MODE = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('Object Mode')
)

# Curve
TRANSFORM_RESIZE_CURVE = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('Curve')
)

# Curves
TRANSFORM_RESIZE_CURVES = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('Curves')
)

# Mesh
TRANSFORM_RESIZE_MESH = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('Mesh')
)

# Armature
TRANSFORM_RESIZE_ARMATURE = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('Armature')
)

# Metaball
TRANSFORM_RESIZE_METABALL = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('Metaball')
)

# Lattice
TRANSFORM_RESIZE_LATTICE = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('Lattice')
)

# Particle
TRANSFORM_RESIZE_PARTICLE = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('Particle')
)

# Point Cloud
TRANSFORM_RESIZE_POINT_CLOUD = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('Point Cloud')
)

# Grease Pencil Edit Mode
TRANSFORM_RESIZE_GREASE_PENCIL_EDIT_MODE = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('Grease Pencil Edit Mode')
)

# UV Editor
TRANSFORM_RESIZE_UV_EDITOR = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('UV Editor')
)

# Mask Editing
TRANSFORM_RESIZE_MASK_EDITING = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('Mask Editing')
)

# Graph Editor
TRANSFORM_RESIZE_GRAPH_EDITOR = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('Graph Editor', space_type='GRAPH_EDITOR')
)

# Node Editor
TRANSFORM_RESIZE_NODE_EDITOR = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('Node Editor', space_type='NODE_EDITOR')
)

# Preview
TRANSFORM_RESIZE_PREVIEW = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('Preview', space_type='SEQUENCE_EDITOR')
)

# Clip Editor
TRANSFORM_RESIZE_CLIP_EDITOR = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('Clip Editor', space_type='CLIP_EDITOR')
)

# Clip Graph Editor
TRANSFORM_RESIZE_CLIP_GRAPH_EDITOR = OperatorAction(
    operator='transform.resize',
    keymap_bindings=_resize_bindings('Clip Graph Editor', space_type='CLIP_EDITOR')
)

# ----------------------------------------------------------------------------------------------------------------------
# FEATURE: GIZMO TRANSFORM TOOLS (BUILTIN)

# MOVE
# Pose
TRANSFORM_TOOL_POSE_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Pose', space_type='VIEW_3D')
)

# Object Mode
TRANSFORM_TOOL_OBJECT_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Object Mode', space_type='VIEW_3D')
)

# Curve
TRANSFORM_TOOL_CURVE_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Curve', space_type='VIEW_3D')
)

# Curves
TRANSFORM_TOOL_CURVES_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Curves', space_type='VIEW_3D')
)

# Mesh
TRANSFORM_TOOL_MESH_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Mesh', space_type='VIEW_3D')
)

# Armature
TRANSFORM_TOOL_ARMATURE_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Armature', space_type='VIEW_3D')
)

# Metaball
TRANSFORM_TOOL_METABALL_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Metaball', space_type='VIEW_3D')
)

# Lattice
TRANSFORM_TOOL_LATTICE_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Lattice', space_type='VIEW_3D')
)

# UV Editor
TRANSFORM_TOOL_UV_EDITOR_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('UV Editor', space_type='IMAGE_EDITOR')
)

# Grease Pencil Edit mode
TRANSFORM_TOOL_GREASE_PENCIL_EDIT_MODE_MOVE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.move'},
    keymap_bindings=_builtin_move_bindings('Grease Pencil Edit Mode', space_type='VIEW_3D')
)

# ROTATE
# Pose
TRANSFORM_TOOL_POSE_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Pose', space_type='VIEW_3D')
)

# Object Mode
TRANSFORM_TOOL_OBJECT_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Object Mode', space_type='VIEW_3D')
)

# Curve
TRANSFORM_TOOL_CURVE_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Curve', space_type='VIEW_3D')
)

# Curves
TRANSFORM_TOOL_CURVES_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Curves', space_type='VIEW_3D')
)

# Mesh
TRANSFORM_TOOL_MESH_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Mesh', space_type='VIEW_3D')
)

# Armature
TRANSFORM_TOOL_ARMATURE_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Armature', space_type='VIEW_3D')
)

# Metaball
TRANSFORM_TOOL_METABALL_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Metaball', space_type='VIEW_3D')
)


# Lattice
TRANSFORM_TOOL_LATTICE_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Lattice', space_type='VIEW_3D')
)

# UV Editor
TRANSFORM_TOOL_UV_EDITOR_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('UV Editor', space_type='IMAGE_EDITOR')
)

# Grease Pencil Edit mode
TRANSFORM_TOOL_GREASE_PENCIL_EDIT_MODE_ROTATE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.rotate'},
    keymap_bindings=_builtin_rotate_bindings('Grease Pencil Edit Mode', space_type='VIEW_3D')
)

# SCALE
# Pose
TRANSFORM_TOOL_POSE_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Pose', space_type='VIEW_3D')
)

# Object Mode
TRANSFORM_TOOL_OBJECT_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Object Mode', space_type='VIEW_3D')
)

# Curve
TRANSFORM_TOOL_CURVE_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Curve', space_type='VIEW_3D')
)

# Curves
TRANSFORM_TOOL_CURVES_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Curves', space_type='VIEW_3D')
)

# Mesh
TRANSFORM_TOOL_MESH_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Mesh', space_type='VIEW_3D')
)

# Armature
TRANSFORM_TOOL_ARMATURE_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Armature', space_type='VIEW_3D')
)

# Metaball
TRANSFORM_TOOL_METABALL_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Metaball', space_type='VIEW_3D')
)

# Lattice
TRANSFORM_TOOL_LATTICE_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Lattice', space_type='VIEW_3D')
)

# UV Editor
TRANSFORM_TOOL_UV_EDITOR_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('UV Editor', space_type='IMAGE_EDITOR')
)


# Grease Pencil Edit mode
TRANSFORM_TOOL_GREASE_PENCIL_EDIT_MODE_SCALE = OperatorAction(
    operator='wm.tool_set_by_id',
    props={'name': 'builtin.scale'},
    keymap_bindings=_builtin_scale_bindings('Grease Pencil Edit Mode', space_type='VIEW_3D')
)

# ----------------------------------------------------------------------------------------------------------------------
# ACTION LIST

TRANSFORM_TOOLS_ACTIONS: list[OperatorAction] = [

    # Translate
    TRANSFORM_TRANSLATE_PAINT_CURVE,
    TRANSFORM_TRANSLATE_POSE,
    TRANSFORM_TRANSLATE_OBJECT_MODE,
    TRANSFORM_TRANSLATE_CURVE,
    TRANSFORM_TRANSLATE_CURVES,
    TRANSFORM_TRANSLATE_MESH,
    TRANSFORM_TRANSLATE_ARMATURE,
    TRANSFORM_TRANSLATE_METABALL,
    TRANSFORM_TRANSLATE_LATTICE,
    TRANSFORM_TRANSLATE_PARTICLE,
    TRANSFORM_TRANSLATE_POINT_CLOUD,
    TRANSFORM_TRANSLATE_GREASE_PENCIL_EDIT_MODE,
    TRANSFORM_TRANSLATE_UV_EDITOR,
    TRANSFORM_TRANSLATE_MASK_EDITING,
    TRANSFORM_TRANSLATE_GRAPH_EDITOR,
    TRANSFORM_TRANSLATE_NODE_EDITOR,
    TRANSFORM_TRANSLATE_PREVIEW,
    TRANSFORM_TRANSLATE_CLIP_EDITOR,
    TRANSFORM_TRANSLATE_CLIP_GRAPH_EDITOR,

    # Rotate
    TRANSFORM_ROTATE_PAINT_CURVE,
    TRANSFORM_ROTATE_POSE,
    TRANSFORM_ROTATE_OBJECT_MODE,
    TRANSFORM_ROTATE_CURVE,
    TRANSFORM_ROTATE_CURVES,
    TRANSFORM_ROTATE_MESH,
    TRANSFORM_ROTATE_ARMATURE,
    TRANSFORM_ROTATE_METABALL,
    TRANSFORM_ROTATE_LATTICE,
    TRANSFORM_ROTATE_PARTICLE,
    TRANSFORM_ROTATE_POINT_CLOUD,
    TRANSFORM_ROTATE_GREASE_PENCIL_EDIT_MODE,
    TRANSFORM_ROTATE_UV_EDITOR,
    TRANSFORM_ROTATE_MASK_EDITING,
    TRANSFORM_ROTATE_GRAPH_EDITOR,
    TRANSFORM_ROTATE_NODE_EDITOR,
    TRANSFORM_ROTATE_PREVIEW,
    TRANSFORM_ROTATE_CLIP_EDITOR,
    TRANSFORM_ROTATE_CLIP_GRAPH_EDITOR,

    # Scale
    TRANSFORM_RESIZE_PAINT_CURVE,
    TRANSFORM_RESIZE_POSE,
    TRANSFORM_RESIZE_OBJECT_MODE,
    TRANSFORM_RESIZE_CURVE,
    TRANSFORM_RESIZE_CURVES,
    TRANSFORM_RESIZE_MESH,
    TRANSFORM_RESIZE_ARMATURE,
    TRANSFORM_RESIZE_METABALL,
    TRANSFORM_RESIZE_LATTICE,
    TRANSFORM_RESIZE_PARTICLE,
    TRANSFORM_RESIZE_POINT_CLOUD,
    TRANSFORM_RESIZE_GREASE_PENCIL_EDIT_MODE,
    TRANSFORM_RESIZE_UV_EDITOR,
    TRANSFORM_RESIZE_MASK_EDITING,
    TRANSFORM_RESIZE_GRAPH_EDITOR,
    TRANSFORM_RESIZE_NODE_EDITOR,
    TRANSFORM_RESIZE_PREVIEW,
    TRANSFORM_RESIZE_CLIP_EDITOR,
    TRANSFORM_RESIZE_CLIP_GRAPH_EDITOR,

    # BUILT-IN MOVE, ROTATE, SCALE
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

    # ROTATE
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

    # SCALE
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


def get_transform_tools_actions() -> list[OperatorAction]:
    """
    Return all declared Blue Hole transform tool operator actions.
    """
    return TRANSFORM_TOOLS_ACTIONS
