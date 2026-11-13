"""Artist editor workflows against brief 08's synthetic profile and store."""

import importlib
import unittest
from types import SimpleNamespace

import test_deluxe_profiles
from runtime_keymap_fakes import row


class EditorTests(unittest.TestCase):
    def setUp(self):
        harness = test_deluxe_profiles.ProfileTests()
        harness.setUp()
        self.addCleanup(harness.doCleanups)
        self.h = harness
        self.editor_module = importlib.import_module(
            '_deluxe_profiles_test.preferences.addon.keymaps.deluxe_editor_model')
        self.editor = self.editor_module.Editor(harness.store)

    def test_shared_and_local_edits_then_discard(self):
        editor = self.editor
        editor.stage_event('view-frame', {'type': 'F11'}, shared=True)
        self.assertEqual(editor.catalog['events']['frame']['type'], 'F11')
        editor.stage_event('image-frame', {'type': 'F12'}, shared=False)
        changed = editor.catalog['assignments']['image-frame']['event']
        self.assertNotEqual(changed, 'frame')
        self.assertEqual(editor.catalog['events'][changed]['type'], 'F12')
        self.assertEqual(editor.draft.uses('events', 'frame'), ('view-frame',))
        self.assertEqual(editor.store.snapshot(), self.h.defaults)
        editor.discard()
        self.assertFalse(editor.dirty)
        self.assertEqual(editor.catalog, self.h.defaults)

    def test_typed_key_search_matches_modifiers_and_key_names(self):
        labels = {'F10': 'F10', 'F11': 'F11', 'RIGHTMOUSE': 'Right Mouse',
                  'NUMPAD_PLUS': 'Numpad +', 'A': 'A'}
        search = self.editor_module.key_filter
        for query in ('shift F10', 'Shift+F10', 'Shift + F10'):
            matches = search(query, labels)
            self.assertTrue(matches({'type': 'F10', 'shift': 1, 'ctrl': True}))
            self.assertFalse(matches({'type': 'F10'}))
            self.assertFalse(matches({'type': 'F11', 'shift': True}))
        self.assertTrue(search('cmd RMB', labels)({'type': 'RIGHTMOUSE', 'oskey': True}))
        self.assertTrue(search('Shift +', labels)({'type': 'NUMPAD_PLUS', 'shift': True}))
        self.assertTrue(search('A', labels)({'type': 'F10', 'key_modifier': 'A'}))
        self.assertFalse(search('unknown-key', labels)({'type': 'F10'}))

    def test_section_mapping_move_and_persist(self):
        editor = self.editor
        editor.edit_section('Artist tools')
        id_ = editor.section
        editor.edit_section('My framing', id_)
        editor.reorder_section(-1)
        self.assertEqual(editor.sections(), ['framing', id_, 'overview'])
        mapping = editor.draft.add_assignment(id_, 'provider-fit', 'frame-selected',
                                             {'name': '3D View', 'space_type': 'VIEW_3D'})
        editor.changed()
        editor.apply()
        self.assertFalse(editor.dirty)
        self.assertEqual(editor.store.snapshot()['assignments'][mapping]['section'], id_)
        editor.draft.update('assignments', mapping, section='overview')
        editor.changed()
        editor.apply()
        self.assertEqual(editor.store.snapshot()['assignments'][mapping]['section'], 'overview')

    def test_command_metadata_and_single_assignment_clone(self):
        def rna():
            field = SimpleNamespace(name='All Regions', type='BOOLEAN', is_readonly=False,
                                    is_skip_save=True, default=False)
            return SimpleNamespace(name='Frame Selected', properties={'use_all_regions': field})

        self.h.runtime.bpy.ops = SimpleNamespace(view3d=SimpleNamespace(
            view_selected=SimpleNamespace(get_rna_type=rna)))
        editor = self.editor
        editor.edit_command('frame-selected', 'use_all_regions', True, 'view-frame')
        clone = editor.catalog['assignments']['view-frame']['command']
        self.assertNotEqual(clone, 'frame-selected')
        self.assertFalse(editor.catalog['commands']['frame-selected']['properties']['use_all_regions'])
        self.assertTrue(editor.catalog['commands'][clone]['properties']['use_all_regions'])
        self.assertEqual(editor.preview()['commands']['provider-fit']['availability'], 'waiting_for_provider')
        self.assertFalse(editor.preview()['assignments']['uv-provider-fit']['eligible'])

    def test_command_filters_follow_assignment_sections(self):
        editor = self.editor
        self.assertIn('select-none', editor.command_ids())
        editor.command_category = 'navigation'
        self.assertEqual(editor.command_ids(), {'frame-selected', 'frame-all-regions'})
        editor.command_section = 'overview'
        self.assertEqual(editor.command_ids(), {'frame-all-regions'})

    def test_unset_rna_setting_can_be_overridden_then_returned_to_default(self):
        setting = SimpleNamespace(name='New setting', type='INT', is_readonly=False,
                                  is_skip_save=True, default=2, hard_min=1, hard_max=5)
        hidden = SimpleNamespace(name='Hidden setting', type='BOOLEAN', is_hidden=True)
        self.h.runtime.bpy.ops = SimpleNamespace(view3d=SimpleNamespace(
            view_selected=SimpleNamespace(get_rna_type=lambda: SimpleNamespace(
                name='Frame Selected', properties={'segments': setting, 'hidden': hidden}))))
        editor = self.editor
        command = editor.catalog['commands']['frame-selected']
        fields = editor.store.resolver.describe_command(command, include_unset=True)['fields']
        self.assertNotIn('hidden', fields)
        self.assertEqual(fields['segments']['default'], 2)
        self.assertFalse(fields['segments']['explicit'])
        self.assertTrue(fields['segments']['editable'])
        with self.assertRaisesRegex(ValueError, 'Invalid segments'):
            editor.edit_command('frame-selected', 'segments', 6)
        editor.edit_command('frame-selected', 'segments', 3)
        editor.apply()
        self.assertEqual(editor.catalog['commands']['frame-selected']['properties']['segments'], 3)
        editor.edit_command('frame-selected', 'segments', None, unset=True)
        self.assertNotIn('segments', editor.catalog['commands']['frame-selected']['properties'])

    def test_two_similar_bindings_are_distinct_in_staged_rules(self):
        editor = self.editor
        source = self.h.runtime.map('default', 'Object Mode', space='EMPTY', tool=False)
        select = source.keymap_items.append_fixture(row('object.select_all', key='A',
                                                       prop_values={'action': 'SELECT'}))
        other = source.keymap_items.append_fixture(row('object.select_all', key='A', alt=True,
                                                      prop_values={'action': 'SELECT'}))
        rule = editor.draft.stage_suppression('framing', source, select, 'default', replacement='select-none')
        editor.changed()
        self.assertEqual(editor.preview()['suppressions'][rule]['status'], 'resolved')
        editor.draft.stage_suppression('framing', source, other, 'default', id_=rule)
        editor.changed()
        self.assertEqual(editor.preview()['suppressions'][rule]['status'], 'unsupported')
        self.assertTrue(editor.catalog['suppressions'][rule]['selector']['event']['alt'])
        self.assertTrue(select.active and other.active)


if __name__ == '__main__':
    unittest.main()
