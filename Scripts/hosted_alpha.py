"""Explicit hosted alpha review; missing Blender keeps the publication gate closed."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from Scripts.release_adapter import source_identity,package,prepare,ReleaseTransport,artifact_name



def relocated_candidate(candidate, directory):
    """Rebind downloaded evidence files, retaining every source/checksum gate."""
    directory=Path(directory).resolve()
    candidate=json.loads(json.dumps(candidate))
    candidate['artifact']=str(directory/artifact_name())
    for name in ('portable','inspection','native'):
        evidence=candidate.get('evidence',{}).get(name)
        if not isinstance(evidence,dict) or not evidence.get('report'):
            raise ValueError('Required downloaded '+name+' report is missing.')
        report=directory/Path(evidence['report']).name
        if report.is_symlink() or not report.is_file() or not report.resolve().is_relative_to(directory):
            raise ValueError('Required downloaded '+name+' report is missing or unsafe.')
        evidence['report']=str(report)
    return candidate


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--create-draft',action='store_true')
    args=parser.parse_args()
    source=source_identity()
    if source['dirty'] or source['commit']!=os.environ['EXPECTED_COMMIT']:
        raise ValueError('Hosted source differs from the reviewed dispatch.')
    artifact=ROOT/'test-results/release'/artifact_name()
    if args.create_draft:
        candidate=relocated_candidate(json.loads((artifact.parent/'candidate.json').read_text()),artifact.parent)
        if os.environ.get('REVIEWED_SHA256')!=candidate['sha256'] or os.environ.get('RELEASE_TAG')!=candidate['tag']:
            raise ValueError('Post-build review of this exact checksum, embedded version and destination/tag is required before draft creation.')
        from Scripts.release_adapter import verify_candidate
        verify_candidate(candidate) # Reject stale/missing gates before reading credentials.
        from Scripts.github_alpha import GitHubDraftClient
        from build_manager.github import credential_token
        from build_manager.settings import SettingsStore
        account=SettingsStore().account_defaults('io.github.ispaure.bluehole',{'github':{'reference':'auth.github_reference','kind':'auth.github_kind'}})
        reference=os.environ.get('BLUEHOLE_GITHUB_REFERENCE') or account.get('auth.github_reference') or 'GH_TOKEN'
        kind=os.environ.get('BLUEHOLE_GITHUB_KIND') or account.get('auth.github_kind') or 'auto'
        token=credential_token(reference=reference,kind=kind,root=ROOT)
        receipt=ReleaseTransport(GitHubDraftClient(token)).publish_draft(candidate,confirmed=True)
        (artifact.parent/'draft-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt));return
    receipt=package(artifact)
    from Scripts.validation import native_suite, package_suite
    inspection=package_suite(artifact.with_suffix('.json'),artifact.parent/'inspection.xml')
    native=native_suite(artifact.parent/'native.xml',artifact.with_suffix('.json'))
    if inspection['status']!='passed' or native['status']!='passed':
        raise ValueError('Exact package inspection and supported Blender install/enable acceptance are required.')
    hosted=dict(status='passed',source=source,platforms=dict(macos='passed',linux='passed',windows='passed'),run_id=os.environ['GITHUB_RUN_ID'])
    candidate=prepare(receipt,os.environ['RELEASE_TAG'],native=native,hosted=hosted,inspection=inspection)
    (artifact.parent/'candidate.json').write_text(json.dumps(candidate,indent=2)+'\n')
    print(json.dumps(candidate,indent=2))


if __name__=='__main__':main()
