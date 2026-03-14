"""
Selection keymap operator actions for Blue Hole.
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


def _select_more_bindings(keymap_name: str, space_type: str = 'EMPTY', region_type: str = 'WINDOW') -> tuple[KeymapBinding, ...]:
    """
    Return the default Blue Hole keymap bindings for a 'select more' style action.
    """
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='WHEELUPMOUSE',
            shift=True,
        ),
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='WHEELRIGHTMOUSE',
            shift=True,
        ),
    )


def _select_less_bindings(keymap_name: str, space_type: str = 'EMPTY', region_type: str = 'WINDOW') -> tuple[KeymapBinding, ...]:
    """
    Return the default Blue Hole keymap bindings for a 'select less' style action.
    """
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='WHEELDOWNMOUSE',
            shift=True,
        ),
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='WHEELLEFTMOUSE',
            shift=True,
        ),
    )

# ----------------------------------------------------------------------------------------------------------------------
# FEATURE: SELECT MORE / SELECT LESS

# Dopesheet
SELECTION_DOPESHEET_SELECT_MORE = OperatorAction(
    operator='action.select_more',
    keymap_bindings=_select_more_bindings('Dopesheet')
)

SELECTION_DOPESHEET_SELECT_LESS = OperatorAction(
    operator='action.select_less',
    keymap_bindings=_select_less_bindings('Dopesheet')
)

# Object Mode
SELECTION_OBJECT_SELECT_MORE = OperatorAction(
    operator='object.select_hierarchy',
    props={
        'direction': 'PARENT',
        'extend': True,
    },
    keymap_bindings=_select_more_bindings('Object Mode')
)

SELECTION_OBJECT_SELECT_LESS = OperatorAction(
    operator='object.select_hierarchy',
    props={
        'direction': 'CHILD',
        'extend': True,
    },
    keymap_bindings=_select_less_bindings('Object Mode')
)

# Curve
SELECTION_CURVE_SELECT_MORE = OperatorAction(
    operator='curve.select_more',
    keymap_bindings=_select_more_bindings('Curve')
)

SELECTION_CURVE_SELECT_LESS = OperatorAction(
    operator='curve.select_less',
    keymap_bindings=_select_less_bindings('Curve')
)

# Curves
SELECTION_CURVES_SELECT_MORE = OperatorAction(
    operator='curves.select_more',
    keymap_bindings=_select_more_bindings('Curves')
)

SELECTION_CURVES_SELECT_LESS = OperatorAction(
    operator='curves.select_less',
    keymap_bindings=_select_less_bindings('Curves')
)

# Mesh
SELECTION_MESH_SELECT_MORE = OperatorAction(
    operator='mesh.select_more',
    keymap_bindings=_select_more_bindings('Mesh')
)

SELECTION_MESH_SELECT_LESS = OperatorAction(
    operator='mesh.select_less',
    keymap_bindings=_select_less_bindings('Mesh')
)

# Armature
SELECTION_ARMATURE_SELECT_MORE = OperatorAction(
    operator='armature.select_more',
    keymap_bindings=_select_more_bindings('Armature')
)

SELECTION_ARMATURE_SELECT_LESS = OperatorAction(
    operator='armature.select_less',
    keymap_bindings=_select_less_bindings('Armature')
)

# Lattice
SELECTION_LATTICE_SELECT_MORE = OperatorAction(
    operator='lattice.select_more',
    keymap_bindings=_select_more_bindings('Lattice')
)

SELECTION_LATTICE_SELECT_LESS = OperatorAction(
    operator='lattice.select_less',
    keymap_bindings=_select_less_bindings('Lattice')
)

# Particle
SELECTION_PARTICLE_SELECT_MORE = OperatorAction(
    operator='particle.select_more',
    keymap_bindings=_select_more_bindings('Particle')
)

SELECTION_PARTICLE_SELECT_LESS = OperatorAction(
    operator='particle.select_less',
    keymap_bindings=_select_less_bindings('Particle')
)

# UV Editor
SELECTION_UV_SELECT_MORE = OperatorAction(
    operator='uv.select_more',
    keymap_bindings=_select_more_bindings('UV Editor')
)

SELECTION_UV_SELECT_LESS = OperatorAction(
    operator='uv.select_less',
    keymap_bindings=_select_less_bindings('UV Editor')
)

# Mask Editing
SELECTION_MASK_SELECT_MORE = OperatorAction(
    operator='mask.select_more',
    keymap_bindings=_select_more_bindings('Mask Editing')
)

SELECTION_MASK_SELECT_LESS = OperatorAction(
    operator='mask.select_less',
    keymap_bindings=_select_less_bindings('Mask Editing')
)

# Graph Editor
SELECTION_GRAPH_SELECT_MORE = OperatorAction(
    operator='graph.select_more',
    keymap_bindings=_select_more_bindings('Graph Editor')
)

SELECTION_GRAPH_SELECT_LESS = OperatorAction(
    operator='graph.select_less',
    keymap_bindings=_select_less_bindings('Graph Editor')
)

# Node Editor
SELECTION_NODE_SELECT_MORE = OperatorAction(
    operator='node.select_linked_to',
    keymap_bindings=_select_more_bindings('Node Editor')
)

SELECTION_NODE_SELECT_LESS = OperatorAction(
    operator='node.select_linked_from',
    keymap_bindings=_select_less_bindings('Node Editor')
)

# Sequencer
SELECTION_SEQUENCER_SELECT_MORE = OperatorAction(
    operator='sequencer.select_more',
    keymap_bindings=_select_more_bindings('Sequencer')
)

SELECTION_SEQUENCER_SELECT_LESS = OperatorAction(
    operator='sequencer.select_less',
    keymap_bindings=_select_less_bindings('Sequencer')
)

# ----------------------------------------------------------------------------------------------------------------------
# TODO
#
# Transform Modal Map:
# This likely does not use a normal operator-based keymap item structure and may need a separate system.
# Investigate later before trying to fold it into OperatorAction.

# ----------------------------------------------------------------------------------------------------------------------
# ACTION LIST

SELECTION_MORE_LESS_ACTIONS: list[OperatorAction] = [
    SELECTION_DOPESHEET_SELECT_MORE,
    SELECTION_DOPESHEET_SELECT_LESS,

    SELECTION_OBJECT_SELECT_MORE,
    SELECTION_OBJECT_SELECT_LESS,

    SELECTION_CURVE_SELECT_MORE,
    SELECTION_CURVE_SELECT_LESS,

    SELECTION_CURVES_SELECT_MORE,
    SELECTION_CURVES_SELECT_LESS,

    SELECTION_MESH_SELECT_MORE,
    SELECTION_MESH_SELECT_LESS,

    SELECTION_ARMATURE_SELECT_MORE,
    SELECTION_ARMATURE_SELECT_LESS,

    SELECTION_LATTICE_SELECT_MORE,
    SELECTION_LATTICE_SELECT_LESS,

    SELECTION_PARTICLE_SELECT_MORE,
    SELECTION_PARTICLE_SELECT_LESS,

    SELECTION_UV_SELECT_MORE,
    SELECTION_UV_SELECT_LESS,

    SELECTION_MASK_SELECT_MORE,
    SELECTION_MASK_SELECT_LESS,

    SELECTION_GRAPH_SELECT_MORE,
    SELECTION_GRAPH_SELECT_LESS,

    SELECTION_NODE_SELECT_MORE,
    SELECTION_NODE_SELECT_LESS,

    SELECTION_SEQUENCER_SELECT_MORE,
    SELECTION_SEQUENCER_SELECT_LESS,
]


def get_selection_more_less_actions() -> list[OperatorAction]:
    """
    Return all declared Blue Hole selection more/less operator actions.
    """
    return SELECTION_MORE_LESS_ACTIONS
