"""Regressions from the 4.5.1 userprefs / 5.2.2 clean-profile comparison."""
from dataclasses import replace
import importlib
import json
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import patch

import test_deluxe_profiles
import test_keymap_runtime
from runtime_keymap_fakes import row


class RuntimeParityTests(unittest.TestCase):
    def setUp(self):
        self.h = test_keymap_runtime.RuntimeKeymapTests()
        self.h.setUp()
        self.addCleanup(self.h.doCleanups)
        self.core, self.runtime = self.h.utils, self.h.runtime
        self.addCleanup(self.core.release_all)

    def test_unloaded_operator_is_checked_before_its_freed_property_rna(self):
        self.h.addon()
        self.runtime.bpy.app = SimpleNamespace(version=(5, 2, 2))
        operator = SimpleNamespace(get_rna_type=lambda: object())
        self.runtime.bpy.ops = SimpleNamespace(bluehole=SimpleNamespace(replacement=operator))
        handle = self.core.register_feature('provider', assignments=(self.h.assignment(),))
        self.assertEqual(len(handle.owned_pairs), 1)
        item = handle.owned_pairs[0][1]
        class PoisonedProperties:
            @property
            def bl_rna(self):
                raise AssertionError('Freed property RNA must never be dereferenced')
        item.properties = PoisonedProperties()
        del self.runtime.bpy.ops.bluehole.replacement
        handle.release()
        self.assertEqual(self.core.pending_cleanup()[0]['reason'], 'owned_snapshot_unavailable')
        # Provider removal eventually deletes its native item; cleanup then drains.
        self.runtime.configs.addon.keymaps.get('3D View').keymap_items.remove(item)
        self.core.retry_unreadable_cleanup(16)
        self.assertFalse(self.core.pending_cleanup())

    def test_modal_alias_precedes_wildcard_and_releases_without_touching_source(self):
        km = self.runtime.map('default', 'Knife Tool Modal Map', space='EMPTY', modal=True)
        original = km.keymap_items.append_fixture(row('', key='LEFTMOUSE', value='ANY',
                                                     any=True, modal_value='ADD_CUT'))
        request = self.core.KeymapAssignment('pan', self.core.capture_scope(km),
            self.core.KeymapEvent('LEFTMOUSE', alt=True, map_type='MOUSE'),
            self.core.KeymapTarget(modal_value='PANNING'))
        handle = self.core.register_feature('modal', assignments=(request,))
        self.assertEqual([x.propvalue for x in km.keymap_items], ['PANNING', 'ADD_CUT'])
        self.assertEqual(handle.diagnostics[0].status, 'applied')
        handle.release()
        self.assertEqual(list(km.keymap_items), [original])
        self.assertFalse(self.runtime.configs.addon.keymaps.rows)

    def test_missing_menu_stays_pending_then_registers_and_withdraws_on_unload(self):
        self.h.addon().keymap_items.new_prop_schema = {'name': ''}
        self.runtime.bpy.types = SimpleNamespace()
        request = replace(self.h.assignment(target=self.core.KeymapTarget('wm.call_menu', {'name':'PROVIDER_MT_menu'})),
                          required_class='PROVIDER_MT_menu')
        handle = self.core.register_feature('menu', assignments=(request,))
        self.assertEqual(handle.diagnostics[0].reason, 'waiting_for_provider')
        self.assertFalse(handle.owned_pairs)
        self.runtime.bpy.types.PROVIDER_MT_menu = type('Menu', (), {})
        handle.refresh()
        self.assertEqual(len(handle.owned_pairs), 1)
        del self.runtime.bpy.types.PROVIDER_MT_menu
        handle.refresh()
        self.assertFalse(handle.owned_pairs)
        self.assertEqual(handle.diagnostics[0].reason, 'waiting_for_provider')

    def test_reviewed_poll_chain_does_not_allow_unrelated_event_collision(self):
        self.h.addon()
        a = replace(self.h.assignment('a'), dispatch_group='reviewed')
        b = replace(self.h.assignment('b', target=self.h.target('other.action')), dispatch_group='reviewed')
        first = self.core.register_feature('a', assignments=(a,))
        second = self.core.register_feature('b', assignments=(b,))
        unrelated = self.core.register_feature('c', assignments=(self.h.assignment('c'),))
        self.assertEqual((len(first.owned_pairs), len(second.owned_pairs)), (1, 1))
        self.assertIn('conflicting_assignment', self.h.reasons(unrelated))

    def test_extension_namespace_dependency_and_partial_modal_failure(self):
        request = replace(self.h.assignment(), required_addon='ZenUV')
        module = SimpleNamespace(__addon_enabled__=True)
        with patch.dict(sys.modules, {'bl_ext.example.ZenUV': module}):
            self.assertTrue(self.core._assignment_dependency_ready(request))
            module.__addon_enabled__ = False
            self.assertFalse(self.core._assignment_dependency_ready(request))
        km = self.runtime.map('default', 'Transform Modal Map', space='EMPTY', modal=True)
        original = km.keymap_items.append_fixture(row('', key='G', modal_value='TRANSLATE'))
        request = self.core.KeymapAssignment('move', self.core.capture_scope(km),
            self.core.KeymapEvent('W'), self.core.KeymapTarget(modal_value='TRANSLATE'))
        km.keymap_items.fail_after_create = True
        handle = self.core.register_feature('modal-failure', assignments=(request,))
        self.assertFalse(handle.owned_pairs)
        self.assertEqual(list(km.keymap_items), [original])
        copy = km.keymap_items.new_from_item
        def broken_copy(*args, **kwargs):
            copy(*args, **kwargs)
            raise RuntimeError('failed after native copy')
        with patch.object(km.keymap_items, 'new_from_item', side_effect=broken_copy):
            handle.refresh()
        self.assertEqual(list(km.keymap_items), [original])

    def test_macro_properties_and_gesture_collections_detect_later_edits(self):
        class Group:
            def __init__(self, schema, **values):
                self.bl_rna = SimpleNamespace(properties=schema)
                self.__dict__.update(values)
        self.runtime.bpy.types = SimpleNamespace(OperatorProperties=Group)
        value_prop = SimpleNamespace(identifier='release_confirm', type='BOOLEAN')
        macro_type = SimpleNamespace(identifier='OperatorProperties', base=None)
        child_prop = SimpleNamespace(identifier='TRANSFORM_OT_translate', type='POINTER', fixed_type=macro_type)
        path_prop = SimpleNamespace(identifier='path', type='COLLECTION')
        child = Group([value_prop], release_confirm=False)
        item = SimpleNamespace(properties=Group([child_prop, path_prop], TRANSFORM_OT_translate=child, path=[]))
        before = self.core._properties(item)
        requested = self.core.KeymapTarget('mesh.duplicate_move', {'TRANSFORM_OT_translate': {'release_confirm': True}})
        for name, value in requested.properties:self.core._set_property(item, name, value)
        after = self.core._properties(item)
        self.assertNotEqual(before, after)
        self.assertTrue(self.core._declared_properties_match(after, requested.properties))
        self.assertTrue(self.core._declared_properties_match(after, (('TRANSFORM_OT_translate', ()),)))
        item.properties.path.append(Group([value_prop], release_confirm=True))
        self.assertNotEqual(after, self.core._properties(item))


