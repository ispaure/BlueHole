"""Reversible disables of exact, unmodified Blender and add-on bindings.

The source lives only in memory. No user keymap delta is created, and restoration
requires the same native item and complete unchanged disabled snapshot.
"""

from dataclasses import dataclass, replace
from time import monotonic

from . import keymap_utils as runtime


@dataclass
class DisabledBinding:
    selector: object
    config: object
    map: object
    item: object
    item_id: int
    pending: bool = False


_bindings = {}
_results = {}
_requests = {}
_cursor = 0


def _valid(record):
    return (runtime._same(runtime._config(record.selector.source_role), record.config)
            and runtime._contains(record.config.keymaps, record.map)
            and runtime._contains(record.map.keymap_items, record.item)
            and record.item.id == record.item_id
            and runtime.capture_scope(record.map) == record.selector.scope)


def _snapshot(record, active):
    return record.selector.event, record.selector.target, active


def _merged_item(selector, item_id, active):
    merged = runtime._one_map(runtime._config('user'), selector.scope)
    # Blender assigns new IDs to add-on rows when merging them. Match the
    # complete unique snapshot there; source identity still controls restoration.
    matches = [item for item in merged.keymap_items
               if (item.id == item_id if selector.source_role == 'default' else
                   item.idname == selector.target.idname and runtime.capture_event(item) == selector.event
                   and runtime._snapshot(item, selector.scope.is_modal) == (selector.event, selector.target, active))]
    if len(matches) != 1:
        raise runtime._Pending('merged_source_missing_or_edited')
    item = matches[0]
    if (item.is_user_modified or item.is_user_defined
            or runtime._snapshot(item, selector.scope.is_modal) != (selector.event, selector.target, active)):
        raise runtime._Pending('user_binding_modified', 'unsupported')
    return item


def _preflight(selector):
    if (selector.source_role not in {'default', 'addon'} or selector.scope.is_tool
            or not runtime._same(runtime._config('active'), runtime._config('default'))):
        raise runtime._Pending('only_inherited_blender_bindings', 'unsupported')
    config, map_, item = runtime._exact_source(selector)
    runtime._preflight_merged_source(selector)
    _merged_item(selector, item.id, True)
    return DisabledBinding(selector, config, map_, item, item.id)


def managed_rule(map_, item):
    """Identify a managed default from the native merged Keymap preferences."""
    for id_, record in _bindings.items():
        if (not record.pending and _valid(record)
                and (record.selector.source_role == 'addon' or item.id == record.item_id)
                and runtime.capture_scope(map_) == record.selector.scope
                and runtime._snapshot(item, record.selector.scope.is_modal) == _snapshot(record, False)):
            return id_, record.selector
    return None


def _resolve(selector, explicit_properties):
    """Old preset exports contain only explicitly set properties, not RNA defaults.

    Imported default and add-on rules use this mode. Resolve one complete native
    snapshot before mutation and keep that exact snapshot for restoration.
    """
    if not explicit_properties:
        return selector
    if selector.source_role not in {'default', 'addon'} or selector.scope.is_modal:
        raise runtime._Pending('invalid_explicit_property_selector', 'unsupported')
    map_ = runtime._one_map(runtime._config(selector.source_role), selector.scope)
    matches = []
    for item in map_.keymap_items:
        if item.idname != selector.target.idname or runtime.capture_event(item) != selector.event:
            continue
        target = runtime.capture_target(item, modal=False)
        if runtime._declared_properties_match(target.properties, selector.target.properties):
            matches.append(target)
    if len(matches) != 1:
        raise runtime._Pending('ambiguous_source' if matches else 'source_missing_or_edited')
    return replace(selector, target=matches[0])


def status(selector, *, explicit_properties=False):
    try:
        for id_, record in _bindings.items():
            if (_requests.get(id_) == (selector, explicit_properties)
                    and not record.pending and _valid(record)):
                if runtime._snapshot(record.item, record.selector.scope.is_modal) == _snapshot(record, False):
                    _merged_item(record.selector, record.item_id, False)
                    return 'resolved', ''
        _preflight(_resolve(selector, explicit_properties))
        return 'resolved', ''
    except runtime._Pending as error:
        state = ('ambiguous' if error.reason.startswith('ambiguous') else
                 'unsupported' if error.status == 'unsupported' else 'missing')
        return state, error.reason


