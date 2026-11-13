"""Confined GUI evidence for Deluxe Navigation, Selection and Transform.

Run only when this lane owns the coordinated native input slot. An explicit
executable is required. Original app/profile/provider inputs are read-only;
all resource writes and event injection belong to the one owned child process.
"""
import argparse
import copy
from dataclasses import asdict
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback

REPO = Path(os.environ.get('DELUXE_CATEGORY_REPO', Path(__file__).resolve().parents[1])).resolve()
RESOURCE_NAMES = ('RESOURCES', 'CONFIG', 'SCRIPTS', 'EXTENSIONS', 'DATAFILES')
PACKAGE = 'bluehole_runtime'
PRODUCTION_PATHS = (
    'actions/actions/keymaps/navigation/__init__.py',
    'actions/actions/keymaps/navigation/viewport_movement.py',
    'actions/actions/keymaps/navigation/viewport_axis.py',
    'actions/actions/keymaps/navigation/view_framing.py',
    'actions/actions/keymaps/selection/selection_more_less.py',
    'actions/actions/keymaps/selection/selection_tool_switch.py',
    'actions/actions/keymaps/selection/selection_all_none.py',
    'actions/actions/keymaps/selection/selection_circle.py',
    'actions/actions/keymaps/selection/__init__.py',
    'actions/actions/keymaps/transform/transform_tools_modal.py',
    'actions/actions/keymaps/transform/transform_tools_gizmo.py',
    'actions/actions/keymaps/transform/__init__.py',
    'keymaps/navigation_keymaps_register.py',
    'keymaps/selection_keymaps_register.py',
    'keymaps/transform_keymaps_register.py',
    'preferences/addon/keymaps/keymap_props_navigation.py',
    'preferences/addon/keymaps/keymap_props_selection.py',
    'preferences/addon/keymaps/keymap_props_transform.py',
    'operators/box_xray_ops.py',
    'operators/selection_more_less_ops.py', 'operators/operators_register.py',
    'keymaps/pipeline_keymaps_register.py', 'actions/actions/keymaps/pipeline/obligatory.py',
    'keymaps/keymap_utils.py', 'keymaps/keymap_action_utils.py',
    'keymaps/keymaps_register.py', 'actions/operator_action.py', '__init__.py',
)


def load_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def protected_hashes(profile=None):
    paths = {'packaged_preset': REPO / 'overlays/deluxe/payload/keyconfig/BH_Keymaps.py',
             'packaged_preferences': REPO / 'overlays/deluxe/payload/userpref.blend'}
    if profile:
        paths.update(reference_preset=profile / 'scripts/presets/keyconfig/BH_Keymaps.py',
                     reference_preferences=profile / 'config/userpref.blend')
    return {name: sha(path) for name, path in paths.items()}


def retain_crashes(root, args, process):
    """Retain owned diagnostics before either normal or exceptional cleanup."""
    retained = []
    app = args.blender.parent.parent.parent
    aliases = []
    if args.profile_source:
        aliases.append((str(args.profile_source), '<reference profile>'))
    aliases.extend(((str(app), '<reference app>'), (app.name, '<reference app>'),
                    (str(root), '<owned session>')))
    for index, crash in enumerate(sorted(root.rglob('*.crash.txt'))):
        assert crash.resolve().is_relative_to(root.resolve())
        content = crash.read_text(errors='replace')
        for value, alias in aliases:
            content = content.replace(value, alias)
        filename = 'sanitized-crash-' + str(index) + '.txt'
        destination = root / filename
        destination.write_text(content)
        retained.append({'file': filename, 'source_sha256': sha(crash),
                         'retained_sha256': sha(destination),
                         'process': {key: process.get(key) for key in
                                     ('pid', 'returncode', 'private_launch_log_sha256')}})
    return retained


def _run_session(args, root):
    runtime_driver = load_file('category_runtime_driver', REPO / 'tests/blender_keymap_runtime.py')
    before = protected_hashes(args.profile_source)
    environment = dict(os.environ)
    environment.pop('PYTHONPATH', None)
    environment.update(PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1',
                       PYTHONUNBUFFERED='1', DELUXE_CATEGORY_ROOT=str(root),
                       DELUXE_CATEGORY_MODE=args.mode, DELUXE_CATEGORY_REPO=str(REPO))
    if args.mode in ('ordinary_observe', 'ordinary_probe', 'ordinary_production', 'uv_arrow_probe', 'uv_arrow_production'):
        environment['DELUXE_CATEGORY_ORDINARY_CLUSTER'] = getattr(args, 'ordinary_cluster', 'axis')
        environment['DELUXE_CATEGORY_INVERT_ZOOM'] = str(getattr(args, 'invert_zoom', None))
    if args.mode in ('editor_observe', 'editor_probe', 'editor_production', 'persistence', 'reopen', 'editor_save', 'editor_reopen', 'uv_arrow_save', 'uv_arrow_reopen'):
        environment['DELUXE_CATEGORY_EDITOR_CLUSTER'] = getattr(args, 'editor_cluster', 'selection')
        environment['DELUXE_CATEGORY_EDITOR_INPUT_CONTROLS'] = '1' if getattr(args, 'editor_input_controls', False) else '0'
        environment['DELUXE_CATEGORY_EDITOR_PRIME_READINESS'] = '1' if getattr(args, 'editor_prime_readiness', False) else '0'
        environment['DELUXE_CATEGORY_EDITOR_MATCHED_ENDPOINTS'] = '1' if getattr(args, 'editor_matched_endpoints', False) else '0'
    for name in RESOURCE_NAMES:
        folder = root / name.lower()
        folder.mkdir()
        environment['BLENDER_USER_' + name] = str(folder)
    for name, folder in (('TMPDIR', 'tmp'), ('XDG_CACHE_HOME', 'cache')):
        (root / folder).mkdir()
        environment[name] = str(root / folder)
    minimum = tuple(map(int, args.test_minimum_version.split('.'))) if args.test_minimum_version else None
    runtime_driver.stage_package(root, minimum)
    package = root / 'scripts/addons' / PACKAGE
    # This reviewable new declaration may not be tracked until integrated checks
    # pass. Copy only the explicitly reserved production path, not arbitrary files.
    for name in PRODUCTION_PATHS:
        source = REPO / name
        if source.exists() and not (package / name).exists():
            (package / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, package / name)
    if args.provider_source:
        if any(p.is_symlink() for p in args.provider_source.rglob('*')):
            raise ValueError('Provider source contains an internal resource link')
        shutil.copytree(args.provider_source, root / 'scripts/addons/xray_selection_tools',
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        environment['DELUXE_CATEGORY_PROVIDER'] = 'xray_selection_tools'
    if args.incoming:
        shutil.copytree(args.incoming, root / 'incoming')
    executed = root / 'executed-native-test.py'
    shutil.copyfile(Path(__file__).resolve(), executed)
    if args.mode in ('handler_observe', 'handler_probe', 'circle_production'):
        shutil.copyfile(REPO / 'tests/blender_keymap_category03_handlers.py', root / 'handler-fixture.py')
    if args.mode in ('ordinary_observe', 'ordinary_probe', 'ordinary_production', 'uv_arrow_probe', 'uv_arrow_production'):
        shutil.copyfile(REPO / 'tests/blender_keymap_category03_ordinary.py', root / 'ordinary-fixture.py')
        shutil.copyfile(REPO / 'tests/fixtures/deluxe_keymaps/reconciliation-ledger.jsonl', root / 'ordinary-ledger.jsonl')
    if args.mode in ('editor_observe', 'editor_probe', 'editor_production', 'persistence', 'reopen', 'editor_save', 'editor_reopen', 'uv_arrow_production', 'uv_arrow_save', 'uv_arrow_reopen'):
        shutil.copyfile(REPO / 'tests/blender_keymap_category03_editors.py', root / 'editor-fixture.py')
    if args.mode in ('persistence', 'reopen', 'editor_save', 'editor_reopen', 'uv_arrow_save', 'uv_arrow_reopen'):
        shutil.copyfile(REPO / 'tests/blender_keymap_category03_persistence.py', root / 'persistence-fixture.py')
    policy = root / 'confinement.sb'
    policy.write_text('(version 1)\n(allow default)\n(deny network*)\n(deny file-write*)\n'
                      '(allow file-write* (subpath ' + json.dumps(str(root)) + '))\n'
                      '(allow file-write* (literal "/dev/null"))\n')
    command = ['/usr/bin/sandbox-exec', '-f', str(policy), str(args.blender),
               '--factory-startup', '--disable-autoexec', '--offline-mode',
               '--enable-event-simulate', '--python-exit-code', '1', '--python', str(executed),
               '--', '-ApplePersistenceIgnoreState', 'YES']
    source_hashes = {name: sha(package / name) for name in PRODUCTION_PATHS if (package / name).exists()}
    started = time.monotonic()
    child = None
    try:
        with (root / 'private-launch.log').open('w') as stream:
            child = subprocess.Popen(command, env=environment, stdout=stream, stderr=subprocess.STDOUT)
            try:
                returncode = child.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                child.terminate()
                try:
                    child.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
                returncode = 'timeout'
        result = {'mode': args.mode, 'pid': child.pid, 'returncode': returncode, 'child_exited': child.poll() is not None,
                  'seconds': round(time.monotonic() - started, 4), 'source_sha256': source_hashes,
                  'native_driver_sha256': sha(executed), 'protected_before': before,
                  'protected_after': protected_hashes(args.profile_source)}
        result['protected_unchanged'] = result['protected_before'] == result['protected_after']
        if (root / 'handler-fixture.py').exists():
            result['handler_fixture_sha256'] = sha(root / 'handler-fixture.py')
        if (root / 'ordinary-fixture.py').exists():
            result['ordinary_fixture_sha256'] = sha(root / 'ordinary-fixture.py')
            result['ordinary_ledger_sha256'] = sha(root / 'ordinary-ledger.jsonl')
        if (root / 'editor-fixture.py').exists():
            result['editor_fixture_sha256'] = sha(root / 'editor-fixture.py')
        if (root / 'persistence-fixture.py').exists():
            result['persistence_fixture_sha256'] = sha(root / 'persistence-fixture.py')
        result['private_launch_log_sha256'] = sha(root / 'private-launch.log')
        # Bind PID/exit/log even if parsing the native receipt itself fails.
        (root / 'process.json').write_text(json.dumps(result, indent=2) + '\n')
        native = root / 'native.json'
        result['native'] = json.loads(native.read_text()) if native.exists() else {'status': 'missing'}
        result['crash_retained_files'] = retain_crashes(root, args, result)
        result['crash_files_found'] = len(result['crash_retained_files'])
        # Keep only explicit saved fixtures needed by the next fresh process.
        if (root / 'saved-cases').exists():
            destination = args.output.resolve() / ('incoming-' + root.name)
            shutil.copytree(root / 'saved-cases', destination)
            result['next_reader_fixture'] = destination.name
        result['removed_resources'] = runtime_driver.cleanup_resources(root)
        (root / 'process.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'session': root.name, 'returncode': returncode,
                          'native_status': result['native'].get('status'),
                          'cases': len(result['native'].get('dispatch', [])),
                          'protected_unchanged': result['protected_unchanged'],
                          'removed_resources': result['removed_resources']}, indent=2))
        return 0 if returncode == 0 and result['native'].get('status') == 'complete' and result['protected_unchanged'] else 1
    finally:
        if child is not None and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=3)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


def launch(args):
    root = args.output.resolve() / (args.mode + '-' + str(time.time_ns()))
    root.mkdir(parents=True)
    before = protected_hashes(args.profile_source)
    try:
        return _run_session(args, root)
    finally:
        # Also cover staging/provider-copy/Popen failures before _run_session's
        # native-process try block. Only this invocation's exact owned roots go.
        process_path = root / 'process.json'
        process = json.loads(process_path.read_text()) if process_path.exists() else {}
        retained = retain_crashes(root, args, process)
        if retained:
            process['crash_retained_files'] = retained
            process['crash_files_found'] = len(retained)
            process_path.write_text(json.dumps(process, indent=2) + '\n')
        removed = []
        for name in (*[n.lower() for n in RESOURCE_NAMES], 'tmp', 'cache', 'incoming', 'saved-cases'):
            path = root / name
            if path.exists():
                shutil.rmtree(path)
                removed.append(name)
        after = protected_hashes(args.profile_source)
        (root / 'host-cleanup.json').write_text(json.dumps({
            'protected_before': before, 'protected_after': after,
            'protected_unchanged': before == after, 'final_removed_resources': removed,
            'remaining_resource_roots': [n.lower() for n in RESOURCE_NAMES if (root / n.lower()).exists()],
        }, indent=2) + '\n')
        assert before == after, 'Protected input changed'


