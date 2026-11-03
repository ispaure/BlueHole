"""Blue Hole policy for explicitly marked disposable package preparations."""
from pathlib import Path
import re

from build_manager.retention import delete_owned, linked, owned_entries, prune

ROOT = Path(__file__).resolve().parents[1]
MARKER = '.manager-build-output'


def group(root=ROOT):
    def eligible(path):
        marker = path / MARKER
        return bool(re.fullmatch('[0-9a-f]{32}', path.name)) and marker.is_file() and not linked(marker)
    return dict(root=Path(root) / 'test-results/release', eligible=eligible, lock_path=lambda p: p / 'operation.lock')


def clean(root=ROOT, *, apply=False):
    return prune(**group(root), age_days=7, max_bytes=4 * 1024 ** 3, grace_days=1/24, apply=apply)


def storage_inventory(root=ROOT):
    return [dict(row, group='Package preparations') for row in owned_entries(**group(root))]


def delete_storage(selections, root=ROOT):
    if set(selections) != {'Package preparations'}:
        raise ValueError('Choose declared Blue Hole package preparations.')
    return delete_owned(**group(root), names=selections['Package preparations'])


def enroll_preparation(output, root=ROOT):
    output = Path(output).absolute()
    parent = Path(root).absolute() / 'test-results/release'
    path = output.parent
    if path.parent != parent or not re.fullmatch('[0-9a-f]{32}', path.name):
        return
    if any(linked(p) for p in (path, *path.parents)) or linked(path / MARKER):
        raise ValueError('Package preparation refuses linked storage.')
    path.mkdir(parents=True, exist_ok=True)
    (path / MARKER).write_text('Disposable manager package preparation.\n')
