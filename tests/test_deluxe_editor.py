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

    def test_capture_keeps_repeat_and_phase_for_compatible_input(self):
        capture = self.editor_module.captured_input
        event = SimpleNamespace(type='H', shift=True, ctrl=False, alt=False, oskey=False)
        previous = {'type': 'G', 'repeat': True, 'value': 'PRESS', 'key_modifier': 'D'}
        updated = capture(previous, event)
        self.assertTrue(updated['repeat'])
        self.assertEqual(updated['key_modifier'], 'D')
        self.assertTrue(updated['shift'])
        event.type = 'MIDDLEMOUSE'
        updated = capture(previous, event)
        self.assertEqual(updated['map_type'], 'MOUSE')
        self.assertFalse(updated['repeat'])
        self.assertEqual(updated['value'], 'PRESS')
        self.assertEqual(previous['type'], 'G')

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

    def test_dynamic_tabs_recover_after_removal_discard_and_reload(self):
        editor = self.editor
        editor.edit_section('Artist tools')
        section = editor.feature_section
        editor.edit_section('Renamed tools', section)
        self.assertEqual(editor.feature_section, section)
        self.assertEqual(editor.catalog['sections'][section]['label'], 'Renamed tools')
        editor.draft.delete('sections', section)
        editor.changed()
        self.assertIn(editor.feature_section, editor.sections(editor.feature_category))
        self.assertNotEqual(editor.feature_section, section)

        editor.draft.put('categories', 'custom', {'label': 'Custom'})
        editor.draft.put('sections', 'custom.tools', {'label': 'Tools', 'category': 'custom'})
        editor.changed()
        editor.category = editor.feature_category = editor.command_category = 'custom'
        editor.section = editor.feature_section = editor.command_section = 'custom.tools'
        editor.ensure_selection()
        self.assertEqual(editor.feature_section, 'custom.tools')
        editor.discard()
        self.assertIn(editor.feature_category, editor.catalog['categories'])
        self.assertIn(editor.feature_section, editor.sections(editor.feature_category))
        self.assertEqual((editor.command_category, editor.command_section), ('', ''))
        self.assertFalse(editor.dirty)

        editor.category = editor.feature_category = 'removed-category'
        editor.section = editor.feature_section = 'removed-section'
        editor.reload()
        self.assertIn(editor.section, editor.sections())
        self.assertIn(editor.feature_section, editor.sections(editor.feature_category))
        self.assertFalse(editor.dirty)

    def test_group_choices_preview_without_saving_and_discard_restores(self):
        editor = self.editor
        path = editor.store.path
        original_file = path.read_bytes() if path.exists() else None
        original_plan = editor.store.resolver.plan(editor.store.snapshot(), self.h.settings)
        for table, id_ in (('categories', 'navigation'), ('sections', 'framing')):
            editor.set_enabled(table, id_, False)
        self.assertTrue(editor.dirty)
        self.assertEqual(path.read_bytes() if path.exists() else None, original_file)
        self.assertEqual(editor.store.snapshot(), self.h.defaults)
        self.assertEqual(editor.store.resolver.plan(editor.store.snapshot(), self.h.settings), original_plan)
        self.assertFalse(self.h.installed['categories']['navigation']['enabled'])
        self.assertFalse(self.h.installed['sections']['framing']['enabled'])
        editor.discard()
        self.assertEqual(self.h.installed, self.h.defaults)
        self.assertTrue(editor.catalog['categories']['navigation'].get('enabled', True))
        editor.set_enabled('sections', 'framing', False)
        editor.apply()
        self.assertFalse(editor.store.snapshot()['sections']['framing']['enabled'])
        self.assertNotEqual(path.read_bytes(), original_file)

    def test_failed_preview_keeps_last_good_runtime_and_draft(self):
        editor = self.editor
        editor.set_enabled('sections', 'framing', False)
        previous = self.h.installed
        install = editor.store._install

        def reject(candidate, before):
            if before is not None:
                raise RuntimeError('Cannot preview this edit')
            install(candidate, before)

        editor.store._install = reject
        editor.set_enabled('sections', 'overview', False)
        self.assertIn('Cannot preview', editor.preview_error)
        self.assertFalse(editor.catalog['sections']['overview']['enabled'])
        self.assertEqual(self.h.installed, previous)
        self.assertFalse(self.h.path.exists())
        editor.store._install = install
        editor.discard()
        self.assertEqual(self.h.installed, self.h.defaults)

    def test_command_metadata_and_single_assignment_clone(self):
        def rna():
            field = SimpleNamespace(name='All Regions', type='BOOLEAN', is_readonly=False,
                                    is_skip_save=True, default=False)
            return SimpleNamespace(name='Frame Selected', properties={'use_all_regions': field})

        self.h.runtime.bpy.ops = SimpleNamespace(view3d=SimpleNamespace(
            view_selected=SimpleNamespace(get_rna_type=rna)))
        editor = self.editor
        editor.draft.update('assignments', 'image-frame', command='frame-selected')
        editor.changed()
        editor.edit_command('frame-selected', 'use_all_regions', True, 'view-frame')
        clone = editor.catalog['assignments']['view-frame']['command']
        self.assertNotEqual(clone, 'frame-selected')
        self.assertFalse(editor.catalog['commands']['frame-selected']['properties']['use_all_regions'])
        self.assertTrue(editor.catalog['commands'][clone]['properties']['use_all_regions'])
        editor.edit_command(clone, 'use_all_regions', False, 'view-frame')
        self.assertEqual(editor.catalog['assignments']['view-frame']['command'], clone)
        editor.edit_command('frame-selected', 'use_all_regions', True)
        self.assertFalse(editor.catalog['commands'][clone]['properties']['use_all_regions'])
        self.assertTrue(editor.catalog['commands']['frame-selected']['properties']['use_all_regions'])
        self.assertEqual(editor.preview()['commands']['provider-fit']['availability'], 'waiting_for_provider')
        self.assertFalse(editor.preview()['assignments']['uv-provider-fit']['eligible'])

    def test_command_filters_follow_assignment_sections(self):
        editor = self.editor
        self.assertIn('select-none', editor.command_ids())
        editor.command_category = 'navigation'
        self.assertEqual(editor.command_ids(), {'frame-selected', 'frame-all-regions'})
        editor.command_section = 'overview'
        self.assertEqual(editor.command_ids(), {'frame-all-regions'})

    def test_binding_filters_combine_and_all_uses_includes_inactive_sections(self):
        editor = self.editor
        rows = editor.catalog['assignments']
        visible = lambda: {id_ for id_, row in editor.catalog['assignments'].items() if editor.accepts_binding(row)}
        self.assertEqual(visible(), set(rows))
        editor.select_category('navigation')
        self.assertEqual(visible(), {'view-frame', 'image-frame'})
        editor.binding_context = self.editor_module.context_id(rows['image-frame']['scope'])
        self.assertEqual(visible(), {'image-frame'})
        editor.select_section('framing')
        self.assertEqual(visible(), set())
        self.assertFalse(editor.dirty)
        self.assertFalse(self.h.path.exists())
        editor.draft.update('assignments', 'uv-provider-fit', command='frame-selected')
        editor.changed()
        editor.show_all_bindings('frame-selected')
        self.assertEqual(visible(), {'view-frame', 'uv-provider-fit'})
        self.assertEqual(editor.binding_context, '')
        self.assertFalse(editor.catalog['categories']['selection']['enabled'])
        editor.binding_context = 'removed context'
        editor.category = 'removed section'
        editor.binding_all = False
        editor.ensure_selection()
        self.assertTrue(editor.binding_all)
        self.assertEqual(editor.binding_context, '')

    def test_new_unused_command_duplicate_and_save_discard(self):
        self.h.runtime.bpy.ops = SimpleNamespace(object=SimpleNamespace(
            shade_smooth=SimpleNamespace(get_rna_type=lambda: SimpleNamespace(
                name='Shade Smooth', properties={}))))
        editor = self.editor
        new = editor.create_command('object.shade_smooth', 'My Smooth')
        copy = editor.create_command(source=new, label='Smooth Copy')
        self.assertIn(new, editor.command_ids())
        self.assertEqual(editor.draft.uses('commands', new), ())
        self.assertEqual(editor.preview()['commands'][new]['label'], 'My Smooth')
        self.assertEqual(editor.catalog['commands'][copy]['label'], 'Smooth Copy')
        self.assertFalse(self.h.path.exists())
        editor.remove_command(copy)
        with self.assertRaisesRegex(ValueError, 'every binding'):
            editor.remove_command('frame-selected')
        editor.apply()
        self.assertIn(new, editor.store.snapshot()['commands'])
        editor.remove_command(new)
        editor.discard()
        self.assertIn(new, editor.catalog['commands'])
        with self.assertRaisesRegex(ValueError, 'Unknown command'):
            editor.create_command('unknown.operator')

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
