"""Project-owned suite execution and exact-package Blender release acceptance."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build_manager.reporting import run_suite, write_junit, test_ids
from build_manager.test_results import read_junit


def suite_selection(suite, operation, target, pattern=''):
    if target != 'blender':
        raise ValueError('Unsupported Blue Hole target.')
    if suite:
        rows = json.loads((ROOT / 'build-project.json').read_text())['test_suites']
        if not any(row['id'] == suite and target in row['platforms'] and operation in row['operations'] for row in rows):
            raise ValueError('Unsupported Blue Hole test suite for this operation.')
    if pattern and (operation != 'Check' or suite not in {'', 'portable.contracts'}
                    or not pattern.endswith('.py') or '/' in pattern or '\\' in pattern):
        raise ValueError('Focused filename patterns apply only to portable Check; release gates cannot be narrowed.')


def source():
    from Scripts.release_adapter import source_identity
    value = source_identity()
    expected = os.environ.get('BLUEHOLE_MANAGER_SOURCE')
    if expected and json.loads(expected) != value:
        raise ValueError('Source changed after planning; inspect a new plan.')
    return value


def inspect_package(receipt):
    data = json.loads(Path(receipt).read_text())
    artifact = Path(data['artifact'])
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    if digest != data['sha256'] or data['source'] != source():
        raise ValueError('Package checksum or source changed.')
    with zipfile.ZipFile(artifact) as archive:
        identity = json.loads(archive.read('BlueHole/build-identity.json'))
        names = archive.namelist()
        expected = {'BlueHole/' + name for name in identity['members']} | {'BlueHole/build-identity.json'}
        if identity['source'] != data['source'] or len(names) != len(set(names)) or set(names) != expected:
            raise ValueError('Packaged identity or member inventory differs.')
        from Scripts.release_adapter import members
        if set(identity['members']) != set(members()):
            raise ValueError('Packaged members differ from the reviewed project allowlist.')
        for name, checksum in identity['members'].items():
            if hashlib.sha256(archive.read('BlueHole/' + name)).hexdigest() != checksum:
                raise ValueError('Packaged member checksum differs: ' + name)
    return dict(status='passed', source=data['source'], artifact=str(artifact), artifact_sha256=digest)


def package_suite(receipt, junit):
    evidence = {}
    class PackageInspection(unittest.TestCase):
        def test_exact_member_inventory_and_checksums(self):
            evidence.update(inspect_package(receipt))
    result = run_suite(unittest.defaultTestLoader.loadTestsFromTestCase(PackageInspection), junit, 'package.inspection', fail_on_skip=True)
    return dict(result, **evidence)


def native_suite(junit, receipt=None):
    evidence = {}
    class NativeAcceptance(unittest.TestCase):
        def test_supported_runtime_and_install(self):
            before = source()
            binary = Path(os.environ.get('BLUEHOLE_BLENDER', ''))
            if not binary.is_file():
                raise ValueError('Configure BLUEHOLE_BLENDER for supported Blender 5.2.2; portable checks cannot replace native acceptance.')
            version = subprocess.check_output([str(binary), '--version'], text=True, timeout=30).splitlines()[0]
            if not re.match(r'^Blender 5\.2\.2(?:\s|$)', version):
                raise ValueError('Native acceptance requires exact Blender 5.2.2.')
            command = [sys.executable, 'tests/blender_addon_smoke.py', '--blender', str(binary)]
            package = inspect_package(receipt) if receipt else None
            if package:
                command += ['--package', package['artifact']]
            subprocess.run(command, cwd=ROOT, check=True, timeout=180)
            if source() != before or package and inspect_package(receipt) != package:
                raise ValueError('Source or exact tested package changed during native acceptance.')
            evidence.update(source=before, runtime=version, registration_tested=True,
                            artifact_sha256=package['artifact_sha256'] if package else None)
    result = run_suite(unittest.defaultTestLoader.loadTestsFromTestCase(NativeAcceptance), junit, 'blender.integration', fail_on_skip=True)
    return dict(result, **evidence)


def require_cases(evidence, expected_source, suite):
    if evidence.get('status') != 'passed' or evidence.get('source') != expected_source:
        raise ValueError(suite + ': missing successful exact-source evidence.')
    cases = read_junit(evidence['report'])
    observed = [row['classname'] + '.' + row['name'] for row in cases]
    expected = evidence.get('expected_tests', [])
    if (not expected or len(observed) != len(set(observed)) or sorted(observed) != sorted(expected)
            or evidence.get('tests_run') != len(expected) or any(row['status'] != 'passed' for row in cases)
            or any(evidence.get(key) != 0 for key in ('failures', 'errors', 'skipped'))):
        raise ValueError(suite + ': required case inventory failed, changed or skipped.')
    names = {row['name'] for row in cases}
    required = {'blender.integration': 'test_supported_runtime_and_install',
                'package.inspection': 'test_exact_member_inventory_and_checksums'}.get(suite)
    if required and names != {required}:
        raise ValueError(suite + ': declared project case inventory differs.')
    if suite == 'portable.contracts':
        shared = [name for name in expected if name.endswith('.SharedCopy.test_pinned_shared_copy')]
        if len(shared) != 1 or sorted(set(expected) - set(shared)) != sorted(portable_case_ids()):
            raise ValueError('Portable full-suite inventory differs; focused results cannot satisfy release acceptance.')


def portable_case_ids():
    return list(test_ids(unittest.defaultTestLoader.discover(str(ROOT / 'tests'))))


def release_acceptance(checks, receipt, inspection, native, hosted, *, expected_source=None):
    current = expected_source if expected_source is not None else source()
    if current['dirty']:
        raise ValueError('Release acceptance requires exact clean committed source.')
    require_cases(checks, current, 'portable.contracts')
    require_cases(inspection, current, 'package.inspection')
    require_cases(native, current, 'blender.integration')
    if (native.get('registration_tested') is not True
            or not re.match(r'^Blender 5\.2\.2(?:\s|$)', native.get('runtime', ''))
            or native.get('artifact_sha256') != receipt['sha256']
            or inspection.get('artifact_sha256') != receipt['sha256']):
        raise ValueError('Native install/enable acceptance does not cover this exact package/runtime.')
    if (not hosted or hosted.get('status') != 'passed' or hosted.get('source') != current
            or hosted.get('platforms') != dict(macos='passed', linux='passed', windows='passed') or not hosted.get('run_id')):
        raise ValueError('Required exact-source hosted platform evidence is missing; no dispatch is implied.')
    return dict(schema=1, status='passed', source=current, artifact_sha256=receipt['sha256'],
                suites=['portable.contracts', 'package.inspection', 'blender.integration'], hosted_run=hosted['run_id'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['portable', 'native', 'inspect', 'acceptance'])
    parser.add_argument('--junit', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--checks', type=Path)
    parser.add_argument('--inspection', type=Path)
    parser.add_argument('--native', type=Path)
    parser.add_argument('--hosted', type=Path)
    parser.add_argument('--pattern', default='test*.py')
    args = parser.parse_args()
    args.junit.unlink(missing_ok=True)
    args.output.unlink(missing_ok=True)
    try:
        if args.action == 'portable':
            from Scripts.release_adapter import checks
            result = checks(junit=args.junit, pattern=args.pattern)
        elif args.action == 'native':
            result = native_suite(args.junit, args.receipt)
        elif args.action == 'inspect':
            result = package_suite(args.receipt, args.junit)
        else:
            value = {}
            class ReleaseAcceptance(unittest.TestCase):
                def test_required_source_package_host_and_case_inventory(self):
                    hosted = json.loads(args.hosted.read_text()) if args.hosted else None
                    value.update(release_acceptance(*(json.loads(path.read_text()) for path in
                        (args.checks, args.receipt, args.inspection, args.native)), hosted))
            outcome = run_suite(unittest.defaultTestLoader.loadTestsFromTestCase(ReleaseAcceptance), args.junit, 'release.acceptance', fail_on_skip=True)
            result = dict(outcome, **value)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        if not args.junit.exists():
            write_junit(args.junit, args.action, [dict(name='suite_prerequisites', classname=args.action, status='error', message=str(error))])
        result = dict(status='failed', error=str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    return int(result['status'] != 'passed')


if __name__ == '__main__':
    raise SystemExit(main())
