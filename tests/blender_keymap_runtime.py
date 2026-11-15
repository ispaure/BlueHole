"""Isolated GUI checks for the integrated Deluxe keymap runtime.

The launcher requires macOS sandbox-exec, an explicit Blender binary and an
installed MACHIN3tools source directory. It copies resources, denies
network access and writes outside the disposable fixture, and never loads the
caller's preferences. Run --help outside Blender for the reproducible command.
"""
import argparse
import ast
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback

REPO = Path(os.environ.get('DELUXE_RUNTIME_REPO', Path(__file__).resolve().parents[1])).resolve()
PROVIDER = 'MACHIN3tools'
RESOURCE_NAMES = ('RESOURCES', 'CONFIG', 'SCRIPTS', 'EXTENSIONS', 'DATAFILES')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def stage_package(root, minimum, package_archive=None):
    package = root / 'scripts/addons/bluehole_runtime'
    if package_archive is not None:
        if minimum is not None:
            raise ValueError('Exact package tests cannot override compatibility')
        from blender_addon_smoke import extract_package
        extract_package(package_archive, package)
        return
    names = subprocess.check_output(['git', '-C', str(REPO), 'ls-files', '--cached', '--others', '--exclude-standard', '-z']).decode().split('\0')
    for name in filter(None, names):
        if name.startswith(('tests/', '.github/', 'overlays/deluxe/payload/', 'docs/')):
            continue
        source = REPO / name
        if source.is_symlink() or not source.is_file():
            continue
        target = package / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    if minimum:
        initializer = package / '__init__.py'
        text = initializer.read_text()
        tree = ast.parse(text)
        info = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == 'bl_info' for t in n.targets))
        entry = next(v for k, v in zip(info.keys, info.values) if ast.literal_eval(k) == 'blender')
        lines = text.splitlines(keepends=True)
        line = lines[entry.lineno - 1]
        lines[entry.lineno - 1] = line[:entry.col_offset] + repr(minimum) + line[entry.end_col_offset:]
        initializer.write_text(''.join(lines))


