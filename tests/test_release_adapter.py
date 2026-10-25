"""Packaging and publication guards use isolated fixtures and controlled transport."""
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch,Mock

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('bluehole_release',ROOT/'Scripts/release_adapter.py')
adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)


class ReleaseAdapterTests(unittest.TestCase):
    def test_allowlist_rejects_unexpected_runtime_member(self):
        original=adapter.git
        def git(*args):
            result=original(*args)
            return result+'\0wrappers/unexpected.py' if args[0]=='ls-files' else result
        with patch.object(adapter,'git',side_effect=git),patch.object(Path,'is_file',return_value=True):
            with self.assertRaisesRegex(ValueError,'allowlist'):adapter.members()

    def test_alpha_tag_separates_addon_and_blender_versions(self):
        self.assertEqual(adapter.release_tag('6.9.21',2),'bluehole-v6.9.21-blender5.2.2-alpha.2')
        with self.assertRaises(ValueError):adapter.release_tag('5.2.2',0)

    def test_development_receipt_cannot_be_relabelled_or_upload_without_gates(self):
        source=dict(dirty=True)
        with patch.object(adapter,'source_identity',return_value=source):
            with self.assertRaisesRegex(ValueError,'committed'):adapter.prepare({'source':source},'fake')
        client=Mock();transport=adapter.ReleaseTransport(client)
        with self.assertRaises(ValueError):transport.publish_draft({'publishable':False},confirmed=True)
        client.assert_not_called();client.reconcile.assert_not_called()

    def candidate(self,root):
        import zipfile,hashlib
        source=dict(dirty=False,commit='a'*40,addon_version='6.9.21')
        artifact=root/'addon.zip'
        with zipfile.ZipFile(artifact,'w') as archive:
            archive.writestr('BlueHole/build-identity.json',json.dumps(dict(source=source)))
        evidence=dict(native=dict(status='passed',source=source,runtime='Blender 5.2.2'),
            hosted=dict(status='passed',source=source,platforms=dict(macos='passed',linux='passed',windows='passed'),run_id='7'))
        return dict(source=source,artifact=str(artifact),sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),
            publishable=True,blocked_gates=[],evidence=evidence,repository='ispaure/BlueHole',tag='bluehole-v6.9.21-blender5.2.2-alpha.1')

    def test_controlled_retry_reconciles_without_duplicate_draft(self):
        with TemporaryDirectory() as directory:
            candidate=self.candidate(Path(directory))
            receipt=dict(tag='fixture',status='draft created')
            client=Mock();client.reconcile.return_value=receipt
            with patch.object(adapter,'source_identity',return_value=candidate['source']):
                self.assertEqual(adapter.ReleaseTransport(client).publish_draft(candidate,confirmed=True),receipt)
            client.create_draft.assert_not_called()

    def test_upload_accepted_before_connection_loss_reconciles_exact_existing_asset(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('github_alpha',ROOT/'Scripts/github_alpha.py')
        client_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(client_module)
        with TemporaryDirectory() as directory:
            candidate=self.candidate(Path(directory));state={'release':None,'posts':0,'uploads':0}
            def transport(method,path,body):
                if method=='GET':
                    if '/releases/tags/' in path and state['release']:return state['release']
                    raise RuntimeError('GitHub HTTP 404')
                if method=='POST':
                    state['posts']+=1
                    state['release']=dict(id=17,draft=True,prerelease=True,target_commitish=candidate['source']['commit'],assets=[],html_url='https://example.invalid/draft/17')
                    return state['release']
                if method=='UPLOAD':
                    state['uploads']+=1
                    state['release']['assets']=[dict(id=23,name='addon.zip',digest='sha256:'+candidate['sha256'])]
                    raise ConnectionError('synthetic accepted upload before connection loss')
                raise AssertionError('Unexpected provider operation')
            client=client_module.GitHubDraftClient(transport=transport)
            with patch.object(adapter,'source_identity',return_value=candidate['source']):
                with self.assertRaises(ConnectionError):adapter.ReleaseTransport(client).publish_draft(candidate,confirmed=True)
                receipt=adapter.ReleaseTransport(client).publish_draft(candidate,confirmed=True)
            self.assertEqual(receipt['asset_id'],23);self.assertEqual(state['posts'],1);self.assertEqual(state['uploads'],1)
