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
        changed = deepcopy(catalog)
        changed['assignments']['view-frame']['enabled'] = False
        with patch.object(self.rules, 'release', wraps=self.rules.release) as release:
            self.store.update_registration(changed, catalog)
            release.assert_not_called()
        self.assertFalse(source.active)
        self.assertEqual(self.rules.registration_results()['rule'], ('applied', ''))

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

    def fast_editor(self):
        self.h.runtime.bpy.types = SimpleNamespace()
        rna = SimpleNamespace(name='Frame', properties={})
        self.h.runtime.bpy.ops.view3d.view_selected.get_rna_type = lambda: rna
        self.store._install_toggle = lambda candidate, previous, plans: self.store.update_registration(
            candidate, previous, plans=plans, verify=True)
        self.store.register()
        model = importlib.import_module('_deluxe_profiles_test.preferences.addon.keymaps.deluxe_editor_model')
        editor = model.Editor(self.store)
        editor.preview()
        return editor

    def assert_fresh_preview(self, editor):
        previous = deepcopy(editor.preview())
        self.store._preview_cache = None
        self.assertEqual(previous, self.store.preview(editor.draft))

    def test_boolean_edit_reuses_metadata_and_checks_only_affected_native_rows(self):
        editor = self.fast_editor()
        preview = editor.preview()
        unaffected = self.image.keymap_items[0]
        with patch.object(self.store, '_validate', side_effect=AssertionError('full validation on Boolean edit')):
            editor.set_enabled('assignments', 'view-frame', False)
            self.assertIs(editor.preview(), preview)
            self.assertFalse(preview['assignments']['view-frame']['eligible'])
            self.assertFalse(preview['assignments']['view-frame']['registered'])
            editor.set_enabled('assignments', 'view-frame', True)
        self.assertTrue(preview['assignments']['view-frame']['registered'])
        self.assertIs(self.image.keymap_items[0], unaffected)
        self.assert_fresh_preview(editor)
        self.assertEqual(editor._preview_token, self.store.preview_token(editor.catalog))

    def test_fast_toggle_is_undoable_and_does_not_mutate_saved_or_undo_snapshots(self):
        editor = self.fast_editor()
        before = deepcopy(editor.catalog)
        editor.set_enabled('assignments', 'view-frame', False)
        self.assertEqual(self.store.snapshot(), before)
        self.assertEqual(editor._undo[-1], before)
        editor.undo()
        self.assertEqual(editor.catalog, before)
        self.assertFalse(self.h.path.exists())

    def test_fast_rule_toggle_updates_source_and_matches_a_fresh_preview(self):
        source = self.view.keymap_items.append_fixture(row('wm.call_menu', key='Q', prop_values={'name':'Original'}))
        self.store._catalog['suppressions']['rule'] = dict(section='framing', disable=True,
            selector=self.h.resolver.selector_data(self.core.capture_selector(self.view, source, source_role='addon')))
        editor = self.fast_editor()
        native_rows = [item.as_pointer() for item in self.view.keymap_items]
        for enabled in (False, True):
            with patch.object(self.store, '_validate', side_effect=AssertionError('full validation on Boolean edit')):
                editor.set_enabled('suppressions', 'rule', enabled)
            self.assertEqual(source.active, not enabled)
            self.assertEqual([item.as_pointer() for item in self.view.keymap_items], native_rows)
            preview = editor.preview()
            self.assert_fresh_preview(editor)
            self.assertEqual(editor._preview_token, self.store.preview_token(editor.catalog))

    def test_unvalidated_structural_edit_cannot_use_boolean_fast_path(self):
        editor = self.fast_editor()
        editor.draft.update('events', 'frame', type='not a key')
        self.assertIsNone(self.store.toggle_enabled(editor.draft, 'assignments', 'view-frame', {'enabled':False}))
        with self.assertRaises(ValueError):
            self.store.preview_draft(editor.draft)

    def test_failed_fast_toggle_restores_previous_runtime_and_discards_fast_cache(self):
        editor = self.fast_editor()
        previous = self.store.runtime_catalog()
        self.store._install_toggle = lambda *args: (_ for _ in ()).throw(RuntimeError('injected toggle failure'))
        with patch.object(self.store, '_install') as install:
            with self.assertRaisesRegex(RuntimeError, 'injected'):
                editor.set_enabled('assignments', 'view-frame', False)
            install.assert_called_once_with(previous, None)
        self.assertIsNone(self.store._preview_cache)
        self.assertEqual(editor.catalog, previous)

    def test_native_configuration_or_provider_change_invalidates_fast_toggle(self):
        editor = self.fast_editor()
        self.h.runtime.replace_config('addon')
        self.assertIsNone(self.store.toggle_enabled(editor.draft, 'assignments', 'view-frame', {'enabled':False}))
        editor = self.fast_editor()
        del self.h.runtime.bpy.ops.view3d.view_selected
        self.assertIsNone(self.store.toggle_enabled(editor.draft, 'assignments', 'view-frame', {'enabled':False}))

    def test_category_and_section_toggles_match_fresh_previews_without_full_validation(self):
        editor = self.fast_editor()
        for table, key in [('sections', 'framing'), ('categories', 'navigation')]:
            for enabled in (False, True):
                with patch.object(self.store, '_validate', side_effect=AssertionError('full Boolean validation')):
                    editor.set_enabled(table, key, enabled)
                self.assert_fresh_preview(editor)
                self.assertEqual(editor.preview()['sections']['framing'], enabled)

    def test_structural_edit_reuses_untouched_rna_and_matches_full_read_model(self):
        editor = self.fast_editor()
        command = editor.catalog['assignments']['view-frame']['command']
        with patch.object(self.store.resolver, 'validate_command', wraps=self.store.resolver.validate_command) as validate:
            editor.draft.update('commands', command, label='My framing')
            editor.changed()
            self.assertFalse(editor.preview_error)
            editor.preview()
            self.assertEqual([call.args[1] for call in validate.call_args_list], [command])
        self.assert_fresh_preview(editor)
        for key in ('G', 'H'):
            editor.draft.update('events', 'frame', type=key)
            editor.changed()
            self.assertFalse(editor.preview_error)
            self.assertEqual(self.view.keymap_items[0].type, key)
            self.assert_fresh_preview(editor)

    def test_deleted_assignment_is_removed_from_cached_diagnostics(self):
        editor = self.fast_editor()
        editor.draft.delete('assignments', 'view-frame')
        editor.changed()
        self.assertFalse(editor.preview_error)
        self.assertNotIn('view-frame', editor.preview()['assignments'])
        self.assert_fresh_preview(editor)


if __name__ == '__main__':
    unittest.main()
