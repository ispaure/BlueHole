"""Capture and benchmark a disposable Logistics preset copy.

Requires macOS sandbox-exec for confinement of third-party provider code. Pass
--blender, --preset and --output explicitly. --reference-ref optionally captures
a historical Blue Hole checkout and its packaged Deluxe preference artifacts.
The source preset is never launched or modified. No extra Blender libraries.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory
import time

from blender_keymap_runtime import REPO, stage_package


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def launch(args):
    if sys.platform != 'darwin' or not Path('/usr/bin/sandbox-exec').is_file():
        raise ValueError('Provider-preset capture requires macOS sandbox-exec; use factory native tests on other platforms')
    output, source = args.output.resolve(), args.preset.resolve()
    if output == source or output.is_relative_to(source):
        raise ValueError('Evidence directory must be outside the source preset')
    output.mkdir(parents=True, exist_ok=True)
    protected = [source / 'config/userpref.blend', source / '.logistics-addons.json']
    before = {str(path): file_hash(path) for path in protected}
    receipt = {'source_hashes': before, 'source_commit': subprocess.check_output(
        ['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip(), 'runs': []}
    receipt['source_dirty'] = bool(subprocess.check_output(['git', '-C', str(REPO), 'status', '--porcelain']))
    variants = ['current', 'legacy'] if args.reference_ref else ['current']
    try:
        for variant in variants:
            with TemporaryDirectory(prefix=variant + '-', dir=output) as temporary:
                root = Path(temporary)
                def ignore(_path, names):
                    return [name for name in names if name in {'BlueHole', '__pycache__', '.DS_Store'} or name.endswith('.log')]
                for name in ('scripts', 'extensions', 'datafiles', 'addon-data'):
                    if (source / name).exists():
                        shutil.copytree(source / name, root / name, ignore=ignore)
                (root / 'config').mkdir()
                shutil.copyfile(protected[0], root / 'config/userpref.blend')
                shutil.copyfile(protected[1], root / 'manifest.json')
                if variant == 'current':
                    stage_package(root, None)
                    (root / 'scripts/addons/bluehole_runtime').rename(root / 'scripts/addons/BlueHole')
                else:
                    commit = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', '--verify', args.reference_ref + '^{commit}'], text=True).strip()
                    receipt['reference_commit'] = commit
                    package = root / 'scripts/addons/BlueHole'
                    package.mkdir(parents=True)
                    data = subprocess.check_output(['git', '-C', str(REPO), 'archive', commit])
                    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
                        archive.extractall(package, filter='data')
                    payload = package / 'overlays/deluxe/payload'
                    shutil.copyfile(payload / 'userpref.blend', root / 'config/userpref.blend')
                    preset = root / 'scripts/presets/keyconfig/BH_Keymaps.py'
                    preset.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(payload / 'keyconfig/BH_Keymaps.py', preset)
                    receipt['reference_payloads'] = {name: file_hash(payload / name) for name in ('userpref.blend', 'keyconfig/BH_Keymaps.py')}
                env = dict(os.environ, BH_AUDIT_ROOT=str(root), BH_AUDIT_OUT=str(output),
                           BH_AUDIT_VARIANT=variant, BH_SOURCE_PROFILE=str(source),
                           BH_AUDIT_SAMPLES=str(args.samples), PYTHONDONTWRITEBYTECODE='1',
                           PYTHONNOUSERSITE='1', PYTHONUNBUFFERED='1', BLENDER_USER_RESOURCES=str(root))
                env.pop('PYTHONPATH', None)
                for table in ('assignment', 'suppression'):
                    if getattr(args, table):
                        env['BH_AUDIT_' + table.upper()] = getattr(args, table)
                for name in ('CONFIG', 'SCRIPTS', 'EXTENSIONS', 'DATAFILES'):
                    folder = root / name.lower()
                    folder.mkdir(exist_ok=True)
                    env['BLENDER_USER_' + name] = str(folder)
                for name, folder in (('TMPDIR', 'tmp'), ('XDG_CACHE_HOME', 'cache')):
                    (root / folder).mkdir()
                    env[name] = str(root / folder)
                policy = root / 'sandbox.sb'
                policy.write_text('(version 1)\n(allow default)\n(deny network*)\n(deny file-write*)\n'
                                  '(allow file-write* (subpath ' + json.dumps(str(output)) + '))\n'
                                  '(allow file-write* (literal "/dev/null"))\n')
                status = output / (variant + '-status.json')
                status.unlink(missing_ok=True)
                start = time.monotonic()
                with (output / (variant + '.log')).open('w') as log:
                    child = subprocess.Popen(['/usr/bin/sandbox-exec', '-f', str(policy), str(args.blender),
                        '--factory-startup', '--disable-autoexec', '--offline-mode', '--python-exit-code', '1',
                        '--python', str(Path(__file__).with_name('blender_keymap_preset_probe.py'))],
                        env=env, stdout=log, stderr=subprocess.STDOUT)
                    try:
                        code = child.wait(timeout=args.timeout)
                    except subprocess.TimeoutExpired:
                        child.kill()
                        child.wait()
                        raise
                report = json.loads(status.read_text()) if status.exists() else {}
                receipt['runs'].append({'variant': variant, 'returncode': code,
                                        'seconds': round(time.monotonic() - start, 3),
                                        'status': report.get('status'), 'fatal': report.get('fatal')})
                if code or report.get('status') != 'complete' or report.get('fatal'):
                    raise RuntimeError(f'{variant} capture failed; see {status}')
    finally:
        receipt['source_preserved'] = before == {str(path): file_hash(path) for path in protected}
        receipt['temporary_copies_removed'] = not any(output.glob('current-*/')) and not any(output.glob('legacy-*/'))
        (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    if not receipt['source_preserved']:
        raise RuntimeError('Source preset hashes changed during capture')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blender', type=Path, required=True)
    parser.add_argument('--preset', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reference-ref')
    parser.add_argument('--assignment', help='Specific added binding to benchmark')
    parser.add_argument('--suppression', help='Specific removal rule to benchmark')
    parser.add_argument('--samples', type=int, default=20)
    parser.add_argument('--timeout', type=int, default=240)
    args = parser.parse_args()
    if args.samples < 2 or args.samples % 2:
        parser.error('--samples must be an even number of at least two')
    launch(args)
