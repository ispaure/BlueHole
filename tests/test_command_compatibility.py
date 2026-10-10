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
