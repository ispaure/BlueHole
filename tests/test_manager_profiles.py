"""Per-checkout settings isolation; legacy defaults do not override saved values."""
import contextlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from Scripts import manager_bridge
from build_manager.profiles import save_profile, load_profile


class ManagerProfileTests(unittest.TestCase):
    def test_profiles_keep_legacy_defaults_and_isolate_registration_overrides(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / 'projects/io.github.ispaure.bluehole.json'
            save_profile(legacy, {'tools.blender': 'original', 'tools.shared_source': 'shared'},
                         allowed={'tools.blender','tools.shared_source'})
            def call(profile, action, values):
                output = io.StringIO()
                payload = json.dumps(dict(schema=1, action=action, values=values, settings_profile=str(profile)))
                with patch('sys.stdin', io.StringIO(payload)), contextlib.redirect_stdout(output), \
                        patch('build_manager.registry.config_directory', return_value=root), patch.dict(os.environ, {}, clear=True):
                    manager_bridge.main()
                return json.loads(output.getvalue())['result']
            first, second = root/'one/profile.json', root/'two/profile.json'
            call(first, 'save_settings', {'changes': {'tools.blender': 'first'}})
            call(second, 'save_settings', {'changes': {'tools.blender': 'second'}})
            self.assertEqual(call(first, 'settings', {})['tools.blender']['value'], 'first')
            self.assertEqual(call(second, 'settings', {})['tools.blender']['value'], 'second')
            self.assertEqual(load_profile(first)['tools.shared_source'], 'shared')
            self.assertEqual(load_profile(legacy)['tools.blender'], 'original')

    def test_real_project_bridge_resolves_project_vendored_dependency(self):
        from build_manager.bridge import ProjectBridge
        from build_manager.registry import Registry
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as directory:
            registry = Registry(Path(directory))
            key = registry.add(root)
            registry.trust(key)
            row, _ = registry.resolve(key)
            profile = registry.path.parent / row['name'] / 'profile.json'
            save_profile(profile, {}, allowed=set())
            bridge = ProjectBridge(registry, key)
            settings = bridge.call('settings', timeout=20)
            plan = bridge.call('plan', operation='Check', target='blender', backend='Local',
                               suite='portable.contracts', timeout=20)
            self.assertEqual([phase['id'] for phase in plan['phases']], ['portable-contracts'])
            self.assertEqual(settings['project.identity']['value'], 'Blue Hole · Blender 5.2.2 alpha')
            environment = dict(os.environ, BUILD_MANAGER_DEPENDENCIES='project')
            environment.pop('PYTHONPATH', None)
            environment.pop('PYTHONHOME', None)
            code = ("import runpy;from pathlib import Path;"
                    "runpy.run_path('Scripts/manager_bridge.py',run_name='bridge_contract');"
                    "import build_manager,commonUtils;"
                    "assert Path(commonUtils.__file__).resolve()==Path('Lib/commonUtils/__init__.py').resolve();"
                    "print('project vendor resolved')")
            result = subprocess.run([sys.executable, '-c', code], cwd=root, env=environment,
                                    capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), 'project vendor resolved')
