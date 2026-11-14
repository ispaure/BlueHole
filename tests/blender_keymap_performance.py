"""Measure Deluxe lifecycle in an isolated Blender GUI with factory preferences.

Run with --blender /path/to/Blender --output test-results/keymap-performance.
Timings include synchronous merged-keymap updates, but exclude application startup.
"""

import argparse
import cProfile
import hashlib
import importlib
import json
import os
from pathlib import Path
import pstats
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
import traceback
from types import MethodType, SimpleNamespace


def exercise(output):
    import addon_utils
    import bpy

    report = {'version': bpy.app.version_string, 'build': bpy.app.build_hash.decode()}
    try:
        bpy.context.preferences.use_preferences_save = False
        sys.path.insert(0, str(Path(os.environ['BLENDER_USER_SCRIPTS']) / 'addons'))
        bpy.utils.refresh_script_paths()
        module = addon_utils.enable('bluehole_runtime', default_set=True, persistent=False)
        assert module is not None
        module._post_register_init()
        registrar = importlib.import_module('bluehole_runtime.keymaps.keymaps_register')
        runtime = registrar.keymap_utils
        prefs = bpy.context.preferences.addons['bluehole_runtime'].preferences
        registrar.unregister()
        prefs.keymap['deluxe_configured'] = True
        prefs.keymap['enable_keymaps'] = True
        configs = bpy.context.window_manager.keyconfigs

        def source_state():
            return [(km.name, [(item.id, item.idname, item.type, item.value, item.active)
                               for item in km.keymap_items]) for km in configs.addon.keymaps]

        def merged_digest():
            rows = []
            for km in configs.user.keymaps:
                for item in km.keymap_items:
                    try:
                        rows.append((runtime.capture_scope(km), runtime._snapshot(item, km.is_modal)))
                    except runtime._Pending:
                        pass
            return hashlib.sha256(repr(rows).encode()).hexdigest()

        initial = source_state()
        merged_before = merged_digest()
        calls = []
        update = runtime._update_merged

        def counted_update():
            started = time.perf_counter()
            try:
                return update()
            finally:
                calls.append(time.perf_counter() - started)

        runtime._update_merged = counted_update

        def measure(action):
            calls.clear()
            started = time.perf_counter()
            action()
            elapsed = time.perf_counter() - started
            return {'seconds': elapsed, 'merged_updates': len(calls),
                    'merged_update_seconds': sum(calls), 'runtime': runtime.runtime_stats()}

        cycles = []
        registered_digest = None
        for _ in range(3):
            loaded = measure(registrar.register)
            digest = merged_digest()
            if registered_digest is not None:
                assert digest == registered_digest, 'Repeated registration changed merged bindings'
            registered_digest = digest
            unloaded = measure(registrar.unregister)
            assert source_state() == initial, 'Unloading changed foreign add-on rows'
            assert merged_digest() == merged_before, 'Unloading changed merged bindings'
            assert unloaded['runtime']['tracked_resources'] == 0
            assert unloaded['runtime']['features'] == 0
            cycles.append({'load': loaded, 'unload': unloaded})
        for label, action in (('load', registrar.register), ('unload', registrar.unregister)):
            profile = cProfile.Profile()
            profile.runcall(action)
            with (output / (label + '-profile.txt')).open('w') as stream:
                pstats.Stats(profile, stream=stream).strip_dirs().sort_stats('cumulative').print_stats(35)
        registrar.register()
        toggles = []
        for _ in range(3):
            prefs.keymap['enable_keymaps'] = False
            disabled = measure(registrar.refresh)
            assert disabled['runtime']['owned'] == 2  # Required Save As bindings.
            prefs.keymap['enable_keymaps'] = True
            enabled = measure(registrar.refresh)
            assert merged_digest() == registered_digest
            toggles.append({'enable': enabled, 'disable': disabled})

        # Former preference switches cannot silently override the JSON choices.
        prefs.keymap['navigation'] = {'enable_navigation_keymaps': False, 'enable_navigation_view_framing': False}
        registrar.refresh()
        assert merged_digest() == registered_digest
        assert prefs.keymap.bl_rna.properties['enable_keymaps'].name == 'Enable Deluxe Keymaps'

        section = 'navigation.view_framing'
        catalog_path = registrar.deluxe_profile().path
        def catalog_revision():
            return registrar.deluxe_profile()._disk_revision()
        before_edit = catalog_revision()
        editor_ops = importlib.import_module('bluehole_runtime.preferences.addon.keymaps.deluxe_editor_ops')

        def checkbox(table, target):
            current = editor_ops.editor()
            return editor_ops.inline_value(editor_ops.state(bpy.context), 'enabled', 'boolean',
                                           current.catalog[table][target].get('enabled', True),
                                           table=table, entry=target)

        for table, target in (('sections', section), ('categories', 'pie')):
            checkbox(table, target).boolean = False
            assert not editor_ops.editor().catalog[table][target]['enabled']
        assert catalog_revision() == before_edit, 'Draft toggles wrote the catalog'
        assert not editor_ops.editor().preview_error, editor_ops.editor().preview_error
        assert not registrar.deluxe_section_enabled(section), 'Draft did not preview in live keymaps'
        assert bpy.ops.wm.bh_deluxe_edit(action='discard') == {'FINISHED'}
        for table, target in (('sections', section), ('categories', 'pie')):
            assert checkbox(table, target).boolean, 'Discard did not reset a checkbox'
            checkbox(table, target).boolean = False
        assert bpy.ops.wm.bh_deluxe_edit(action='apply') == {'FINISHED'}
        saved = catalog_revision()
        catalog = registrar.deluxe_profile().snapshot()
        assert not catalog['sections'][section]['enabled']
        assert not catalog['categories']['pie']['enabled']
        registrar.unregister()
        registrar.register()
        assert not registrar.deluxe_section_enabled(section)
        assert not registrar.deluxe_section_enabled('pie.menus')
        prefs.keymap['enable_keymaps'] = False
        registrar.refresh()
        prefs.keymap['enable_keymaps'] = True
        registrar.refresh()
        assert not registrar.deluxe_section_enabled(section)
        assert catalog_revision() == saved
        for table, target in (('sections', section), ('categories', 'pie')):
            checkbox(table, target).boolean = True
        assert bpy.ops.wm.bh_deluxe_edit(action='apply') == {'FINISHED'}
        assert merged_digest() == registered_digest

        # Browse by section/context, then reach all uses without hidden filters.
        current = editor_ops.editor()
        view = editor_ops.state(bpy.context)
        assert set(view.bl_rna.properties['tab'].enum_items.keys()) == {'BINDINGS', 'COMMANDS'}
        assert current.binding_all
        bpy.ops.wm.bh_deluxe_edit(action='feature_category', target='navigation')
        view.search = 'narrow search'
        scope = next(scope for scope in current.binding_contexts().values() if scope['name'] == '3D View')
        picker = SimpleNamespace(choice_key='')
        popup_context = SimpleNamespace(window_manager=SimpleNamespace(invoke_search_popup=lambda _: None))
        assert editor_ops.BH_OT_deluxe_filter_context.invoke(picker, popup_context, None) == {'INTERFACE'}
        picker.context = editor_ops.context_id(scope)
        editor_ops.BH_OT_deluxe_filter_context.stage(picker, current)
        assert all(row['scope']['name'] == '3D View' and
                   current.catalog['sections'][row['section']]['category'] == 'navigation'
                   for row in current.catalog['assignments'].values() if current.accepts_binding(row))
        editor_ops.EditorOperator.release_choices(picker)
        shared_command = next(id_ for id_ in current.catalog['commands'] if len(current.draft.uses('commands', id_)) > 1)
        bpy.ops.wm.bh_deluxe_edit(action='command_bindings', target=shared_command)
        assert view.search == '' and current.binding_context == '' and current.binding_all
        assert {id_ for id_, row in current.catalog['assignments'].items() if current.accepts_binding(row)} == set(
            current.draft.uses('commands', shared_command))
        bpy.ops.wm.bh_deluxe_edit(action='all_bindings')

        # Exercise the actual dialog operators with live RNA and keymaps.
        saved = catalog_revision()
        dialog_context = SimpleNamespace(window_manager=SimpleNamespace(
            keyconfigs=configs, invoke_props_dialog=lambda *_args, **_kwargs: {'RUNNING_MODAL'}))
        command_type = editor_ops.BH_OT_deluxe_command
        new_command = SimpleNamespace(source='', choice_key='')
        new_command._choices_first = MethodType(command_type._choices_first, new_command)
        assert command_type.invoke(new_command, dialog_context, None) == {'RUNNING_MODAL'}
        new_command.operator_id, new_command.label = 'view3d.view_selected', 'Test shared frame'
        command_type.stage(new_command, current)
        command_id = current.command
        assert view.tab == 'COMMANDS' and not current.draft.uses('commands', command_id)
        editor_ops.EditorOperator.release_choices(new_command)
        duplicate = SimpleNamespace(source=command_id, choice_key='')
        assert command_type.invoke(duplicate, dialog_context, None) == {'RUNNING_MODAL'}
        command_type.stage(duplicate, current)
        copy_id = current.command
        assert current.catalog['commands'][copy_id]['label'] == 'Test shared frame Copy'
        current.remove_command(copy_id)
        current.draft.put('events', 'test-command-event',
                          dict(type='F24', ctrl=True, shift=True, alt=True, oskey=True))
        current.changed()
        mappings = []
        for scope_name in ('3D View', 'Image'):
            mapping = SimpleNamespace(assignment='', command_hint=command_id, choice_key='')
            assert editor_ops.BH_OT_deluxe_mapping.invoke(mapping, dialog_context, None) == {'RUNNING_MODAL'}
            assert mapping.command == command_id
            mapping.event_id = 'test-command-event'
            mapping.section = 'navigation.view_framing'
            mapping.scope_id = next(id_ for id_, scope in mapping._scopes.items() if scope['name'] == scope_name)
            editor_ops.BH_OT_deluxe_mapping.stage(mapping, current)
            mappings.append(mapping.assignment)
            assert view.tab == 'BINDINGS' and current.assignment == mapping.assignment
            editor_ops.EditorOperator.release_choices(mapping)
        view.command_edit_scope = 'SINGLE'
        control = editor_ops.inline_value(view, 'use_all_regions', 'boolean', False,
                                         command=command_id, assignment=mappings[0])
        control.boolean = True
        clone = current.catalog['assignments'][mappings[0]]['command']
        assert clone != command_id
        assert 'use_all_regions' not in current.catalog['commands'][command_id]['properties']
        control.boolean = False
        assert current.catalog['assignments'][mappings[0]]['command'] == clone
        current.draft.update('assignments', mappings[0], command=command_id)
        current.changed()
        view.command_edit_scope = 'SHARED'
        editor_ops.inline_value(view, 'use_all_regions', 'boolean', False,
                               command=command_id, assignment=mappings[0]).boolean = True
        assert all(current.catalog['assignments'][id_]['command'] == command_id for id_ in mappings)
        assert current.catalog['commands'][command_id]['properties']['use_all_regions']
        assert not current.preview_error, current.preview_error
        assert catalog_revision() == saved, 'Creating/editing commands saved JSON before Apply'
        current.discard()
        view.command_edit_scope = 'SINGLE'
        bpy.ops.wm.bh_deluxe_edit(action='all_bindings')
        assert merged_digest() == registered_digest
        report.update(binding_filters_verified=True, command_library_verified=True,
                      single_and_shared_command_preview_verified=True)

        # Live changes fork a shared event without changing the saved JSON.
        current = editor_ops.editor()
        assignment = 'other-screen-c7515cc97075'
        original_event = current.catalog['assignments'][assignment]['event']
        def event_field(field, prop, value, items=()):
            data = current.catalog['events'][current.catalog['assignments'][assignment]['event']]
            control = editor_ops.inline_value(editor_ops.state(bpy.context), field, prop,
                                               data.get(field, 'KEYBOARD' if field == 'map_type' else False),
                                               assignment=assignment, items=items)
            setattr(control, prop, value)
            assert not current.preview_error, current.preview_error

        saved = catalog_revision()
        event_field('repeat', 'boolean', False)
        assert current.catalog['events'][original_event]['repeat']
        assert not next(item for item in configs.user.keymaps['Screen'].keymap_items
                        if item.idname == 'screen.repeat_last' and item.type == 'G').repeat
        event_field('map_type', 'option', 'MOUSE', editor_ops.INPUT_TYPES)
        assert next(item for item in configs.addon.keymaps['Screen'].keymap_items
                    if item.idname == 'screen.repeat_last').map_type == 'MOUSE'
        event_field('map_type', 'option', 'KEYBOARD', editor_ops.INPUT_TYPES)
        assert catalog_revision() == saved
        current.discard()
        assert merged_digest() == registered_digest

        # Capturing a different keyboard key retains Repeat and does not save.
        capture_type = editor_ops.BH_OT_deluxe_capture
        capture = SimpleNamespace(assignment=assignment, shared=False)
        for name in ('run', 'cancel'):
            setattr(capture, name, MethodType(getattr(capture_type, name), capture))
        capture.report = lambda _level, message: report.update(operator_error=message)
        capture_context = SimpleNamespace(area=bpy.context.area, window_manager=SimpleNamespace(
            windows=bpy.context.window_manager.windows, modal_handler_add=lambda _operator: None))
        assert capture_type.execute(capture, capture_context) == {'RUNNING_MODAL'}
        assert capture_type.modal(capture, bpy.context, SimpleNamespace(type='H', value='PRESS',
            shift=False, ctrl=False, alt=False, oskey=False)) == {'FINISHED'}, report.get('operator_error')
        captured = current.catalog['events'][current.catalog['assignments'][assignment]['event']]
        assert captured['type'] == 'H' and captured['repeat']
        assert not current.preview_error, current.preview_error
        assert catalog_revision() == saved
        current.discard()
        assert merged_digest() == registered_digest

        # Disable an exact inherited default, test draft/commit/unload restoration.
        source = configs.default.keymaps['Object Mode']
        item = next(item for item in source.keymap_items
                    if item.idname == 'object.select_all' and item.type == 'A'
                    and item.properties.action == 'SELECT')
        candidate = editor_ops.resolver.capture_candidate(source, item, 'default')
        assert candidate['can_disable'], candidate
        current.feature_category, current.feature_section = 'selection', 'selection.all_none'
        merged_map = configs.user.keymaps['Object Mode']
        user_item = merged_map.keymap_items.from_id(item.id)
        menu_entries = []
        class MenuLayout:
            def separator(self):
                pass
            def operator(self, idname, **kwargs):
                props = SimpleNamespace()
                menu_entries.append((idname, props))
                return props
        native_context = SimpleNamespace(button_pointer=user_item, keymap=merged_map)
        editor_ops.draw_binding_context(SimpleNamespace(layout=MenuLayout()), native_context)
        operator_id, properties = menu_entries[0]
        assert operator_id == editor_ops.BH_OT_deluxe_stage_binding.bl_idname
        operation_type = editor_ops.BH_OT_deluxe_stage_binding
        operation = SimpleNamespace(rule='', use_replacement=False, **vars(properties))
        for name in ('selected', 'run', 'release_choices'):
            setattr(operation, name, MethodType(getattr(operation_type, name), operation))
        operation.report = lambda _level, message: report.update(operator_error=message)
        dialog_context = SimpleNamespace(window_manager=SimpleNamespace(
            keyconfigs=configs, invoke_props_dialog=lambda *_args, **_kwargs: {'RUNNING_MODAL'}))
        assert operation_type.invoke(operation, dialog_context, None) == {'RUNNING_MODAL'}
        assert operation.disable_binding
        assert operation_type.execute(operation, bpy.context) == {'FINISHED'}, report.get('operator_error')
        rule, = current.catalog['suppressions']
        assert not current.preview_error, current.preview_error
        assert not item.active, 'Default disable did not preview'
        user_item = configs.user.keymaps['Object Mode'].keymap_items.from_id(item.id)
        assert not user_item.active and not user_item.is_user_modified
        assert current.preview()['suppressions'][rule]['registered']
        assert catalog_revision() == saved
        # Save only this disposable profile while preview is active; a second
        # Blender process checks that no disabled user-keymap delta leaked out.
        bpy.ops.wm.save_userpref()
        menu_entries.clear()
        native_context.button_pointer = configs.user.keymaps['Object Mode'].keymap_items.from_id(item.id)
        native_context.keymap = configs.user.keymaps['Object Mode']
        editor_ops.draw_binding_context(SimpleNamespace(layout=MenuLayout()), native_context)
        assert menu_entries[0][1].action == 'restore_default'
        current.discard()
        assert item.active
        rule = current.draft.stage_suppression('selection.all_none', source, item, 'default', disable=True)
        current.changed()
        current.apply()
        assert registrar.deluxe_profile().snapshot()['suppressions'][rule]['disable']
        prefs.keymap.enable_keymaps = False
        assert item.active
        prefs.keymap.enable_keymaps = True
        assert not item.active
        registrar.unregister()
        assert item.active
        registrar.register()
        assert not item.active
        current = editor_ops.editor()
        current.draft.delete('suppressions', rule)
        current.changed()
        assert item.active
        current.apply()
        assert merged_digest() == registered_digest
        report.update(automatic_preview_verified=True, default_disable_restore_verified=True,
                      native_context_action_verified=True)

        def edited_binding():
            return next(item for item in configs.user.keymaps['Object Mode'].keymap_items
                        if item.idname == 'object.bh_face_select_or_pose')

        edited_binding().type = 'F19'
        configs.update()
        registrar.refresh()
        assert edited_binding().type == 'F19', 'Full refresh lost a native Preferences edit'
        prefs.keymap['enable_keymaps'] = False
        registrar.refresh()
        prefs.keymap['enable_keymaps'] = True
        registrar.refresh()
        assert edited_binding().type == 'F19', 'Disable/enable lost a native Preferences edit'
        registrar.unregister()
        assert runtime.runtime_stats()['tracked_resources'] == 0
        assert source_state() == initial
        report.update(status='passed', cycles=cycles, toggles=toggles,
                      merged_digest=registered_digest, native_preferences_edit_preserved=True,
                      catalog_section_choices_preserved=True, legacy_switches_ignored=True)
        if os.environ.get('BLUEHOLE_CAPTURE_EDITOR'):
            registrar.register()
            prefs.main_settings = 'GENERAL_ADDON'
            prefs.general_addon_settings = 'KEYMAP'
            bpy.ops.wm.bh_deluxe_edit(action='all_bindings')
            window = bpy.context.window_manager.windows[0]
            area = max(window.screen.areas, key=lambda area: area.width * area.height)
            area.type = 'PREFERENCES'
            with bpy.context.temp_override(window=window, area=area):
                bpy.ops.preferences.addon_show(module='bluehole_runtime')

            saved = catalog_revision()
            captures = []
            capture_operation = None
            def show_binding():
                prefs.keymap.enable_keymaps = True
                bpy.ops.wm.bh_deluxe_edit(action='discard')
                bpy.ops.wm.bh_deluxe_edit(action='show_assignments', target='other.shortcuts')
                editor_ops.state(bpy.context).search = 'repeat_last'
                editor_ops.editor().assignment = assignment

            def start_capture():
                nonlocal capture_operation
                operation_type = editor_ops.BH_OT_deluxe_capture
                capture_operation = SimpleNamespace(assignment=assignment, shared=False)
                capture_operation.report = lambda _level, message: report.update(operator_error=message)
                capture_operation.cancel = MethodType(operation_type.cancel, capture_operation)
                context = SimpleNamespace(area=area, window_manager=SimpleNamespace(
                    windows=bpy.context.window_manager.windows, modal_handler_add=lambda _operator: None))
                assert operation_type.execute(capture_operation, context) == {'RUNNING_MODAL'}
                assert editor_ops.editor().capture_assignment == assignment

            def show_default_rule():
                assert editor_ops.BH_OT_deluxe_capture.modal(capture_operation, bpy.context,
                    SimpleNamespace(type='ESC')) == {'CANCELLED'}
                assert not editor_ops.editor().capture_assignment
                active = editor_ops.editor()
                active.draft.stage_suppression('selection.all_none', source, item, 'default', disable=True)
                active.changed()
                bpy.ops.wm.bh_deluxe_edit(action='show_assignments', target='selection.all_none')

            def show_mesh():
                bpy.ops.wm.bh_deluxe_edit(action='show_assignments', target='mesh.tools')

            def show_context():
                bpy.ops.wm.bh_deluxe_edit(action='feature_category', target='navigation')
                editor_ops.editor().binding_context = editor_ops.context_id(scope)

            def show_commands():
                bpy.ops.wm.bh_deluxe_edit(action='discard')
                command = next(id_ for id_, row in editor_ops.editor().catalog['commands'].items()
                               if row.get('operator') == 'view3d.view_selected')
                active = editor_ops.editor()
                active.command = command
                active.focus_command = True
                active.command_category = active.command_section = ''
                editor_ops.state(bpy.context).tab = 'COMMANDS'

            steps = (
                ('all-bindings.png', show_context),
                ('context-filter.png', show_mesh),
                ('sections.png', lambda: setattr(checkbox('sections', 'mesh.tools'), 'boolean', False)),
                ('subsection-disabled.png', lambda: setattr(checkbox('categories', 'mesh'), 'boolean', False)),
                ('category-disabled.png', lambda: setattr(prefs.keymap, 'enable_keymaps', False)),
                ('deluxe-disabled.png', show_binding),
                ('keymap-binding.png', start_capture),
                ('input-key.png', show_default_rule),
                ('default-rule.png', show_commands),
                ('commands.png', None),
            )

            def capture():
                try:
                    name, change = steps[len(captures)]
                    with bpy.context.temp_override(window=window, area=area):
                        bpy.ops.screen.screenshot(filepath=str(output / name))
                    captures.append(name)
                    if change is not None:
                        change()
                        area.tag_redraw()
                        for region in area.regions:
                            region.tag_redraw()
                        # Let Blender process property notifications before the next draw.
                        return 1.0
                    assert catalog_revision() == saved, 'UI checkbox changes wrote the catalog'
                    prefs.keymap.enable_keymaps = True
                    assert bpy.ops.wm.bh_deluxe_edit(action='discard') == {'FINISHED'}
                    assert checkbox('categories', 'mesh').boolean
                    assert checkbox('sections', 'mesh.tools').boolean
                    report['editor_screenshots'] = captures
                except BaseException:
                    report.update(status='failed', error=traceback.format_exc())
                addon_utils.disable('bluehole_runtime', default_set=True)
                (output / 'timings.json').write_text(json.dumps(report, indent=2) + '\n')
                bpy.ops.wm.quit_blender()

            bpy.app.timers.register(capture, first_interval=1.0)
            return
        addon_utils.disable('bluehole_runtime', default_set=True)
    except BaseException:
        report.update(status='failed', error=traceback.format_exc())
        # Retire timers and registered types on a failed assertion too.
        addon_utils.disable('bluehole_runtime', default_set=True)
    (output / 'timings.json').write_text(json.dumps(report, indent=2) + '\n')
    bpy.ops.wm.quit_blender()


