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
from contextlib import contextmanager
from collections.abc import Mapping
import math
import sys
import time

import bpy
from .provider_policy import PROVIDERS, module_matches

from .descriptors import (EVENT_FIELDS, SCOPE_FIELDS, KeymapScope, KeymapEvent, KeymapTarget,
                          KeymapAssignment, KeymapSelector, KeymapOverride, KeymapDiagnostic, freeze as _freeze)

_CONTEXT_PROOFS = frozenset(('stock_object_mode_select_all',
                             'synthetic_ordinary_provider',
                             'machin3tools_object_toggle_smooth',
                             'transform_translate_precision_cancel'))
_MODAL_PROOF = 'transform_translate_precision_cancel'
_MISSING = object()



def _freeze_rna_array(prop, value):
    """Read a fixed numeric RNA array with its complete declared shape.

    Only Blender's observed array/vector/matrix classes are accepted here. This
    does not make arbitrary iterable objects valid descriptor/property values.
    """
    try:
        from mathutils import Matrix, Vector
        import mathutils
    except ImportError as exc:
        raise ValueError('unreadable_property_schema') from exc
    array_type = getattr(getattr(bpy, 'types', None), 'bpy_prop_array', None)
    scalar_type = {'BOOLEAN': bool, 'INT': int, 'FLOAT': float}.get(prop.type)
    raw_dimensions = tuple(prop.array_dimensions)
    if scalar_type is None or len(raw_dimensions) != 3:
        raise ValueError('unreadable_property_schema')
    dimensions = []
    ended = False
    for dimension in raw_dimensions:
        if type(dimension) is not int or dimension < 0 or (ended and dimension):
            raise ValueError('unreadable_property_schema')
        if dimension == 0:
            ended = True
        else:
            dimensions.append(dimension)
    if (not dimensions or type(prop.array_length) is not int
            or math.prod(dimensions) != prop.array_length):
        raise ValueError('unreadable_property_schema')

    def read(part, depth):
        if depth == len(dimensions):
            if type(part) is not scalar_type:
                raise ValueError('unreadable_property_schema')
            return _freeze(part)  # Reject nonfinite floats; canonicalize negative zero.
        remaining = len(dimensions) - depth
        kind = type(part)
        if not ((isinstance(array_type, type) and kind is array_type)
                or (scalar_type is float and remaining == 1 and kind in
                    tuple(getattr(mathutils, name, None) for name in ('Vector', 'Color', 'Euler', 'Quaternion')))
                or (scalar_type is float and kind is Matrix and remaining == 2)):
            raise ValueError('unreadable_property_schema')
        if len(part) != dimensions[depth]:
            raise ValueError('unreadable_property_schema')
        return tuple(read(part[index], depth + 1) for index in range(dimensions[depth]))

    return read(value, 0)


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


def _remove_native_item(map_, item):
    """Single native removal leaf; fault probes may replace it temporarily."""
    map_.keymap_items.remove(item)



def _selector_key(selector):
    return (selector.scope, selector.event, selector.target, selector.source_role)


def _scope_event(request):
    if isinstance(request, KeymapOverride):
        return request.selector.scope, request.selector.event
    return request.scope, request.event


def _assignment_dependency_ready(request):
    if request.required_class and not hasattr(getattr(bpy, 'types', None), request.required_class):
        return False
    if request.required_addon and not _addon_enabled(request.required_addon):
        return False
    return not request.requires_operator or _operator_available(request.target.idname)


def _operator_available(idname):
    try:
        namespace, name = idname.split('.')
        getattr(getattr(bpy.ops, namespace), name).get_rna_type()
    except (AttributeError, KeyError, ReferenceError, RuntimeError, TypeError, ValueError):
        return False
    return True


def _addon_enabled(name):
    # Logistics may install the same provider as a legacy add-on or as an
    # extension in any repository namespace.
    return any(module_matches(module_name, (name,))
               and getattr(module, '__addon_enabled__', False)
               for module_name, module in tuple(sys.modules.items()))



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
    item_id: int | None = field(default=None, init=False)
    config_pointer: tuple | None = field(default=None, init=False)
    map_pointer: tuple | None = field(default=None, init=False)
    item_pointer: tuple | None = field(default=None, init=False)

    def __post_init__(self):
        self.config_pointer = _pointer(self.config)
        self.map_pointer = _pointer(self.map)
        self.item_pointer = _pointer(self.item)
        try:
            self.item_id = self.item.id
        except (AttributeError, ReferenceError, RuntimeError):
            self.item_id = None


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
_PAIR_ALIASES = {}
_PENDING_CLEANUP = {}
_UNREADABLE_CLEANUP_REASONS = frozenset(('owned_snapshot_unavailable', 'owned_operator_unavailable'))
_CLEANUP_RETRY_REASONS = _UNREADABLE_CLEANUP_REASONS | {'owned_remove_failed'}
_PROVIDER_REF_IDS = {}
_RECONCILE_CURSOR = 0
_MERGED_BATCH_DEPTH = 0
_MERGED_DIRTY = False
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
        return [map_ for map_ in _members(config.keymaps)
                if map_.name == scope.name and _scope(map_) == scope]
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
    """Flush immediately, including inside a batch, before merged-map proofs."""
    global _MERGED_DIRTY
    wm = get_window_manager()
    update = getattr(getattr(wm, 'keyconfigs', None), 'update', None)
    if callable(update):
        try:
            # Keep backing properties through Blender's operator-type rebind.
            # They are needed to distinguish artist edits when a provider returns.
            update(keep_properties=True)
        except (AttributeError, ReferenceError, RuntimeError, TypeError) as exc:
            raise _Pending('merged_update_failed') from exc
    _MERGED_DIRTY = False


