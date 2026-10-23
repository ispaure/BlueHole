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

    def test_linked_members_and_parent_directories_are_rejected(self):
        with TemporaryDirectory() as directory:
            source, target, outside = (Path(directory) / name for name in ('source', 'target', 'outside'))
            for path in (source, target, outside):
                path.mkdir()
            (source / 'owner.py').write_text('owner')
            (outside / 'owner.py').write_text('owner')
            (target / 'owner.py').symlink_to(outside / 'owner.py')
            self.assertEqual(checker.compare_copy(source, target, ['owner.py'], ['owner.py']), [('linked', 'owner.py')])
            (target / 'owner.py').unlink()
            (source / 'nested').mkdir()
            (source / 'nested/owner.py').write_text('owner')
            (target / 'nested').symlink_to(outside, target_is_directory=True)
            self.assertEqual(checker.compare_copy(source, target, ['nested/owner.py'], ['nested/owner.py']), [('linked', 'nested/owner.py')])

    def test_committed_copy_accepts_checkout_line_endings_and_ignores_dirty_upstream(self):
        from contextlib import redirect_stdout
        import io
        import subprocess
        with TemporaryDirectory() as directory:
            root, source = Path(directory) / 'consumer', Path(directory) / 'shared'
            for repo in (root, source):
                repo.mkdir()
                subprocess.run(['git', '-C', str(repo), 'init', '--quiet'], check=True)
                subprocess.run(['git', '-C', str(repo), 'config', 'core.autocrlf', 'false'], check=True)
            (source / '.gitattributes').write_text('*.txt text eol=lf\n')
            (source / 'owner.txt').write_bytes(b'owner\n')
            subprocess.run(['git', '-C', str(source), 'add', '.'], check=True)
            hooks = Path(directory) / 'disabled-hooks'
            hooks.mkdir()
            subprocess.run(['git', '-C', str(source), '-c', 'user.name=Fixture',
                '-c', 'user.email=fixture@example.invalid', '-c', 'commit.gpgsign=false',
                '-c', 'core.hooksPath=' + str(hooks), 'commit', '--quiet', '-m', 'fixture'], check=True)
            revision = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
            vendor = root / 'Lib/commonUtils'
            vendor.mkdir(parents=True)
            (root / 'Lib/commonUtils.revision').write_text(revision + '\n')
            (vendor / '.gitattributes').write_bytes((source / '.gitattributes').read_bytes())
            (vendor / 'owner.txt').write_bytes(b'owner\r\n')
            with redirect_stdout(io.StringIO()):
                checker.main(source, root=root)
                (source / 'owner.txt').write_text('unfinished upstream edit\n')
                checker.main(source, root=root)
            (vendor / 'owner.txt').write_bytes(b'changed\r\n')
            with self.assertRaisesRegex(SystemExit, 'changed: owner.txt'):
                checker.main(source, root=root)
