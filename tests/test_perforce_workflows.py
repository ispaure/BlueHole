"""Blue Hole source-control callbacks keep saves permissive, outside Blender."""
import importlib
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


class BlueHoleWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(os.environ.get('BLUEHOLE_TEST_ROOT', Path(__file__).resolve().parents[1]))
        cls.name = '_bluehole_workflow_tests'
        package = types.ModuleType(cls.name)
        package.__path__ = [str(root)]
        blender = types.ModuleType(cls.name + '.blenderUtils')
        blender.__path__ = [str(root / 'blenderUtils')]
        cls.file = types.SimpleNamespace(has_blend_filepath=lambda: True,
                                        get_blend_file_path=lambda: '/work/scene.blend')
        blender.blenderFile = cls.file
        blender.filterUtils = types.SimpleNamespace(check_tests=Mock(return_value=True))
        cls.settings = types.SimpleNamespace(source_control_enable=True, source_control_solution='perforce')
        cls.preferences = types.SimpleNamespace(sourcecontrol=cls.settings,
            bridge=types.SimpleNamespace(enable_pre_export_override=False, enable_post_export_override=False),
            container=types.SimpleNamespace(asset_hierarchy_struct_prefix_static_mesh='SM_',
                asset_hierarchy_struct_prefix_static_mesh_kit='KIT_', asset_hierarchy_struct_prefix_skeletal_mesh='SK_'))
        prefs = types.ModuleType(cls.name + '.preferences.prefs')
        prefs.prefs = lambda: cls.preferences
        bpy = types.ModuleType('bpy')
        bpy.ops = types.SimpleNamespace(wm=types.SimpleNamespace(open_mainfile=Mock(), save_as_mainfile=Mock(return_value={'FINISHED'})))
        bpy.app = types.SimpleNamespace(handlers=types.SimpleNamespace(persistent=lambda f: f))
        bpy.types = types.SimpleNamespace(Operator=type('Operator', (), {}))
        props = types.ModuleType('bpy.props')
        props.StringProperty = props.BoolProperty = lambda **kwargs: None
        bpy.props = props
        extras = types.ModuleType('bpy_extras.io_utils')
        extras.ExportHelper = type('ExportHelper', (), {})
        cls.modules = patch.dict(sys.modules, {cls.name: package, blender.__name__: blender,
            prefs.__name__: prefs, 'bpy': bpy, 'bpy.props': props, 'bpy_extras.io_utils': extras})
        cls.modules.start()
        cls.addClassCleanup(cls.modules.stop)
        cls.addClassCleanup(lambda: [sys.modules.pop(key, None) for key in tuple(sys.modules)
            if key == cls.name or key.startswith(cls.name + '.')])
        cls.adapter = importlib.import_module(cls.name + '.wrappers.perforce.p4_file')
        cls.source = importlib.import_module(cls.name + '.blenderUtils.sourceControlUtils')
        cls.callbacks = importlib.import_module(cls.name + '.blenderUtils.callbacks')
        operators = types.ModuleType(cls.name + '.operators')
        operators.__path__ = [str(root / 'operators')]
        sys.modules[operators.__name__] = operators
        cls.save = importlib.import_module(cls.name + '.operators.save_ops')
        cls.bpy = bpy
        for suffix, relative in (('blenderUtils.export', 'blenderUtils/export'),
                                 ('blenderUtils.export.model', 'blenderUtils/export/model')):
            module = types.ModuleType(cls.name + '.' + suffix)
            module.__path__ = [str(root / relative)]
            sys.modules[module.__name__] = module
        export_settings = types.ModuleType(cls.name + '.blenderUtils.export.exportSettings')
        export_settings.ExportSettings = object
        export_settings.Engine = types.SimpleNamespace(UNREAL='unreal')
        container = types.ModuleType(cls.name + '.blenderUtils.export.model.container')
        container.Container = object
        container.ContainerDummy = Mock()
        unreal = types.ModuleType(cls.name + '.unrealUtils')
        unreal.sendUnreal = types.SimpleNamespace(trigger_unreal_import=Mock())
        unreal.renameUnreal = types.SimpleNamespace(trigger_unreal_rename=Mock(return_value=True))
        unreal.communicateUnreal = types.SimpleNamespace(test_unreal_connection=Mock(return_value=True))
        for module in (export_settings, container, unreal):
            sys.modules[module.__name__] = module
        cls.groups = importlib.import_module(cls.name + '.blenderUtils.export.model.containerGroup')
        export = sys.modules[cls.name + '.blenderUtils.export']
        export.exportSettingsPresets = types.SimpleNamespace(get_export_settings=Mock(return_value=object()),
            ExportSettingsPreset=types.SimpleNamespace(UNREAL='unreal'))
        sys.modules[cls.name + '.blenderUtils.export.model'].containerUtils = types.SimpleNamespace(get_container_groups_all=Mock())
        blender.objectUtils = types.SimpleNamespace(get_obj_upmost_parent=lambda obj: obj)
        cls.rename = importlib.import_module(cls.name + '.operators.rename_ops')

    def setUp(self):
        self.settings.source_control_enable = True
        self.callbacks.SKIP_NEXT_SAVE_PRE_SC_CHECK = False
        self.callbacks.CHECK_SC_AFTER_SAVE = False
        self.bpy.ops.wm.save_as_mainfile.reset_mock()

    def test_scene_adapter_and_dispatcher_propagate_success_and_failure(self):
        for outcome in (True, False):
            with patch.object(self.adapter.P4File, 'open_for_edit', return_value=outcome) as edit:
                self.assertIs(self.source.sc_check_blend('/work/scene.blend', allow_sync=False), outcome)
            edit.assert_called_once_with(silent=False, allow_sync=False)

    def test_load_allows_sync_and_save_pre_disallows_it_without_blocking(self):
        with patch.object(self.source, 'sc_check_blend', return_value=False) as checkout:
            self.callbacks.load_post_handler(None)
            checkout.assert_called_once_with('/work/scene.blend', allow_sync=True, silent_mode=False)
            checkout.reset_mock()
            self.assertIsNone(self.callbacks.save_pre_handler(None))
            checkout.assert_called_once_with('/work/scene.blend', allow_sync=False, silent_mode=False)

    def test_existing_save_as_still_saves_after_checkout_failure(self):
        operator = self.save.BHSaveAsMainfile()
        operator.filepath = '/work/existing.blend'
        operator.copy, operator.check_existing = False, True
        operator.compress, operator.relative_remap = False, True
        with patch.object(self.save.os.path, 'exists', return_value=True), patch.object(
                self.source, 'sc_check_blend', return_value=False) as checkout:
            self.assertEqual(operator.execute(None), {'FINISHED'})
            checkout.assert_called_once_with(operator.filepath, allow_sync=False, silent_mode=False)
            self.bpy.ops.wm.save_as_mainfile.assert_called_once()
            # The custom operator already checked its destination. Blender's
            # next save_pre must not query the old current-scene path again.
            self.callbacks.save_pre_handler(None)
            self.assertEqual(checkout.call_count, 1)
            self.assertFalse(self.callbacks.SKIP_NEXT_SAVE_PRE_SC_CHECK)

    def test_new_save_as_checks_after_creation_and_does_not_repeat(self):
        operator = self.save.BHSaveAsMainfile()
        operator.filepath = '/work/new.blend'
        operator.copy, operator.check_existing = False, True
        operator.compress, operator.relative_remap = False, True
        with patch.object(self.save.os.path, 'exists', return_value=False), patch.object(
                self.source, 'sc_check_blend', return_value=False) as checkout:
            self.assertEqual(operator.execute(None), {'FINISHED'})
            checkout.assert_not_called()
            self.callbacks.save_pre_handler(None)
            checkout.assert_not_called()
            self.callbacks.save_post_handler(None)
            checkout.assert_called_once_with('/work/scene.blend', allow_sync=False, silent_mode=False)
            self.callbacks.save_post_handler(None)
            self.assertEqual(checkout.call_count, 1)

    def test_disabled_source_control_returns_success(self):
        self.settings.source_control_enable = False
        with patch.object(self.adapter.P4File, 'open_for_edit') as checkout:
            self.assertTrue(self.source.sc_check_blend('/work/scene.blend', allow_sync=False))
        checkout.assert_not_called()

    def test_export_still_honors_abort_preference(self):
        class Group(self.groups.ContainerGroup):
            def set_containers_from_selection(self, silent_if_empty):
                pass
            def set_containers_from_scene(self, silent_if_empty):
                pass
        for abort in (True, False):
            with self.subTest(abort=abort):
                self.settings.source_control_error_aborts_exp = abort
                item = types.SimpleNamespace(path=Path('/work/export.fbx'), export_proc=Mock(return_value=True))
                group = Group(types.SimpleNamespace(engine='unreal'))
                group.container_lst = [item]
                self.bpy.context = types.SimpleNamespace(view_layer=types.SimpleNamespace(objects=types.SimpleNamespace(active='original')))
                with patch.object(self.groups, 'P4FileGroup') as batch, patch.object(self.groups, 'log'):
                    batch.return_value.open_for_edit.return_value = False
                    self.assertIs(group.export_proc(send=False), not abort)
                self.assertEqual(item.export_proc.call_count, 0 if abort else 1)
                self.assertEqual(self.bpy.context.view_layer.objects.active, 'original')

    def test_rename_stops_before_local_fallback_after_checkout_or_move_failure(self):
        for checkout_ok in (False, True):
            with self.subTest(checkout_ok=checkout_ok):
                root = types.SimpleNamespace(name='SM_old', parent=None)
                def make_group(settings):
                    item = types.SimpleNamespace(root=root, name=root.name, path=Path('/work') / (root.name + '.fbx'))
                    return types.SimpleNamespace(container_lst=[item], set_containers_from_scene=Mock())
                def dummy(root, settings):
                    path = Path('/work') / (root.name + '.uasset')
                    return types.SimpleNamespace(get_path_uasset=lambda: path)
                operator = self.rename.BH_OT_rename_in_outliner_and_unreal()
                operator.new_name = 'SM_new'
                with patch.object(self.rename.containerUtils, 'get_container_groups_all', return_value=[make_group]), patch.object(
                        self.rename, 'ContainerDummy', side_effect=dummy), patch.object(
                        self.rename.os.path, 'isfile', side_effect=lambda path: 'SM_old' in path), patch.object(
                        self.rename.p4_file, 'P4File') as file, patch.object(self.rename.fileUtils, 'File') as local, patch.object(
                        self.rename, 'log'):
                    file.return_value.open_for_edit.return_value = checkout_ok
                    file.return_value.run_p4_move.return_value = False
                    self.assertEqual(operator.execute(types.SimpleNamespace(active_object=root)), {'CANCELLED'})
                    self.assertEqual(file.return_value.run_p4_move.call_count, int(checkout_ok))
                    local.assert_not_called()


if __name__ == '__main__':
    unittest.main()
