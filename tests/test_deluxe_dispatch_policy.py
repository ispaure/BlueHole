"""Reviewed shared events are invalidated by semantic edits, not UI toggles."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from keymaps.catalog_inventory import read_catalog
from keymaps.dispatch_policy import manifest, reviewed_groups


class DispatchPolicyTests(unittest.TestCase):
    def setUp(self):
        self.catalog, _ = read_catalog(Path(__file__).resolve().parents[1] / 'keymaps/deluxe-defaults.json')
        self.group, review = next(iter(manifest().items()))
        self.id = review['members'][0]['id']

    def test_every_shipped_chain_matches_its_independent_review_manifest(self):
        self.assertEqual(set(manifest()), reviewed_groups(self.catalog))

    def test_command_event_scope_and_relative_order_edits_revoke_exemption(self):
        for field in ('command', 'event', 'scope', 'order'):
            with self.subTest(field=field):
                catalog = deepcopy(self.catalog)
                row = catalog['assignments'][self.id]
                if field == 'command':
                    catalog['commands'][row['command']]['operator'] = 'wm.unrelated'
                elif field == 'event':
                    catalog['events'][row['event']]['type'] = 'F24'
                elif field == 'scope':
                    row['scope']['name'] = 'Window'
                else:
                    row['order'] = 1000000
                self.assertNotIn(self.group, reviewed_groups(catalog))

    def test_toggles_labels_and_unrelated_insertions_keep_reviewed_semantics(self):
        row = self.catalog['assignments'][self.id]
        row.update(enabled=False, active=False)
        self.catalog['commands'][row['command']]['label'] = 'Personal label'
        for definition in self.catalog['assignments'].values():
            definition['order'] += 10
        self.assertIn(self.group, reviewed_groups(self.catalog))


if __name__ == '__main__':
    unittest.main()
