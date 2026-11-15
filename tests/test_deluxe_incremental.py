"""Edits retain unrelated native items and the order within touched contexts."""
from copy import deepcopy
import importlib
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import test_deluxe_profiles
from runtime_keymap_fakes import row


class IncrementalTests(unittest.TestCase):
    def setUp(self):
        self.h = test_deluxe_profiles.ProfileTests()
        self.h.setUp()
        self.addCleanup(self.h.doCleanups)
        self.core, self.store = self.h.core, self.h.store
        self.rules = importlib.import_module('_deluxe_profiles_test.keymaps.default_bindings')
        self.addCleanup(self.core.release_all)
        self.addCleanup(self.rules.release_all)
        self.view = self.h.runtime.map('addon', '3D View')
        self.image = self.h.runtime.map('addon', 'Image', space='IMAGE_EDITOR')
        for km in (self.view, self.image):
            km.keymap_items.new_prop_schema = {'use_all_regions': False}
        operator = SimpleNamespace(get_rna_type=lambda: SimpleNamespace(name='Frame', properties=[]))
        self.h.runtime.bpy.ops = SimpleNamespace(view3d=SimpleNamespace(view_selected=operator))

    def test_toggle_rebuilds_only_its_context_and_restores_source_order(self):
        catalog = self.store.snapshot()
        catalog['events']['second'] = {'type': 'G'}
        catalog['commands']['second'] = deepcopy(catalog['commands']['frame-selected'])
        catalog['assignments']['second'] = dict(catalog['assignments']['view-frame'],
            feature='second', event='second', command='second', order=3)
        self.store.register(catalog)
        unaffected = self.image.keymap_items[0]
        original = [(item.type, item.idname) for item in self.view.keymap_items]
        changed = deepcopy(catalog)
        changed['assignments']['view-frame']['enabled'] = False
        self.store.update_registration(changed, catalog)
        self.assertEqual([item.type for item in self.view.keymap_items], ['G'])
        self.assertIs(self.image.keymap_items[0], unaffected)
        self.store.update_registration(catalog, changed)
        self.assertEqual([(item.type, item.idname) for item in self.view.keymap_items], original)
        self.assertIs(self.image.keymap_items[0], unaffected)

    def test_disable_rule_toggle_does_not_rebuild_any_added_binding(self):
        source = self.view.keymap_items.append_fixture(row('wm.call_menu', key='Q', prop_values={'name':'Original'}))
        catalog = self.store.snapshot()
        catalog['suppressions']['rule'] = dict(section='framing', disable=True,
            selector=self.h.resolver.selector_data(self.core.capture_selector(self.view, source, source_role='addon')))
        self.store.register(catalog)
        self.assertFalse(source.active)
        before = [item.as_pointer() for item in self.view.keymap_items]
        changed = deepcopy(catalog)
        changed['suppressions']['rule']['enabled'] = False
        self.store.update_registration(changed, catalog)
        self.assertTrue(source.active)
        self.assertEqual([item.as_pointer() for item in self.view.keymap_items], before)
        self.store.update_registration(catalog, changed)
        self.assertFalse(source.active)
        self.assertEqual([item.as_pointer() for item in self.view.keymap_items], before)

    def test_command_edit_preserves_an_unrelated_native_edit(self):
        catalog = self.store.snapshot()
        self.store.register(catalog)
        unaffected = self.image.keymap_items[0]
        unaffected.type = 'H'
        changed = deepcopy(catalog)
        command = changed['assignments']['view-frame']['command']
        changed['commands'][command]['properties']['use_all_regions'] = True
        self.store.update_registration(changed, catalog)
        self.assertTrue(self.view.keymap_items[0].properties.use_all_regions)
        self.assertIs(self.image.keymap_items[0], unaffected)
        self.assertEqual(unaffected.type, 'H')

    def test_saving_an_already_previewed_edit_does_not_reinstall_it(self):
        draft = self.store.begin()
        draft.update('assignments', 'view-frame', enabled=False)
        with patch.object(self.store, '_install', wraps=self.store._install) as install:
            self.store.preview_draft(draft)
            self.store.apply(draft)
            self.assertEqual(install.call_count, 1)
        self.assertFalse(self.store.snapshot()['assignments']['view-frame']['enabled'])


if __name__ == '__main__':
    unittest.main()
