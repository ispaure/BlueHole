"""Run portable vendored contracts in Blender's embedded Python, without registration."""
import argparse
import asyncio
import importlib
import json
import os
from pathlib import Path
import sys
import subprocess
from tempfile import TemporaryDirectory
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = '_bluehole_embedded_smoke'
OWNED_NAMESPACES = (NAMESPACE, 'commonUtils', 'test_pie_actions')
# Reuse portable library regressions; GUI/host-Python subprocess tests need their own runtimes.
PORTABLE_TESTS = (
    'test_streams', 'test_browsing', 'test_persistence', 'test_session_store', 'test_batch',
    'test_local_access', 'test_bulk_rename', 'test_sse_framing', 'test_json_type', 'test_xml',
    'test_archives.ArchiveWorkspaceTests.test_selected_directory_extracts_descendants_preserving_paths',
    'test_archives.ArchiveWorkspaceTests.test_racing_destination_at_extraction_publication_is_preserved',
    'test_archives.ArchiveWorkspaceTests.test_extract_rejects_managed_destination_before_creating_parent_folders',
    'test_archives.ArchiveWorkspaceTests.test_extract_rechecks_provider_boundary_before_complete_tree_publication',
)


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
        standalone = importlib.import_module('commonUtils.runtime.platform')
        self.assertTrue(Path(standalone.__file__).is_relative_to(ROOT / 'Lib/commonUtils'))
        self.assertIsNot(shared('runtime.platform'), standalone)
        self.assertIsNot(shared('formats.registry').file_types,
                         importlib.import_module('commonUtils.formats.registry').file_types)
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

    def test_embedded_command_capture(self):
        import bpy
        result = shared('integrations.wrappers.cmdShellWrapper').run_command(
            [bpy.app.binary_path, '--version'], timeout=30)
        self.assertTrue(result.success, result)
        self.assertTrue(any(line.startswith('Blender ') for line in result.stdout))


def main():
    import bpy
    if any(name in sys.modules for name in OWNED_NAMESPACES):
        raise RuntimeError('Smoke-test library namespaces are already loaded')
    original_path = sys.path[:]
    sys.path[:0] = [str(ROOT / 'Lib'), str(ROOT / 'tests')]
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
                suite = unittest.TestSuite((
                    unittest.defaultTestLoader.loadTestsFromTestCase(EmbeddedSharedTests),
                    unittest.defaultTestLoader.loadTestsFromNames(
                        ['commonUtils.tests.' + name for name in PORTABLE_TESTS]),
                    unittest.defaultTestLoader.loadTestsFromName('test_pie_actions'),
                ))
                standalone_logging = importlib.import_module('commonUtils.runtime.diagnostics').noninteractive_logging
                with standalone_logging(), shared('runtime.diagnostics').noninteractive_logging():
                    result = unittest.TextTestRunner(verbosity=2).run(suite)
            print(json.dumps({'blender': bpy.app.version_string, 'python': sys.version.split()[0],
                              'shared': (ROOT / 'Lib/commonUtils.revision').read_text().strip(),
                              'tests': result.testsRun, 'skipped': len(result.skipped), 'registration_tested': False}))
            if not result.wasSuccessful():
                raise RuntimeError('Embedded shared-library smoke tests failed')
    finally:
        sys.path[:] = original_path
        for name in tuple(sys.modules):
            if any(name == owner or name.startswith(owner + '.') for owner in OWNED_NAMESPACES):
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
