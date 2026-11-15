"""Exact default disables must restore without touching changed or foreign rows."""

import importlib
from dataclasses import replace
import unittest
from unittest.mock import patch

import test_deluxe_profiles
from runtime_keymap_fakes import row


class DefaultBindingTests(unittest.TestCase):
    def setUp(self):
        harness = test_deluxe_profiles.ProfileTests()
        harness.setUp()
        self.addCleanup(harness.doCleanups)
        self.h = harness
        self.api = importlib.import_module('_deluxe_profiles_test.keymaps.default_bindings')
        self.addCleanup(self.api.release_all)
        self.map = harness.runtime.map('default', 'Object Mode', space='EMPTY', tool=False)
        self.item = self.map.keymap_items.append_fixture(row('object.select_all', prop_values={'action': 'SELECT'}))
        self.selector = harness.core.capture_selector(self.map, self.item)

    def test_disable_merged_binding_and_restore_exact_default(self):
        self.assertEqual(self.api.status(self.selector), ('resolved', ''))
        self.api.install('rule', self.selector)
        self.assertFalse(self.item.active)
        merged = self.h.runtime.configs.user.keymaps.get('Object Mode')
        self.assertFalse(merged.keymap_items.rows[0].active)
        self.assertEqual(self.api.managed_rule(merged, merged.keymap_items.rows[0])[0], 'rule')
        self.api.release_all()
        self.assertTrue(self.item.active)
        self.assertFalse(self.api.pending_cleanup())

    def test_changed_source_is_preserved_and_identical_replacement_not_touched(self):
        self.api.install('rule', self.selector)
        self.item.type = 'B'
        self.api.release_all()
        self.assertFalse(self.item.active)
        self.item.type, self.item.active = 'A', True
        self.api.install('rule', self.selector)
        self.map.keymap_items.remove(self.item)
        lookalike = self.map.keymap_items.append_fixture(row('object.select_all', prop_values={'action': 'SELECT'}, active=False))
        self.api.release_all()
        self.assertFalse(lookalike.active)

    def test_ambiguous_or_native_user_modified_source_is_rejected(self):
        duplicate = self.map.keymap_items.append_fixture(row('object.select_all', prop_values={'action': 'SELECT'}))
        self.assertEqual(self.api.status(self.selector)[0], 'ambiguous')
        self.api.install('rule', self.selector)
        self.assertTrue(self.item.active)
        self.map.keymap_items.remove(duplicate)
        self.item.is_user_modified = True
        self.assertEqual(self.api.status(self.selector), ('unsupported', 'user_binding_modified'))

    def test_failed_readback_restores_source_and_unreadable_release_retries(self):
        with patch.object(self.api, '_merged_item', side_effect=[self.item, RuntimeError('readback failed')]):
            with self.assertRaisesRegex(RuntimeError, 'readback failed'):
                self.api.install('rule', self.selector)
        self.assertTrue(self.item.active)
        self.api.install('rule', self.selector)
        with patch.object(self.h.core, '_snapshot', side_effect=self.h.core._Pending('unreadable_property_schema')):
            self.assertTrue(self.api.release_all())
        self.assertFalse(self.item.active)
        self.api.retry_cleanup()
        self.assertTrue(self.item.active)

    def test_native_user_edit_is_not_reported_as_an_applied_disable(self):
        self.api.install('rule', self.selector)
        with patch.object(self.api, '_merged_item', side_effect=self.h.core._Pending('user_binding_modified', 'unsupported')):
            self.assertEqual(self.api.status(self.selector), ('unsupported', 'user_binding_modified'))
            self.assertEqual(self.api.registration_results()['rule'][0], 'pending')
        self.assertFalse(self.item.active)
        self.api.release_all()
        self.assertTrue(self.item.active)

    def test_addon_rule_detects_merged_origin_and_follows_enable_reload_disable(self):
        map_ = self.h.runtime.map('addon', '3D View', space='VIEW_3D', tool=False)
        item = map_.keymap_items.append_fixture(row('provider.action', prop_values={'mode': 'A'}))
        selector = self.h.core.capture_selector(map_, item, source_role='addon')
        candidate = self.h.resolver.capture_candidate(map_, item, 'addon')
        self.assertTrue(candidate['can_disable'])
        self.assertEqual(candidate['selector']['source_role'], 'addon')
        inherited, reason = self.h.resolver._inherited_source(replace(selector, source_role='user'))
        self.assertEqual(inherited, selector)
        self.assertFalse(reason)
        map_.keymap_items.remove(item)
        self.api.install('provider', selector)
        self.assertEqual(self.api.registration_results()['provider'][0], 'pending')
        item = map_.keymap_items.append_fixture(row('provider.action', prop_values={'mode': 'A'}))
        self.api.reconcile()
        self.assertFalse(item.active)
        map_.keymap_items.remove(item)
        item = map_.keymap_items.append_fixture(row('provider.action', prop_values={'mode': 'A'}))
        self.api.reconcile()
        self.assertFalse(item.active)
        self.api.release_all()
        self.assertTrue(item.active)
        self.assertEqual(self.api.reconcile(), 0)

    def test_addon_native_edit_survives_watcher_and_removal(self):
        map_ = self.h.runtime.map('addon', '3D View', space='VIEW_3D', tool=False)
        item = map_.keymap_items.append_fixture(row('provider.action'))
        selector = self.h.core.capture_selector(map_, item, source_role='addon')
        self.api.install('provider', selector)
        item.type, item.active = 'B', True
        self.api.reconcile()
        self.assertTrue(item.active)
        self.api.release_all()
        self.assertEqual(item.type, 'B')
        self.assertTrue(item.active)

    def test_legacy_addon_rule_resolves_exact_snapshot_and_refuses_ambiguity(self):
        map_ = self.h.runtime.map('addon', '3D View', space='VIEW_3D', tool=False)
        item = map_.keymap_items.append_fixture(row('provider.action', prop_values={'mode': 'A', 'new_default': 7}))
        selector = self.h.core.capture_selector(map_, item, source_role='addon')
        legacy = replace(selector, target=self.h.core.KeymapTarget('provider.action', {'mode': 'A'}))
        self.api.install('legacy', legacy, explicit_properties=True)
        self.assertFalse(item.active)
        self.assertEqual(self.api.status(legacy, explicit_properties=True), ('resolved', ''))
        self.api.release_all()
        self.assertTrue(item.active)
        duplicate = map_.keymap_items.append_fixture(row('provider.action', prop_values={'mode': 'A', 'new_default': 8}))
        self.api.install('legacy', legacy, explicit_properties=True)
        self.assertTrue(item.active)
        self.assertTrue(duplicate.active)
        self.assertEqual(self.api.status(legacy, explicit_properties=True)[0], 'ambiguous')
        map_.keymap_items.remove(duplicate)
        self.api.reconcile()
        self.assertFalse(item.active)

    def test_addon_disable_has_no_assumption_about_merged_item_ids(self):
        map_ = self.h.runtime.map('addon', '3D View', space='VIEW_3D', tool=False)
        item = map_.keymap_items.append_fixture(row('provider.action'))
        selector = self.h.core.capture_selector(map_, item, source_role='addon')
        # The actual Blender merger renumbers these IDs independently.
        with patch.object(type(item), 'merged_copy', autospec=True, side_effect=lambda original: original.clone()):
            self.api.install('provider', selector)
            self.assertFalse(item.active)
            self.assertEqual(self.api.status(selector), ('resolved', ''))


if __name__ == '__main__':
    unittest.main()
