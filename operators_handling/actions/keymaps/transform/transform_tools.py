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


# ----------------------------------------------------------------------------------------------------------------------
# FEATURE: TRANSFORM TOOLS

# Paint Curve
TRANSFORM_PAINT_CURVE_TRANSLATE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Paint Curve')
)

# Pose
TRANSFORM_POSE_TRANSLATE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Pose')
)

# Object Mode
TRANSFORM_OBJECT_MODE_TRANSLATE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Object Mode')
)

# Curve
TRANSFORM_CURVE_TRANSLATE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Curve')
)

# Curves
TRANSFORM_CURVES_TRANSLATE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Curves')
)

# Mesh
TRANSFORM_MESH_TRANSLATE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Mesh')
)

# Armature
TRANSFORM_ARMATURE_TRANSLATE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Armature')
)

# Metaball
TRANSFORM_METABALL_TRANSLATE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Metaball')
)

# Lattice
TRANSFORM_LATTICE_TRANSLATE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Lattice')
)

# Particle
TRANSFORM_PARTICLE_TRANSLATE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Particle')
)

# Point Cloud
TRANSFORM_POINT_CLOUD_TRANSLATE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Point Cloud')
)

# Grease Pencil Edit Mode
TRANSFORM_GREASE_PENCIL_EDIT_MODE_TRANSLATE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Grease Pencil Edit Mode')
)

# UV Editor
TRANSFORM_UV_EDITOR_TRANSLATE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('UV Editor')
)

# Mask Editing
TRANSFORM_MASK_EDITING_TRANSLATE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Mask Editing')
)

# Graph Editor
TRANSFORM_GRAPH_EDITOR_TRANSLATE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Graph Editor', space_type='GRAPH_EDITOR')
)

# Node Editor
TRANSFORM_NODE_EDITOR_TRANSLATE = OperatorAction(
    operator='transform.translate',
    props={
        'view2d_edge_pan': True,
    },
    keymap_bindings=_translate_bindings('Node Editor', space_type='NODE_EDITOR')
)

# Preview
TRANSFORM_PREVIEW_TRANSLATE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Preview', space_type='SEQUENCE_EDITOR')
)

# Clip Editor
TRANSFORM_CLIP_EDITOR_TRANSLATE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Clip Editor', space_type='CLIP_EDITOR')
)

# Clip Graph Editor
TRANSFORM_CLIP_GRAPH_EDITOR_TRANSLATE = OperatorAction(
    operator='transform.translate',
    keymap_bindings=_translate_bindings('Clip Graph Editor', space_type='CLIP_EDITOR')
)

# ----------------------------------------------------------------------------------------------------------------------
# ACTION LIST

TRANSFORM_TOOLS_ACTIONS: list[OperatorAction] = [

    # Translate
    TRANSFORM_PAINT_CURVE_TRANSLATE,
    TRANSFORM_POSE_TRANSLATE,
    TRANSFORM_OBJECT_MODE_TRANSLATE,
    TRANSFORM_CURVE_TRANSLATE,
    TRANSFORM_CURVES_TRANSLATE,
    TRANSFORM_MESH_TRANSLATE,
    TRANSFORM_ARMATURE_TRANSLATE,
    TRANSFORM_METABALL_TRANSLATE,
    TRANSFORM_LATTICE_TRANSLATE,
    TRANSFORM_PARTICLE_TRANSLATE,
    TRANSFORM_POINT_CLOUD_TRANSLATE,
    TRANSFORM_GREASE_PENCIL_EDIT_MODE_TRANSLATE,
    TRANSFORM_UV_EDITOR_TRANSLATE,
    TRANSFORM_MASK_EDITING_TRANSLATE,
    TRANSFORM_GRAPH_EDITOR_TRANSLATE,
    TRANSFORM_NODE_EDITOR_TRANSLATE,
    TRANSFORM_PREVIEW_TRANSLATE,
    TRANSFORM_CLIP_EDITOR_TRANSLATE,
    TRANSFORM_CLIP_GRAPH_EDITOR_TRANSLATE,

    # Rotate

    # Scale

]


def get_transform_tools_actions() -> list[OperatorAction]:
    """
    Return all declared Blue Hole transform tool operator actions.
    """
    return TRANSFORM_TOOLS_ACTIONS
