"""Exact, session-owned Blender keymap registration and replacement.

No selector is an ownership token. Only a native item created in this session and
still present in its original configuration/map may be removed by this module.
"""

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

from dataclasses import dataclass, field
import math
import time
from collections.abc import Mapping

import bpy

EVENT_FIELDS = ('type', 'value', 'any', 'shift', 'ctrl', 'alt', 'oskey',
                'hyper', 'key_modifier', 'direction', 'repeat', 'map_type')
SCOPE_FIELDS = ('name', 'space_type', 'region_type', 'is_modal', 'is_tool')
_CONTEXT_PROOFS = frozenset(('stock_object_mode_select_all',
                             'synthetic_ordinary_provider',
                             'machin3tools_object_toggle_smooth',
                             'transform_translate_precision_cancel'))
_MODAL_PROOF = 'transform_translate_precision_cancel'
_MISSING = object()


def _freeze(value):
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is float and math.isfinite(value):
        return 0.0 if value == 0 else value
    if isinstance(value, Mapping):
        return tuple(sorted((str(k), _freeze(v)) for k, v in value.items()))
    if isinstance(value, (tuple, list)):
        return tuple(_freeze(v) for v in value)
    raise ValueError('unreadable_property_schema')


def _pointer(obj):
    try:
        return ('native', obj.as_pointer())
    except AttributeError:
        return ('python', id(obj))
    except (ReferenceError, RuntimeError):
        return None


def _same(a, b):
    if a is None or b is None:
        return False
    pointer = _pointer(a)
    return pointer is not None and pointer == _pointer(b)


def _members(collection):
    return tuple(collection)


def _contains(collection, obj):
    return any(_same(item, obj) for item in _members(collection))


@dataclass(frozen=True)
class KeymapScope:
    name: str
    space_type: str = 'EMPTY'
    region_type: str = 'WINDOW'
    is_modal: bool = False
    is_tool: bool | None = None


@dataclass(frozen=True)
class KeymapEvent:
    type: str
    value: str = 'PRESS'
    any: bool = False
    shift: bool | int = False
    ctrl: bool | int = False
    alt: bool | int = False
    oskey: bool | int = False
    hyper: bool | int | None = False
    key_modifier: str = 'NONE'
    direction: str = 'ANY'
    repeat: bool = False
    map_type: str = 'KEYBOARD'


@dataclass(frozen=True)
class KeymapTarget:
    idname: str = ''
    properties: tuple = ()
    modal_value: str = ''

    def __post_init__(self):
        object.__setattr__(self, 'properties', _freeze(dict(self.properties)))
        if bool(self.idname) == bool(self.modal_value):
            raise ValueError('Target requires exactly one operator or modal token')


@dataclass(frozen=True)
class KeymapAssignment:
    request_id: str
    scope: KeymapScope
    event: KeymapEvent
    target: KeymapTarget
    ledger_id: str = ''
    sample_id: str = ''
    declared_properties_only: bool = False
    active: bool = True


@dataclass(frozen=True)
class KeymapSelector:
    scope: KeymapScope
    event: KeymapEvent
    target: KeymapTarget
    source_role: str = 'default'
    ledger_id: str = ''
    sample_id: str = ''


def _selector_key(selector):
    return (selector.scope, selector.event, selector.target, selector.source_role)


def _scope_event(request):
    if isinstance(request, KeymapOverride):
        return request.selector.scope, request.selector.event
    return request.scope, request.event


@dataclass(frozen=True)
class KeymapOverride:
    request_id: str
    selector: KeymapSelector
    replacement: KeymapTarget
    capability: str = ''
    context: str = ''
    ledger_id: str = ''
    sample_id: str = ''
    replacement_event: KeymapEvent | None = field(default=None, init=False)
    replacement_active: bool = field(default=True, init=False)

    def __post_init__(self):
        if isinstance(self.replacement, KeymapAssignment):
            assignment = self.replacement
            object.__setattr__(self, 'replacement_event', assignment.event)
            object.__setattr__(self, 'replacement_active', assignment.active)
            object.__setattr__(self, 'replacement', assignment.target)


@dataclass(frozen=True)
class KeymapDiagnostic:
    owner_id: str
    request_id: str
    status: str
    reason: str
    ledger_id: str = ''
    sample_id: str = ''
    observed_role: str = ''
    observed_context: str = ''
    pending_capability: str = ''
    dispatch_evidence: bool = False


@dataclass
class _Owned:
    config: object
    map: object
    item: object
    snapshot: tuple
    source_config: object = None
    source_map: object = None
    source_item: object = None
    source_snapshot: tuple = ()
    source_index: int = -1
    overtakes: int = 0
    detached: bool = False
    owner_id: str = ''
    request_id: str = ''


class _Pending(Exception):
    def __init__(self, reason, status='pending', role='', capability=''):
        self.reason = reason
        self.status = status
        self.role = role
        self.capability = capability


_FEATURES = {}
_BOUND_CATEGORIES = {}
_CREATED_MAPS = {}
_RETAINED_EDITED = {}
_RECONCILE_CURSOR = 0
_COUNTS = {'checked': 0, 'created': 0, 'removed': 0, 'reinsertions': 0}


def get_window_manager():
    return getattr(bpy.context, 'window_manager', None)


