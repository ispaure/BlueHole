"""Evidence must identify source bytes and preserve ordering/duplicate changes."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from keymaps.catalog_inventory import inventory, read_catalog
from Scripts.keymap_compare import compare


class InventoryTests(unittest.TestCase):
    def test_inventory_identifies_every_catalog_source_and_chain_member(self):
        catalog, sources = read_catalog(ROOT / 'keymaps/deluxe-defaults.json')
        report = inventory(catalog, sources)
        self.assertEqual(report, inventory(deepcopy(catalog), dict(reversed(list(sources.items())))))
        self.assertEqual(len(sources), len(catalog['categories']) + 1)
        self.assertEqual(sum(len(rows) for rows in report['dispatch_chains'].values()),
                         sum(bool(row.get('dispatch_group')) for row in catalog['assignments'].values()))
        id_ = next(iter(catalog['assignments']))
        catalog['assignments'][id_]['enabled'] = False
        self.assertNotEqual(inventory(catalog)['catalog_digest'], report['catalog_digest'])

    def test_comparison_retains_duplicates_order_and_read_issues(self):
        first = dict(target='wm.first', event={'type': 'A'}, properties={}, active=True, read_issues={})
        second = dict(first, target='wm.second')
        def snapshot(items):
            return {'roles': {'user': {'maps': [{'scope': {'name': 'Window'}, 'items': items}]}}}
        result = compare(snapshot([first, second]), snapshot([second, first]))
        self.assertTrue(result['multiset_equal'])
        self.assertFalse(result['ordered_equal'])
        result = compare(snapshot([first, first]), snapshot([first]))
        self.assertEqual(result['removed'][0]['count'], 1)
        result = compare(snapshot([first]), snapshot([dict(first, read_issues={'name': 'unreadable'})]))
        self.assertFalse(result['multiset_equal'])


if __name__ == '__main__':
    unittest.main()
