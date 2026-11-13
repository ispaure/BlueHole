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
from .....operators.transform_ops import (
    WM_OT_BH_TranslateAutoConstraint,
    WM_OT_BH_RotateAutoConstraint,
    WM_OT_BH_ResizeAutoConstraint,
)

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


TRANSFORM_TRANSLATE_PAINT_CURVE = OperatorAction(
    operator='transform.translate',
    text='Move Tool (Modal)',
    keymap_bindings=_translate_bindings('Paint Curve')
)

TRANSFORM_TRANSLATE_POSE = OperatorAction(
    operator=WM_OT_BH_TranslateAutoConstraint,
    text='Move Tool (Modal)',
    keymap_bindings=_translate_bindings('Pose')
)

TRANSFORM_TRANSLATE_OBJECT_MODE = OperatorAction(
    operator=WM_OT_BH_TranslateAutoConstraint,
    text='Move Tool (Modal)',
    keymap_bindings=_translate_bindings('Object Mode')
)

TRANSFORM_TRANSLATE_CURVE = OperatorAction(
    operator=WM_OT_BH_TranslateAutoConstraint,
    text='Move Tool (Modal)',
    keymap_bindings=_translate_bindings('Curve')
)

TRANSFORM_TRANSLATE_CURVES = OperatorAction(
    operator=WM_OT_BH_TranslateAutoConstraint,
    text='Move Tool (Modal)',
    keymap_bindings=_translate_bindings('Curves')
)

TRANSFORM_TRANSLATE_MESH = OperatorAction(
    operator=WM_OT_BH_TranslateAutoConstraint,
    text='Move Tool (Modal)',
    keymap_bindings=_translate_bindings('Mesh')
)

TRANSFORM_TRANSLATE_ARMATURE = OperatorAction(
    operator=WM_OT_BH_TranslateAutoConstraint,
    text='Move Tool (Modal)',
    keymap_bindings=_translate_bindings('Armature')
)

TRANSFORM_TRANSLATE_METABALL = OperatorAction(
    operator=WM_OT_BH_TranslateAutoConstraint,
    text='Move Tool (Modal)',
    keymap_bindings=_translate_bindings('Metaball')
)

TRANSFORM_TRANSLATE_LATTICE = OperatorAction(
    operator=WM_OT_BH_TranslateAutoConstraint,
    text='Move Tool (Modal)',
    keymap_bindings=_translate_bindings('Lattice')
)

TRANSFORM_TRANSLATE_PARTICLE = OperatorAction(
    operator=WM_OT_BH_TranslateAutoConstraint,
    text='Move Tool (Modal)',
    keymap_bindings=_translate_bindings('Particle')
)

TRANSFORM_TRANSLATE_POINT_CLOUD = OperatorAction(
    operator=WM_OT_BH_TranslateAutoConstraint,
    text='Move Tool (Modal)',
    keymap_bindings=_translate_bindings('Point Cloud')
)

TRANSFORM_TRANSLATE_GREASE_PENCIL_EDIT_MODE = OperatorAction(
    operator='transform.translate',
    text='Move Tool (Modal)',
    keymap_bindings=_translate_bindings('Grease Pencil Edit Mode')
)

TRANSFORM_TRANSLATE_UV_EDITOR = OperatorAction(
    operator='transform.translate',
    text='Move Tool (Modal)',
    keymap_bindings=_translate_bindings('UV Editor')
)

TRANSFORM_TRANSLATE_UV_CURSOR = OperatorAction(
    operator='transform.translate',
    text='Move UV Cursor',
    props={'cursor_transform': True, 'release_confirm': True},
    keymap_bindings=(
        # ade9ef951b1ade1364980da4a38375de3cf040ad12a2419e56e644958dabfda1
        KeymapBinding(
            keymap_name='UV Editor',
            space_type='EMPTY',
            key='MIDDLEMOUSE',
            value='CLICK_DRAG',
            ctrl=True,
            shift=True,
        ),
    ),
)