def get_addon_keyconfig():
    wm = get_window_manager()
    return getattr(getattr(wm, 'keyconfigs', None), 'addon', None)


def get_keyconfig_sequence(check_user=True, check_addon=True, check_default=False):
    wm = get_window_manager()
    configs = getattr(wm, 'keyconfigs', None)
    if configs is None:
        return []
    return [config for enabled, role in ((check_user, 'user'), (check_addon, 'addon'),
                                         (check_default, 'default'))
            if enabled and (config := getattr(configs, role, None)) is not None]


def _scope(map_):
    try:
        return KeymapScope(map_.name, map_.space_type, map_.region_type,
                           map_.is_modal, getattr(map_, 'is_tool', None))
    except (AttributeError, ReferenceError, RuntimeError, ValueError) as exc:
        raise _Pending('unreadable_scope') from exc


def _maps(config, scope):
    try:
        return [map_ for map_ in _members(config.keymaps) if _scope(map_) == scope]
    except (AttributeError, ReferenceError, RuntimeError, TypeError) as exc:
        raise _Pending('unreadable_keymaps') from exc


def _one_map(config, scope, *, required=True):
    maps = _maps(config, scope)
    if len(maps) > 1:
        raise _Pending('ambiguous_scope', 'unsupported')
    if not maps and required:
        raise _Pending('missing_scope')
    return maps[0] if maps else None


def _config(role):
    wm = get_window_manager()
    config = getattr(getattr(wm, 'keyconfigs', None), role, None)
    if config is None:
        raise _Pending('keyconfig_unavailable', role=role)
    return config


def _update_merged():
    wm = get_window_manager()
    update = getattr(getattr(wm, 'keyconfigs', None), 'update', None)
    if callable(update):
        try:
            update()
        except (AttributeError, ReferenceError, RuntimeError, TypeError) as exc:
            raise _Pending('merged_update_failed') from exc


def _event(item):
    try:
        values = tuple(getattr(item, field, None) for field in EVENT_FIELDS)
        if values[0] in ('', None) or values[1] in ('', None) or any(value == '' for value in values):
            raise _Pending('unreadable_event')
        return KeymapEvent(*values)
    except (AttributeError, ReferenceError, RuntimeError, ValueError, TypeError) as exc:
        raise _Pending('unreadable_event') from exc


def _properties(item):
    props = getattr(item, 'properties', None)
    if props is None:
        raise _Pending('unreadable_property_schema')
    schema = getattr(getattr(props, 'bl_rna', None), 'properties', None)
    if schema is None:
        # Mapping is useful for a deterministic fake; real Blender must provide RNA.
        if isinstance(props, Mapping):
            return _freeze(props)
        raise _Pending('unreadable_property_schema')
    values = {}
    try:
        for prop in schema:
            name = prop.identifier
            if name == 'rna_type':
                continue
            if prop.type in ('POINTER', 'COLLECTION'):
                raise _Pending('unreadable_property_schema')
            value = getattr(props, name)
            if prop.type == 'ENUM' and value == '':
                raise _Pending('unreadable_property_schema')
            values[name] = _freeze(value)
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError) as exc:
        raise _Pending('unreadable_property_schema') from exc
    return _freeze(values)


def _target(item, modal):
    try:
        if modal:
            token = item.propvalue
            if not token or token == 'NONE':
                raise _Pending('unknown_modal_token', 'unsupported')
            return KeymapTarget(modal_value=token)
        idname = item.idname
        if not idname:
            raise _Pending('unreadable_target')
        return KeymapTarget(idname=idname, properties=_properties(item))
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError) as exc:
        raise _Pending('unreadable_target') from exc


def _snapshot(item, modal):
    try:
        return (_event(item), _target(item, modal), bool(item.active))
    except (AttributeError, ReferenceError, RuntimeError) as exc:
        raise _Pending('unreadable_item') from exc


def _exact_source(selector):
    if selector.source_role not in ('default', 'active', 'addon'):
        raise _Pending('unsupported_source_role', 'unsupported', selector.source_role)
    config = _config(selector.source_role)
    map_ = _one_map(config, selector.scope)
    if not _same(_config(selector.source_role), config):
        raise _Pending('source_generation_changed')
    matches = []
    for item in _members(map_.keymap_items):
        try:
            if _event(item) != selector.event:
                continue
            if selector.scope.is_modal:
                if getattr(item, 'propvalue') != selector.target.modal_value:
                    continue
            elif getattr(item, 'idname') != selector.target.idname:
                continue
            if _snapshot(item, selector.scope.is_modal) == (selector.event, selector.target, True):
                matches.append(item)
        except (AttributeError, ReferenceError, RuntimeError, ValueError) as exc:
            raise _Pending('unreadable_candidate_target') from exc
        except _Pending:
            # An unreadable candidate can mask an otherwise apparent exact match.
            raise
    if len(matches) > 1:
        raise _Pending('ambiguous_source', 'unsupported', selector.source_role)
    if not matches:
        raise _Pending('source_missing_or_edited', role=selector.source_role)
    if any(_same(matches[0], owned.item) and _same(map_, owned.map)
           for handle in _FEATURES.values() for owned in handle._owned.values()):
        raise _Pending('source_is_runtime_owned', 'unsupported', selector.source_role)
    return config, map_, matches[0]


