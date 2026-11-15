"""Exercise the pushed updater in a disposable installed copy, never a preset.

python tests/blender_addon_update.py --blender /path/to/blender --output /path/to/evidence
Requires online access to the public BlueHole repository. Saves screenshots and
receipts, then removes all temporary addon/preferences/download directories.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
import traceback


def native(root, output):
    import addon_utils
    import bpy
    import importlib
    bpy.context.preferences.use_preferences_save = False
    bpy.context.preferences.view.show_splash = False
    addon_utils.enable('BlueHole', default_set=True)
    package = root / 'scripts/addons/BlueHole'
    initial_module = sys.modules['BlueHole']
    report = {'status': 'running'}
    stage = 0
    deadline = time.monotonic() + 240
    original_hash = None
    session = None
    saved_default = None
    initial_handlers = None
    workspace = None

    def finish(error=None):
        report['status'] = 'failed' if error else 'passed'
        if error:report['error'] = error
        (output/'verification.json').write_text(json.dumps(report,indent=2))
        addon_utils.disable('BlueHole',default_set=True)
        bpy.ops.wm.quit_blender()

    def tick():
        nonlocal stage,original_hash,session,saved_default,initial_handlers,workspace
        try:
            if time.monotonic() > deadline:raise RuntimeError('Update integration test timed out')
            module = sys.modules['BlueHole']
            runtime = importlib.import_module('BlueHole.blenderUtils.addon_updates')
            prefs = bpy.context.preferences.addons['BlueHole'].preferences
            if stage == 0:
                if not module._keymaps_registered:return .2
                assert prefs.help_n_update.update_channel == 'main'
                prefs.help_n_update.update_channel = 'alpha'
                # These old preference artifacts must neither prompt nor change.
                keyconfig = root/'scripts/presets/keyconfig/BH_Keymaps.py'
                keyconfig.parent.mkdir(parents=True,exist_ok=True);keyconfig.write_text('# old artifact')
                assert bpy.ops.wm.bh_apply_deluxe_prefs('INVOKE_DEFAULT') == {'FINISHED'}
                assert prefs.keymap.enable_keymaps
                assert bpy.ops.wm.bh_disable_deluxe_keymaps('INVOKE_DEFAULT') == {'FINISHED'}
                assert not prefs.keymap.enable_keymaps
                assert bpy.ops.wm.bh_apply_deluxe_prefs('INVOKE_DEFAULT') == {'FINISHED'}
                report['direct_keymap_toggle'] = True
                custom = package/'envFiles/Update Test Studio'
                shutil.copytree(package/'envFiles/default',custom)
                (custom/'keep-me.bin').write_bytes(b'private environment\x00data')
                (package/'envFiles/default/obsolete-test-file.txt').write_text('must disappear')
                bpy.ops.wm.save_userpref()
                original_hash = hashlib.sha256((root/'config/userpref.blend').read_bytes()).hexdigest()
                initial_handlers = {name:len(getattr(bpy.app.handlers,name)) for name in ('load_pre','load_post','save_pre','save_post')}
                prefs.main_settings='GENERAL_ADDON';prefs.general_addon_settings='HELP_N_UPDATE'
                area=max(bpy.context.window.screen.areas,key=lambda a:a.width*a.height);area.type='PREFERENCES'
                with bpy.context.temp_override(area=area):bpy.ops.preferences.addon_show(module='BlueHole')
                bpy.ops.wm.bh_check_update();stage=1
            elif stage == 1:
                if runtime.state['status'] in {'idle','checking'}:return .2
                assert runtime.state['status']=='available',runtime.state
                report['selected_branch']=runtime.state['release']['branch']
                report['downloaded_commit']=runtime.state['release']['commit']
                assert report['selected_branch']=='blender-5.2.2/alpha'
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=2)
                bpy.ops.screen.screenshot(filepath=str(output/'update-available.png'))
                assert bpy.ops.wm.bh_update_addon()=={'FINISHED'}
                stage=2
            elif stage == 2:
                if runtime.state['status'] in {'downloading','installing','idle'}:return .2
                assert runtime.state['status']=='current',runtime.state
                assert module is not initial_module
                assert prefs.keymap.enable_keymaps and prefs.help_n_update.update_channel=='alpha'
                assert (package/'envFiles/Update Test Studio/keep-me.bin').read_bytes()==b'private environment\x00data'
                assert not (package/'envFiles/default/obsolete-test-file.txt').exists()
                assert hashlib.sha256((root/'config/userpref.blend').read_bytes()).hexdigest()==original_hash
                assert {name:len(getattr(bpy.app.handlers,name)) for name in initial_handlers}==initial_handlers
                marker=json.loads((package/'.bluehole-update.json').read_text())
                manifest=json.loads((root/'.logistics-addons.json').read_text())
                assert marker['commit']==report['downloaded_commit']==manifest['installed_bluehole']['commit']
                assert manifest['bluehole']['branch']=='alpha'
                assert manifest['installed']['legacy:BlueHole']['digest']==marker['package_digest']
                report.update(reloaded_in_place=True,custom_environments_preserved=True,default_environment_replaced=True,
                              userpref_bytes_unchanged=True,preferences_retained=True,no_duplicate_handlers=True,logistics_receipt_updated=True)
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=2)
                bpy.ops.screen.screenshot(filepath=str(output/'update-complete.png'))
                # A separately staged broken candidate verifies native rollback.
                workspace=TemporaryDirectory(prefix='.rollback-test-',dir=package.parent)
                snapshot=Path(workspace.name)/'snapshot'
                shutil.copytree(package,snapshot,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
                with (snapshot/'__init__.py').open('a') as stream:
                    stream.write('\ndef register():\n    raise RuntimeError("Deliberate update validation failure")\n')
                saved_default=(package/'envFiles/default/env_variables.ini').read_bytes()
                runtime._handoff=True
                session=runtime.ReloadSession(package,snapshot,marker,workspace)
                session.begin();stage=3
            elif stage == 3:
                if not session.done:return .2
                assert runtime.state['status']=='error' and 'previous Blue Hole restored' in runtime.state['message'],runtime.state
                assert addon_utils.check('BlueHole')[1] and module._keymaps_registered
                assert (package/'envFiles/default/env_variables.ini').read_bytes()==saved_default
                assert (package/'envFiles/Update Test Studio/keep-me.bin').read_bytes()==b'private environment\x00data'
                assert hashlib.sha256((root/'config/userpref.blend').read_bytes()).hexdigest()==original_hash
                assert {name:len(getattr(bpy.app.handlers,name)) for name in initial_handlers}==initial_handlers
                report['failed_update_restores_live_addon']=True
                assert not list(package.parent.glob('.bluehole-update-*'))
                assert not list(package.parent.glob('.rollback-test-*'))
                report['temporary_downloads_removed']=True
                finish();return None
            return .2
        except Exception:
            finish(traceback.format_exc());return None
    bpy.app.timers.register(tick,first_interval=1)


def launch():
    parser=argparse.ArgumentParser()
    parser.add_argument('--blender',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
    from blender_keymap_runtime import stage_package
    with TemporaryDirectory(prefix='bluehole-update-test-') as temp:
        root=Path(temp).resolve()/'preset'
        root.mkdir()
        env=dict(os.environ);env.pop('PYTHONPATH',None)
        for name in ('RESOURCES','CONFIG','SCRIPTS','EXTENSIONS','DATAFILES'):
            folder=root/name.lower();folder.mkdir();env['BLENDER_USER_'+name]=str(folder)
        (root/'tmp').mkdir();env['TMPDIR']=str(root/'tmp')
        env.update(BLUEHOLE_UPDATE_TEST_ROOT=str(root),BLUEHOLE_UPDATE_TEST_OUTPUT=str(output),PYTHONDONTWRITEBYTECODE='1')
        stage_package(root,None)
        (root/'scripts/addons/bluehole_runtime').rename(root/'scripts/addons/BlueHole')
        previous_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD^'],
                                                  cwd=Path(__file__).resolve().parents[1], text=True).strip()
        (root/'.logistics-addons.json').write_text(json.dumps(dict(selected=[],
            installed={'legacy:BlueHole':dict(path='scripts/addons/BlueHole',module='BlueHole',digest='0'*64,version='6.9.21')},
            bluehole=dict(enabled=True,source='github',branch='main',auto_update=False),
            installed_bluehole=dict(branch='blender-5.2.2/main',commit=previous_commit))))
        command=[str(args.blender),'--factory-startup','--disable-autoexec','--online-mode','--python-exit-code','1','--python',str(Path(__file__).resolve())]
        if sys.platform=='darwin':
            policy=root/'policy.sb'
            policy.write_text('(version 1)\n(allow default)\n(deny file-write*)\n'+
                ''.join('(allow file-write* (subpath '+json.dumps(str(p))+'))\n' for p in (root.parent,output))+
                '(allow file-write* (literal "/dev/null"))\n')
            command=['/usr/bin/sandbox-exec','-f',str(policy),*command]
        with (output/'blender.log').open('w') as log:
            child=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT)
            try:code=child.wait(timeout=270)
            except subprocess.TimeoutExpired:
                child.kill();child.wait();raise
        report=json.loads((output/'verification.json').read_text())
        report['process_exit_code']=code
    report['temporary_installation_removed']=not root.exists()
    (output/'verification.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    if code or report['status']!='passed':raise SystemExit(1)


if __name__=='__main__':
    if os.environ.get('BLUEHOLE_UPDATE_TEST_ROOT'):
        native(Path(os.environ['BLUEHOLE_UPDATE_TEST_ROOT']),Path(os.environ['BLUEHOLE_UPDATE_TEST_OUTPUT']))
    else:
        launch()
