"""Reversible disables of exact, unmodified Blender default bindings.

The source lives only in memory. No user keymap delta is created, and restoration
requires the same native item and complete unchanged disabled snapshot.
"""

from dataclasses import dataclass

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


def _valid(record):
    return (runtime._same(runtime._config('default'), record.config)
            and runtime._contains(record.config.keymaps, record.map)
            and runtime._contains(record.map.keymap_items, record.item)
            and record.item.id == record.item_id
            and runtime.capture_scope(record.map) == record.selector.scope)


def _snapshot(record, active):
    return record.selector.event, record.selector.target, active


def _merged_item(selector, item_id, active):
    merged = runtime._one_map(runtime._config('user'), selector.scope)
    matches = [item for item in merged.keymap_items if item.id == item_id]
    if len(matches) != 1:
        raise runtime._Pending('merged_source_missing_or_edited')
    item = matches[0]
    if (item.is_user_modified or item.is_user_defined
            or runtime._snapshot(item, False) != (selector.event, selector.target, active)):
        raise runtime._Pending('user_binding_modified', 'unsupported')
    return item


def _preflight(selector):
    if (selector.source_role != 'default' or selector.scope.is_modal or selector.scope.is_tool
            or not runtime._same(runtime._config('active'), runtime._config('default'))):
        raise runtime._Pending('only_ordinary_blender_defaults', 'unsupported')
    config, map_, item = runtime._exact_source(selector)
    runtime._preflight_merged_source(selector)
    _merged_item(selector, item.id, True)
    return DisabledBinding(selector, config, map_, item, item.id)


def managed_rule(map_, item):
    """Identify a managed default from the native merged Keymap preferences."""
    for id_, record in _bindings.items():
        if (not record.pending and _valid(record) and item.id == record.item_id
                and runtime.capture_scope(map_) == record.selector.scope
                and runtime._snapshot(item, False) == _snapshot(record, False)):
            return id_, record.selector
    return None


def status(selector):
    try:
        for record in _bindings.values():
            if record.selector == selector and not record.pending and _valid(record):
                if runtime._snapshot(record.item, False) == _snapshot(record, False):
                    _merged_item(selector, record.item_id, False)
                    return 'resolved', ''
        _preflight(selector)
        return 'resolved', ''
    except runtime._Pending as error:
        state = ('ambiguous' if error.reason.startswith('ambiguous') else
                 'unsupported' if error.status == 'unsupported' else 'missing')
        return state, error.reason


def install(id_, selector):
    runtime._update_merged()
    try:
        record = _preflight(selector)
    except runtime._Pending as error:
        _results[id_] = (error.status, error.reason)
        return
    _bindings[id_] = record
    try:
        record.item.active = False
        runtime._update_merged()
        if not _valid(record) or runtime._snapshot(record.item, False) != _snapshot(record, False):
            raise RuntimeError('Default binding changed while disabling it')
        _merged_item(selector, record.item_id, False)
    except Exception:
        record.pending = True
        retry_cleanup()
        raise
    _results[id_] = ('applied', '')


def retry_cleanup():
    changed = False
    for id_, record in tuple(_bindings.items()):
        if not record.pending:
            continue
        try:
            if _valid(record) and runtime._snapshot(record.item, False) == _snapshot(record, False):
                record.item.active = True
                changed = True
                if runtime._snapshot(record.item, False) != _snapshot(record, True):
                    continue
            # Gone or edited entries no longer authorize mutation.
            del _bindings[id_]
        except (runtime._Pending, AttributeError, ReferenceError, RuntimeError, TypeError):
            continue
    if changed:
        runtime._request_merged_update()
    return pending_cleanup()


def release_all():
    _results.clear()
    for record in _bindings.values():
        record.pending = True
    return retry_cleanup()


def pending_cleanup():
    return tuple(id_ for id_, record in _bindings.items() if record.pending)


def registration_results():
    results = dict(_results)
    for id_, record in _bindings.items():
        try:
            intact = not record.pending and _valid(record) and runtime._snapshot(record.item, False) == _snapshot(record, False)
            if intact:
                _merged_item(record.selector, record.item_id, False)
        except (runtime._Pending, AttributeError, ReferenceError, RuntimeError, TypeError):
            intact = False
        if not intact:
            results[id_] = ('pending', 'default_binding_changed_or_unreadable')
    return results