def _diagnostic(handle, request, status, reason, role='', capability=''):
    if not capability and status in ('pending', 'unsupported'):
        capability = getattr(request, 'capability', '')
    return KeymapDiagnostic(handle.owner_id, request.request_id, status, reason,
                            getattr(request, 'ledger_id', '') or getattr(getattr(request, 'selector', None), 'ledger_id', ''),
                            getattr(request, 'sample_id', '') or getattr(getattr(request, 'selector', None), 'sample_id', ''),
                            role, getattr(request, 'context', ''), capability)


def _valid_owned(owned):
    try:
        configs = get_window_manager().keyconfigs
        if not any(_same(getattr(configs, role, None), owned.config)
                   for role in ('addon', 'default', 'active')):
            return False
        return (_contains(owned.config.keymaps, owned.map) and
                _contains(owned.map.keymap_items, owned.item))
    except (AttributeError, ReferenceError, RuntimeError, TypeError):
        return False


def _remove_owned(owned):
    if not _valid_owned(owned):
        return 'stale_owned_reference'
    try:
        if _snapshot(owned.item, _scope(owned.map).is_modal) != owned.snapshot:
            _retain_edited(owned)
            return 'user_edited_owned_item_retained'
    except _Pending:
        _retain_edited(owned)
        return 'unreadable_owned_item_retained'
    try:
        owned.map.keymap_items.remove(owned.item)
        _COUNTS['removed'] += 1
        _remove_empty_map(owned.config, owned.map)
        try:
            _update_merged()
        except _Pending:
            return 'released_merged_update_failed'
        return 'released'
    except (AttributeError, ReferenceError, RuntimeError, ValueError):
        return 'owned_remove_failed'


def _retain_edited(owned):
    owned.detached = True
    _RETAINED_EDITED[(_pointer(owned.config), _pointer(owned.map), _pointer(owned.item))] = owned
    _CREATED_MAPS.pop((_pointer(owned.config), _pointer(owned.map)), None)


def retained_edits():
    """Visible source rows transferred to the user after direct source edits."""
    rows = []
    for key, owned in tuple(_RETAINED_EDITED.items()):
        if not _valid_owned(owned):
            _RETAINED_EDITED.pop(key, None)
            continue
        try:
            scope = _scope(owned.map)
            current = _snapshot(owned.item, scope.is_modal)
        except _Pending:
            current = None
            scope = None
        rows.append({'owner_id': owned.owner_id, 'request_id': owned.request_id,
                     'scope': scope, 'current': current})
    return tuple(rows)


def _new_item(map_, target, event):
    kwargs = dict(type=event.type, value=event.value, any=event.any,
                  shift=event.shift, ctrl=event.ctrl, alt=event.alt,
                  oskey=event.oskey, key_modifier=event.key_modifier,
                  direction=event.direction, repeat=event.repeat, head=False)
    # Blender versions differ on repeat/head keyword support; a rejected schema
    # fails closed rather than emitting an item with silently changed fields.
    before = {_pointer(item) for item in _members(map_.keymap_items)}
    try:
        item = map_.keymap_items.new(target.idname, **kwargs)
    except (TypeError, AttributeError, ValueError, RuntimeError) as exc:
        candidates = [item for item in _members(map_.keymap_items)
                      if _pointer(item) not in before and getattr(item, 'idname', None) == target.idname]
        if len(candidates) == 1:
            map_.keymap_items.remove(candidates[0])
        raise _Pending('unsupported_creation_schema', 'unsupported') from exc
    return item


def _validate_created(owned, expected_event, expected_target, expected_active=True):
    if not _valid_owned(owned):
        raise _Pending('created_membership_lost')
    actual = _snapshot(owned.item, _scope(owned.map).is_modal)
    if actual != (expected_event, expected_target, expected_active):
        raise _Pending('created_readback_mismatch', 'unsupported')
    owned.snapshot = actual


def _legacy_event_readback(actual, expected):
    defaults = KeymapEvent(expected.type, expected.value)
    for field in EVENT_FIELDS:
        observed = getattr(actual, field)
        wanted = getattr(expected, field)
        if observed is None and field not in ('type', 'value') and wanted == getattr(defaults, field):
            continue
        if observed != wanted:
            return False
    return True


