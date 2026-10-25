"""Blue Hole tooling runs in its own environment, never in Blender's interpreter."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def main():
    request=json.load(sys.stdin)
    if request.get('schema')!=1:
        raise ValueError('Unsupported adapter schema.')
    from build_manager import Phase,Plan
    from build_manager.profiles import load_profile,save_profile
    from build_manager.registry import config_directory
    import os
    profile=config_directory()/'projects/io.github.ispaure.bluehole.json'
    tools=load_profile(profile)
    origins={}
    for key,variable in [('tools.shared_source','BLUEHOLE_SHARED_SOURCE'),('tools.blender','BLUEHOLE_BLENDER')]:
        origins[variable]='environment '+variable if variable in os.environ else 'private project tooling profile' if tools.get(key) else 'tracked unconfigured default'
        if tools.get(key) and variable not in os.environ:os.environ[variable]=tools[key]
    account=request.get('account_defaults',{})
    for key,variable,default in [('auth.github_reference','BLUEHOLE_GITHUB_REFERENCE','GH_TOKEN'),('auth.github_kind','BLUEHOLE_GITHUB_KIND','auto')]:
        origins[variable]='environment '+variable if variable in os.environ else 'selected shared GitHub account' if key in account else 'tracked project default'
        if variable not in os.environ:os.environ[variable]=account.get(key,default)
    values=request.get('values',{})
    action=request['action']
    if action=='plan':
        from Scripts.release_adapter import source_identity,artifact_name
        operation=values['operation']
        if operation not in ('Check','Package','Prepare GitHub release') or values['target']!='blender' or values['backend']!='Local':
            raise ValueError('Unsupported Blue Hole capability.')
        source=source_identity()
        from uuid import uuid4
        run=ROOT/'test-results/release'/uuid4().hex
        artifact=run/artifact_name()
        base=(sys.executable,'Scripts/release_adapter.py')
        tools_env={key:os.environ.get(key,'') for key in ('BLUEHOLE_SHARED_SOURCE','BLUEHOLE_BLENDER','BLUEHOLE_GITHUB_REFERENCE','BLUEHOLE_GITHUB_KIND')}
        tools_env['BLUEHOLE_MANAGER_SOURCE']=json.dumps(source)
        checks=run/'checks.json'
        check=Phase('checks',(*base,'check','--output',str(checks)),str(ROOT),timeout=300,environment=tools_env,artifacts=(str(checks),))
        phases=(check,)
        if operation!='Check':
            phases=(check,Phase('package',(*base,'package','--output',str(artifact),'--checks',str(checks)),str(ROOT),
                timeout=300,dependencies=('checks',),kind='build',environment=tools_env,artifacts=(str(artifact),str(artifact.with_suffix('.json')))))
        if operation=='Prepare GitHub release':
            if not values.get('release_tag'):raise ValueError('Choose an explicit alpha release tag.')
            phases+= (Phase('release-review',(*base,'prepare','--receipt',str(artifact.with_suffix('.json')),
                '--tag',values['release_tag'],'--output',str(run/'candidate.json')),str(ROOT),dependencies=('package',),kind='inspect',environment=tools_env,artifacts=(str(run/'candidate.json'),)),)
        secrets=tuple(dict.fromkeys(('GH_TOKEN','GITHUB_TOKEN','FIREBASE_TOKEN',os.environ['BLUEHOLE_GITHUB_REFERENCE']))) if os.environ['BLUEHOLE_GITHUB_KIND'] in {'auto','environment-name'} else ('GH_TOKEN','GITHUB_TOKEN','FIREBASE_TOKEN')
        result=Plan('Blue Hole',operation,dict(source,destination='ispaure/BlueHole',channel='alpha'),phases,str(ROOT/'test-results/build-manager/workspace'),
                    effect='test' if operation=='Check' else 'build',secret_environment=secrets,settings=dict(values=tools_env,origins=dict(origins,BLUEHOLE_MANAGER_SOURCE='captured source identity'))).data()
    elif action=='settings':
        result={'github.repository':dict(value='ispaure/BlueHole',origin='tracked alpha release policy',read_only=True),
                'project.identity':dict(value='Blue Hole · Blender 5.2.2 alpha',origin='tracked project descriptor',read_only=True),
                'tools.shared_source':dict(value=__import__('os').environ.get('BLUEHOLE_SHARED_SOURCE',''),kind='directory',origin=origins['BLUEHOLE_SHARED_SOURCE']),
                'tools.blender':dict(value=__import__('os').environ.get('BLUEHOLE_BLENDER',''),kind='reference',origin=origins['BLUEHOLE_BLENDER']),
                'auth.github_reference':dict(value=os.environ['BLUEHOLE_GITHUB_REFERENCE'],origin=origins['BLUEHOLE_GITHUB_REFERENCE'],read_only=True),
                'auth.github_kind':dict(value=os.environ['BLUEHOLE_GITHUB_KIND'],origin=origins['BLUEHOLE_GITHUB_KIND'],read_only=True)}
    elif action=='save_settings':
        changes=values['changes']
        save_profile(profile,changes,allowed={'tools.shared_source','tools.blender'})
        result=None
    else:raise ValueError('Unsupported Blue Hole adapter action.')
    print(json.dumps(dict(schema=1,result=result)))


if __name__=='__main__':
    try:main()
    except (OSError,ValueError,RuntimeError) as error:
        print(str(error),file=sys.stderr);raise SystemExit(1)