TRANSFORM_TRANSLATE_MASK_EDITING = OperatorAction(
    operator='transform.translate',
    text='Move Tool (Modal)',
    keymap_bindings=_translate_bindings('Mask Editing')
)

TRANSFORM_TRANSLATE_GRAPH_EDITOR = OperatorAction(
    operator='transform.translate',
    text='Move Tool (Modal)',
    keymap_bindings=_translate_bindings('Graph Editor', space_type='GRAPH_EDITOR')
)

TRANSFORM_TRANSLATE_NODE_EDITOR = OperatorAction(
    operator='transform.translate',
    text='Move Tool (Modal)',
    props={'view2d_edge_pan': True},
    keymap_bindings=_translate_bindings('Node Editor', space_type='NODE_EDITOR')
)

TRANSFORM_TRANSLATE_PREVIEW = OperatorAction(
    operator='transform.translate',
    text='Move Tool (Modal)',
    keymap_bindings=_translate_bindings('Preview', space_type='SEQUENCE_EDITOR')
)

TRANSFORM_TRANSLATE_CLIP_EDITOR = OperatorAction(
    operator='transform.translate',
    text='Move Tool (Modal)',
    keymap_bindings=_translate_bindings('Clip Editor', space_type='CLIP_EDITOR')
)

TRANSFORM_TRANSLATE_CLIP_GRAPH_EDITOR = OperatorAction(
    operator='transform.translate',
    text='Move Tool (Modal)',
    keymap_bindings=_translate_bindings('Clip Graph Editor', space_type='CLIP_EDITOR')
)

# ----------------------------------------------------------------------------------------------------------------------
# FEATURE: TRANSFORM MODAL (ROTATE)

TRANSFORM_ROTATE_PAINT_CURVE = OperatorAction(
    operator='transform.rotate',
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('Paint Curve')
)

TRANSFORM_ROTATE_POSE = OperatorAction(
    operator=WM_OT_BH_RotateAutoConstraint,
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('Pose')
)

TRANSFORM_ROTATE_OBJECT_MODE = OperatorAction(
    operator=WM_OT_BH_RotateAutoConstraint,
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('Object Mode')
)

TRANSFORM_ROTATE_CURVE = OperatorAction(
    operator=WM_OT_BH_RotateAutoConstraint,
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('Curve')
)

TRANSFORM_ROTATE_CURVES = OperatorAction(
    operator=WM_OT_BH_RotateAutoConstraint,
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('Curves')
)

TRANSFORM_ROTATE_MESH = OperatorAction(
    operator=WM_OT_BH_RotateAutoConstraint,
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('Mesh')
)

TRANSFORM_ROTATE_ARMATURE = OperatorAction(
    operator=WM_OT_BH_RotateAutoConstraint,
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('Armature')
)

TRANSFORM_ROTATE_METABALL = OperatorAction(
    operator=WM_OT_BH_RotateAutoConstraint,
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('Metaball')
)

TRANSFORM_ROTATE_LATTICE = OperatorAction(
    operator=WM_OT_BH_RotateAutoConstraint,
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('Lattice')
)

TRANSFORM_ROTATE_PARTICLE = OperatorAction(
    operator=WM_OT_BH_RotateAutoConstraint,
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('Particle')
)

TRANSFORM_ROTATE_POINT_CLOUD = OperatorAction(
    operator=WM_OT_BH_RotateAutoConstraint,
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('Point Cloud')
)

TRANSFORM_ROTATE_GREASE_PENCIL_EDIT_MODE = OperatorAction(
    operator='transform.rotate',
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('Grease Pencil Edit Mode')
)

TRANSFORM_ROTATE_UV_EDITOR = OperatorAction(
    operator='transform.rotate',
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('UV Editor')
)

TRANSFORM_ROTATE_MASK_EDITING = OperatorAction(
    operator='transform.rotate',
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('Mask Editing')
)

TRANSFORM_ROTATE_GRAPH_EDITOR = OperatorAction(
    operator='transform.rotate',
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('Graph Editor', space_type='GRAPH_EDITOR')
)