def verify_saved_preferences(output):
    import addon_utils
    import bpy
    addon_utils.disable('bluehole_runtime', default_set=True)
    bpy.context.window_manager.keyconfigs.update()
    bindings = bpy.context.window_manager.keyconfigs.user.keymaps['Object Mode'].keymap_items
    selected = [item for item in bindings if item.idname == 'object.select_all' and item.type == 'A'
                and item.properties.action == 'SELECT']
    assert len(selected) == 1 and selected[0].active, ('Preview disable leaked into userpref.blend: ' +
            repr([(item.id, item.active, item.is_user_modified) for item in selected]))
    assert not selected[0].is_user_modified, 'Preview created a native user override'
    (output / 'preferences-check.json').write_text(json.dumps({'status': 'passed'}))


def launch(binary, output, *, capture_editor=False):
    from blender_keymap_runtime import RESOURCE_NAMES, stage_package

    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    report_path = output / 'timings.json'
    report_path.unlink(missing_ok=True)
    (output / 'preferences-check.json').unlink(missing_ok=True)
    with TemporaryDirectory(prefix='bluehole-perf-', dir=output) as temporary:
        root = Path(temporary)
        environment = dict(os.environ)
        environment.pop('PYTHONPATH', None)
        environment.update(PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1',
                           BLUEHOLE_PERF_OUTPUT=str(output))
        if capture_editor:
            environment['BLUEHOLE_CAPTURE_EDITOR'] = '1'
        for name in RESOURCE_NAMES:
            folder = root / name.lower()
            folder.mkdir()
            environment['BLENDER_USER_' + name] = str(folder)
        for name, folder in (('TMPDIR', 'tmp'), ('XDG_CACHE_HOME', 'cache')):
            (root / folder).mkdir()
            environment[name] = str(root / folder)
        stage_package(root, None)
        command = [str(binary), '--factory-startup', '--disable-autoexec', '--offline-mode',
                   '--python-exit-code', '1', '--python', str(Path(__file__).resolve())]
        if sys.platform == 'darwin':
            policy = root / 'confinement.sb'
            policy.write_text('(version 1)\n(allow default)\n(deny network*)\n(deny file-write*)\n'
                              '(allow file-write* (subpath ' + json.dumps(str(output)) + '))\n'
                              '(allow file-write* (literal "/dev/null"))\n')
            command = ['/usr/bin/sandbox-exec', '-f', str(policy), *command]
        with (output / 'blender.log').open('w') as stream:
            subprocess.run(command, env=environment, stdout=stream, stderr=subprocess.STDOUT,
                           timeout=180, check=True)
        preliminary = json.loads(report_path.read_text())
        if preliminary['status'] == 'passed':
            verify = [part for part in command if part != '--factory-startup']
            with (output / 'preferences-check.log').open('w') as stream:
                subprocess.run(verify, env={**environment, 'BLUEHOLE_VERIFY_PREFS': '1'},
                               stdout=stream, stderr=subprocess.STDOUT, timeout=90, check=True)
    report = json.loads(report_path.read_text())
    report['preview_left_no_userpref_delta'] = (output / 'preferences-check.json').is_file()
    if report['status'] == 'passed' and not report['preview_left_no_userpref_delta']:
        report.update(status='failed', error='Preferences verification failed; see preferences-check.log')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return int(report['status'] != 'passed')


if __name__ == '__main__':
    if 'BLUEHOLE_VERIFY_PREFS' in os.environ:
        import bpy
        def verify_then_quit():
            try:
                verify_saved_preferences(Path(os.environ['BLUEHOLE_PERF_OUTPUT']))
            finally:
                bpy.ops.wm.quit_blender()
        bpy.app.timers.register(verify_then_quit, first_interval=1.0)
    elif 'BLUEHOLE_PERF_OUTPUT' in os.environ:
        import bpy
        bpy.context.preferences.view.show_splash = False
        bpy.app.timers.register(lambda: exercise(Path(os.environ['BLUEHOLE_PERF_OUTPUT'])), first_interval=1.0)
    else:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--blender', type=Path, required=True)
        parser.add_argument('--output', type=Path, required=True)
        parser.add_argument('--capture-editor', action='store_true', help='Capture the Bindings and Commands editor after validation')
        args = parser.parse_args()
        raise SystemExit(launch(args.blender, args.output, capture_editor=args.capture_editor))
