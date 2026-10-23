"""Run portable vendored contracts in Blender's embedded Python, without registration."""
from array import array
import argparse
import asyncio
import importlib
from io import BytesIO
import json
import os
from pathlib import Path
import sys
import subprocess
from tempfile import TemporaryDirectory
import types
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = '_bluehole_embedded_smoke'


def shared(name):
    return importlib.import_module(f'{NAMESPACE}.Lib.commonUtils.{name}')


class EmbeddedSharedTests(unittest.TestCase):
    def test_portable_imports_do_not_load_optional_toolkits(self):
        before = set(sys.modules)
        browser = shared('ui.native_browser')
        self.assertIs(browser.BrowserLifecycle, shared('ui.native_browser.lifecycle').BrowserLifecycle)
        shared('integrations.wrappers.cmdShellWrapper')
        self.assertFalse(any(name.split('.')[0] in {'toga', 'PySide6', 'commonUtils'}
                             for name in set(sys.modules) - before))
        self.assertTrue(Path(shared('runtime.platform').__file__).is_relative_to(ROOT / 'Lib/commonUtils'))
        async def retirement():
            work = browser.BrowserLifecycle()
            work.stop()
            coroutine = asyncio.sleep(0)
            try:
                self.assertIsNone(work.spawn(coroutine))
            finally:
                coroutine.close()
            # Prepared-tree publication explicitly reopens this existing owner.
            work.closed = False
            self.assertIsNotNone(work.spawn(asyncio.sleep(0)))
            await work.close()
            self.assertFalse(work.tasks)
        asyncio.run(retirement())

    def test_short_streams_range_buffers_and_batch_success(self):
        streams = shared('runtime.streams')
        data = b'portable embedded data'
        class ShortRead(BytesIO):
            def read(self, count=-1):
                return super().read(min(count, 3))
        class ShortWrite(BytesIO):
            def write(self, data):
                return super().write(data[:2])
        self.assertEqual(streams.read_up_to(ShortRead(data), len(data) + 1), data)
        output = ShortWrite()
        streams.copy_stream(ShortRead(data), output)
        self.assertEqual(output.getvalue(), data)
        RangeReader = shared('runtime.resources.range_reader').RangeReader
        with RangeReader(8, lambda start, count: b'12345678'[start:start + count]) as stream:
            target = array('I', [0, 0])
            self.assertEqual(stream.readinto(target), target.itemsize * len(target))
            self.assertEqual(target.tobytes(), b'12345678')
        item = {'path': 'synthetic'}
        result = shared('runtime.operations').run_batch([item], lambda value: True)
        self.assertEqual(result.completed, [item])
        self.assertFalse(result.failed)

    def test_native_publication_and_collision_preservation(self):
        persistence = shared('persistence')
        publication = shared('persistence.publication')
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            target, stage = root / 'target', root / 'stage'
            target.mkdir(); stage.mkdir()
            (target / 'old').write_bytes(b'old')
            (stage / 'new').write_bytes(b'new')
            backup = persistence.promote_path(stage, target)
            self.assertEqual((backup / 'old').read_bytes(), b'old')
            self.assertEqual((target / 'new').read_bytes(), b'new')
            source, occupied = root / 'source', root / 'occupied'
            source.mkdir(); occupied.mkdir()
            with self.assertRaises(FileExistsError):
                publication.rename_exclusive(source, occupied)
            self.assertTrue(source.is_dir())
            self.assertEqual(list(occupied.iterdir()), [])
            renamed = root / 'renamed'
            shared('filesystem.rename').rename_path(source, renamed)
            self.assertTrue(renamed.is_dir())

    def test_archive_and_json_publication(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / 'sample.zip'
            with zipfile.ZipFile(archive, 'w') as output:
                output.writestr('nested/sample.txt', 'embedded')
            destination = root / 'extracted'
            shared('archives.extraction').extract(archive, destination)
            self.assertEqual((destination / 'nested/sample.txt').read_text(), 'embedded')
            with self.assertRaises(FileExistsError):
                shared('archives.extraction').extract(archive, destination)
            record = shared('formats.jsonType').JSONFile(root / 'record.json')
            record.write_json({'name': '😀'})
            self.assertEqual(record.read_json(), {'name': '😀'})
            before = record.path.read_bytes()
            with self.assertRaises(ValueError):
                record.write_json({'invalid': float('nan')})
            self.assertEqual(record.path.read_bytes(), before)

    def test_embedded_command_capture(self):
        import bpy
        result = shared('integrations.wrappers.cmdShellWrapper').run_command(
            [bpy.app.binary_path, '--version'], timeout=30)
        self.assertTrue(result.success, result)
        self.assertTrue(any(line.startswith('Blender ') for line in result.stdout))


def main():
    import bpy
    if NAMESPACE in sys.modules:
        raise RuntimeError('Smoke-test namespace is already loaded')
    package = types.ModuleType(NAMESPACE)
    package.__path__ = [str(ROOT)]
    sys.modules[NAMESPACE] = package
    try:
        with TemporaryDirectory(prefix='bluehole-embedded-') as temporary:
            root = Path(temporary)
            home = root / 'home'
            home.mkdir()
            environment = {'COMMONUTILS_STORAGE_ROOT': str(root / 'shared'),
                           'XDG_CONFIG_HOME': str(home / '.config'), 'XDG_CACHE_HOME': str(home / '.cache'),
                           'APPDATA': str(home / 'AppData/Roaming'), 'LOCALAPPDATA': str(home / 'AppData/Local')}
            with patch.dict(os.environ, environment), patch.object(Path, 'home', return_value=home):
                suite = unittest.defaultTestLoader.loadTestsFromTestCase(EmbeddedSharedTests)
                result = unittest.TextTestRunner(verbosity=2).run(suite)
            print(json.dumps({'blender': bpy.app.version_string, 'python': sys.version.split()[0],
                              'shared': (ROOT / 'Lib/commonUtils.revision').read_text().strip(),
                              'tests': result.testsRun, 'registration_tested': False}))
            if not result.wasSuccessful():
                raise RuntimeError('Embedded shared-library smoke tests failed')
    finally:
        for name in tuple(sys.modules):
            if name == NAMESPACE or name.startswith(NAMESPACE + '.'):
                sys.modules.pop(name, None)


def launch(binary):
    """Start Blender with temporary user resources before its Python initializes."""
    with TemporaryDirectory(prefix='bluehole-profile-') as temporary:
        root = Path(temporary)
        environment = dict(os.environ)
        environment.pop('PYTHONPATH', None)
        environment['PYTHONNOUSERSITE'] = '1'
        for key in ('RESOURCES', 'CONFIG', 'SCRIPTS', 'EXTENSIONS', 'DATAFILES'):
            folder = root / key.lower()
            folder.mkdir()
            environment['BLENDER_USER_' + key] = str(folder)
        return subprocess.run([str(binary), '--background', '--factory-startup', '--disable-autoexec',
            '--python-exit-code', '1', '--python', str(Path(__file__).resolve())],
            env=environment, timeout=90).returncode


if __name__ == '__main__':
    if '--blender' in sys.argv:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--blender', type=Path, required=True)
        args = parser.parse_args()
        raise SystemExit(launch(args.blender.resolve(strict=True)))
    main()
