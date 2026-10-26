"""Blue Hole-owned Blender 5.2.2 alpha checks, installable ZIP and release review."""
import argparse
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path,PurePosixPath
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
FILES={'__init__.py','LICENSE.md','url_database.ini'}
DIRECTORIES={'actions','blenderUtils','debug','environment','keymaps','operators','overlays',
             'preferences','ui','unrealUtils','wrappers','Lib','envFiles'}
EXCLUDE={'.git','.github','__pycache__','tests','test-results','.venv','docs','user_docs','.ruff_cache'}


def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args],text=True,timeout=60).strip()


def info():
    for node in ast.parse((ROOT/'__init__.py').read_text()).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='bl_info' for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError('Missing literal bl_info.')


def source_identity():
    metadata=info();branch=git('branch','--show-current')
    if branch!='blender-5.2.2/alpha' or tuple(metadata['blender'])!=(5,2,2):
        raise ValueError('This adapter is limited to the existing Blender 5.2.2 alpha branch.')
    names=git('ls-files','-c','-o','--exclude-standard','-z').split('\0')
    digest=hashlib.sha256()
    for name in sorted(set(names)):
        if not name:continue
        path=ROOT/name;digest.update(name.encode())
        if path.is_symlink():raise ValueError('Source symlinks are not accepted: '+name)
        digest.update(path.read_bytes() if path.is_file() else b'deleted')
    return dict(commit=git('rev-parse','HEAD'),branch=branch,dirty=bool(git('status','--porcelain')),
                fingerprint=digest.hexdigest(),addon_version='.'.join(map(str,metadata['version'])),
                blender_compatibility='.'.join(map(str,metadata['blender'])),
                commonUtils=(ROOT/'Lib/commonUtils.revision').read_text().strip())


def artifact_name():
    metadata=info()
    return 'BlueHole-'+'.'.join(map(str,metadata['version']))+'-blender5.2.2-alpha.zip'


def members():
    result=[]
    for name in git('ls-files','-c','-o','--exclude-standard','-z').split('\0'):
        if not name:continue
        path=PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts:raise ValueError('Unsafe archive path.')
        if any(part in EXCLUDE or part.endswith('.egg-info') for part in path.parts):continue
        if path.parts[0] not in DIRECTORIES and name not in FILES:continue
        if path.parts[0]=='envFiles' and path.parts[1:2]!=('default',):continue
        if path.name.startswith(('.env','._','secrets','service-account')) or path.name in {'.DS_Store','Thumbs.db','credentials.json'}:continue
        if path.suffix.lower() in {'.pyc','.pyo','.p8','.pem','.key','.p12','.pfx','.jks','.keystore'}:continue
        source=ROOT/name
        if source.is_symlink() or any(p.is_symlink() for p in source.parents if p!=ROOT and ROOT in p.parents):
            raise ValueError('Archive source must not contain links: '+name)
        if source.is_file():result.append(name)
    if not FILES.issubset(result) or 'Lib/commonUtils.revision' not in result:
        raise ValueError('Required add-on or shared identity files are missing.')
    allowed=json.loads((ROOT/'Scripts/package-files.json').read_text())
    if allowed.get('schema')!=1:raise ValueError('Unsupported package allowlist schema.')
    expected=set(allowed['members'])
    if set(result)!=expected:
        raise ValueError('Package source differs from its reviewed allowlist: '+str(sorted(set(result)^expected)))
    return sorted(expected)


def check_shared(upstream):
    if not upstream:raise ValueError('Configure BLUEHOLE_SHARED_SOURCE to an explicit commonUtils checkout for the pinned shared-copy check.')
    upstream=Path(upstream).expanduser().resolve()
    expected=(ROOT/'Lib/commonUtils.revision').read_text().strip()
    # Read the exact recorded commit without changing the operator's checkout.
    with tempfile.TemporaryDirectory(prefix='shared-check-',dir=storage()) as directory:
        clone=Path(directory)/'commonUtils'
        subprocess.run(['git','clone','--quiet','--shared','--no-checkout',str(upstream),str(clone)],check=True,timeout=60)
        subprocess.run(['git','-C',str(clone),'checkout','--quiet','--detach',expected],check=True,timeout=60)
        spec=importlib.util.spec_from_file_location('bluehole_shared_check',ROOT/'.github/scripts/check_shared_copy.py')
        checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
        checker.main(clone,root=ROOT)


def storage():
    path=ROOT/'test-results/release';path.mkdir(parents=True,exist_ok=True);return path


