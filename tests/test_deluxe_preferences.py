"""Exercise Deluxe activation and legacy recovery without touching Blender profiles."""

from hashlib import sha256
import importlib
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch


class Settings(dict):
    """Model Blender RNA defaults separately from saved ID properties."""
    def __init__(self, **defaults):
        super().__init__()
        self.defaults = defaults
        self.bl_rna = SimpleNamespace(properties=[
            SimpleNamespace(type='BOOLEAN', identifier=name) for name in defaults
        ])

    def __getattr__(self, name):
        if name not in self.defaults:
            raise AttributeError(name)
        return self.get(name, self.defaults[name])

    def is_property_set(self, name):
        return name in self


class DeluxePreferencesTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.saved = self.root / 'config/userpref.blend'
        self.preset = self.root / 'scripts/presets/keyconfig/BH_Keymaps.py'
        self.saved.parent.mkdir()
        self.preset.parent.mkdir(parents=True)

        package_name = '_bluehole_deluxe_tests'
        package = ModuleType(package_name)
        package.__path__ = [str(Path(__file__).resolve().parents[1])]
        blender = ModuleType('bpy')
        blender.utils = SimpleNamespace(
            user_resource=lambda kind, *, path: str(self.root / kind.lower() / path),
            preset_find=lambda name, *_args, **_kwargs: (
                str(self.preset) if name == self.preset.stem and self.preset.is_file() else None),
        )
        patcher = patch.dict(sys.modules, {package_name: package, 'bpy': blender})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.module = importlib.import_module(f'{package_name}.overlays.deluxe.applyDeluxePrefs')
        keymaps = importlib.import_module(f'{package_name}.keymaps')
        self.refresh = Mock(return_value=12)
        self.pending_cleanup = Mock(return_value=())
        keymaps.keymaps_register = SimpleNamespace(
            refresh=self.refresh, keymap_utils=SimpleNamespace(pending_cleanup=self.pending_cleanup))
        sys.modules[f'{package_name}.preferences.addon.keymap_props'] = SimpleNamespace(
            KEYMAP_CATEGORIES=('navigation',),
        )

        self.pref = SimpleNamespace(
            keymap=Settings(enable_keymaps=False, deluxe_configured=False),
            pie=Settings(enable_pie_menus=False, enable_editor_pie_shortcuts=True),
            thirdparty=SimpleNamespace(
                auto_constraints=Settings(enable_modal=True),
                x_ray_selection_tools=Settings(enable_xray=True),
            ),
        )
        self.pref.keymap.navigation = Settings(enable_navigation_keymaps=True)
        self.factory = SimpleNamespace(name='Blender')
        self.configs = SimpleNamespace(active=self.factory, default=self.factory,
                                       user=SimpleNamespace(keymaps=[]))
        self.context = SimpleNamespace(
            preferences=SimpleNamespace(
                keymap=SimpleNamespace(active_keyconfig='Blender'), is_dirty=False,
                inputs=SimpleNamespace(invert_mouse_zoom=False), addons={'existing': object()},
            ),
            window_manager=SimpleNamespace(keyconfigs=self.configs),
        )

    def apply(self, **kwargs):
        self.module.apply_deluxe_prefs(self.context, self.pref, **kwargs)

    def test_activation_saves_only_master_state_without_writing_files(self):
        self.assertFalse(self.pref.keymap.enable_keymaps)
        self.assertFalse(self.pref.pie.enable_pie_menus)
        self.apply()
        self.assertTrue(self.pref.keymap.deluxe_configured)
        self.assertTrue(self.pref.keymap.enable_keymaps)
        self.assertTrue(self.pref.keymap.navigation.enable_navigation_keymaps)
        self.assertFalse(self.pref.pie.enable_pie_menus)
        self.assertEqual(dict(self.pref.pie), {})
        self.assertTrue(self.pref.pie.enable_editor_pie_shortcuts)
        self.assertFalse(self.context.preferences.inputs.invert_mouse_zoom)
        self.assertFalse(self.saved.exists())
        self.assertFalse(self.preset.exists())
        self.assertTrue(self.context.preferences.is_dirty)
        self.assertEqual(dict(self.pref.keymap), {'deluxe_configured': True, 'enable_keymaps': True})
        self.refresh.assert_called_once_with()

    def test_saved_choices_survive_activation_disable_and_reenable(self):
        self.pref.pie['enable_pie_menus'] = False
        self.pref.keymap.navigation['enable_navigation_keymaps'] = False
        self.pref.thirdparty.auto_constraints['enable_modal'] = False
        self.apply()
        self.module.disable_deluxe_keymaps(self.context, self.pref)
        self.assertFalse(self.pref.keymap.enable_keymaps)
        self.apply()
        self.assertTrue(self.pref.keymap.enable_keymaps)
        self.assertFalse(self.pref.pie.enable_pie_menus)
        self.assertFalse(self.pref.keymap.navigation.enable_navigation_keymaps)
        self.assertFalse(self.pref.thirdparty.auto_constraints.enable_modal)

    def test_current_and_missing_legacy_presets_cannot_be_overlaid(self):
        for active in (SimpleNamespace(name='BH_Keymaps'), self.factory):
            with self.subTest(active=active):
                self.configs.active = active
                self.context.preferences.keymap.active_keyconfig = 'BH_Keymaps'
                with self.assertRaisesRegex(ValueError, 'Select Blender'):
                    self.apply(reviewed=True)
        self.assertFalse(self.pref.keymap.deluxe_configured)
        self.refresh.assert_not_called()

    def test_known_profile_waits_for_review_with_or_without_old_backups(self):
        self.saved.write_bytes(b'legacy plus personal preferences')
        self.preset.write_bytes(b'legacy plus personal shortcuts')
        personal = SimpleNamespace(is_user_modified=True)
        self.configs.user.keymaps.append(personal)
        prior = self.saved.with_name('userpref.blend.previous-abc')
        for with_backup in (False, True):
            with self.subTest(with_backup=with_backup):
                if with_backup:
                    prior.write_bytes(b'older settings')
                self.assertTrue(self.module.has_legacy_profile(self.context))
                with self.assertRaisesRegex(ValueError, 'Review the saved shortcuts'):
                    self.apply()
                self.assertFalse(self.pref.keymap.deluxe_configured)
        addon = self.context.preferences.addons['existing']
        self.apply(reviewed=True)
        self.assertEqual(self.saved.read_bytes(), b'legacy plus personal preferences')
        self.assertEqual(self.preset.read_bytes(), b'legacy plus personal shortcuts')
        self.assertEqual(prior.read_bytes(), b'older settings')
        self.assertIs(self.configs.user.keymaps[0], personal)
        self.assertIs(self.context.preferences.addons['existing'], addon)
        self.refresh.assert_called_once_with()

    def test_ambiguous_preset_and_unattributed_saved_edits_require_review(self):
        self.configs.active = SimpleNamespace(name='Custom')
        with self.assertRaisesRegex(ValueError, 'Select Blender'):
            self.apply()
        self.assertEqual(self.configs.active.name, 'Custom')
        self.configs.active = self.factory
        self.configs.user.keymaps.append(SimpleNamespace(is_user_modified=True))
        with self.assertRaisesRegex(ValueError, 'Review the saved shortcuts'):
            self.apply()

    def test_exact_legacy_preferences_detected_with_preset_missing(self):
        payload = b'original shipped settings'
        self.saved.write_bytes(payload)
        with patch.multiple(self.module, LEGACY_PREFERENCES_SIZE=len(payload),
                            LEGACY_PREFERENCES_HASH=sha256(payload).hexdigest()):
            self.assertTrue(self.module.has_legacy_profile(self.context))
            self.saved.write_bytes(b'different preferences')
            self.assertFalse(self.module.has_legacy_profile(self.context))

    def test_preference_backup_alone_does_not_stamp_profile(self):
        self.saved.with_name('userpref.blend.previous-abc').write_bytes(b'ordinary recovery data')
        self.assertFalse(self.module.has_legacy_profile(self.context))
        self.preset.with_name('BH_Keymaps.py.previous-abc').write_bytes(b'previous preset')
        self.assertTrue(self.module.has_legacy_profile(self.context))

    def test_failed_refresh_restores_the_exact_previous_choices(self):
        self.pref.pie['enable_pie_menus'] = False
        self.refresh.side_effect = [RuntimeError('failed refresh'), None]
        with self.assertRaisesRegex(RuntimeError, 'failed refresh'):
            self.apply()
        self.assertEqual(dict(self.pref.keymap), {})
        self.assertEqual(dict(self.pref.pie), {'enable_pie_menus': False})
        self.assertFalse(self.context.preferences.is_dirty)
        self.assertEqual(self.refresh.call_count, 2)

    def test_busy_runtime_and_pending_cleanup_leave_activation_off(self):
        for count, pending, message in ((None, (), 'still starting'),
                                        (12, ('owned shortcut',), 'still releasing prior keymaps')):
            with self.subTest(message=message):
                self.refresh.return_value = count
                self.pending_cleanup.return_value = pending
                with self.assertRaisesRegex(RuntimeError, message):
                    self.apply()
                self.assertEqual(dict(self.pref.keymap), {})
                self.assertEqual(dict(self.pref.pie), {})
                self.assertFalse(self.context.preferences.is_dirty)

    def test_failed_rollback_preserves_preference_choices_and_explains_recovery(self):
        self.refresh.side_effect = [RuntimeError('apply failed'), RuntimeError('rollback failed')]
        with self.assertRaisesRegex(RuntimeError, 'Reopen Blender'):
            self.apply()
        self.assertEqual(dict(self.pref.keymap), {})
        self.assertEqual(dict(self.pref.pie), {})
        self.assertFalse(self.context.preferences.is_dirty)


if __name__ == '__main__':
    unittest.main()
