"""Personal overrides survive changed defaults, retirement, save, and recovery."""
from copy import deepcopy
import importlib
import json
from pathlib import Path
import unittest

import test_deluxe_profiles


class UserProfileTests(unittest.TestCase):
    def setUp(self):
        self.h = test_deluxe_profiles.ProfileTests()
        self.h.setUp()
        self.addCleanup(self.h.doCleanups)
        self.api = importlib.import_module('_deluxe_profiles_test.keymaps.profile_storage')
        self.base = self.h.store.defaults()

    def test_roundtrip_field_removal_and_disabled_section(self):
        edited = deepcopy(self.base)
        edited['sections']['framing']['enabled'] = False
        edited['commands']['frame-selected']['label'] = 'My label'
        document = self.api.encode_profile(self.base, edited)
        self.assertEqual(self.api.decode_profile(self.base, document).catalog, edited)

    def test_user_values_win_overlapping_edits_and_inherit_other_new_defaults(self):
        personal, update = deepcopy(self.base), deepcopy(self.base)
        personal['events']['frame']['type'] = 'F11'
        update['events']['frame'].update(type='F12', alt=True)
        update['sections']['overview']['label'] = 'New overview'
        decoded = self.api.decode_profile(update, self.api.encode_profile(self.base, personal))
        self.assertEqual(decoded.catalog['events']['frame']['type'], 'F11')
        self.assertTrue(decoded.catalog['events']['frame']['alt'])
        self.assertEqual(decoded.catalog['sections']['overview']['label'], 'New overview')
        self.assertTrue(decoded.conflicts)
        accepted = self.api.encode_profile(update, decoded.catalog)
        self.assertFalse(self.api.decode_profile(update, accepted).conflicts)

    def test_deleted_upstream_edited_binding_is_retained_with_dependencies(self):
        personal, update = deepcopy(self.base), deepcopy(self.base)
        personal['assignments']['view-frame']['active'] = False
        retired = update['assignments'].pop('view-frame')
        update['commands'].pop(retired['command'])
        decoded = self.api.decode_profile(update, self.api.encode_profile(self.base, personal))
        retained = decoded.catalog['assignments']['view-frame']
        self.assertFalse(retained['active'])
        self.assertEqual(retained['feature'], 'view-frame')
        self.assertIn(retained['command'], decoded.catalog['commands'])
        self.assertTrue(decoded.conflicts)

    def test_tombstone_stays_deleted_when_default_disappears(self):
        personal, update = deepcopy(self.base), deepcopy(self.base)
        personal['assignments'].pop('view-frame')
        update['assignments'].pop('view-frame')
        decoded = self.api.decode_profile(update, self.api.encode_profile(self.base, personal))
        self.assertNotIn('view-frame', decoded.catalog['assignments'])

    def test_retired_binding_with_only_a_command_edit_is_preserved(self):
        personal, update = deepcopy(self.base), deepcopy(self.base)
        personal['commands']['frame-selected']['properties']['use_all_regions'] = True
        update['assignments'].pop('view-frame')
        decoded = self.api.decode_profile(update, self.api.encode_profile(self.base, personal))
        self.assertIn('view-frame', decoded.catalog['assignments'])
        self.assertTrue(decoded.catalog['commands']['frame-selected']['properties']['use_all_regions'])

    def test_upstream_operator_change_does_not_receive_old_personal_properties(self):
        personal, update = deepcopy(self.base), deepcopy(self.base)
        personal['commands']['frame-selected']['properties']['use_all_regions'] = True
        update['commands']['frame-selected'] = {'operator': 'wm.other', 'properties': {}}
        decoded = self.api.decode_profile(update, self.api.encode_profile(self.base, personal))
        self.assertEqual(decoded.catalog['commands']['frame-selected'], personal['commands']['frame-selected'])
        self.assertTrue(decoded.conflicts)

    def test_new_required_binding_replaces_old_personal_override(self):
        personal, update = deepcopy(self.base), deepcopy(self.base)
        personal['assignments']['view-frame']['active'] = False
        update['assignments']['view-frame']['required'] = True
        decoded = self.api.decode_profile(update, self.api.encode_profile(self.base, personal))
        self.assertEqual(decoded.catalog['assignments']['view-frame'], update['assignments']['view-frame'])

    def test_new_operator_does_not_inherit_incompatible_old_properties(self):
        personal, update = deepcopy(self.base), deepcopy(self.base)
        personal['commands']['frame-selected'] = {'operator': 'wm.other', 'properties': {'name': 'Menu'}}
        update['commands']['frame-selected']['properties']['use_all_regions'] = True
        decoded = self.api.decode_profile(update, self.api.encode_profile(self.base, personal))
        self.assertEqual(decoded.catalog['commands']['frame-selected'], personal['commands']['frame-selected'])

    def test_legacy_installed_edits_get_a_personal_profile_and_full_backup(self):
        root = self.h.path.parent
        factory = root / 'factory-defaults.json'
        factory.write_text(json.dumps(self.base))
        installed = deepcopy(self.base)
        installed['assignments']['view-frame']['enabled'] = False
        catalog = root / 'deluxe-defaults.json'
        catalog.write_text(json.dumps(installed))
        profile = root / 'config/bluehole/keymaps.json'
        store = self.h.api.ProfileStore.open_user(catalog, profile, lambda: self.h.settings, lambda *args: None)
        self.assertFalse(store.snapshot()['assignments']['view-frame']['enabled'])
        self.assertEqual(json.loads(profile.with_name('legacy-installed-catalog.json').read_text()), installed)
        self.assertEqual(json.loads(catalog.read_text()), installed)
        catalog.write_text(json.dumps(self.base))
        reopened = self.h.api.ProfileStore.open_user(catalog, profile, lambda: self.h.settings, lambda *args: None)
        self.assertEqual(reopened.snapshot(), store.snapshot())

    def test_normal_save_never_changes_the_addon_catalog(self):
        root = self.h.path.parent
        catalog = root / 'deluxe-defaults.json'
        catalog.write_text(json.dumps(self.base))
        before = catalog.read_bytes()
        profile = root / 'config/bluehole/keymaps.json'
        store = self.h.api.ProfileStore.open_user(catalog, profile, lambda: self.h.settings, lambda *args: None)
        draft = store.begin()
        draft.update('assignments', 'view-frame', enabled=False)
        store.apply(draft)
        self.assertEqual(catalog.read_bytes(), before)
        self.assertEqual(json.loads(profile.read_text())['profile_version'], 2)
        profile.write_text('{broken')
        recovered = self.h.api.ProfileStore.open_user(catalog, profile, lambda: self.h.settings, lambda *args: None)
        self.assertEqual(recovered.load_issue, 'invalid_profile_recovered_previous')
        self.assertFalse(recovered.snapshot()['assignments']['view-frame']['enabled'])

    def test_wrong_json_shapes_recover_from_backup_or_defaults(self):
        store, path = self.h.store, self.h.path
        draft = store.begin()
        draft.update('assignments', 'view-frame', enabled=False)
        saved = store.apply(draft)
        document = json.loads(path.read_text())
        for malformed in (None, 42, [], {**document, 'changes': []},
                          {**document, 'deleted_fields': None}):
            with self.subTest(malformed=type(malformed)):
                path.write_text(json.dumps(malformed))
                recovered = self.h.api.ProfileStore(self.base, path, lambda: self.h.settings, None)
                self.assertEqual(recovered.load_issue, 'invalid_profile_recovered_previous')
                self.assertEqual(recovered.snapshot(), saved)

        path.with_suffix('.previous.json').write_text('null')
        recovered = self.h.api.ProfileStore(self.base, path, lambda: self.h.settings, None)
        self.assertEqual(recovered.load_issue, 'invalid_profile_recovered_defaults')
        self.assertEqual(recovered.snapshot(), self.base)

    def test_shipped_release_snapshot_matches_authoring_catalog(self):
        root = Path(__file__).resolve().parents[1] / 'keymaps'
        self.assertEqual(self.h.api.deluxe_catalog.load(root / 'deluxe-defaults.json'),
                         self.h.api.deluxe_catalog.load(root / 'factory-defaults.json'))

    def test_new_publisher_ids_do_not_replace_personal_bindings_or_commands(self):
        personal, update = deepcopy(self.base), deepcopy(self.base)
        for catalog, key in ((personal, 'F11'), (update, 'F12')):
            catalog['events']['new-event'] = {'type': key}
            catalog['commands']['new-command'] = {'operator': 'wm.search_menu', 'properties': {}, 'label': key}
            catalog['assignments']['new-binding'] = dict(catalog['assignments']['view-frame'],
                feature='new-binding', event='new-event', command='new-command', order=100)
        decoded = self.api.decode_profile(update, self.api.encode_profile(self.base, personal))
        rows = decoded.catalog['assignments']
        self.assertIn('new-binding-personal', rows)
        self.assertEqual(decoded.catalog['events'][rows['new-binding']['event']]['type'], 'F12')
        self.assertEqual(decoded.catalog['events'][rows['new-binding-personal']['event']]['type'], 'F11')
        self.h.schema.validate_catalog(decoded.catalog)
        self.assertTrue(any('ID collision' in notice for notice in decoded.conflicts))

    def test_invalid_installed_catalog_does_not_destroy_a_personal_profile(self):
        root = self.h.path.parent
        (root / 'factory-defaults.json').write_text(json.dumps(self.base))
        catalog = root / 'deluxe-defaults.json'
        catalog.write_text('{invalid')
        personal = deepcopy(self.base)
        personal['assignments']['view-frame']['enabled'] = False
        self.h.path.write_text(json.dumps(self.api.encode_profile(self.base, personal)))
        before = self.h.path.read_bytes()
        store = self.h.api.ProfileStore.open_user(catalog, self.h.path, lambda: self.h.settings, lambda *args: None)
        self.assertEqual(store.load_issue, 'invalid_installed_catalog_using_factory')
        self.assertFalse(store.snapshot()['assignments']['view-frame']['enabled'])
        self.assertEqual(self.h.path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
