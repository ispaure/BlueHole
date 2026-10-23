"""Verify exact vendored membership and bytes at a recorded shared revision."""
from pathlib import Path
import subprocess
import sys


def compare_copy(upstream, vendored, expected, actual):
    expected, actual = set(expected), set(actual)
    failures = [('missing', name) for name in sorted(expected - actual)]
    failures.extend(('obsolete', name) for name in sorted(actual - expected))
    for name in sorted(expected & actual):
        source, target = upstream / name, vendored / name
        if target.is_symlink() or any(parent.is_symlink() for parent in target.parents if parent == vendored or vendored in parent.parents):
            failures.append(('linked', name))
        elif not target.is_file() or target.read_bytes() != source.read_bytes():
            failures.append(('changed', name))
    return failures


def main(upstream, *, root=None):
    root = root or Path(__file__).resolve().parents[2]
    upstream = Path(upstream).resolve()
    expected_revision = (root / 'Lib/commonUtils.revision').read_text().strip()
    actual_revision = subprocess.check_output(['git', '-C', str(upstream), 'rev-parse', 'HEAD'], text=True).strip()
    if actual_revision != expected_revision:
        raise SystemExit(f'Wrong shared revision: {actual_revision}, expected {expected_revision}')
    names = subprocess.check_output(['git', '-C', str(upstream), 'ls-files', '-z']).decode().split('\0')
    expected = {name for name in names if name and not name.startswith('.github/')}
    prefix = 'Lib/commonUtils/'
    names = subprocess.check_output(['git', '-C', str(root), 'ls-files', '--cached', '--others', '--exclude-standard', '-z', '--', prefix]).decode().split('\0')
    actual = {name[len(prefix):] for name in names if name.startswith(prefix)}
    failures = compare_copy(upstream, root / 'Lib/commonUtils', expected, actual)
    if failures:
        raise SystemExit('Shared copy differs: ' + ', '.join(f'{kind}: {name}' for kind, name in failures))
    print('Vendored commonUtils matches', expected_revision)


if __name__ == '__main__':
    main(sys.argv[1])