def install(id_, selector, *, explicit_properties=False):
    _requests[id_] = selector, explicit_properties
    try:
        selector = _resolve(selector, explicit_properties)
        # An absent provider should not force a native keyconfig rebuild on
        # every watcher tick. Flush only after finding an actual source.
        runtime._exact_source(selector)
        runtime._update_merged()
        record = _preflight(selector)
    except runtime._Pending as error:
        _results[id_] = (error.status, error.reason)
        return
    _bindings[id_] = record
    try:
        record.item.active = False
        runtime._update_merged()
        if not _valid(record) or runtime._snapshot(record.item, record.selector.scope.is_modal) != _snapshot(record, False):
            raise RuntimeError('Default binding changed while disabling it')
        _merged_item(selector, record.item_id, False)
    except Exception:
        record.pending = True
        retry_cleanup()
        raise
    _results[id_] = ('applied', '')


def reconcile(*, budget=4, time_budget=0.004):
    """Follow provider enable/reload in bounded steps, preserving native edits."""
    global _cursor
    ids = tuple(_requests)
    if not ids:
        return 0
    started = monotonic()
    checked = 0
    while checked < min(budget, len(ids)) and monotonic() - started < time_budget:
        id_ = ids[_cursor % len(ids)]
        _cursor += 1
        checked += 1
        record = _bindings.get(id_)
        if record is not None:
            try:
                if _valid(record):
                    # An in-place edit belongs to the artist. Never keep
                    # disabling it; a recreated provider item is a new source.
                    if runtime._snapshot(record.item, record.selector.scope.is_modal) != _snapshot(record, False):
                        _results[id_] = ('pending', 'source_binding_edited')
                    continue
            except (runtime._Pending, AttributeError, ReferenceError, RuntimeError, TypeError):
                continue
            del _bindings[id_]
        selector, explicit_properties = _requests[id_]
        install(id_, selector, explicit_properties=explicit_properties)
    return checked


def retry_cleanup():
    changed = False
    for id_, record in tuple(_bindings.items()):
        if not record.pending:
            continue
        try:
            if _valid(record) and runtime._snapshot(record.item, record.selector.scope.is_modal) == _snapshot(record, False):
                record.item.active = True
                changed = True
                if runtime._snapshot(record.item, record.selector.scope.is_modal) != _snapshot(record, True):
                    continue
            # Gone or edited entries no longer authorize mutation.
            del _bindings[id_]
        except (runtime._Pending, AttributeError, ReferenceError, RuntimeError, TypeError):
            continue
    if changed:
        runtime._request_merged_update()
    return pending_cleanup()


def release_all():
    global _cursor
    _requests.clear()
    _cursor = 0
    _results.clear()
    for record in _bindings.values():
        record.pending = True
    return retry_cleanup()


def release(id_):
    """Restore one rule without disturbing other managed bindings."""
    _requests.pop(id_, None)
    _results.pop(id_, None)
    if record := _bindings.get(id_):
        record.pending = True
    return retry_cleanup()


def pending_cleanup():
    return tuple(id_ for id_, record in _bindings.items() if record.pending)


def registration_results(ids=None):
    results = {k:v for k,v in _results.items() if ids is None or k in ids}
    for id_, record in _bindings.items():
        if ids is not None and id_ not in ids:
            continue
        try:
            intact = not record.pending and _valid(record) and runtime._snapshot(record.item, record.selector.scope.is_modal) == _snapshot(record, False)
            if intact:
                _merged_item(record.selector, record.item_id, False)
        except (runtime._Pending, AttributeError, ReferenceError, RuntimeError, TypeError):
            intact = False
        if not intact:
            results[id_] = ('pending', 'default_binding_changed_or_unreadable')
    return results
