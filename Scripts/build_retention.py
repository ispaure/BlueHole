"""Blue Hole policy for explicitly marked disposable package preparations."""
from pathlib import Path
import re

from build_manager.retention import delete_owned, linked, owned_entries, prune

ROOT = Path(__file__).resolve().parents[1]
MARKER = '.manager-build-output'
CHECK_RESULTS = Path('tmp/test-results/checks')
PREPARATIONS = {'Package preparations': Path('test-results/release'),
                'Test preparations': CHECK_RESULTS}


def group(root=ROOT, directory=PREPARATIONS['Package preparations']):
    def eligible(path):
        marker = path / MARKER
        return bool(re.fullmatch('[0-9a-f]{32}', path.name)) and marker.is_file() and not linked(marker)
    return dict(root=Path(root) / directory, eligible=eligible, lock_path=lambda p: p / 'operation.lock', ownership_files=(MARKER,))


def clean(root=ROOT, *, apply=False):
    return [path for directory in PREPARATIONS.values()
            for path in prune(**group(root, directory), age_days=7,
                              max_bytes=4 * 1024 ** 3, grace_days=1/24, apply=apply)]


def storage_inventory(root=ROOT):
    return [dict(row, group=name) for name, directory in PREPARATIONS.items()
            for row in owned_entries(**group(root, directory))]


def delete_storage(selections, root=ROOT):
    if not selections or set(selections) - PREPARATIONS.keys():
        raise ValueError('Choose declared Blue Hole test or package preparations.')
    result = dict(removed=[], skipped=[])
    for name, names in selections.items():
        outcome = delete_owned(**group(root, PREPARATIONS[name]), names=names)
        for key in result:
            result[key].extend(outcome[key])
    return result


def enroll_preparation(output, root=ROOT):
    output = Path(output).absolute()
    root = Path(root).absolute()
    path = output.parent
    if path.parent not in {root / directory for directory in PREPARATIONS.values()} or not re.fullmatch('[0-9a-f]{32}', path.name):
        return
    if any(linked(p) for p in (path, *path.parents)) or linked(path / MARKER):
        raise ValueError('Package preparation refuses linked storage.')
    path.mkdir(parents=True, exist_ok=True)
    (path / MARKER).write_text('Disposable manager preparation.\n')
