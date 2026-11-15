"""Nonblocking update checks and main-thread addon unload/swap/reload."""
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic

import addon_utils
import bpy

from . import update_service as service

ROOT = Path(__file__).absolute().parents[1]
MODULE = __package__.split('.')[0]
state = {'status': 'idle', 'message': '', 'release': None, 'channel': None}
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
        blocker = service.install_blocker(ROOT)
        if blocker:
            raise ValueError(blocker)
        if not state['release'] or state['channel'] != channel:
            raise ValueError('Check for updates in the selected channel first')
    workspace = TemporaryDirectory(prefix='.bluehole-update-', dir=ROOT.parent if action == 'install' else None)
    folder = Path(workspace.name)
    request = {'action': 'check' if action == 'check' else 'stage', 'channel': channel,
               'blender_version': list(bpy.app.version), 'workspace': str(folder), 'release': state['release']}
    (folder / 'request.json').write_text(json.dumps(request), encoding='utf-8')
    try:
        with (folder / 'worker.log').open('wb') as output:
            process = subprocess.Popen([sys.executable, *bpy.app.python_args,
                str(ROOT / 'blenderUtils/update_worker.py'), str(folder / 'request.json'), str(folder / 'response.json')],
                stdin=subprocess.DEVNULL, stdout=output, stderr=output,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    except Exception:
        workspace.cleanup()
        raise
    _job = (process, workspace, action, monotonic())
    state.update(status='checking' if action == 'check' else 'downloading', channel=channel, message='')
    redraw()


def invalidate(_self=None, _context=None):
    # A channel change invalidates a checked commit; never install the previous
    # channel's candidate after the user changes this preference.
    if _job is None and not _handoff:
        state.update(status='idle', release=None, channel=None, message='')


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
        response = Path(workspace.name) / 'response.json'
        if process.returncode or not response.is_file():
            raise ValueError('The update helper stopped. Check your connection and try again.')
        result = json.loads(response.read_text(encoding='utf-8'))
        if not result['ok']:
            raise ValueError(result['error'])
        release = result['release']
        if prefs.update_channel != release['channel']:
            invalidate()
        elif action == 'check':
            current = service.installed_commit(ROOT)
            state.update(status='current' if current == release['commit'] else 'available',
                         release=release, channel=release['channel'], message=service.install_blocker(ROOT))
        else:
            _handoff = True
            state.update(status='installing', message='Reloading Blue Hole…')
            session = ReloadSession(ROOT, Path(workspace.name) / 'snapshot', release, workspace)
            handed_off = True
            session.begin()
    except Exception as error:
        _handoff = False
        state.update(status='error', message=str(error))
    finally:
        if not handed_off:
            workspace.cleanup()
    redraw()
    return None if handed_off else 1.0


def _purge_modules():
    for name in tuple(sys.modules):
        if name == MODULE or name.startswith(MODULE + '.'):
            del sys.modules[name]
    importlib.invalidate_caches()


def _disable():
    module = sys.modules.get(MODULE)
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


def _enable():
    errors = []
    addon_utils.enable(MODULE, default_set=False, persistent=True, handle_error=errors.append)
    if errors or not addon_utils.check(MODULE)[1]:
        raise RuntimeError(f'Could not load Blue Hole: {errors[0] if errors else "addon remained disabled"}')


class ReloadSession:
    """This timer object survives removal of its defining module from sys.modules."""
    def __init__(self, root, snapshot, release, workspace):
        self.installation = service.Installation(root, snapshot, release, bpy.app.version)
        self.release, self.workspace = release, workspace
        self.deadline = monotonic() + 30
        self.error = ''
        self.restoring = False
        self.done = False

    def begin(self):
        try:
            self.installation.prepare()
        except Exception as error:
            self.error = str(error)
            self.complete()
            return
        try:
            _disable()
            self.installation.publish()
            _purge_modules()
            _enable()
        except Exception as error:
            self.rollback(error)
        if not self.done:
            bpy.app.timers.register(self.wait_ready, first_interval=0.1)

    def wait_ready(self):
        module = sys.modules.get(MODULE)
        error = getattr(module, '_post_register_error', None)
        if module is not None and getattr(module, '_keymaps_registered', False) and not error:
            try:
                if not self.restoring:
                    self.installation.finish()
                self.complete()
            except Exception as failure:
                self.rollback(failure)
            return None if self.done else 0.1
        if error or monotonic() >= self.deadline:
            self.rollback(RuntimeError(error or 'Blue Hole initialization timed out'))
            return None if self.done else 0.1
        return 0.1

    def rollback(self, error):
        self.error = str(error)
        if self.restoring:
            self.complete(recovered=False)
            return
        self.restoring = True
        try:
            _disable()
            self.installation.rollback()
            _purge_modules()
            _enable()
            self.deadline = monotonic() + 30
        except Exception as recovery:
            # Restore files even when an incomplete registration could not be
            # unloaded. Keep recovery evidence if either operation fails.
            try:
                self.installation.rollback()
            except Exception as restore_error:
                self.error += f'; file recovery: {restore_error}'
            self.error += f'; reload recovery: {recovery}'
            self.complete(recovered=False)

    def complete(self, recovered=True):
        global _handoff
        _handoff = False
        self.done = True
        runtime = sys.modules.get(MODULE + '.blenderUtils.addon_updates')
        message = (f'Update failed; previous Blue Hole restored. {self.error}' if self.error and recovered else
                   f'Update failed. Restart Blender before continuing. Recovery files: {self.workspace.name}. {self.error}'
                   if self.error else f'Blue Hole updated to {self.release["branch"]}.')
        if runtime is not None:
            runtime.state.update(status='error' if self.error else 'current', message=message,
                                 channel=self.release['channel'], release=self.release)
        if recovered:
            try:
                self.workspace.cleanup()
            except OSError as error:
                message += f' Temporary files could not be removed: {error}'
        else:
            # TemporaryDirectory must not remove a recovery backup on GC.
            self.workspace._finalizer.detach()
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
    elif status == 'available' and release:
        row = layout.row()
        row.enabled = not bool(state['message'])
        row.operator('wm.bh_update_addon', text=f'Update Blue Hole · {release["version"]} ({release["channel"]})', icon='IMPORT')
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
        if state['message']:
            import textwrap
            for line in textwrap.wrap(state['message'], width=85):
                layout.label(text=line)
        if status in {'available', 'current'}:
            layout.operator('wm.bh_check_update', text='Check for Updates', icon='FILE_REFRESH')


def register():
    if not bpy.app.timers.is_registered(poll):
        bpy.app.timers.register(poll, first_interval=5.0, persistent=True)


def unregister():
    global _job
    if bpy.app.timers.is_registered(poll):
        bpy.app.timers.unregister(poll)
    if _job is not None:
        process, workspace, *_ = _job
        if process.poll() is None:
            process.kill()
            process.wait()
        workspace.cleanup()
        _job = None