def _request_merged_update():
    global _MERGED_DIRTY
    _MERGED_DIRTY = True
    if not _MERGED_BATCH_DEPTH:
        _update_merged()


@contextmanager
def batch_merged_updates():
    """Coalesce source mutations on the main thread; flush before returning.

    Source membership, readback, and removal checks still run for every item.
    Callers that inspect merged keymaps must use _update_merged first. Nested
    batches and failed operations flush at the outer boundary, including any
    rollback removals. This is a merge boundary, not a source transaction.
    """
    global _MERGED_BATCH_DEPTH
    _MERGED_BATCH_DEPTH += 1
    try:
        yield
    finally:
        _MERGED_BATCH_DEPTH -= 1
        if not _MERGED_BATCH_DEPTH and _MERGED_DIRTY:
            _update_merged()


def _event(item):
    try:
        values = tuple(getattr(item, field, None) for field in EVENT_FIELDS)
        if values[0] in ('', None) or values[1] in ('', None) or any(value == '' for value in values):
            raise _Pending('unreadable_event')
        return KeymapEvent(*values)
    except (AttributeError, ReferenceError, RuntimeError, ValueError, TypeError) as exc:
        raise _Pending('unreadable_event') from exc


def _properties(item):
    # A provider can unregister its operator before Blue Hole releases a KMI.
    # Blender may leave that item's property RNA pointing at the freed type;
    # even asking for properties.bl_rna can then segfault (not raise Python).
    # Resolve the live operator first, without touching the property pointer.
    if hasattr(getattr(bpy, 'app', None), 'version') and not _operator_available(item.idname):
        raise _Pending('waiting_for_provider')
    props = getattr(item, 'properties', None)
    if props is None:
        raise _Pending('unreadable_property_schema')
    schema = getattr(getattr(props, 'bl_rna', None), 'properties', None)
    if schema is None:
        # Mapping is useful for a deterministic fake; real Blender must provide RNA.
        if isinstance(props, Mapping):
            return _freeze(props)
        raise _Pending('unreadable_property_schema')
    return _read_property_group(props)


def _operator_property_group(prop, value):
    base = getattr(prop, 'fixed_type', None)
    while base is not None and base.identifier != 'OperatorProperties':
        base = base.base
    operator_properties = getattr(getattr(bpy, 'types', None), 'OperatorProperties', None)
    return base is not None and operator_properties is not None and isinstance(value, operator_properties)


def _read_property_group(props, depth=0):
    if depth > 4:
        raise _Pending('unreadable_property_schema')
    values = {}
    try:
        for prop in props.bl_rna.properties:
            name = prop.identifier
            if name == 'rna_type':
                continue
            value = getattr(props, name)
            if prop.type == 'POINTER':
                if not _operator_property_group(prop, value):
                    raise _Pending('unreadable_property_schema')
                values[name] = _read_property_group(value, depth + 1)
            elif prop.type == 'COLLECTION':
                # Gesture paths, paint strokes and batch-rename actions are
                # value collections. Include even empty collections so later
                # user edits remain visible to the ownership comparison.
                if len(value) > 4096:
                    raise _Pending('unreadable_property_schema')
                values[name] = tuple(_read_property_group(entry, depth + 1) for entry in value)
            elif prop.type == 'ENUM' and value == '':
                raise _Pending('unreadable_property_schema')
            elif getattr(prop, 'is_array', False):
                values[name] = _freeze_rna_array(prop, value)
            elif prop.type == 'ENUM' and getattr(prop, 'is_enum_flag', False) is True:
                allowed = _enum_flag_identifiers(prop)
                if type(value) is not set or any(type(v) is not str or v not in allowed for v in value):
                    raise ValueError('unreadable_property_schema')
                values[name] = tuple(sorted(value))
            else:
                values[name] = _freeze(value)
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError) as exc:
        raise _Pending('unreadable_property_schema') from exc
    return _freeze(values)


def _declared_properties_match(actual, expected):
    def named_pairs(entries):
        return isinstance(entries, tuple) and bool(entries) and all(
            isinstance(pair, tuple) and len(pair) == 2 and isinstance(pair[0], str) for pair in entries)

    actual = dict(actual)
    for name, value in expected:
        observed = actual.get(name, _MISSING)
        # Nested tuples of named pairs are macro operator property groups.
        group = named_pairs(value) or value == () and named_pairs(observed)
        if group:
            if not isinstance(observed, tuple) or not _declared_properties_match(observed, value):
                return False
        elif observed != value:
            return False
    return True


def _enum_flag_identifiers(prop):
    if prop.type != 'ENUM' or getattr(prop, 'is_enum_flag', False) is not True:
        raise ValueError('unreadable_property_schema')
    identifiers = tuple(item.identifier for item in prop.enum_items)
    if not identifiers or any(type(identifier) is not str for identifier in identifiers):
        raise ValueError('unreadable_property_schema')
    # Empty enum identifiers are UI separators, never selectable flags.
    allowed = frozenset(identifier for identifier in identifiers if identifier)
    if not allowed:
        raise ValueError('unreadable_property_schema')
    return allowed


