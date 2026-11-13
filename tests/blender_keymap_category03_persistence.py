"""Native persistence checks using real category toggles and owned identities."""

import copy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import shutil


class PersistenceCases:
    def __init__(self, *, bpy, configs, runtime, categories, preferences, fixture,
                 root, record, receipt, set_groups, production_paths, package,
                 editor_only=False, reopen=False):
        self.bpy, self.configs, self.rt = bpy, configs, runtime
        self.kmreg, self.prefs, self.fixture = categories, preferences, fixture
        self.root, self.record, self.receipt = Path(root), record, receipt
        self.set_groups, self.production_paths, self.package = set_groups, production_paths, package
        self.reopen, self.editor_only = reopen, editor_only
        self.scenario = 'editor' if editor_only else 'circle_framing'
        self.state = {'scenario': self.scenario, 'fresh_process': reopen, 'restorations': []}
        self.receipt['production_persistence'] = self.state
        self.specs = ([{'name': 'editor_more', 'category': 'Selection',
                       'scope': 'View2D', 'space': 'EMPTY', 'target': 'wm.bh_editor_select_more',
                       'key': 'WHEELUPMOUSE', 'shift': True, 'edited_key': 'F18',
                       'edited_active': False}] if editor_only else [
            {'name': 'framing', 'category': 'Navigation', 'scope': '3D View',
             'space': 'VIEW_3D', 'target': 'view3d.view_selected', 'key': 'F',
             'shift': False, 'edited_key': 'F19', 'edited_active': True},
            {'name': 'circle', 'category': 'Selection', 'scope': '3D View Generic',
             'space': 'VIEW_3D', 'target': 'view3d.select_circle', 'key': 'MIDDLEMOUSE',
             'shift': True, 'edited_key': 'F20', 'edited_active': True, 'edited_radius': 31},
        ])

    @staticmethod
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def executed_sources(self):
        package = self.root / 'scripts/addons' / self.package
        result = {name: self.sha(package / name) for name in self.production_paths}
        for name in ('executed-native-test.py', 'editor-fixture.py', 'persistence-fixture.py'):
            result['fixture:' + name] = self.sha(self.root / name)
        return result

    def setup(self):
        nav, sel = self.prefs.keymap.navigation, self.prefs.keymap.selection
        nav.enable_navigation_viewport_movement = False
        nav.enable_navigation_viewport_axis = False
        nav.enable_navigation_view_framing = False
        for name in ('enable_selection_more_less', 'enable_selection_all_none',
                     'enable_selection_circle', 'enable_selection_tool_switch'):
            setattr(sel, name, False)
        self.set_groups(not self.editor_only, True, False)
        modules = (self.kmreg.selection_keymaps_register, self.kmreg.navigation_keymaps_register)
        getters = ('get_selection_more_less_actions',) if self.editor_only else (
            'get_selection_circle_actions', 'get_navigation_view_framing_actions')
        self.fixture.extra_source_names = {
            binding.keymap_name for module in modules for getter in getters
            if hasattr(module, getter) for action in getattr(module, getter)()
            for binding in action.keymap_bindings}
        self.state['extra_source_scopes'] = sorted(self.fixture.extra_source_names)
        if self.reopen:
            incoming = self.root / 'incoming'
            manifest = json.loads((incoming / 'category-persistence-expected.json').read_text())
            assert manifest['scenario'] == self.scenario and manifest['edits'] == self.specs
            assert manifest['preference_sha256'] == self.sha(incoming / 'userpref.blend')
            assert manifest['executed_sources'] == self.executed_sources()
            self.state['verified_incoming_manifest'] = manifest
            self.state['declared_sources'] = manifest['declared_sources']
        self.record('production_persistence_setup')

    def toggle(self, enabled):
        if self.editor_only:
            self.prefs.keymap.selection.enable_selection_more_less = enabled
        else:
            self.prefs.keymap.navigation.enable_navigation_view_framing = enabled
            self.prefs.keymap.selection.enable_selection_circle = enabled
        self.kmreg.refresh()
        self.configs.update()
        if not enabled:
            for spec in self.specs:
                assert not self.merged_matches(spec, edited=True)
        self.record('production_persistence_enabled' if enabled else 'production_persistence_disabled')

    @staticmethod
    def matches_scope(keymap, spec):
        return (keymap.name, keymap.space_type, keymap.region_type) == (
            spec['scope'], spec['space'], 'WINDOW')

    def owned_source(self, spec):
        module = getattr(self.kmreg, spec['category'].lower() + '_keymaps_register')
        registered = getattr(module, 'registered_' + spec['category'].lower() + '_keymaps')
        matches = []
        for owner_id, handle in self.rt._FEATURES.items():
            if not owner_id.startswith('legacy:' + spec['category'] + ':'):
                continue
            for request_id, owned in handle._owned.items():
                item = owned.item
                if not (self.matches_scope(owned.map, spec) and item.idname == spec['target']
                        and item.type == spec['key'] and bool(item.shift) == spec['shift']
                        and not any((item.ctrl, item.alt, item.oskey, item.any))):
                    continue
                assert self.rt._valid_owned(owned)
                assert sum(self.rt._same(km, owned.map) and self.rt._same(kmi, item)
                           for km, kmi in registered) == 1
                capture = self.fixture.capture(owned.map)
                row = next(row for row in capture['items'] if row['blender_id'] == item.id)
                assert not row['read_issues']
                request = next(r for r in handle.assignments if r.request_id == request_id)
                matches.append({'owner_id': owner_id, 'request_id': request_id,
                                'runtime_owned_valid': True, 'registered_pair_matches': True,
                                'scope': capture['scope'], 'row': row,
                                'assignment': json.loads(json.dumps(asdict(request)))})
        assert len(matches) == 1, (spec['name'], len(matches))
        return matches[0]

    def merged_matches(self, spec, *, edited):
        key = spec['edited_key'] if edited else spec['key']
        return [(km, item) for km in self.configs.user.keymaps if self.matches_scope(km, spec)
                for item in km.keymap_items if item.idname == spec['target'] and item.type == key
                and bool(item.shift) == spec['shift']
                and not any((item.ctrl, item.alt, item.oskey, item.any))]

    def observe_edited(self, spec, declared):
        matches = self.merged_matches(spec, edited=True)
        assert len(matches) == 1, (spec['name'], len(matches))
        keymap, item = matches[0]
        capture = self.fixture.capture(keymap)
        row = next(row for row in capture['items'] if row['blender_id'] == item.id)
        expected = copy.deepcopy(declared['row'])
        expected['event']['type'] = spec['edited_key']
        expected['event']['map_type'] = 'KEYBOARD'
        expected['active'] = spec['edited_active']
        expected['is_user_modified'] = True
        if 'edited_radius' in spec:
            expected['properties']['radius'] = spec['edited_radius']
        observation = {'scope': capture['scope'], 'row': row,
                       'map_is_user_modified': keymap.is_user_modified}
        self.state.setdefault('edited_observations', []).append({'name': spec['name'], **observation})
        self.record('production_persistence_edited_item_reacquired')
        assert {k: v for k, v in row.items() if k != 'blender_id'} == {
            k: v for k, v in expected.items() if k != 'blender_id'}
        assert keymap.is_user_modified
        self.fixture.verified_merged_edits.append({
            'owner_id': declared['owner_id'], 'request_id': declared['request_id'],
            'scope': capture['scope'], 'row': row, 'map_is_user_modified': True,
            'runtime_owned_valid': True, 'registered_pair_matches': True})
        return observation

    def save(self):
        sources = {spec['name']: self.owned_source(spec) for spec in self.specs}
        self.state['declared_sources'] = sources
        self.state['merged_before_edit'] = {}
        held = []
        for spec in self.specs:
            matches = self.merged_matches(spec, edited=False)
            assert len(matches) == 1
            keymap, item = matches[0]
            self.state['merged_before_edit'][spec['name']] = next(
                row for row in self.fixture.capture(keymap)['items'] if row['blender_id'] == item.id)
            item.map_type = 'KEYBOARD'
            item.type = spec['edited_key']
            for name in ('value', 'any', 'shift', 'ctrl', 'alt', 'oskey',
                         'key_modifier', 'direction', 'repeat'):
                setattr(item, name, sources[spec['name']]['row']['event'][name])
            item.active = spec['edited_active']
            if 'edited_radius' in spec:
                item.properties.radius = spec['edited_radius']
            held.append(item)
        self.state['save_result'] = sorted(self.bpy.ops.wm.save_userpref())
        self.state['immediate_save'] = True
        # Save can invalidate merged wrappers. Never use them for assertions.
        self.state['held_wrappers_after_save'] = []
        for item in held:
            try:
                self.state['held_wrappers_after_save'].append({'id': item.id, 'target': item.idname,
                                                              'type': item.type, 'active': item.active})
            except (ReferenceError, RuntimeError) as error:
                self.state['held_wrappers_after_save'].append({'read_error': type(error).__name__})
        saved = self.root / 'saved-cases'
        saved.mkdir()
        shutil.copyfile(self.root / 'config/userpref.blend', saved / 'userpref.blend')
        after = {spec['name']: self.owned_source(spec) for spec in self.specs}
        self.state['source_after_save'] = after
        self.state['declared_sources_unchanged'] = sources == after
        self.record('production_persistence_immediate_save_recorded')
        assert sources == after
        self.configs.update()
        for spec in self.specs:
            self.observe_edited(spec, sources[spec['name']])
        manifest = {'scenario': self.scenario, 'edits': self.specs,
                    'preference_sha256': self.sha(saved / 'userpref.blend'),
                    'executed_sources': self.executed_sources(), 'declared_sources': sources}
        (saved / 'category-persistence-expected.json').write_text(json.dumps(manifest, indent=2) + '\n')
        self.state['saved_manifest'] = manifest

    def check_restored(self):
        restored = {}
        for spec in self.specs:
            expected = self.state['declared_sources'][spec['name']]
            actual = self.owned_source(spec)
            for key in ('owner_id', 'request_id', 'scope', 'assignment'):
                assert actual[key] == expected[key], (spec['name'], key)
            assert {k: v for k, v in actual['row'].items() if k != 'blender_id'} == {
                k: v for k, v in expected['row'].items() if k != 'blender_id'}
            restored[spec['name']] = self.observe_edited(spec, actual)
        self.state['restorations'].append(restored)
        self.record('production_persistence_saved_edits_restored')

    def append(self, steps):
        steps.append(self.setup)
        self.fixture.append_matched_endpoint('before_production_persistence')
        steps.extend((self.fixture.start, lambda: self.toggle(True)))
        steps.append(self.check_restored if self.reopen else self.save)
        steps.append(lambda: self.toggle(False))
        self.fixture.append_matched_endpoint('after_first_persistence_release')
        steps.extend((lambda: self.toggle(True), self.check_restored, lambda: self.toggle(False)))
        self.fixture.append_matched_endpoint('after_second_persistence_release')
        steps.append(self.fixture.cleanup)
        return self