def _create_assignment(request):
    if request.scope.is_modal or request.target.modal_value:
        raise _Pending('unsupported_assignment_kind', 'unsupported')
    config = _config('addon')
    map_ = _one_map(config, request.scope, required=False)
    created_map = False
    if map_ is None:
        if request.scope.is_tool is not None:
            raise _Pending('unproved_tool_scope', 'unsupported')
        before_maps = {_pointer(candidate) for candidate in _members(config.keymaps)}
        map_ = config.keymaps.new(name=request.scope.name, space_type=request.scope.space_type,
                                  region_type=request.scope.region_type)
        if _pointer(map_) in before_maps:
            raise _Pending('existing_map_scope_conflict', 'unsupported')
        created_map = True
        _CREATED_MAPS[(_pointer(config), _pointer(map_))] = (config, map_)
    actual_scope = _scope(map_)
    if (actual_scope.name, actual_scope.space_type, actual_scope.region_type,
            actual_scope.is_modal) != (request.scope.name, request.scope.space_type,
                                       request.scope.region_type, request.scope.is_modal) or \
            (request.scope.is_tool is not None and actual_scope.is_tool != request.scope.is_tool) or \
            actual_scope.is_tool is True:
        if created_map:
            _remove_empty_map(config, map_)
        raise _Pending('created_scope_mismatch', 'unsupported')
    try:
        item = _new_item(map_, request.target, request.event)
    except Exception:
        if created_map:
            _remove_empty_map(config, map_)
        raise
    owned = _Owned(config, map_, item, ())
    try:
        for key, value in request.target.properties:
            setattr(item.properties, key, value)
        item.active = request.active
        if request.declared_properties_only:
            actual = _snapshot(item, False)
            if not _legacy_event_readback(actual[0], request.event) or \
                    actual[2] != request.active or actual[1].idname != request.target.idname:
                raise _Pending('created_readback_mismatch', 'unsupported')
            actual_properties = dict(actual[1].properties)
            if any(actual_properties.get(key, _MISSING) != value for key, value in request.target.properties):
                raise _Pending('created_readback_mismatch', 'unsupported')
            owned.snapshot = actual
        else:
            _validate_created(owned, request.event, request.target, request.active)
        _update_merged()
        if not _valid_owned(owned):
            raise _Pending('created_membership_lost')
        _COUNTS['created'] += 1
        return owned
    except Exception:
        _remove_raw(owned)
        if created_map:
            _remove_empty_map(config, map_)
        raise


def _remove_raw(owned):
    if _valid_owned(owned):
        try:
            owned.map.keymap_items.remove(owned.item)
            _remove_empty_map(owned.config, owned.map)
            try:
                _update_merged()
            except _Pending:
                pass
        except (AttributeError, ReferenceError, RuntimeError, ValueError):
            pass


def _remove_empty_map(config, map_):
    key = (_pointer(config), _pointer(map_))
    recorded = _CREATED_MAPS.get(key)
    if recorded is None or not (_same(recorded[0], config) and _same(recorded[1], map_)):
        return
    try:
        if _contains(config.keymaps, map_) and not _members(map_.keymap_items):
            config.keymaps.remove(map_)
            _CREATED_MAPS.pop(key, None)
    except (AttributeError, ReferenceError, RuntimeError, ValueError, TypeError):
        pass


def _preflight_override(request):
    selector = request.selector
    if not request.replacement_active:
        raise _Pending('inactive_replacement_unsupported', 'unsupported', capability=request.capability)
    if request.replacement_event is not None and request.replacement_event != selector.event:
        raise _Pending('replacement_event_mismatch', 'unsupported', capability=request.capability)
    if request.capability not in ('ordinary_tail', 'modal_head'):
        raise _Pending('unsupported_capability', 'unsupported', capability=request.capability)
    if request.context not in _CONTEXT_PROOFS:
        raise _Pending('unproved_context', 'unsupported', capability=request.capability)
    if request.context == _MODAL_PROOF and request.capability != 'modal_head':
        raise _Pending('unproved_context', 'unsupported', capability=request.capability)
    if request.context == 'synthetic_ordinary_provider' and hasattr(bpy, 'app'):
        raise _Pending('test_capability_unavailable_in_blender', 'unsupported', capability=request.capability)
    if request.context == 'stock_object_mode_select_all':
        if not (selector.scope.name == 'Object Mode'
                and selector.scope.space_type == 'EMPTY'
                and selector.scope.region_type == 'WINDOW'
                and selector.scope.is_modal is False
                and selector.scope.is_tool in (False, None)
                and selector.event == KeymapEvent('A')
                and selector.target == KeymapTarget(
                    idname='object.select_all', properties={'action': 'SELECT'})
                and selector.source_role in ('default', 'active')
                and request.capability == 'ordinary_tail'):
            raise _Pending('unproved_stock_context', 'unsupported', capability=request.capability)
    if request.context == 'machin3tools_object_toggle_smooth':
        provider = KeymapTarget(idname='machin3.toggle_smooth', properties={
            'toggle_subd_overlays': False,
            'toggle_korean_bevel_overlays': True,
            'mode': 'SUBD',
        })
        if not (selector.scope.name == '3D View Generic'
                and selector.scope.space_type == 'VIEW_3D'
                and selector.scope.region_type == 'WINDOW'
                and selector.scope.is_modal is False
                and selector.scope.is_tool in (False, None)
                and selector.event == KeymapEvent('TAB', alt=True)
                and selector.target == provider
                and selector.source_role == 'addon'
                and request.capability == 'ordinary_tail'):
            raise _Pending('unproved_provider_context', 'unsupported', capability=request.capability)
    if selector.scope.is_tool not in (False, None):
        raise _Pending('unproved_tool_scope', 'unsupported', capability=request.capability)
    if request.capability == 'ordinary_tail':
        if selector.scope.is_modal or request.replacement.modal_value or selector.target.modal_value:
            raise _Pending('unsupported_capability', 'unsupported', capability=request.capability)
    else:
        if not selector.scope.is_modal or not request.replacement.modal_value or not selector.target.modal_value:
            raise _Pending('unsupported_capability', 'unsupported', capability=request.capability)
        if selector.source_role not in ('default', 'active'):
            raise _Pending('unsupported_source_role', 'unsupported', selector.source_role)
        modal_event = KeymapEvent('LEFT_SHIFT', value='ANY', any=True,
                                  shift=-1, ctrl=-1, alt=-1, oskey=-1, hyper=-1)
        if not (request.context == _MODAL_PROOF
                and selector.scope.name == 'Transform Modal Map'
                and selector.scope.space_type == 'EMPTY'
                and selector.scope.region_type == 'WINDOW'
                and selector.scope.is_modal is True
                and selector.scope.is_tool in (False, None)
                and selector.event == modal_event
                and selector.target == KeymapTarget(modal_value='PRECISION')
                and request.replacement == KeymapTarget(modal_value='CANCEL')):
            raise _Pending('unproved_modal_context', 'unsupported', capability=request.capability)
    source_config, source_map, source_item = _exact_source(selector)
    if request.capability == 'modal_head':
        observed_tokens = {getattr(item, 'propvalue', None)
                           for item in _members(source_map.keymap_items)}
        if request.replacement.modal_value not in observed_tokens:
            raise _Pending('modal_token_not_observed', 'unsupported', selector.source_role,
                           request.capability)
    source_items = _members(source_map.keymap_items)
    source_index = next(i for i, item in enumerate(source_items) if _same(item, source_item))
    return source_config, source_map, source_item, _snapshot(source_item, selector.scope.is_modal), source_index