def _set_property(item, name, value):
    """Convert reviewed canonical flags/matrix rows to native RNA setter input."""
    _set_property_group(item.properties, name, value)


def _set_property_group(properties, name, value):
    schema = getattr(getattr(properties, 'bl_rna', None), 'properties', ())
    prop = next((prop for prop in schema if prop.identifier == name), None)
    if prop is not None and prop.type == 'POINTER':
        child = getattr(properties, name)
        if not _operator_property_group(prop, child):
            raise ValueError('unreadable_property_schema')
        for key, entry in value:
            _set_property_group(child, key, entry)
        return
    if prop is not None and prop.type == 'ENUM' and getattr(prop, 'is_enum_flag', False) is True:
        allowed = _enum_flag_identifiers(prop)
        if (type(value) is not tuple
                or any(type(flag) is not str or flag not in allowed for flag in value)
                or value != tuple(sorted(set(value)))):
            raise ValueError('unreadable_property_schema')
        value = set(value)
    elif prop is not None and prop.type == 'FLOAT' and getattr(prop, 'is_array', False):
        from mathutils import Matrix
        if type(getattr(properties, name)) is Matrix:
            # Native RNA tuple input is column-major for this property, whereas
            # Matrix readback and our canonical signature preserve logical rows.
            # The observed typed Matrix setter preserves that same row ordering.
            if (type(value) is not tuple or not value
                    or any(type(row) is not tuple or not row
                           or any(type(part) is not float for part in row) for row in value)):
                raise ValueError('unreadable_property_schema')
            matrix = Matrix(value)
            if _freeze_rna_array(prop, matrix) != value:
                raise ValueError('unreadable_property_schema')
            value = matrix
    setattr(properties, name, value)


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


def _preflight_merged_source(selector):
    merged = _one_map(_config('user'), selector.scope)
    candidates = []
    for item in _members(merged.keymap_items):
        if _event(item) != selector.event:
            continue
        try:
            discriminator = item.propvalue if selector.scope.is_modal else item.idname
        except (AttributeError, ReferenceError, RuntimeError, ValueError) as exc:
            raise _Pending('unreadable_merged_target', role='user') from exc
        wanted = selector.target.modal_value if selector.scope.is_modal else selector.target.idname
        if discriminator != wanted:
            continue
        snapshot = _snapshot(item, selector.scope.is_modal)
        if snapshot[:2] == (selector.event, selector.target):
            candidates.append(snapshot)
    if len(candidates) > 1:
        raise _Pending('ambiguous_merged_source', 'unsupported', 'user')
    if not candidates:
        raise _Pending('merged_source_missing_or_edited', role='user')
    if not candidates[0][2]:
        raise _Pending('merged_source_inactive', role='user')


def _diagnostic(handle, request, status, reason, role='', capability=''):
    if not capability and status in ('pending', 'unsupported'):
        capability = getattr(request, 'capability', '')
    return KeymapDiagnostic(handle.owner_id, request.request_id, status, reason,
                            getattr(request, 'ledger_id', '') or getattr(getattr(request, 'selector', None), 'ledger_id', ''),
                            getattr(request, 'sample_id', '') or getattr(getattr(request, 'selector', None), 'sample_id', ''),
                            role, getattr(request, 'context', ''), capability)


def _live_owned_members(owned):
    if any(token is None for token in (owned.config_pointer, owned.map_pointer,
                                       owned.item_pointer)):
        return None
    try:
        configs = get_window_manager().keyconfigs
        config = next((candidate for role in ('addon', 'default', 'active')
                       if (candidate := getattr(configs, role, None)) is not None
                       and _pointer(candidate) == owned.config_pointer), None)
        if config is None:
            return None
        map_ = next((candidate for candidate in _members(config.keymaps)
                     if _pointer(candidate) == owned.map_pointer), None)
        if map_ is None:
            return None
        if owned.item_pointer is None:
            return None
        for item in _members(map_.keymap_items):
            if _pointer(item) != owned.item_pointer:
                continue
            live_id = getattr(item, 'id', None)
            if owned.item_id is None:
                if hasattr(bpy, 'app'):
                    return None
            elif live_id != owned.item_id:
                return None
            return map_, item
        return None
    except (AttributeError, ReferenceError, RuntimeError, TypeError):
        return None


def _valid_owned(owned):
    return _live_owned_members(owned) is not None


def _remove_owned(owned):
    live = _live_owned_members(owned)
    if live is None:
        return 'stale_owned_reference'
    map_, item = live
    try:
        if _snapshot(item, _scope(map_).is_modal) != owned.snapshot:
            _retain_edited(owned)
            return 'user_edited_owned_item_retained'
    except _Pending as issue:
        reason = 'owned_snapshot_unavailable'
        if (issue.reason == 'waiting_for_provider' and owned.snapshot
                and item.idname == owned.snapshot[1].idname):
            reason = 'owned_operator_unavailable'
        _queue_cleanup(owned, reason)
        return reason
    try:
        _remove_native_item(map_, item)
        _COUNTS['removed'] += 1
        _remove_empty_map(owned.config, map_)
        try:
            _request_merged_update()
        except _Pending:
            return 'released_merged_update_failed'
        return 'released'
    except (AttributeError, ReferenceError, RuntimeError, ValueError):
        if _valid_owned(owned):
            _queue_cleanup(owned)
            return 'owned_remove_failed'
        return 'released'


