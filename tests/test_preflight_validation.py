"""Operation gates retain lazy checks, early exit and diagnostic behavior without Blender."""
import importlib
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


class PreflightValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        name = '_bluehole_preflight_tests'
        root = Path(__file__).resolve().parents[1]
        package = types.ModuleType(name)
        package.__path__ = [str(root)]
        blender = types.ModuleType(name + '.blenderUtils')
        blender.__path__ = [str(root / 'blenderUtils')]
        blender.blenderFile = types.SimpleNamespace()
        blender.objectUtils = types.SimpleNamespace()
        blender.projectUtils = types.SimpleNamespace()
        environment = types.ModuleType(name + '.environment')
        environment.envPathResolver = types.SimpleNamespace()
        preferences = types.ModuleType(name + '.preferences.prefs')
        preferences.prefs = Mock()
        addon = types.ModuleType('addon_utils')
        addon.check = Mock(return_value=(True, True))
        cls.modules = patch.dict(sys.modules, {name: package, blender.__name__: blender,
            environment.__name__: environment, preferences.__name__: preferences, 'addon_utils': addon})
        cls.modules.start()
        cls.addClassCleanup(cls.modules.stop)
        cls.addClassCleanup(lambda: [sys.modules.pop(key, None) for key in tuple(sys.modules)
            if key == name or key.startswith(name + '.')])
        cls.module = importlib.import_module(name + '.blenderUtils.filterUtils')

    def setUp(self):
        self.events = []
        m = self.module
        def observed(name, value):
            def call(*args, **kwargs):
                self.events.append(name)
                return value
            return Mock(side_effect=call)
        self.settings = types.SimpleNamespace(
            directory=types.SimpleNamespace(sc_dir_struct_scenes='Scenes'),
            sourcecontrol=types.SimpleNamespace(source_control_enable=True, win32_env_override=False))
        values = {
            'blenderFile': types.SimpleNamespace(
                get_blend_file_path=observed('blend', '/source/project/scene.blend'),
                get_blend_directory_path=observed('blend_dir', '/source/project'),
                get_blend_file_name=observed('blend_name', 'scene')),
            'objectUtils': types.SimpleNamespace(get_selection=observed('selection', [object()])),
            'projectUtils': types.SimpleNamespace(get_project_sub_dir=observed('scene_dir', '/source/project')),
            'envPathResolver': types.SimpleNamespace(
                get_valid_unity_asset_dir_path=observed('unity', Path('/unity/Assets')),
                get_valid_godot_project_dir_path=observed('godot', Path('/godot'))),
            'check_blend_location_in_dir_structure': observed('layout', True),
            'prefs': observed('prefs', self.settings),
            'P4Info': observed('connection', types.SimpleNamespace(status=True)),
            'get_valid_source_content_path': observed('source', Path('/source')),
            'get_os': observed('platform', m.OS.LINUX),
            'log': Mock(),
        }
        self.real_location_check = m.check_blend_location_in_dir_structure
        for name, value in values.items():
            patcher = patch.object(m, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_unused_checks_do_not_read_blender_preferences_or_paths(self):
        self.assertTrue(self.module.check_tests('Example'))
        self.assertEqual(self.events, [])
        self.module.log.assert_not_called()

    def test_all_enabled_checks_keep_their_order_and_reuse_source_path(self):
        self.assertTrue(self.module.check_tests('Example', check_blend_exist=True,
            check_blend_loc_in_dir_structure=True, check_selection_not_empty=True,
            check_source_control_enable=True, check_source_control_connection=True,
            check_source_content_root_path_exist=True, check_blend_in_source_content=True,
            check_unity_assets_path_exist=True, check_godot_project_root_path_exist=True))
        self.assertEqual(self.events, ['blend', 'layout', 'selection', 'prefs', 'connection',
                                     'source', 'platform', 'blend_dir', 'unity', 'godot'])

    def test_first_failed_gate_stops_before_connection_and_path_lookups(self):
        m = self.module
        m.blenderFile.get_blend_file_path.side_effect = None
        m.blenderFile.get_blend_file_path.return_value = ''
        self.assertFalse(m.check_tests('Example', check_blend_exist=True,
            check_selection_not_empty=True, check_source_control_connection=True,
            check_source_content_root_path_exist=True))
        self.assertEqual(self.events, [])
        m.objectUtils.get_selection.assert_not_called()
        m.P4Info.assert_not_called()
        m.get_valid_source_content_path.assert_not_called()
        self.assertEqual([c.args[0] for c in m.log.call_args_list], [m.Severity.ERROR, m.Severity.CRITICAL])
        self.assertIn('Save the Blender file', m.log.call_args.args[2])
        self.assertTrue(m.log.call_args.kwargs['popup'])

    def test_silent_scene_failure_only_logs_the_failed_check(self):
        m = self.module
        m.objectUtils.get_selection.side_effect = None
        m.objectUtils.get_selection.return_value = []
        self.assertFalse(m.check_tests('Example', check_selection_not_empty=True, silent_mode=True))
        m.log.assert_called_once_with(m.Severity.ERROR, 'Example', 'Check Selection not Empty Failed')

    def test_silent_missing_source_still_reports_the_path_without_popup(self):
        m = self.module
        m.get_valid_source_content_path.side_effect = None
        m.get_valid_source_content_path.return_value = None
        self.assertFalse(m.check_tests('Example', check_blend_in_source_content=True, silent_mode=True))
        m.log.assert_called_once()
        self.assertEqual(m.log.call_args.args[0], m.Severity.CRITICAL)
        self.assertFalse(m.log.call_args.kwargs['popup'])
        self.assertIn('Configured Source Content Root Path:\n"None"', m.log.call_args.args[2])
        m.blenderFile.get_blend_directory_path.assert_not_called()

    def test_windows_membership_is_case_insensitive_but_unix_is_not(self):
        m = self.module
        for platform, expected in ((m.OS.WIN, True), (m.OS.LINUX, False), (m.OS.MAC, False)):
            with self.subTest(platform=platform):
                m.get_os.side_effect = None
                m.get_os.return_value = platform
                m.get_valid_source_content_path.side_effect = None
                m.get_valid_source_content_path.return_value = Path('/SOURCE')
                self.assertEqual(m.check_tests('Example', check_blend_in_source_content=True), expected)

    def test_logger_failure_is_not_swallowed_or_replaced(self):
        m = self.module
        m.P4Info.side_effect = None
        m.P4Info.return_value = types.SimpleNamespace(status=False)
        def diagnostic(severity, *args, **kwargs):
            if severity is m.Severity.CRITICAL:
                raise RuntimeError('diagnostic failure')
        m.log.side_effect = diagnostic
        with self.assertRaisesRegex(RuntimeError, 'diagnostic failure'):
            m.check_tests('Example', check_source_control_connection=True)

    def test_scene_layout_normalizes_slashes_without_changing_directory_policy(self):
        m = self.module
        m.projectUtils.get_project_sub_dir.side_effect = None
        m.projectUtils.get_project_sub_dir.return_value = '/source/project'
        m.blenderFile.get_blend_file_path.side_effect = None
        m.blenderFile.get_blend_file_path.return_value = '\\source\\project\\scene.blend'
        self.assertTrue(self.real_location_check())
        m.blenderFile.get_blend_file_path.return_value = '/other/scene.blend'
        self.assertFalse(self.real_location_check())