def _proof_generation(proof):
    return (_pointer(proof[0]), _pointer(proof[1]), _pointer(proof[2]),
            proof[3], proof[4])


def _merged_order(request, owned, source_item):
    _update_merged()
    if not _valid_owned(owned) or not _contains(owned.source_map.keymap_items, source_item):
        raise _Pending('source_generation_changed')
    merged_config = _config('user')
    merged_map = _one_map(merged_config, request.selector.scope)
    items = _members(merged_map.keymap_items)
    own_snapshot = _snapshot(owned.item, request.selector.scope.is_modal)
    source_snapshot = _snapshot(source_item, request.selector.scope.is_modal)
    owned_positions = []
    source_positions = []
    for i, item in enumerate(items):
        if _event(item) != request.selector.event:
            continue
        try:
            discriminator = (item.propvalue if request.selector.scope.is_modal else item.idname)
        except (AttributeError, ReferenceError, RuntimeError, ValueError) as exc:
            raise _Pending('unreadable_merged_target') from exc
        if discriminator not in (owned.snapshot[1].modal_value or owned.snapshot[1].idname,
                                 source_snapshot[1].modal_value or source_snapshot[1].idname):
            continue
        snapshot = _snapshot(item, request.selector.scope.is_modal)
        if snapshot == own_snapshot:
            owned_positions.append(i)
        if snapshot == source_snapshot:
            source_positions.append(i)
    # Merged items may be distinct native objects. The full emitted fields and
    # unique ordering are the available structural proof there.
    if len(owned_positions) != 1 or len(source_positions) != 1 or owned_positions[0] >= source_positions[0]:
        raise _Pending('merged_priority_unproved', 'unsupported', 'user')


def _create_override(request, proof):
    source_config, source_map, source_item, source_snapshot, source_index = proof
    if _snapshot(source_item, request.selector.scope.is_modal) != source_snapshot or not _contains(source_map.keymap_items, source_item):
        raise _Pending('source_generation_changed')
    if request.capability == 'modal_head':
        before = {_pointer(item) for item in _members(source_map.keymap_items)}
        try:
            item = source_map.keymap_items.new_from_item(source_item, head=True)
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError) as exc:
            candidates = [candidate for candidate in _members(source_map.keymap_items)
                          if _pointer(candidate) not in before]
            if len(candidates) == 1:
                source_map.keymap_items.remove(candidates[0])
            raise _Pending('modal_copy_unavailable', 'unsupported') from exc
        owned = _Owned(source_config, source_map, item, (), source_config, source_map,
                       source_item, source_snapshot, source_index)
        try:
            item.propvalue = request.replacement.modal_value
            _validate_created(owned, request.selector.event, request.replacement)
            _merged_order(request, owned, source_item)
            _COUNTS['created'] += 1
            return owned
        except Exception:
            _remove_raw(owned)
            raise
    addon = _config('addon')
    addon_map = _one_map(addon, request.selector.scope, required=False)
    created_map = False
    if addon_map is None:
        before_maps = {_pointer(candidate) for candidate in _members(addon.keymaps)}
        addon_map = addon.keymaps.new(name=request.selector.scope.name,
                                      space_type=request.selector.scope.space_type,
                                      region_type=request.selector.scope.region_type)
        if _pointer(addon_map) in before_maps:
            raise _Pending('existing_map_scope_conflict', 'unsupported')
        created_map = True
        _CREATED_MAPS[(_pointer(addon), _pointer(addon_map))] = (addon, addon_map)
    if _scope(addon_map) != request.selector.scope:
        if created_map:
            _remove_empty_map(addon, addon_map)
        raise _Pending('created_scope_mismatch', 'unsupported')
    try:
        item = _new_item(addon_map, request.replacement, request.selector.event)
    except Exception:
        if created_map:
            _remove_empty_map(addon, addon_map)
        raise
    owned = _Owned(addon, addon_map, item, (), source_config, source_map,
                   source_item, source_snapshot, source_index)
    try:
        for key, value in request.replacement.properties:
            setattr(item.properties, key, value)
        _validate_created(owned, request.selector.event, request.replacement)
        _merged_order(request, owned, source_item)
        _COUNTS['created'] += 1
        return owned
    except Exception:
        _remove_raw(owned)
        if created_map:
            _remove_empty_map(addon, addon_map)
        raise


