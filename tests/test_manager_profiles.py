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
            def call(profile, action, values, environment=None):
                output = io.StringIO()
                payload = json.dumps(dict(schema=1, action=action, values=values, settings_profile=str(profile)))
                with patch('sys.stdin', io.StringIO(payload)), contextlib.redirect_stdout(output), \
                        patch('build_manager.registry.config_directory', return_value=root), patch.dict(os.environ, environment or {}, clear=True):
                    manager_bridge.main()
                return json.loads(output.getvalue())['result']
            first, second = root/'one/profile.json', root/'two/profile.json'
            call(first, 'save_settings', {'changes': {'tools.blender': 'first'}})
            call(second, 'save_settings', {'changes': {'tools.blender': 'second'}})
            self.assertEqual(call(first, 'settings', {})['tools.blender']['value'], 'first')
            self.assertEqual(call(second, 'settings', {})['tools.blender']['value'], 'second')
            self.assertEqual(load_profile(first)['tools.shared_source'], 'shared')
            self.assertEqual(load_profile(legacy)['tools.blender'], 'original')
            legacy_before = legacy.read_bytes()
            environment = {'BLUEHOLE_BLENDER': '/fixture/environment-blender'}
            row = call(first, 'settings', {}, environment)['tools.blender']
            self.assertEqual(row['reset'], dict(overridden=True, value='/fixture/environment-blender',
                                                origin='environment BLUEHOLE_BLENDER'))
            before = first.read_bytes()
            with self.assertRaises(ValueError):
                call(first, 'save_settings', {'changes': {}, 'resets': ['auth.github_reference']})
            self.assertEqual(first.read_bytes(), before)
            call(first, 'save_settings', {'changes': {'tools.hosted_evidence': ''},
                                          'resets': ['tools.blender']}, environment)
            self.assertEqual(call(first, 'settings', {}, environment)['tools.blender']['value'],
                             '/fixture/environment-blender')
            inherited = call(first, 'settings', {})['tools.blender']
            self.assertEqual(inherited['value'], '')
            self.assertEqual(inherited['origin'], 'tracked unconfigured default')
            self.assertFalse(inherited['reset']['overridden'])
            self.assertEqual(call(first, 'settings', {})['tools.hosted_evidence']['origin'],
                             'private project tooling profile')
            self.assertEqual(load_profile(first), {'tools.shared_source': 'shared', 'tools.hosted_evidence': ''})
            self.assertEqual(load_profile(second)['tools.blender'], 'second')
            third = root/'three/profile.json'
            call(third, 'save_settings', {'changes': {}, 'resets': ['tools.blender']})
            self.assertEqual(load_profile(third), {'tools.shared_source': 'shared'})
            self.assertEqual(legacy.read_bytes(), legacy_before)

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
            branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=root, text=True).strip()
            options = dict(operation='Check', target='blender', backend='Local',
                           suite='portable.contracts', timeout=20)
            if branch == 'blender-5.2.2/alpha':
                plan = bridge.call('plan', **options)
                self.assertEqual([phase['id'] for phase in plan['phases']], ['portable-contracts'])
            else:
                # Promoted and detached checkouts keep the same alpha-only
                # packaging adapter. Test its restriction instead of bypassing it.
                with self.assertRaisesRegex(ValueError, 'limited to the existing Blender 5.2.2 alpha branch'):
                    bridge.call('plan', **options)
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
