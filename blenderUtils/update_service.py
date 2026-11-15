"""Blender-independent update selection and reversible addon publication."""
import ast
import base64
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import quote

REPOSITORY = 'ispaure/BlueHole'
CHANNELS = ('main', 'beta', 'alpha')
VERSION_BRANCH = re.compile(r'blender-(\d+\.\d+\.\d+)/(main|beta|alpha)')
COMMIT = re.compile(r'[a-f0-9]{40}')
MARKER = '.bluehole-update.json'


def version_tuple(value):
    return tuple(map(int, value.split('.'))) if isinstance(value, str) else tuple(value)


def select_branch(names, channel, blender_version):
    """Match Logistics: highest supported baseline within the chosen channel."""
    if channel not in CHANNELS:
        raise ValueError('Choose Main, Beta or Alpha')
    choices = [(version_tuple(match[1]), name) for name in names
               if (match := VERSION_BRANCH.fullmatch(name)) and match[2] == channel
               and version_tuple(match[1]) <= version_tuple(blender_version)]
    if choices:
        return max(choices)[1]
    if channel in names:
        return channel
    raise ValueError(f'No Blue Hole {channel} branch supports Blender {".".join(map(str, blender_version))}')


def addon_info(source, blender_version):
    tree = ast.parse(source)
    info = next((ast.literal_eval(node.value) for node in tree.body
                 if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'bl_info'
                                                        for t in node.targets)), None)
    if not isinstance(info, dict) or info.get('name') != 'Blue Hole':
        raise ValueError('The update is not a Blue Hole addon')
    if not info.get('blender') or version_tuple(info['blender']) > version_tuple(blender_version):
        raise ValueError('This Blue Hole update requires a newer Blender version')
    return info


def latest(channel, blender_version, json_get):
    names = []
    base = f'https://api.github.com/repos/{REPOSITORY}'
    for page in range(1, 21):
        records = json_get(f'{base}/branches?per_page=100&page={page}')
        if not isinstance(records, list) or any(not isinstance(r, dict) or not isinstance(r.get('name'), str) for r in records):
            raise ValueError('GitHub returned invalid branch metadata')
        names.extend(r['name'] for r in records)
        if len(records) < 100:
            break
    else:
        raise ValueError('Blue Hole branch catalog exceeds the size limit')
    branch = select_branch(names, channel, blender_version)
    commit = json_get(f'{base}/branches/{quote(branch, safe="")}')['commit']['sha']
    if not isinstance(commit, str) or not COMMIT.fullmatch(commit):
        raise ValueError('GitHub returned an invalid commit')
    entry = json_get(f'{base}/contents/__init__.py?ref={commit}')
    if entry.get('encoding') != 'base64':
        raise ValueError('GitHub returned invalid addon metadata')
    info = addon_info(base64.b64decode(entry['content']), blender_version)
    return {'repository': REPOSITORY, 'branch': branch, 'commit': commit,
            'version': '.'.join(map(str, info['version'])), 'channel': channel}


def logistics_manifest(root):
    """Only recognize a manifest that explicitly owns this installed directory."""
    root = Path(root).absolute()
    path = root.parent.parent.parent / '.logistics-addons.json'
    if not path.is_file() or path.is_symlink():
        return None
    state = json.loads(path.read_text(encoding='utf-8'))
    entry = state.get('installed', {}).get('legacy:BlueHole', {})
    if path.parent / entry.get('path', '') != root:
        return None
    return path, state


def install_blocker(root):
    root = Path(root).absolute()
    if root.is_symlink() or root.resolve() != root:
        return 'Local checkout/link: update its source through Git or Logistics.'
    if any((parent / '.git').exists() for parent in (root, *root.parents)):
        return 'Development checkout: update its source through Git or Logistics.'
    managed = logistics_manifest(root)
    if managed and managed[1].get('bluehole', {}).get('source') == 'local':
        return 'Local checkout: update its source through Git or Logistics.'
    return ''


