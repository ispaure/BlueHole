"""Exercise Logistics legacy-to-extension upgrades and Deluxe Zen UV gestures.

All package installation, preferences and UI events use disposable resources.
The private commercial addon is supplied by the caller and is never bundled.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def native(output):
    import addon_utils
    import bmesh
    import bpy
    import traceback

    bpy.context.preferences.view.show_splash = False
    result = {'version': bpy.app.version_string, 'checks': {}}
    window = bpy.context.window_manager.windows[0]
    area = max(window.screen.areas, key=lambda item: item.width * item.height)
    state = {}
    def inside():
        region = next(item for item in area.regions if item.type == 'WINDOW')
        return bpy.context.temp_override(window=window, area=area, region=region)
    def send(key, **mods):
        region = next(item for item in area.regions if item.type == 'WINDOW')
        x, y = region.x + region.width // 3, region.y + region.height // 3
        window.event_simulate(type='MOUSEMOVE', value='NOTHING', x=x, y=y)
        window.event_simulate(type=key, value='PRESS', x=x, y=y, **mods)
        if not key.startswith('WHEEL'):
            window.event_simulate(type=key, value='RELEASE', x=x, y=y, **mods)
    def setup():
        bpy.context.preferences.use_preferences_save = False
        assert addon_utils.enable('bl_ext.logistics.ZenUV', default_set=True) is not None
        assert addon_utils.check('bl_ext.logistics.ZenUV')[1]
        addon = addon_utils.enable('bluehole_runtime', default_set=True)
        assert addon is not None
        addon._post_register_init()
        assert addon._keymaps_registered, addon._post_register_error
        assert bpy.ops.wm.bh_apply_deluxe_prefs() == {'FINISHED'}
        store = addon.keymaps_register.deluxe_profile()
        catalog = store.snapshot()
        preview = store.preview()
        state['store'] = store
        for id_, row in catalog['assignments'].items():
            command = catalog['commands'][row['command']]
            if command.get('provider') == 'Zen UV':
                status = store.registration_results().get(id_)
                result['checks'][command['operator']] = {'runtime': status, 'event': catalog['events'][row['event']]}
                assert preview['commands'][row['command']]['availability'] == 'available'
                assert status[0] == 'applied', status
        area.type = 'VIEW_3D'
        with inside():
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)
            bpy.ops.mesh.primitive_plane_add()
            state['mesh'] = bpy.context.object.data
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.context.scene.tool_settings.use_uv_select_sync = True
        area.ui_type = 'UV'
    def prepare_uv():
        with inside():
            bpy.context.preferences.addons['bl_ext.logistics.ZenUV'].preferences.trimsheet.mode = 'SCENE'
            owner = bpy.context.scene.zen_uv
            trim = owner.trimsheet.add()
            trim.name = 'Disposable test trim'
            trim.rect = (0.15, 0.85, 0.55, 0.45)
            owner.trimsheet_index = len(owner.trimsheet) - 1
            area.spaces.active.cursor_location = (0.4, 0.2)
            assert bpy.ops.uv.zenuv_move_cursor_to.poll()
            assert bpy.ops.uv.zenuv_fit_to_trim.poll()
    def check_cursor():
        location = list(area.spaces.active.cursor_location)
        result['checks']['cursor_input'] = location
        result['checks']['uv_context'] = {'area': area.type, 'ui_type': area.ui_type, 'mode': bpy.context.mode}
        assert location == [0.0, 1.0], location
    def bounds():
        bm = bmesh.from_edit_mesh(state['mesh'])
        uv = bm.loops.layers.uv.active
        coords = [tuple(loop[uv].uv) for face in bm.faces for loop in face.loops]
        return [min(p[0] for p in coords), min(p[1] for p in coords), max(p[0] for p in coords), max(p[1] for p in coords)]
    def before_fit():
        state['before'] = bounds()
    def check_fit():
        current = bounds()
        result['checks']['fit_input'] = {'before': state['before'], 'after': current}
        assert current != state['before']
        assert current[0] >= .15 - 1e-5 and current[1] >= .45 - 1e-5
        assert current[2] <= .55 + 1e-5 and current[3] <= .85 + 1e-5, current
    steps = iter((lambda: send('LEFTMOUSE'), lambda: send('ESC'), setup, prepare_uv,
                  lambda: send('WHEELLEFTMOUSE', ctrl=True, shift=True),
                  check_cursor, before_fit, lambda: send('MIDDLEMOUSE', ctrl=True, shift=True, alt=True), check_fit))
    def tick():
        try:
            step = next(steps, None)
            if step:
                step()
                return .7
            result['status'] = 'passed'
        except BaseException:
            result.update(status='failed', error=traceback.format_exc())
        finally:
            (output / 'native.json').write_text(json.dumps(result, indent=2) + '\n')
        addon_utils.disable('bluehole_runtime', default_set=True)
        addon_utils.disable('bl_ext.logistics.ZenUV', default_set=True)
        bpy.ops.wm.quit_blender()
    bpy.app.timers.register(tick, first_interval=1.5)


def launch(args):
    sys.path.insert(0, str(args.logistics_source / 'Python'))
    from features.blender.presets.manager import BlenderManager
    from features.blender.addons.library import AddonLibrary
    from blender_keymap_runtime import stage_package

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix='zenuv-check-', dir=output) as temporary:
        root = Path(temporary)
        release = SimpleNamespace(version=args.version, platform='macos-arm64')
        manager = BlenderManager(root)
        manager.executable = lambda _release: args.blender.resolve()
        preset = manager.create_preset(release, 'Disposable')
        library = AddonLibrary(manager, provided_root=args.library)
        old_entries = [entry for entry in library.entries() if entry.identity == 'legacy:ZenUV']
        assert old_entries, 'Supply the old Zen UV package to exercise the upgrade'
        policy = root / 'confinement.sb'
        policy.write_text('(version 1)\n(allow default)\n(deny network*)\n(deny file-write*)\n'
                          '(allow file-write* (subpath ' + json.dumps(str(output)) + '))\n'
                          '(allow file-write* (literal "/dev/null"))\n')
        popen = subprocess.Popen
        def confined(command, *positional, **kwargs):
            if str(command[0]) == str(args.blender.resolve()):
                command = ['/usr/bin/sandbox-exec', '-f', str(policy), *command]
            return popen(command, *positional, **kwargs)
        disabled = {'enabled': False, 'branch': 'main', 'deluxe': False}
        with patch.object(subprocess, 'Popen', confined):
            with patch.object(AddonLibrary, 'entries', return_value=old_entries):
                library.apply(release, 'Disposable', ['legacy:ZenUV'], bluehole=disabled)
            assert (preset / 'scripts/addons/ZenUV').is_dir()
            # Same operation invoked by Logistics' Launch button for an existing preset.
            library.apply(release, 'Disposable', library.selection(preset)['selected'], bluehole=disabled)
            state = library.selection(preset)
            installed = state['installed']['extension:ZenUV']
            assert installed['version'] == '5.4.0', installed
            assert installed['module'] == 'bl_ext.logistics.ZenUV'
            assert not (preset / 'scripts/addons/ZenUV').exists()
            assert not (preset / 'scripts/presets/keyconfig/BH_Keymaps.py').exists()
            (output / 'upgrade.json').write_text(json.dumps({'status': 'passed', 'installed': installed,
                                                           'selected': state['selected']}, indent=2))
            stage_package(preset, (4, 5, 1) if args.version == '4.5.1' else None)
            env = manager.environment(release, 'Disposable')
            env.pop('PYTHONPATH', None)
            env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1', BLUEHOLE_ZENUV_OUTPUT=str(output))
            for key, name in (('TMPDIR', 'tmp'), ('XDG_CACHE_HOME', 'cache')):
                folder = root / name
                folder.mkdir()
                env[key] = str(folder)
            command = [str(args.blender.resolve()), '--offline-mode', '--disable-autoexec', '--enable-event-simulate',
                       '--python-exit-code', '1', '--python', str(Path(__file__).resolve())]
            with (output / 'blender.log').open('w') as log:
                subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=120, check=True)
        result = json.loads((output / 'native.json').read_text())
        print(json.dumps(result, indent=2))
        return int(result['status'] != 'passed')


if __name__ == '__main__':
    if 'BLUEHOLE_ZENUV_OUTPUT' in os.environ:
        native(Path(os.environ['BLUEHOLE_ZENUV_OUTPUT']))
    else:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--blender', type=Path, required=True)
        parser.add_argument('--version', required=True)
        parser.add_argument('--logistics-source', type=Path, required=True)
        parser.add_argument('--library', type=Path, required=True)
        parser.add_argument('--output', type=Path, required=True)
        raise SystemExit(launch(parser.parse_args()))
