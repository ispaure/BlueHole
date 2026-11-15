"""Binding tree navigation, tab balance and addon ownership regressions."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest

import test_deluxe_editor
import test_deluxe_profiles

ROOT = Path(__file__).resolve().parents[1]


def function(file, name, **namespace):
    # These pure layout/state helpers do not need Blender's RNA metaclasses.
    module = ast.parse((ROOT / 'preferences/addon/keymaps' / file).read_text())
    node = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), file, 'exec'), namespace)
    return namespace[name]


class NavigationTests(unittest.TestCase):
    setUp = test_deluxe_editor.EditorTests.setUp

    def test_expand_all_opens_only_branches_with_bindings_and_collapse_closes_roots(self):
        cls = self.editor_module.BindingContext
        contexts = [cls('root', 'Root', [], [cls('leaf', 'Leaf', ['view-frame'], []),
                                          cls('empty', 'Empty', [], [])]),
                    cls('other', 'Other', [], [])]
        self.editor.assignment = 'view-frame'
        self.editor.expand_binding_contexts(contexts, True)
        self.assertEqual(self.editor.binding_context_expansion,
                         {'root': True, 'leaf': True, 'empty': False, 'other': False})
        self.editor.expand_binding_contexts(contexts, False)
        self.assertFalse(any(self.editor.binding_context_expansion.values()))
        self.assertEqual(self.editor.binding_focus_context, 'root')
        self.assertEqual(self.editor.assignment, 'view-frame')

    def test_tabs_are_balanced_and_never_exceed_twelve(self):
        rows = function('deluxe_editor.py', 'balanced_rows')
        self.assertEqual([len(row) for row in rows(range(16))], [8, 8])
        for count in range(100):
            result = list(rows(range(count)))
            self.assertEqual([item for row in result for item in row], list(range(count)))
            if result:
                sizes = [len(row) for row in result]
                self.assertLessEqual(max(sizes), 12)
                self.assertLessEqual(max(sizes) - min(sizes), 1)

    def test_repeated_blender_scopes_have_independent_expansion_state(self):
        scope = dict(name='Image Paint', space_type='EMPTY', region_type='WINDOW')
        leaf = ('Image Paint', 'EMPTY', 'WINDOW', [])
        hierarchy = [('3D View', 'VIEW_3D', 'WINDOW', [leaf]),
                     ('Image', 'IMAGE_EDITOR', 'WINDOW', [leaf])]
        contexts = self.editor_module.binding_context_tree(
            hierarchy, {('Image Paint', 'EMPTY', 'WINDOW'): ['view-frame']}, [scope])
        populated, empty = [root.children[0] for root in contexts]
        self.assertNotEqual(populated.id, empty.id)
        self.editor.expand_binding_contexts(contexts, True)
        self.assertTrue(self.editor.binding_context_expansion[populated.id])
        self.assertFalse(self.editor.binding_context_expansion[empty.id])
        self.assertTrue(self.editor.binding_context_expansion[contexts[0].id])
        self.assertFalse(self.editor.binding_context_expansion[contexts[1].id])

    def test_rebuilding_after_expansion_keeps_header_focus_without_changing_inspector(self):
        sync = function('deluxe_editor_ops.py', 'sync_binding_rows')
        class Rows(list):
            def add(self):
                row = SimpleNamespace()
                self.append(row)
                return row
        view = SimpleNamespace(binding_rows=Rows(), rows_key='', binding_index=-1,
                               list_selection='', list_focus='')
        def rows():
            yield dict(kind='context', target='clicked')
            yield dict(kind='binding', target='selected')
            yield dict(kind='binding', target='other')
        sync(view, 'initial', rows, 'selected')
        self.assertEqual(view.binding_index, 1)
        sync(view, 'expanded', rows, 'selected', focus_context='clicked')
        self.assertEqual(view.binding_index, 0)
        sync(view, 'fresh-preview', rows, 'selected')
        self.assertEqual(view.binding_index, 0)
        self.assertEqual(view.list_selection, 'selected')
        sync(view, 'fresh-preview', rows, 'other')
        self.assertEqual(view.binding_index, 2)
        self.assertEqual(view.list_focus, '')

    def test_addon_catalog_groups_own_commands_and_keeps_save_as_required(self):
        catalog = self.h.api.deluxe_catalog.load(test_deluxe_profiles.DEFAULTS)
        required = []
        for row in catalog['assignments'].values():
            command = catalog['commands'][row['command']]
            provider = command.get('provider')
            if provider:
                section = catalog['sections'][row['section']]
                self.assertEqual(section['category'], 'addons')
                self.assertEqual(section['label'], provider)
            if command.get('operator') == 'wm.bh_save_as_mainfile':
                self.assertTrue(row['required'])
                self.assertEqual(row['section'], 'addons.blue-hole')
                required.append(row)
        self.assertEqual(len(required), 2)
        labels = [s['label'] for s in catalog['sections'].values() if s['category'] == 'addons']
        self.assertEqual(len(labels), len(set(labels)))
        self.assertIn('MACHIN3tools', labels)
        self.assertIn('MESHmachine', labels)
        for rule in catalog['suppressions'].values():
            self.assertNotIn('requires_assignment', rule)
        self.assertEqual(catalog['suppressions']['parity-disable-400848e85e7b']['section'], 'addons.hard-ops')
        outside_addons = {s['label'] for s in catalog['sections'].values() if s['category'] != 'addons'}
        self.assertFalse(outside_addons.intersection(labels))
        self.assertNotIn('MACHIN3tools / MESHmachine', outside_addons)
        self.assertNotIn('Pie Menu Editor / custom pies', outside_addons)

    def test_required_binding_in_editable_section_cannot_be_changed_or_removed(self):
        self.h.defaults['assignments']['view-frame']['required'] = True
        self.h.store = self.h.api.ProfileStore(self.h.defaults, self.h.path,
                                              lambda: self.h.settings, lambda *args: None)
        editor = self.editor_module.Editor(self.h.store)
        with self.assertRaisesRegex(ValueError, 'required'):
            editor.stage_event('view-frame', {'type': 'F10'})
        draft = self.h.store.begin()
        draft.delete('assignments', 'view-frame')
        with self.assertRaisesRegex(ValueError, 'Required binding'):
            self.h.store.validate(draft)