class FeatureHandle:
    """One owner and its requests. ``release`` may safely be called repeatedly."""

    def __init__(self, owner_id, assignments, overrides):
        self.owner_id = owner_id
        self.assignments = tuple(assignments)
        self.overrides = tuple(overrides)
        self._owned = {}
        self._cancelled = set()
        self._overtakes = {}
        self._blocked = {}
        self._retry_after = {}
        self._retry_delay = {}
        self._released = False
        self.diagnostics = ()
        self._refreshes = 0

    def refresh(self, budget=None, *, manual=True):
        if self._released:
            return self.diagnostics
        requests = tuple(request for request in (*self.assignments, *self.overrides)
                         if request.request_id not in self._cancelled)
        if budget is not None and budget < len(requests):
            self.diagnostics = (KeymapDiagnostic(self.owner_id, '*', 'pending',
                                                 'feature_exceeds_reconcile_budget'),)
            return self.diagnostics
        diagnostics = []
        staged = []
        preflight_failed = False
        seen_requests = set()
        for request in requests:
            key = request.request_id
            if not manual and time.monotonic() < self._retry_after.get(key, 0):
                diagnostics.append(_diagnostic(self, request, 'pending', 'retry_backoff'))
                preflight_failed = True
                continue
            if any(owned.owner_id == self.owner_id and owned.request_id == key
                   and _valid_owned(owned) for owned in _RETAINED_EDITED.values()):
                diagnostics.append(_diagnostic(self, request, 'unsupported',
                                               'user_edited_owned_item_retained'))
                preflight_failed = True
                continue
            semantic_key = _scope_event(request)
            if semantic_key in seen_requests:
                diagnostics.append(_diagnostic(self, request, 'unsupported',
                                               'conflicting_assignment'))
                preflight_failed = True
                continue
            seen_requests.add(semantic_key)
            prior = self._owned.get(key)
            if prior is not None:
                if not _valid_owned(prior):
                    self._owned.pop(key, None)
                    try:
                        current_config = any(_same(getattr(get_window_manager().keyconfigs, role, None), prior.config)
                                             for role in ('addon', 'default', 'active'))
                        current_map = current_config and _contains(prior.config.keymaps, prior.map)
                    except (AttributeError, ReferenceError, RuntimeError, TypeError):
                        current_map = False
                    if current_map and not _contains(prior.map.keymap_items, prior.item):
                        _remove_empty_map(prior.config, prior.map)
                        self._cancelled.add(key)
                        diagnostics.append(_diagnostic(self, request, 'released', 'user_removed_owned_item'))
                        continue
                    prior = None
                else:
                    try:
                        current_snapshot = _snapshot(prior.item, _scope(prior.map).is_modal)
                    except _Pending:
                        diagnostics.append(_diagnostic(self, request, 'pending',
                                                       'unreadable_owned_item_retained'))
                        preflight_failed = True
                        continue
                    if current_snapshot != prior.snapshot:
                        _retain_edited(prior)
                        self._owned.pop(key, None)
                        self._cancelled.add(key)
                        diagnostics.append(_diagnostic(self, request, 'released',
                                                       'user_edited_owned_item_retained'))
                        continue
                if prior is not None and isinstance(request, KeymapOverride):
                    try:
                        proof = _preflight_override(request)
                        if not (_same(proof[0], prior.source_config) and _same(proof[1], prior.source_map)
                                and _same(proof[2], prior.source_item) and proof[3] == prior.source_snapshot):
                            raise _Pending('source_generation_changed')
                        _merged_order(request, prior, proof[2])
                    except _Pending as issue:
                        if issue.reason == 'merged_priority_unproved':
                            self._blocked[key] = _proof_generation(proof)
                        _remove_owned(prior)
                        self._owned.pop(key, None)
                        diagnostics.append(_diagnostic(self, request, issue.status, issue.reason, issue.role, issue.capability))
                        preflight_failed = True
                        continue
                    later = ()
                    if request.capability == 'ordinary_tail':
                        source_items = _members(prior.map.keymap_items)
                        own_index = next((i for i, item in enumerate(source_items)
                                          if _same(item, prior.item)), -1)
                        later = source_items[own_index + 1:] if own_index >= 0 else ()
                    try:
                        relevant_later = any(_event(item) == request.selector.event
                                             and bool(item.active) for item in later)
                    except _Pending:
                        diagnostics.append(_diagnostic(self, request, 'pending',
                                                       'unreadable_later_provider'))
                        preflight_failed = True
                        continue
                    if relevant_later:
                        if self._overtakes.get(key, 0) >= 2:
                            diagnostics.append(_diagnostic(self, request, 'unsupported',
                                                           'provider_priority_conflict', 'addon'))
                            continue
                        attempts = self._overtakes.get(key, 0) + 1
                        self._overtakes[key] = attempts
                        _remove_owned(prior)
                        self._owned.pop(key, None)
                        try:
                            replacement = _create_override(request, proof)
                            replacement.overtakes = attempts
                            replacement.owner_id = self.owner_id
                            replacement.request_id = key
                            self._owned[key] = replacement
                            self._retry_after.pop(key, None)
                            self._retry_delay.pop(key, None)
                            _COUNTS['reinsertions'] += 1
                            diagnostics.append(_diagnostic(self, request, 'applied',
                                                           'owned_tail_reinserted', 'addon'))
                        except _Pending as issue:
                            self._backoff(key)
                            diagnostics.append(_diagnostic(self, request, issue.status, issue.reason,
                                                           issue.role, issue.capability))
                        continue
                    diagnostics.append(_diagnostic(self, request, 'applied', 'already_registered', request.selector.source_role))
                    continue
                elif prior is not None:
                    diagnostics.append(_diagnostic(self, request, 'applied', 'already_registered', 'addon'))
                    continue
            try:
                scope, event = _scope_event(request)
                if any(other is not self and _valid_owned(owned)
                       and owned.snapshot[2] and _scope(owned.map) == scope
                       and owned.snapshot[0] == event
                       for other in _FEATURES.values() for owned in other._owned.values()):
                    raise _Pending('conflicting_assignment', 'unsupported')
                if isinstance(request, KeymapOverride):
                    proof = _preflight_override(request)
                    blocked = self._blocked.get(key)
                    if blocked == _proof_generation(proof):
                        raise _Pending('merged_priority_unproved', role='user')
                    self._blocked.pop(key, None)
                    staged.append((request, proof))
                else:
                    if request.scope.is_tool is not None and request.scope.is_tool is not False:
                        raise _Pending('unproved_tool_scope', 'unsupported')
                    staged.append((request, None))
            except _Pending as issue:
                diagnostics.append(_diagnostic(self, request, issue.status, issue.reason, issue.role, issue.capability))
                preflight_failed = True
        if preflight_failed:
            diagnostics.extend(_diagnostic(self, request, 'pending', 'feature_preflight_incomplete')
                               for request, _ in staged)
            self._refreshes += 1
            self.diagnostics = tuple(diagnostics)
            return self.diagnostics
        created = []
        for request, proof in staged:
            try:
                owned = _create_override(request, proof) if proof else _create_assignment(request)
                owned.owner_id = self.owner_id
                owned.request_id = request.request_id
                self._owned[request.request_id] = owned
                self._retry_after.pop(request.request_id, None)
                self._retry_delay.pop(request.request_id, None)
                created.append((request, owned))
                diagnostics.append(_diagnostic(self, request, 'applied', 'structural_registration',
                                                request.selector.source_role if proof else 'addon'))
            except _Pending as issue:
                self._backoff(request.request_id)
                if proof is not None and issue.reason == 'merged_priority_unproved':
                    self._blocked[request.request_id] = _proof_generation(proof)
                for _, partial in reversed(created):
                    _remove_raw(partial)
                for prior_request, _ in created:
                    self._owned.pop(prior_request.request_id, None)
                diagnostics.append(_diagnostic(self, request, issue.status, issue.reason, issue.role, issue.capability))
                break
            except Exception:
                self._backoff(request.request_id)
                for _, partial in reversed(created):
                    _remove_raw(partial)
                for prior_request, _ in created:
                    self._owned.pop(prior_request.request_id, None)
                diagnostics.append(_diagnostic(self, request, 'unsupported', 'creation_or_setter_failed'))
                break
        self._refreshes += 1
        self.diagnostics = tuple(diagnostics)
        return self.diagnostics

    def _backoff(self, request_id):
        delay = min(2.0, self._retry_delay.get(request_id, 0.125) * 2)
        self._retry_delay[request_id] = delay
        self._retry_after[request_id] = time.monotonic() + delay

    def release(self):
        if self._released:
            return ()
        self._released = True
        results = []
        for request_id, owned in reversed(tuple(self._owned.items())):
            results.append((request_id, _remove_owned(owned)))
        self._owned.clear()
        if _FEATURES.get(self.owner_id) is self:
            del _FEATURES[self.owner_id]
        return tuple(results)

    @property
    def owned_pairs(self):
        return [(owned.map, owned.item) for owned in self._owned.values() if _valid_owned(owned)]

    @property
    def stats(self):
        return {'owned': len(self._owned), 'refreshes': self._refreshes,
                'pending': sum(d.status == 'pending' for d in self.diagnostics),
                'unsupported': sum(d.status == 'unsupported' for d in self.diagnostics)}


