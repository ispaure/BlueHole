"""Native half of blender_keymap_preset.py; run through its isolated launcher.

Copied preferences are loaded with addon auto-registration suspended, then all
absolute preference paths are redirected before providers are enabled. Captures
and live edits belong only to the temporary preset. Snapshot export is structural
evidence; dispatch assertions are separately identified in the receipt.
"""
import addon_utils, bpy, hashlib, importlib, importlib.util, json, os, re, sys, time, traceback
from pathlib import Path
root = Path(os.environ['BH_AUDIT_ROOT'])
out = Path(os.environ['BH_AUDIT_OUT'])
variant = os.environ['BH_AUDIT_VARIANT']
source = Path(os.environ['BH_SOURCE_PROFILE'])
repo = Path(__file__).resolve().parents[1]
meta = {'variant': variant, 'failures': {}, 'phases': {}}
manifest = json.loads((root / 'manifest.json').read_text())
spec = importlib.util.spec_from_file_location('exporter', repo / 'tests/blender_keymap_baseline.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)

def write():
    (out / (variant + '-status.json')).write_text(json.dumps(meta, indent=2, default=str))

def clear_overrides():
    configs = bpy.context.window_manager.keyconfigs
    configs.update()
    keys = [(km.name, km.space_type, km.region_type) for km in configs.user.keymaps]
    for key in keys:
        km = next((km for km in configs.user.keymaps if (km.name, km.space_type, km.region_type) == key), None)
        if km:
            km.restore_to_default()
            del km
            configs.update()

def operator_info(target, props):
    if not target or '.' not in target:
        return {'kind': 'modal'}
    ns, op = target.split('.', 1)
    try:
        rna = getattr(getattr(bpy.ops, ns), op).get_rna_type()
        cls = bpy.types.Operator.bl_rna_get_subclass_py(rna.identifier)
        mod = getattr(cls, '__module__', None)
        info = {'available': True, 'module': mod, 'label': rna.name}
    except Exception:
        info = {'available': False}
    if target in {'wm.call_menu', 'wm.call_menu_pie', 'wm.call_panel'}:
        name = props.get('name')
        cls = getattr(bpy.types, name, None) if name else None
        info['menu_available'] = bool(cls)
        info['menu_module'] = getattr(cls, '__module__', None)
    return info

def capture(label):
    snap = exporter.capture_snapshot({'variant': variant, 'phase': label})
    exporter.write_snapshot(out / (label + '.json'), snap)
    info = {}
    for role in snap['roles'].values():
        for km in role['maps']:
            for row in km['items']:
                k = json.dumps([row['target'], row['properties'].get('name')])
                if k not in info:
                    info[k] = operator_info(row['target'], row['properties'])
    (out / (label + '-operators.json')).write_text(json.dumps(info, indent=2))
    meta['phases'][label] = {'active': snap['metadata']['active_config'], 'rows': {r: sum((len(k['items']) for k in d['maps'])) for r, d in snap['roles'].items()}}
    write()

def begin():
    global last, stable, started
    try:
        bpy.context.preferences.use_preferences_save = False
        factory_addons = list(bpy.context.preferences.addons.keys())
        for n in factory_addons:
            addon_utils.disable(n, default_set=False)
        saved_enable = addon_utils.enable
        addon_utils.enable = lambda *a, **k: None
        saved_reset = addon_utils.reset_all
        saved_refresh = bpy.utils.refresh_script_paths
        saved_keyconfig = bpy.utils.keyconfig_set
        addon_utils.reset_all = lambda *a, **k: None
        bpy.utils.refresh_script_paths = lambda *a, **k: None
        bpy.utils.keyconfig_set = lambda *a, **k: None
        meta['checkpoint'] = 'reading_preferences'
        write()
        bpy.ops.wm.read_userpref()
        bpy.context.preferences.use_preferences_save = False
        meta['checkpoint'] = 'redirecting_preferences'
        write()
        temporary = []
        for i, addon in enumerate(bpy.context.preferences.addons):
            if addon.preferences is None:
                cls = type('AUDIT_PREFS_' + str(i), (bpy.types.AddonPreferences,), {'bl_idname': addon.module})
                bpy.utils.register_class(cls)
                temporary.append(cls)

        def rooted(s):
            return isinstance(s, str) and (s.startswith(('/', '~')) or re.match('^[A-Za-z]:[\\\\/]', s))

        def redirect(s, field):
            p = Path(s).expanduser()
            if p.is_absolute() and p.is_relative_to(root):
                return s
            if p.is_absolute() and p.is_relative_to(source):
                q = root / p.relative_to(source)
            else:
                q = root / 'redirected' / hashlib.sha256(field.encode()).hexdigest()[:12]
            if not q.exists():
                q.mkdir(parents=True, exist_ok=True)
            return str(q)

        def idprops(v, where):
            if not hasattr(v, 'items'):
                return
            try:
                items = list(v.items())
            except TypeError:
                return
            for k, x in items:
                if rooted(x):
                    v[k] = redirect(x, where + '.' + k)
                elif hasattr(x, 'items'):
                    idprops(x, where + '.' + k)
        seen = set()

        def rna(v, where, depth=0):
            if v is None or not hasattr(v, 'bl_rna') or depth > 10:
                return
            key = (v.bl_rna.identifier, v.as_pointer())
            if key in seen:
                return
            seen.add(key)
            for p in v.bl_rna.properties:
                if p.identifier == 'rna_type':
                    continue
                try:
                    x = getattr(v, p.identifier)
                except Exception:
                    continue
                field = where + '.' + p.identifier
                if p.type == 'STRING' and (not p.is_readonly) and rooted(x):
                    setattr(v, p.identifier, redirect(x, field))
                elif p.type == 'POINTER':
                    rna(x, field, depth + 1)
                elif p.type == 'COLLECTION':
                    for i, y in enumerate(x):
                        rna(y, field + str(i), depth + 1)
            idprops(v, where)
        rna(bpy.context.preferences, 'prefs')
        meta['checkpoint'] = 'extension_repository'
        write()
        addon_utils.reset_all = saved_reset
        bpy.utils.refresh_script_paths = saved_refresh
        bpy.utils.keyconfig_set = saved_keyconfig
        repos = bpy.context.preferences.extensions.repos
        ext = next((x for x in repos if x.module == 'logistics'), None)
        if ext is None:
            bpy.ops.preferences.extension_repo_add(name='Logistics', type='LOCAL', use_custom_directory=True, custom_directory=str(root / 'extensions/logistics'))
            ext = repos[-1]
            ext.module = 'logistics'
        ext.custom_directory = str(root / 'extensions/logistics')
        ext.use_custom_directory = True
        ext.enabled = True
        for entry in manifest['installed'].values():
            mod = entry['module']
            old = mod.rsplit('.', 1)[-1]
            if mod.startswith('bl_ext.') and bpy.context.preferences.addons.get(old) and (not bpy.context.preferences.addons.get(mod)):
                original = bpy.context.preferences.addons[old]
                new = bpy.context.preferences.addons.new()
                new.module = mod
                cls = type('AUDIT_EXTENSION_PREFS_' + str(len(temporary)), (bpy.types.AddonPreferences,), {'bl_idname': mod})
                bpy.utils.register_class(cls)
                temporary.append(cls)
                try:
                    entries = list(original.preferences.items())
                except TypeError:
                    entries = []
                for k, v in entries:
                    new.preferences[k] = v.to_dict() if hasattr(v, 'to_dict') else v
        for cls in reversed(temporary):
            bpy.utils.unregister_class(cls)
        addon_utils.enable = saved_enable
        bpy.utils.refresh_script_paths()
        addon_utils.modules_refresh()
        requested = [x['module'] for x in sorted(manifest['installed'].values(), key=lambda e: (e.get('name', e['module']).casefold(), e['module'].casefold()))]
        requested = list(dict.fromkeys(factory_addons + requested))
        meta['requested'] = requested
        for mod in requested:
            if bpy.app.version >= (5, 3, 0) and mod in {'hair_tool', 'bl_ext.logistics.xray_selection_tools'}:
                meta['failures'][mod] = ['Excluded after isolated Blender 5.3 GPU shader creation crash; see crash receipt']
                continue
            errors = []
            meta['enabling'] = mod
            write()
            try:
                addon_utils.enable(mod, default_set=True, persistent=False, handle_error=lambda *args: errors.append(traceback.format_exc()))
                if not addon_utils.check(mod)[1]:
                    meta['failures'][mod] = errors or ['not enabled']
            except Exception:
                meta['failures'][mod] = traceback.format_exc()
        configs = bpy.context.window_manager.keyconfigs
        if variant == 'legacy':
            bpy.utils.keyconfig_set(str(root / 'scripts/presets/keyconfig/BH_Keymaps.py'))
        else:
            configs.active = configs.default
            bpy.context.preferences.keymap.active_keyconfig = 'Blender'
        write()
    except Exception:
        meta['fatal'] = traceback.format_exc()
        write()
        bpy.app.timers.register(lambda: bpy.ops.wm.quit_blender() and None, first_interval=0.5)
    else:
        started = time.monotonic()
        last = None
        stable = 0

        def finish():
            global last, stable
            try:
                module = sys.modules.get('BlueHole')
                pending = module and bpy.app.timers.is_registered(module._post_register_init)
                sig = hashlib.sha256(json.dumps(exporter.capture_snapshot()['roles'], sort_keys=True).encode()).hexdigest()
                stable = stable + 1 if sig == last else 0
                last = sig
                if (stable < 2 or pending) and time.monotonic() - started < 40:
                    return 1.0
                meta['stable'] = stable >= 2
                meta['loaded'] = [n for n in requested if addon_utils.check(n)[1]]
                meta['providers'] = {name: {'version': getattr(sys.modules.get(name), 'bl_info', {}).get('version'), 'loaded': name in meta['loaded']} for name in requested}
                meta['blender'] = {'version': bpy.app.version_string, 'build': bpy.app.build_hash.decode()}
                registrar = importlib.import_module('BlueHole.keymaps.keymaps_register')
                capture(variant + '-as-loaded')
                if variant == 'legacy':
                    clear_overrides()
                    capture('legacy-preset-no-saved')
                    registrar.unregister()
                    configs.active = configs.default
                    bpy.context.preferences.keymap.active_keyconfig = 'Blender'
                    clear_overrides()
                    capture('legacy-base')
                else:
                    registrar.unregister()
                    clear_overrides()
                    capture('current-base')
                    spec = importlib.util.spec_from_file_location('parity_checks', repo / 'tests/blender_keymap_parity.py')
                    checks = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(checks)
                    baseline = checks.source_state(registrar.keymap_utils)
                    prefs = bpy.context.preferences.addons['BlueHole'].preferences
                    prefs.keymap['deluxe_configured'] = True
                    prefs.keymap['enable_keymaps'] = True
                    registrar.register()
                    configs.update()
                    registrar.default_bindings.reconcile(budget=2000, time_budget=10)
                    capture('current-generated')
                    store = registrar.deluxe_profile()
                    meta['registration_results'] = store.registration_results()
                    meta['runtime'] = registrar.keymap_utils.runtime_stats()
                    (out / 'current-catalog.json').write_text(json.dumps(store.snapshot(), indent=2))
                    rule = 'parity-disable-400848e85e7b'
                    model = importlib.import_module('BlueHole.preferences.addon.keymaps.deluxe_editor_model')

                    def snapshot(label):
                        configs.update()
                        result = []
                        for role in ('addon', 'user'):
                            km = getattr(configs, role).keymaps.get('3D View')
                            for item in km.keymap_items:
                                name = getattr(item.properties, 'name', '')
                                if item.type == 'Q' and name in {'HOPS_MT_MainMenu', 'HOPS_MT_MainPie', 'MACHIN3_MT_mesh_machine'}:
                                    result.append(dict(role=role, name=name, value=item.value, shift=item.shift, ctrl=item.ctrl, alt=item.alt, active=item.active))
                        preview = store.preview()
                        editor = model.Editor(store)
                        record = dict(rows=result, rule=preview['suppressions'][rule], label=editor.rule_status(rule, preview))
                        meta.setdefault('hardops', {})[label] = record
                        write()
                        return record

                    def active(record, name, value, shift):
                        matches = [r for r in record['rows'] if r['role'] == 'user' and r['name'] == name and (r['value'] == value) and (r['shift'] == shift)]
                        assert len(matches) == 1, matches
                        return matches[0]['active']
                    if hasattr(bpy.types, 'HOPS_MT_MainPie') and (not hasattr(bpy.types, 'MACHIN3_MT_mesh_machine')):
                        before = snapshot('missing_meshmachine')
                        assert before['rule']['registered'], before
                        assert not active(before, 'HOPS_MT_MainMenu', 'PRESS', False)
                        assert not active(before, 'HOPS_MT_MainPie', 'PRESS', True)
                        assert active(before, 'HOPS_MT_MainPie', 'CLICK_DRAG', False)
                        assert before['label'] == 'Exact target resolved'
                        draft = store.begin()
                        draft.update('suppressions', rule, enabled=False)
                        store.apply(draft)
                        disabled = snapshot('rule_disabled')
                        assert active(disabled, 'HOPS_MT_MainPie', 'PRESS', True)
                        assert disabled['label'] == 'Rule inactive'
                        draft = store.begin()
                        draft.update('suppressions', rule, enabled=True)
                        store.apply(draft)

                        class MACHIN3_MT_mesh_machine(bpy.types.Menu):
                            bl_label = 'Temporary MESHmachine provider probe'

                            def draw(self, context):
                                self.layout.label(text='Probe')
                        bpy.utils.register_class(MACHIN3_MT_mesh_machine)
                        registrar.refresh()
                        configs.update()
                        registrar.default_bindings.reconcile(budget=2000, time_budget=10)
                        ready = snapshot('replacement_registered')
                        assert ready['rule']['registered'], ready
                        assert not active(ready, 'HOPS_MT_MainPie', 'PRESS', True)
                        assert active(ready, 'MACHIN3_MT_mesh_machine', 'PRESS', True)
                        bpy.utils.unregister_class(MACHIN3_MT_mesh_machine)
                        registrar.refresh()
                        configs.update()
                        registrar.default_bindings.reconcile(budget=2000, time_budget=10)
                        restored = snapshot('replacement_removed')
                        assert not active(restored, 'HOPS_MT_MainPie', 'PRESS', True)
                        assert restored['rule']['registered']
                    import cProfile, pstats
                    ui = importlib.import_module('BlueHole.preferences.addon.keymaps.deluxe_editor')
                    ops = importlib.import_module('BlueHole.preferences.addon.keymaps.deluxe_editor_ops')
                    editor = model.Editor(store)
                    editor.show_all_bindings()
                    editor.preview()
                    found, contexts = ui.binding_list_data(editor, editor.preview(), '', False)
                    view = ops.state(bpy.context)
                    editor.binding_context_expansion.update({c.id: True for c in contexts})

                    def draw_list():
                        preview = editor.preview()
                        key = (id(preview), '', False, editor.binding_all, editor.binding_category_all, editor.category, editor.section)
                        cached = editor.display_cache.get('bindings')
                        if cached is None or cached[0] != key:
                            cached = (key, ui.binding_list_data(editor, preview, '', False))
                            editor.display_cache['bindings'] = cached
                        found, contexts = cached[1]
                        ops.sync_binding_rows(view, repr((key, getattr(editor, 'binding_state_revision', 0))), lambda: ui.binding_rows(editor, preview, contexts, found, searching=True), editor.assignment)
                    draw_list()
                    bpy.context.preferences.view.show_splash = False
                    prefs.main_settings = 'GENERAL_ADDON'
                    prefs.general_addon_settings = 'KEYMAP'
                    ops._editor = editor
                    area = max(bpy.context.window.screen.areas, key=lambda a: a.width * a.height)
                    area.type = 'PREFERENCES'
                    with bpy.context.temp_override(area=area):
                        bpy.ops.preferences.addon_show(module='BlueHole')
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)
                    meta['timings'] = {}
                    candidates = []
                    for table in ('suppressions', 'assignments'):
                        binding = os.environ.get('BH_AUDIT_' + table[:-1].upper())
                        if not binding:
                            binding = next(id_ for id_, status in editor.preview()[table].items()
                                if status['registered'] and not editor.catalog[table][id_].get('required')
                                and not editor.catalog['sections'][editor.catalog[table][id_]['section']].get('required'))
                        assert editor.preview()[table][binding]['registered'], binding
                        candidates.append((table, binding))
                    meta['benchmark_bindings'] = dict(candidates)
                    for table, binding in candidates:
                        values = []
                        for n in range(int(os.environ.get('BH_AUDIT_SAMPLES', '20'))):
                            enabled = n % 2 == 1
                            began = time.perf_counter()
                            editor.set_enabled(table, binding, enabled)
                            changed = time.perf_counter()
                            draw_list()
                            refreshed = time.perf_counter()
                            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                            values.append(dict(enabled=enabled, toggle_ms=(changed - began) * 1000, list_ms=(refreshed - began) * 1000, paint_ms=(time.perf_counter() - began) * 1000))
                            assert not editor.preview_error, editor.preview_error
                        meta['timings'][table] = values
                    profiler = cProfile.Profile()
                    profiler.enable()
                    editor.set_enabled('assignments', candidates[1][1], False)
                    draw_list()
                    profiler.disable()
                    with (out / 'toggle-profile.txt').open('w') as stream:
                        pstats.Stats(profiler, stream=stream).sort_stats('cumulative').print_stats(40)
                    editor.discard()
                    ops._editor = None
                    meta['verification'] = checks.verify(registrar, baseline)
                    registrar.unregister()
                    configs.update()
                    meta['hardops_verified'] = bool(meta.get('hardops'))
                meta['status'] = 'complete'
                write()
            except Exception:
                meta['fatal'] = traceback.format_exc()
                write()
            bpy.ops.wm.quit_blender()
        bpy.app.timers.register(finish, first_interval=4)
begin()
