"""Suite routing, JUnit, exact ZIP native isolation and release gate contracts."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch
import zipfile

from build_manager.reporting import write_junit
from build_manager.test_results import read_junit
from Scripts import manager_plans, validation, reviewed_release

ROOT = Path(__file__).resolve().parents[1]


class ManagerSuiteTests(unittest.TestCase):
    def test_suite_validation_and_focused_release_rejection(self):
        validation.suite_selection('portable.contracts', 'Check', 'blender', 'test_release*.py')
        for suite, operation, pattern in [('missing','Check',''), ('blender.integration','Package',''),
                                           ('blender.integration','Check','test_*.py'), ('','Package','test_*.py')]:
            with self.subTest(suite=suite, operation=operation), self.assertRaises(ValueError):
                validation.suite_selection(suite, operation, 'blender', pattern)

    def plan(self, operation, suite='', **values):
        source = dict(dirty=False, commit='a', addon_version='6.9.21')
        env = dict(BLUEHOLE_MANAGER_SOURCE=json.dumps(source))
        return manager_plans.make_plan(operation, 'blender', 'Local', dict(suite=suite, **values), source, env, {}, ())

    def test_portable_and_native_choices_route_exactly_and_preserve_pattern(self):
        portable = self.plan('Check', 'portable.contracts', pattern='test_release*.py')
        self.assertEqual([phase.id for phase in portable.phases], ['portable-contracts'])
        self.assertIn('test_release*.py', portable.phases[0].argv)
        native = self.plan('Check', 'blender.integration')
        self.assertEqual([phase.id for phase in native.phases], ['blender-integration'])
        self.assertIn('junit', native.phases[0].artifact_types.values())
        self.assertEqual([phase.id for phase in self.plan('Check').phases], ['portable-contracts','blender-integration'])

    def test_reviewed_draft_depends_on_all_required_case_and_package_gates(self):
        plan = self.plan('Reviewed GitHub draft', 'release.acceptance', release_tag='bluehole-v6.9.21-blender5.2.2-alpha.1')
        rows = {phase.id: phase for phase in plan.phases}
        self.assertEqual(rows['blender-integration'].dependencies, ('package-inspection',))
        self.assertIn('--receipt', rows['blender-integration'].argv)
        self.assertEqual(rows['release-acceptance'].dependencies, ('portable-contracts','package-inspection','blender-integration'))
        self.assertEqual(rows['release-review'].dependencies, ('release-acceptance',))
        self.assertEqual(rows['github-draft'].dependencies, ('release-review',))
        self.assertEqual(rows['github-draft'].effect, 'upload')
        self.assertEqual(plan.effect, 'build')

    def test_missing_and_wrong_supported_runtime_produce_failing_case_reports(self):
        with TemporaryDirectory() as directory:
            root = Path(directory);report = root / 'native.xml'
            with patch.dict(os.environ, {'BLUEHOLE_BLENDER':''}), patch.object(validation, 'source', return_value={}):
                result = validation.native_suite(report)
            self.assertEqual(result['status'], 'failed')
            self.assertIn('Configure BLUEHOLE_BLENDER', read_junit(report)[0]['message'])
            binary = root / 'blender';binary.touch()
            with patch.dict(os.environ, {'BLUEHOLE_BLENDER':str(binary)}), patch.object(validation, 'source', return_value={}), \
                    patch.object(validation.subprocess, 'check_output', return_value='Blender 5.2.20\n'), \
                    patch.object(validation.subprocess, 'run') as run:
                self.assertEqual(validation.native_suite(report)['status'], 'failed')
            run.assert_not_called()

    def fixture_package(self, root):
        source = dict(commit='fixed', dirty=False)
        payload = b'bl_info={}'
        identity = dict(source=source, members={'__init__.py':hashlib.sha256(payload).hexdigest()})
        artifact = root / 'BlueHole.zip'
        with zipfile.ZipFile(artifact, 'w') as archive:
            archive.writestr('BlueHole/__init__.py', payload)
            archive.writestr('BlueHole/build-identity.json', json.dumps(identity))
        receipt = root / 'BlueHole.json'
        receipt.write_text(json.dumps(dict(source=source, artifact=str(artifact), sha256=hashlib.sha256(artifact.read_bytes()).hexdigest())))
        return receipt, source

    def test_package_inventory_inspects_actual_members_and_rejects_changed_bytes(self):
        with TemporaryDirectory() as directory:
            root = Path(directory);receipt, source = self.fixture_package(root)
            with patch.object(validation, 'source', return_value=source), patch('Scripts.release_adapter.members', return_value=['__init__.py']):
                self.assertEqual(validation.package_suite(receipt, root/'inspection.xml')['status'], 'passed')
                (root / 'BlueHole.zip').write_bytes(b'changed')
                self.assertEqual(validation.package_suite(receipt, root/'inspection.xml')['status'], 'failed')

    def test_native_driver_uses_exact_package_after_version_check(self):
        with TemporaryDirectory() as directory:
            root = Path(directory);receipt, source = self.fixture_package(root)
            binary = root / 'blender';binary.touch()
            with patch.object(validation, 'source', return_value=source), patch('Scripts.release_adapter.members', return_value=['__init__.py']), \
                    patch.dict(os.environ, {'BLUEHOLE_BLENDER':str(binary)}), \
                    patch.object(validation.subprocess, 'check_output', return_value='Blender 5.2.2\n'), \
                    patch.object(validation.subprocess, 'run') as run:
                result = validation.native_suite(root/'native.xml', receipt)
            self.assertEqual(result['status'], 'passed')
            self.assertIn('--package', run.call_args.args[0])
            self.assertEqual(result['artifact_sha256'], json.loads(receipt.read_text())['sha256'])

    def test_zip_fixture_extraction_rejects_traversal_and_links(self):
        spec = importlib.util.spec_from_file_location('isolated_blender_smoke', ROOT/'tests/blender_addon_smoke.py')
        smoke = importlib.util.module_from_spec(spec);spec.loader.exec_module(smoke)
        with TemporaryDirectory() as directory:
            root = Path(directory);archive = root/'bad.zip'
            for name in ('../escape', 'BlueHole/../escape', '/BlueHole/escape', 'Elsewhere/file'):
                with zipfile.ZipFile(archive, 'w') as files:files.writestr(name,'bad')
                with self.assertRaises(ValueError):smoke.extract_package(archive, root/'fixture')
            with zipfile.ZipFile(archive, 'w') as files:
                entry = zipfile.ZipInfo('BlueHole/link');entry.external_attr = 0o120777 << 16
                files.writestr(entry,'outside')
            with self.assertRaises(ValueError):smoke.extract_package(archive, root/'fixture')

    def evidence(self, root, suite, names, source):
        path = root / (suite + '.xml')
        cases = []
        for identity in names:
            classname, _, name = identity.rpartition('.')
            cases.append(dict(classname=classname, name=name, status='passed', seconds=.01))
        write_junit(path, suite, cases)
        return dict(status='passed',source=source, report=str(path),expected_tests=names, tests_run=len(names), failures=0, errors=0, skipped=0)

    def test_release_acceptance_checks_full_inventory_skips_native_package_and_hosted_source(self):
        with TemporaryDirectory() as directory:
            root = Path(directory);source = dict(dirty=False,commit='fixed')
            checks = self.evidence(root,'portable.contracts',['test_a.Case.test_one','Scripts.release_adapter.checks.<locals>.SharedCopy.test_pinned_shared_copy'],source)
            native = self.evidence(root,'blender.integration',['driver.NativeAcceptance.test_supported_runtime_and_install'],source)
            native.update(runtime='Blender 5.2.2',registration_tested=True,artifact_sha256='digest')
            inspection = self.evidence(root,'package.inspection',['driver.PackageInspection.test_exact_member_inventory_and_checksums'],source)
            inspection['artifact_sha256'] = 'digest'
            receipt = dict(source=source,sha256='digest')
            hosted = dict(status='passed',source=source,platforms=dict(macos='passed',linux='passed',windows='passed'),run_id='fixture')
            with patch.object(validation,'source',return_value=source), patch.object(validation,'portable_case_ids',return_value=['test_a.Case.test_one']):
                self.assertEqual(validation.release_acceptance(checks,receipt,inspection,native,hosted)['status'],'passed')
                with self.assertRaisesRegex(ValueError,'hosted'):validation.release_acceptance(checks,receipt,inspection,native,None)
                native['artifact_sha256'] = 'different'
                with self.assertRaisesRegex(ValueError,'exact package'):validation.release_acceptance(checks,receipt,inspection,native,hosted)
                native['artifact_sha256'] = 'digest';checks['skipped'] = 1
                with self.assertRaisesRegex(ValueError,'skipped'):validation.release_acceptance(checks,receipt,inspection,native,hosted)
                checks['skipped'] = 0
                with patch.object(validation,'portable_case_ids',return_value=['test_a.Case.test_one','test_a.Case.test_two']):
                    with self.assertRaisesRegex(ValueError,'full-suite inventory'):
                        validation.release_acceptance(checks,receipt,inspection,native,hosted)

    def test_real_bridge_forwards_selected_suite_without_dispatch(self):
        request = dict(schema=1, action='plan', values=dict(operation='Check', target='blender', backend='Local', suite='portable.contracts', pattern='test_release*.py'))
        result = subprocess.run([sys.executable, 'Scripts/manager_bridge.py'], cwd=ROOT, input=json.dumps(request), capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        plan = json.loads(result.stdout)['result']
        self.assertEqual([phase['id'] for phase in plan['phases']], ['portable-contracts'])
        self.assertIn('test_release*.py', plan['phases'][0]['argv'])
        self.assertEqual(plan['source']['test_suite'],'portable.contracts')

    def test_unapproved_or_interrupted_draft_never_uses_a_provider(self):
        with TemporaryDirectory() as directory:
            root = Path(directory);artifact = root/'addon.zip';artifact.write_bytes(b'fixture')
            candidate = root/'candidate.json';candidate.write_text(json.dumps(dict(artifact=str(artifact),sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),tag='fixture')))
            client = Mock()
            with patch.dict(os.environ,{'BUILD_MANAGER_APPROVED_PLAN':'','BUILD_MANAGER_APPROVED_ARTIFACTS':'[]'}):
                with self.assertRaisesRegex(ValueError,'approval'):reviewed_release.publish(candidate,root/'receipt.json',client=client)
            client.assert_not_called()
            rows = [dict(original_path=str(path.resolve()),sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for path in (artifact,candidate)]
            env = dict(BUILD_MANAGER_APPROVED_PLAN='fixture',BUILD_MANAGER_APPROVED_ARTIFACTS=json.dumps(rows))
            with patch.dict(os.environ,env), patch('Scripts.release_adapter.verify_candidate'), \
                    patch('Scripts.release_adapter.ReleaseTransport.publish_draft',side_effect=ConnectionError('accepted before connection loss')) as effect:
                with self.assertRaises(ConnectionError):reviewed_release.publish(candidate,root/'receipt.json',client=client)
                with self.assertRaisesRegex(ValueError,'Reconcile'):reviewed_release.publish(candidate,root/'receipt.json',client=client)
            self.assertEqual(effect.call_count,1)

    def test_downloaded_hosted_evidence_relocates_only_files_inside_artifact_directory(self):
        from Scripts.hosted_alpha import relocated_candidate
        with TemporaryDirectory() as directory:
            root=Path(directory)
            candidate={'artifact':'/previous-macos-runner/addon.zip','evidence':{}}
            for name in ('portable','inspection','native'):
                filename=name+'.xml';(root/filename).write_text('<testsuite/>')
                candidate['evidence'][name]={'report':'/previous-macos-runner/'+filename,'source':{'commit':'fixed'}}
            actual=relocated_candidate(candidate,root)
            for name in candidate['evidence']:
                self.assertEqual(actual['evidence'][name]['report'],str((root/(name+'.xml')).resolve()))
                self.assertEqual(actual['evidence'][name]['source'],{'commit':'fixed'})
            self.assertTrue(candidate['evidence']['native']['report'].startswith('/previous-macos-runner/'))
            (root/'native.xml').unlink()
            with self.assertRaisesRegex(ValueError,'missing or unsafe'):
                relocated_candidate(candidate,root)
            outside=root.parent/('outside-'+root.name+'.xml');outside.write_text('<testsuite/>')
            try:
                (root/'native.xml').symlink_to(outside)
                with self.assertRaisesRegex(ValueError,'missing or unsafe'):
                    relocated_candidate(candidate,root)
            finally:outside.unlink()
