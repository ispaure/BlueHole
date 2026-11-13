"""Optional pipeline shortcut declarations."""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://github.com/ispaure/BlueHole

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

from ....operator_action import KeymapBinding, OperatorAction

PIPELINE_KEYMAP_GROUPS = {
    'export': 'enable_pipeline_export_shortcuts',
}

# Blender prepends add-on rows during merge. Register in reverse reference order
# so the merged map retains the order of these declarations.
_PIPELINE_CATALOG = (
    ('export', OperatorAction(
        operator='export_scene.fbx',
        keymap_bindings=(KeymapBinding(
            'Window', 'EMPTY', 'E', shift=True, ctrl=True, repeat=True),),
    )),
)


def get_all_pipeline_actions():
    return tuple(action for _, action in _PIPELINE_CATALOG)


def get_pipeline_group_actions(group):
    return tuple(action for feature, action in reversed(_PIPELINE_CATALOG) if feature == group)


def get_enabled_pipeline_catalog(preferences):
    return [action for group, action in _PIPELINE_CATALOG
            if getattr(preferences, PIPELINE_KEYMAP_GROUPS[group])]
