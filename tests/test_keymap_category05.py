"""Bulk structural comparison of the remaining Deluxe keymaps."""

import json
import unittest

from test_keymap_category04 import BASELINE, FIXTURES, read_jsonl


class Category05CatalogTest(unittest.TestCase):

    def test_historical_catalog_reconciliation_coverage(self):
        receipt = json.loads((FIXTURES / 'deluxe_keymaps_category05/bulk-catalog.json').read_text())
        ledger = {r['row_id']: r for r in read_jsonl(BASELINE / 'reconciliation-ledger.jsonl')
                  if r['owner'] == '05'}
        self.assertEqual(len(ledger), 3175)

        def count(id_, capture):
            return ledger[id_]['presence'].get(capture, {}).get('user', 0)

        candidates = {id_ for id_ in ledger
                      if count(id_, 'full') > max(count(id_, 'stock'), count(id_, 'neither'))}
        catalog = receipt['catalog']
        exceptions = receipt['exceptions']
        existing = {id_ for id_, entry in catalog.items() if entry[-1] in ('existing', 'defaults')}
        self.assertEqual(existing, {id_ for id_, r in ledger.items()
                                   if count(id_, 'full')
                                   and r['runtime_coverage']['reference_bluehole_owned']})
        self.assertEqual(candidates, (catalog.keys() - existing) | exceptions.keys())
        self.assertFalse(catalog.keys() & exceptions.keys())
        self.assertEqual(receipt['stock_reductions'], {
            id_: count(id_, 'stock') - count(id_, 'full') for id_ in ledger
            if count(id_, 'stock') > count(id_, 'full')
        })
        self.assertEqual(set(receipt['absent_in_full_and_stock']), {
            id_ for id_ in ledger if not count(id_, 'full') and not count(id_, 'stock')
        })
        self.assertEqual(set(receipt['blue_hole_pies_absent_in_full']), {
            id_ for id_ in receipt['absent_in_full_and_stock']
            if ledger[id_]['runtime_coverage']['reference_bluehole_owned']
        })


if __name__ == '__main__':
    unittest.main()
