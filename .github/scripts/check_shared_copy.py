"""Verify exact vendored membership and bytes at a recorded shared revision."""
from pathlib import Path
import subprocess
import sys


def compare_copy(upstream, vendored, expected, actual, *, content_matches=None):
    expected, actual = set(expected), set(actual)
    failures = [('missing', name) for name in sorted(expected - actual)]
    failures.extend(('obsolete', name) for name in sorted(actual - expected))
    for name in sorted(expected & actual):
        source, target = upstream / name, vendored / name
        if target.is_symlink() or any(parent.is_symlink() for parent in target.parents if parent == vendored or vendored in parent.parents):
            failures.append(('linked', name))
        elif not target.is_file():
            failures.append(('changed', name))
        else:
            matches = (content_matches(name) if content_matches is not None
                       else target.read_bytes() == source.read_bytes())
            if not matches:
                failures.append(('changed', name))
    return failures


def main(upstream, *, root=None):
    root = root or Path(__file__).resolve().parents[2]
    upstream = Path(upstream).resolve()
    expected_revision = (root / 'Lib/commonUtils.revision').read_text().strip()
    actual_revision = subprocess.check_output(['git', '-C', str(upstream), 'rev-parse', 'HEAD'], text=True).strip()
    if actual_revision != expected_revision:
        raise SystemExit(f'Wrong shared revision: {actual_revision}, expected {expected_revision}')
    entries = subprocess.check_output(['git', '-C', str(upstream), 'ls-tree', '-r', '-z', 'HEAD']).decode().split('\0')
    expected = {}
    for entry in entries:
        if not entry:
            continue
        metadata, name = entry.split('\t', 1)
        mode, kind, object_id = metadata.split()
        if name.startswith('.github/'):
            continue
        if kind != 'blob' or mode not in {'100644', '100755'}:
            raise SystemExit(f'Shared source member is not a regular file: {name}')
        expected[name] = object_id
    prefix = 'Lib/commonUtils/'
    names = subprocess.check_output(['git', '-C', str(root), 'ls-files', '--cached', '--others', '--exclude-standard', '-z', '--', prefix]).decode().split('\0')
    actual = {name[len(prefix):] for name in names if name.startswith(prefix)}

    def content_matches(name):
        # Hash the consumer file using its tracked Git text/filter policy. This
        # accepts legitimate checkout line endings but still compares against
        # the pinned commit, never an unfinished upstream working-tree edit.
        actual_id = subprocess.check_output(
            ['git', '-C', str(root), 'hash-object', '--', prefix + name], text=True).strip()
        return actual_id == expected[name]

    failures = compare_copy(upstream, root / 'Lib/commonUtils', expected, actual,
                            content_matches=content_matches)
    if failures:
        raise SystemExit('Shared copy differs: ' + ', '.join(f'{kind}: {name}' for kind, name in failures))
    print('Vendored commonUtils matches', expected_revision)


if __name__ == '__main__':
    main(sys.argv[1])
