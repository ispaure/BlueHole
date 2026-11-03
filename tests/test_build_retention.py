"""Blue Hole only retires marked preparation outputs under shared active locks."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import unittest
from build_manager.locking import workspace_lock
from build_manager.retention import durable_hold
from Scripts.build_retention import clean, enroll_preparation, storage_inventory, delete_storage, MARKER


class BuildRetentionTests(unittest.TestCase):
    def test_marked_preparations_keep_holds_pins_active_work_and_unknown_evidence(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve(); parent = root / 'test-results/release'
            for i in range(8):
                path = parent / (str(i) * 32)
                enroll_preparation(path / 'checks.json', root)
                os.utime(path, (i + 1, i + 1))
            unknown = parent / 'old-evidence'; unknown.mkdir()
            (parent / ('0' * 32) / '.keep').touch()
            os.utime(parent / ('0' * 32), (1, 1))
            durable_hold(parent / ('1' * 32), 'paused-fixture')
            with workspace_lock(parent / ('2' * 32) / 'operation.lock'):
                preview = clean(root)
                self.assertEqual(set(map(lambda p: Path(p).name, preview)), {'3' * 32, '4' * 32})
                self.assertEqual(clean(root, apply=True), preview)
            self.assertTrue(unknown.exists())
            self.assertFalse(any(row['name'] == 'old-evidence' for row in storage_inventory(root)))
            result = delete_storage({'Package preparations': ['1' * 32]}, root)
            self.assertFalse(result['removed'])
            self.assertTrue(result['skipped'])

    def test_enrollment_does_not_claim_arbitrary_or_linked_outputs(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve(); outside = root / 'evidence'; outside.mkdir()
            enroll_preparation(outside / 'checks.json', root)
            self.assertFalse((outside / MARKER).exists())
            parent = root / 'test-results/release'; parent.mkdir(parents=True)
            (parent / ('a' * 32)).symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                enroll_preparation(parent / ('a' * 32) / 'checks.json', root)