def checks(upstream=None, *, junit=None, pattern='test*.py'):
    before=source_identity()
    expected=os.environ.get('BLUEHOLE_MANAGER_SOURCE')
    if expected and json.loads(expected)!=before:raise ValueError('Source changed after manager planning; inspect a new plan.')
    import unittest
    from uuid import uuid4
    from build_manager.reporting import run_suite
    report = Path(junit) if junit else storage() / (uuid4().hex + '-portable.xml')
    class SharedCopy(unittest.TestCase):
        def test_pinned_shared_copy(self):
            check_shared(upstream or os.environ.get('BLUEHOLE_SHARED_SOURCE'))
    suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(SharedCopy),
                               unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern=pattern)])
    result = run_suite(suite, report, 'portable.contracts', fail_on_skip=True)
    if result['status'] != 'passed':raise ValueError('Blue Hole adapter prerequisites failed; inspect the JUnit report.')
    if source_identity()!=before:raise ValueError('Source changed during prerequisite checks.')
    return dict(result,source=before,python=sys.version,interpreter=sys.executable,scope='portable adapter tests and exact shared-copy check')


def package(destination,*,upstream=None,validation=None):
    before=source_identity()
    if validation is not None:
        if validation.get('status')!='passed' or validation.get('source')!=before or validation.get('python')!=sys.version or validation.get('interpreter')!=sys.executable:
            raise ValueError('Prerequisite evidence differs from this source or tooling environment.')
        evidence=validation
    else:evidence=checks(upstream)
    expected=os.environ.get('BLUEHOLE_MANAGER_SOURCE')
    if expected and json.loads(expected)!=before:raise ValueError('Source changed after manager planning; inspect a new plan.')
    destination=Path(destination)
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():raise ValueError('Package destination already exists; it will not be overwritten.')
    names=members();manifest={}
    try:
        with zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED) as archive:
            for name in names:
                payload=(ROOT/name).read_bytes();manifest[name]=hashlib.sha256(payload).hexdigest()
                entry=zipfile.ZipInfo('BlueHole/'+name,date_time=(2026,1,1,0,0,0))
                entry.external_attr=0o100644<<16;entry.compress_type=zipfile.ZIP_DEFLATED
                archive.writestr(entry,payload)
            metadata=dict(schema=1,source=before,members=manifest)
            entry=zipfile.ZipInfo('BlueHole/build-identity.json',date_time=(2026,1,1,0,0,0))
            entry.external_attr=0o100644<<16;entry.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(entry,json.dumps(metadata,sort_keys=True))
        if source_identity()!=before:raise ValueError('Source changed while packaging; inspect a new candidate.')
        with zipfile.ZipFile(destination) as archive:
            if archive.testzip() is not None:raise ValueError('ZIP validation failed.')
            for name,digest in manifest.items():
                if hashlib.sha256(archive.read('BlueHole/'+name)).hexdigest()!=digest:raise ValueError('ZIP member differs.')
        receipt=dict(schema=1,artifact=str(destination.resolve()),sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
                     source=before,checks=evidence,publishable=False,
                     status='development package' if before['dirty'] else 'package; native and hosted acceptance required')
        destination.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n')
        return receipt
    except BaseException:
        destination.unlink(missing_ok=True);raise


def release_tag(version,sequence):
    if not re.fullmatch(r'\d+\.\d+\.\d+',version) or not str(sequence).isdigit() or int(sequence)<1:
        raise ValueError('Choose a version and positive alpha sequence.')
    return f'bluehole-v{version}-blender5.2.2-alpha.{int(sequence)}'


def suggest_release_tag(source):
    prefix=release_tag(source['addon_version'],1).rsplit('.',1)[0]+'.'
    tags=subprocess.check_output(['git','tag','--list',prefix+'*'],cwd=ROOT,text=True,timeout=10).splitlines()
    numbers=[int(tag[len(prefix):]) for tag in tags if tag[len(prefix):].isdigit()]
    return prefix+str(max(numbers,default=0)+1)


