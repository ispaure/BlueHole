"""Blue Hole tooling runs in its own environment, never in Blender's interpreter."""
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def main():
    request=json.load(sys.stdin)
    if request.get('schema')!=1:
        raise ValueError('Unsupported adapter schema.')
    from build_manager import Phase,Plan
    values=request.get('values',{})
    action=request['action']
    if action=='plan':
        if values['operation']!='Check' or values['target']!='blender' or values['backend']!='Local':
            raise ValueError('Unsupported Blue Hole capability.')
        source=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
        result=Plan('Blue Hole','Check',source,
            (Phase('checks',(sys.executable,'-m','unittest','discover','-s','tests','-v'),str(ROOT)),),
            str(ROOT/'test-results/build-manager/workspace')).data()
    elif action=='settings':
        result={'project.identity':dict(value='Blue Hole · Blender 5.2.2 alpha',origin='tracked project descriptor',read_only=True)}
    elif action=='save_settings':
        if values['changes']:raise ValueError('No mutable Blue Hole settings are declared yet.')
        result=None
    else:raise ValueError('Unsupported Blue Hole adapter action.')
    print(json.dumps(dict(schema=1,result=result)))


if __name__=='__main__':
    try:main()
    except (OSError,ValueError,RuntimeError) as error:
        print(str(error),file=sys.stderr);raise SystemExit(1)
