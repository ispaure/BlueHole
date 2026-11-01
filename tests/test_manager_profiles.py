"""Per-checkout settings isolation; legacy defaults do not override saved values."""
import contextlib
import io
import json
import os
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
