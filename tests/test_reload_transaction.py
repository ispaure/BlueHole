"""No publication or second runtime before cleanup, including recovery."""
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from blenderUtils.reload_transaction import ReloadTransaction


class ReloadTests(unittest.TestCase):
    def setUp(self):
        self.events, self.clean, self.now = [], False, 0
        self.ready, self.fail_enable = (True, ''), False
        def enable():
            self.events.append('enable')
            if self.fail_enable:
                self.fail_enable, self.clean = False, False
                raise RuntimeError('injected registration failure')
        def disable():
            self.events.append('disable')
            return lambda: self.clean
        installation = SimpleNamespace(**{name: lambda name=name: self.events.append(name)
            for name in ('prepare', 'publish', 'rollback', 'finish')})
        self.session = ReloadTransaction(installation, disable=disable,
            purge=lambda: self.events.append('purge'), enable=enable,
            readiness=lambda: self.ready, complete=lambda recovered: self.events.append(('complete', recovered)),
            clock=lambda: self.now, timeout=2)

    def test_waits_for_cleanup_before_publication(self):
        self.session.begin()
        self.session.tick()
        self.assertEqual(self.events, ['prepare', 'disable'])
        self.clean = True
        self.session.tick()
        self.assertEqual(self.events, ['prepare', 'disable', 'publish', 'purge', 'enable', 'finish', ('complete', True)])

    def test_cleanup_timeout_does_not_start_another_runtime(self):
        self.session.begin()
        self.now = 3
        self.session.tick()
        self.assertEqual(self.events, ['prepare', 'disable', 'rollback', ('complete', False)])
        self.assertIn('cleanup timed out', self.session.error)
        self.assertIsNone(self.session.tick())

    def test_rollback_also_waits_for_failed_candidates_cleanup(self):
        self.clean = self.fail_enable = True
        self.session.begin()
        self.session.tick()
        self.assertEqual(self.events[-2:], ['enable', 'disable'])
        self.session.tick()
        self.assertNotIn('rollback', self.events)
        self.clean = True
        self.session.tick()
        self.assertEqual(self.events[-4:], ['rollback', 'purge', 'enable', ('complete', True)])
        self.assertIn('injected', self.session.error)

    def test_rollback_timeout_restores_files_without_loading_over_pending_ownership(self):
        self.clean = self.fail_enable = True
        self.session.begin()
        self.session.tick()
        self.now = 3
        self.session.tick()
        self.assertEqual(self.events.count('enable'), 1)
        self.assertEqual(self.events[-2:], ['rollback', ('complete', False)])


if __name__ == '__main__':
    unittest.main()
