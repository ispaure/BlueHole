"""Legacy action adapter for exact, owned runtime keymap assignments."""

import hashlib

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

from .keymap_utils import (KeymapAssignment, KeymapEvent, KeymapScope,
                           KeymapTarget, _same, capture_scope, get_addon_keyconfig,
                           register_feature)

show_verbose = True
registered_navigation_keymaps = []


def _event(binding):
    map_type = binding.map_type
    if map_type is None:
        if 'MOUSE' in binding.key or 'TRACKPAD' in binding.key:
            map_type = 'MOUSE'
        elif binding.key.startswith('NDOF'):
            map_type = 'NDOF'
        else:
            map_type = 'KEYBOARD'
    return KeymapEvent(binding.key, binding.value, binding.any, binding.shift,
                       binding.ctrl, binding.alt, binding.oskey, binding.hyper,
                       binding.key_modifier, binding.direction, binding.repeat,
                       map_type)


def remove_existing_action_keymaps_from_keyconfig(category, kc, action):
    """Compatibility no-op: an operator match never grants deletion rights."""
    return 0


def _binding_scope(binding, config):
    stated = KeymapScope(binding.keymap_name, binding.space_type,
                         binding.region_type, False, binding.is_tool)
    if config is None or binding.is_tool is not None:
        return stated
    try:
        candidates = [capture_scope(map_) for map_ in config.keymaps
                      if map_.name == binding.keymap_name
                      and map_.space_type == binding.space_type
                      and map_.region_type == binding.region_type
                      and not map_.is_modal]
    except (AttributeError, ReferenceError, RuntimeError, TypeError):
        return stated
    return candidates[0] if len(candidates) == 1 else stated


def ensure_action_keymaps(category, action, context=None, keyconfig=None):
    """Register action bindings through the session ledger and return owned pairs.

    Dynamic properties are resolved once for the whole attempt. A missing add-on
    keyconfig leaves a pending feature for the lifecycle watcher.
    """
    if not action.keymap_bindings:
        return []
    if keyconfig is not None and not _same(keyconfig, get_addon_keyconfig()):
        return []
    if context is None:
        from bpy import context as blender_context
        context = blender_context
    try:
        idname = action.get_idname()
        properties = action.get_props(context)
        target = KeymapTarget(idname=idname, properties=properties)
    except (AttributeError, TypeError, ValueError, RuntimeError):
        return []
    assignments = tuple(KeymapAssignment(
        request_id=f'{index}:{binding.keymap_name}:{binding.key}:{binding.value}',
        scope=_binding_scope(binding, get_addon_keyconfig()),
        event=_event(binding), target=target, declared_properties_only=True,
        active=binding.active)
        for index, binding in enumerate(action.keymap_bindings))
    declaration_digest = hashlib.sha256(repr(assignments).encode('utf-8')).hexdigest()
    owner_id = f'legacy:{category}:{declaration_digest}'
    try:
        handle = register_feature(owner_id, assignments=assignments)
    except ValueError:
        return []
    pairs = handle.owned_pairs
    return pairs
