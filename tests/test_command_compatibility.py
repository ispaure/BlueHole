"""Vendored command outcomes and Perforce diagnostics without Blender startup."""
import importlib
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


class CommandCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        name = '_bluehole_command_tests'
        root = Path(__file__).resolve().parents[1]
        package = types.ModuleType(name); package.__path__ = [str(root)]
        blender = types.ModuleType(f'{name}.blenderUtils')
        blender.blenderFile = types.SimpleNamespace()
        prefs = types.ModuleType(f'{name}.preferences.prefs')
        prefs.prefs = Mock()
        sys.modules[name] = package
        sys.modules[blender.__name__] = blender
        sys.modules[prefs.__name__] = prefs
        cls.commands = importlib.import_module(f'{name}.Lib.commonUtils.wrappers.cmdShellWrapper')
        cls.module = importlib.import_module(f'{name}.wrappers.perforce.p4_utils')
        cls.addClassCleanup(lambda: [sys.modules.pop(key, None) for key in tuple(sys.modules)
            if key == name or key.startswith(name + '.')])

    def test_vendored_result_captures_real_exit_status_and_legacy_output(self):
        result = self.commands.run_command([sys.executable, '-c', 'import sys; print("out"); sys.exit(7)'])
        self.assertEqual(result.returncode, 7)
        self.assertEqual(result.lines, ['out'])
        self.assertFalse(result.success)
        self.assertEqual(self.commands.exec_cmd('echo compatible'), ['compatible'])

    def test_perforce_missing_file_diagnostics_retain_parser_contract(self):
        result = self.commands.CommandResult(1, stderr=('file - no such file(s).',))
        with patch.object(self.module, 'get_os', return_value=self.module.OS.WIN), patch.object(
                self.commands, 'run_command', return_value=result) as run:
            self.assertEqual(self.module.exec_p4_command('p4 fstat "file"'), result.lines)
        self.assertEqual(run.call_args.kwargs, {'shell': True, 'idle_timeout': 15})

    def test_perforce_timeout_never_returns_partial_success(self):
        result = self.commands.CommandResult(-1, stdout=('partial',), timed_out=True)
        def fail(severity, title, message, **kwargs):
            if severity == self.module.Severity.CRITICAL:
                raise RuntimeError(message)
        with patch.object(self.module, 'get_os', return_value=self.module.OS.WIN), patch.object(
                self.commands, 'run_command', return_value=result), patch.object(self.module, 'log', side_effect=fail):
            with self.assertRaisesRegex(RuntimeError, 'timed out'):
                self.module.exec_p4_command('p4 edit "file"')

    def test_adapter_uses_lazy_preferences_and_shared_module_identity(self):
        adapter = importlib.import_module(self.module.__name__.split('.Lib.')[0] + '.wrappers.perforce')
        preference_module = importlib.import_module(adapter.__name__.split('.wrappers.')[0] + '.preferences.prefs')
        settings = types.SimpleNamespace(source_control_enable=True, source_control_solution='perforce',
            linux_env_setting_p4user='alice', linux_env_setting_p4port='server:1666', linux_env_setting_p4client='work',
            p4_parallel_path_linux='/opt/p4', p4v_app_path_mac='/Applications/P4V.app')
        with patch.object(preference_module, 'prefs', return_value=types.SimpleNamespace(sourcecontrol=settings)), patch.object(adapter, 'get_os', return_value=adapter.OS.LINUX):
            self.assertEqual(adapter._environment(), {'P4USER': 'alice', 'P4PORT': 'server:1666', 'P4CLIENT': 'work'})
            settings.linux_env_setting_p4user = 'bob'
            self.assertEqual(adapter._environment()['P4USER'], 'bob')
            self.assertEqual(adapter._executable(adapter.OS.LINUX), '/opt/p4')
            self.assertEqual(adapter._executable(adapter.OS.MAC), '/Applications/P4V.app/Contents/Resources/p4_parallel')
            settings.source_control_enable = False
            self.assertEqual(adapter._environment(), {})
        compat = importlib.import_module(adapter.__name__ + '.p4_file_group')
        shared = importlib.import_module(adapter.__name__.split('.wrappers.')[0] + '.Lib.commonUtils.wrappers.perforce.p4_file_group')
        self.assertIs(compat, shared)

    def test_blend_file_keeps_filter_and_scene_reload_callbacks(self):
        root = self.module.__name__.split('.Lib.')[0]
        blender = importlib.import_module(root + '.blenderUtils')
        filters = types.SimpleNamespace(check_tests=Mock(return_value=False))
        bpy = types.ModuleType('bpy')
        bpy.ops = types.SimpleNamespace(wm=types.SimpleNamespace(open_mainfile=Mock()))
        with patch.dict(sys.modules, {'bpy': bpy}), patch.object(blender, 'filterUtils', filters, create=True):
            module = importlib.import_module(root + '.wrappers.perforce.p4_file')
            shared = importlib.import_module(root + '.Lib.commonUtils.wrappers.perforce.p4_file')
            self.assertIs(module.P4File, shared.P4File)
            file = module.BlendP4File('/work/scene.blend')
            with patch.object(shared.P4File, 'open_for_edit', return_value=True) as edit:
                self.assertFalse(file.open_blend_for_edit(allow_sync=True))
                edit.assert_not_called()
                filters.check_tests.return_value = True
                file.open_blend_for_edit(allow_sync=True, silent=True)
                edit.assert_called_once_with(silent=True, allow_sync=True)
            file._callback_post_sync()
            bpy.ops.wm.open_mainfile.assert_called_once_with(filepath='/work/scene.blend')