def native_main(root, mode):
    import bpy
    import addon_utils
    from mathutils import Quaternion

    for name in RESOURCE_NAMES:
        actual = Path(bpy.utils.resource_path('USER') if name == 'RESOURCES'
                      else bpy.utils.user_resource(name)).resolve()
        assert actual == Path(os.environ['BLENDER_USER_' + name]).resolve()
        assert actual.is_relative_to(root)
    bpy.context.preferences.use_preferences_save = False
    sys.path.insert(0, str(root / 'scripts/addons'))
    bpy.utils.refresh_script_paths()
    exporter = load_file('category_exporter', REPO / 'tests/blender_keymap_baseline.py')
    receipt = {'schema_version': 1, 'mode': mode, 'status': 'running',
               'native': {'version': bpy.app.version_string, 'build': bpy.app.build_hash.decode(),
                          'background': bpy.app.background},
               'dispatch_method': 'Window.event_simulate through the owned GUI window',
               'steps': [], 'dispatch': [], 'invariants': []}
    start = time.monotonic()

    def record(label, **values):
        receipt['steps'].append({'label': label, 'seconds': round(time.monotonic() - start, 4), **values})
        (root / 'native.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print('CATEGORY03 ' + label, flush=True)

    if mode in ('reopen', 'uv_g_reopen', 'uv_g_production_reopen', 'editor_reopen', 'uv_arrow_reopen'):
        shutil.copyfile(root / 'incoming/userpref.blend', root / 'config/userpref.blend')
        bpy.ops.wm.read_userpref()
        bpy.context.preferences.use_preferences_save = False
    addon = addon_utils.enable(PACKAGE, default_set=True, persistent=False)
    assert addon is not None
    kmreg = addon.keymaps_register
    rt = kmreg.keymap_utils
    prefs = bpy.context.preferences.addons[PACKAGE].preferences
    configs = bpy.context.window_manager.keyconfigs
    window = bpy.context.window_manager.windows[0]
    area = next(a for a in window.screen.areas if a.type == 'VIEW_3D')
    state = {'sentinel': 0, 'wrapper_calls': []}
    sentinel_pairs = []
    steps = []
    uv_repeat_production = mode.startswith('uv_g_production')
    uv_repeat_reopen = mode in ('uv_g_reopen', 'uv_g_production_reopen')

    def region():
        return next(r for r in area.regions if r.type == 'WINDOW')

    def point():
        r = region()
        return r.x + r.width // 2, r.y + r.height // 2

    def override():
        return bpy.context.temp_override(window=window, area=area, region=region())

    def event(key, value='PRESS', *, dx=0, dy=0, **mods):
        x, y = point()
        window.event_simulate(type=key, value=value, x=x + dx, y=y + dy, **mods)

    def press(key, **mods):
        event('MOUSEMOVE', 'NOTHING')
        event(key, **mods)
        if 'WHEEL' not in key:
            event(key, 'RELEASE', **mods)

    class CATEGORY03_OT_sentinel(bpy.types.Operator):
        bl_idname = 'wm.deluxe_category03_sentinel'
        bl_label = 'Category input sentinel'

        def execute(self, context):
            state['sentinel'] += 1
            return {'FINISHED'}

    bpy.utils.register_class(CATEGORY03_OT_sentinel)

    def initialize():
        assert addon._keymaps_registered, addon._post_register_error
        if mode.startswith('uv_g_'):
            prefs.keymap.transform.enable_transform_action_shortcuts = False
        prefs.keymap.enable_keymaps = True
        prefs.pie.enable_pie_menus = False
        kmreg.refresh()
        keymap = configs.addon.keymaps.new(name='Window', space_type='EMPTY')
        sentinel_pairs.append((keymap, keymap.keymap_items.new(
            CATEGORY03_OT_sentinel.bl_idname, type='F24', value='PRESS')))
        configs.update()
        record('ready', runtime=rt.runtime_stats(), active_keyconfig=configs.active.name)

    def set_groups(navigation=False, selection=False, transform=False):
        prefs.keymap.navigation.enable_navigation_keymaps = navigation
        prefs.keymap.selection.enable_selection_keymaps = selection
        prefs.keymap.transform.enable_transform_keymaps = transform
        kmreg.refresh()
        configs.update()

    def pipeline_source_provenance(sources):
        # Prove both exact unrelated source identities from the live
        # ownership ledger and the category's registered native pairs.
        registered = kmreg.pipeline_keymaps_register.registered_pipeline_keymaps
        result = []
        for owner_id, handle in rt._FEATURES.items():
            if not owner_id.startswith('legacy:Pipeline:'):
                continue
            for request_id, owned in handle._owned.items():
                if owned.item.idname != 'wm.bh_save_as_mainfile':
                    continue
                valid = rt._valid_owned(owned)
                pair_matches = sum(rt._same(km, owned.map) and rt._same(item, owned.item)
                                   for km, item in registered)
                assert valid and pair_matches == 1
                assert rt._same(owned.config, configs.addon)
                scope = asdict(rt.capture_scope(owned.map))
                matches = [(i, j, row) for i, keymap in enumerate(sources['addon'])
                           if keymap['scope'] == scope
                           for j, row in enumerate(keymap['items'])
                           if row['blender_id'] == owned.item.id]
                assert len(matches) == 1
                index, position, row = matches[0]
                request = next(r for r in handle.assignments if r.request_id == request_id)
                assert request.target.idname == 'wm.bh_save_as_mainfile'
                result.append({'owner_id': owner_id, 'request_id': request_id,
                               'runtime_owned_valid': valid, 'registered_pair_matches': True,
                               'native_map_pointer': owned.map.as_pointer(),
                               'native_item_pointer': owned.item.as_pointer(),
                               'map_index': index, 'row_index': position,
                               'scope': scope, 'row': row, 'request': asdict(request)})
        assert len(result) == 2
        return sorted(result, key=lambda proof: (proof['map_index'], proof['row_index']))

    def owned_rows():
        result = {}
        for category in ('navigation', 'selection', 'transform'):
            module = getattr(kmreg, category + '_keymaps_register')
            pairs = getattr(module, 'registered_' + category + '_keymaps')
            result[category] = [{'scope': asdict(rt.capture_scope(km)),
                                'idname': item.idname, 'event': asdict(rt._event(item)),
                                'properties': dict(rt._target(item, False).properties)}
                               for km, item in pairs]
        return result

    def inspect():
        set_groups(True, True, True)
        receipt['owned_category_rows'] = owned_rows()
        receipt['diagnostics'] = [asdict(d) for d in rt.runtime_diagnostics()]
        names = {r['scope']['name'] for rows in receipt['owned_category_rows'].values() for r in rows}
        receipt['observed_scopes'] = {
            role: [asdict(rt.capture_scope(km)) for km in getattr(configs, role).keymaps if km.name in names]
            for role in ('default', 'addon', 'user')}
        for category in ('navigation', 'selection', 'transform'):
            before = owned_rows()
            group = getattr(prefs.keymap, category)
            setattr(group, 'enable_' + category + '_keymaps', False)
            kmreg.refresh()
            after = owned_rows()
            assert not after[category]
            assert all(after[c] == before[c] for c in before if c != category)
            setattr(group, 'enable_' + category + '_keymaps', True)
            kmreg.refresh()
            assert owned_rows() == before
        record('category_registration_and_toggle_isolation', counts={k: len(v) for k, v in owned_rows().items()})

    def schema_probe():
        import mathutils
        set_groups(False, False, False)
        known_math = tuple(getattr(mathutils, name) for name in ('Vector', 'Matrix', 'Quaternion', 'Euler'))
        array_type = getattr(bpy.types, 'bpy_prop_array', None)
        recognized = known_math + ((array_type,) if isinstance(array_type, type) else ())
        def numeric(value):
            if type(value) in (bool, int, float):
                return value
            if isinstance(value, recognized):
                return [numeric(v) for v in value]
            raise TypeError(type(value).__module__ + '.' + type(value).__name__)
        targets = ('transform.translate', 'transform.rotate', 'transform.resize',
                   'image.view_pan', 'clip.view_pan')
        receipt['property_schema'] = []
        for target in targets:
            matches = [(km, item) for km in configs.default.keymaps for item in km.keymap_items
                       if item.idname == target]
            assert matches, target
            km, item = next(((km, item) for km, item in matches if km.name == 'UV Editor'), matches[0])
            row = {'operator': target, 'source_scope': asdict(rt.capture_scope(km)),
                   'array_type_exposed': isinstance(array_type, type), 'properties': []}
            for prop in item.properties.bl_rna.properties:
                if prop.identifier == 'rna_type':
                    continue
                value = getattr(item.properties, prop.identifier)
                entry = {'name': prop.identifier, 'rna_type': prop.type,
                         'value_class': type(value).__module__ + '.' + type(value).__name__,
                         'is_array': getattr(prop, 'is_array', False),
                         'array_length': getattr(prop, 'array_length', 0),
                         'array_dimensions': list(getattr(prop, 'array_dimensions', ())) }
                if prop.type == 'ENUM':
                    entry['is_enum_flag'] = prop.is_enum_flag
                    entry['enum_identifiers'] = [item.identifier for item in prop.enum_items]
                    entry['native_value'] = sorted(value) if type(value) is set else value
                try:
                    rt._freeze(value)
                    entry['runtime_freeze'] = 'accepted'
                except Exception as exc:
                    entry['runtime_freeze'] = type(exc).__name__
                    try:
                        entry['numeric_probe_value'] = numeric(value)
                    except Exception as read_error:
                        entry['numeric_probe_error'] = str(read_error)
                row['properties'].append(entry)
            try:
                rt._properties(item)
                row['runtime_properties'] = 'accepted'
            except Exception as exc:
                row['runtime_properties'] = getattr(exc, 'reason', type(exc).__name__)
            receipt['property_schema'].append(row)
        record('exact_native_property_schema_observed')
        if any(row['runtime_properties'] != 'accepted' for row in receipt['property_schema']):
            record('assignment_probe_blocked_by_readback')
            return
        receipt['schema_assignments'] = []
        for target in targets:
            source_scope = next(row['source_scope'] for row in receipt['property_schema']
                                if row['operator'] == target)
            scope = rt.KeymapScope(**source_scope)
            if target.endswith('view_pan'):
                properties = {'offset': (1.25, -2.5)}
            else:
                properties = {'orient_matrix': ((1., 2., 0.), (0., 1., 3.), (0., 0., 1.)),
                              'constraint_axis': (False, True, False), 'snap_elements': ('VERTEX',)}
                properties['value'] = 0.25 if target == 'transform.rotate' else (1.25, 2.5, -3.75)
            default_map = next(km for km in configs.default.keymaps if rt.capture_scope(km) == scope)
            before = exporter._capture_map(default_map, bpy.types.OperatorProperties)
            probe_map = configs.addon.keymaps.new(name='Category03 Property Probe', space_type='EMPTY')
            probe_item = probe_map.keymap_items.new(target, type='F22', value='PRESS')
            try:
                for key, value in properties.items():
                    rt._set_property(probe_item, key, value)
                actual_properties = dict(rt._properties(probe_item))
                record('schema_explicit_property_control', operator=target,
                       requested=properties,
                       observed={key: actual_properties[key] for key in properties})
                if 'orient_matrix' in properties:
                    probe_item.properties.orient_matrix = mathutils.Matrix(properties['orient_matrix'])
                    record('typed_matrix_setter_control', operator=target,
                           requested=properties['orient_matrix'],
                           observed=dict(rt._properties(probe_item))['orient_matrix'])
            finally:
                probe_map.keymap_items.remove(probe_item)
                configs.addon.keymaps.remove(probe_map)
            request = rt.KeymapAssignment('schema-' + target, scope, rt.KeymapEvent('F22'),
                                          rt.KeymapTarget(target, properties), declared_properties_only=True)
            handle = rt.register_feature('category03-schema-' + target, assignments=(request,))
            try:
                assert len(handle.owned_pairs) == 1, handle.diagnostics
                own_map, own_item = handle.owned_pairs[0]
                actual = rt._target(own_item, False)
                assert all(dict(actual.properties)[key] == value for key, value in request.target.properties)
                merged = [(km, item) for km in configs.user.keymaps if rt.capture_scope(km) == scope
                          for item in km.keymap_items if item.idname == target and item.type == 'F22']
                assert len(merged) == 1
                assert rt._target(merged[0][1], False) == actual
                observed = {'operator': target, 'scope': source_scope,
                            'declared': dict(request.target.properties),
                            'complete_readback': dict(actual.properties),
                            'merged_readback_matches': True}
                if target in ('image.view_pan', 'transform.translate'):
                    key, value = ('offset', (3.5, -1.25)) if target == 'image.view_pan' else ('snap_elements', set())
                    setattr(own_item.properties, key, value)
                    handle.release()
                    assert rt.retained_edits()
                    assert own_item in tuple(own_map.keymap_items)
                    own_map.keymap_items.remove(own_item)
                    assert not rt.retained_edits()
                    observed['edited_source_retained_then_removed_by_fixture'] = key
            finally:
                handle.release()
            configs.update()
            after = exporter._capture_map(default_map, bpy.types.OperatorProperties)
            assert before == after
            observed['foreign_default_unchanged'] = True
            observed['released'] = not any(item.type == 'F22' and item.idname == target
                                           for km in configs.addon.keymaps if rt.capture_scope(km) == scope
                                           for item in km.keymap_items)
            assert observed['released']
            receipt['schema_assignments'].append(observed)
        for target, scope, properties in (
                ('image.view_pan', rt.KeymapScope('Image', 'IMAGE_EDITOR'), {'offset': (1.,)}),
                ('transform.translate', rt.KeymapScope('UV Editor'), {'snap_elements': ('NOT_A_FLAG',)}),
                ('transform.rotate', rt.KeymapScope('UV Editor'), {'value': 0.2})):
            before = rt.runtime_stats()['owned']
            invalid = rt.KeymapAssignment('invalid-' + target, scope, rt.KeymapEvent('F22'),
                                          rt.KeymapTarget(target, properties), declared_properties_only=True)
            handle = rt.register_feature('category03-invalid-' + target, assignments=(invalid,))
            assert not handle.owned_pairs, handle.diagnostics
            assert rt.runtime_stats()['owned'] == before
            receipt['schema_assignments'].append({'operator': target, 'invalid_rejected': True,
                                                  'diagnostics': [asdict(d) for d in handle.diagnostics]})
            handle.release()
        record('ordinary_numeric_and_flag_assignments_readback_release')

    def object_setup():
        area.type = 'VIEW_3D'
        with override():
            if bpy.context.object and bpy.context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            cube = bpy.data.objects.get('Cube')
            if cube is None:
                bpy.ops.mesh.primitive_cube_add()
                cube = bpy.context.object
                cube.name = 'Cube'
            for obj in bpy.context.scene.objects:
                obj.select_set(obj == cube)
            bpy.context.view_layer.objects.active = cube
            cube.location = (4, 2, 0)
            bpy.ops.wm.tool_set_by_id(name='builtin.select_box')
        view = area.spaces.active.region_3d
        view.view_rotation = Quaternion((0.712375879, 0.441062093, 0.287358254, 0.464122921))
        view.view_location = (0, 0, 0)
        view.view_distance = 25
        view.view_perspective = 'PERSP'

    def view_value():
        v = area.spaces.active.region_3d
        return {'rotation': list(v.view_rotation), 'location': list(v.view_location),
                'distance': v.view_distance, 'perspective': v.view_perspective,
                'selected': sorted(o.name for o in bpy.context.selected_objects)}

    def nav_case(label, key, *, mods=None, drag=None, tool='builtin.select_box'):
        before = {}

        def begin():
            object_setup()
            with override():
                bpy.ops.wm.tool_set_by_id(name=tool)
            before.update(view_value())
            before['tool'] = active_tool()
            if drag:
                event('MOUSEMOVE', 'NOTHING')
                event(key, **(mods or {}))
            else:
                press(key, **(mods or {}))

        def move():
            event('MOUSEMOVE', 'NOTHING', dx=drag[0], dy=drag[1], **(mods or {}))

        def release():
            event(key, 'RELEASE', dx=drag[0], dy=drag[1], **(mods or {}))

        def end():
            observed = view_value()
            observed['tool'] = active_tool()
            receipt['dispatch'].append({'case': label, 'key': key, 'modifiers': mods or {},
                                        'drag': drag, 'before': before, 'after': observed})
            record(label)

        steps.append(begin)
        if drag:
            steps.extend((move, release))
        steps.extend((lambda: None, end))

    def active_tool():
        with override():
            tool = bpy.context.workspace.tools.from_space_view3d_mode(bpy.context.mode, create=False)
            return tool.idname if tool else None

    def q_case(label, kind='object'):
        before = {}

        def begin():
            try:
                if kind == 'object':
                    object_setup()
                else:
                    selection_setup(kind)
                with override():
                    bpy.ops.wm.tool_set_by_id(name='builtin.move')
                if state.get('q_probe_requested_scopes'):
                    # Preference/provider refresh can intentionally release all
                    # runtime owners. Reinstall this experiment immediately
                    # before its event; never mistake a released probe for a
                    # dispatch failure in a different provider state.
                    q_press_probe(state['q_probe_requested_scopes'])
                before['tool'] = active_tool()
                before['probe_owned'] = len(state['q_press_probe'].owned_pairs) if state.get('q_probe_requested_scopes') else 0
                state['wrapper_calls'].clear()
                press('Q')
            except Exception:
                before['fixture_error'] = traceback.format_exc()

        def end():
            if 'fixture_error' in before:
                receipt['dispatch'].append({'case': label, 'kind': kind, 'status': 'fixture_error',
                                            'error': before['fixture_error']})
                record(label)
                return
            receipt['dispatch'].append({'case': label, 'before_tool': before['tool'],
                                        'kind': kind,
                                        'probe_owned_before_input': before['probe_owned'],
                                        'after_tool': active_tool(),
                                        'wrapper_calls': list(state['wrapper_calls']),
                                        'operator_history': [o.bl_idname for o in bpy.context.window_manager.operators]})
            record(label)
            press('ESC')

        steps.extend((begin, lambda: None, end))

    def trace_q_wrappers():
        module = sys.modules[PACKAGE + '.operators.box_xray_ops']
        codes = {cls.execute.__code__: cls.bl_idname for cls in module.classes}
        state['tracked_codes'] = codes
        state['previous_profile'] = sys.getprofile()
        def trace(frame, event, result):
            if event == 'return' and frame.f_code in codes:
                state['wrapper_calls'].append({'operator': codes[frame.f_code],
                                               'result': sorted(result) if isinstance(result, set) else str(result)})
        # Observe the existing Python callback; never replace a method of a live
        # Blender-registered class. The first experiment doing so crashed before
        # recording a Q result and is explicitly retained as a failed attempt.
        sys.setprofile(trace)
        # Quick Favorites is a native menu rather than a Python Menu type on
        # this build. Record its candidate binding without inventing draw hooks
        # or treating registration as evidence that it won dispatch.
        receipt['q_candidates'] = [
            {'scope': km.name, 'operator': item.idname, 'value': item.value}
            for km in configs.user.keymaps for item in km.keymap_items
            if item.type == 'Q' and item.active and not any((item.shift, item.ctrl, item.alt, item.oskey))
            and km.name in ('Screen', '3D View', 'Object Mode')]
        object_setup()
        with override():
            bpy.ops.wm.tool_set_by_id(name='builtin.move')
            bpy.ops.wm.bh_tool_select_box_xray_object()
        assert state['wrapper_calls'], 'Wrapper instrumentation did not observe direct invocation control'
        record('q_instrumentation_control', calls=list(state['wrapper_calls']), tool=active_tool(),
               method='Direct invocation validates instrumentation only, not shortcut dispatch')

    def reset_objects():
        area.type = 'VIEW_3D'
        with override():
            if bpy.context.object and bpy.context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            for obj in tuple(bpy.context.scene.objects):
                bpy.data.objects.remove(obj, do_unlink=True)

    def selection_setup(kind):
        """Build test data with direct calls; tested selection uses native events."""
        reset_objects()
        if kind == 'object':
            parent = bpy.data.objects.new('Category Parent', None)
            child = bpy.data.objects.new('Category Child', None)
            bpy.context.collection.objects.link(parent)
            bpy.context.collection.objects.link(child)
            child.parent = parent
            child.select_set(True)
            bpy.context.view_layer.objects.active = child
            return lambda: sorted(o.name for o in bpy.context.selected_objects)
        if kind in ('mesh', 'uv'):
            import bmesh
            with override():
                bpy.ops.mesh.primitive_grid_add(x_subdivisions=4, y_subdivisions=4)
                obj = bpy.context.object
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.context.tool_settings.mesh_select_mode = (True, False, False)
                bm = bmesh.from_edit_mesh(obj.data)
                bm.verts.ensure_lookup_table()
                for v in bm.verts:
                    v.select_set(v.index == len(bm.verts) // 2)
                bm.select_flush_mode()
                bmesh.update_edit_mesh(obj.data)
            if kind == 'mesh':
                return lambda: sorted(v.index for v in bmesh.from_edit_mesh(obj.data).verts if v.select)
            with override():
                bpy.ops.mesh.select_all(action='SELECT')
            bm = bmesh.from_edit_mesh(obj.data)
            uv = bm.loops.layers.uv.verify()
            prefs_ui = bpy.context.scene.tool_settings
            prefs_ui.use_uv_select_sync = False
            for face in bm.faces:
                face.select = True
                for loop in face.loops:
                    loop[uv].select = face.index == 0
            bmesh.update_edit_mesh(obj.data)
            area.type = 'IMAGE_EDITOR'
            area.ui_type = 'UV'
            return lambda: [(f.index, i) for f in bmesh.from_edit_mesh(obj.data).faces
                            for i, loop in enumerate(f.loops) if loop[uv].select]
        if kind == 'curve':
            data = bpy.data.curves.new('Category Curve', 'CURVE')
            data.dimensions = '3D'
            spline = data.splines.new('POLY')
            spline.points.add(4)
            for i, p in enumerate(spline.points):
                p.co = (i, 0, 0, 1)
                p.select = i == 2
            obj = bpy.data.objects.new('Category Curve', data)
            bpy.context.collection.objects.link(obj)
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            with override():
                bpy.ops.object.mode_set(mode='EDIT')
            def read_curve_selection():
                # Legacy Curve edit data is flushed to the RNA splines when
                # leaving Edit mode; reading the original spline can be stale.
                with override():
                    bpy.ops.object.mode_set(mode='OBJECT')
                    result = [i for i, p in enumerate(data.splines[0].points) if p.select]
                    bpy.ops.object.mode_set(mode='EDIT')
                return result
            return read_curve_selection
        if kind == 'curves':
            data = bpy.data.hair_curves.new('Category Curves')
            data.add_curves([5])
            for i, point in enumerate(data.attributes['position'].data):
                point.vector = (i, 0, 0)
            selected = data.attributes.get('.selection') or data.attributes.new('.selection', 'BOOLEAN', 'POINT')
            for i, value in enumerate(selected.data):
                value.value = i == 2
            if hasattr(data, 'selection_domain'):
                data.selection_domain = 'POINT'
            obj = bpy.data.objects.new('Category Curves', data)
            bpy.context.collection.objects.link(obj)
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            with override():
                bpy.ops.object.mode_set(mode='EDIT')
            return lambda: [i for i, p in enumerate(data.attributes['.selection'].data) if p.value]
        if kind == 'lattice':
            data = bpy.data.lattices.new('Category Lattice')
            data.points_u = data.points_v = data.points_w = 3
            obj = bpy.data.objects.new('Category Lattice', data)
            bpy.context.collection.objects.link(obj)
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            for i, p in enumerate(data.points):
                p.select = i == len(data.points) // 2
            with override():
                bpy.ops.object.mode_set(mode='EDIT')
            return lambda: [i for i, p in enumerate(data.points) if p.select]
        if kind == 'armature':
            data = bpy.data.armatures.new('Category Armature')
            obj = bpy.data.objects.new('Category Armature', data)
            bpy.context.collection.objects.link(obj)
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            with override():
                bpy.ops.object.mode_set(mode='EDIT')
                previous = None
                for i in range(5):
                    bone = data.edit_bones.new('Bone ' + str(i))
                    bone.head, bone.tail = (0, 0, i), (0, 0, i + 1)
                    if previous:
                        bone.parent, bone.use_connect = previous, True
                    previous = bone
                for i, bone in enumerate(data.edit_bones):
                    bone.select = bone.select_head = bone.select_tail = i == 2
            return lambda: [b.name for b in data.edit_bones if b.select]
        if kind in ('dopesheet', 'graph'):
            obj = bpy.data.objects.new('Category Animated', None)
            bpy.context.collection.objects.link(obj)
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            for frame in (1, 10, 20, 30, 40):
                obj.location.x = frame / 10
                obj.keyframe_insert(data_path='location', index=0, frame=frame)
            curves = obj.animation_data.action.fcurves
            for curve in curves:
                curve.select = True
                for i, key in enumerate(curve.keyframe_points):
                    key.select_control_point = key.select_left_handle = key.select_right_handle = i == 2
            area.type = 'DOPESHEET_EDITOR' if kind == 'dopesheet' else 'GRAPH_EDITOR'
            if kind == 'dopesheet':
                area.spaces.active.mode = 'DOPESHEET'
            return lambda: [(i, j) for i, c in enumerate(curves) for j, k in enumerate(c.keyframe_points)
                            if k.select_control_point]
        if kind == 'node':
            area.type = 'NODE_EDITOR'
            area.ui_type = 'CompositorNodeTree'
            scene = bpy.context.scene
            scene.use_nodes = True
            tree = scene.node_tree
            tree.nodes.clear()
            nodes = [tree.nodes.new('CompositorNodeMath') for _ in range(3)]
            for i, node in enumerate(nodes):
                node.location = (i * 200, 0)
                node.select = i == 1
            for a, b in zip(nodes, nodes[1:]):
                tree.links.new(a.outputs[0], b.inputs[0])
            tree.nodes.active = nodes[1]
            return lambda: [i for i, n in enumerate(nodes) if n.select]
        if kind == 'sequencer':
            scene = bpy.context.scene
            editor = scene.sequence_editor_create()
            strips = [editor.strips.new_effect('Category Strip ' + str(i), type='COLOR', channel=1,
                                               frame_start=1 + i * 10, frame_end=11 + i * 10)
                      for i in range(3)]
            for i, strip in enumerate(strips):
                strip.select = i == 1
            editor.active_strip = strips[1]
            area.type = 'SEQUENCE_EDITOR'
            area.spaces.active.view_type = 'SEQUENCER'
            return lambda: [i for i, s in enumerate(strips) if s.select]
        if kind == 'mask':
            area.type = 'IMAGE_EDITOR'
            area.spaces.active.mode = 'MASK'
            mask = bpy.data.masks.new('Category Mask')
            layer = mask.layers.new(name='Category Layer')
            spline = layer.splines.new()
            spline.points.add(4)
            for i, point in enumerate(spline.points):
                point.co = (0.15 + i * 0.15, 0.5)
                point.select = point.select_left_handle = point.select_right_handle = i == 2
            area.spaces.active.mask = mask
            area.spaces.active.image = (bpy.data.images.get('Category Mask Image') or
                                       bpy.data.images.new('Category Mask Image', width=512, height=512))
            return lambda: [i for i, p in enumerate(spline.points) if p.select]
        raise ValueError('Unsupported fixture: ' + kind)

    def selection_case(kind, key, *, shift=True, control=False):
        values = {}

        def prepare():
            try:
                values['read'] = selection_setup(kind)
            except Exception:
                values['setup_error'] = traceback.format_exc()

        def begin():
            if 'setup_error' in values:
                return
            values['before'] = values['read']()
            values['editor'] = area.type
            values['mode'] = bpy.context.mode
            if control:
                r = region()
                values['view_before'] = (list(r.view2d.region_to_view(r.width / 2, r.height / 2))
                                         if area.type != 'VIEW_3D' else None)
            press(key, shift=shift)

        def end():
            row = {'case': 'more_less_' + kind + '_' + key, 'key': key, 'shift': shift}
            if 'setup_error' in values:
                row.update(status='fixture_error', error=values['setup_error'])
            else:
                after = values['read']()
                row.update(status='observed', editor=values['editor'], context_mode=values['mode'],
                           before=values['before'], after=after, changed=after != values['before'])
                if control:
                    r = region()
                    row['view_before'] = values['view_before']
                    row['view_after'] = (list(r.view2d.region_to_view(r.width / 2, r.height / 2))
                                          if area.type != 'VIEW_3D' else None)
                    row['candidates'] = [
                        {'scope': km.name, 'row': item}
                        for km in configs.user.keymaps
                        if km.name in ('View2D', 'Mesh', 'Curve', 'Dopesheet', 'Graph Editor', 'Node Editor', 'Sequencer', 'Mask Editing')
                        for item in exporter._capture_map(km, bpy.types.OperatorProperties)['items']
                        if item['event']['type'] == key and item['event']['shift'] == 1]
                    targets = {'mesh': ('mesh', 'select_more', 'select_less'),
                               'curve': ('curve', 'select_more', 'select_less'),
                               'dopesheet': ('action', 'select_more', 'select_less'),
                               'graph': ('graph', 'select_more', 'select_less'),
                               'node': ('node', 'select_linked_to', 'select_linked_from'),
                               'sequencer': ('sequencer', 'select_more', 'select_less'),
                               'mask': ('mask', 'select_more', 'select_less')}
                    module, more, less = targets[kind]
                    with override():
                        result = getattr(getattr(bpy.ops, module), more if key == 'WHEELUPMOUSE' else less)()
                    row['direct_control'] = {'result': sorted(result), 'after': values['read'](),
                                             'method': 'Direct execution tests fixture/operator, not shortcut dispatch'}
            receipt['dispatch'].append(row)
            record(row['case'])

        steps.extend((prepare, lambda: None, begin, lambda: None, end))

    def selection_all_none_case(*, shift=False, oskey=False):
        values = {}
        def prepare():
            values['read'] = selection_setup('uv')
        def begin():
            values['before'] = values['read']()
            press('A', shift=shift, ctrl=not oskey, oskey=oskey)
        def end():
            after = values['read']()
            receipt['dispatch'].append({'case': 'uv_' + ('deselect_all' if shift else 'select_all')
                                        + ('_cmd' if oskey else '_ctrl'),
                                        'before': values['before'], 'after': after,
                                        'changed': after != values['before']})
            record('uv_all_none_observed')
            press('ESC')
        steps.extend((prepare, lambda: None, begin, lambda: None, end))

    def selection_all_none_isolation():
        before = owned_rows()
        defaults = [exporter._capture_map(km, bpy.types.OperatorProperties)
                    for km in configs.default.keymaps if km.name == 'UV Editor']
        all_none = [r for r in before['selection'] if r['idname'] == 'uv.select_all']
        assert len(all_none) == 4
        prefs.keymap.selection.enable_selection_all_none = False
        kmreg.refresh()
        off = owned_rows()
        assert not any(r['idname'] == 'uv.select_all' for r in off['selection'])
        assert off['selection'] == [r for r in before['selection'] if r['idname'] != 'uv.select_all']
        assert all(off[c] == before[c] for c in ('navigation', 'transform'))
        prefs.keymap.selection.enable_selection_all_none = True
        kmreg.refresh()
        assert owned_rows() == before
        assert defaults == [exporter._capture_map(km, bpy.types.OperatorProperties)
                            for km in configs.default.keymaps if km.name == 'UV Editor']
        receipt['invariants'].append({'case': 'selection_all_none_toggle_isolation',
                                      'owned_bindings': 4, 'other_groups_unchanged': True,
                                      'foreign_default_unchanged': True, 'restored': True})
        record('selection_all_none_toggle_isolation')

    def transform_setup(gizmo=False):
        object_setup()
        cube = bpy.context.object
        cube.location = (0, 0, 0)
        cube.rotation_euler = (0, 0, 0)
        cube.scale = (1, 1, 1)
        if gizmo:
            with override():
                bpy.ops.wm.tool_set_by_id(name='builtin.move')

    def transform_value():
        obj = bpy.context.object
        return {'location': list(obj.location), 'rotation': list(obj.rotation_euler),
                'scale': list(obj.scale), 'tool': active_tool()}

    def transform_case(key, *, shift=False, gizmo=False):
        values = {}

        def begin():
            transform_setup(gizmo)
            values['before'] = transform_value()
            press(key, shift=shift)

        def move():
            event('MOUSEMOVE', 'NOTHING', dx=90, dy=40)

        def observe_moving():
            values['during'] = transform_value()

        def confirm():
            # press() also recenters the pointer, which would reset a mouse
            # transform before confirming. Preserve the displaced position.
            event('RET', dx=90, dy=40)
            event('RET', 'RELEASE', dx=90, dy=40)

        def end():
            receipt['dispatch'].append({'case': 'transform_' + key + ('_gizmo_active' if gizmo else '')
                                        + ('_shift' if shift else ''), 'key': key, 'shift': shift,
                                        'before': values['before'], 'during': values.get('during'),
                                        'after': transform_value(),
                                        'operator_history': [o.bl_idname for o in bpy.context.window_manager.operators]})
            record('transform_' + key + ('_shift' if shift else ''))
            press('ESC')

        steps.append(begin)
        if not shift:
            steps.extend((move, observe_moving, confirm))
        steps.extend((lambda: None, end))

    def context_menu_case():
        def callback(self, context):
            state['context_menu_draws'] = state.get('context_menu_draws', 0) + 1
        def begin():
            transform_setup(gizmo=True)
            state['context_menu_draws'] = 0
            bpy.types.VIEW3D_MT_object_context_menu.append(callback)
            state['menu_callbacks'] = [(bpy.types.VIEW3D_MT_object_context_menu, callback)]
            press('RIGHTMOUSE')
        def end():
            receipt['dispatch'].append({'case': 'object_context_menu_with_active_move_gizmo',
                                        'menu_draws': state['context_menu_draws'],
                                        'tool': active_tool()})
            press('ESC')
            record('object_context_menu_with_active_move_gizmo')
        steps.extend((begin, lambda: None, end))

    def face_case():
        import bmesh
        from bpy_extras.view3d_utils import location_3d_to_region_2d
        values = {}
        def prepare():
            transform_setup(gizmo=True)
            with override():
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.wm.tool_set_by_id(name='builtin.move')
                bpy.context.tool_settings.mesh_select_mode = (False, False, True)
                bm = bmesh.from_edit_mesh(bpy.context.object.data)
                bm.faces.ensure_lookup_table()
                for f in bm.faces:
                    f.select = f.normal.x > 0.9
                bmesh.update_edit_mesh(bpy.context.object.data)
                target = next(f for f in bm.faces if f.normal.z > 0.9)
                values['target'] = target.index
                values['before'] = [f.index for f in bm.faces if f.select]
                values['before_tool'] = active_tool()
                location = bpy.context.object.matrix_world @ target.calc_center_median()
                point_2d = location_3d_to_region_2d(region(), area.spaces.active.region_3d, location)
                assert point_2d is not None
                values['point'] = (int(region().x + point_2d.x), int(region().y + point_2d.y))
        def click():
            x, y = values['point']
            for key, value in (('MOUSEMOVE', 'NOTHING'), ('LEFTMOUSE', 'PRESS'), ('LEFTMOUSE', 'RELEASE')):
                window.event_simulate(type=key, value=value, x=x, y=y)
        def end():
            bm = bmesh.from_edit_mesh(bpy.context.object.data)
            receipt['dispatch'].append({'case': 'mesh_face_select_with_active_move_gizmo',
                                        'before': values['before'], 'target_face': values['target'],
                                        'before_tool': values['before_tool'],
                                        'after': [f.index for f in bm.faces if f.select], 'tool': active_tool()})
            record('mesh_face_select_with_active_move_gizmo')
        steps.extend((prepare, lambda: None, click, lambda: None, end))

    def image_value():
        r = region()
        center = r.view2d.region_to_view(r.width / 2, r.height / 2)
        return {'zoom': list(area.spaces.active.zoom), 'view_center': list(center),
                'selected_uv': state['uv_read']()}

    def uv_transform_case(key, *, shift=False, prior_rotation=False,
                          prior_translation=False, expectation=None):
        import bmesh
        values = {}
        prior_transform = prior_rotation or prior_translation
        control_target = 'transform.translate' if prior_translation else 'transform.rotate'
        control_history = 'TRANSFORM_OT_translate' if prior_translation else 'TRANSFORM_OT_rotate'
        def read():
            bm = bmesh.from_edit_mesh(bpy.data.objects[state['uv_object_name']].data)
            uv = bm.loops.layers.uv.active
            tool = bpy.context.workspace.tools.from_space_image_mode('UV', create=False)
            return {'selected_positions': [[f.index, i, *loop[uv].uv]
                                           for f in bm.faces for i, loop in enumerate(f.loops)
                                           if loop[uv].select],
                    'tool': tool.idname if tool else None}
        def prepare():
            selection_setup('uv')
            state['uv_object_name'] = bpy.context.object.name
            with override():
                bpy.ops.wm.tool_set_by_id(name='builtin.select_box')
                bpy.ops.image.view_all()
                if prior_transform:
                    bm = bmesh.from_edit_mesh(bpy.data.objects[state['uv_object_name']].data)
                    uv = bm.loops.layers.uv.active
                    values['original_uv'] = [(fi, li, tuple(loop[uv].uv))
                                             for fi, f in enumerate(bm.faces) for li, loop in enumerate(f.loops)]
                    values['control_before'] = read()
        def control_begin():
            assert not any(i.type == 'F23' for km in configs.user.keymaps for i in km.keymap_items)
            keymap = configs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
            item = keymap.keymap_items.new(control_target, type='F23', value='PRESS')
            state['g_control_binding'] = (keymap, item)
            configs.update()
            receipt['g_control_binding'] = {'event': 'F23/PRESS', 'target': control_target,
                                             'scope': 'UV Editor', 'fixture_owned': True}
            merged = [(km, row) for km in configs.user.keymaps
                      if km.name == 'UV Editor' and km.space_type == 'EMPTY' and km.region_type == 'WINDOW'
                      for row in km.keymap_items if row.idname == control_target and row.type == 'F23'
                      and row.value == 'PRESS' and row.active
                      and not any((row.shift, row.ctrl, row.alt, row.oskey, row.any))]
            receipt['g_control_binding']['exact_merged_occurrences'] = len(merged)
            assert len(merged) == 1, 'Temporary rotation control was not admitted to the effective UV map'
            km, row = merged[0]
            captured = exporter._capture_map(km, bpy.types.OperatorProperties)
            receipt['g_control_binding']['merged_scope'] = captured['scope']
            receipt['g_control_binding']['merged_row'] = next(v for v in captured['items'] if v['blender_id'] == row.id)
            press('F23')
        def control_move():
            # A native numeric angle avoids a zero-effect mouse rotation when
            # the incoming event position happens to align with the UV pivot.
            if prior_translation:
                event('X')
                event('X', 'RELEASE')
            digits = (('ZERO', '0'), ('PERIOD', '.'), ('TWO', '2'), ('FIVE', '5')) if prior_translation else (('NINE', '9'), ('ZERO', '0'))
            for key, character in digits:
                event(key, unicode=character)
                event(key, 'RELEASE')
        def control_confirm():
            event('RET')
            event('RET', 'RELEASE')
        def control_restore():
            values['control_after'] = read()
            values['history_before_g'] = [o.bl_idname for o in bpy.context.window_manager.operators]
            receipt['uv_g_control'] = {k: values[k] for k in ('control_before', 'control_after', 'history_before_g')}
            receipt['uv_g_control']['method'] = ('native fixture-owned F23 translate, X 0.25, Return'
                                                if prior_translation else 'native fixture-owned F23 rotate, numeric 90, Return')
            keymap, item = state.pop('g_control_binding')
            keymap.keymap_items.remove(item)
            configs.update()
            receipt['g_control_binding']['removed_before_g'] = True
            record('uv_g_rotation_control_observed')
            assert values['control_after']['selected_positions'] != values['control_before']['selected_positions'], 'Rotation control did not affect UV coordinates'
            assert values['history_before_g'][-1:] == [control_history], values['history_before_g']
            obj = bpy.data.objects[state['uv_object_name']]
            bm = bmesh.from_edit_mesh(obj.data)
            bm.faces.ensure_lookup_table()
            uv = bm.loops.layers.uv.active
            for fi, li, position in values.pop('original_uv'):
                bm.faces[fi].loops[li][uv].uv = position
            bmesh.update_edit_mesh(obj.data)
        def begin():
            values['before'] = read()
            values['history_before_input'] = [o.bl_idname for o in bpy.context.window_manager.operators]
            with override():
                values['repeat_poll_before_input'] = bpy.ops.screen.repeat_last.poll()
            if expectation == 'empty_history':
                assert not values['history_before_input'], 'Empty-history fixture is not empty'
            press(key, shift=shift)
        def after_key():
            values['after_key'] = read()
        def move():
            event('MOUSEMOVE', 'NOTHING', dx=70, dy=30)
        def confirm():
            values['during'] = read()
            event('RET', dx=70, dy=30)
            event('RET', 'RELEASE', dx=70, dy=30)
        def end():
            observed = {'case': 'uv_transform_' + key + ('_shift' if shift else '')
                                        + ('_after_known_rotate' if prior_rotation else '')
                                        + ('_after_known_translate' if prior_translation else ''),
                                        'key': key, 'shift': shift, 'before': values['before'],
                                        'during': values.get('during'), 'after': read(),
                                        'after_key': values.get('after_key'),
                                        'expectation': expectation,
                                        'history_before_input': values['history_before_input'],
                                        'repeat_poll_before_input': values['repeat_poll_before_input'],
                                        'history_after_input': [o.bl_idname for o in bpy.context.window_manager.operators],
                                        'prior_rotation_control': {k: v for k, v in values.items()
                                                                   if k in ('control_before', 'control_after', 'history_before_g')}}
            receipt['dispatch'].append(observed)
            record('uv_transform_' + key + ('_shift' if shift else ''))
            def equal_positions(left, right):
                return len(left) == len(right) and all(
                    a[:2] == b[:2] and all(abs(x-y) < 1e-6 for x, y in zip(a[2:], b[2:]))
                    for a, b in zip(left, right))
            before = observed['before']['selected_positions']
            immediate = observed['after_key']['selected_positions']
            after = observed['after']['selected_positions']
            if expectation == 'single_repeat':
                expected = values['control_after']['selected_positions']
                assert observed['repeat_poll_before_input']
                assert equal_positions(immediate, expected), 'G did not immediately repeat exactly once'
                assert equal_positions(after, expected), 'Mouse motion started a fresh transform after repeat'
            elif expectation == 'translate' or (expectation == 'empty_history' and not observed['repeat_poll_before_input']):
                assert equal_positions(immediate, before)
                deltas = [[b-a for a, b in zip(old[2:], new[2:])] for old, new in zip(before, after)]
                assert any(abs(v) > 1e-6 for v in deltas[0]), 'Fallback Translate had no effect'
                assert all(all(abs(a-b) < 1e-6 for a, b in zip(delta, deltas[0])) for delta in deltas)
            elif expectation == 'move_tool':
                assert observed['after']['tool'] == 'builtin.move'
                assert equal_positions(after, before)
            press('ESC')
        steps.extend((prepare, lambda: None))
        if prior_transform:
            steps.extend((control_begin, control_move, control_confirm, lambda: None, control_restore))
        steps.extend((begin, after_key))
        if not shift:
            steps.extend((move, confirm))
        steps.extend((lambda: None, end))

    def image_case(key, mods, drag=None):
        values = {}
        def prepare():
            state['uv_read'] = selection_setup('uv')
            image = bpy.data.images.get('Category Image') or bpy.data.images.new('Category Image', width=512, height=512)
            area.spaces.active.image = image
            with override():
                bpy.ops.image.view_zoom_ratio(ratio=2.0)
        def begin():
            values['before'] = image_value()
            if drag:
                event('MOUSEMOVE', 'NOTHING')
                event(key, **mods)
            else:
                press(key, **mods)
        def end():
            receipt['dispatch'].append({'case': 'image_' + key + ('_drag' if drag else ''),
                                        'modifiers': mods, 'before': values['before'], 'after': image_value()})
            record('image_' + key)
        steps.extend((prepare, lambda: None, begin))
        if drag:
            steps.extend((lambda: event('MOUSEMOVE', 'NOTHING', dx=drag[0], dy=drag[1], **mods),
                          lambda: event(key, 'RELEASE', dx=drag[0], dy=drag[1], **mods)))
        steps.extend((lambda: None, end))

    def uv_repeat_sources():
        """Exact snapshots at endpoints where the fixture assignment is absent."""
        return {
            role: [exporter._capture_map(km, bpy.types.OperatorProperties)
                   for km in getattr(configs, role).keymaps
                   if km.name in ('UV Editor', 'Image', 'Screen')]
            for role in ('default', 'active', 'addon', 'user')
        }

    def uv_repeat_matches():
        return [(km, item) for km in configs.user.keymaps
                if km.name == 'UV Editor' and km.space_type == 'EMPTY'
                and km.region_type == 'WINDOW'
                for item in km.keymap_items if item.idname == 'screen.repeat_last']

    def uv_repeat_request():
        if not uv_repeat_production:
            return 'category03:uv-repeat-probe', rt.KeymapAssignment(
                'uv-repeat-g', rt.KeymapScope('UV Editor', 'EMPTY', 'WINDOW'),
                rt.KeymapEvent('G', repeat=True), rt.KeymapTarget(idname='screen.repeat_last'),
                declared_properties_only=True)
        # Derive the expected identity from the real public declaration. Only
        # the category register below creates/releases its production handle.
        adapter = importlib.import_module(PACKAGE + '.keymaps.keymap_action_utils')
        actions = kmreg.transform_keymaps_register.get_transform_action_shortcuts()
        assert len(actions) == 1 and len(actions[0].keymap_bindings) == 1
        action = actions[0]
        binding = action.keymap_bindings[0]
        request = rt.KeymapAssignment(
            f'0:{binding.keymap_name}:{binding.key}:{binding.value}',
            adapter._binding_scope(binding, configs.addon), adapter._event(binding),
            rt.KeymapTarget(idname=action.get_idname(), properties=action.get_props(bpy.context)),
            declared_properties_only=True, active=binding.active)
        owner = 'legacy:Transform:' + hashlib.sha256(repr((request,)).encode('utf-8')).hexdigest()
        return owner, request

    def uv_repeat_start():
        selection_setup('uv')
        with override():
            bpy.ops.wm.tool_set_by_id(name='builtin.select_box')
            bpy.ops.image.view_all()
        configs.update()
        owner, request = uv_repeat_request()
        if uv_repeat_reopen:
            incoming = json.loads((root / 'incoming/uv-repeat-expected.json').read_text())
            assert incoming['preference_sha256'] == sha(root / 'incoming/userpref.blend')
            assert incoming['owner'] == owner
            assert incoming['request_id'] == request.request_id
            assert incoming['expected_edit'] == {'event': 'F20/PRESS', 'active': False, 'repeat': True}
            state['uv_repeat_incoming_manifest'] = incoming
        assert not uv_repeat_matches(), 'Existing UV repeat row would make the owned probe ambiguous'
        if uv_repeat_production:
            # A category refresh legitimately recreates its own W/E/R items.
            # Compare their declarations separately; compare all foreign raw
            # snapshots with Transform absent at both endpoints, without
            # discarding IDs or other fields from any foreign row.
            state['uv_other_transform_rows'] = owned_rows()['transform']
            set_groups(False, False, False)
        receipt['uv_repeat_probe'] = {
            'status': ('actual production Transform Actions toggle' if uv_repeat_production
                       else 'isolated fixture; production Actions disabled'),
            'owner': owner, 'request_id': request.request_id,
            'production_identity': uv_repeat_production,
            'stock_uv_selector': 'a617d6ba7bffe5931c516dd6f7be58620c8bc146f29634ef62a12c2935a891da',
            'owner05_screen_row': '404d0973700b95f4354799748f01445ff8aefb0031509c88fa0c71647bdcfd2b',
            'source_and_foreign_merged_before': uv_repeat_sources(),
            'installations': [], 'releases': [],
        }
        if uv_repeat_production:
            receipt['uv_repeat_probe']['preservation_endpoint'] = 'Transform category off at both complete snapshot endpoints'
            receipt['uv_repeat_probe']['other_transform_declarations'] = state['uv_other_transform_rows']
            set_groups(False, False, True)
            assert owned_rows()['transform'] == state['uv_other_transform_rows']
        if 'uv_repeat_incoming_manifest' in state:
            receipt['uv_repeat_probe']['verified_incoming_manifest'] = state['uv_repeat_incoming_manifest']

    def uv_repeat_owned_source():
        pairs = state['uv_repeat_handle'].owned_pairs
        assert len(pairs) == 1
        keymap, item = pairs[0]
        captured = exporter._capture_map(keymap, bpy.types.OperatorProperties)
        return {'scope': captured['scope'], 'row': next(row for row in captured['items']
                                                       if row['blender_id'] == item.id)}

    def uv_repeat_item_fields(keymap, item):
        values = {}
        for field in ('id', 'idname', 'type', 'value', 'active', 'repeat',
                      'is_user_modified', 'is_user_defined'):
            try:
                values[field] = getattr(item, field)
            except (AttributeError, ReferenceError, RuntimeError) as error:
                values[field] = {'read_error': type(error).__name__}
        try:
            values['map_is_user_modified'] = keymap.is_user_modified
            values['item_pointer'] = item.as_pointer()
        except (ReferenceError, RuntimeError) as error:
            values['wrapper_error'] = type(error).__name__
        return values

    def uv_repeat_install():
        owner, request = uv_repeat_request()
        handle = uv_repeat_enable(owner, request)
        proof = receipt['uv_repeat_probe']
        entry = {'assignment': asdict(request), 'owner': owner,
                 'via_production_toggle': uv_repeat_production,
                 'diagnostics': [asdict(d) for d in handle.diagnostics],
                 'owned_count': len(handle.owned_pairs),
                 'merged': [exporter._capture_map(km, bpy.types.OperatorProperties)
                            for km in configs.user.keymaps if km.name == 'UV Editor']}
        proof['installations'].append(entry)
        record('uv_repeat_candidate_installed')
        assert len(handle.owned_pairs) == 1, 'Ordinary runtime assignment was not admitted'
        matches = uv_repeat_matches()
        assert len(matches) == 1, 'Expected one exact effective UV repeat candidate'
        _, item = matches[0]
        expected_key = 'F20' if uv_repeat_reopen else 'G'
        assert item.type == expected_key and item.value == 'PRESS' and item.repeat
        assert not any((item.shift, item.ctrl, item.alt, item.oskey, item.any))
        if not uv_repeat_reopen:
            assert item.active

    def uv_repeat_enable(owner, request):
        if uv_repeat_production:
            prefs.keymap.transform.enable_transform_action_shortcuts = True
            kmreg.refresh()
            # Read-only ownership evidence; registration uses only the public
            # preference/category path, never a fixture register_feature call.
            handle = rt._FEATURES.get(owner)
            assert handle is not None and handle.assignments == (request,)
        else:
            handle = rt.register_feature(owner, assignments=(request,))
        state['uv_repeat_handle'] = handle
        configs.update()
        return handle

    def uv_repeat_release():
        handle = state.pop('uv_repeat_handle', None)
        if handle is None:
            return
        if uv_repeat_production:
            prefs.keymap.transform.enable_transform_action_shortcuts = False
            kmreg.refresh()
            assert handle.owner_id not in rt._FEATURES
            assert not uv_repeat_matches()
            assert owned_rows()['transform'] == state['uv_other_transform_rows']
            set_groups(False, False, False)
        else:
            handle.release()
        configs.update()
        proof = receipt['uv_repeat_probe']
        after = uv_repeat_sources()
        expected = copy.deepcopy(proof['source_and_foreign_merged_before'])
        owned_edit = proof.get('saved_edit') or proof.get('saved_edit_restored')
        aggregate_marker = None
        if owned_edit and owned_edit.get('map_is_user_modified_after_edit'):
            # This map-level marker describes our own saved user edit too.
            # Keep every row and all other source/merged metadata exact.
            for keymap in expected['user']:
                if keymap['scope']['name'] == 'UV Editor':
                    aggregate_marker = {'before': keymap['is_user_modified'], 'expected_after': True,
                                        'reason': 'verified edit of the owned merged row'}
                    keymap['is_user_modified'] = True
        entry = {'source_and_foreign_merged_after': after,
                 'strict_snapshot_equality': after == proof['source_and_foreign_merged_before'],
                 'expected_owned_map_edit_marker': aggregate_marker,
                 'strict_preservation': after == expected,
                 'source_maps_exact': all(after[role] == proof['source_and_foreign_merged_before'][role]
                                          for role in ('default', 'active', 'addon')),
                 'retained_source_edit_count': len(rt.retained_edits()),
                 'owned_candidate_absent': not uv_repeat_matches()}
        if uv_repeat_production:
            entry['other_transform_declarations_preserved_after_actions_off'] = True
        proof['releases'].append(entry)
        record('uv_repeat_candidate_released')
        assert entry['strict_preservation'], 'UV repeat release changed captured foreign fields/order/readability'
        assert entry['source_maps_exact'] and entry['retained_source_edit_count'] == 0
        assert entry['owned_candidate_absent']
        if uv_repeat_production:
            set_groups(False, False, True)
            assert owned_rows()['transform'] == state['uv_other_transform_rows']

    def uv_repeat_save():
        keymap, item = uv_repeat_matches()[0]
        source_before = uv_repeat_owned_source()
        evidence = {
            'event': 'F20/PRESS', 'repeat': True, 'active': False,
            'immediate_save': False, 'layer': 'owned merged user item',
            'actual_before_edit': uv_repeat_item_fields(keymap, item),
            'owned_source_before': source_before,
        }
        receipt['uv_repeat_probe']['saved_edit'] = evidence
        item.type = 'F20'
        item.active = False
        evidence['actual_before_save'] = uv_repeat_item_fields(keymap, item)
        # Save in the same callback, before the lifecycle watcher gets a tick.
        evidence['save_result'] = sorted(bpy.ops.wm.save_userpref())
        evidence['immediate_save'] = True
        evidence['held_wrapper_after_save'] = uv_repeat_item_fields(keymap, item)
        saved = root / 'saved-cases'
        saved.mkdir()
        shutil.copyfile(root / 'config/userpref.blend', saved / 'userpref.blend')
        source_after = uv_repeat_owned_source()
        evidence['owned_source_after'] = source_after
        evidence['owned_source_unchanged'] = source_after == source_before
        record('uv_repeat_immediate_save_recorded')
        assert source_after == source_before, 'Merged edit unexpectedly changed the owned addon source'
        # Saving may rebuild the merged map. Reacquire from the exact scope and
        # target after an explicit update rather than trusting an old RNA wrapper.
        configs.update()
        matches = uv_repeat_matches()
        evidence['merged_matches_after_update'] = len(matches)
        record('uv_repeat_saved_map_updated')
        assert len(matches) == 1
        keymap, item = matches[0]
        actual = uv_repeat_item_fields(keymap, item)
        evidence['reacquired_after_update'] = actual
        evidence['map_is_user_modified_after_edit'] = keymap.is_user_modified
        record('uv_repeat_saved_item_reacquired')
        assert actual['type'] == 'F20', actual
        assert actual['value'] == 'PRESS', actual
        assert actual['active'] is False, actual
        assert actual['repeat'] is True, actual
        assert actual['is_user_modified'] is True, actual
        owner, request = uv_repeat_request()
        manifest = {'owner': owner, 'request_id': request.request_id,
                    'production_identity': uv_repeat_production,
                    'preference_sha256': sha(saved / 'userpref.blend'),
                    'declared_source': source_before,
                    'expected_edit': {'event': 'F20/PRESS', 'active': False, 'repeat': True}}
        (saved / 'uv-repeat-expected.json').write_text(json.dumps(manifest, indent=2) + '\n')
        evidence['saved_manifest'] = manifest
        uv_repeat_release()
        # The runtime should restore the saved override for this same owner.
        uv_repeat_install_edited()

    def uv_repeat_install_edited():
        owner, request = uv_repeat_request()
        uv_repeat_enable(owner, request)
        matches = uv_repeat_matches()
        receipt['uv_repeat_probe']['restoration_match_count'] = len(matches)
        assert len(matches) == 1
        keymap, item = matches[0]
        actual = uv_repeat_item_fields(keymap, item)
        receipt['uv_repeat_probe']['restoration_actual_item'] = actual
        record('uv_repeat_restoration_item_observed')
        assert actual['type'] == 'F20', actual
        assert actual['value'] == 'PRESS', actual
        assert actual['active'] is False, actual
        assert actual['repeat'] is True, actual
        assert actual['is_user_modified'] is True, actual
        owned_source = uv_repeat_owned_source()
        expected_source = (state['uv_repeat_incoming_manifest']['declared_source']
                           if uv_repeat_reopen else receipt['uv_repeat_probe']['saved_edit']['owned_source_before'])
        assert owned_source['scope'] == expected_source['scope']
        assert {k: v for k, v in owned_source['row'].items() if k != 'blender_id'} == {
            k: v for k, v in expected_source['row'].items() if k != 'blender_id'}
        receipt['uv_repeat_probe']['saved_edit_restored'] = {
            'event': item.type, 'active': item.active, 'repeat': item.repeat,
            'is_user_modified': item.is_user_modified, 'fresh_process': uv_repeat_reopen,
            'map_is_user_modified_after_edit': keymap.is_user_modified,
            'exact_declared_source_restored': owned_source,
        }
        record('uv_repeat_saved_edit_restored')

    def provider_enable():
        if not os.environ.get('DELUXE_CATEGORY_PROVIDER'):
            record('xray_provider_unavailable')
            return
        module = addon_utils.enable('xray_selection_tools', default_set=True, persistent=False)
        state['provider_enabled'] = module is not None
        receipt['provider'] = {'module': 'xray_selection_tools',
                               'version': list(module.bl_info['version']) if module else None,
                               'enabled': module is not None}
        if module is not None and 'tracked_codes' in state:
            for name, loaded in tuple(sys.modules.items()):
                if name.startswith('xray_selection_tools.') and loaded is not None:
                    for candidate in tuple(vars(loaded).values()):
                        if not isinstance(candidate, type):
                            continue
                        identifier = getattr(candidate, 'bl_idname', '')
                        if not isinstance(identifier, str) or not identifier:
                            continue
                        for method in ('invoke', 'execute', 'modal'):
                            code = getattr(getattr(candidate, method, None), '__code__', None)
                            if code is not None:
                                state['tracked_codes'][code] = identifier
        record('xray_provider_enable')

    def provider_disable():
        if state.get('provider_enabled'):
            addon_utils.disable('xray_selection_tools', default_set=True)
            state['provider_enabled'] = False
        record('xray_provider_disable')

    def set_xray_preference(enabled):
        prefs.thirdparty.x_ray_selection_tools.enable_selection_tool_switch_box_x_ray = enabled

    def q_press_probe(scopes=('Object Mode',)):
        if 'q_press_probe' in state:
            state['q_press_probe'].release()
        state['q_probe_requested_scopes'] = scopes
        targets = {'Object Mode': 'object', 'Mesh': 'mesh', 'Curve': 'curve', 'Curves': 'curves'}
        requests = tuple(rt.KeymapAssignment('q-press-probe-' + scope, rt.KeymapScope(scope), rt.KeymapEvent('Q'),
                                             rt.KeymapTarget('wm.bh_tool_select_box_xray_' + targets[scope]),
                                             declared_properties_only=True) for scope in scopes)
        handle = rt.register_feature('category03-q-press-probe', assignments=requests)
        state['q_press_probe'] = handle
        assert len(handle.owned_pairs) == len(requests), handle.diagnostics
        configs.update()
        record('temporary_owned_q_press_probe_applied', scopes=list(scopes))

    def box_tool_case(kind, provider):
        import bmesh
        values = {}
        def prepare():
            if kind == 'object':
                reset_objects()
                with override():
                    for x in (0, 4):
                        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 0))
                    for obj in bpy.context.scene.objects:
                        obj.select_set(False)
                values['read'] = lambda: sorted(o.name for o in bpy.context.selected_objects)
            else:
                selection_setup('mesh')
                obj = bpy.context.object
                bm = bmesh.from_edit_mesh(obj.data)
                for vertex in bm.verts:
                    vertex.select = False
                bmesh.update_edit_mesh(obj.data)
                values['read'] = lambda: [v.index for v in bmesh.from_edit_mesh(obj.data).verts if v.select]
            view = area.spaces.active.region_3d
            view.view_rotation = Quaternion((1, 0, 0, 0))
            view.view_location = (0, 0, 0)
            view.view_distance = 9
            view.view_perspective = 'ORTHO'
            set_xray_preference(provider)
            state['wrapper_calls'].clear()
            with override():
                result = getattr(bpy.ops.wm, 'bh_tool_select_box_xray_' + kind)()
            values.update(before=values['read'](), tool=active_tool(), activation_result=sorted(result))
        def begin():
            event('MOUSEMOVE', 'NOTHING', dx=-60, dy=-60)
            event('LEFTMOUSE', dx=-60, dy=-60)
        def move():
            event('MOUSEMOVE', 'NOTHING', dx=60, dy=60)
        def start_drag():
            event('MOUSEMOVE', 'NOTHING', dx=-45, dy=-45)
        def release():
            event('LEFTMOUSE', 'RELEASE', dx=60, dy=60)
        def end():
            receipt['dispatch'].append({'case': 'box_tool_' + kind + ('_provider' if provider else '_builtin'),
                                        'activation_method': 'direct wrapper invocation; not Q dispatch',
                                        'activation_result': values['activation_result'], 'tool': values['tool'],
                                        'selection_method': 'native left-button drag through active tool',
                                        'before': values['before'], 'after': values['read'](),
                                        'observed_callbacks': list(state['wrapper_calls'])})
            record('box_tool_' + kind)
            press('ESC')
        steps.extend((prepare, lambda: None, begin, start_drag, move, release, lambda: None, end))

    def walk_case(label, finish='RIGHTMOUSE'):
        values = {}
        def begin():
            object_setup()
            values['before'] = view_value()
            with override():
                result = bpy.ops.view3d.walk('INVOKE_DEFAULT')
            assert 'RUNNING_MODAL' in result, result
        def moving():
            event('W')
        def finish_walk():
            event('W', 'RELEASE')
            values['during'] = view_value()
            event(finish)
            event(finish, 'RELEASE')
        def end():
            receipt['dispatch'].append({'case': label, 'before': values['before'],
                                        'during': values['during'], 'after': view_value(),
                                        'start_method': 'direct Walk invocation; native W and finish inputs'})
            record(label)
        steps.extend((begin, moving, lambda: None, lambda: None, finish_walk, lambda: None, end))

    def install_walk_probe():
        keymap = configs.default.keymaps['View3D Walk Modal']
        sources = [i for i in keymap.keymap_items
                   if i.propvalue == 'CANCEL' and i.type == 'RIGHTMOUSE' and i.value == 'ANY' and i.any]
        assert len(sources) == 1
        assert any(i.propvalue == 'CONFIRM' for i in keymap.keymap_items)
        state['walk_before'] = exporter._capture_map(keymap, bpy.types.OperatorProperties)
        item = keymap.keymap_items.new_from_item(sources[0], head=True)
        state['walk_probe'] = (keymap, item)
        # Experiment authorized for this owned disposable copy only. This does
        # not enable a runtime capability or mutate an inherited source field.
        item.propvalue = 'CONFIRM'
        configs.update()
        assert tuple(keymap.keymap_items)[0] == item
        receipt['walk_probe'] = {'source': 'e2b764b7b0c4e71301aeb27d4a387fe16ca5b2245744d499e17a8760f031cddc',
                                 'desired': '9fad693a3ea8bcf1557c567c0c28d1021016e6ddcd510288ac80e686fb673dff',
                                 'owned_copy_head': True, 'ordinary_runtime_capability_enabled': False}
        record('owned_walk_modal_copy_installed')

    def release_walk_probe():
        if 'walk_probe' not in state:
            return
        keymap, item = state.pop('walk_probe')
        keymap.keymap_items.remove(item)
        configs.update()
        assert exporter._capture_map(keymap, bpy.types.OperatorProperties) == state['walk_before']
        receipt['walk_probe']['source_fields_and_order_restored'] = True
        record('owned_walk_modal_copy_released')

    steps.extend((lambda: press('ESC'), lambda: press('ESC'), initialize,
                  lambda: press('F24')))

    def verify_sentinel():
        assert state['sentinel'] == 1, state['sentinel']
        record('keyboard_sentinel_passed')

    steps.append(verify_sentinel)
    if mode == 'inspect':
        steps.append(inspect)
    elif mode == 'schema':
        steps.append(schema_probe)
    elif mode == 'navigation':
        steps.append(lambda: set_groups(True, False, False))
        nav_case('orbit_alt_left', 'LEFTMOUSE', mods={'alt': True}, drag=(90, 40))
        nav_case('pan_alt_middle', 'MIDDLEMOUSE', mods={'alt': True}, drag=(90, 40))
        nav_case('zoom_alt_right', 'RIGHTMOUSE', mods={'alt': True}, drag=(90, 40))
        for label, delta in (('north', (0, 95)), ('south', (0, -95)), ('west', (-95, 0)), ('east', (95, 0))):
            nav_case('axis_' + label, 'LEFTMOUSE', mods={'shift': True, 'alt': True}, drag=delta)
        nav_case('axis_front_middle', 'MIDDLEMOUSE', mods={'shift': True, 'alt': True})
        for label, delta in (('north', (0, 95)), ('south', (0, -95)), ('west', (-95, 0)), ('east', (95, 0))):
            nav_case('axis_' + label + '_select_tool', 'LEFTMOUSE',
                     mods={'shift': True, 'alt': True}, drag=delta, tool='builtin.select')
        for key in ('WHEELLEFTMOUSE', 'WHEELRIGHTMOUSE'):
            nav_case('pan_' + key, key)
        for key, mods in (('F', {}), ('F', {'shift': True}), ('A', {}),
                          ('WHEELUPMOUSE', {'shift': True, 'alt': True}),
                          ('WHEELRIGHTMOUSE', {'shift': True, 'alt': True}),
                          ('WHEELDOWNMOUSE', {'shift': True, 'alt': True}),
                          ('WHEELLEFTMOUSE', {'shift': True, 'alt': True})):
            nav_case('framing_' + key + ('_shift' if mods.get('shift') else ''), key, mods=mods)
    elif mode == 'q':
        steps.extend((lambda: set_groups(False, True, False), trace_q_wrappers))
        q_case('q_object_provider_absent')
        steps.append(provider_enable)
        q_case('q_object_provider_available')
        steps.append(lambda: set_xray_preference(False))
        q_case('q_object_preference_off')
        steps.append(q_press_probe)
        q_case('q_owned_press_probe_builtin_fallback')
        steps.append(lambda: set_xray_preference(True))
        q_case('q_owned_press_probe_xray_tool')
        def release_press_probe():
            state.pop('q_probe_requested_scopes', None)
            state['q_press_probe'].release()
            configs.update()
        steps.append(release_press_probe)
        q_case('q_press_probe_released')
    elif mode in ('q_modes', 'q_probe_modes'):
        steps.extend((lambda: set_groups(False, True, False), trace_q_wrappers))
        if mode == 'q_probe_modes':
            steps.append(lambda: q_press_probe(('Object Mode', 'Mesh', 'Curve', 'Curves')))
        for phase in ('absent', 'enabled', 'preference_off', 'disabled', 'reenabled'):
            if phase in ('enabled', 'reenabled'):
                steps.append(provider_enable)
            elif phase == 'preference_off':
                steps.append(lambda: set_xray_preference(False))
            elif phase == 'disabled':
                steps.extend((provider_disable, lambda: set_xray_preference(True)))
            for kind in ('object', 'mesh', 'curve', 'curves'):
                q_case('q_' + kind + '_' + phase, kind)
    elif mode == 'q_tools':
        steps.extend((lambda: set_groups(False, True, False), trace_q_wrappers, provider_enable))
        for kind in ('object', 'mesh'):
            box_tool_case(kind, True)
            box_tool_case(kind, False)
    elif mode == 'walk_probe':
        steps.append(lambda: set_groups(False, False, False))
        walk_case('walk_stock_right_cancel')
        steps.append(install_walk_probe)
        walk_case('walk_owned_right_confirm')
        walk_case('walk_owned_escape_still_cancel', 'ESC')
        steps.append(release_walk_probe)
        walk_case('walk_released_right_cancel')
    elif mode == 'uv_g_control':
        steps.append(lambda: set_groups(False, False, True))
        uv_transform_case('G', prior_rotation=True)
    elif mode in ('uv_g_probe', 'uv_g_save', 'uv_g_reopen', 'uv_g_production',
                  'uv_g_production_save', 'uv_g_production_reopen'):
        steps.extend((lambda: set_groups(False, False, True), uv_repeat_start))
        if uv_repeat_reopen:
            steps.extend((uv_repeat_install_edited, uv_repeat_release,
                          uv_repeat_install_edited, uv_repeat_release))
        else:
            steps.append(uv_repeat_install)
            if mode in ('uv_g_save', 'uv_g_production_save'):
                steps.extend((uv_repeat_save, uv_repeat_release))
            else:
                uv_transform_case('G', expectation='empty_history')
                uv_transform_case('G', prior_rotation=True, expectation='single_repeat')
                uv_transform_case('G', prior_translation=True, expectation='single_repeat')
                uv_transform_case('W', expectation='translate')
                uv_transform_case('W', shift=True, expectation='move_tool')
                steps.append(uv_repeat_release)
                uv_transform_case('G', prior_rotation=True, expectation='translate')
                if uv_repeat_production:
                    uv_transform_case('W', expectation='translate')
                    uv_transform_case('W', shift=True, expectation='move_tool')
                steps.append(uv_repeat_install)
                uv_transform_case('G', prior_rotation=True, expectation='single_repeat')
                steps.append(uv_repeat_release)
    elif mode in ('handler_observe', 'handler_probe'):
        steps.append(lambda: set_groups(False, False, False))
        handler = load_file('category03_handler_fixture', root / 'handler-fixture.py')
        state['handler_fixture'] = handler.HandlerCases(
            steps, receipt, record, window, area, exporter, probe=mode == 'handler_probe').append()
    elif mode == 'circle_production':
        def circle_setup():
            prefs.keymap.selection.enable_selection_more_less = False
            prefs.keymap.selection.enable_selection_tool_switch = False
            prefs.keymap.selection.enable_selection_all_none = False
            prefs.keymap.selection.enable_selection_circle = True
            set_groups(False, True, False)
            assert len(owned_rows()['selection']) == 4
        steps.append(circle_setup)
        handler = load_file('category03_handler_fixture', root / 'handler-fixture.py')
        fixture = handler.HandlerCases(steps, receipt, record, window, area, exporter)
        state['handler_fixture'] = fixture
        steps.append(fixture.start)
        def circle_metadata():
            receipt['handler_proof'].update(stage='production_circle', ledger_ids=[
                key for key, binding in handler.BINDINGS.items()
                if binding['target'] in ('view3d.select_circle', 'uv.select_circle')])
        steps.append(circle_metadata)
        for kind in ('object', 'uv'):
            fixture.case('production_circle_' + kind + '_add', kind, mods={'shift': True}, circle=True)
            fixture.case('production_circle_' + kind + '_subtract', kind, mods={'ctrl': True}, circle=True, subtract=True)
        def circle_off():
            state['circle_before'] = owned_rows()
            prefs.keymap.selection.enable_selection_circle = False
            kmreg.refresh()
            configs.update()
            after = owned_rows()
            assert not after['selection']
            assert all(after[c] == state['circle_before'][c] for c in ('navigation', 'transform'))
            receipt['circle_toggle'] = {'off_removed_exactly_four': True, 'unrelated_categories_unchanged': True}
        steps.append(circle_off)
        fixture.case('production_circle_disabled_object_add', mods={'shift': True})
        def circle_on():
            prefs.keymap.selection.enable_selection_circle = True
            kmreg.refresh()
            configs.update()
            assert owned_rows() == state['circle_before']
            receipt['circle_toggle']['restored_exactly'] = True
        steps.append(circle_on)
        fixture.case('production_circle_reenabled_object_add', mods={'shift': True}, circle=True)
        steps.append(fixture.cleanup)
    elif mode in ('uv_arrow_probe', 'uv_arrow_production'):
        production = None
        if mode == 'uv_arrow_production':
            editor_helper = load_file('category03_editor_comparison', root / 'editor-fixture.py')
            operators = sys.modules[PACKAGE + '.operators.selection_more_less_ops']

            def arrow_production_setup():
                for name in ('enable_selection_more_less', 'enable_selection_all_none',
                             'enable_selection_circle', 'enable_selection_tool_switch'):
                    setattr(prefs.keymap.selection, name, False)
                set_groups(False, True, False)

            def arrow_production_toggle(enabled):
                prefs.keymap.selection.enable_selection_more_less = enabled
                kmreg.refresh()
                configs.update()

            steps.append(arrow_production_setup)
            production = {
                'classes': (operators.WM_OT_BH_uv_select_more, operators.WM_OT_BH_uv_select_less),
                'toggle': arrow_production_toggle,
                'registered_pairs': lambda: kmreg.selection_keymaps_register.registered_selection_keymaps,
                'source_provenance': pipeline_source_provenance,
                'compare_sources': editor_helper.EditorCases.compare_sources,
            }
        else:
            steps.append(lambda: set_groups(True, True, True))
        helper = load_file('category03_ordinary_fixture', root / 'ordinary-fixture.py')
        ordinary = helper.OrdinaryCases(
            steps, receipt, record, window, area, exporter,
            cluster='uv_edit', ledger_path=root / 'ordinary-ledger.jsonl')
        state['ordinary_fixture'] = helper.UVArrowPrecedenceCases(ordinary, rt, production=production).append()
    elif mode in ('ordinary_observe', 'ordinary_probe', 'ordinary_production'):
        steps.append(lambda: set_groups(mode == 'ordinary_production', mode == 'ordinary_production', mode == 'ordinary_production'))
        helper = load_file('category03_ordinary_fixture', root / 'ordinary-fixture.py')
        inversion = {'True': True, 'False': False}.get(os.environ.get('DELUXE_CATEGORY_INVERT_ZOOM'))
        state['ordinary_fixture'] = helper.OrdinaryCases(
            steps, receipt, record, window, area, exporter, probe=mode == 'ordinary_probe',
            cluster=os.environ.get('DELUXE_CATEGORY_ORDINARY_CLUSTER', 'axis'), invert_zoom=inversion,
            ledger_path=root / 'ordinary-ledger.jsonl').append()
    elif mode == 'editor_production':
        helper = load_file('category03_editor_fixture', root / 'editor-fixture.py')
        cluster = os.environ.get('DELUXE_CATEGORY_EDITOR_CLUSTER', 'selection')
        fixture = helper.EditorCases(steps, receipt, record, window, area, exporter,
                                     cluster=cluster, matched_endpoints=True, input_controls=True)
        state['editor_fixture'] = fixture
        fixture.owned_source_provenance = pipeline_source_provenance
        def production_editor_setup():
            prefs.keymap.selection.enable_selection_more_less = False
            prefs.keymap.selection.enable_selection_all_none = False
            prefs.keymap.selection.enable_selection_circle = False
            prefs.keymap.selection.enable_selection_tool_switch = False
            set_groups(False, True, False)
            if cluster == 'remaining':
                directory = root / 'datafiles/category03-file-browser'
                directory.mkdir()
                for index in range(256):
                    (directory / f'Fixture_{index:03}').mkdir()
                fixture.file_browser_directory = directory
            module = next(module for module in addon.operators_register.OPERATOR_MODULES
                          if module.__name__.endswith('.selection_more_less_ops'))
            codes = {module.WM_OT_BH_editor_select_more.execute.__code__: 'UP',
                     module.WM_OT_BH_editor_select_less.execute.__code__: 'DOWN'}
            previous = sys.getprofile()
            state['previous_profile'] = previous
            def observe(frame, event, argument):
                if event == 'call' and frame.f_code in codes:
                    direction = codes[frame.f_code]
                    context = frame.f_locals['context']
                    kind = fixture.guarded_kind(context)
                    fixture.callbacks.append({'direction': direction,
                                              'target': helper.TARGETS[kind][direction][0] if kind else None,
                                              'operator': 'wm.bh_editor_select_' + ('more' if direction == 'UP' else 'less')})
                if previous is not None:
                    previous(frame, event, argument)
            # Observe the actual input dispatch interval only. Snapshot capture
            # and JSON serialization need no execute-call profiling.
            fixture.before_shortcut = lambda: sys.setprofile(observe)
            fixture.after_shortcut = lambda: sys.setprofile(previous)
        steps.append(production_editor_setup)
        fixture.append_matched_endpoint('before_production_guard')
        steps.append(fixture.start)
        def production_editor_metadata():
            fixture.state['stage'] = 'production_guarded_editor'
            fixture.state['production_operators'] = ['wm.bh_editor_select_more', 'wm.bh_editor_select_less']
            fixture.state['callback_observation'] = 'read-only profile during shortcut dispatch; disabled before snapshots'
        steps.append(production_editor_metadata)
        kinds = (tuple(helper.TARGETS) if cluster == 'selection' else
                 helper.REMAINING_PASSTHROUGH if cluster == 'remaining' else helper.PASSTHROUGH)
        for kind in kinds:
            fixture.case(kind, 'UP', 'before_install', direct=False)
        def production_editor_on():
            prefs.keymap.selection.enable_selection_more_less = True
            kmreg.refresh()
            configs.update()
            selected = [row for row in owned_rows()['selection']
                        if row['idname'] in fixture.state['production_operators']]
            assert len(selected) == 2
            observed = []
            for direction, target in zip(('UP', 'DOWN'), fixture.state['production_operators']):
                expected = {**fixture.exact_descriptor(direction), 'target': target}
                matches = [row for keymap in configs.user.keymaps
                           if all(getattr(keymap, field, None) == value
                                  for field, value in helper.PROBE_SCOPE.items())
                           for row in exporter._capture_map(keymap, bpy.types.OperatorProperties)['items']
                           if row['target'] == target]
                assert len(matches) == 1 and fixture.exact_row(matches[0], expected)
                observed.append({'scope': helper.PROBE_SCOPE, 'row': matches[0]})
            fixture.state['installations'].append({'production': True, 'exact_guard_rows': observed})
            record('production_editor_guard_enabled')
        steps.append(production_editor_on)
        for kind in kinds:
            for direction in ('UP', 'DOWN'):
                fixture.case(kind, direction, 'installed', direct=cluster == 'selection')
        def production_editor_off():
            prefs.keymap.selection.enable_selection_more_less = False
            kmreg.refresh()
            configs.update()
            assert not any(item.idname in fixture.state['production_operators']
                           for keymap in configs.user.keymaps for item in keymap.keymap_items)
            fixture.state['releases'].append({'production': True, 'merged_probe_rows_absent': True,
                                             'immediate_source': fixture.source_maps()})
            record('production_editor_guard_disabled')
        steps.append(production_editor_off)
        fixture.append_matched_endpoint('after_first_production_release')
        fixture.case(kinds[0], 'UP', 'after_release', direct=False)
        steps.append(production_editor_on)
        fixture.case(kinds[0], 'UP', 'reinstalled', direct=False)
        steps.append(production_editor_off)
        fixture.append_matched_endpoint('after_second_production_release')
        steps.append(fixture.cleanup)
    elif mode in ('editor_observe', 'editor_probe'):
        steps.append(lambda: set_groups(False, mode == 'editor_observe', False))
        helper = load_file('category03_editor_fixture', root / 'editor-fixture.py')
        state['editor_fixture'] = helper.EditorCases(
            steps, receipt, record, window, area, exporter, probe=mode == 'editor_probe',
            cluster=os.environ.get('DELUXE_CATEGORY_EDITOR_CLUSTER', 'selection'),
            input_controls=os.environ.get('DELUXE_CATEGORY_EDITOR_INPUT_CONTROLS') == '1',
            prime_readiness=os.environ.get('DELUXE_CATEGORY_EDITOR_PRIME_READINESS') == '1',
            matched_endpoints=os.environ.get('DELUXE_CATEGORY_EDITOR_MATCHED_ENDPOINTS') == '1').append()
    elif mode == 'selection':
        steps.append(lambda: set_groups(False, True, False))
        for kind in ('object', 'mesh', 'curve', 'curves', 'lattice', 'armature', 'uv',
                     'dopesheet', 'graph', 'node', 'sequencer', 'mask'):
            selection_case(kind, 'WHEELUPMOUSE')
            selection_case(kind, 'WHEELDOWNMOUSE')
        selection_case('uv', 'RIGHT_BRACKET', shift=False)
        selection_case('uv', 'LEFT_BRACKET', shift=False)
        for oskey in (False, True):
            selection_all_none_case(oskey=oskey)
            selection_all_none_case(shift=True, oskey=oskey)
        steps.append(selection_all_none_isolation)
    elif mode == 'selection_failures':
        steps.append(lambda: set_groups(False, True, False))
        for kind in ('mesh', 'curve', 'dopesheet', 'graph', 'node', 'sequencer', 'mask'):
            selection_case(kind, 'WHEELUPMOUSE', control=True)
            selection_case(kind, 'WHEELDOWNMOUSE', control=True)
    elif mode == 'transform':
        steps.append(lambda: set_groups(False, False, True))
        for key in ('W', 'E', 'R', 'G'):
            transform_case(key)
        for key in ('W', 'E', 'R'):
            transform_case(key, shift=True)
        transform_case('W', gizmo=True)
        context_menu_case()
        face_case()
        for key in ('W', 'G'):
            uv_transform_case(key)
        uv_transform_case('W', shift=True)
    elif mode == 'image':
        steps.append(lambda: set_groups(True, False, False))
        image_case('LEFTMOUSE', {'alt': True}, (90, 40))
        image_case('MIDDLEMOUSE', {'alt': True}, (90, 40))
        image_case('RIGHTMOUSE', {'alt': True}, (90, 40))
        for key in ('F', 'A', 'WHEELUPMOUSE', 'WHEELRIGHTMOUSE', 'WHEELDOWNMOUSE', 'WHEELLEFTMOUSE'):
            image_case(key, {'shift': True, 'alt': True} if key.startswith('WHEEL') else {})
    elif mode in ('persistence', 'reopen', 'editor_save', 'editor_reopen', 'uv_arrow_save', 'uv_arrow_reopen'):
        editor_helper = load_file('category03_editor_fixture', root / 'editor-fixture.py')
        persistence_helper = load_file('category03_persistence_fixture', root / 'persistence-fixture.py')
        fixture = editor_helper.EditorCases(steps, receipt, record, window, area, exporter,
                                             matched_endpoints=True)
        fixture.owned_source_provenance = pipeline_source_provenance
        state['editor_fixture'] = fixture
        state['persistence_fixture'] = persistence_helper.PersistenceCases(
            bpy=bpy, configs=configs, runtime=rt, categories=kmreg, preferences=prefs,
            fixture=fixture, root=root, record=record, receipt=receipt, set_groups=set_groups,
            production_paths=PRODUCTION_PATHS, package=PACKAGE,
            editor_only=mode.startswith('editor_'), uv_arrow_only=mode.startswith('uv_arrow_'),
            reopen=mode in ('reopen', 'editor_reopen', 'uv_arrow_reopen')).append(steps)
    else:
        raise ValueError('Native case not implemented: ' + mode)

    def cleanup():
        ordinary_cleanup_error = None
        if 'g_control_binding' in state:
            keymap, item = state.pop('g_control_binding')
            keymap.keymap_items.remove(item)
            configs.update()
        uv_repeat_release()
        if 'editor_fixture' in state:
            state['editor_fixture'].cleanup()
        if 'ordinary_fixture' in state:
            try:
                state['ordinary_fixture'].cleanup()
            except Exception:
                ordinary_cleanup_error = traceback.format_exc()
                receipt['ordinary_fixture_cleanup_error'] = ordinary_cleanup_error
        if 'handler_fixture' in state:
            state['handler_fixture'].cleanup()
        release_walk_probe()
        if 'q_press_probe' in state:
            state['q_press_probe'].release()
        for menu, callback in state.get('menu_callbacks', ()):
            menu.remove(callback)
        if 'previous_profile' in state:
            sys.setprofile(state['previous_profile'])
        for keymap, item in sentinel_pairs:
            keymap.keymap_items.remove(item)
        sentinel_pairs.clear()
        addon_utils.disable(PACKAGE, default_set=True)
        if state.get('provider_enabled'):
            addon_utils.disable('xray_selection_tools', default_set=True)
        configs.update()
        bpy.utils.unregister_class(CATEGORY03_OT_sentinel)
        receipt['cleanup'] = rt.runtime_stats()
        receipt['watcher_stopped'] = not bpy.app.timers.is_registered(kmreg._watch_keymaps)
        assert not receipt['cleanup']['owned'] and not receipt['cleanup']['pending_cleanup']
        assert receipt['watcher_stopped']
        if ordinary_cleanup_error:
            raise AssertionError('Ordinary fixture cleanup failed; addon shutdown completed')

    iterator = iter(steps)

    def tick():
        try:
            step = next(iterator)
            print('CATEGORY03_CALL ' + step.__qualname__, flush=True)
            step()
            return 0.3
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
        bpy.app.timers.register(lambda: bpy.ops.wm.quit_blender() and None, first_interval=0.4)

    bpy.app.timers.register(tick, first_interval=2.0)
    record('scheduled')


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blender', type=Path, required=True)
    parser.add_argument('--profile-source', type=Path, help='Read-only protected input hashes; not loaded in factory cases')
    parser.add_argument('--provider-source', type=Path)
    parser.add_argument('--mode', choices=('inspect', 'schema', 'navigation', 'q', 'q_modes', 'q_probe_modes', 'q_tools', 'walk_probe', 'uv_g_control', 'uv_g_probe', 'uv_g_save', 'uv_g_reopen', 'uv_g_production', 'uv_g_production_save', 'uv_g_production_reopen', 'uv_arrow_probe', 'handler_observe', 'handler_probe', 'circle_production', 'ordinary_observe', 'ordinary_probe', 'ordinary_production', 'editor_observe', 'editor_probe', 'editor_production', 'selection', 'selection_failures',
                                         'transform', 'image', 'persistence', 'reopen', 'editor_save', 'editor_reopen',
                                         'uv_arrow_production', 'uv_arrow_save', 'uv_arrow_reopen'), required=True)
    parser.add_argument('--editor-input-controls', action='store_true')
    parser.add_argument('--editor-prime-readiness', action='store_true')
    parser.add_argument('--editor-matched-endpoints', action='store_true')
    parser.add_argument('--editor-cluster', choices=('selection', 'passthrough', 'remaining'), default='selection')
    parser.add_argument('--ordinary-cluster', choices=('axis', 'wheel_zoom', 'uv_edit', 'uv_cursor', 'tools', 'selection', 'tools_selection'), default='axis')
    parser.add_argument('--invert-zoom', action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument('--output', type=Path, default=REPO / 'test-results/deluxe-keymaps-category03')
    parser.add_argument('--incoming', type=Path)
    parser.add_argument('--test-minimum-version')
    parser.add_argument('--timeout', type=float, default=75)
    args = parser.parse_args()
    if not Path('/usr/bin/sandbox-exec').is_file():
        parser.error('Requires macOS sandbox-exec confinement.')
    return launch(args)


if __name__ == '__main__':
    if 'DELUXE_CATEGORY_ROOT' in os.environ:
        native_main(Path(os.environ['DELUXE_CATEGORY_ROOT']), os.environ['DELUXE_CATEGORY_MODE'])
    else:
        raise SystemExit(cli())