def _cleanup_key(owned):
    return owned.owner_id, owned.request_id


def _queue_cleanup(owned, reason='owned_remove_failed'):
    key = _cleanup_key(owned)
    records = _PENDING_CLEANUP.setdefault(key, [])
    if not any(record[0] is owned for record in records):
        records.append((owned, reason))


def _cleanup_one(owned):
    if not _valid_owned(owned):
        return 'stale_owned_reference'
    if not owned.snapshot:
        _retain_edited(owned)
        return 'unreadable_owned_item_retained'
    return _remove_owned(owned)


def _retry_cleanup_key(key):
    records = _PENDING_CLEANUP.get(key, ())
    remaining = []
    for owned, reason in records:
        if _dormant_cleanup(owned, reason):
            remaining.append((owned, reason))
            continue
        if reason == 'owned_operator_unavailable' and _valid_owned(owned):
            try:
                # Operator registration can queue Blender's property-RNA
                # rebind. Flush it before touching a previously freed pointer.
                _update_merged()
            except _Pending:
                remaining.append((owned, reason))
                continue
        outcome = _cleanup_one(owned)
        if outcome in _CLEANUP_RETRY_REASONS:
            remaining.append((owned, outcome))
        else:
            handle = _FEATURES.get(key[0])
            if handle is not None and handle._owned.get(key[1]) is owned:
                handle._owned.pop(key[1], None)
    _PENDING_CLEANUP.pop(key, None)
    if remaining:
        _PENDING_CLEANUP[key] = remaining


def _dormant_cleanup(owned, reason):
    if reason != 'owned_operator_unavailable':
        return False
    live = _live_owned_members(owned)
    return (live is not None and live[1].idname == owned.snapshot[1].idname
            and not _operator_available(live[1].idname))


def _ready_cleanup_keys():
    return tuple(key for key, records in _PENDING_CLEANUP.items()
                 if any(not _dormant_cleanup(owned, reason) for owned, reason in records))


def _retry_cleanup(limit=None, *, keys=None):
    diagnostics = []
    if keys is None:
        keys = _ready_cleanup_keys()
    for key in keys[:limit]:
        _retry_cleanup_key(key)
        pending = _PENDING_CLEANUP.get(key)
        diagnostics.append(KeymapDiagnostic(key[0], key[1],
                                            'pending' if pending else 'released',
                                            pending[0][1] if pending else 'cleanup_complete'))
    return tuple(diagnostics)


def retry_unreadable_cleanup(budget):
    """Retry released bindings during preference reload without registering anything."""
    keys = tuple(key for key in _ready_cleanup_keys() if any(
        reason in _UNREADABLE_CLEANUP_REASONS for _, reason in _PENDING_CLEANUP[key]))
    _retry_cleanup(limit=budget, keys=keys)
    return unreadable_cleanup_pending()


def pending_cleanup():
    return tuple({'owner_id': owner_id, 'request_id': request_id, 'reason': reason}
                 for (owner_id, request_id), records in _PENDING_CLEANUP.items()
                 for _, reason in records)


def blocking_cleanup():
    """An unloaded operator can't dispatch. Its row still requires exact cleanup."""
    return bool(_ready_cleanup_keys())


def unreadable_cleanup_pending():
    return any(reason in _UNREADABLE_CLEANUP_REASONS
               for records in _PENDING_CLEANUP.values() for _, reason in records)


def drain_cleanup(budget=16):
    """Retry released ownership without refreshing or creating any bindings."""
    _retry_cleanup(limit=budget)
    return not _PENDING_CLEANUP


def _remember_pair(handle, request_id, owned):
    key = id(owned.map), id(owned.item)
    _PAIR_ALIASES[key] = (owned.map, owned.item, handle, request_id)


def _forget_handle_pairs(handle):
    for key, alias in tuple(_PAIR_ALIASES.items()):
        if alias[2] is handle:
            _PAIR_ALIASES.pop(key, None)


def _retain_edited(owned):
    owned.detached = True
    _RETAINED_EDITED[(owned.config_pointer, owned.map_pointer, owned.item_pointer,
                      owned.item_id)] = owned
    _CREATED_MAPS.pop((owned.config_pointer, owned.map_pointer), None)


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


def _new_item(config, map_, target, event, owner_id, request_id):
    kwargs = dict(type=event.type, value=event.value, any=event.any,
                  shift=event.shift, ctrl=event.ctrl, alt=event.alt,
                  oskey=event.oskey, key_modifier=event.key_modifier,
                  direction=event.direction, repeat=event.repeat, head=False)
    # Blender versions differ on repeat/head keyword support; a rejected schema
    # fails closed rather than emitting an item with silently changed fields.
    before = {_pointer(item) for item in _members(map_.keymap_items)}
    try:
        item = map_.keymap_items.new(target.idname, **kwargs)
        # Hyper is exposed on newer keymap items but is not accepted by every
        # version's creation API. Set it on the owned item, then verify readback.
        if event.hyper not in (None, False):
            if not hasattr(item, 'hyper'):
                raise AttributeError('Hyper modifier is unavailable')
            item.hyper = event.hyper
    except (TypeError, AttributeError, ValueError, RuntimeError) as exc:
        candidates = [item for item in _members(map_.keymap_items)
                      if _pointer(item) not in before]
        if len(candidates) == 1:
            partial = _Owned(config, map_, candidates[0], (), owner_id=owner_id,
                             request_id=request_id)
            _remove_raw(partial)
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