class CatalogParityTests(unittest.TestCase):
    def setUp(self):
        self.h = test_deluxe_profiles.ProfileTests()
        self.h.setUp()
        self.addCleanup(self.h.doCleanups)
        self.catalog = self.h.api.deluxe_catalog.load(test_deluxe_profiles.DEFAULTS)

    def bindings(self, scope, operator):
        c = self.catalog
        return [(r, c['events'][r['event']], c['commands'][r['command']])
                for r in c['assignments'].values() if r['scope']['name'] == scope
                and c['commands'][r['command']].get('operator', c['commands'][r['command']].get('modal_value')) == operator]

    def test_provider_and_editor_shortcuts_are_declared_without_userprefs(self):
        cases = [('3D View', 'hops.bev_multi', 'Q', {'alt': 1}),
                 ('3D View', 'hops.helper', 'Q', {'alt': 1, 'shift': 1, 'value': 'CLICK'}),
                 ('3D View', 'view3d.dreamuv_hotspotter', 'MIDDLEMOUSE', {'ctrl': 1, 'shift': 1, 'alt': 1}),
                 ('3D View', 'mesh.smart_delete', 'D', {'alt': 1}),
                 ('Window', 'wm.sticky_uv_editor', 'SPACE', {'ctrl': 1, 'alt': 1}),
                 ('UV Editor', 'uv.zenuv_isolate_island', 'S', {}),
                 ('Curves', 'wm.bh_tool_select_box_xray_curves', 'Q', {'value': 'CLICK'}),
                 ('Node Editor', 'node.view_all', 'A', {}),
                 ('Node Editor', 'node.view_selected', 'F', {}),
                 ('Node Editor', 'node.select_box', 'Q', {}),
                 ('Dopesheet', 'action.view_all', 'A', {}),
                 ('Graph Editor', 'graph.keyframe_insert', 'S', {}),
                 ('Sequencer', 'sequencer.view_all', 'A', {}),
                 ('Transform Modal Map', 'TRANSLATE', 'W', {}),
                 ('Transform Modal Map', 'ROTATE', 'E', {}),
                 ('Transform Modal Map', 'RESIZE', 'R', {}),
                 ('Transform Modal Map', 'SNAP_TOGGLE', 'X', {}),
                 ('Knife Tool Modal Map', 'CONFIRM', 'Q', {}),
                 ('View3D Walk Modal', 'CONFIRM', 'MIDDLEMOUSE', {'value': 'RELEASE'})]
        for scope, op, key, options in cases:
            with self.subTest(scope=scope, operator=op):
                self.assertTrue(any(e['type'] == key and all(e.get(k) == v for k,v in options.items())
                                    for r,e,c in self.bindings(scope, op)))
        for tool, op in [('Move','translate'), ('Rotate','rotate'), ('Scale','resize')]:
            self.assertTrue(any(e['type']=='LEFTMOUSE' and e['value']=='CLICK_DRAG' and cmd['properties']['release_confirm']
                                for r,e,cmd in self.bindings('3D View Tool: '+tool, 'transform.'+op+'_auto_constraint')))
            self.assertNotIn('legacy-addon-disable-3d-view-tool-'+tool.lower()+'-0', self.catalog['suppressions'])
        translate = self.bindings('3D View', 'transform.translate')
        self.assertTrue(any(not r['active'] for r,e,c in translate if c['properties'].get('cursor_transform')))

    def test_missing_provider_rows_survive_preview_and_both_signs_are_pending(self):
        model = importlib.import_module('_deluxe_profiles_test.preferences.addon.keymaps.deluxe_editor_model')
        store = self.h.api.ProfileStore(self.catalog, self.h.path, lambda: self.h.settings, lambda *_: None)
        editor = model.Editor(store)
        self.h.runtime.bpy.types = SimpleNamespace()
        preview = store.preview()
        for ids in preview['conflicts']:
            groups = {self.catalog['assignments'][id_].get('dispatch_group') for id_ in ids}
            self.assertFalse(len(groups) == 1 and None not in groups, 'Reviewed poll chain reported as a conflict')
        for op in ('node.nw_merge_nodes', 'machin3.focus', 'uv.toolkit_unwrap_selected'):
            ids = [i for i,r in self.catalog['assignments'].items() if self.catalog['commands'][r['command']].get('operator') == op]
            self.assertTrue(ids)
            for id_ in ids:
                self.assertIn(id_, preview['assignments'])
                self.assertTrue(editor.binding_pending(id_, preview))
                self.assertEqual(editor.binding_origin(id_, preview)[0], 'ADD')
        id_ = 'legacy-addon-disable-mesh-28'
        self.assertTrue(editor.binding_pending(id_, preview))
        self.assertEqual(editor.binding_origin(id_, preview)[0], 'REMOVE')

    def test_removal_is_independent_of_same_shortcut_assignment(self):
        core = self.h.core
        api = importlib.import_module('_deluxe_profiles_test.keymaps.default_bindings')
        self.addCleanup(api.release_all)
        self.addCleanup(core.release_all)
        km = self.h.runtime.map('default','Object Mode',space='EMPTY',tool=False)
        source = km.keymap_items.append_fixture(row('transform.translate', key='G'))
        selector = core.capture_selector(km,source)
        api.install('rule', selector)
        self.assertFalse(source.active)
        self.h.runtime.map('addon','Object Mode',space='EMPTY',tool=False)
        assignment = core.KeymapAssignment('provider',core.capture_scope(km),core.KeymapEvent('G'),core.KeymapTarget('provider.move'))
        handle = core.register_feature('provider',assignments=(assignment,))
        api.reconcile()
        self.assertFalse(source.active)
        handle.release()
        api.reconcile()
        self.assertFalse(source.active)
        self.assertEqual(api.registration_results()['rule'], ('applied',''))
        api.release_all()
        self.assertTrue(source.active)

    def test_hardops_shift_q_removal_resolves_without_meshmachine(self):
        model = importlib.import_module('_deluxe_profiles_test.preferences.addon.keymaps.deluxe_editor_model')
        store = self.h.api.ProfileStore(self.catalog, self.h.path, lambda: self.h.settings, lambda *_: None)
        editor = model.Editor(store)
        self.h.runtime.bpy.types = SimpleNamespace()
        km = self.h.runtime.map('addon', '3D View', space='VIEW_3D')
        km.keymap_items.append_fixture(row('wm.call_menu_pie', key='Q', shift=True,
                                          prop_values={'name': 'HOPS_MT_MainPie'}))
        preview = store.preview()
        rule = 'parity-disable-400848e85e7b'
        self.assertEqual(preview['suppressions'][rule]['status'], 'resolved')
        self.assertEqual(editor.rule_status(rule, preview), 'Exact target resolved')
        preview['suppressions'][rule]['eligible'] = False
        self.assertEqual(editor.rule_status(rule, preview), 'Rule inactive')
        self.assertTrue(editor.binding_origin(rule, preview)[1].endswith('Inactive'))

    def test_legacy_assignment_dependencies_are_migrated_without_losing_rule_edits(self):
        rule = 'parity-disable-400848e85e7b'
        overlay = dict(schema_version=self.catalog['schema_version'], catalog_version=self.catalog['catalog_version'],
                       base=self.catalog['base']['preset'], changes={'suppressions': {
                           rule: {'enabled': False, 'requires_assignment': 'removed-assignment'}}})
        self.h.path.write_text(json.dumps(overlay))
        store = self.h.api.ProfileStore(self.catalog, self.h.path, lambda: self.h.settings, lambda *_: None)
        self.assertIsNone(store.load_issue)
        self.assertTrue(store.needs_migration)
        self.assertFalse(store.snapshot()['suppressions'][rule]['enabled'])
        self.assertNotIn('requires_assignment', store.snapshot()['suppressions'][rule])
        store.apply(store.begin())
        self.assertNotIn('requires_assignment', self.h.path.read_text())

    def test_modal_assignment_is_not_reported_as_its_own_inherited_conflict(self):
        core = self.h.core
        self.addCleanup(core.release_all)
        km = self.h.runtime.map('default','Transform Modal Map',space='EMPTY',modal=True)
        km.keymap_items.append_fixture(row('', key='G', modal_value='TRANSLATE'))
        scope, event = core.capture_scope(km), core.KeymapEvent('W')
        assignment = core.KeymapAssignment('alias', scope, event, core.KeymapTarget(modal_value='TRANSLATE'))
        core.register_feature('modal', assignments=(assignment,))
        self.assertEqual(self.h.api.ProfileStore._inherited_conflicts({(scope,event): ['alias']}), {})
        km.keymap_items.append_fixture(row('', key='W', modal_value='OTHER'))
        self.assertEqual(self.h.api.ProfileStore._inherited_conflicts({(scope,event): ['alias']}), {'alias': ('OTHER',)})

if __name__ == '__main__': unittest.main()