TRANSFORM_ROTATE_NODE_EDITOR = OperatorAction(
    operator='transform.rotate',
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('Node Editor', space_type='NODE_EDITOR')
)

TRANSFORM_ROTATE_PREVIEW = OperatorAction(
    operator='transform.rotate',
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('Preview', space_type='SEQUENCE_EDITOR')
)

TRANSFORM_ROTATE_CLIP_EDITOR = OperatorAction(
    operator='transform.rotate',
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('Clip Editor', space_type='CLIP_EDITOR')
)

TRANSFORM_ROTATE_CLIP_GRAPH_EDITOR = OperatorAction(
    operator='transform.rotate',
    text='Rotate Tool (Modal)',
    keymap_bindings=_rotate_bindings('Clip Graph Editor', space_type='CLIP_EDITOR')
)

# ----------------------------------------------------------------------------------------------------------------------
# FEATURE: TRANSFORM MODAL (RESIZE)

TRANSFORM_RESIZE_PAINT_CURVE = OperatorAction(
    operator='transform.resize',
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('Paint Curve')
)

TRANSFORM_RESIZE_POSE = OperatorAction(
    operator=WM_OT_BH_ResizeAutoConstraint,
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('Pose')
)

TRANSFORM_RESIZE_OBJECT_MODE = OperatorAction(
    operator=WM_OT_BH_ResizeAutoConstraint,
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('Object Mode')
)

TRANSFORM_RESIZE_CURVE = OperatorAction(
    operator=WM_OT_BH_ResizeAutoConstraint,
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('Curve')
)

TRANSFORM_RESIZE_CURVES = OperatorAction(
    operator=WM_OT_BH_ResizeAutoConstraint,
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('Curves')
)

TRANSFORM_RESIZE_MESH = OperatorAction(
    operator=WM_OT_BH_ResizeAutoConstraint,
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('Mesh')
)

TRANSFORM_RESIZE_ARMATURE = OperatorAction(
    operator=WM_OT_BH_ResizeAutoConstraint,
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('Armature')
)

TRANSFORM_RESIZE_METABALL = OperatorAction(
    operator=WM_OT_BH_ResizeAutoConstraint,
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('Metaball')
)

TRANSFORM_RESIZE_LATTICE = OperatorAction(
    operator=WM_OT_BH_ResizeAutoConstraint,
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('Lattice')
)

TRANSFORM_RESIZE_PARTICLE = OperatorAction(
    operator=WM_OT_BH_ResizeAutoConstraint,
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('Particle')
)

TRANSFORM_RESIZE_POINT_CLOUD = OperatorAction(
    operator=WM_OT_BH_ResizeAutoConstraint,
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('Point Cloud')
)

TRANSFORM_RESIZE_GREASE_PENCIL_EDIT_MODE = OperatorAction(
    operator='transform.resize',
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('Grease Pencil Edit Mode')
)

TRANSFORM_RESIZE_UV_EDITOR = OperatorAction(
    operator='transform.resize',
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('UV Editor')
)

TRANSFORM_RESIZE_MASK_EDITING = OperatorAction(
    operator='transform.resize',
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('Mask Editing')
)

TRANSFORM_RESIZE_GRAPH_EDITOR = OperatorAction(
    operator='transform.resize',
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('Graph Editor', space_type='GRAPH_EDITOR')
)

TRANSFORM_RESIZE_NODE_EDITOR = OperatorAction(
    operator='transform.resize',
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('Node Editor', space_type='NODE_EDITOR')
)

TRANSFORM_RESIZE_PREVIEW = OperatorAction(
    operator='transform.resize',
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('Preview', space_type='SEQUENCE_EDITOR')
)

TRANSFORM_RESIZE_CLIP_EDITOR = OperatorAction(
    operator='transform.resize',
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('Clip Editor', space_type='CLIP_EDITOR')
)