def _create_assignment(request, owner_id):
    if request.scope.is_modal:
        return _create_modal_assignment(request, owner_id)
    if request.target.modal_value:
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
        item = _new_item(config, map_, request.target, request.event,
                         owner_id, request.request_id)
    except Exception:
        if created_map:
            _remove_empty_map(config, map_)
        raise
    owned = _Owned(config, map_, item, (), owner_id=owner_id,
                   request_id=request.request_id)
    try:
        for key, value in request.target.properties:
            _set_property(item, key, value)
        item.active = request.active
        if request.declared_properties_only:
            actual = _snapshot(item, False)
            if not _legacy_event_readback(actual[0], request.event) or \
                    actual[2] != request.active or actual[1].idname != request.target.idname:
                raise _Pending('created_readback_mismatch', 'unsupported')
            if not _declared_properties_match(actual[1].properties, request.target.properties):
                raise _Pending('created_readback_mismatch', 'unsupported')
            owned.snapshot = actual
        else:
            _validate_created(owned, request.event, request.target, request.active)
        _request_merged_update()
        if not _valid_owned(owned):
            raise _Pending('created_membership_lost')
        _COUNTS['created'] += 1
        return owned
    except Exception:
        _remove_raw(owned)
        if created_map:
            _remove_empty_map(config, map_)
        raise


def _create_modal_assignment(request, owner_id):
    """Add a reversible modal alias to the actual built-in handler map.

    Blender does not merge add-on modal maps into its modal handlers. Register
    only in an existing default modal map, never in the saved user keyconfig.
    """
    if not request.target.modal_value:
        raise _Pending('unsupported_assignment_kind', 'unsupported')
    config = _config('default')
    map_ = _one_map(config, request.scope)
    event = request.event
    kwargs = {name: getattr(event, name) for name in EVENT_FIELDS
              if name not in {'map_type', 'hyper'}}
    before = {_pointer(item) for item in _members(map_.keymap_items)}

    def remove_partial():
        for candidate in _members(map_.keymap_items):
            if _pointer(candidate) not in before:
                _remove_raw(_Owned(config, map_, candidate, (), owner_id=owner_id,
                                   request_id=request.request_id))

    try:
        item = map_.keymap_items.new_modal(request.target.modal_value, **kwargs)
    except (TypeError, ValueError, RuntimeError) as exc:
        remove_partial()
        raise _Pending('unsupported_modal_token_or_event', 'unsupported') from exc
    owned = _Owned(config, map_, item, (), owner_id=owner_id, request_id=request.request_id)
    try:
        # new_modal has no head argument. Copy the freshly created item to the
        # front so a built-in ANY event cannot swallow a more specific alias.
        # Both objects are ours, so removing the temporary tail is safe.
        front = map_.keymap_items.new_from_item(item, head=True)
        owned = _Owned(config, map_, front, (), owner_id=owner_id, request_id=request.request_id)
        _remove_native_item(map_, item)
        item = front
        if event.hyper not in (None, False):
            item.hyper = event.hyper
        item.active = request.active
        _validate_created(owned, event, request.target, request.active)
        _request_merged_update()
        _COUNTS['created'] += 1
        return owned
    except Exception:
        remove_partial()
        raise


def _remove_raw(owned):
    live = _live_owned_members(owned)
    if live is None:
        return 'stale_owned_reference'
    map_, item = live
    try:
        _remove_native_item(map_, item)
        _remove_empty_map(owned.config, map_)
        try:
            _request_merged_update()
        except _Pending:
            return 'released_merged_update_failed'
        return 'released'
    except (AttributeError, ReferenceError, RuntimeError, ValueError):
        if not _valid_owned(owned):
            return 'released'
        if not owned.snapshot:
            try:
                owned.snapshot = _snapshot(item, _scope(map_).is_modal)
            except _Pending:
                owned.snapshot = ()
        _queue_cleanup(owned)
        return 'owned_remove_failed'


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


def _conflicting_owned_event(owner_id, scope, event, dispatch_group=''):
    for other in _FEATURES.values():
        if other.owner_id == owner_id:
            continue
        for owned in other._owned.values():
            # Only a matching captured event can conflict. Native membership
            # checks scan Blender collections, so avoid them for unrelated rows.
            if not owned.snapshot or not owned.snapshot[2] or owned.snapshot[0] != event:
                continue
            live = _live_owned_members(owned)
            if live is not None and _scope(live[0]) == scope:
                # Reviewed poll chains (and Blender's paired modal actions)
                # deliberately share an event. Unrelated assignments still fail.
                if dispatch_group and any(request.request_id == owned.request_id
                                          and request.dispatch_group == dispatch_group
                                          for request in other.assignments):
                    continue
                return True
    for records in _PENDING_CLEANUP.values():
        for owned, _ in records:
            if owned.snapshot and (not owned.snapshot[2] or owned.snapshot[0] != event):
                continue
            live = _live_owned_members(owned)
            if live is None or _scope(live[0]) != scope:
                continue
            if not owned.snapshot or (owned.snapshot[2] and owned.snapshot[0] == event):
                return True
    return False


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
        if not _same(_config('active'), _config('default')):
            raise _Pending('unproved_active_modal_config', 'unsupported', selector.source_role)
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
    _exact_source(selector)
    _update_merged()
    _preflight_merged_source(selector)
    source_config, source_map, source_item = _exact_source(selector)
    if request.context == 'machin3tools_object_toggle_smooth':
        _verify_machin3_provider(source_map, source_item)
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


