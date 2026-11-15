"""Artist editor workflows against brief 08's synthetic profile and store."""

import importlib
import unittest
from types import SimpleNamespace
from unittest.mock import patch

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

    def test_browsing_cache_refreshes_on_edits_and_live_operator_changes(self):
        editor = self.editor
        with patch.object(editor.store, 'preview', wraps=editor.store.preview) as preview:
            with patch.object(self.editor_module, 'monotonic', return_value=10):
                initial = editor.preview()
            with patch.object(self.editor_module, 'monotonic', return_value=12):
                self.assertIs(editor.preview(), initial)
            self.assertEqual(preview.call_count, 1)
            editor.stage_event('view-frame', {'type': 'F11'})
            self.assertIsNot(editor.preview(), initial)
            self.assertEqual(preview.call_count, 2)
            with patch.object(editor.store, 'preview_token', return_value=('provider changed',)):
                editor._preview_at = 0
                editor.preview()
            self.assertEqual(preview.call_count, 3)

    def test_shortcut_edits_are_local_then_discard(self):
        editor = self.editor
        editor.stage_event('view-frame', {'type': 'F11'})
        self.assertEqual(editor.catalog['events']['frame']['type'], 'F')
        first = editor.catalog['assignments']['view-frame']['event']
        self.assertEqual(editor.catalog['events'][first]['type'], 'F11')
        editor.stage_event('image-frame', {'type': 'F12'})
        changed = editor.catalog['assignments']['image-frame']['event']
        self.assertNotEqual(changed, first)
        self.assertEqual(editor.catalog['events'][changed]['type'], 'F12')
        self.assertEqual(editor.draft.uses('events', 'frame'), ('image-frame',))
        self.assertEqual(editor.store.snapshot(), self.h.defaults)
        editor.discard()
        self.assertFalse(editor.dirty)
        self.assertEqual(editor.catalog, self.h.defaults)

    def test_invalid_reload_preserves_draft_preview_and_undo(self):
        editor = self.editor
        editor.stage_event('view-frame', {'type': 'F11'})
        first = editor.draft.snapshot()
        editor.stage_event('view-frame', {'type': 'F12'})
        preview = editor.draft.snapshot()
        active_draft = editor.draft
        self.h.path.write_text('null')

        editor.reload()

        self.assertIs(editor.draft, active_draft)
        self.assertTrue(editor.dirty)
        self.assertEqual(editor.catalog, preview)
        self.assertEqual(self.h.installed, preview)
        self.assertEqual(editor.store.load_issue, 'profile_reload_failed')
        self.h.path.write_text('42')
        with self.assertRaisesRegex(ValueError, 'changed on disk'):
            editor.apply()
        self.h.path.write_text('null')
        editor.undo()
        self.assertEqual(self.h.installed, first)
        editor.apply()
        self.assertEqual(editor.saved, first)
        self.assertIsNone(editor.store.load_issue)

    def test_reload_install_failure_restores_live_preview_and_keeps_undo(self):
        editor = self.editor
        editor.stage_event('view-frame', {'type': 'F11'})
        preview = editor.draft.snapshot()
        install = editor.store._install

        def fail_once(candidate, previous):
            install(candidate, previous)
            if previous is not None:
                raise RuntimeError('Injected native install failure')

        with patch.object(editor.store, '_install', side_effect=fail_once):
            with self.assertRaisesRegex(RuntimeError, 'Injected native install failure'):
                editor.reload()
        self.assertEqual(editor.catalog, preview)
        self.assertEqual(self.h.installed, preview)
        self.assertTrue(editor.can_undo)
        editor.reload()
        self.assertEqual(self.h.installed, self.h.defaults)
        self.assertFalse(editor.can_undo)

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
        editor.category = editor.feature_category = 'custom'
        editor.section = editor.feature_section = 'custom.tools'
        editor.ensure_selection()
        self.assertEqual(editor.feature_section, 'custom.tools')
        editor.discard()
        self.assertIn(editor.feature_category, editor.catalog['categories'])
        self.assertIn(editor.feature_section, editor.sections(editor.feature_category))
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

    def test_enabling_inactive_binding_activates_only_that_binding_and_undo_restores_it(self):
        editor = self.editor
        editor.draft.update('assignments', 'view-frame', active=False)
        editor.changed()
        inactive = editor.catalog['assignments']['view-frame']
        other = editor.catalog['assignments']['image-frame']
        editor.set_enabled('assignments', 'view-frame', True)
        self.assertTrue(editor.catalog['assignments']['view-frame']['active'])
        self.assertTrue(editor.preview()['assignments']['view-frame']['active'])
        self.assertEqual(editor.catalog['assignments']['image-frame'], other)
        editor.undo()
        self.assertEqual(editor.catalog['assignments']['view-frame'], inactive)
        editor.set_enabled('assignments', 'view-frame', True)
        editor.set_enabled('assignments', 'view-frame', False)
        self.assertFalse(editor.preview()['assignments']['view-frame']['eligible'])
        editor.apply()
        editor.reload()
        self.assertFalse(editor.catalog['assignments']['view-frame']['enabled'])
        editor.set_enabled('assignments', 'view-frame', True)
        self.assertTrue(editor.preview()['assignments']['view-frame']['active'])

    def test_command_settings_are_independent_before_the_first_edit(self):
        def rna():
            field = SimpleNamespace(name='All Regions', type='BOOLEAN', is_readonly=False,
                                    is_skip_save=True, default=False)
            return SimpleNamespace(name='Frame Selected', properties={'use_all_regions': field})

        self.h.runtime.bpy.ops = SimpleNamespace(view3d=SimpleNamespace(
            view_selected=SimpleNamespace(get_rna_type=rna)))
        editor = self.editor
        editor.draft.update('assignments', 'image-frame', command='frame-selected')
        editor.changed()
        other = editor.catalog['assignments']['image-frame']['command']
        self.assertNotEqual(other, 'frame-selected')
        editor.edit_command('frame-selected', 'use_all_regions', True, 'view-frame')
        self.assertFalse(editor.catalog['commands'][other]['properties']['use_all_regions'])
        self.assertTrue(editor.catalog['commands']['frame-selected']['properties']['use_all_regions'])
        editor.edit_command('frame-selected', 'use_all_regions', None, 'view-frame', unset=True)
        self.assertNotIn('use_all_regions', editor.catalog['commands']['frame-selected']['properties'])
        self.assertFalse(editor.catalog['commands'][other]['properties']['use_all_regions'])
        editor.undo()
        self.assertTrue(editor.catalog['commands']['frame-selected']['properties']['use_all_regions'])
        editor.apply()
        editor.reload()
        self.assertNotEqual(editor.catalog['assignments']['image-frame']['command'], 'frame-selected')
        self.assertFalse(editor.catalog['commands'][other]['properties']['use_all_regions'])
        self.assertEqual(editor.preview()['commands']['provider-fit']['availability'], 'waiting_for_provider')
        self.assertFalse(editor.preview()['assignments']['uv-provider-fit']['eligible'])

    def test_binding_filters_combine_and_all_bindings_includes_inactive_sections(self):
        editor = self.editor
        rows = editor.catalog['assignments']
        visible = lambda: {id_ for id_, row in editor.catalog['assignments'].items() if editor.accepts_binding(row)}
        self.assertEqual(visible(), set(rows))
        editor.select_category('navigation')
        self.assertEqual(visible(), {'view-frame', 'image-frame'})
        editor.select_section('framing')
        self.assertEqual(visible(), {'view-frame'})
        self.assertFalse(editor.dirty)
        self.assertFalse(self.h.path.exists())
        editor.draft.update('assignments', 'uv-provider-fit', command='frame-selected')
        editor.changed()
        editor.show_all_bindings()
        self.assertEqual(visible(), set(rows))
        self.assertFalse(editor.catalog['categories']['selection']['enabled'])
        editor.category = 'removed section'
        editor.binding_all = False
        editor.ensure_selection()
        self.assertTrue(editor.binding_all)

    def test_binding_tree_prunes_empty_contexts_and_retains_unlisted_scopes(self):
        model = self.editor_module
        view = ('3D View', 'VIEW_3D', 'WINDOW')
        mesh = ('Mesh', 'EMPTY', 'WINDOW')
        custom = ('Mesh', 'VIEW_3D', 'HEADER')
        hierarchy = [
            ('Window', 'EMPTY', 'WINDOW', []),
            (*view, [(*mesh, []), ('Sculpt', 'EMPTY', 'WINDOW', [])]),
        ]
        groups = {custom: ['header'], mesh: ['cut', 'extrude'], view: ['orbit']}

        tree = model.binding_context_tree(hierarchy, groups)
        self.assertEqual([node.label for node in tree], ['3D View', 'Mesh · View 3D · Header'])
        self.assertEqual([node.label for node in tree[0].children], ['3D View (Global)', 'Mesh'])
        self.assertEqual([node.bindings for node in tree[0].children], [['orbit'], ['cut', 'extrude']])
        self.assertEqual(tree[1].bindings, ['header'])
        self.assertEqual(model.binding_context_path(tree, 'extrude'), (tree[0].id, tree[0].children[1].id))
        self.assertEqual(model.binding_context_path(tree, 'hidden'), ())

        filtered = model.binding_context_tree(hierarchy, {mesh: ['extrude']})
        self.assertEqual([node.label for node in filtered], ['3D View'])
        self.assertEqual(filtered[0].children[0].bindings, ['extrude'])
        self.assertEqual(len(groups), 3)

    def test_new_bindings_own_commands_and_delete_undo_save_preserve_other_binding(self):
        self.h.runtime.bpy.ops = SimpleNamespace(object=SimpleNamespace(
            shade_smooth=SimpleNamespace(get_rna_type=lambda: SimpleNamespace(
                name='Shade Smooth', properties={}))))
        editor = self.editor
        scope = {'name': '3D View', 'space_type': 'VIEW_3D'}
        first = editor.configure_binding('framing', 'frame', 'object.shade_smooth', scope)
        second = editor.configure_binding('framing', 'frame', 'object.shade_smooth', scope)
        first_command = editor.catalog['assignments'][first]['command']
        second_command = editor.catalog['assignments'][second]['command']
        self.assertNotEqual(first_command, second_command)
        self.assertEqual(editor.catalog['commands'][first_command], editor.catalog['commands'][second_command])
        editor.draft.delete('assignments', first)
        editor.changed()
        self.assertNotIn(first_command, editor.catalog['commands'])
        self.assertIn(second_command, editor.catalog['commands'])
        editor.undo()
        self.assertEqual(editor.catalog['assignments'][first]['command'], first_command)
        editor.apply()
        editor.reload()
        self.assertIn(first, editor.catalog['assignments'])
        self.assertEqual(editor.catalog['assignments'][second]['command'], second_command)
        before = editor.catalog
        with self.assertRaisesRegex(ValueError, 'operator ID'):
            editor.configure_binding('framing', 'frame', 'not an operator', scope)
        self.assertEqual(editor.catalog, before)
        self.assertEqual(editor.draft.snapshot(), before)

    def test_new_context_binding_is_unassigned_and_can_move_category_without_changing_behavior(self):
        editor = self.editor
        before = editor.store.resolver.plan(editor.catalog, self.h.settings)
        scope = {'name': '3D View', 'space_type': 'VIEW_3D'}
        added = editor.add_binding(scope, 'framing')
        binding = editor.catalog['assignments'][added]
        self.assertTrue(editor.binding_all)
        self.assertEqual(editor.catalog['commands'][binding['command']]['operator'], '')
        self.assertEqual(editor.catalog['events'][binding['event']]['type'], 'NONE')
        self.assertEqual(editor.store.resolver.plan(editor.catalog, self.h.settings), before)
        self.assertFalse(editor.preview_error)
        editor.move_binding(added, category='selection')
        moved = editor.catalog['assignments'][added]
        self.assertEqual(moved['section'], 'provider')
        self.assertEqual({k: v for k, v in binding.items() if k != 'section'},
                         {k: v for k, v in moved.items() if k != 'section'})
        editor.undo()
        self.assertEqual(editor.catalog['assignments'][added], binding)
        editor.undo()
        self.assertNotIn(added, editor.catalog['assignments'])

    def test_typed_missing_operator_persists_and_exposes_properties_when_registered(self):
        editor = self.editor
        command = 'frame-selected'
        editor.change_command_operator(command, 'bpy.ops.custom.new_tool')
        self.assertEqual(editor.catalog['commands'][command], {'operator': 'custom.new_tool', 'properties': {}})
        self.assertEqual(editor.preview()['commands'][command]['availability'], 'unavailable')
        _, groups = editor.store.resolver.plan(editor.catalog, self.h.settings)
        request = next(item for rows in groups.values() for item in rows if item.request_id == 'view-frame')
        self.assertTrue(request.requires_operator)
        editor.apply()
        editor.reload()
        field = SimpleNamespace(name='Strength', type='FLOAT', is_readonly=False,
                                default=1.0, hard_min=0.0, hard_max=10.0)
        self.h.runtime.bpy.ops = SimpleNamespace(custom=SimpleNamespace(
            new_tool=SimpleNamespace(get_rna_type=lambda: SimpleNamespace(name='New Tool', properties={'strength': field}))))
        editor.edit_command(command, 'strength', 2.0, 'view-frame')
        self.assertEqual(editor.catalog['commands'][command]['properties'], {'strength': 2.0})

    def test_unassigned_binding_survives_save_and_reload_in_its_category(self):
        editor = self.editor
        editor.select_category('navigation')
        added = editor.add_binding({'name': 'Image', 'space_type': 'IMAGE_EDITOR'})
        row = editor.catalog['assignments'][added]
        self.assertTrue(editor.accepts_binding(row))
        self.assertEqual(editor.binding_origin(added, editor.preview()),
                         ('ADD', 'Keymap Added by Blue Hole Deluxe · Unassigned'))
        editor.apply()
        editor.reload()
        self.assertEqual(editor.catalog['assignments'][added], row)
        self.assertEqual(editor.catalog['commands'][row['command']]['operator'], '')

    def test_binding_origin_does_not_claim_pending_registration_is_active(self):
        preview = self.editor.preview()
        state = preview['assignments']['view-frame']
        state.update(eligible=True, active=True, registered=False)
        command = self.editor.catalog['assignments']['view-frame']['command']
        preview['commands'][command]['availability'] = 'available'
        self.assertTrue(self.editor.binding_origin('view-frame', preview)[1].endswith('Pending registration'))
        state['registered'] = True
        self.assertTrue(self.editor.binding_origin('view-frame', preview)[1].endswith('Active'))
        state['eligible'] = False
        self.assertTrue(self.editor.binding_origin('view-frame', preview)[1].endswith('Inactive'))

    def test_menu_name_property_and_provider_retarget_are_editable(self):
        editor = self.editor
        self.h.runtime.bpy.types = SimpleNamespace()
        name = SimpleNamespace(name='Name', type='STRING', is_readonly=False, default='', length_max=0)
        self.h.runtime.bpy.ops = SimpleNamespace(wm=SimpleNamespace(
            call_menu_pie=SimpleNamespace(get_rna_type=lambda: SimpleNamespace(name='Call Pie Menu', properties={'name': name}))))
        editor.change_command_operator('provider-fit', 'wm.call_menu_pie')
        command = editor.catalog['assignments']['uv-provider-fit']['command']
        self.assertNotEqual(command, 'provider-fit')
        editor.edit_command(command, 'name', 'BLUEHOLE_MT_pie_add', 'uv-provider-fit')
        self.assertEqual(editor.catalog['commands'][command]['properties']['name'], 'BLUEHOLE_MT_pie_add')
        editor.apply()
        editor.reload()
        self.assertEqual(editor.catalog['commands'][command]['operator'], 'wm.call_menu_pie')

    def test_empty_contexts_have_add_targets_and_containers_always_use_global_children(self):
        hierarchy = [('3D View', 'VIEW_3D', 'WINDOW', [('Object Mode', 'EMPTY', 'WINDOW', [])])]
        view = {'name': '3D View', 'space_type': 'VIEW_3D'}
        obj = {'name': 'Object Mode'}
        tree = self.editor_module.binding_context_tree(hierarchy, {}, [view, obj])
        self.assertIsNone(tree[0].scope)
        self.assertEqual([node.label for node in tree[0].children], ['3D View (Global)', 'Object Mode'])
        self.assertEqual([node.scope for node in tree[0].children], [view, obj])
        filtered = self.editor_module.binding_context_tree(hierarchy, {('3D View', 'VIEW_3D', 'WINDOW'): ['a']}, [view])
        self.assertIsNone(filtered[0].scope)
        self.assertEqual(filtered[0].children[0].label, '3D View (Global)')
        self.assertEqual(filtered[0].children[0].bindings, ['a'])

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

    def test_undo_restores_reset_setting_and_deleted_binding_in_reverse_order(self):
        editor = self.editor
        setting = SimpleNamespace(name='All Regions', type='BOOLEAN', is_readonly=False, default=False)
        self.h.runtime.bpy.ops = SimpleNamespace(view3d=SimpleNamespace(
            view_selected=SimpleNamespace(get_rna_type=lambda: SimpleNamespace(
                name='Frame Selected', properties={'use_all_regions': setting}))))
        editor.edit_command('frame-selected', 'use_all_regions', True)
        editor.edit_command('frame-selected', 'use_all_regions', None, unset=True)
        original = editor.catalog['assignments']['view-frame']
        editor.draft.delete('assignments', 'view-frame')
        editor.changed()
        editor.undo()
        self.assertEqual(editor.catalog['assignments']['view-frame'], original)
        editor.undo()
        self.assertTrue(editor.catalog['commands']['frame-selected']['properties']['use_all_regions'])
        self.assertEqual(editor.store.runtime_catalog(), editor.catalog)
        editor.undo()
        self.assertEqual(editor.catalog, editor.saved)
        self.assertFalse(editor.can_undo)
        editor.edit_command('frame-selected', 'use_all_regions', True)
        editor.apply()
        self.assertFalse(editor.can_undo)

    def test_change_command_operator_keeps_bindings_and_uses_new_operator_defaults(self):
        editor = self.editor
        self.h.runtime.bpy.ops = SimpleNamespace(object=SimpleNamespace(
            shade_smooth=SimpleNamespace(get_rna_type=lambda: SimpleNamespace(
                name='Shade Smooth', properties={}))))
        editor.draft.update('assignments', 'view-frame', command='frame-all-regions')
        editor.changed()
        assignments = editor.catalog['assignments']
        other = assignments['view-frame']['command']
        original = editor.catalog['commands'][other]
        before = editor.catalog
        self.assertTrue(editor.can_change_operator('frame-all-regions'))
        with self.assertRaisesRegex(ValueError, 'operator ID'):
            editor.change_command_operator('frame-all-regions', 'not an operator')
        self.assertEqual(editor.catalog, before)
        editor.change_command_operator('frame-all-regions', 'object.shade_smooth')
        self.assertEqual(editor.catalog['commands']['frame-all-regions'],
                         {'operator': 'object.shade_smooth', 'properties': {}})
        self.assertEqual(editor.catalog['assignments'], assignments)
        self.assertEqual(editor.catalog['commands'][other], original)
        editor.undo()
        self.assertEqual(editor.catalog, before)

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