TRANSFORM_RESIZE_CLIP_GRAPH_EDITOR = OperatorAction(
    operator='transform.resize',
    text='Scale Tool (Modal)',
    keymap_bindings=_resize_bindings('Clip Graph Editor', space_type='CLIP_EDITOR')
)

# ----------------------------------------------------------------------------------------------------------------------
# ACTION LIST

TRANSFORM_TOOLS_MODAL_ACTIONS: list[OperatorAction] = [
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
    TRANSFORM_TRANSLATE_UV_CURSOR,
    TRANSFORM_TRANSLATE_MASK_EDITING,
    TRANSFORM_TRANSLATE_GRAPH_EDITOR,
    TRANSFORM_TRANSLATE_NODE_EDITOR,
    TRANSFORM_TRANSLATE_PREVIEW,
    TRANSFORM_TRANSLATE_CLIP_EDITOR,
    TRANSFORM_TRANSLATE_CLIP_GRAPH_EDITOR,

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


# Local UV precedence for the reference Screen G / Repeat Last behavior.
# Stock UV Translate selector: a617d6ba7bffe5931c516dd6f7be58620c8bc146f29634ef62a12c2935a891da
# Reference Screen trigger (owner 05): 404d0973700b95f4354799748f01445ff8aefb0031509c88fa0c71647bdcfd2b
TRANSFORM_UV_REPEAT_LAST = OperatorAction(
    operator='screen.repeat_last',
    text='Repeat Last (UV)',
    keymap_bindings=(
        KeymapBinding(keymap_name='UV Editor', space_type='EMPTY', key='G', repeat=True),
    ),
)

TRANSFORM_ACTION_SHORTCUTS = [TRANSFORM_UV_REPEAT_LAST]


def get_transform_action_shortcuts() -> list[OperatorAction]:
    return TRANSFORM_ACTION_SHORTCUTS


# Exact ordinary Deluxe rows; source order reverses the merged reference order.
# 2da275dfdea64e1af816040ce670cc617972adff6d71209a08deb648aa0f9386
DELUXE_3D_VIEW_TRANSLATE_MIDDLEMOUSE_PRESS_ANY_SHIFTCTRL = OperatorAction(
    operator='transform.translate', text='3D View', props={'cursor_transform': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View', space_type='VIEW_3D',
        key='MIDDLEMOUSE', shift=True, ctrl=True),),
)

# 89cb7f518397c9ec8d21dddbc23755ab4b9a08e57064b70b853537c726ec3ee0
DELUXE_EDIT_ARMATURE_ROLL_TRANSFORM_MIDDLEMOUSE_PRESS_ANY = OperatorAction(
    operator='transform.transform', text='Edit Armature, Roll', props={'mode': 'BONE_ROLL', 'release_confirm': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Edit Armature, Roll', space_type='VIEW_3D',
        key='MIDDLEMOUSE'),),
)

# e282d1da12fee44a1c6e0f0b9bd9d3780e406aeebc48132c53a9aa2271b2e307
DELUXE_EDIT_ARMATURE_BONE_SIZE_TRANSFORM_MIDDLEMOUSE_PRESS_ANY = OperatorAction(
    operator='transform.transform', text='Edit Armature, Bone Size', props={'mode': 'BONE_ENVELOPE', 'release_confirm': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Edit Armature, Bone Size', space_type='VIEW_3D',
        key='MIDDLEMOUSE'),),
)

# d4d197feac7d4ae1e9048a60e7b762e02e21bd57f61c873fd8401b6beda437b5
DELUXE_EDIT_ARMATURE_BONE_ENVELOPE_BBONE_RESIZE_MIDDLEMOUSE_PRESS_ANY = OperatorAction(
    operator='transform.bbone_resize', text='Edit Armature, Bone Envelope', props={'release_confirm': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Edit Armature, Bone Envelope', space_type='VIEW_3D',
        key='MIDDLEMOUSE'),),
)

