"""Exercise Deluxe installation against temporary files without Blender or PySide."""

import importlib
from pathlib import Path
import stat
import sys
from tempfile import TemporaryDirectory
import types
import unittest
from unittest.mock import Mock, patch


class DeluxePreferencesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load the real implementation and commonUtils without running add-on startup.
        package_name = '_bluehole_deluxe_tests'
        package = types.ModuleType(package_name)
        package.__path__ = [str(Path(__file__).resolve().parents[1])]
        blender_utils = types.ModuleType(f'{package_name}.blenderUtils')
        blender_utils.blenderFile = types.SimpleNamespace(
            get_userpref_path=Mock(), get_keyconfig_path=Mock())
        sys.modules[package_name] = package
        sys.modules[blender_utils.__name__] = blender_utils
        cls.module = importlib.import_module(f'{package_name}.overlays.deluxe.applyDeluxePrefs')
        cls.module.ui.use_pyside = False
        cls.addClassCleanup(lambda: [sys.modules.pop(name, None)
            for name in tuple(sys.modules)
            if name == package_name or name.startswith(package_name + '.')])

    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.payload = root / 'payload'
        (self.payload / 'keyconfig').mkdir(parents=True)
        (self.payload / 'userpref.blend').write_bytes(b'deluxe preferences')
        (self.payload / 'keyconfig' / 'BH_Keymaps.py').write_bytes(b'deluxe keymaps')
        self.prefs = root / 'config' / 'userpref.blend'
        self.keymap = root / 'scripts' / 'presets' / 'keyconfig' / 'BH_Keymaps.py'
        self.log = Mock()
        self.notice = Mock()
        self.exit = Mock(side_effect=SystemExit)
        for target, value in (
            ('get_payload_dir', Mock(return_value=self.payload)),
            ('warning_bh_deluxe', Mock(return_value=True)),
            ('log', self.log),
            ('notice_blender_closure', self.notice),
        ):
            patcher = patch.object(self.module, target, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        for target, value in (
            ('get_userpref_path', self.prefs),
            ('get_keyconfig_path', self.keymap.parent),
        ):
            patcher = patch.object(self.module.blenderFile, target, Mock(return_value=value))
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = patch.object(self.module.sys, 'exit', self.exit)
        patcher.start()
        self.addCleanup(patcher.stop)

    def assert_failed(self, text):
        self.assertFalse(self.module.apply_deluxe_prefs())
        self.notice.assert_not_called()
        self.exit.assert_not_called()
        errors = [call for call in self.log.call_args_list if call.kwargs.get('popup')]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].args[0], self.module.Severity.ERROR)
        self.assertIn(text, errors[0].args[2])

    def test_read_only_files_are_overwritten_and_verified(self):
        for path in (self.prefs, self.keymap):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'old settings')
            path.chmod(stat.S_IRUSR)
        with self.assertRaises(SystemExit):
            self.module.apply_deluxe_prefs()
        self.assertEqual(self.prefs.read_bytes(), b'deluxe preferences')
        self.assertEqual(self.keymap.read_bytes(), b'deluxe keymaps')
        self.assertTrue(self.prefs.stat().st_mode & stat.S_IWUSR)
        self.notice.assert_called_once()

    def test_missing_destination_folders_are_created(self):
        with self.assertRaises(SystemExit):
            self.module.apply_deluxe_prefs()
        self.assertEqual(self.prefs.read_bytes(), b'deluxe preferences')
        self.assertEqual(self.keymap.read_bytes(), b'deluxe keymaps')

    def test_missing_payload_aborts_before_any_overwrite(self):
        self.prefs.parent.mkdir()
        self.prefs.write_bytes(b'original')
        (self.payload / 'keyconfig' / 'BH_Keymaps.py').unlink()
        self.assert_failed('missing or empty')
        self.assertEqual(self.prefs.read_bytes(), b'original')

    def test_locked_destination_shows_underlying_error(self):
        with patch.object(self.module, 'copyfile', side_effect=PermissionError('File is locked')):
            self.assert_failed('PermissionError: File is locked')

    def test_incorrect_copy_is_detected(self):
        def corrupt_copy(source, destination):
            destination.write_bytes(b'wrong contents')
        with patch.object(self.module, 'copyfile', side_effect=corrupt_copy):
            self.assert_failed('Content verification failed')

    def test_second_copy_failure_reports_partial_installation(self):
        copyfile = self.module.copyfile
        def fail_keymap(source, destination):
            if destination == self.keymap:
                raise PermissionError('Keymap locked')
            return copyfile(source, destination)
        with patch.object(self.module, 'copyfile', side_effect=fail_keymap):
            self.assert_failed('Keymap locked')
        self.assertIn(str(self.prefs), self.log.call_args.args[2])
        self.assertEqual(self.prefs.read_bytes(), b'deluxe preferences')

    def test_user_cancellation_does_not_copy_or_show_error(self):
        with patch.object(self.module, 'warning_bh_deluxe', return_value=False):
            self.assertFalse(self.module.apply_deluxe_prefs())
        self.assertFalse(self.prefs.exists())
        self.notice.assert_not_called()
        self.exit.assert_not_called()
        self.assertFalse(any(call.kwargs.get('popup') for call in self.log.call_args_list))


if __name__ == '__main__':
    unittest.main()
