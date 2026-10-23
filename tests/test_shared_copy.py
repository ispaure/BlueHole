"""Deleted upstream modules must not survive the vendored compatibility check."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('shared_copy_check', ROOT / '.github/scripts/check_shared_copy.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class SharedCopyTests(unittest.TestCase):
    def test_exact_membership_bytes_and_stale_redirectors(self):
        with TemporaryDirectory() as directory:
            source, target = Path(directory) / 'source', Path(directory) / 'target'
            source.mkdir()
            target.mkdir()
            (source / 'owner.py').write_text('owner')
            (target / 'owner.py').write_text('owner')
            self.assertEqual(checker.compare_copy(source, target, ['owner.py'], ['owner.py']), [])
            (target / 'redirector.py').write_text('old redirector')
            self.assertEqual(checker.compare_copy(source, target, ['owner.py'], ['owner.py', 'redirector.py']), [('obsolete', 'redirector.py')])
            (target / 'owner.py').write_text('modified')
            self.assertEqual(checker.compare_copy(source, target, ['owner.py'], ['owner.py']), [('changed', 'owner.py')])
            self.assertEqual(checker.compare_copy(source, target, ['owner.py'], []), [('missing', 'owner.py')])
