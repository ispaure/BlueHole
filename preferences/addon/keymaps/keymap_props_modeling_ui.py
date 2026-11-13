"""Draw Object, Mesh and UV bindings in Blender's merged keyconfig."""

import rna_keymap_ui

from ....keymaps.keymap_action_utils import _binding_scope, _event
from ....keymaps.keymap_utils import (
    _Pending, capture_event, capture_scope, capture_target, get_keyconfig_sequence,
    owned_pairs_for_map,
)
from ....operators.ui_ops import WM_OT_BH_ToggleUISection, draw_action_feature_keymaps_dropdown_state


def draw_modeling_keymaps(column, preferences, toggle, actions):
    column.prop(preferences, toggle)
    if not getattr(preferences, toggle):
        return

    section = f'{type(preferences).__name__}.{toggle}'
    expanded = draw_action_feature_keymaps_dropdown_state.get(section, False)
    box = column.box()
    disclosure = box.operator(
        WM_OT_BH_ToggleUISection.bl_idname, text='See Bindings',
        icon='TRIA_DOWN' if expanded else 'TRIA_RIGHT', emboss=False,
    )
    disclosure.section_key = section
    if not expanded:
        return

    configs = get_keyconfig_sequence()
    if len(configs) != 2:
        return
    config, addon = configs

    current_scope = None
    for action in actions:
        binding, = action.keymap_bindings
        scope = _binding_scope(binding, addon)
        if scope != current_scope:
            current_scope = scope
            group = box.box()
            group.label(text=scope.name)
        group.label(text=action.get_label())
        keymap = _find_map(config, scope)
        source = _find_map(addon, scope)
        item = _find_binding(keymap, source, action, binding)
        if item is None:
            group.label(text='See Blender Preferences → Keymap for unavailable or edited bindings.')
            continue
        group.context_pointer_set('keymap', keymap)
        rna_keymap_ui.draw_kmi([], config, keymap, item, group, 0)


def _find_map(config, scope):
    matches = [keymap for keymap in config.keymaps if capture_scope(keymap) == scope]
    return matches[0] if len(matches) == 1 else None


def _find_binding(keymap, source, action, binding):
    if keymap is None or source is None:
        return None
    event = _event(binding)
    properties = action.get_props()
    idname = action.get_idname()
    targets = [target for _, item in owned_pairs_for_map(source)
               if (target := _matching_target(item, idname, event)) is not None
               and properties.items() <= dict(target.properties).items()]
    if len(targets) != 1:
        return None
    matches = [item for item in keymap.keymap_items
               if _matching_target(item, idname, event) == targets[0]]
    return matches[0] if len(matches) == 1 else None


def _matching_target(item, idname, event):
    if item.idname != idname:
        return None
    try:
        if capture_event(item) == event:
            return capture_target(item)
    except _Pending:
        return None
