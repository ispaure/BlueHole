"""Blue Hole tooling runs in its own environment, never in Blender's interpreter."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
# Adapter dependencies belong to this add-on, including its vendored shared pin.
sys.path.insert(0,str(ROOT / 'Lib'))


TOOLS = {
    'tools.shared_source': ('BLUEHOLE_SHARED_SOURCE', 'directory'),
    'tools.blender': ('BLUEHOLE_BLENDER', 'reference'),
    'tools.hosted_evidence': ('BLUEHOLE_HOSTED_EVIDENCE', 'reference'),
}


def tool_setting(name, tools, environment):
    variable, _ = TOOLS[name]
    if variable in environment:
        return environment[variable], 'environment ' + variable
    if name in tools:
        return tools[name], 'private project tooling profile'
    return '', 'tracked unconfigured default'


def write_tools(profile, legacy, changes, resets):
    from build_manager.locking import workspace_lock
    from build_manager.profiles import load_profile, save_profile

    if (not isinstance(resets, (list, tuple)) or
            any(not isinstance(name, str) or name not in TOOLS for name in resets) or
            len(set(resets)) != len(resets) or set(resets).intersection(changes)):
        raise ValueError('Reset must name supported tooling overrides that are not also edited.')
    if set(changes) - TOOLS.keys() or any(not isinstance(value, str) for value in changes.values()):
        raise ValueError('Tool settings require supported field names and text values.')
    with workspace_lock(profile.with_name(profile.name + '.lock'), timeout=5):
        tools = load_profile(profile if profile.exists() else legacy)
        incoming = {name: tools[name] for name in TOOLS if name in tools and name not in resets}
        incoming.update(changes)
        save_profile(profile, incoming, allowed=TOOLS)


def main():
    request=json.load(sys.stdin)
    if request.get('schema')!=1:
        raise ValueError('Unsupported adapter schema.')
    from build_manager.profiles import load_profile
    from build_manager.registry import config_directory
    import os
    legacy=config_directory()/'projects/io.github.ispaure.bluehole.json'
    profile=Path(request['settings_profile']) if request.get('settings_profile') else legacy
    values=request.get('values',{})
    action=request['action']
    if action == 'save_settings':
        write_tools(profile, legacy, values['changes'], values.get('resets', ()))
        print(json.dumps(dict(schema=1, result=None)))
        return
    tools=load_profile(profile if profile.exists() else legacy)
    environment = dict(os.environ)
    origins={}
    for key, (variable, _) in TOOLS.items():
        value, origins[variable] = tool_setting(key, tools, environment)
        if value and variable not in environment:
            os.environ[variable] = value
    account=request.get('account_defaults',{})
    for key,variable,default in [('auth.github_reference','BLUEHOLE_GITHUB_REFERENCE','GH_TOKEN'),('auth.github_kind','BLUEHOLE_GITHUB_KIND','auto')]:
        origins[variable]='environment '+variable if variable in os.environ else 'selected shared GitHub account' if key in account else 'tracked project default'
        if variable not in os.environ:os.environ[variable]=account.get(key,default)
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
    elif action=='storage_inventory':
        from Scripts.build_retention import storage_inventory
        result=storage_inventory(ROOT)
    elif action=='delete_storage':
        from Scripts.build_retention import delete_storage
        result=delete_storage(values['selections'], ROOT)
    elif action=='storage_maintenance':
        from Scripts.build_retention import clean
        result=dict(status='passed',removed=clean(ROOT,apply=True))
    elif action=='settings':
        result={'github.repository':dict(value='ispaure/BlueHole',origin='tracked alpha release policy',read_only=True),
                'project.identity':dict(value='Blue Hole · Blender 5.2.2 alpha',origin='tracked project descriptor',read_only=True),
                'auth.github_reference':dict(value=os.environ['BLUEHOLE_GITHUB_REFERENCE'],origin=origins['BLUEHOLE_GITHUB_REFERENCE'],read_only=True),
                'auth.github_kind':dict(value=os.environ['BLUEHOLE_GITHUB_KIND'],origin=origins['BLUEHOLE_GITHUB_KIND'],read_only=True)}
        for name, (variable, kind) in TOOLS.items():
            fallback, fallback_origin = tool_setting(name, {}, environment)
            result[name] = dict(value=os.environ.get(variable, ''), kind=kind, origin=origins[variable],
                                reset=dict(overridden=name in tools, value=fallback, origin=fallback_origin))
    else:raise ValueError('Unsupported Blue Hole adapter action.')
    print(json.dumps(dict(schema=1,result=result)))


if __name__=='__main__':
    try:main()
    except (OSError,ValueError,RuntimeError) as error:
        print(str(error),file=sys.stderr);raise SystemExit(1)