# bcae02cd13d1e011539c5d8dbdb29bf943eb66f8c2fc7789a493d317f55fa589
DELUXE_EDIT_MESH_RANDOMIZE_VERTEX_RANDOM_MIDDLEMOUSE_PRESS_ANY = OperatorAction(
    operator='transform.vertex_random', text='Edit Mesh, Randomize', props={'wait_for_input': False},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Edit Mesh, Randomize', space_type='VIEW_3D',
        key='MIDDLEMOUSE'),),
)

# 4ad6a1a938b0cf3b49f37d25f11cf2e4c4ad56f31c7f1882a5b5c642d90c624d
DELUXE_EDIT_MESH_EDGE_SLIDE_EDGE_SLIDE_MIDDLEMOUSE_PRESS_ANY = OperatorAction(
    operator='transform.edge_slide', text='Edit Mesh, Edge Slide', props={'release_confirm': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Edit Mesh, Edge Slide', space_type='VIEW_3D',
        key='MIDDLEMOUSE'),),
)

# 85a2956c0e0c91c3b8e855f46e6a482d14473619ba732632f58ef27b2b4e53f7
DELUXE_EDIT_MESH_VERTEX_SLIDE_VERT_SLIDE_MIDDLEMOUSE_PRESS_ANY = OperatorAction(
    operator='transform.vert_slide', text='Edit Mesh, Vertex Slide', props={'release_confirm': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Edit Mesh, Vertex Slide', space_type='VIEW_3D',
        key='MIDDLEMOUSE'),),
)

# f957e81133575b0b522168c54f283c11ce51f67c0198e9cdc13a01633ea0023f
DELUXE_EDIT_MESH_SHRINK_FATTEN_SHRINK_FATTEN_MIDDLEMOUSE_PRESS_ANY = OperatorAction(
    operator='transform.shrink_fatten', text='Edit Mesh, Shrink/Fatten', props={'release_confirm': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Edit Mesh, Shrink/Fatten', space_type='VIEW_3D',
        key='MIDDLEMOUSE'),),
)

# 0b3b17fdcef721534f7b102fd7d77e15e574080eda30999affa7d8af661ac929
DELUXE_EDIT_MESH_PUSH_PULL_PUSH_PULL_MIDDLEMOUSE_PRESS_ANY = OperatorAction(
    operator='transform.push_pull', text='Edit Mesh, Push/Pull', props={'release_confirm': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Edit Mesh, Push/Pull', space_type='VIEW_3D',
        key='MIDDLEMOUSE'),),
)

# bb82015ee5df69300ab84e2cc780f7e4265dc768586571ce0091bd6ebf382806
DELUXE_EDIT_MESH_TO_SPHERE_TOSPHERE_MIDDLEMOUSE_PRESS_ANY = OperatorAction(
    operator='transform.tosphere', text='Edit Mesh, To Sphere', props={'release_confirm': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Edit Mesh, To Sphere', space_type='VIEW_3D',
        key='MIDDLEMOUSE'),),
)

# 579a61643a511284f84f4524b20e68fc53814c4f4c95dbb21bd108a2089690d3
DELUXE_EDIT_CURVE_RADIUS_TRANSFORM_MIDDLEMOUSE_PRESS_ANY = OperatorAction(
    operator='transform.transform', text='Edit Curve, Radius', props={'mode': 'CURVE_SHRINKFATTEN', 'release_confirm': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Edit Curve, Radius', space_type='VIEW_3D',
        key='MIDDLEMOUSE'),),
)

# a923a65228974defa24e62f1dd309499b690215cf898aebdb5679a8ccb6a388b
DELUXE_EDIT_CURVE_TILT_TILT_MIDDLEMOUSE_PRESS_ANY = OperatorAction(
    operator='transform.tilt', text='Edit Curve, Tilt', props={'release_confirm': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Edit Curve, Tilt', space_type='VIEW_3D',
        key='MIDDLEMOUSE'),),
)

