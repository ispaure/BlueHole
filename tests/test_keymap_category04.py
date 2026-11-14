"""Bulk reconciliation of the Object, Mesh and UV catalog."""

import json
from pathlib import Path
import unittest



ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures'
BASELINE = FIXTURES / 'deluxe_keymaps'


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


class Category04CatalogTest(unittest.TestCase):
    def test_historical_catalog_reconciliation_coverage(self):
        receipt = json.loads((FIXTURES / 'deluxe_keymaps_category04/bulk-catalog.json').read_text())
        ledger = {r['row_id']: r for r in read_jsonl(BASELINE / 'reconciliation-ledger.jsonl')}
        transfers = {r['row_id'] for r in read_jsonl(
            FIXTURES / 'deluxe_keymaps_category03/reconciliation.jsonl')
            if r.get('authorized_transfer', {}).get('to_category') == '04'}
        self.assertEqual(set(receipt['transfers']), transfers)
        assigned = {id_ for id_, r in ledger.items() if r['owner'] == '04'} | transfers
        self.assertEqual(len(assigned), 310)

        def count(id_, capture):
            return ledger[id_]['presence'].get(capture, {}).get('user', 0)

        candidates = {id_ for id_ in assigned
                      if count(id_, 'full') > max(count(id_, 'stock'), count(id_, 'neither'))}
        declarations = {r['row_id']: r for r in receipt['declarations']}
        exceptions = {r['row_id'] for rows in receipt['exceptions'].values() for r in rows}
        self.assertEqual(len(declarations), len(receipt['declarations']))
        self.assertEqual(len(exceptions), sum(map(len, receipt['exceptions'].values())))
        self.assertFalse(declarations.keys() & exceptions)
        self.assertEqual(candidates, declarations.keys() | exceptions)
        self.assertLessEqual(transfers, declarations.keys())


if __name__ == '__main__':
    unittest.main()
