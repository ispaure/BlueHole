"""Portable profile edits, source resolution, and atomic recovery."""

from copy import deepcopy
from dataclasses import asdict
import hashlib
import importlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

from runtime_keymap_fakes import FakeRuntime, row

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures'
DEFAULTS = ROOT / 'keymaps/deluxe-defaults.json'


def read(path):
    return json.loads(path.read_text())


class ProfileTests(unittest.TestCase):
    def setUp(self):
        package = ModuleType('_deluxe_profiles_test')
        package.__path__ = [str(ROOT)]
        self.runtime = FakeRuntime()
        self.enterContext(patch.dict(sys.modules, {package.__name__: package, 'bpy': self.runtime.bpy}))

        def load(name):
            return importlib.import_module(package.__name__ + '.keymaps.' + name)

        self.api = load('deluxe_profiles')
        self.core = load('keymap_utils')
        self.schema = load('deluxe_schema')
        self.resolver = load('deluxe_resolver')
        self.defaults = read(FIXTURES / 'deluxe_keymaps_category08/editor.json')
        self.path = Path(self.enterContext(TemporaryDirectory())) / 'profile.json'
        self.settings = SimpleNamespace(keymap=SimpleNamespace(enable_keymaps=True))
        self.installed = self.defaults

        def install(candidate, previous):
            self.installed = deepcopy(candidate)

        self.store = self.api.ProfileStore(self.defaults, self.path, lambda: self.settings, install)

    def test_bulk_equivalence_and_inherited_rows(self):
        catalog = read(DEFAULTS)
        self.schema.validate_catalog(catalog)
        resolver = self.resolver.Resolver(catalog)

        def switch_paths(value):
            settings = SimpleNamespace()
            for path in value:
                parent = settings
                *branches, leaf = path.split('.')
                for branch in branches:
                    if not hasattr(parent, branch):
                        setattr(parent, branch, SimpleNamespace())
                    parent = getattr(parent, branch)
                setattr(parent, leaf, True)
            return settings

        paths = {'keymap.enable_keymaps'} | {row['switch'] for table in ('categories', 'sections')
                                            for row in catalog[table].values() if row.get('switch')}
        settings = switch_paths(paths)
        _, groups = resolver.plan(catalog, settings)
        # Compare the ordered pre-cutover groups from 07, accounting for the
        # context-sensitive 3 shortcut and the two provider scope changes.
        face_id, = [id_ for id_, row in catalog['assignments'].items()
                    if row['command'] == 'object-face-select-or-pose']
        face, = [request for requests in groups.values() for request in requests
                 if request.request_id == face_id]
        self.assertEqual(face.scope, self.core.KeymapScope('Object Non-modal'))
        self.assertEqual(face.event, self.core.KeymapEvent('THREE'))
        self.assertEqual(face.target, self.core.KeymapTarget('object.bh_face_select_or_pose'))
        old_pose = resolver.target(catalog['commands']['object-mode-set-fa1f913c4675'])
        self.assertEqual(old_pose, self.core.KeymapTarget('object.mode_set', {'mode': 'POSE'}))
        def reference_row(request):
            scope, target = request.scope, request.target
            if target.idname in ('mesh.smart_delete', 'object.join_group_override'):
                scope = self.core.KeymapScope('3D View', 'VIEW_3D')
            if request.request_id == face_id:
                target = old_pose
            return [asdict(scope), asdict(request.event), target.idname, dict(target.properties), request.active]

        payload = [(owner.split(':')[1], [reference_row(request) for request in requests
                    if request.request_id in catalog['assignments']]) for owner, requests in groups.items()]
        blob = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
        self.assertEqual(hashlib.sha256(blob).hexdigest(), '9c48fa5b54876c7377817d306874f8ee96eb69518ae9947f5d64f92b95e4360c')
        self.assertEqual(sum(len(rows) for _, rows in payload), 795)
        stock = {}
        for row in map(json.loads, (FIXTURES / 'deluxe_keymaps/reconciliation-ledger.jsonl').read_text().splitlines()):
            if row['presence'].get('stock', {}).get('user'):
                binding = row['binding']
                key = (self.core.KeymapScope(**binding['scope']), self.core.KeymapEvent(**binding['event']),
                       binding['target'], binding['active'])
                stock.setdefault(key, []).append(row)
        precedence = []
        object_mode_keys = []
        for requests in groups.values():
            for request in requests:
                if request.request_id not in catalog['assignments']:
                    original_id = self.resolver.profile_assignment_id(request.request_id)
                    original, = [row for row in requests if row.request_id == original_id]
                    self.assertEqual(request.scope, self.core.KeymapScope('Object Mode'))
                    self.assertEqual(request.event, original.event)
                    self.assertEqual(request.target, original.target)
                    object_mode_keys.append(request.event.type)
                    continue
                assignment = catalog['assignments'][request.request_id]
                key = request.scope, request.event, request.target.idname, request.active
                for row in stock.get(key, ()):
                    if not all(row['binding']['properties'].get(k) == v for k, v in request.target.properties):
                        continue
                    presence = row['presence']
                    if not presence.get('full', {}).get('user'):
                        # The exact stock row was absent from the reference's
                        # merged user maps. Preserve the accepted custom scope.
                        continue
                    self.assertEqual(assignment.get('kind'), 'precedence')
                    self.assertIn(row['row_id'], assignment['samples'])
                    precedence.append(row['row_id'][:8])
        self.assertCountEqual(precedence, ('8125a8cf', '14a9687b', '94f907c3', 'eb202e0e'))
        self.assertCountEqual(object_mode_keys, ('ONE', 'TWO', 'THREE', 'FIVE', 'SIX', 'SEVEN', 'EIGHT'))

        old_id, = [id_ for id_, row in catalog['assignments'].items()
                   if row['command'] == 'object-mode-set-with-submode-2a694a5467e5']
        recreated = dict(catalog['assignments'].pop(old_id), feature='recreated-mode')
        catalog['assignments']['recreated-mode'] = recreated
        _, groups = resolver.plan(catalog, settings)
        self.assertEqual([row.scope.name for row in groups['legacy:Object:deluxe-recreated-mode']],
                         ['Object Non-modal', 'Object Mode'])
        recreated['active'] = False
        _, groups = resolver.plan(catalog, settings)
        self.assertEqual([row.scope.name for row in groups['legacy:Object:deluxe-recreated-mode']],
                         ['Object Non-modal'])

    def test_reference_command_providers(self):
        catalog = read(DEFAULTS)
        resolver = self.resolver.Resolver(catalog)
        for operator, provider, scope in (('mesh.smart_delete', 'Interactive Tools', 'Mesh'),
                                          ('object.join_group_override', 'Group Pro', 'Object Mode')):
            command, = resolver.commands[operator]
            command_id, = [id_ for id_, row in catalog['commands'].items() if row == command]
            assignment, = [row for row in catalog['assignments'].values() if row['command'] == command_id]
            self.assertEqual(assignment['scope'], {'name': scope})
            meta = resolver.describe_command(command)
            self.assertEqual(meta['owner'], provider)
            self.assertEqual(meta['availability'], 'waiting_for_provider')

    def test_round_trip_shared_edit_clone_and_group_crud(self):
        draft = self.store.begin()
        self.assertEqual(draft.uses('events', 'frame'), ('view-frame', 'image-frame'))
        self.assertEqual(draft.uses('commands', 'frame-selected'), ('view-frame',))
        draft.update('events', 'frame', type='F11')
        clone = draft.clone('events', 'image-frame', new_id='image-event')
        draft.update('events', clone, type='F12')
        command = draft.clone('commands', 'image-frame', new_id='image-command')
        draft.update('commands', command, properties={'use_all_regions': False})
        draft.put('categories', 'artist', {'label': 'Artist'})
        draft.put('sections', 'artist-framing', {'label': 'Framing', 'category': 'artist', 'enabled': False})
        draft.update('sections', 'artist-framing', label='Framing tools', order=1)
        draft.update('assignments', 'image-frame', section='artist-framing')
        draft.delete('sections', 'overview')
        self.assertFalse(self.store.preview(draft)['assignments']['image-frame']['eligible'])
        committed = self.store.apply(draft)
        self.assertEqual(committed, self.installed)
        overlay = read(self.path)
        self.assertIsNone(overlay['changes']['sections']['overview'])
        self.assertEqual(overlay['changes']['events']['frame'], {'type': 'F11'})
        self.assertEqual(set(overlay['changes']['assignments']), {'image-frame'})
        self.assertEqual(self.store.reload(), committed)
        reopened = self.api.ProfileStore(self.defaults, self.path, lambda: self.settings, None)
        self.assertEqual(reopened.snapshot(), committed)
        reset = reopened.begin()
        reset.reset()
        self.assertEqual(reset.snapshot(), self.defaults)
        reset.discard()
        with self.assertRaisesRegex(ValueError, 'closed'):
            reopened.apply(reset)

    def test_invalid_stale_and_failed_writes_keep_disk_and_runtime(self):
        draft = self.store.begin()
        draft.update('events', 'frame', shift=7)
        with self.assertRaisesRegex(ValueError, 'shift'):
            self.store.apply(draft)
        self.assertFalse(self.path.exists())
        self.assertEqual(self.installed, self.defaults)

        stale = self.store.begin()
        draft.update('events', 'frame', shift=True)
        committed = self.store.apply(draft)
        previous = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'stale'):
            self.store.apply(stale)
        draft = self.store.begin()
        draft.update('events', 'frame', shift=False)
        with patch.object(self.store._file, 'write_json', side_effect=OSError('injected failure')):
            with self.assertRaisesRegex(OSError, 'injected failure'):
                self.store.apply(draft)
        self.assertEqual(self.path.read_bytes(), previous)
        self.assertEqual(self.installed, committed)
        self.path.write_text('{')
        with self.assertRaisesRegex(ValueError, 'changed on disk'):
            self.store.apply(draft)
        self.assertEqual(self.store.reload(), committed)
        self.assertEqual(self.store.load_issue, 'invalid_profile_recovered_previous')
        reopened = self.api.ProfileStore(self.defaults, self.path, lambda: self.settings, None)
        self.assertEqual(reopened.snapshot(), committed)

    def test_native_install_failure_rolls_back(self):
        def install(candidate, previous):
            self.installed = deepcopy(candidate)
            if previous is not None:
                raise RuntimeError('native apply failed')

        self.store._install = install
        draft = self.store.begin()
        draft.update('events', 'frame', repeat=True)
        with self.assertRaisesRegex(RuntimeError, 'native apply'):
            self.store.apply(draft)
        self.assertEqual(self.installed, self.defaults)
        self.assertEqual(self.store.snapshot(), self.defaults)
        self.assertFalse(self.path.exists())

    def test_compatible_upgrade_uses_new_defaults_and_keeps_disabled_choice(self):
        stock = self.runtime.map('default', 'Window', space='EMPTY', tool=None)
        inherited = stock.keymap_items.append_fixture(row('wm.search_menu', key='F3'))
        draft = self.store.begin()
        draft.update('sections', 'framing', enabled=False)
        self.store.apply(draft)
        updated = deepcopy(self.defaults)
        updated['catalog_version'] += 1
        updated['base']['reference_version'] = '4.5.2'
        updated['sections']['framing']['label'] = 'Frame view'
        updated['events']['frame']['repeat'] = True
        store = self.api.ProfileStore(updated, self.path, lambda: self.settings, None)
        inherited.type = 'F4'
        store.register()
        self.assertEqual(store.snapshot()['sections']['framing'],
                         {'label': 'Frame view', 'category': 'navigation', 'order': 0, 'enabled': False})
        self.assertTrue(store.snapshot()['events']['frame']['repeat'])
        self.assertEqual(store.snapshot()['base']['reference_version'], '4.5.2')
        merged = self.runtime.configs.user.keymaps.get('Window')
        self.assertEqual([(item.idname, item.type) for item in merged.keymap_items],
                         [('wm.search_menu', 'F4')])

    def test_selected_binding_reports_missing_ambiguous_and_unsupported(self):
        stock = self.runtime.map('default', 'Object Mode', space='EMPTY', tool=False)
        addon = self.runtime.map('addon', 'Object Mode', space='EMPTY', tool=False)
        addon.keymap_items.new_prop_schema = {'action': 'TOGGLE'}
        select = stock.keymap_items.append_fixture(row('object.select_all', key='A',
                                                      prop_values={'action': 'SELECT'}))
        inherited = stock.keymap_items.append_fixture(row('wm.search_menu', key='F3'))
        self.runtime.configs.update()
        draft = self.store.begin()
        draft.stage_suppression('framing', stock, select, 'default', replacement='select-none', id_='rule')
        draft.stage_suppression('framing', stock, inherited, 'default', id_='unsupported')
        self.assertEqual(self.store.preview(draft)['suppressions']['rule']['status'], 'resolved')
        self.assertEqual(self.store.preview(draft)['suppressions']['unsupported']['status'], 'unsupported')
        self.store.apply(draft)
        self.assertEqual(set(read(self.path)['changes']), {'suppressions'})
        self.store.register()
        self.assertEqual(self.store.registration_results()['rule'][0], 'applied')
        self.core.release_all()
        self.assertTrue(select.active)
        self.assertEqual(select.properties.action, 'SELECT')
        stock.keymap_items.append_fixture(select.clone())
        self.runtime.configs.update()
        self.assertEqual(self.store.preview()['suppressions']['rule']['status'], 'ambiguous')
        stock.keymap_items.remove(select)
        stock.keymap_items[1].properties.action = 'TOGGLE'
        self.runtime.configs.update()
        self.assertEqual(self.store.preview()['suppressions']['rule']['status'], 'missing')
        self.assertEqual(inherited.type, 'F3')
        self.assertTrue(inherited.active)

    def test_diagnostics_for_conflicts_and_missing_providers(self):
        draft = self.store.begin()
        draft.add_assignment('framing', 'frame', 'frame-selected',
                             {'name': '3D View', 'space_type': 'VIEW_3D'}, id_='collision')
        preview = self.store.preview(draft)
        self.assertEqual(preview['conflicts'], (('view-frame', 'collision'),))
        self.assertEqual(preview['commands']['provider-fit']['availability'], 'waiting_for_provider')
        draft.update('commands', 'frame-selected', operator='wm.python_file_run')
        with self.assertRaisesRegex(ValueError, 'Unknown command'):
            self.store.validate(draft)
        draft.delete('commands', 'frame-selected')
        with self.assertRaisesRegex(ValueError, 'Missing command'):
            self.store.validate(draft)

    def test_section_state_uses_the_applied_profile_and_current_preferences(self):
        draft = self.store.begin()
        draft.update('sections', 'framing', enabled=False)
        self.assertFalse(self.store.preview(draft)['sections']['framing'])
        self.assertTrue(self.store.section_enabled('framing'))
        self.store.apply(draft)
        self.assertFalse(self.store.section_enabled('framing'))

        draft = self.store.begin()
        draft.update('sections', 'framing', enabled=True)
        self.store.apply(draft)
        self.assertTrue(self.store.section_enabled('framing'))
        self.settings.keymap.enable_keymaps = False
        self.assertFalse(self.store.section_enabled('framing'))
        self.assertFalse(self.store.section_enabled('unknown'))

    def test_edit_metadata_and_enum_validation_use_rna(self):
        enum_items = [SimpleNamespace(identifier=name) for name in ('DESELECT', 'SELECT', 'TOGGLE')]
        action = SimpleNamespace(name='Action', type='ENUM', is_enum_flag=False, is_readonly=False,
                                 default='TOGGLE', enum_items=enum_items)
        operator = SimpleNamespace(get_rna_type=lambda: SimpleNamespace(name='Select All',
                                   properties={'action': action}))
        self.runtime.bpy.ops = SimpleNamespace(object=SimpleNamespace(select_all=operator))
        draft = self.store.begin()
        draft.update('commands', 'select-none', properties={'action': 'SELECT'})
        fields = self.store.preview(draft)['commands']['select-none']['fields']
        self.assertEqual(fields['action']['values'], ('DESELECT', 'SELECT', 'TOGGLE'))
        self.assertTrue(fields['action']['editable'])
        draft.update('commands', 'select-none', properties={'action': 'UNKNOWN'})
        with self.assertRaisesRegex(ValueError, 'Invalid action'):
            self.store.validate(draft)


if __name__ == '__main__':
    unittest.main()