# 2a27ddc3e73f8afe2399cbc08bad0a8408803fc0818169bb9a23f27afac22783
DELUXE_EDIT_CURVE_RANDOMIZE_VERTEX_RANDOM_MIDDLEMOUSE_PRESS_ANY = OperatorAction(
    operator='transform.vertex_random', text='Edit Curve, Randomize', props={'wait_for_input': False},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Edit Curve, Randomize', space_type='VIEW_3D',
        key='MIDDLEMOUSE'),),
)

# 577f32f9ae4962d85fbd32829eec7b7908a681ad80488896451b2a48ab705b70
DELUXE_UV_MOVE_TRANSLATE_MIDDLEMOUSE_PRESS_ANY = OperatorAction(
    operator='transform.translate', text='UV Move', props={'release_confirm': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='Image Editor Tool: Uv, Move', space_type='IMAGE_EDITOR',
        key='MIDDLEMOUSE'),),
)

# c8a157e968c2607ba0cd2cb4a2282753fd6214c6b6930ed5091294ac08eb1b6c
DELUXE_UV_ROTATE_ROTATE_MIDDLEMOUSE_PRESS_ANY = OperatorAction(
    operator='transform.rotate', text='UV Rotate', props={'release_confirm': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='Image Editor Tool: Uv, Rotate', space_type='IMAGE_EDITOR',
        key='MIDDLEMOUSE'),),
)

# 70940e43122d3439e725435a71d452868374be484e3d4db437f5a55d322613d8
DELUXE_UV_SCALE_RESIZE_MIDDLEMOUSE_PRESS_ANY = OperatorAction(
    operator='transform.resize', text='UV Scale', props={'release_confirm': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='Image Editor Tool: Uv, Scale', space_type='IMAGE_EDITOR',
        key='MIDDLEMOUSE'),),
)

# ab3b061abbe012204066c8bcbd2afbc7d174b58fefe67e141f5fa9edde8c7dec
DELUXE_TWEAK_FALLBACK_TRANSLATE_LEFTMOUSE_CLICK_DRAG_ANY = OperatorAction(
    operator='transform.translate', text='Tweak (fallback)', props={'release_confirm': False},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Tweak (fallback)', space_type='VIEW_3D',
        key='LEFTMOUSE', value='CLICK_DRAG'),),
)

# a4c80c54d92171e6b4b488d4258342c1a8c12eeb20e6059d4449cdbbe915c8b7
DELUXE_MOVE_TRANSLATE_LEFTMOUSE_CLICK_DRAG_ANY = OperatorAction(
    operator='transform.translate', text='Move', props={'release_confirm': False},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Move', space_type='VIEW_3D',
        key='LEFTMOUSE', value='CLICK_DRAG'),),
)

# fd6e0ab6011eb8dd92255819fc80d0d36caacfacadee35caabc03d8778a03ee4
DELUXE_ROTATE_ROTATE_LEFTMOUSE_CLICK_DRAG_ANY = OperatorAction(
    operator='transform.rotate', text='Rotate', props={'release_confirm': False},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Rotate', space_type='VIEW_3D',
        key='LEFTMOUSE', value='CLICK_DRAG'),),
)

# 3edd30f9cef4a7830f5777df1e5a44531013979666e863323bce96ea1fe09ca8
DELUXE_SCALE_RESIZE_LEFTMOUSE_CLICK_DRAG_ANY = OperatorAction(
    operator='transform.resize', text='Scale', props={'release_confirm': False},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Scale', space_type='VIEW_3D',
        key='LEFTMOUSE', value='CLICK_DRAG'),),
)

# ddc19ef6688d562af64ea4ec6fb9601a124ec28047493c892bbbfbc32aa8d217
DELUXE_SHEAR_SHEAR_MIDDLEMOUSE_PRESS_ANY = OperatorAction(
    operator='transform.shear', text='Shear', props={'orient_axis_ortho': 'X', 'release_confirm': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Shear', space_type='VIEW_3D',
        key='MIDDLEMOUSE'),),
)

