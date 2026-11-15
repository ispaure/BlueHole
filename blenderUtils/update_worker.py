"""Run with Blender's bundled Python, outside Blender's UI/interpreter."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import zipfile


def run(request):
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'Lib'))
    # Reuse commonUtils' bounded downloads and validated archive extraction.
    from commonUtils.runtime.updates.github import GitHubSource, json_get
    spec = importlib.util.spec_from_file_location('bluehole_update_service', root / 'blenderUtils/update_service.py')
    service = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(service)
    if request['action'] == 'check':
        release = service.latest(request['channel'], request['blender_version'], json_get)
        return {'release': release, 'check': service.check_release(request['installed_root'], release, json_get)}
    release = request['release']
    workspace = Path(request['workspace'])
    snapshot = GitHubSource(service.REPOSITORY).snapshot(release['commit'], workspace)
    info = service.validate_snapshot(snapshot, request['blender_version'])
    if '.'.join(map(str, info['version'])) != release['version']:
        raise ValueError('Downloaded addon version does not match the checked commit')
    # Match Logistics' normalized package digest so its next launch can retain
    # this installed copy instead of installing the same commit a second time.
    package = workspace / 'addon.zip'
    with zipfile.ZipFile(workspace / 'application.zip') as source, zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED) as output:
        for member in source.infolist():
            parts = Path(member.filename).parts[1:]
            if member.is_dir() or not parts:
                continue
            entry = zipfile.ZipInfo('BlueHole/' + '/'.join(parts))
            entry.external_attr = member.external_attr
            with source.open(member) as inp, output.open(entry, 'w') as out:
                shutil.copyfileobj(inp, out)
    with package.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    return {'release': {**release, 'package_digest': digest}}


if __name__ == '__main__':
    request_path, response_path = map(Path, sys.argv[1:])
    try:
        result = {'ok': True, **run(json.loads(request_path.read_text(encoding='utf-8')))}
    except Exception as error:
        result = {'ok': False, 'error': f'{type(error).__name__}: {error}'}
    response_path.write_text(json.dumps(result), encoding='utf-8')
