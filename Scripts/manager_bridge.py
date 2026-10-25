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
    from build_manager.profiles import load_profile,save_profile
    from build_manager.registry import config_directory
    import os
    profile=config_directory()/'projects/io.github.ispaure.bluehole.json'
    tools=load_profile(profile)
    origins={}
    for key,variable in [('tools.shared_source','BLUEHOLE_SHARED_SOURCE'),('tools.blender','BLUEHOLE_BLENDER'),('tools.hosted_evidence','BLUEHOLE_HOSTED_EVIDENCE')]:
        origins[variable]='environment '+variable if variable in os.environ else 'private project tooling profile' if tools.get(key) else 'tracked unconfigured default'
        if tools.get(key) and variable not in os.environ:os.environ[variable]=tools[key]
    account=request.get('account_defaults',{})
    for key,variable,default in [('auth.github_reference','BLUEHOLE_GITHUB_REFERENCE','GH_TOKEN'),('auth.github_kind','BLUEHOLE_GITHUB_KIND','auto')]:
        origins[variable]='environment '+variable if variable in os.environ else 'selected shared GitHub account' if key in account else 'tracked project default'
        if variable not in os.environ:os.environ[variable]=account.get(key,default)
    values=request.get('values',{})
    action=request['action']
    if action=='plan':
        from Scripts.release_adapter import source_identity
        operation=values['operation']
        if operation not in ('Check','Package','Prepare GitHub release','Reviewed GitHub draft') or values['target']!='blender' or values['backend']!='Local':
            raise ValueError('Unsupported Blue Hole capability.')
        source=source_identity()
        tools_env={key:os.environ.get(key,'') for key in ('BLUEHOLE_SHARED_SOURCE','BLUEHOLE_BLENDER','BLUEHOLE_HOSTED_EVIDENCE','BLUEHOLE_GITHUB_REFERENCE','BLUEHOLE_GITHUB_KIND')}
        tools_env['BLUEHOLE_MANAGER_SOURCE']=json.dumps(source)
        secrets=tuple(dict.fromkeys(('GH_TOKEN','GITHUB_TOKEN','FIREBASE_TOKEN',os.environ['BLUEHOLE_GITHUB_REFERENCE']))) if os.environ['BLUEHOLE_GITHUB_KIND'] in {'auto','environment-name'} else ('GH_TOKEN','GITHUB_TOKEN','FIREBASE_TOKEN')
        from Scripts.manager_plans import make_plan
        result=make_plan(operation,values['target'],values['backend'],values,source,tools_env,origins,secrets).data()
    elif action=='settings':
        result={'github.repository':dict(value='ispaure/BlueHole',origin='tracked alpha release policy',read_only=True),
                'project.identity':dict(value='Blue Hole · Blender 5.2.2 alpha',origin='tracked project descriptor',read_only=True),
                'tools.shared_source':dict(value=__import__('os').environ.get('BLUEHOLE_SHARED_SOURCE',''),kind='directory',origin=origins['BLUEHOLE_SHARED_SOURCE']),
                'tools.blender':dict(value=__import__('os').environ.get('BLUEHOLE_BLENDER',''),kind='reference',origin=origins['BLUEHOLE_BLENDER']),
                'tools.hosted_evidence':dict(value=os.environ.get('BLUEHOLE_HOSTED_EVIDENCE',''),kind='reference',origin=origins['BLUEHOLE_HOSTED_EVIDENCE']),
                'auth.github_reference':dict(value=os.environ['BLUEHOLE_GITHUB_REFERENCE'],origin=origins['BLUEHOLE_GITHUB_REFERENCE'],read_only=True),
                'auth.github_kind':dict(value=os.environ['BLUEHOLE_GITHUB_KIND'],origin=origins['BLUEHOLE_GITHUB_KIND'],read_only=True)}
    elif action=='save_settings':
        changes=values['changes']
        save_profile(profile,changes,allowed={'tools.shared_source','tools.blender','tools.hosted_evidence'})
        result=None
    else:raise ValueError('Unsupported Blue Hole adapter action.')
    print(json.dumps(dict(schema=1,result=result)))


if __name__=='__main__':
    try:main()
    except (OSError,ValueError,RuntimeError) as error:
        print(str(error),file=sys.stderr);raise SystemExit(1)