# 97098068e63f25cdc5a79f13d2ac15994d2852e42867f7a21024572271d2b4f4
DELUXE_SHEAR_SHEAR_MIDDLEMOUSE_CLICK_DRAG_SOUTH = OperatorAction(
    operator='transform.shear', text='Shear', props={'orient_axis_ortho': 'Y', 'release_confirm': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Shear', space_type='VIEW_3D',
        key='MIDDLEMOUSE', value='CLICK_DRAG', direction='SOUTH'),),
)

# 0708447fb1e254a30e01393ad0de5e9465ef39a0c915d9c1d16f4a2ac3556059
DELUXE_SHEAR_SHEAR_MIDDLEMOUSE_CLICK_DRAG_NORTH = OperatorAction(
    operator='transform.shear', text='Shear', props={'orient_axis_ortho': 'Y', 'release_confirm': True},
    keymap_bindings=(KeymapBinding(
        keymap_name='3D View Tool: Shear', space_type='VIEW_3D',
        key='MIDDLEMOUSE', value='CLICK_DRAG', direction='NORTH'),),
)

TRANSFORM_TOOLS_MODAL_ACTIONS.extend([
    DELUXE_3D_VIEW_TRANSLATE_MIDDLEMOUSE_PRESS_ANY_SHIFTCTRL,
    DELUXE_EDIT_ARMATURE_ROLL_TRANSFORM_MIDDLEMOUSE_PRESS_ANY,
    DELUXE_EDIT_ARMATURE_BONE_SIZE_TRANSFORM_MIDDLEMOUSE_PRESS_ANY,
    DELUXE_EDIT_ARMATURE_BONE_ENVELOPE_BBONE_RESIZE_MIDDLEMOUSE_PRESS_ANY,
    DELUXE_EDIT_MESH_RANDOMIZE_VERTEX_RANDOM_MIDDLEMOUSE_PRESS_ANY,
    DELUXE_EDIT_MESH_EDGE_SLIDE_EDGE_SLIDE_MIDDLEMOUSE_PRESS_ANY,
    DELUXE_EDIT_MESH_VERTEX_SLIDE_VERT_SLIDE_MIDDLEMOUSE_PRESS_ANY,
    DELUXE_EDIT_MESH_SHRINK_FATTEN_SHRINK_FATTEN_MIDDLEMOUSE_PRESS_ANY,
    DELUXE_EDIT_MESH_PUSH_PULL_PUSH_PULL_MIDDLEMOUSE_PRESS_ANY,
    DELUXE_EDIT_MESH_TO_SPHERE_TOSPHERE_MIDDLEMOUSE_PRESS_ANY,
    DELUXE_EDIT_CURVE_RADIUS_TRANSFORM_MIDDLEMOUSE_PRESS_ANY,
    DELUXE_EDIT_CURVE_TILT_TILT_MIDDLEMOUSE_PRESS_ANY,
    DELUXE_EDIT_CURVE_RANDOMIZE_VERTEX_RANDOM_MIDDLEMOUSE_PRESS_ANY,
    DELUXE_UV_MOVE_TRANSLATE_MIDDLEMOUSE_PRESS_ANY,
    DELUXE_UV_ROTATE_ROTATE_MIDDLEMOUSE_PRESS_ANY,
    DELUXE_UV_SCALE_RESIZE_MIDDLEMOUSE_PRESS_ANY,
    DELUXE_TWEAK_FALLBACK_TRANSLATE_LEFTMOUSE_CLICK_DRAG_ANY,
    DELUXE_MOVE_TRANSLATE_LEFTMOUSE_CLICK_DRAG_ANY,
    DELUXE_ROTATE_ROTATE_LEFTMOUSE_CLICK_DRAG_ANY,
    DELUXE_SCALE_RESIZE_LEFTMOUSE_CLICK_DRAG_ANY,
    DELUXE_SHEAR_SHEAR_MIDDLEMOUSE_PRESS_ANY,
    DELUXE_SHEAR_SHEAR_MIDDLEMOUSE_CLICK_DRAG_SOUTH,
    DELUXE_SHEAR_SHEAR_MIDDLEMOUSE_CLICK_DRAG_NORTH,
])