def register_feature(owner_id, assignments=(), overrides=()):
    assignments, overrides = tuple(assignments), tuple(overrides)
    ids = [request.request_id for request in (*assignments, *overrides)]
    if len(ids) > 16:
        raise ValueError('request_budget_exceeded')
    if not owner_id or any(not id_ for id_ in ids) or len(ids) != len(set(ids)):
        raise ValueError('owner and request IDs must be nonempty and unique')
    existing = _FEATURES.get(owner_id)
    if existing is not None:
        if existing.assignments != assignments or existing.overrides != overrides:
            raise ValueError('owner_id already registered with different requests')
        existing.refresh()
        return existing
    handle = FeatureHandle(owner_id, assignments, overrides)
    _FEATURES[owner_id] = handle
    handle.refresh()
    return handle


def reconcile(budget=16, *, max_requests=None, time_budget=0.004):
    """Round-robin whole features within a request and monotonic time budget."""
    global _RECONCILE_CURSOR
    remaining = max(0, budget if max_requests is None else max_requests)
    deadline = time.monotonic() + max(0.0, time_budget)
    result = []
    handles = tuple(_FEATURES.values())
    if not handles:
        return ()
    start = _RECONCILE_CURSOR % len(handles)
    visited = 0
    while visited < len(handles):
        if not remaining or time.monotonic() >= deadline:
            break
        handle = handles[(start + visited) % len(handles)]
        count = len(handle.assignments) + len(handle.overrides)
        if count > remaining:
            result.append(KeymapDiagnostic(handle.owner_id, '*', 'pending',
                                           'feature_exceeds_reconcile_budget'))
            visited += 1
            continue
        result.extend(handle.refresh(manual=False))
        _COUNTS['checked'] += count
        remaining -= count
        visited += 1
    _RECONCILE_CURSOR = (start + visited) % len(handles)
    for category in tuple(_BOUND_CATEGORIES):
        sync_category_pairs(category)
    return tuple(result)


