"""Vendored directory package smoke checks without Blender startup."""
import importlib
from pathlib import Path
import sys
import tempfile
import types
import unittest


class DirectoryIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        name = '_bluehole_directory_tests'
        package = types.ModuleType(name)
        package.__path__ = [str(Path(__file__).resolve().parents[1])]
        sys.modules[name] = package
        from shared_source import install_candidate
        install_candidate(name)
        cls.canonical = importlib.import_module(name + '.Lib.commonUtils.filesystem.index')
        cls.addClassCleanup(lambda: [sys.modules.pop(key, None) for key in tuple(sys.modules)
            if key == name or key.startswith(name + '.')])

    def test_metadata_scan_uses_moved_dependencies(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'example.txt'
            path.write_text('sample')
            snapshot = self.canonical.scan_metadata(Path(folder))
            self.assertEqual([entry.path for entry in snapshot.entries], [path])

    def test_persistent_scan_initializes_vendored_schema(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'files'
            root.mkdir()
            path = root / 'example.txt'
            path.write_text('sample')
            cache = self.canonical.DirectoryCache(database=Path(folder) / 'index.sqlite3')
            try:
                snapshot = cache.get(root)
                self.assertEqual(snapshot.entry(path).size, 6)
                snapshot.close()
            finally:
                cache.close()