def _verify_machin3_provider(source_map, source_item):
    policy = PROVIDERS['MACHIN3tools']
    matches = [(name, module) for name, module in tuple(sys.modules.items())
               if module_matches(name, policy.modules) and getattr(module, '__addon_enabled__', False) is True]
    if len(matches) != 1:
        _PROVIDER_REF_IDS.clear()
        raise _Pending('provider_unavailable', role='addon')
    module_name, module = matches[0]
    if any(record[0] is not module for record in _PROVIDER_REF_IDS.values()):
        _PROVIDER_REF_IDS.clear()
    info = getattr(module, 'bl_info', None)
    version = info.get('version', ()) if isinstance(info, dict) else ()
    if not isinstance(version, (tuple, list)) or tuple(version[:3]) not in policy.replacement_versions:
        raise _Pending('unproved_provider_version', 'unsupported', 'addon')
    addons = getattr(getattr(bpy.context, 'preferences', None), 'addons', None)
    if addons is None:
        _PROVIDER_REF_IDS.clear()
        raise _Pending('provider_unavailable', role='addon')
    try:
        entry = addons.get(module_name) if hasattr(addons, 'get') else next(
            (entry for entry in addons if getattr(entry, 'module', None) == module_name), None)
        if entry is None or getattr(entry, 'module', None) != module_name or \
                getattr(getattr(entry, 'preferences', None), 'activate_smooth', None) is not True:
            _PROVIDER_REF_IDS.clear()
            raise _Pending('provider_unavailable', role='addon')
    except (AttributeError, ReferenceError, RuntimeError, TypeError) as exc:
        raise _Pending('provider_unavailable', role='addon') from exc
    try:
        bpy.ops.machin3.toggle_smooth.get_rna_type()
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError) as exc:
        raise _Pending('provider_operator_unavailable', role='addon') from exc
    source_id = getattr(source_item, 'id', None)
    if source_id is None:
        raise _Pending('provider_reference_unreadable', 'unsupported', 'addon')
    try:
        pairs = tuple(module.keymaps)
        for key, record in tuple(_PROVIDER_REF_IDS.items()):
            if not any(map_ is record[1] and item is record[2] for map_, item in pairs):
                _PROVIDER_REF_IDS.pop(key, None)
        trusted = False
        for map_, item in pairs:
            if not (_same(map_, source_map) and _same(item, source_item)):
                continue
            key = (id(module), id(map_), id(item))
            record = _PROVIDER_REF_IDS.get(key)
            item_id = getattr(item, 'id', None)
            if record is not None and (record[0] is not module or record[1] is not map_
                                       or record[2] is not item or record[3] != item_id):
                raise _Pending('provider_reference_generation_changed', 'unsupported', 'addon')
            if item_id != source_id:
                continue
            _PROVIDER_REF_IDS[key] = (module, map_, item, item_id)
            trusted = True
            break
        if not trusted:
            raise _Pending('provider_reference_missing', role='addon')
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError) as exc:
        raise _Pending('provider_reference_unreadable', 'unsupported', 'addon') from exc


def _merged_order(request, owned, source_item):
    _update_merged()
    own_live = _live_owned_members(owned)
    if own_live is None or not _contains(owned.source_map.keymap_items, source_item):
        raise _Pending('source_generation_changed')
    merged_config = _config('user')
    merged_map = _one_map(merged_config, request.selector.scope)
    items = _members(merged_map.keymap_items)
    own_snapshot = _snapshot(own_live[1], request.selector.scope.is_modal)
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