def launch_case(binary, provider_source, output, mode, *, incoming=None, minimum=None, timeout=55):
    """Return one process receipt; only the child created here can be terminated."""
    root = output / (mode + '-' + str(time.time_ns()))
    root.mkdir(parents=True)
    environment = dict(os.environ)
    environment.pop('PYTHONPATH', None)
    environment.update(PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1', PYTHONUNBUFFERED='1',
                       DELUXE_CAPTURE_ROOT=str(root), DELUXE_RUNTIME_MODE=mode, DELUXE_RUNTIME_REPO=str(REPO))
    for name in RESOURCE_NAMES:
        folder = root / name.lower()
        folder.mkdir()
        environment['BLENDER_USER_' + name] = str(folder)
    for name, folder in (('TMPDIR', 'tmp'), ('XDG_CACHE_HOME', 'cache')):
        (root / folder).mkdir()
        environment[name] = str(root / folder)
    destination = root / 'scripts/addons' / PROVIDER
    if provider_source is not None:
        if any(p.is_symlink() for p in provider_source.rglob('*')):
            raise ValueError('Provider fixture must not contain symlinks')
        shutil.copytree(provider_source, destination, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    stage_package(root, minimum)
    if incoming:
        shutil.copytree(incoming, root / 'incoming')
    executed_script = root / 'executed-native-test.py'
    shutil.copyfile(Path(__file__).resolve(), executed_script)
    policy = root / 'confinement.sb'
    policy.write_text('(version 1)\n(allow default)\n(deny network*)\n(deny file-write*)\n'
                      '(allow file-write* (subpath ' + json.dumps(str(root)) + '))\n'
                      '(allow file-write* (literal "/dev/null"))\n')
    command = ['/usr/bin/sandbox-exec', '-f', str(policy), str(binary), '--factory-startup',
               '--disable-autoexec', '--offline-mode', '--enable-event-simulate',
               '--python-exit-code', '1', '--python', str(executed_script),
               '--', '-ApplePersistenceIgnoreState', 'YES']
    started = time.monotonic()
    with (root / 'private-launch.log').open('w') as stream:
        child = subprocess.Popen(command, env=environment, stdout=stream, stderr=subprocess.STDOUT)
        try:
            code = child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            child.terminate()
            try:
                child.wait(timeout=3)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
            code = 'timeout'
    result = {'mode': mode, 'returncode': code, 'child_exited': child.poll() is not None,
              'seconds': round(time.monotonic() - started, 4)}
    path = root / 'runtime.json'
    result['runtime'] = json.loads(path.read_text()) if path.exists() else {'status': 'missing'}
    (root / 'process.json').write_text(json.dumps(result, indent=2) + '\n')
    return root, result


def cleanup_resources(root):
    removed = []
    for name in (*[name.lower() for name in RESOURCE_NAMES], 'tmp', 'cache', 'incoming', 'saved-cases'):
        path = root / name
        if path.exists():
            shutil.rmtree(path)
            removed.append(name)
    return removed


def native_main(root, mode):
    import bpy
    import addon_utils
    from dataclasses import asdict, replace

    for name in RESOURCE_NAMES:
        expected = Path(os.environ['BLENDER_USER_' + name]).resolve()
        observed = Path(bpy.utils.resource_path('USER') if name == 'RESOURCES'
                        else bpy.utils.user_resource(name)).resolve()
        assert observed == expected and observed.is_relative_to(root), name
    bpy.context.preferences.use_preferences_save = False
    sys.path.insert(0, str(root / 'scripts/addons'))
    bpy.utils.refresh_script_paths()
    if mode == 'lifecycle':
        return native_lifecycle(root, bpy, addon_utils)
    rt = None  # Bound to the real enabled add-on after fresh preference loading.
    exporter_spec = importlib.util.spec_from_file_location('runtime_exporter', REPO / 'tests/blender_keymap_baseline.py')
    exporter = importlib.util.module_from_spec(exporter_spec)
    exporter_spec.loader.exec_module(exporter)
    receipt = {'schema_version': 1, 'mode': mode, 'status': 'running', 'steps': [],
               'dispatch': [], 'invariants': [], 'diagnostics': [],
               'native_test_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'native': {'version': bpy.app.version_string, 'build': bpy.app.build_hash.decode(),
                          'background': bpy.app.background},
               'source_sha256': {name: hashlib.sha256((root / 'scripts/addons/bluehole_runtime' / name).read_bytes()).hexdigest()
                                  for name in ('keymaps/keymap_utils.py', 'keymaps/deluxe-defaults.json', 'keymaps/deluxe_profiles.py',
                                               'keymaps/keymaps_register.py', 'actions/operator_action.py', '__init__.py')}}
    began = time.monotonic()

    def record(label, **values):
        receipt['steps'].append({'label': label, 'seconds': round(time.monotonic() - began, 5), **values})
        (root / 'runtime.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print('RUNTIME ' + label, flush=True)

    configs = lambda: bpy.context.window_manager.keyconfigs
    update = lambda: configs().update()
    handles = {}
    selectors = {}
    sentinel_refs = []
    calls = []
    state = {'poll': True, 'flow': 'finish'}

    class RUNTIME_OT_action(bpy.types.Operator):
        bl_idname = 'wm.deluxe_runtime_action'
        bl_label = 'Deluxe runtime test action'
        marker: bpy.props.StringProperty(default='')

        @classmethod
        def poll(cls, context):
            return state['poll']

        def execute(self, context):
            calls.append(self.marker)
            if self.marker == 'stock':
                objects = list(context.scene.objects)
                for obj in objects:
                    obj.select_set(False)
                objects[0].select_set(True)
            return {'PASS_THROUGH'} if state['flow'] == 'pass' else {'FINISHED'}

    class RUNTIME_OT_sentinel(bpy.types.Operator):
        bl_idname = 'wm.deluxe_runtime_sentinel'
        bl_label = 'Deluxe runtime keyboard sentinel'
        def execute(self, context):
            calls.append('sentinel')
            return {'FINISHED'}

    classes = (RUNTIME_OT_action, RUNTIME_OT_sentinel)
    for cls in classes:
        bpy.utils.register_class(cls)

    def enable_provider():
        provider = addon_utils.enable(PROVIDER, default_set=True, persistent=False)
        assert provider is not None
        preference = bpy.context.preferences.addons[PROVIDER].preferences
        preference.activate_smooth = True
        update()
        receipt['provider'] = {'module': PROVIDER, 'version': list(provider.bl_info['version']),
                               'kind': 'installed third-party source copied into disposable profile',
                               'configured_feature': 'activate_smooth'}
        return provider

    def disable_provider():
        addon_utils.disable(PROVIDER, default_set=True)
        update()

    def provider_value():
        return tuple(poly.use_smooth for obj in bpy.context.scene.objects if obj.type == 'MESH' for poly in obj.data.polygons)

    def source(role, name, predicate):
        maps = [km for km in getattr(configs(), role).keymaps if km.name == name]
        matches = [(km, item) for km in maps for item in km.keymap_items if predicate(item)]
        assert len(matches) == 1, (role, name, len(matches))
        return matches[0]

    def capture_selectors():
        km, item = source('default', 'Object Mode', lambda i: i.idname == 'object.select_all'
                          and i.type == 'A' and i.value == 'PRESS' and i.properties.action == 'SELECT')
        selectors['stock'] = rt.capture_selector(km, item, source_role='default',
             ledger_id='deluxe-baseline-2026-11-12-v1',
             sample_id='587d6f920557a2ebfd965e899461aef183d9908ec703a37394c3c605ade92328')
        if mode != 'stock-dispatch':
            km, item = source('addon', '3D View Generic', lambda i: i.idname == 'machin3.toggle_smooth')
            selectors['provider'] = rt.capture_selector(km, item, source_role='addon', sample_id='installed-machin3-smooth-v1')
        km, item = source('default', 'Transform Modal Map', lambda i: i.propvalue == 'PRECISION'
                          and i.type == 'LEFT_SHIFT' and i.value == 'ANY')
        selectors['modal'] = rt.capture_selector(km, item, source_role='default',
             ledger_id='deluxe-baseline-2026-11-12-v1',
             sample_id='000259f5b47d975e344d2139174c8859226c03e17a671d8775274f0a0873a9ea')
        receipt['selectors'] = {name: asdict(value) for name, value in selectors.items()}

    def add(name, *, applied=True):
        request = rt.KeymapOverride(name, selectors[name],
            rt.KeymapTarget(modal_value='CANCEL') if name == 'modal' else
            rt.KeymapTarget(RUNTIME_OT_action.bl_idname, {'marker': name}),
            capability='modal_head' if name == 'modal' else 'ordinary_tail',
            context={'stock': 'stock_object_mode_select_all', 'provider': 'machin3tools_object_toggle_smooth',
                     'modal': 'transform_translate_precision_cancel'}[name])
        handle = rt.register_feature('native:' + name, overrides=(request,))
        handles[name] = handle
        update()
        receipt['diagnostics'].append({'label': 'add_' + name,
                                      'values': [asdict(d) for d in handle.diagnostics]})
        if applied:
            assert handle.owned_pairs, handle.diagnostics
        return handle

    def remove(name):
        handle = handles.pop(name, None)
        if handle:
            handle.release()
        update()

    def snapshot():
        result = {}
        for role in ('default', 'active', 'addon', 'user'):
            rows = []
            for km in getattr(configs(), role).keymaps:
                if km.name not in ('Object Mode', 'Mesh', '3D View Generic', 'Transform Modal Map', 'Window'):
                    continue
                captured = exporter._capture_map(km, bpy.types.OperatorProperties)
                items = []
                for item in captured['items']:
                    if item['target'] in (RUNTIME_OT_action.bl_idname, RUNTIME_OT_sentinel.bl_idname):
                        continue
                    # This exact new modal signature has no foreign row in the tested map.
                    if (km.name == 'Transform Modal Map' and item['target'] == 'CANCEL'
                            and item['event']['type'] == 'LEFT_SHIFT'):
                        continue
                    items.append({k: v for k, v in item.items() if k != 'blender_id'})
                if items:
                    rows.append({'scope': captured['scope'], 'items': items})
            result[role] = rows
        return result

    def invariant(label, expected):
        observed = snapshot()
        passed = observed == expected
        receipt['invariants'].append({'label': label, 'passed': passed,
                                     'expected': digest(expected), 'observed': digest(observed)})
        if not passed:
            (root / ('private-difference-' + label + '.json')).write_text(json.dumps(
                {'expected': expected, 'observed': observed}, indent=2))
        assert passed, label

    # Fresh preference loading happens before UI timers; never reload preferences
    # while an active preferences editor holds pointers into the previous data.
    if mode in ('read', 'owned-read'):
        filename = 'present.blend' if mode == 'read' else 'owned-present.blend'
        shutil.copyfile(root / 'incoming' / filename, root / 'config/userpref.blend')
        bpy.ops.wm.read_userpref()
        bpy.context.preferences.use_preferences_save = False
    runtime_addon = addon_utils.enable('bluehole_runtime', default_set=True, persistent=False)
    assert runtime_addon is not None
    rt = runtime_addon.keymaps_register.keymap_utils
    if mode != 'stock-dispatch':
        enable_provider()
    else:
        receipt['provider'] = {'status': 'not_requested', 'scope': 'stock and modal dispatch only'}
    capture_selectors()
    record('isolated_runtime_loaded')

    window = bpy.context.window_manager.windows[0]
    area = next(a for a in window.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    x, y = region.x + region.width // 2, region.y + region.height // 2

    def event(key, value='PRESS', **modifiers):
        window.event_simulate(type=key, value=value, x=x, y=y, **modifiers)

    def press(key, **modifiers):
        event('MOUSEMOVE', 'NOTHING')
        event(key, **modifiers)
        event(key, 'RELEASE', **modifiers)

    def object_mode():
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

    def edit_mode():
        object_mode()
        cube = next(obj for obj in bpy.context.scene.objects if obj.type == 'MESH')
        bpy.context.view_layer.objects.active = cube
        cube.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')

    def initialize():
        km = configs().addon.keymaps.new(name='Window', space_type='EMPTY')
        sentinel_refs.append((km, km.keymap_items.new(RUNTIME_OT_sentinel.bl_idname, type='F24', value='PRESS')))
        update()

    steps = []
    def case(label, key, expected_calls, *, selected=None, provider_changes=None, poll=True, flow='finish', **mods):
        before = {}
        def begin():
            state.update(poll=poll, flow=flow)
            calls.clear()
            if selected is not None:
                object_mode()
                for obj in bpy.context.scene.objects:
                    obj.select_set(False)
            before['provider'] = provider_value()
            press(key, **mods)
        def end():
            row = {'case': label, 'calls': list(calls), 'selected': sum(o.select_get() for o in bpy.context.scene.objects),
                   'provider_changed': before['provider'] != provider_value()}
            receipt['dispatch'].append(row)
            assert calls == expected_calls, row
            if selected is not None:
                assert row['selected'] == selected, row
            if provider_changes is not None:
                assert row['provider_changed'] is provider_changes, row
            record(label)
        steps.extend((begin, end))

    def foreign_edits(restore=False):
        _, stock = source('user', 'Object Mode', lambda i: i.idname == 'object.select_all'
                          and i.type == ('F19' if restore else 'A') and i.properties.action == ('DESELECT' if restore else 'SELECT'))
        stock.type = 'A' if restore else 'F19'
        stock.properties.action = 'SELECT' if restore else 'DESELECT'
        _, provider = source('user', '3D View Generic', lambda i: i.idname == 'machin3.toggle_smooth')
        provider.type = 'TAB' if restore else 'F18'
        _, modal = source('user', 'Transform Modal Map', lambda i: i.propvalue == 'PRECISION'
                          and i.type == ('F17' if restore else 'LEFT_SHIFT'))
        modal.type = 'LEFT_SHIFT' if restore else 'F17'
        modal.value = 'ANY' if restore else 'PRESS'
        assert (stock.type, provider.type, modal.type) == (('A', 'TAB', 'LEFT_SHIFT') if restore else ('F19', 'F18', 'F17'))

    def save(name):
        assert bpy.ops.wm.save_userpref() == {'FINISHED'}
        folder = root / 'saved-cases'
        folder.mkdir(exist_ok=True)
        shutil.copyfile(root / 'config/userpref.blend', folder / (name + '.blend'))

    def persistence():
        object_mode()
        for name in tuple(handles):
            remove(name)
        baseline = snapshot()
        foreign_edits()
        save('control')
        expected = snapshot()
        (root / 'saved-cases/expected.json').write_text(json.dumps(expected))
        foreign_edits(restore=True)
        update()
        invariant('intentional_edit_restored', baseline)
        for name in ('stock', 'provider', 'modal'):
            add(name)
        invariant('all_owned_before_immediate_edit', baseline)
        foreign_edits()
        # Save in the same callback: no runtime tick can repair this state first.
        save('present')
        invariant('immediate_edit_save', expected)
        original_create = rt._create_override
        attempts = []
        def observe_creation(*args, **kwargs):
            attempts.append(args[0].request_id)
            return original_create(*args, **kwargs)
        rt._create_override = observe_creation
        try:
            for _ in range(20):
                # Explicit refresh also bypasses retry delay, so this proves
                # preflight refusal rather than merely waiting out a timer.
                for handle in handles.values():
                    handle.refresh()
                rt.reconcile()
            assert not attempts, attempts
            assert all(not handle.owned_pairs for handle in handles.values())
            invariant('edited_targets_twenty_checks_no_recreation', expected)
            record('edited_targets_twenty_checks_no_creation_attempts', attempts=len(attempts))
        finally:
            rt._create_override = original_create
        for name in tuple(handles):
            remove(name)
        invariant('foreign_edits_after_release', expected)
        receipt['immediate_save_without_reconciliation'] = True

    def reader():
        expected = json.loads((root / 'incoming/expected.json').read_text())
        invariant('fresh_reopen_foreign_edits', expected)
        for name in ('stock', 'provider', 'modal'):
            handle = add(name, applied=False)
            # Edited merged rows make the original selector ineligible.
            assert not handle.owned_pairs, handle.diagnostics
        invariant('edited_targets_remain_after_later_add', expected)
        for name in tuple(handles):
            remove(name)
        invariant('edited_targets_remain_after_later_remove', expected)

    def owned_invariant(name):
        before = snapshot()
        add(name)
        invariant(name + '_add_preserves_foreign', before)

    def provider_reload_begin():
        disable_provider()
        state['provider_reload_began'] = time.monotonic()

    def provider_reload_enable():
        assert not handles['provider'].owned_pairs, handles['provider'].diagnostics
        enable_provider()
        state['provider_available_at'] = time.monotonic()

    def provider_reload_recovered():
        assert handles['provider'].owned_pairs, handles['provider'].diagnostics
        record('provider_unregister_register_recovered_by_watcher',
               observed_seconds_since_available=time.monotonic() - state['provider_available_at'])

    def unchanged():
        before = rt.runtime_stats()
        times = []
        for _ in range(20):
            start = time.monotonic()
            rt.reconcile(budget=16, time_budget=0.004)
            times.append(time.monotonic() - start)
        after = rt.runtime_stats()
        assert before['created'] == after['created'] and before['removed'] == after['removed'], (before, after)
        receipt['unchanged_reconciliation'] = {'iterations': 20, 'max_seconds': max(times), 'before': before, 'after': after}

    def modal_case(label, cancelled):
        positions = {}
        def prepare():
            object_mode()
            cube = next(obj for obj in bpy.context.scene.objects if obj.type == 'MESH')
            bpy.context.view_layer.objects.active = cube
            for obj in bpy.context.scene.objects:
                obj.select_set(obj == cube)
            cube.location = (0, 0, 0)
            positions['object'] = cube
            press('G')
        def drag():
            window.event_simulate(type='MOUSEMOVE', value='NOTHING', x=x + 90, y=y + 40)
        def shift():
            positions['drag'] = positions['object'].location.length
            event('LEFT_SHIFT')
        def confirm():
            press('RET')
            event('LEFT_SHIFT', 'RELEASE')
        def end():
            final = positions['object'].location.length
            assert positions['drag'] > 0.1 and ((final < 1e-6) if cancelled else final > 0.1), (label, positions['drag'], final)
            receipt['dispatch'].append({'case': label, 'drag_distance': positions['drag'], 'final_distance': final})
            record(label)
        steps.extend((prepare, drag, shift, confirm, end))

    def diagnostics_cases():
        before = snapshot()
        unsupported = rt.register_feature('native:unsupported', overrides=(rt.KeymapOverride(
            'veto', selectors['stock'], rt.KeymapTarget(RUNTIME_OT_action.bl_idname, {'marker': 'stock'}),
            capability='suppress_item', context='stock_object_mode_select_all'),))
        assert not unsupported.owned_pairs
        assert any(d.reason == 'unsupported_capability' for d in unsupported.diagnostics)
        unsupported.release()
        invariant('unsupported_veto_has_no_effect', before)
        first = add('provider')
        conflict = rt.register_feature('native:conflict', overrides=first.overrides)
        assert not conflict.owned_pairs and any(d.reason == 'conflicting_assignment' for d in conflict.diagnostics)
        conflict.release()
        remove('provider')
        invariant('conflicting_owner_has_no_foreign_effect', before)
        # Isolated active keyconfig supplies originally missing/inactive/ambiguous
        # rows. Existing default/add-on rows remain untouched.
        previous = configs().active
        fixture = configs().new('Deluxe Runtime Selector Fixture')
        km = fixture.keymaps.new(name='Object Mode', space_type='EMPTY')
        configs().active = fixture
        update()
        selector = replace(selectors['stock'], source_role='active')
        def request(label):
            handle = rt.register_feature('native:selector:' + label, overrides=(rt.KeymapOverride(
                label, selector, rt.KeymapTarget(RUNTIME_OT_action.bl_idname, {'marker': 'stock'}),
                capability='ordinary_tail', context='stock_object_mode_select_all'),))
            receipt['diagnostics'].append({'label': label, 'values': [asdict(d) for d in handle.diagnostics]})
            assert not handle.owned_pairs, handle.diagnostics
            handle.release()
        try:
            request('missing')
            item = km.keymap_items.new('object.select_all', type='A', value='PRESS')
            item.properties.action = 'SELECT'
            item.active = False  # Initial fixture state; never an existing foreign source.
            request('originally_inactive')
            km.keymap_items.remove(item)
            for _ in range(2):
                item = km.keymap_items.new('object.select_all', type='A', value='PRESS')
                item.properties.action = 'SELECT'
            request('ambiguous')
        finally:
            configs().active = previous
            configs().remove(fixture)
            update()
        invariant('selector_fixture_restored', before)
        assignment = rt.KeymapAssignment('valid', rt.KeymapScope('Window'), rt.KeymapEvent('F22'),
                                          rt.KeymapTarget(RUNTIME_OT_action.bl_idname, {'marker': 'valid'}))
        bad = replace(assignment, request_id='bad', event=rt.KeymapEvent('F21'),
                      target=rt.KeymapTarget(RUNTIME_OT_action.bl_idname, {'marker': 'bad', 'undefined_property': True}))
        failed = rt.register_feature('native:partial', assignments=(assignment, bad))
        assert not failed.owned_pairs
        assert not any(i.idname == RUNTIME_OT_action.bl_idname for km in configs().addon.keymaps for i in km.keymap_items)
        failed.release()
        recovered = rt.register_feature('native:partial', assignments=(assignment,))
        assert len(recovered.owned_pairs) == 1
        km, item = recovered.owned_pairs[0]
        km.keymap_items.remove(item)  # Simulated user deletion of the owned item.
        foreign = km.keymap_items.new(RUNTIME_OT_action.bl_idname, type='F22', value='PRESS')
        foreign.properties.marker = 'valid'
        recovered.refresh()
        recovered.release()
        assert any(i.as_pointer() == foreign.as_pointer() for i in km.keymap_items)
        km.keymap_items.remove(foreign)
        update()
        invariant('partial_failure_recovery_stale_lookalike', before)
        record('fail_closed_and_transaction_cases')

    def cold_provider_request():
        disable_provider()
        handle = add('provider', applied=False)
        assert not handle.owned_pairs
        enable_provider()
        record('requested_before_provider_registration')

    def cold_provider_recovered():
        assert handles['provider'].owned_pairs, handles['provider'].diagnostics
        remove('provider')
        record('late_provider_recovered_by_actual_watcher')

    def repeated_overtaking():
        handle = add('provider')
        fixture_rows = []
        before = rt.runtime_stats()
        try:
            for _ in range(4):
                km = handle.owned_pairs[0][0]
                item = km.keymap_items.new(RUNTIME_OT_sentinel.bl_idname, type='TAB', value='PRESS', alt=True)
                fixture_rows.append((km, item))
                update()
                handle.refresh()
            after = rt.runtime_stats()
            assert after['reinsertions'] - before['reinsertions'] == 2, (before, after)
            assert any(d.reason == 'provider_priority_conflict' for d in handle.diagnostics), handle.diagnostics
            for _ in range(4):
                handle.refresh()
            assert rt.runtime_stats()['created'] == after['created']
            receipt['overtaking'] = {'before': before, 'after': after,
                                      'diagnostics': [asdict(d) for d in handle.diagnostics]}
        finally:
            remove('provider')
            for km, item in reversed(fixture_rows):
                km.keymap_items.remove(item)
            update()
        record('repeated_overtaking_stops_after_two_reinsertions')

    def copied_legacy_pair_cleanup():
        handle = add('provider')
        copied = list(handle.owned_pairs)
        km = copied[0][0]
        fallback = km.keymap_items.new(RUNTIME_OT_sentinel.bl_idname, type='TAB', value='PRESS', alt=True)
        update()
        handle.refresh()
        assert handle.owned_pairs
        # A distinct, exact lookalike must survive cleanup via the old wrapper pair.
        foreign = km.keymap_items.new(RUNTIME_OT_action.bl_idname, type='TAB', value='PRESS', alt=True)
        foreign.properties.marker = 'provider'
        foreign_id = foreign.id
        rt.release_owned_pairs(copied)
        assert not handle.owned_pairs and not copied
        assert any(i.id == foreign_id for i in km.keymap_items)
        rt.reconcile(budget=16, time_budget=0.02)
        assert not handle.owned_pairs
        km.keymap_items.remove(foreign)
        km.keymap_items.remove(fallback)
        remove('provider')
        record('copied_pre_repriority_pairs_release_current_request_and_preserve_lookalike')

    def native_removal_faults():
        original_remove = rt._remove_native_item
        fault = {'enabled': True, 'attempts': 0}
        fault_fixture_pairs = []
        def injected(map_, item):
            if fault['enabled'] and item.idname == RUNTIME_OT_action.bl_idname:
                fault['attempts'] += 1
                raise RuntimeError('injected native removal failure')
            return original_remove(map_, item)
        def rows():
            return [(km, i) for km in configs().addon.keymaps for i in km.keymap_items
                    if i.idname == RUNTIME_OT_action.bl_idname]
        assignment = rt.KeymapAssignment('cleanup', rt.KeymapScope('Window'), rt.KeymapEvent('F22'),
                                          rt.KeymapTarget(RUNTIME_OT_action.bl_idname, {'marker': 'cleanup'}))
        bad = replace(assignment, request_id='bad', event=rt.KeymapEvent('F21'),
                      target=rt.KeymapTarget(RUNTIME_OT_action.bl_idname, {'undefined_property': True}))
        rt._remove_native_item = injected
        try:
            failed = rt.register_feature('native:rollback-fault', assignments=(assignment, bad))
            assert rt.runtime_stats()['pending_cleanup'] == 2 and len(rows()) == 2
            failed.refresh()
            assert len(rows()) == 2  # Failed cleanup never licenses a duplicate.
            fault['enabled'] = False
            rt.reconcile(budget=16, time_budget=0.02)
            failed.release()
            assert rt.runtime_stats()['pending_cleanup'] == 0 and not rows()
            fault['enabled'] = True
            handle = rt.register_feature('native:release-fault', assignments=(assignment,))
            handle.release()
            assert rt.runtime_stats()['pending_cleanup'] == 1 and len(rows()) == 1
            replay = rt.register_feature('native:release-fault', assignments=(assignment,))
            assert not replay.owned_pairs and len(rows()) == 1
            replay.release()
            renamed = rt.register_feature('native:release-fault', assignments=(
                replace(assignment, request_id='cleanup-renamed'),))
            assert not renamed.owned_pairs and len(rows()) == 1
            assert any(d.reason == 'conflicting_assignment' for d in renamed.diagnostics), renamed.diagnostics
            renamed.release()
            rival = rt.register_feature('native:different-owner', assignments=(assignment,))
            assert not rival.owned_pairs and len(rows()) == 1
            assert any(d.reason == 'conflicting_assignment' for d in rival.diagnostics), rival.diagnostics
            rival.refresh()
            assert not rival.owned_pairs and len(rows()) == 1
            fault['enabled'] = False
            rt.reconcile(budget=16, time_budget=0.02)
            rival.refresh()
            assert rt.runtime_stats()['pending_cleanup'] == 0
            assert len(rival.owned_pairs) == 1 and len(rows()) == 1
            rival.release()
            assert not rows()
            handle = add('provider')
            km = handle.owned_pairs[0][0]
            fallback = km.keymap_items.new(RUNTIME_OT_sentinel.bl_idname, type='TAB', value='PRESS', alt=True)
            fault_fixture_pairs.append((km, fallback))
            fault['enabled'] = True
            handle.refresh()
            assert rt.runtime_stats()['pending_cleanup'] == 1 and len(rows()) == 1
            handle.refresh()
            assert len(rows()) == 1
            fault['enabled'] = False
            rt.reconcile(budget=16, time_budget=0.02)
            handle.refresh()
            assert len(handle.owned_pairs) == 1 and len(rows()) == 1, {
                'diagnostics': [asdict(d) for d in handle.diagnostics], 'runtime': rt.runtime_stats(),
                'native_rows': len(rows())}
            remove('provider')
            km.keymap_items.remove(fallback)
            assert not rows() and rt.runtime_stats()['pending_cleanup'] == 0
            receipt['native_removal_fault_injection'] = {'failure_attempts': fault['attempts'],
                'cases': ['rollback', 'release_and_replay', 'renamed_request_conflict',
                          'different_owner_conflict', 'repriority'],
                'note': 'Injected exception at native removal call boundary; not an observed Blender failure.'}
            record('native_removal_failures_retain_ownership_and_recover_without_duplicates')
        finally:
            fault['enabled'] = False
            rt._remove_native_item = original_remove
            for map_, item in fault_fixture_pairs:
                try:
                    map_.keymap_items.remove(item)
                except (ReferenceError, RuntimeError):
                    pass
            rt.reconcile(budget=16, time_budget=0.02)

    def disabled_provider_lookalike():
        disable_provider()
        class RUNTIME_OT_provider_shape(bpy.types.Operator):
            bl_idname = 'machin3.toggle_smooth'
            bl_label = 'Synthetic disabled-provider lookalike'
            mode: bpy.props.StringProperty(default='SUBD')
            toggle_korean_bevel_overlays: bpy.props.BoolProperty(default=True)
            toggle_subd_overlays: bpy.props.BoolProperty(default=False)
            def execute(self, context):
                return {'FINISHED'}
        bpy.utils.register_class(RUNTIME_OT_provider_shape)
        km = configs().addon.keymaps.new(name='3D View Generic', space_type='VIEW_3D')
        item = km.keymap_items.new('machin3.toggle_smooth', type='TAB', value='PRESS', alt=True)
        try:
            update()
            assert rt.capture_target(item) == selectors['provider'].target
            handle = add('provider', applied=False)
            assert not handle.owned_pairs
            receipt['diagnostics'].append({'label': 'disabled_provider_exact_lookalike',
                                          'values': [asdict(d) for d in handle.diagnostics]})
            assert any(i.id == item.id for i in km.keymap_items)
            remove('provider')
        finally:
            km.keymap_items.remove(item)
            bpy.utils.unregister_class(RUNTIME_OT_provider_shape)
            enable_provider()
        record('disabled_installed_provider_exact_lookalike_rejected')

    def modal_active_config_transition():
        handle = add('modal')
        previous = configs().active
        alternate = configs().new('Deluxe Runtime Unproved Modal Preset')
        try:
            configs().active = alternate
            update()
            handle.refresh()
            assert not handle.owned_pairs
            assert not any(i.propvalue == 'CANCEL' and i.type == 'LEFT_SHIFT'
                           for km in configs().default.keymaps if km.name == 'Transform Modal Map'
                           for i in km.keymap_items)
            custom_request = replace(handle.overrides[0], selector=replace(selectors['modal'], source_role='active'))
            unproved = rt.register_feature('native:unproved-modal-preset', overrides=(custom_request,))
            assert not unproved.owned_pairs
            unproved.release()
            remove('modal')
        finally:
            configs().active = previous
            configs().remove(alternate)
            update()
        assert not any(i.propvalue == 'CANCEL' and i.type == 'LEFT_SHIFT'
                       for km in configs().default.keymaps if km.name == 'Transform Modal Map'
                       for i in km.keymap_items)
        record('modal_switch_away_back_leaves_no_owned_copy')

    def owned_edit_assignment():
        return rt.KeymapAssignment('edit', rt.KeymapScope('Window'), rt.KeymapEvent('F22'),
                                  rt.KeymapTarget(RUNTIME_OT_action.bl_idname, {'marker': 'owned-original'}))

    def owned_edit_writer():
        assignment = owned_edit_assignment()
        handle = rt.register_feature('native:owned-edit', assignments=(assignment,))
        assert handle.owned_pairs, handle.diagnostics
        update()
        _, item = source('user', 'Window', lambda i: i.idname == RUNTIME_OT_action.bl_idname)
        item.type = 'F23'
        item.properties.marker = 'owned-user-edit'
        save('owned-present')  # Immediate save, before release or reconciliation.
        handle.release()
        update()
        assert not any(i.idname == RUNTIME_OT_action.bl_idname for km in configs().addon.keymaps for i in km.keymap_items)
        again = rt.register_feature('native:owned-edit', assignments=(assignment,))
        update()
        _, item = source('user', 'Window', lambda i: i.idname == RUNTIME_OT_action.bl_idname)
        assert item.type == 'F23' and item.properties.marker == 'owned-user-edit'
        again.release()
        update()
        receipt['owned_user_edit'] = 'saved diff dormant on disable; restored on re-enable after empty-map cleanup'
        # Direct addon-source edits are explicitly transferred and diagnosed.
        direct = rt.register_feature('native:direct-edit', assignments=(replace(assignment, event=rt.KeymapEvent('F21')),))
        km, item = direct.owned_pairs[0]
        item.type = 'F20'
        item.properties.marker = 'direct-source-edit'
        result = direct.release()
        retained = rt.retained_edits()
        assert retained and any(reason == 'user_edited_owned_item_retained' for _, reason in result)
        again = rt.register_feature('native:direct-edit', assignments=direct.assignments)
        assert not again.owned_pairs
        again.release()
        receipt['direct_source_edit'] = {'release': result, 'retained_count': len(retained),
                                         'behavior': 'visible user-adopted row; reported, never silently recreated'}
        # The test author owns this intentional fixture edit and removes its exact
        # reference after checking the runtime's non-destructive transfer.
        km.keymap_items.remove(item)
        update()
        assert not rt.retained_edits()
        record('owned_edits_preserved_and_explicitly_accounted')

    def owned_edit_reader():
        handle = rt.register_feature('native:owned-edit', assignments=(owned_edit_assignment(),))
        update()
        _, item = source('user', 'Window', lambda i: i.idname == RUNTIME_OT_action.bl_idname)
        assert item.type == 'F23' and item.properties.marker == 'owned-user-edit' and item.is_user_modified
        receipt['owned_user_edit_reopened'] = {'type': item.type, 'marker': item.properties.marker,
                                              'active': item.active, 'is_user_modified': item.is_user_modified}
        handle.release()
        update()
        assert not any(i.idname == RUNTIME_OT_action.bl_idname for km in configs().addon.keymaps for i in km.keymap_items)
        record('owned_user_edit_fresh_reopen_and_release')

    if mode == 'stock-dispatch':
        steps.extend((lambda: press('ESC'), lambda: press('ESC'), initialize))
        case('keyboard_sentinel', 'F24', ['sentinel'])
        case('stock_baseline', 'A', [], selected=3)
        steps.append(lambda: owned_invariant('stock'))
        case('stock_replacement', 'A', ['stock'], selected=1)
        case('stock_poll_fallback', 'A', [], selected=3, poll=False)
        case('stock_pass_through', 'A', ['stock'], selected=3, flow='pass')
        steps.extend((lambda: remove('stock'), object_mode))
        modal_case('modal_baseline', False)
        steps.append(lambda: owned_invariant('modal'))
        modal_case('modal_replacement_cancel', True)
        steps.append(lambda: remove('modal'))
        modal_case('modal_release_fallback', False)
        steps.extend((modal_active_config_transition, unchanged))
    elif mode == 'write':
        steps.extend((lambda: press('ESC'), lambda: press('ESC'), initialize))
        case('keyboard_sentinel', 'F24', ['sentinel'])
        case('stock_baseline', 'A', [], selected=3)
        steps.append(lambda: owned_invariant('stock'))
        case('stock_replacement', 'A', ['stock'], selected=1)
        case('stock_poll_fallback', 'A', [], selected=3, poll=False)
        case('stock_pass_through', 'A', ['stock'], selected=3, flow='pass')
        steps.extend((lambda: remove('stock'), object_mode))
        case('installed_provider_baseline', 'TAB', [], provider_changes=True, alt=True)
        steps.append(lambda: owned_invariant('provider'))
        case('installed_provider_replacement', 'TAB', ['provider'], provider_changes=False, alt=True)
        case('installed_provider_poll_fallback', 'TAB', [], provider_changes=True, poll=False, alt=True)
        case('installed_provider_pass_through', 'TAB', ['provider'], provider_changes=True, flow='pass', alt=True)
        steps.extend((provider_reload_begin, provider_reload_enable, lambda: None, provider_reload_recovered))
        case('installed_provider_reload_replacement', 'TAB', ['provider'], provider_changes=False, alt=True)
        steps.extend((unchanged, lambda: remove('provider'), object_mode))
        modal_case('modal_baseline', False)
        steps.append(lambda: owned_invariant('modal'))
        modal_case('modal_replacement_cancel', True)
        steps.append(lambda: remove('modal'))
        modal_case('modal_release_fallback', False)
        steps.append(persistence)
    elif mode == 'read':
        steps.append(reader)
    elif mode == 'mechanics':
        steps.extend((diagnostics_cases, cold_provider_request, cold_provider_recovered, repeated_overtaking,
                      copied_legacy_pair_cleanup, native_removal_faults, disabled_provider_lookalike,
                      modal_active_config_transition, owned_edit_writer))
    elif mode == 'owned-read':
        steps.append(owned_edit_reader)
    else:
        raise ValueError('Unsupported runtime mode: ' + mode)

    def cleanup():
        for name in tuple(handles):
            remove(name)
        rt.release_all()
        receipt['watcher'] = dict(runtime_addon.keymaps_register.watcher_stats)
        addon_utils.disable('bluehole_runtime', default_set=True)
        assert not bpy.app.timers.is_registered(runtime_addon.keymaps_register._watch_keymaps)
        for km, item in reversed(sentinel_refs):
            km.keymap_items.remove(item)
        sentinel_refs.clear()
        update()
        if mode != 'stock-dispatch':
            disable_provider()
        update()
        remaining = [(role, km.name, item.idname) for role in ('default', 'addon', 'user')
                     for km in getattr(configs(), role).keymaps for item in km.keymap_items
                     if item.idname in (RUNTIME_OT_action.bl_idname, RUNTIME_OT_sentinel.bl_idname)]
        assert not remaining, remaining
        assert not any(item.propvalue == 'CANCEL' and item.type == 'LEFT_SHIFT'
                       for km in configs().default.keymaps if km.name == 'Transform Modal Map'
                       for item in km.keymap_items)
        receipt['remaining_native_fixture_items'] = remaining
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)
        receipt['cleanup'] = rt.runtime_stats()
        assert not receipt['cleanup'].get('owned', 0)
        assert not receipt['cleanup'].get('pending_cleanup', 0)

    actions = iter(steps)
    def quit_blender():
        bpy.ops.wm.quit_blender()
    def tick():
        try:
            next(actions)()
            return 0.35
        except StopIteration:
            cleanup()
            receipt['status'] = 'complete'
            record('complete')
        except Exception:
            receipt['status'] = 'error'
            receipt['error'] = traceback.format_exc()
            try:
                cleanup()
            except Exception:
                receipt['cleanup_error'] = traceback.format_exc()
            record('failed')
        bpy.app.timers.register(quit_blender, first_interval=0.5)
    bpy.app.timers.register(tick, first_interval=2.0)
    record('gui_timer_scheduled')


def native_lifecycle(root, bpy, addon_utils):
    """Exercise the real add-on initializer, categories and one persistent watcher."""
    receipt = {'schema_version': 1, 'mode': 'lifecycle', 'status': 'running', 'steps': [],
               'native_test_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'source_sha256': {name: hashlib.sha256((root / 'scripts/addons/bluehole_runtime' / name).read_bytes()).hexdigest()
                                  for name in ('keymaps/keymap_utils.py', 'keymaps/deluxe-defaults.json', 'keymaps/deluxe_profiles.py',
                                               'keymaps/keymaps_register.py', 'actions/operator_action.py', '__init__.py')},
               'native': {'version': bpy.app.version_string, 'build': bpy.app.build_hash.decode()}}
    started = time.monotonic()
    state = {}
    name = 'bluehole_runtime'
    configs = bpy.context.window_manager.keyconfigs

    def record(label, **values):
        receipt['steps'].append({'label': label, 'seconds': round(time.monotonic() - started, 5), **values})
        (root / 'runtime.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print('RUNTIME ' + label, flush=True)

    def addon_rows():
        return [(km.name, km.space_type, km.region_type,
                 [(i.idname, i.type, i.value, i.ctrl, i.shift, i.alt, i.oskey, i.active)
                  for i in km.keymap_items]) for km in configs.addon.keymaps if len(km.keymap_items)]

    original = addon_rows()

    def enable():
        module = addon_utils.enable(name, default_set=True, persistent=False)
        assert module is not None
        state['module'] = module
        state['km'] = module.keymaps_register
        state['rt'] = module.keymaps_register.keymap_utils
        state['prefs'] = bpy.context.preferences.addons[name].preferences
        state['enable_time'] = time.monotonic()
        record('addon_enabled', init_timer=bpy.app.timers.is_registered(module._post_register_init),
               addon_flag=module._addon_registered, preferences_ready=state['prefs'] is not None)

    def ready():
        module, km, rt = state['module'], state['km'], state['rt']
        if not module._keymaps_registered:
            details = {'init_timer': bpy.app.timers.is_registered(module._post_register_init),
                       'addon_flag': module._addon_registered, 'error': module._post_register_error,
                       'preferences_ready': state['prefs'] is not None,
                       'configs': {role: getattr(configs, role, None) is not None for role in ('addon', 'user', 'active')}}
            record('waiting_for_startup', **details)
            assert time.monotonic() - state['enable_time'] < 6, details
            return False
        assert bpy.app.timers.is_registered(km._watch_keymaps)
        assert bpy.app.timers.is_registered(module.update_env_timer)
        assert rt.runtime_stats()['owned'] > 0
        record('addon_ready', runtime=rt.runtime_stats())

    def all_on():
        prefs = state['prefs']
        prefs.keymap.deluxe_configured = True
        prefs.keymap.enable_keymaps = True
        state['km'].refresh()
        assert state['km'].deluxe_section_enabled('addons.blue-hole')
        record('global_and_pie_enabled', runtime=state['rt'].runtime_stats())

    def all_off():
        prefs, km = state['prefs'], state['km']
        prefs.keymap.enable_keymaps = False
        km.refresh()
        rt = state['rt']
        assert rt.runtime_stats()['owned'] == 2
        assert {request.target.idname for handle in rt._FEATURES.values()
                for request in handle.assignments} == {'wm.bh_save_as_mainfile'}
        record('global_off_retains_obligatory_pipeline', runtime=rt.runtime_stats())
        prefs.keymap.enable_keymaps = True
        store = km.deluxe_profile()
        draft = store.begin()
        draft.update('categories', 'addons', enabled=False)
        store.apply(draft)
        assert not km.deluxe_section_enabled('addons.blue-hole')
        assert any(request.target.idname == 'wm.bh_save_as_mainfile'
                   for handle in rt._FEATURES.values() for request in handle.assignments)
        record('pie_disabled_independently')
        draft = store.begin()
        draft.update('categories', 'addons', enabled=True)
        store.apply(draft)

    def partial_failure():
        km, rt = state['km'], state['rt']
        state['prefs'].keymap.enable_keymaps = True
        store = km.deluxe_profile()
        original_register = store.register
        def fail(profile, **kwargs):
            original_register(profile, **kwargs)
            raise RuntimeError('injected catalog registration failure')
        store.register = fail
        try:
            try:
                km.refresh()
            except RuntimeError as exc:
                assert str(exc) == 'injected catalog registration failure'
            else:
                raise AssertionError('Expected catalog registration failure')
            assert rt.runtime_stats()['owned'] == 0, rt.runtime_stats()
        finally:
            store.register = original_register
        km.refresh()
        assert rt.runtime_stats()['owned'] > 0
        record('partial_category_failure_rolled_back_and_recovered', runtime=rt.runtime_stats())

    def config_transition():
        km, rt = state['km'], state['rt']
        previous = configs.active
        alternate = configs.new('Deluxe Runtime Transition Fixture')
        try:
            configs.active = alternate
            configs.update()
            km._watch_keymaps()
            transitioned = rt.runtime_stats()
        finally:
            configs.active = previous
            configs.update()
            km._watch_keymaps()
            configs.remove(alternate)
        assert rt.runtime_stats()['owned'] > 0
        record('active_keyconfig_round_trip', during=transitioned, after=rt.runtime_stats())

    def unchanged():
        km, rt = state['km'], state['rt']
        before = rt.runtime_stats()
        durations = []
        for _ in range(20):
            then = time.monotonic()
            km._watch_keymaps()
            durations.append(time.monotonic() - then)
        after = rt.runtime_stats()
        assert before['created'] == after['created'] and before['removed'] == after['removed'], (before, after)
        record('unchanged_watcher_twenty_ticks', max_seconds=max(durations), before=before, after=after,
               watcher=km.watcher_stats)

    def disable():
        module, km, rt = state['module'], state['km'], state['rt']
        addon_utils.disable(name, default_set=True)
        assert not bpy.app.timers.is_registered(km._watch_keymaps)
        assert not bpy.app.timers.is_registered(module._post_register_init)
        assert not bpy.app.timers.is_registered(module.update_env_timer)
        assert rt.runtime_stats()['owned'] == 0 and rt.runtime_stats()['features'] == 0
        assert rt.runtime_stats()['pending_cleanup'] == 0
        configs.update()
        assert addon_rows() == original
        record('addon_disabled_all_owned_resources_drained', runtime=rt.runtime_stats())

    steps = iter((enable, ready, all_on, all_off, all_on, all_off, partial_failure,
                  config_transition, unchanged, disable, enable, ready, disable))
    def tick():
        try:
            if state.get('pending_action') is None:
                state['pending_action'] = next(steps)
            if state['pending_action']() is not False:
                state['pending_action'] = None
            return 0.5
        except StopIteration:
            receipt['status'] = 'complete'
            record('complete')
        except Exception:
            receipt['status'] = 'error'
            receipt['error'] = traceback.format_exc()
            try:
                if name in bpy.context.preferences.addons:
                    addon_utils.disable(name, default_set=True)
            except Exception:
                receipt['cleanup_error'] = traceback.format_exc()
            record('failed')
        bpy.app.timers.register(lambda: bpy.ops.wm.quit_blender() and None, first_interval=0.5)
    bpy.app.timers.register(tick, first_interval=2.0)
    record('lifecycle_scheduled')


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blender', type=Path, required=True)
    parser.add_argument('--provider-source', type=Path)
    parser.add_argument('--stock-only', action='store_true', help='Exercise stock/modal dispatch without a third-party fixture')
    parser.add_argument('--output', type=Path, default=REPO / 'test-results/deluxe-keymaps-runtime')
    parser.add_argument('--test-minimum-version', help='Change only the disposable add-on copy, e.g. 4.5.1')
    args = parser.parse_args()
    if not args.stock_only and args.provider_source is None:
        parser.error('--provider-source is required unless --stock-only is selected')
    if not Path('/usr/bin/sandbox-exec').is_file():
        parser.error('This GUI isolation launcher requires macOS sandbox-exec.')
    minimum = tuple(map(int, args.test_minimum_version.split('.'))) if args.test_minimum_version else None
    args.output = args.output.resolve()
    results, roots = [], []
    try:
        if args.stock_only:
            root, result = launch_case(args.blender, None, args.output, 'stock-dispatch', minimum=minimum)
            roots.append(root); results.append(result)
            if result['returncode'] != 0 or result['runtime']['status'] != 'complete':
                raise RuntimeError('Stock/modal dispatch failed; inspect the native receipt')
            print(json.dumps({'status': 'complete', 'cases': 1, 'scope': 'stock/modal dispatch'}))
            return
        writer, result = launch_case(args.blender, args.provider_source, args.output, 'write', minimum=minimum)
        roots.append(writer); results.append(result)
        if result['returncode'] != 0 or result['runtime']['status'] != 'complete':
            raise RuntimeError('Integrated writer failed; see its private runtime receipt.')
        reader, result = launch_case(args.blender, args.provider_source, args.output, 'read',
                                     minimum=minimum, incoming=writer / 'saved-cases')
        roots.append(reader); results.append(result)
        if result['returncode'] != 0 or result['runtime']['status'] != 'complete':
            raise RuntimeError('Integrated reader failed; see its private runtime receipt.')
        lifecycle, result = launch_case(args.blender, args.provider_source, args.output, 'lifecycle', minimum=minimum)
        roots.append(lifecycle); results.append(result)
        if result['returncode'] != 0 or result['runtime']['status'] != 'complete':
            raise RuntimeError('Integrated add-on lifecycle failed; see its private runtime receipt.')
        mechanics, result = launch_case(args.blender, args.provider_source, args.output, 'mechanics', minimum=minimum)
        roots.append(mechanics); results.append(result)
        if result['returncode'] != 0 or result['runtime']['status'] != 'complete':
            raise RuntimeError('Integrated ownership mechanics failed; see its private runtime receipt.')
        owned_reader, result = launch_case(args.blender, args.provider_source, args.output, 'owned-read',
                                           minimum=minimum, incoming=mechanics / 'saved-cases')
        roots.append(owned_reader); results.append(result)
        if result['returncode'] != 0 or result['runtime']['status'] != 'complete':
            raise RuntimeError('Edited owned binding fresh reopen failed; see its private runtime receipt.')
    finally:
        cleanup = {root.name: cleanup_resources(root) for root in roots}
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / 'receipt.json').write_text(json.dumps({'cases': results, 'cleanup': cleanup}, indent=2) + '\n')
    print(json.dumps({'status': 'complete', 'cases': len(results), 'receipt': str(args.output / 'receipt.json')}))


if __name__ == '__main__':
    if os.environ.get('DELUXE_RUNTIME_MODE'):
        native_main(Path(os.environ['DELUXE_CAPTURE_ROOT']).resolve(), os.environ['DELUXE_RUNTIME_MODE'])
    else:
        cli()
