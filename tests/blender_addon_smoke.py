"""Native Blender fixture validation without changing installed preferences/projects."""
import argparse
import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile
import stat
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]


def launch(binary, minimum=None, package_archive=None):
    with TemporaryDirectory(prefix='bluehole-native-') as temporary:
        root = Path(temporary)
        environment = dict(os.environ)
        environment.pop('PYTHONPATH', None)
        environment['PYTHONNOUSERSITE'] = '1'
        for key in ('RESOURCES', 'CONFIG', 'SCRIPTS', 'EXTENSIONS', 'DATAFILES'):
            folder = root / key.lower()
            folder.mkdir()
            environment['BLENDER_USER_' + key] = str(folder)
        package = root / 'scripts/addons/bluehole_health'
        package.mkdir(parents=True)
        if package_archive:
            if minimum is not None:
                raise ValueError('Exact-package acceptance cannot override Blender compatibility.')
            extract_package(package_archive, package)
        else:
            names = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '-z']).decode().split('\0')
            for name in filter(None, names):
                if name.startswith(('tests/', '.github/')):
                    continue
                source = ROOT / name
                if source.is_symlink() or not source.is_file():
                    raise RuntimeError('Expected a regular tracked file: ' + name)
                destination = package / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
        if minimum is not None:
            initializer = package / '__init__.py'
            text = initializer.read_text()
            tree = ast.parse(text)
            info = next(node.value for node in tree.body if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == 'bl_info' for target in node.targets))
            entry = next(value for key, value in zip(info.keys, info.values) if ast.literal_eval(key) == 'blender')
            lines = text.splitlines(keepends=True)
            assert entry.lineno == entry.end_lineno
            line = lines[entry.lineno - 1]
            lines[entry.lineno - 1] = line[:entry.col_offset] + repr(minimum) + line[entry.end_col_offset:]
            initializer.write_text(''.join(lines))
        return subprocess.run([str(binary), '--background', '--factory-startup', '--disable-autoexec',
                               '--python-exit-code', '1', '--python', str(Path(__file__).resolve()),
                               '--', '--fixture-root', str(root)],
                              env=environment, timeout=120).returncode


def extract_package(archive_path, destination):
    from pathlib import PurePosixPath
    with zipfile.ZipFile(archive_path) as archive:
        rows = archive.infolist()
        if len(rows) > 20000 or sum(row.file_size for row in rows) > 256 * 1024 * 1024:
            raise ValueError('Native package fixture exceeds bounded extraction limits.')
        if len({row.filename for row in rows}) != len(rows):
            raise ValueError('Native package contains duplicate members.')
        for row in rows:
            name = PurePosixPath(row.filename)
            kind = stat.S_IFMT(row.external_attr >> 16)
            if (name.is_absolute() or '..' in name.parts or '\\' in row.filename
                    or not name.parts or name.parts[0] != 'BlueHole' or kind not in (0, stat.S_IFREG, stat.S_IFDIR)):
                raise ValueError('Unsafe native package member: ' + row.filename)
            target = destination.joinpath(*name.parts[1:])
            if row.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(row))