def _create_override(request, proof, owner_id):
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
                partial = _Owned(source_config, source_map, candidates[0], (),
                                 owner_id=owner_id, request_id=request.request_id)
                _remove_raw(partial)
            raise _Pending('modal_copy_unavailable', 'unsupported') from exc
        owned = _Owned(source_config, source_map, item, (), source_config, source_map,
                       source_item, source_snapshot, source_index,
                       owner_id=owner_id, request_id=request.request_id)
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
        item = _new_item(addon, addon_map, request.replacement, request.selector.event,
                         owner_id, request.request_id)
    except Exception:
        if created_map:
            _remove_empty_map(addon, addon_map)
        raise
    owned = _Owned(addon, addon_map, item, (), source_config, source_map,
                   source_item, source_snapshot, source_index,
                   owner_id=owner_id, request_id=request.request_id)
    try:
        for key, value in request.replacement.properties:
            _set_property(item, key, value)
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
            cleanup_key = self.owner_id, key
            if cleanup_key in _PENDING_CLEANUP:
                _retry_cleanup_key(cleanup_key)
                if cleanup_key in _PENDING_CLEANUP:
                    diagnostics.append(_diagnostic(self, request, 'pending',
                                                   _PENDING_CLEANUP[cleanup_key][0][1]))
                else:
                    diagnostics.append(_diagnostic(self, request, 'released',
                                                   'cleanup_complete'))
                preflight_failed = True
                continue
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
            if isinstance(request, KeymapAssignment) and not _assignment_dependency_ready(request):
                if prior is not None:
                    removal = _remove_owned(prior)
                    if removal not in _CLEANUP_RETRY_REASONS:
                        self._owned.pop(key, None)
                diagnostics.append(_diagnostic(self, request, 'pending', 'waiting_for_provider'))
                preflight_failed = True
                continue
            if prior is not None:
                if not _valid_owned(prior):
                    self._owned.pop(key, None)
                    try:
                        configs = get_window_manager().keyconfigs
                        current_config = next((config for role in ('addon', 'default', 'active')
                                               if (config := getattr(configs, role, None)) is not None
                                               and _pointer(config) == prior.config_pointer), None)
                        current_map = (next((map_ for map_ in _members(current_config.keymaps)
                                             if _pointer(map_) == prior.map_pointer), None)
                                       if current_config is not None else None)
                    except (AttributeError, ReferenceError, RuntimeError, TypeError):
                        current_map = None
                    if current_map is not None:
                        _remove_empty_map(current_config, current_map)
                        self._cancelled.add(key)
                        diagnostics.append(_diagnostic(self, request, 'released', 'user_removed_owned_item'))
                        continue
                    prior = None
                else:
                    try:
                        live = _live_owned_members(prior)
                        if live is None:
                            raise _Pending('stale_owned_reference')
                        live_map, live_item = live
                        current_snapshot = _snapshot(live_item, _scope(live_map).is_modal)
                    except _Pending:
                        diagnostics.append(_diagnostic(self, request, 'pending',
                                                       'owned_snapshot_unavailable'))
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
                        removal = _remove_owned(prior)
                        if removal not in _CLEANUP_RETRY_REASONS:
                            self._owned.pop(key, None)
                        else:
                            diagnostics.append(_diagnostic(self, request, 'pending',
                                                           removal))
                            preflight_failed = True
                            continue
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
                        removal = _remove_owned(prior)
                        if removal in _CLEANUP_RETRY_REASONS:
                            diagnostics.append(_diagnostic(self, request, 'pending',
                                                           removal))
                            preflight_failed = True
                            continue
                        self._owned.pop(key, None)
                        try:
                            replacement = _create_override(request, proof, self.owner_id)
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
                if _conflicting_owned_event(self.owner_id, scope, event,
                                            getattr(request, 'dispatch_group', '')):
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
                owned = (_create_override(request, proof, self.owner_id) if proof
                         else _create_assignment(request, self.owner_id))
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
                diagnostics.append(_diagnostic(self, request, issue.status, issue.reason, issue.role, issue.capability))
                self._rollback_creation(created, staged, request, diagnostics)
                break
            except Exception:
                self._backoff(request.request_id)
                diagnostics.append(_diagnostic(self, request, 'unsupported', 'creation_or_setter_failed'))
                self._rollback_creation(created, staged, request, diagnostics)
                break
        self._refreshes += 1
        self.diagnostics = tuple(diagnostics)
        return self.diagnostics

    def _rollback_creation(self, created, staged, failed, diagnostics):
        """Report final transaction state, including unattempted and queued work."""
        outcomes = {}
        for request, owned in reversed(created):
            outcomes[request.request_id] = _remove_raw(owned)
            self._owned.pop(request.request_id, None)
        diagnostics[:] = [row for row in diagnostics if row.request_id not in outcomes]
        for request, _ in staged:
            if request.request_id in outcomes:
                outcome = outcomes[request.request_id]
                reason = outcome if outcome in _CLEANUP_RETRY_REASONS else 'feature_creation_rolled_back'
                diagnostics.append(_diagnostic(self, request, 'pending', reason))
            elif request.request_id != failed.request_id:
                diagnostics.append(_diagnostic(self, request, 'pending', 'feature_creation_not_attempted'))

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
        _forget_handle_pairs(self)
        if _FEATURES.get(self.owner_id) is self:
            del _FEATURES[self.owner_id]
        return tuple(results)

    @property
    def owned_pairs(self):
        pairs = []
        for request_id, owned in self._owned.items():
            if _valid_owned(owned):
                _remember_pair(self, request_id, owned)
                pairs.append((owned.map, owned.item))
        return pairs

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
    cleanup = _ready_cleanup_keys()
    cleanup_count = min(remaining, len(cleanup))
    result = list(_retry_cleanup(limit=cleanup_count, keys=cleanup))
    remaining -= cleanup_count
    handles = tuple(_FEATURES.values())
    if not handles:
        return tuple(result)
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
    owned = sum(len(handle._owned) for handle in _FEATURES.values())
    retained = len(retained_edits())
    pending = sum(len(records) for records in _PENDING_CLEANUP.values())
    tracked = {id(item) for handle in _FEATURES.values() for item in handle._owned.values()}
    tracked.update(id(item) for records in _PENDING_CLEANUP.values() for item, _ in records)
    tracked.update(id(item) for item in _RETAINED_EDITED.values())
    return {**_COUNTS, 'features': len(_FEATURES), 'owned': owned,
            'retained_edited': retained, 'pending_cleanup': pending,
            'tracked_resources': len(tracked)}


