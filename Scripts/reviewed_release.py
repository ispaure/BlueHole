"""Consume one exact manager-approved candidate without rebuilding its ZIP."""
import argparse
import hashlib
import json
import os
from pathlib import Path


def approved(candidate_path):
    candidate_path = Path(candidate_path)
    candidate = json.loads(candidate_path.read_text())
    rows = json.loads(os.environ.get('BUILD_MANAGER_APPROVED_ARTIFACTS', '[]'))
    if not os.environ.get('BUILD_MANAGER_APPROVED_PLAN'):
        raise ValueError('Exact candidate and artifact need manager approval.')
    for path in (candidate_path, Path(candidate['artifact'])):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if not any(row.get('original_path') == str(path.resolve()) and row.get('sha256') == digest for row in rows):
            raise ValueError('Candidate or ZIP differs from exact manager-reviewed artifacts.')
    return candidate


def publish(candidate_path, receipt, *, client=None):
    candidate = approved(candidate_path)
    from Scripts.release_adapter import ReleaseTransport, verify_candidate
    verify_candidate(candidate)
    receipt = Path(receipt)
    attempt = receipt.with_suffix('.attempt.json')
    if attempt.exists() or receipt.exists():
        raise ValueError('Reconcile the recorded GitHub attempt before retry; no blind duplicate is allowed.')
    if client is None:
        from Scripts.github_alpha import GitHubDraftClient
        from build_manager.github import credential_token
        from Scripts.manager_plans import ROOT
        token = credential_token(reference=os.environ.get('BLUEHOLE_GITHUB_REFERENCE', 'GH_TOKEN'),
                                 kind=os.environ.get('BLUEHOLE_GITHUB_KIND', 'auto'), root=ROOT)
        client = GitHubDraftClient(token)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    attempt.write_text(json.dumps(dict(status='unknown until reconciled', plan=os.environ['BUILD_MANAGER_APPROVED_PLAN'],
        operation_id=os.environ.get('BUILD_MANAGER_OPERATION_ID'), tag=candidate['tag'], sha256=candidate['sha256'])) + '\n')
    result = ReleaseTransport(client).publish_draft(candidate, confirmed=True)
    receipt.write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(publish(args.candidate, args.receipt)))


if __name__ == '__main__':
    main()