def main(root):
    import addon_utils
    import bpy
    import importlib
    import builtins
    import dis
    import inspect
    import types
    from unittest.mock import patch

    root = root.resolve()
    for key in ('RESOURCES', 'CONFIG', 'SCRIPTS', 'EXTENSIONS', 'DATAFILES'):
        assert Path(os.environ['BLENDER_USER_' + key]).resolve().is_relative_to(root)
    assert Path(bpy.utils.resource_path('USER')).resolve().is_relative_to(root)
    sys.path.insert(0, str(root / 'scripts/addons'))
    bpy.utils.refresh_script_paths()
    name = 'bluehole_health'
    phases = []
    errors = []
    handler_lists = [bpy.app.handlers.load_pre, bpy.app.handlers.load_post,
                     bpy.app.handlers.save_pre, bpy.app.handlers.save_post]
    handlers_before = [list(handlers) for handlers in handler_lists]

    def keymap_count():
        configuration = bpy.context.window_manager.keyconfigs.addon
        return sum(len(keymap.keymap_items) for keymap in configuration.keymaps) if configuration else 0

    keymaps_before = keymap_count()

    def inspect_globals(function):
        if not inspect.isfunction(function):
            return
        def inspect_code(code):
            for instruction in dis.get_instructions(code):
                if instruction.opname == 'LOAD_GLOBAL':
                    assert instruction.argval in function.__globals__ or hasattr(builtins, instruction.argval), (
                        function.__module__, code.co_name, instruction.argval)
            for value in code.co_consts:
                if isinstance(value, types.CodeType):
                    inspect_code(value)
        inspect_code(function.__code__)

    def fail(*args):
        import traceback
        errors.append(traceback.format_exc())

    for cycle in range(2):
        module = addon_utils.enable(name, default_set=True, persistent=False, handle_error=fail)
        assert module is not None and not errors, errors
        logging = importlib.import_module(name + '.Lib.commonUtils.runtime.diagnostics')
        with logging.noninteractive_logging():
            module._post_register_init()
            preferences = importlib.import_module(name + '.preferences.prefs').prefs()
            assert preferences.is_ready()
            assert bpy.app.timers.is_registered(module.update_env_timer)
            operator_type = importlib.import_module(name + '.operators.export_send_ops').BH_OT_export_containers
            assert operator_type.is_registered
            runtime = importlib.import_module(name + '.Lib.commonUtils.integrations.wrappers.perforce.runtime').runtime()
            adapter = importlib.import_module(name + '.wrappers.perforce')
            assert runtime.environment is adapter._environment
            settings = preferences.sourcecontrol
            settings.source_control_enable = True
            settings.source_control_solution = 'perforce'
            settings.win32_env_override = True
            for prefix in ('win32', 'macos', 'linux'):
                for key in ('p4user', 'p4port', 'p4client'):
                    setattr(settings, f'{prefix}_env_setting_{key}', f'{prefix}-{key}')
            for platform, prefix in ((adapter.OS.WIN, 'win32'), (adapter.OS.MAC, 'macos'), (adapter.OS.LINUX, 'linux')):
                with patch.object(adapter, 'get_os', return_value=platform):
                    assert adapter._environment() == {key: f'{prefix}-{key.lower()}' for key in ('P4USER', 'P4PORT', 'P4CLIENT')}
            settings.source_control_enable = False
            for module_name, loaded in list(sys.modules.items()):
                if not module_name.startswith(name + '.') or '.Lib.' in module_name:
                    continue
                for value in list(vars(loaded).values()):
                    if not getattr(value, '__module__', '').startswith(name + '.'):
                        continue
                    inspect_globals(value)
                    if inspect.isclass(value):
                        for member in vars(value).values():
                            if isinstance(member, (staticmethod, classmethod)):
                                member = member.__func__
                            if isinstance(member, property):
                                for accessor in (member.fget, member.fset, member.fdel):
                                    inspect_globals(accessor)
                            else:
                                inspect_globals(member)
            phases.append('registration/preferences/Perforce cycle ' + str(cycle + 1))

            if cycle == 0:
                bpy.ops.object.select_all(action='SELECT')
                bpy.ops.object.delete(use_global=False)
                bpy.ops.mesh.primitive_cube_add(location=(1, 2, 3))
                cube = bpy.context.object
                cube.name = 'SM_HealthFixture'
                bpy.ops.wm.save_as_mainfile(filepath=str(root / 'fixture.blend'))
                phases.append('save callbacks with source control disabled')
                model = importlib.import_module(name + '.blenderUtils.export.exportSettings')
                container_type = importlib.import_module(name + '.blenderUtils.export.assetMesh.container').AssetMeshContainer
                for export_format in ('FBX', 'GLB'):
                    options = model.ExportSettings(name='Health fixture', exp_dir=root / 'exports',
                        exp_format=export_format, zero_root_transform=True,
                        include_render=True, include_collision=False, include_socket=False,
                        axis_up='Z', axis_fwd='-Y', mesh_smooth_type='OFF', bake_anim=False,
                        apply_scale_options='FBX_SCALE_NONE', rename_collisions_for_ue=False,
                        use_mesh_modifiers=True, engine=model.Engine.UNDEFINED)
                    container = container_type(cube, options)
                    assert container.export_proc(), export_format
                    assert container.path.is_file() and container.path.stat().st_size > 0
                    assert tuple(cube.location) == (1, 2, 3)
                    phases.append(export_format + ' asset-mesh export/transform restoration')
        addon_utils.disable(name, default_set=True, handle_error=fail)
        assert not errors, errors
        assert not bpy.app.timers.is_registered(module.update_env_timer)
        assert not bpy.app.timers.is_registered(module._post_register_init)
        assert not operator_type.is_registered
        assert not bpy.context.preferences.addons.get(name)
        assert [list(handlers) for handlers in handler_lists] == handlers_before
        assert keymap_count() == keymaps_before
        phases.append('unregister cleanup cycle ' + str(cycle + 1))
    print(json.dumps({'blender': bpy.app.version_string, 'python': sys.version.split()[0],
                      'shared': (ROOT / 'Lib/commonUtils.revision').read_text().strip(),
                      'registration_tested': True, 'phases': phases}))


if __name__ == '__main__':
    if '--blender' in sys.argv:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--blender', type=Path, required=True)
        parser.add_argument('--package', type=Path, help='Install these exact packaged bytes into the isolated fixture')
        parser.add_argument('--test-minimum-version', help='Override only the temporary copy, for an explicitly chosen older Blender')
        args = parser.parse_args()
        minimum = tuple(map(int, args.test_minimum_version.split('.'))) if args.test_minimum_version else None
        if minimum is not None and len(minimum) != 3:
            parser.error('Use a three-part minimum version')
        raise SystemExit(launch(args.blender.resolve(strict=True), minimum, args.package))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture-root', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    main(args.fixture_root)