def runtime_diagnostics():
    """Immutable diagnostic snapshot for lifecycle and native receipts."""
    return (tuple(diagnostic for handle in tuple(_FEATURES.values())
                  for diagnostic in handle.diagnostics) +
            tuple(KeymapDiagnostic(owner_id, request_id, 'pending', records[0][1])
                  for (owner_id, request_id), records in _PENDING_CLEANUP.items()))


def release_all():
    results = tuple((owner, handle.release()) for owner, handle in tuple(_FEATURES.items()))
    _retry_cleanup(limit=16)
    for config, map_ in tuple(_CREATED_MAPS.values()):
        _remove_empty_map(config, map_)
    pending_maps = {(_pointer(owned.config), _pointer(owned.map))
                    for records in _PENDING_CLEANUP.values() for owned, _ in records}
    for key in tuple(_CREATED_MAPS):
        if key not in pending_maps:
            _CREATED_MAPS.pop(key, None)
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
        alias = _PAIR_ALIASES.get((id(map_), id(item)))
        if alias is None or alias[0] is not map_ or alias[1] is not item:
            continue
        handle, request_id = alias[2], alias[3]
        if _FEATURES.get(handle.owner_id) is not handle:
            continue
        handle._cancelled.add(request_id)
        owned = handle._owned.get(request_id)
        if owned is not None:
            outcome = _remove_owned(owned)
            if outcome not in _CLEANUP_RETRY_REASONS:
                handle._owned.pop(request_id, None)
            removed.append((handle.owner_id, request_id, outcome))
        else:
            removed.append((handle.owner_id, request_id, 'cancelled_pending'))
    pairs.clear()
    return tuple(removed)


def owned_pairs_for_map(map_):
    return [pair for handle in _FEATURES.values() for pair in handle.owned_pairs
            if _same(pair[0], map_)]


def owned_request_for_merged_item(map_, item):
    """Identify one unchanged merged row for navigation to its owning feature.

    A merged item's ID is not an add-on ownership token. Require a unique
    snapshot plus the original live source before returning a request ID.
    """
    try:
        if (not _contains(_config('user').keymaps, map_)
                or not _contains(map_.keymap_items, item)
                or item.is_user_modified or item.is_user_defined):
            return None
        scope = _scope(map_)
        snapshot = _snapshot(item, scope.is_modal)
        candidates = [candidate for candidate in map_.keymap_items
                      if _event(candidate) == snapshot[0]
                      and _snapshot(candidate, scope.is_modal) == snapshot]
        if len(candidates) != 1:
            return None
        matches = [(handle.owner_id, request_id)
                   for handle in _FEATURES.values() for request_id, owned in handle._owned.items()
                   if owned.snapshot == snapshot and _scope(owned.map) == scope
                   and _valid_owned(owned) and _snapshot(owned.item, scope.is_modal) == snapshot]
        return matches[0] if len(matches) == 1 else None
    except (_Pending, AttributeError, ReferenceError, RuntimeError, ValueError):
        return None


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


def resolve_scope(stated, config):
    """Resolve a catalog scope's observable tool state without changing maps."""
    if config is None or stated.is_tool is not None:
        return stated
    try:
        candidates = [capture_scope(map_) for map_ in config.keymaps
                      if map_.name == stated.name
                      and map_.space_type == stated.space_type
                      and map_.region_type == stated.region_type
                      and not map_.is_modal]
    except (AttributeError, ReferenceError, RuntimeError, TypeError):
        return stated
    return candidates[0] if len(candidates) == 1 else stated


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


# Public Blender adapter boundary. Internal ownership records never leave this module.
Pending = _Pending


def configuration(role):
    return _config(role)


def native_identity(value):
    return _pointer(value)


def same_identity(left, right):
    return _same(left, right)


def contains_native(collection, value):
    return _contains(collection, value)


def matching_maps(config, scope):
    return _maps(config, scope)


def matching_map(config, scope, *, required=True):
    return _one_map(config, scope, required=required)


def exact_source(selector):
    return _exact_source(selector)


def verify_merged_source(selector):
    return _preflight_merged_source(selector)


def snapshot_item(item, modal):
    return _snapshot(item, modal)


def flush_merged():
    return _update_merged()


def request_merged_update():
    return _request_merged_update()


def provider_enabled(name):
    return _addon_enabled(name)


def verify_override(request):
    return _preflight_override(request)


def declared_properties_match(actual, expected):
    return _declared_properties_match(actual, expected)


def release_features(owners):
    """Release selected owners in reverse registration order."""
    selected = set(owners)
    return tuple((owner, handle.release()) for owner, handle in reversed(tuple(_FEATURES.items()))
                 if owner in selected)


def owned_item_tokens(config):
    """Immutable native identities used to exclude our own modal aliases."""
    pointer = _pointer(config)
    return frozenset((owned.map_pointer, owned.item_pointer, owned.item_id)
                     for handle in _FEATURES.values() for owned in handle._owned.values()
                     if owned.config_pointer == pointer)