def prepare(receipt,tag,*,native=None,hosted=None,inspection=None):
    source=source_identity()
    if source['dirty'] or receipt['source']!=source:raise ValueError('Release preparation requires exact clean committed source; development packages cannot be relabelled.')
    if not re.fullmatch(re.escape('bluehole-v'+source['addon_version']+'-blender5.2.2-alpha.')+r'[1-9]\d*',tag):
        raise ValueError('Select a matching alpha release tag.')
    collision=subprocess.run(['git','show-ref','--verify','--quiet','refs/tags/'+tag],cwd=ROOT)
    if collision.returncode==0:raise ValueError('Release tag already exists; never overwrite it.')
    if collision.returncode not in (0,1):raise ValueError('Could not inspect tag collision.')
    artifact=Path(receipt['artifact'])
    if not artifact.is_file() or hashlib.sha256(artifact.read_bytes()).hexdigest()!=receipt['sha256']:
        raise ValueError('Prepared artifact is missing or changed.')
    gates=[]
    for name,evidence in [('blender-5.2.2',native),('hosted-platforms',hosted)]:
        if not evidence or evidence.get('status')!='passed' or evidence.get('source')!=source:
            gates.append(name)
    if native and not str(native.get('runtime','')).startswith('Blender 5.2.2'):
        gates.append('supported-blender-runtime')
    if hosted and (hosted.get('platforms')!={'macos':'passed','linux':'passed','windows':'passed'} or not hosted.get('run_id')):
        gates.append('required-hosted-platforms')
    try:
        from Scripts.validation import release_acceptance
        release_acceptance(receipt.get('checks', {}), receipt, inspection or {}, native or {}, hosted,
                           expected_source=source)
    except (OSError, ValueError, KeyError, TypeError):
        gates.append('required-suite-inventory-and-exact-package-native-acceptance')
    return dict(schema=1,evidence=dict(native=native,hosted=hosted,portable=receipt.get('checks'),inspection=inspection),repository='ispaure/BlueHole',tag=tag,channel='alpha',prerelease=True,draft=True,
                source=source,artifact=receipt['artifact'],sha256=receipt['sha256'],
                publishable=not gates,blocked_gates=gates,effect='prepare only; no network or tag mutation',
                future_channels={'beta':'not implemented','stable':'not implemented'})


def verify_candidate(candidate):
    if not candidate.get("publishable") or candidate.get("blocked_gates"):
        raise ValueError("Reviewed native/hosted suite gates are required.")
    if candidate['source']!=source_identity() or candidate['source']['dirty']:
        raise ValueError('Candidate source identity changed.')
    if candidate.get('repository')!='ispaure/BlueHole' or not re.fullmatch(re.escape('bluehole-v'+candidate['source']['addon_version']+'-blender5.2.2-alpha.')+r'[1-9]\d*',candidate.get('tag','')):
        raise ValueError('Candidate destination or alpha tag differs from project policy.')
    artifact=Path(candidate['artifact'])
    with zipfile.ZipFile(artifact) as archive:
        embedded=json.loads(archive.read('BlueHole/build-identity.json'))
        if embedded['source']!=candidate['source']:raise ValueError('Embedded source differs; development archives cannot be relabelled.')
    evidence=candidate.get('evidence',{})
    native=evidence.get('native') or {};hosted=evidence.get('hosted') or {}
    if (native.get('source')!=candidate['source'] or native.get('status')!='passed'
            or not str(native.get('runtime','')).startswith('Blender 5.2.2')
            or hosted.get('source')!=candidate['source'] or hosted.get('status')!='passed'
            or hosted.get('platforms')!={'macos':'passed','linux':'passed','windows':'passed'} or not hosted.get('run_id')):
        raise ValueError('Native and hosted acceptance evidence is missing or incompatible.')
    from Scripts.validation import release_acceptance
    release_acceptance(evidence.get('portable', {}), candidate, evidence.get('inspection', {}), native, hosted,
                       expected_source=candidate['source'])
    if hashlib.sha256(artifact.read_bytes()).hexdigest()!=candidate['sha256']:raise ValueError('Artifact checksum changed.')


class ReleaseTransport:
    """Injected GitHub transport; exact receipts and reconciliation precede effects."""
    def __init__(self,client):self.client=client

    def publish_draft(self,candidate,*,confirmed=False):
        if not confirmed or not candidate.get('publishable') or candidate.get('blocked_gates'):
            raise ValueError('Reviewed native/hosted gates and explicit operator confirmation are required.')
        verify_candidate(candidate)
        # Client reconciles exact tag/SHA/checksum. Existing unrelated state is never overwritten.
        existing=self.client.reconcile(candidate)
        if existing is not None:return existing
        return self.client.create_draft(candidate)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['check','package','prepare'])
    parser.add_argument('--shared-source',type=Path)
    parser.add_argument('--output',type=Path);parser.add_argument('--receipt',type=Path);parser.add_argument('--tag');parser.add_argument('--checks',type=Path)
    parser.add_argument('--native', type=Path);parser.add_argument('--hosted', type=Path);parser.add_argument('--inspection', type=Path)
    args=parser.parse_args()
    if args.action=='check':result=checks(args.shared_source)
    elif args.action=='package':
        if not args.output:parser.error('--output is required')
        result=package(args.output,upstream=args.shared_source,validation=json.loads(args.checks.read_text()) if args.checks else None)
    else:
        if not args.receipt or not args.tag:parser.error('--receipt and --tag are required')
        result=prepare(json.loads(args.receipt.read_text()),args.tag,
            native=json.loads(args.native.read_text()) if args.native else None,
            hosted=json.loads(args.hosted.read_text()) if args.hosted else None,
            inspection=json.loads(args.inspection.read_text()) if args.inspection else None)
    if args.output and args.action!='package':
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));return 0


if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as error:
        print(str(error),file=sys.stderr);raise SystemExit(1)
