"""Exact-source GitHub draft creation; only explicit reviewed callers may write."""
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request

from build_manager.github import GitHub


class GitHubDraftClient:
    def __init__(self,token=None,*,transport=None):
        self.github=GitHub('ispaure/BlueHole',token,transport=transport)
        self.transport=transport

    def reconcile(self,candidate):
        try:release=self.github.request('GET',self.github.base+'/releases/tags/'+quote(candidate['tag'],safe=''))
        except RuntimeError as error:
            if 'HTTP 404' in str(error):return None
            raise
        if not release.get('draft') or not release.get('prerelease') or release.get('target_commitish')!=candidate['source']['commit']:
            raise ValueError('Existing release/tag belongs to different or published state; it will not be overwritten.')
        matches=[asset for asset in release.get('assets',[]) if asset['name']==Path(candidate['artifact']).name]
        if len(matches)!=1 or matches[0].get('digest')!='sha256:'+candidate['sha256']:
            raise ValueError('Existing draft needs reconciliation; no duplicate release or asset was created.')
        return self.receipt(candidate,release,matches[0])

    def create_draft(self,candidate):
        if self.reconcile(candidate) is not None:raise ValueError('Draft already exists; reuse its verified receipt.')
        try:self.github.resolve_ref(candidate['tag'])
        except ValueError:pass
        else:raise ValueError('Remote tag already exists; it will not be moved.')
        release=self.github.request('POST',self.github.base+'/releases',dict(tag_name=candidate['tag'],
            target_commitish=candidate['source']['commit'],name=candidate['tag'],draft=True,prerelease=True,
            body='Reviewed Blender 5.2.2 alpha candidate. Add-on '+candidate['source']['addon_version']+'.'))
        path=self.github.base+f'/releases/{release["id"]}/assets?name='+quote(Path(candidate['artifact']).name,safe='')
        payload=Path(candidate['artifact']).read_bytes()
        if hashlib.sha256(payload).hexdigest()!=candidate['sha256']:raise ValueError('Artifact changed before upload.')
        if self.transport is not None:asset=self.transport('UPLOAD',path,payload)
        else:
            if not self.github.token:raise ValueError('A protected GitHub credential reference is required.')
            request=Request('https://uploads.github.com'+path,method='POST',data=payload,
                headers={'Authorization':'Bearer '+self.github.token,'Content-Type':'application/zip',
                         'Accept':'application/vnd.github+json'})
            try:
                with self.github.opener.open(request,timeout=120) as response:asset=json.loads(response.read())
            except Exception:
                raise RuntimeError('Draft asset upload outcome is unknown; reconcile this exact draft before retrying.') from None
        if asset.get('digest')!='sha256:'+candidate['sha256']:
            raise RuntimeError('Upload outcome is uncertain; reconcile this exact draft before retrying.')
        return self.receipt(candidate,release,asset)

    @staticmethod
    def receipt(candidate,release,asset):
        return dict(schema=1,status='draft prepared',repository=candidate['repository'],tag=candidate['tag'],
            commit=candidate['source']['commit'],sha256=candidate['sha256'],release_id=release['id'],
            asset_id=asset['id'],url=release['html_url'])
