"""Nonblocking update checks and main-thread addon unload/swap/reload."""
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import mkdtemp
from time import monotonic

import addon_utils
import bpy

from . import update_service as service
from .reload_transaction import ReloadTransaction

ROOT = Path(__file__).absolute().parents[1]
MODULE = __package__.split('.')[0]
state = {'status': 'idle', 'message': '', 'blocked': '', 'release': None, 'channel': None}
_job = None
_handoff = False


def redraw():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()


def settings():
    addon = bpy.context.preferences.addons.get(MODULE)
    return addon.preferences.help_n_update if addon and addon.preferences else None


def start(action):
    global _job
    if _job is not None or _handoff:
        raise ValueError('A Blue Hole update is already in progress')
    if not bpy.app.online_access:
        raise ValueError('Enable Allow Online Access in Blender Preferences → System to check for updates')
    prefs = settings()
    if prefs is None:
        raise ValueError('Blue Hole preferences are not ready')
    channel = prefs.update_channel
    if action == 'install':
        from ..preferences.addon.keymaps.deluxe_editor_ops import require_saved_draft
        require_saved_draft()
        blocker = service.install_blocker(ROOT)
        if blocker:
            raise ValueError(blocker)
        if state['status'] == 'current' and state['channel'] == channel:
            raise ValueError('Blue Hole is already up to date in the selected channel')
        if state['status'] not in {'available', 'unverified', 'ahead', 'different'} or state['channel'] != channel:
            raise ValueError('Check for updates in the selected channel first')
    workspace = Path(mkdtemp(prefix='.bluehole-update-', dir=ROOT.parent if action == 'install' else None))
    request = {'action': 'check' if action == 'check' else 'stage', 'channel': channel,
               'blender_version': list(bpy.app.version), 'workspace': str(workspace), 'release': state['release'],
               'installed_root': str(ROOT)}
    try:
        (workspace / 'request.json').write_text(json.dumps(request), encoding='utf-8')
        with (workspace / 'worker.log').open('wb') as output:
            process = subprocess.Popen([sys.executable, *bpy.app.python_args,
                str(ROOT / 'blenderUtils/update_worker.py'), str(workspace / 'request.json'), str(workspace / 'response.json')],
                stdin=subprocess.DEVNULL, stdout=output, stderr=output,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    except Exception:
        shutil.rmtree(workspace)
        raise
    _job = (process, workspace, action, monotonic())
    state.update(status='checking' if action == 'check' else 'downloading', channel=channel, message='')
    if action == 'check':
        state.update(release=None, blocked='')
    redraw()


def _stop_job():
    global _job
    if _job is not None:
        process, workspace, *_ = _job
        if process.poll() is None:
            process.kill()
            process.wait()
        _job = None
        shutil.rmtree(workspace)


def cancel():
    if _job is None or _handoff:
        raise ValueError('There is no Blue Hole check or download to cancel')
    _stop_job()
    state.update(status='cancelled', release=None, channel=None, message='Blue Hole update cancelled.')
    redraw()


def invalidate(_self=None, _context=None):
    # A channel change invalidates a checked commit; never install the previous
    # channel's candidate after the user changes this preference.
    if _job is None and not _handoff:
        state.update(status='idle', release=None, channel=None, message='', blocked='')


def poll():
    global _job, _handoff
    prefs = settings()
    if prefs is None:
        return 1.0
    if _job is None:
        if state['status'] == 'idle' and not bpy.app.background:
            if bpy.app.online_access:
                try:
                    start('check')
                except Exception as error:
                    state.update(status='error', message=str(error))
            else:
                state.update(status='offline', message='Online access is disabled in Blender.')
        return 1.0
    process, workspace, action, began = _job
    if process.poll() is None:
        if monotonic() - began < 300:
            return 0.2
        process.kill()
        process.wait()
    if bpy.context.window_manager.is_interface_locked:
        return 0.2
    _job = None
    handed_off = False
    try:
        response = workspace / 'response.json'
        if process.returncode or not response.is_file():
            raise ValueError('The update helper stopped. Check your connection and try again.')
        result = json.loads(response.read_text(encoding='utf-8'))
        if not result['ok']:
            raise ValueError(result['error'])
        release = result['release']
        if prefs.update_channel != release['channel']:
            invalidate()
        elif action == 'check':
            state.update(result['check'], release=release, channel=release['channel'])
        else:
            from ..preferences.addon.keymaps.deluxe_editor_ops import require_saved_draft
            require_saved_draft()
            _handoff = True
            state.update(status='installing', message='Reloading Blue Hole…')
            session = ReloadSession(ROOT, workspace / 'snapshot', release, workspace)
            handed_off = True
            session.begin()
    except Exception as error:
        _handoff = False
        state.update(status='error', message=str(error))
    finally:
        if not handed_off:
            shutil.rmtree(workspace)
    redraw()
    return None if handed_off else 1.0


def _purge_modules():
    for name in tuple(sys.modules):
        if name == MODULE or name.startswith(MODULE + '.'):
            del sys.modules[name]
    importlib.invalidate_caches()


def _disable():
    module = sys.modules.get(MODULE)
    registrar = getattr(module, 'keymaps_register', None)
    cleanup = getattr(registrar, 'drain_cleanup', lambda: True)
    errors = []
    if module is not None and getattr(module, '__addon_enabled__', False):
        addon_utils.disable(MODULE, default_set=False, handle_error=errors.append)
    elif module is not None and getattr(module, '_addon_registered', False):
        try:
            module.unregister()
        except Exception as error:
            errors.append(error)
    if errors:
        raise RuntimeError(f'Could not fully unload Blue Hole: {errors[0]}')
    return cleanup


def _enable():
    errors = []
    failed_modules = []
    def capture(error):
        errors.append(error)
        # Blender deletes the module after calling this hook on register failure.
        # Retain it so rollback can unregister partial classes/timers/keymaps.
        failed_modules.append(sys.modules.get(MODULE))
    addon_utils.enable(MODULE, default_set=False, persistent=True, handle_error=capture)
    if errors or not addon_utils.check(MODULE)[1]:
        for module in failed_modules:
            if module is not None:
                sys.modules.setdefault(MODULE, module)
        raise RuntimeError(f'Could not load Blue Hole: {errors[0] if errors else "addon remained disabled"}')


class ReloadSession(ReloadTransaction):
    """Timer wrapper survives removal of its defining module from sys.modules."""
    def __init__(self, root, snapshot, release, workspace):
        self.release, self.workspace = release, workspace
        super().__init__(service.Installation(root, snapshot, release, bpy.app.version),
                         disable=_disable, purge=_purge_modules, enable=_enable,
                         readiness=self.readiness, complete=self.report_complete)

    @staticmethod
    def readiness():
        module = sys.modules.get(MODULE)
        error = getattr(module, '_post_register_error', None)
        return bool(module and getattr(module, '_keymaps_registered', False)), error

    def begin(self):
        super().begin()
        if not self.done:
            bpy.app.timers.register(self.wait_ready, first_interval=0.1)

    def wait_ready(self):
        return self.tick()

    def report_complete(self, recovered=True):
        global _handoff
        _handoff = False
        self.done = True
        runtime = sys.modules.get(MODULE + '.blenderUtils.addon_updates')
        message = (f'Update failed; previous Blue Hole restored. {self.error}' if self.error and recovered else
                   f'Update failed. Close Blender before continuing. Recovery files: {self.workspace}. {self.error}'
                   if self.error else f'Blue Hole updated to {self.release["branch"]}.')
        if self.installation.cleanup_error:
            message += ' ' + self.installation.cleanup_error
        if recovered:
            try:
                shutil.rmtree(self.workspace)
            except OSError as error:
                message += f' Temporary files could not be removed: {error}'
        if runtime is not None:
            runtime.state.update(status='error' if self.error else 'current', message=message,
                                 channel=self.release['channel'], release=self.release)
        print(message)
        if not bpy.app.background:
            def draw(menu, _context):
                menu.layout.label(text=message)
            bpy.context.window_manager.popup_menu(draw, title='Blue Hole Update', icon='ERROR' if self.error else 'CHECKMARK')
        redraw()


def draw_update(layout, *, details=False):
    status = state['status']
    release = state['release']
    if status in {'checking', 'downloading', 'installing'}:
        row = layout.row()
        row.enabled = False
        row.label(text={'checking': 'Checking for Blue Hole updates…', 'downloading': 'Downloading Blue Hole update…',
                        'installing': 'Reloading Blue Hole…'}[status], icon='TIME')
        if status != 'installing':
            layout.operator('wm.bh_cancel_update', text='Cancel Update', icon='CANCEL')
    elif status in {'available', 'unverified', 'ahead', 'different'} and release:
        row = layout.row()
        row.enabled = not bool(state['blocked'])
        action = 'Update' if status == 'available' else 'Install'
        row.operator('wm.bh_update_addon', text=f'{action} Blue Hole · {release["version"]} ({release["channel"]})', icon='IMPORT')
    else:
        layout.operator('wm.bh_check_update', text='Blue Hole up to date · Check Again' if status == 'current'
                        else 'Check for Blue Hole Updates', icon='FILE_REFRESH')
    if details:
        prefs = settings()
        if prefs is not None:
            row = layout.row()
            row.enabled = _job is None and not _handoff
            row.prop(prefs, 'update_channel', text='Update channel')
        if release:
            layout.label(text=f'{release["branch"]} · {release["commit"][:12]}')
        for message in (state['message'], state['blocked']):
            import textwrap
            for line in textwrap.wrap(message, width=85):
                layout.label(text=line)
        if release and status not in {'checking', 'downloading', 'installing'}:
            layout.operator('wm.bh_check_update', text='Check for Updates', icon='FILE_REFRESH')


def register():
    if not bpy.app.timers.is_registered(poll):
        bpy.app.timers.register(poll, first_interval=5.0, persistent=True)


def unregister():
    if bpy.app.timers.is_registered(poll):
        bpy.app.timers.unregister(poll)
    _stop_job()