def installed_commit(root):
    checkout = Path(root).resolve()
    if (checkout / '.git').exists():
        # A linked development preset has no installation marker. Its checkout
        # is authoritative, including worktrees and detached HEADs. Run this in
        # the update worker so a slow Git executable never stalls Blender's UI.
        try:
            result = subprocess.run(['git', '-C', str(checkout), 'rev-parse', '--verify', 'HEAD'],
                                    capture_output=True, text=True, timeout=10, check=True,
                                    env={k: v for k, v in os.environ.items() if not k.startswith('GIT_')},
                                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            commit = result.stdout.strip()
            return commit if COMMIT.fullmatch(commit) else ''
        except (OSError, subprocess.SubprocessError):
            return ''
    marker = Path(root) / MARKER
    if marker.is_file() and not marker.is_symlink():
        record = json.loads(marker.read_text(encoding='utf-8'))
    else:
        managed = logistics_manifest(root)
        record = (managed[1].get('installed_bluehole') or managed[1].get('bluehole', {})) if managed else {}
    commit = record.get('commit')
    return commit if isinstance(commit, str) and COMMIT.fullmatch(commit) else ''


def check_release(root, release, json_get):
    """Only advertise an update when the selected branch is actually newer."""
    current = installed_commit(root)
    status = 'unverified'
    message = 'Installed revision is unknown; the latest selected channel can be installed manually.'
    if current == release['commit']:
        status, message = 'current', ''
    elif current:
        try:
            comparison = json_get(f'https://api.github.com/repos/{REPOSITORY}/compare/{current}...{release["commit"]}')
            status, message = {
                'identical': ('current', ''),
                'ahead': ('available', ''),
                'behind': ('ahead', 'Your installed revision is ahead of the selected channel.'),
                'diverged': ('different', 'Your installed revision and the selected channel have different changes.'),
            }[comparison['status']]
        except Exception:
            # An unpublished checkout or unavailable comparison is not evidence
            # that a newer update exists. Keep manual channel installation usable.
            message = 'Could not compare the installed revision with the selected channel.'
    return dict(status=status, message=message, installed_commit=current, blocked=install_blocker(root))


def validate_snapshot(root, blender_version):
    info = addon_info((root / '__init__.py').read_bytes(), blender_version)
    for name in ('Lib/commonUtils/__init__.py', 'operators/operators_register.py',
                 'preferences/addon_prefs.py', 'envFiles/default'):
        if not (root / name).exists():
            raise ValueError(f'Incomplete Blue Hole update: {name}')
    return info


def preserve_environments(previous, staged):
    """Same ownership as Logistics: custom environments win, default is shipped."""
    source, target = previous / 'envFiles', staged / 'envFiles'
    if source.is_symlink() or target.is_symlink():
        raise ValueError('Blue Hole envFiles must be a real directory')
    if not source.is_dir():
        return
    target.mkdir(exist_ok=True)
    for entry in source.iterdir():
        if entry.name.casefold() == 'default':
            continue
        destination = target / entry.name
        if destination.is_symlink() or destination.is_file():
            destination.unlink()
        elif destination.is_dir():
            shutil.rmtree(destination)
        if entry.is_symlink():
            destination.symlink_to(entry.readlink(), target_is_directory=entry.is_dir())
        elif entry.is_dir():
            shutil.copytree(entry, destination, symlinks=True)
        else:
            shutil.copy2(entry, destination)


def atomic_json(path, value):
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile(dir=path.parent, prefix='.' + path.name, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(json.dumps(value, indent=2).encode('utf-8'))
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


class Installation:
    """Hold the old folder and Logistics lock until the new addon is live."""
    def __init__(self, root, staged, release, blender_version):
        self.root, self.staged = Path(root).absolute(), Path(staged)
        self.release = release
        self.backup = self.staged.parent / 'previous'
        self.failed = self.staged.parent / 'failed'
        self.published = False
        self.lock = None
        self.managed = None
        blocker = install_blocker(self.root)
        if blocker:
            raise ValueError(blocker)
        validate_snapshot(self.staged, blender_version)
        if release.get('repository') != REPOSITORY or not COMMIT.fullmatch(release.get('commit', '')):
            raise ValueError('Invalid update identity')

    def prepare(self):
        self.managed = logistics_manifest(self.root)
        lock_root = self.managed[0].parent if self.managed else self.root
        self.lock = lock_root.with_name('.' + lock_root.name + '.lock')
        try:
            self.lock.mkdir()
        except FileExistsError:
            self.lock = None
            raise ValueError('Another update owns this installation; try again when it finishes') from None
        try:
            preserve_environments(self.root, self.staged)
            atomic_json(self.staged / MARKER, self.release)
        except Exception:
            self.unlock()
            raise

    def publish(self):
        os.replace(self.root, self.backup)
        try:
            os.replace(self.staged, self.root)
        except Exception:
            os.replace(self.backup, self.root)
            raise
        self.published = True

    def finish(self):
        if self.managed:
            path, state = self.managed
            # Do not overwrite a concurrently edited preset manifest.
            if json.loads(path.read_text(encoding='utf-8')) != state:
                raise ValueError('The Logistics preset changed during the update')
            release = self.release
            state['installed_bluehole'] = {k: release[k] for k in ('branch', 'commit', 'version')}
            state['bluehole'].update(branch=release['channel'], commit=release['commit'])
            entry = state['installed']['legacy:BlueHole']
            entry.update(version=release['version'], source='GitHub · ' + release['branch'])
            if release.get('package_digest'):
                entry['digest'] = release['package_digest']
            atomic_json(path, state)
        self.unlock()

    def rollback(self):
        if self.published:
            os.replace(self.root, self.failed)
            os.replace(self.backup, self.root)
            self.published = False
        self.unlock()

    def unlock(self):
        if self.lock is not None:
            self.lock.rmdir()
            self.lock = None
