"""Temporary stock adjustments retain ownership through unreadable RNA."""
from unittest.mock import patch
import unittest
import test_deluxe_profiles
from runtime_keymap_fakes import row


class StockCleanupTests(unittest.TestCase):
    def setUp(self):
        self.h = test_deluxe_profiles.ProfileTests()
        self.h.setUp()
        self.addCleanup(self.h.doCleanups)
        self.core = self.h.core
        self.service = self.h.store.registration
        self.map = self.h.runtime.map('default', 'Object Mode')
        self.item = self.map.keymap_items.append_fixture(row('wm.call_menu', key='A', shift=True,
            value='RELEASE', prop_values={'name': 'VIEW3D_MT_add'}))
        self.target = self.core.KeymapTarget('wm.call_menu', {'name': 'VIEW3D_MT_add'})
        self.service._stock_add_rows.append((self.map, self.item, self.item.id, self.target))

    def test_unreadable_snapshot_is_retried_then_restored(self):
        with patch.object(self.core, 'snapshot_item', side_effect=self.core.Pending('unreadable')):
            self.assertFalse(self.service.restore_stock_add())
        self.assertTrue(self.service.stock_cleanup_pending)
        self.assertEqual(self.item.value, 'RELEASE')
        self.assertTrue(self.service.restore_stock_add())
        self.assertFalse(self.service.stock_cleanup_pending)
        self.assertEqual(self.item.value, 'PRESS')

    def test_native_user_edit_is_never_overwritten(self):
        self.item.type = 'B'
        self.assertTrue(self.service.restore_stock_add())
        self.assertEqual(self.item.value, 'RELEASE')
        self.assertFalse(self.service._stock_add_rows)

    def test_replaced_configuration_relinquishes_old_identity(self):
        self.h.runtime.replace_config('default')
        self.assertTrue(self.service.restore_stock_add())
        self.assertFalse(self.service._stock_add_rows)
