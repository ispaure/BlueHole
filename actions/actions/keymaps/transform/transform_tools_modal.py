"""
Transform modal keymap operator actions for Blue Hole.
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

# ----------------------------------------------------------------------------------------------------------------------
# FEATURE: TRANSFORM MODAL (TRANSLATE)

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
# FEATURE: TRANSFORM MODAL (ROTATE)

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
# FEATURE: TRANSFORM MODAL (RESIZE)

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
# ACTION LIST

TRANSFORM_TOOLS_MODAL_ACTIONS: list[OperatorAction] = [
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

    # Resize
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
]


def get_transform_tools_modal_actions() -> list[OperatorAction]:
    """
    Return all declared Blue Hole transform modal operator actions.
    """
    return TRANSFORM_TOOLS_MODAL_ACTIONS