def runtime_stats():
    return {**_COUNTS, 'features': len(_FEATURES),
            'owned': sum(len(handle._owned) for handle in _FEATURES.values()),
            'retained_edited': len(retained_edits())}


def runtime_diagnostics():
    """Immutable diagnostic snapshot for lifecycle and native receipts."""
    return tuple(diagnostic for handle in tuple(_FEATURES.values())
                 for diagnostic in handle.diagnostics)


def release_all():
    results = tuple((owner, handle.release()) for owner, handle in tuple(_FEATURES.items()))
    for config, map_ in tuple(_CREATED_MAPS.values()):
        _remove_empty_map(config, map_)
    _CREATED_MAPS.clear()
    for category in tuple(_BOUND_CATEGORIES):
        sync_category_pairs(category)
    _BOUND_CATEGORIES.clear()
    return results


def release_owned_pairs(pairs):
    """Compatibility release of exact registered pairs; never search by operator."""
    for category, bound in tuple(_BOUND_CATEGORIES.items()):
        if bound is pairs:
            drain_legacy(category)
            pairs.clear()
            return
    removed = []
    for map_, item in reversed(tuple(pairs)):
        for handle in tuple(_FEATURES.values()):
            for request_id, owned in tuple(handle._owned.items()):
                if _valid_owned(owned) and _same(owned.map, map_) and _same(owned.item, item):
                    _remove_owned(owned)
                    handle._owned.pop(request_id, None)
                    handle._cancelled.add(request_id)
                    removed.append((handle.owner_id, request_id))
    pairs.clear()
    return tuple(removed)


def owned_pairs_for_map(map_):
    return [(owned.map, owned.item) for handle in _FEATURES.values()
            for owned in handle._owned.values()
            if _same(owned.map, map_) and _valid_owned(owned)]


def bind_category_pairs(category, pairs):
    """Bind the category's actual mutable list before its register loop."""
    _BOUND_CATEGORIES[category] = pairs
    sync_category_pairs(category)


def sync_category_pairs(category):
    pairs = _BOUND_CATEGORIES.get(category)
    if pairs is None:
        return
    pairs[:] = [pair for owner_id, handle in _FEATURES.items()
                if owner_id.startswith('legacy:' + category + ':')
                for pair in handle.owned_pairs]


def drain_legacy(category):
    results = []
    for owner_id, handle in tuple(_FEATURES.items()):
        if owner_id.startswith('legacy:' + category + ':'):
            results.append((owner_id, handle.release()))
    sync_category_pairs(category)
    return tuple(results)


def capture_scope(map_):
    return _scope(map_)


def capture_event(item):
    return _event(item)


def capture_target(item, *, modal=False):
    return _target(item, modal)


def capture_selector(map_, item, *, source_role='default', ledger_id='', sample_id=''):
    """Read every effective field from a native source row for a strict selector."""
    scope = _scope(map_)
    if not _contains(map_.keymap_items, item):
        raise ValueError('item is not a member of source map')
    return KeymapSelector(scope, _event(item), _target(item, scope.is_modal),
                          source_role, ledger_id, sample_id)


def get_or_create_keymap(kc, keymap_name, space_type, region_type='WINDOW'):
    if kc is None or not _same(kc, get_addon_keyconfig()):
        return None
    try:
        maps = [map_ for map_ in _members(kc.keymaps)
                if (scope := _scope(map_)).name == keymap_name
                and scope.space_type == space_type and scope.region_type == region_type
                and not scope.is_modal]
        if len(maps) > 1:
            return None
        if maps:
            return maps[0]
        before_maps = {_pointer(candidate) for candidate in _members(kc.keymaps)}
        map_ = kc.keymaps.new(name=keymap_name, space_type=space_type,
                              region_type=region_type)
        if _pointer(map_) in before_maps:
            return None
        _CREATED_MAPS[(_pointer(kc), _pointer(map_))] = (kc, map_)
        return map_
    except (_Pending, AttributeError, ReferenceError, RuntimeError, TypeError):
        return None


def find_matching_kmi(km, idname, property_name=None, property_value=None):
    if km is None:
        return None
    for item in km.keymap_items:
        if getattr(item, 'idname', None) == idname and (property_name is None or
                getattr(getattr(item, 'properties', None), property_name, _MISSING) == property_value):
            return item
    return None


def remove_matching_kmis(km, idname, property_name=None, property_value=None):
    """Legacy name retained for callers; matching cannot authorize deletion."""
    return 0
