"""Native parity assertions for an isolated, plugin-enabled Blender session.

The caller loads its copied providers, clears saved overrides, and captures
source_state() before enabling Deluxe. Nothing here saves preferences.
"""
from collections import Counter
import importlib


def source_state(runtime):
    result = {}
    for role in ('default', 'addon'):
        maps = []
        for km in runtime._config(role).keymaps:
            items = []
            for item in km.keymap_items:
                try:
                    snapshot = runtime._snapshot(item, km.is_modal)
                except runtime._Pending:
                    snapshot = (runtime.capture_event(item), item.idname, item.active, 'unreadable')
                items.append((item.id, snapshot))
            maps.append((runtime.capture_scope(km), items))
        result[role] = maps
    return result


def verify(registrar, baseline):
    runtime = registrar.keymap_utils
    store = registrar.deluxe_profile()
    catalog = store.snapshot()
    preview = store.preview()
    applied, pending = [], []
    for id_, state in preview['assignments'].items():
        if not state['eligible']:
            continue
        if state['availability'] == 'available':
            assert state['registered'], (id_, preview['runtime'].get(id_))
            applied.append(id_)
        else:
            assert not state['registered'], (id_, 'unavailable command registered')
            pending.append(id_)

    configs = runtime.get_window_manager().keyconfigs
    modal = configs.user.keymaps['Knife Tool Modal Map']
    left = [x for x in modal.keymap_items if x.active and x.type == 'LEFTMOUSE']
    pan = next(i for i,x in enumerate(left) if x.propvalue == 'PANNING' and x.alt == 1)
    cut = next(i for i,x in enumerate(left) if x.propvalue == 'ADD_CUT' and x.any)
    assert pan < cut, 'Wildcard cut shadows Alt+LMB pan'
    transform = configs.user.keymaps['Transform Modal Map']
    w = [x.propvalue for x in transform.keymap_items if x.active and x.type == 'W']
    assert w == ['TRANSLATE', 'VERT_EDGE_SLIDE'], w

    package = registrar.__package__.split('.')[0]
    editor_module = importlib.import_module(package + '.preferences.addon.keymaps.deluxe_editor_model')
    editor_ui = importlib.import_module(package + '.preferences.addon.keymaps.deluxe_editor')
    editor = editor_module.Editor(store)
    for id_ in pending:
        assert editor.binding_pending(id_, preview)
        assert editor.binding_origin(id_, preview)[0] == 'ADD'
    pending_rules = [id_ for id_, state in preview['suppressions'].items()
                     if state['eligible'] and not state['registered']]
    for id_ in pending_rules:
        assert editor.binding_pending(id_, preview), id_
        assert editor.binding_origin(id_, preview)[0] == 'REMOVE'
    assert editor_ui.pending_icon('ADD') > 0
    assert editor_ui.pending_icon('REMOVE') > 0
    editor_ui.release_pending_icons()

    # UI rows remain enumerable even when a provider has no native keymap.
    editor.binding_all = True
    editor.binding_context_expansion.clear()
    found, contexts = editor_ui.binding_list_data(editor, preview, '', False)
    listed = {row['target'] for row in editor_ui.binding_rows(
        editor, preview, contexts, found, searching=True) if row['kind'] == 'binding'}
    assert set(pending) <= listed, ('Missing pending additions', set(pending) - listed)
    assert set(pending_rules) <= listed, ('Missing pending removals', set(pending_rules) - listed)

    summary = {'available_registered': len(applied), 'unavailable_yellow_additions': len(pending),
               'pending_yellow_removals': len(pending_rules), 'modal_priority': 'passed',
               'registration_statuses': dict(Counter(value[0] for value in preview['runtime'].values()))}
    registrar.unregister()
    configs.update()
    released = source_state(runtime)
    assert released == baseline, 'Disable did not restore inherited sources exactly'
    assert runtime.runtime_stats()['tracked_resources'] == 0, runtime.runtime_stats()
    assert not registrar.default_bindings.pending_cleanup()
    registrar.register()
    configs.update()
    assert store.registration_results() == preview['runtime'], 'Re-enable changed registrations'
    summary.update(source_restoration='passed', reenable='passed', status='passed')
    return summary
