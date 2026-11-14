"""Split catalog persistence, diagnostics, and whole-generation recovery."""

from copy import deepcopy
import json
import unittest
from unittest.mock import patch

import test_deluxe_profiles


class CatalogTests(unittest.TestCase):
    setUp = test_deluxe_profiles.ProfileTests.setUp

    def open_catalog(self):
        self.io = self.api.deluxe_catalog
        self.path.write_text(json.dumps(self.defaults))
        self.store = self.api.ProfileStore.open_catalog(
            self.path, lambda: self.settings, lambda candidate, previous: setattr(self, 'installed', candidate))
        draft = self.store.begin()
        draft.update('categories', 'navigation', label='Navigation tools')
        self.store.apply(draft)
        return self.store.snapshot()

    def section(self, category):
        return self.path.parent / ('profile-sections/' + category + '.json')

    def test_split_preserves_shared_identity_and_retires_only_deleted_section_files(self):
        original = self.open_catalog()
        draft = self.store.begin()
        draft.put('categories', 'custom', {'label': 'Custom'})
        draft.put('sections', 'custom-tools', {'label': 'Tools', 'category': 'custom'})
        draft.update('assignments', 'image-frame', section='custom-tools', command='frame-selected')
        committed = self.store.apply(draft)
        master = json.loads(self.path.read_text())
        self.assertIn('frame', master['events'])
        self.assertIn('frame-selected', master['commands'])
        self.assertEqual(self.io.load(self.path), committed)
        self.assertTrue(self.section('custom').exists())
        unrelated = self.section('notes')
        unrelated.write_text('Keep this text file untouched')
        self.store.reload()
        draft = self.store.begin()
        draft.update('assignments', 'image-frame', **original['assignments']['image-frame'])
        draft.delete('sections', 'custom-tools')
        draft.delete('categories', 'custom')
        self.store.apply(draft)
        self.assertFalse(self.section('custom').exists())
        self.assertEqual(unrelated.read_text(), 'Keep this text file untouched')
        self.assertNotIn('frame', json.loads(self.path.read_text())['events'])

    def test_missing_file_syntax_duplicate_and_semantic_errors_name_the_source(self):
        expected = self.open_catalog()
        source = self.section('navigation')
        saved = source.read_bytes()
        cases = [('syntax', '{\n  "category": "unterminated\n}', r'navigation.json:2:\d+:'),
                 ('duplicate', '{"category":"a","category":"b"}', r'navigation.json: Duplicate JSON key'),
                 ('number', '{"category":NaN}', r'navigation.json: Invalid JSON number')]
        for name, text, message in cases:
            with self.subTest(name=name):
                source.write_text(text)
                with self.assertRaisesRegex(ValueError, message):
                    self.io.load(self.path)
                self.assertEqual(self.store.reload(), expected)
                self.assertRegex(self.store.load_error, message)
                source.write_bytes(saved)
        part = json.loads(saved)
        del part['assignments']['view-frame']['event']
        source.write_bytes(self.io.encode(part))
        with self.assertRaisesRegex(ValueError, r'navigation.json:\d+: assignments.*view-frame.*Missing fields: event'):
            self.io.load(self.path)
        source.unlink()
        self.assertEqual(self.store.reload(), expected)
        self.assertIn('navigation.json', self.store.load_error)
        reopened = self.api.ProfileStore.open_catalog(self.path, lambda: self.settings, lambda *args: None)
        self.assertEqual(reopened.snapshot(), expected)
        reopened.apply(reopened.begin())
        self.assertEqual(self.io.load(self.path), expected)

    def test_dangling_references_path_traversal_and_duplicate_records_are_rejected(self):
        self.open_catalog()
        source = self.section('navigation')
        part = json.loads(source.read_text())
        part['assignments']['view-frame']['command'] = 'missing-command'
        source.write_bytes(self.io.encode(part))
        with self.assertRaisesRegex(ValueError, r'navigation.json.*view-frame.*Missing command reference'):
            self.io.load(self.path)
        master = json.loads(self.path.read_text())
        master['section_files']['navigation'] = '../outside.json'
        self.path.write_text(json.dumps(master))
        with self.assertRaisesRegex(ValueError, 'section_files'):
            self.io.load(self.path)

    def test_child_external_edit_blocks_stale_apply(self):
        self.open_catalog()
        draft = self.store.begin()
        draft.update('categories', 'selection', label='Changed in UI')
        source = self.section('navigation')
        part = json.loads(source.read_text())
        part['definition']['label'] = 'Changed in text editor'
        source.write_bytes(self.io.encode(part))
        with self.assertRaisesRegex(ValueError, 'changed on disk'):
            self.store.apply(draft)
        self.store.reload()
        self.assertEqual(self.store.snapshot()['categories']['navigation']['label'], 'Changed in text editor')

    def test_invalid_section_reference_types_report_file_and_keep_working_catalog(self):
        expected = self.open_catalog()
        source = self.section('navigation')
        original = json.loads(source.read_text())
        for value in ([], {}, None, 4):
            with self.subTest(value=value):
                part = deepcopy(original)
                part['assignments']['view-frame']['section'] = value
                source.write_bytes(self.io.encode(part))
                self.assertEqual(self.store.reload(), expected)
                self.assertIn('navigation.json: assignments', self.store.load_error)

    def test_recovery_save_repairs_non_object_master(self):
        expected = self.open_catalog()
        for value in ('null', '[]', '42', '"not an object"'):
            with self.subTest(value=value):
                self.path.write_text(value)
                self.assertEqual(self.store.reload(), expected)
                self.assertIn('expected a JSON object', self.store.load_error)
                self.store.apply(self.store.begin())
                self.assertEqual(self.io.load(self.path), expected)

    def test_failed_multi_file_publication_restores_every_file_and_runtime(self):
        expected = self.open_catalog()
        before = {path: path.read_bytes() for path in self.io.split(self.path, expected)}
        draft = self.store.begin()
        draft.update('categories', 'navigation', label='New label')
        draft.update('categories', 'selection', label='Also changed')
        write = self.io.atomic_write_bytes
        failed = False
        def fail_master(path, *args, **kwargs):
            nonlocal failed
            if path == self.path and not failed:
                failed = True
                raise OSError('injected master failure')
            return write(path, *args, **kwargs)
        with patch.object(self.io, 'atomic_write_bytes', side_effect=fail_master):
            with self.assertRaisesRegex(OSError, 'injected'):
                self.store.apply(draft)
        self.assertEqual({path: path.read_bytes() for path in before}, before)
        self.assertEqual(self.installed, expected)
        self.assertFalse(self.io.transaction_path(self.path).exists())

    def test_interrupted_save_uses_whole_recovery_snapshot(self):
        expected = self.open_catalog()
        self.io.transaction_path(self.path).write_text('{}')
        source = self.section('navigation')
        part = json.loads(source.read_text())
        part['definition']['label'] = 'Uncommitted half-save'
        source.write_bytes(self.io.encode(part))
        reopened = self.api.ProfileStore.open_catalog(self.path, lambda: self.settings, lambda *args: None)
        self.assertEqual(reopened.snapshot(), expected)
        self.assertIn('interrupted save', reopened.load_error)
        reopened.apply(reopened.begin())
        self.assertEqual(self.io.load(self.path), expected)
        self.assertFalse(self.io.transaction_path(self.path).exists())


if __name__ == '__main__':
    unittest.main()
