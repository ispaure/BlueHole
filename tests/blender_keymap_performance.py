"""Measure Deluxe lifecycle in an isolated Blender GUI with factory preferences.

Run with --blender /path/to/Blender --output tmp/test-results/keymap-performance.
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
    def checkpoint(name):
        (output / 'progress.json').write_text(json.dumps({'checkpoint': name}))
    try:
        checkpoint('load and unload cycles')
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
        def default_activity():
            return {(km.name, item.id): item.active for km in configs.default.keymaps
                    for item in km.keymap_items}

        defaults_before = default_activity()
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
            rules = {id_: row for id_, row in registrar.deluxe_profile().snapshot()['suppressions'].items()
                     if row['selector']['source_role'] == 'default'}
            results = registrar.deluxe_profile().registration_results()
            original_rules = {id_ for id_ in rules if not id_.startswith('parity-')}
            assert len(original_rules) == 24
            assert all(results.get(id_) == ('applied', '') for id_ in original_rules), {
                id_: results.get(id_) for id_ in original_rules if results.get(id_) != ('applied', '')}
            # Independent disable rules stay applied without a provider;
            # modal additions have new default IDs.
            applied_rules = {id_ for id_ in rules if results.get(id_) == ('applied', '')}
            changed_defaults = {key for key, active in default_activity().items()
                                if key in defaults_before and active != defaults_before[key]}
            assert len(changed_defaults) == len(applied_rules), changed_defaults
            digest = merged_digest()
            if registered_digest is not None:
                assert digest == registered_digest, 'Repeated registration changed merged bindings'
            registered_digest = digest
            unloaded = measure(registrar.unregister)
            assert source_state() == initial, 'Unloading changed foreign add-on rows'
            assert merged_digest() == merged_before, 'Unloading changed merged bindings'
            assert default_activity() == defaults_before, 'Unloading did not restore default activity'
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
        checkpoint('master and catalog toggles')
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
        assert prefs.keymap.bl_rna.properties['enable_keymaps'].name == 'Enable Blue Hole Keymaps & Pie Menus'

        section = 'navigation.view_framing'
        catalog_path = registrar.deluxe_profile().path
        assert catalog_path == Path(bpy.utils.user_resource('CONFIG')) / 'bluehole/keymaps.json'
        def catalog_revision():
            return registrar.deluxe_profile()._disk_revision()
        before_edit = catalog_revision()
        editor_ops = importlib.import_module('bluehole_runtime.preferences.addon.keymaps.deluxe_editor_ops')

        def checkbox(table, target):
            current = editor_ops.editor()
            return editor_ops.inline_value(editor_ops.state(bpy.context), 'enabled', 'boolean',
                                           current.catalog[table][target].get('enabled', True),
                                           table=table, entry=target)

        for table, target in (('sections', section), ('categories', 'addons')):
            checkbox(table, target).boolean = False
            assert not editor_ops.editor().catalog[table][target]['enabled']
        assert catalog_revision() == before_edit, 'Draft toggles wrote the catalog'
        assert not editor_ops.editor().preview_error, editor_ops.editor().preview_error
        assert not registrar.deluxe_section_enabled(section), 'Draft did not preview in live keymaps'
        assert bpy.ops.wm.bh_deluxe_edit(action='discard') == {'FINISHED'}
        for table, target in (('sections', section), ('categories', 'addons')):
            assert checkbox(table, target).boolean, 'Discard did not reset a checkbox'
            checkbox(table, target).boolean = False
        assert bpy.ops.wm.bh_deluxe_edit(action='apply') == {'FINISHED'}
        saved = catalog_revision()
        catalog = registrar.deluxe_profile().snapshot()
        assert not catalog['sections'][section]['enabled']
        assert not catalog['categories']['addons']['enabled']
        registrar.unregister()
        registrar.register()
        assert not registrar.deluxe_section_enabled(section)
        assert not registrar.deluxe_section_enabled('addons.blue-hole')
        prefs.keymap['enable_keymaps'] = False
        registrar.refresh()
        prefs.keymap['enable_keymaps'] = True
        registrar.refresh()
        assert not registrar.deluxe_section_enabled(section)
        assert catalog_revision() == saved
        for table, target in (('sections', section), ('categories', 'addons')):
            checkbox(table, target).boolean = True
        assert bpy.ops.wm.bh_deluxe_edit(action='apply') == {'FINISHED'}
        assert merged_digest() == registered_digest

        # Category filters and name/key search remain; context browsing uses the tree.
        current = editor_ops.editor()
        report['legacy_default_disables_verified'] = len(rules)
        view = editor_ops.state(bpy.context)
        assert 'tab' not in view.bl_rna.properties
        assert 'command_edit_scope' not in view.bl_rna.properties
        assert 'live_source' not in view.bl_rna.properties
        assert not hasattr(editor_ops, 'BH_OT_deluxe_binding_picker')
        assert not hasattr(editor_ops, 'BH_OT_deluxe_shortcut')
        assert set(view.bl_rna.properties['search_mode'].enum_items.keys()) == {'NAME', 'KEY'}
        assert current.binding_all
        bpy.ops.wm.bh_deluxe_edit(action='feature_category', target='navigation')
        view.search = 'narrow search'
        assert all(current.catalog['sections'][row['section']]['category'] == 'navigation'
                   for row in current.catalog['assignments'].values() if current.accepts_binding(row))
        bpy.ops.wm.bh_deluxe_edit(action='all_bindings')
        assert view.search == '' and current.binding_all
        command_ids = [row['command'] for row in current.catalog['assignments'].values()]
        assert len(command_ids) == len(set(command_ids))
        assert any(id_ == 'wm.call_menu_pie' for id_, _ in editor_ops.operator_search(None, bpy.context, 'call_menu_pie'))

        # A historically inactive row is unchecked; enabling it activates that row.
        checkpoint('binding creation and command editing')
        inactive_id = next(id_ for id_, row in current.catalog['assignments'].items()
                           if not row.get('active', True))
        row = current.catalog['assignments'][inactive_id]
        enabled = editor_ops.inline_value(view, 'enabled', 'binding_enabled',
            row.get('enabled', True) and row.get('active', True), table='assignments', entry=inactive_id)
        assert not enabled.binding_enabled
        enabled.binding_enabled = True
        assert current.catalog['assignments'][inactive_id]['active']
        assert not current.preview_error, current.preview_error
        current.discard()
        assert merged_digest() == registered_digest
        report['inactive_binding_enable_verified'] = True

        # Add New creates an unassigned row directly; type operators and properties inline.
        saved = catalog_revision()
        mappings = []
        for scope_name in ('3D View', 'Image'):
            before_add = merged_digest()
            scope = next(scope for scope in editor_ops.assignment_scopes(current, configs) if scope['name'] == scope_name)
            assert bpy.ops.wm.bh_deluxe_add_binding(scope=json.dumps(scope), section='navigation.view_framing') == {'FINISHED'}
            assignment_id = current.assignment
            command_id = current.catalog['assignments'][assignment_id]['command']
            assert not current.catalog['commands'][command_id]['operator']
            assert merged_digest() == before_add
            current.stage_event(assignment_id, dict(type='F24', ctrl=True, shift=True, alt=True, oskey=True))
            editor_ops.inline_value(view, 'operator', 'operator_id', '', command=command_id,
                                   assignment=assignment_id).operator_id = 'view3d.view_selected'
            mappings.append(assignment_id)
            assert not current.preview_error, current.preview_error
        first, second = [current.catalog['assignments'][id_]['command'] for id_ in mappings]
        assert first != second
        assert current.catalog['commands'][first] == current.catalog['commands'][second]
        control = editor_ops.inline_value(view, 'use_all_regions', 'boolean', False,
                                         command=first, assignment=mappings[0])
        control.boolean = True
        assert current.catalog['commands'][first]['properties']['use_all_regions']
        assert not current.catalog['commands'][second]['properties']
        assert bpy.ops.wm.bh_deluxe_inline_edit(command=first, field='use_all_regions', assignment=mappings[0]) == {'FINISHED'}
        current.undo()
        assert current.catalog['commands'][first]['properties']['use_all_regions']
        editor_ops.inline_value(view, 'operator', 'operator_id', 'view3d.view_selected',
                               command=first, assignment=mappings[0]).operator_id = 'wm.call_menu_pie'
        meta = current.store.resolver.describe_command(current.catalog['commands'][first], include_unset=True)
        assert meta['fields']['name']['editable']
        current.edit_command(first, 'name', 'BLUEHOLE_MT_pie_add', mappings[0])
        assert not current.preview_error, current.preview_error
        editor_ops.inline_value(view, 'operator', 'operator_id', 'wm.call_menu_pie',
                               command=first, assignment=mappings[0]).operator_id = 'wm.bh_typed_command_test'
        assert not current.preview_error, current.preview_error
        assert current.preview()['commands'][first]['availability'] == 'unavailable'
        current.apply()
        current.reload()
        assert current.catalog['commands'][first]['operator'] == 'wm.bh_typed_command_test'
        class BH_OT_typed_command_test(bpy.types.Operator):
            bl_idname = 'wm.bh_typed_command_test'
            bl_label = 'Typed Test'
            enabled: bpy.props.BoolProperty(default=False)
            def execute(self, _context):
                return {'FINISHED'}
        bpy.utils.register_class(BH_OT_typed_command_test)
        try:
            current.edit_command(first, 'enabled', True, mappings[0])
            assert not current.preview_error, current.preview_error
            assert current.preview()['commands'][first]['availability'] == 'available'
            current.change_command_operator(first, 'view3d.view_all')
        finally:
            bpy.utils.unregister_class(BH_OT_typed_command_test)
        assert current.catalog['commands'][first]['properties'] == {}
        assert current.catalog['commands'][second]['operator'] == 'view3d.view_selected'
        original = dict(current.catalog['assignments'][mappings[0]])
        category = editor_ops.inline_value(view, 'binding_category', 'option', 'navigation',
            assignment=mappings[0], items=[('navigation', 'Navigation', ''), ('mesh', 'Mesh', '')])
        category.option = 'mesh'
        assert current.catalog['sections'][current.catalog['assignments'][mappings[0]]['section']]['category'] == 'mesh'
        assert current.catalog['assignments'][mappings[0]]['command'] == first
        current.undo()
        assert current.catalog['assignments'][mappings[0]] == original
        assert bpy.ops.wm.bh_deluxe_remove_assignment('EXEC_DEFAULT', assignment=mappings[0]) == {'FINISHED'}
        assert first not in current.catalog['commands'] and second in current.catalog['commands']
        current.undo()
        current.apply()
        current.reload()
        assert current.catalog['commands'][first]['operator'] == 'view3d.view_all'
        for assignment_id in mappings:
            event_id = current.catalog['assignments'][assignment_id]['event']
            current.draft.delete('assignments', assignment_id)
            current.draft.delete('events', event_id)
        current.changed()
        current.apply()
        bpy.ops.wm.bh_deluxe_edit(action='all_bindings')
        assert merged_digest() == registered_digest
        report.update(binding_filters_verified=True, independent_commands_verified=True,
                      direct_context_add_verified=True, typed_missing_operator_verified=True,
                      menu_properties_editable=True, category_move_verified=True,
                      command_reset_undo_retarget_delete_and_reload_verified=True)

        # Live changes fork a shared event without changing the saved JSON.
        checkpoint('event editing and capture')
        current = editor_ops.editor()
        assignment = 'other-screen-c7515cc97075'
        original_event = current.catalog['assignments'][assignment]['event']
        def event_field(field, prop, value, items=()):
            data = current.catalog['events'][current.catalog['assignments'][assignment]['event']]
            control = editor_ops.inline_value(editor_ops.state(bpy.context), field, prop,
                                               data.get(field, {'map_type': 'KEYBOARD', 'value': 'PRESS'}.get(field, False)),
                                               assignment=assignment, items=items)
            setattr(control, prop, value)
            assert not current.preview_error, current.preview_error

        saved = catalog_revision()
        event_field('repeat', 'repeat', False)
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

        # The inline key dropdown covers Escape/None without entering capture mode.
        options = editor_ops.resolver.input_options()['event']
        for key in ('ESC', 'NONE'):
            event_field('type', 'option', key, options['type'])
            assert current.catalog['events'][current.catalog['assignments'][assignment]['event']]['type'] == key
        # Every offered input must register with Blender's actual input type.
        native_map = configs.addon.keymaps['Screen']
        for key in options['type']:
            probe = native_map.keymap_items.new('screen.repeat_last', type=key, value='PRESS')
            try:
                assert probe.map_type == editor_ops.map_type(key), (key, probe.map_type)
            finally:
                native_map.keymap_items.remove(probe)
        for key in ('LEFTMOUSE', 'PEN', 'ERASER', 'TIMER0', 'TEXTINPUT', 'MOUSESMARTZOOM'):
            current.discard()
            event_field('type', 'option', key, options['type'])
            data = current.catalog['events'][current.catalog['assignments'][assignment]['event']]
            assert data['map_type'] == editor_ops.map_type(key)
            assert data['repeat'] == (data['map_type'] == 'KEYBOARD')
        for phase in ('RELEASE', 'CLICK_DRAG'):
            current.discard()
            event_field('value', 'option', phase, options['value'])
            data = current.catalog['events'][current.catalog['assignments'][assignment]['event']]
            assert not data['repeat']
        if 'hyper' in bpy.types.KeyMapItem.bl_rna.properties:
            current.discard()
            for expected in (True, -1, False):
                assert bpy.ops.wm.bh_deluxe_inline_edit(assignment=assignment, field='hyper') == {'FINISHED'}
                assert current.catalog['events'][current.catalog['assignments'][assignment]['event']]['hyper'] == expected
                assert not current.preview_error, current.preview_error
        current.discard()
        assert merged_digest() == registered_digest
        report['inline_shortcut_settings_verified'] = True

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

        # The native menu also disables our own additions via their original
        checkpoint('native disable and preference persistence')
        # catalog setting, without inventing a suppression for an owned row.
        merged_map = configs.user.keymaps['Screen']
        redo = next(item for item in merged_map.keymap_items
                    if item.idname == 'ed.redo' and item.type == 'Y' and item.ctrl)
        original_redo = [(item.id, item.active) for item in configs.default.keymaps['Screen'].keymap_items
                         if item.idname == 'ed.redo']
        menu_entries = []
        class OwnedMenuLayout:
            def separator(self):
                pass
            def operator(self, idname, **kwargs):
                props = SimpleNamespace()
                menu_entries.append((idname, props))
                return props
        editor_ops.draw_binding_context(SimpleNamespace(layout=OwnedMenuLayout()),
                                       SimpleNamespace(button_pointer=redo, keymap=merged_map))
        operator_id, props = menu_entries[0]
        assert operator_id == editor_ops.BH_OT_deluxe_disable_owned_binding.bl_idname
        rules_before = set(current.catalog['suppressions'])
        assert bpy.ops.wm.bh_deluxe_disable_owned_binding(**vars(props)) == {'FINISHED'}
        assert not current.catalog['assignments'][props.assignment]['enabled']
        assert current.assignment == props.assignment
        assert set(current.catalog['suppressions']) == rules_before
        assert not any(item.idname == 'ed.redo' and item.type == 'Y' and item.ctrl
                       for item in configs.user.keymaps['Screen'].keymap_items)
        assert [(item.id, item.active) for item in configs.default.keymaps['Screen'].keymap_items
                if item.idname == 'ed.redo'] == original_redo
        current.undo()
        assert merged_digest() == registered_digest
        current.discard()

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
        existing_rules = set(current.catalog['suppressions'])
        operation = SimpleNamespace(rule='', use_replacement=False, **vars(properties))
        for name in ('selected', 'run', 'release_choices'):
            setattr(operation, name, MethodType(getattr(operation_type, name), operation))
        operation.report = lambda _level, message: report.update(operator_error=message)
        dialog_context = SimpleNamespace(window_manager=SimpleNamespace(
            keyconfigs=configs, invoke_props_dialog=lambda *_args, **_kwargs: {'RUNNING_MODAL'}))
        assert operation_type.invoke(operation, dialog_context, None) == {'RUNNING_MODAL'}
        assert operation.disable_binding
        assert operation_type.execute(operation, bpy.context) == {'FINISHED'}, report.get('operator_error')
        rule, = set(current.catalog['suppressions']) - existing_rules
        assert not current.preview_error, current.preview_error
        assert not item.active, 'Default disable did not preview'
        user_item = configs.user.keymaps['Object Mode'].keymap_items.from_id(item.id)
        assert not user_item.active and not user_item.is_user_modified
        assert current.preview()['suppressions'][rule]['registered']
        assert current.binding_origin(rule, current.preview()) == (
            'REMOVE', 'Blender Keymap Disabled by Blue Hole Deluxe')
        assert bpy.ops.wm.bh_deluxe_edit(action='remove_rule', target=rule) == {'FINISHED'}
        assert item.active, 'Removing the tree row did not restore its Blender default'
        current.undo()
        assert not item.active, 'Undo did not restore the disable rule'
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

        # An artist can capture a provider's merged row without choosing its
        # source. Recreated source IDs are observed by the existing watcher.
        class BH_OT_disable_fixture(bpy.types.Operator):
            bl_idname = 'wm.bh_disable_fixture'
            bl_label = 'Provider Disable Fixture'
            def execute(self, _context):
                return {'FINISHED'}
        bpy.utils.register_class(BH_OT_disable_fixture)
        provider_map = configs.addon.keymaps.new(name='3D View Generic', space_type='VIEW_3D')
        def create_provider_item():
            provider_item = provider_map.keymap_items.new('wm.bh_disable_fixture', 'F18', 'PRESS')
            configs.update()
            return provider_item
        provider_item = create_provider_item()
        merged_map = configs.user.keymaps['3D View Generic']
        merged_item = next(item for item in merged_map.keymap_items if item.idname == 'wm.bh_disable_fixture')
        candidate = editor_ops.resolver.capture_candidate(merged_map, merged_item, 'user')
        assert candidate['can_disable'] and candidate['selector']['source_role'] == 'addon', candidate
        current = editor_ops.editor()
        provider_rule = current.draft.stage_suppression('other.shortcuts', merged_map, merged_item, 'user', disable=True)
        current.changed()
        assert not current.preview_error, current.preview_error
        assert not provider_item.active
        assert current.binding_origin(provider_rule, current.preview())[0] == 'REMOVE'
        assert 'Add-on' in current.binding_origin(provider_rule, current.preview())[1]
        provider_map.keymap_items.remove(provider_item)
        configs.update()
        registrar.default_bindings.reconcile(budget=len(registrar.default_bindings._requests), time_budget=10)
        assert not current.store.registration_results()[provider_rule][0] == 'applied'
        provider_item = create_provider_item()
        registrar.default_bindings.reconcile(budget=len(registrar.default_bindings._requests), time_budget=10)
        assert not provider_item.active, 'Provider enabled after startup was not disabled'
        bpy.ops.wm.save_userpref()
        current.set_enabled('suppressions', provider_rule, False)
        assert provider_item.active
        current.undo()
        assert not provider_item.active
        current.discard()
        assert provider_item.active
        provider_map.keymap_items.remove(provider_item)
        bpy.utils.unregister_class(BH_OT_disable_fixture)
        configs.update()
        assert merged_digest() == registered_digest
        report['provider_disable_capture_reload_restore_verified'] = True

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
        if runtime._contains(configs.addon.keymaps, provider_map) and not provider_map.keymap_items:
            configs.addon.keymaps.remove(provider_map)
        assert source_state() == initial
        report.update(status='passed', cycles=cycles, toggles=toggles,
                      merged_digest=registered_digest, native_preferences_edit_preserved=True,
                      catalog_section_choices_preserved=True, legacy_switches_ignored=True)
        if os.environ.get('BLUEHOLE_CAPTURE_EDITOR'):
            registrar.register()
            editor_ui = importlib.import_module('bluehole_runtime.preferences.addon.keymaps.deluxe_editor')
            draw_times = []
            original_draw = editor_ui.draw
            def measured_draw(*args, **kwargs):
                started = time.perf_counter()
                try:
                    return original_draw(*args, **kwargs)
                finally:
                    draw_times.append(time.perf_counter() - started)
            editor_ui.draw = measured_draw
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
                rule_id = active.draft.stage_suppression('selection.all_none', source, item, 'default', disable=True)
                active.changed()
                bpy.ops.wm.bh_deluxe_edit(action='show_assignments', target='selection.all_none')
                active.assignment = rule_id
                editor_ops.state(bpy.context).search = 'object.select_all'

            def show_mesh():
                bpy.ops.wm.bh_deluxe_edit(action='show_assignments', target='mesh.tools')

            def show_context():
                bpy.ops.wm.bh_deluxe_edit(action='feature_category', target='navigation')
                editor_ops.state(bpy.context).search = 'view_selected'

            def show_command_settings():
                bpy.ops.wm.bh_deluxe_edit(action='discard')
                bpy.ops.wm.bh_deluxe_edit(action='all_bindings')
                active = editor_ops.editor()
                active.assignment = next(id_ for id_, row in active.catalog['assignments'].items()
                                         if active.catalog['commands'][row['command']].get('operator') == 'mesh.bisect')
                editor_ops.state(bpy.context).search = 'mesh.bisect'

            def show_menu_properties():
                bpy.ops.wm.bh_deluxe_edit(action='all_bindings')
                active = editor_ops.editor()
                active.assignment = next(id_ for id_, row in active.catalog['assignments'].items()
                    if active.catalog['commands'][row['command']].get('properties', {}).get('name') == 'BLUEHOLE_MT_pie_add')
                editor_ops.state(bpy.context).search = 'BLUEHOLE_MT_pie_add'

            def show_new_binding():
                active = editor_ops.editor()
                bpy.ops.wm.bh_deluxe_edit(action='show_assignments', target='mesh.tools')
                scope = next(scope for scope in editor_ops.assignment_scopes(active, configs)
                             if scope['name'] == 'Mesh')
                assert bpy.ops.wm.bh_deluxe_add_binding(scope=json.dumps(scope)) == {'FINISHED'}
                assert not active.preview_error, active.preview_error

            def show_pending_addition():
                bpy.ops.wm.bh_deluxe_edit(action='discard')
                bpy.ops.wm.bh_deluxe_edit(action='all_bindings')
                active = editor_ops.editor()
                active.assignment = next(id_ for id_, row in active.catalog['assignments'].items()
                                         if active.catalog['commands'][row['command']].get('operator') == 'machin3.focus')
                editor_ops.state(bpy.context).search = 'machin3.focus'

            def show_pending_removal():
                bpy.ops.wm.bh_deluxe_edit(action='all_bindings')
                editor_ops.editor().assignment = 'legacy-addon-disable-mesh-28'
                editor_ops.state(bpy.context).search = 'machin3.symmetrize'

            steps = (
                ('all-bindings.png', show_context),
                ('name-search.png', show_mesh),
                ('sections.png', lambda: setattr(checkbox('sections', 'mesh.tools'), 'boolean', False)),
                ('subsection-disabled.png', lambda: setattr(checkbox('categories', 'mesh'), 'boolean', False)),
                ('category-disabled.png', lambda: setattr(prefs.keymap, 'enable_keymaps', False)),
                ('deluxe-disabled.png', show_binding),
                ('keymap-binding.png', start_capture),
                ('input-key.png', show_default_rule),
                ('default-rule.png', show_command_settings),
                ('binding-command-settings.png', show_menu_properties),
                ('menu-properties.png', show_new_binding),
                ('new-binding.png', show_pending_addition),
                ('pending-addition.png', show_pending_removal),
                ('pending-removal.png', None),
            )

            def capture():
                try:
                    name, change = steps[len(captures)]
                    with bpy.context.temp_override(window=window, area=area):
                        # Screenshot reads the presented buffer. A timer can
                        # run before the next swap even after a tagged redraw.
                        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
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
                    report['editor_draw_seconds'] = draw_times
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
    configs = bpy.context.window_manager.keyconfigs
    for source in configs.default.keymaps:
        if not source.is_modal:
            continue
        merged = configs.user.keymaps.get(source.name)
        def modal_rows(km):
            return [(item.propvalue, item.type, item.value, item.any, item.shift, item.ctrl,
                     item.alt, item.oskey, item.key_modifier, item.active) for item in km.keymap_items]
        assert modal_rows(merged) == modal_rows(source), ('Modal alias leaked into preferences', source.name)
    assert not any(item.is_user_modified or item.is_user_defined
                   for km in configs.user.keymaps for item in km.keymap_items), 'Runtime changes leaked into saved user keymaps'
    (output / 'preferences-check.json').write_text(json.dumps({'status': 'passed', 'modal_aliases_not_saved': True}))


def launch(binary, output, *, capture_editor=False, package_archive=None):
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
        stage_package(root, None, package_archive)
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
                           timeout=600, check=True)
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
        parser.add_argument('--capture-editor', action='store_true', help='Capture the binding editor after validation')
        parser.add_argument('--package', type=Path, help='Test these exact packaged addon bytes')
        args = parser.parse_args()
        raise SystemExit(launch(args.blender, args.output, capture_editor=args.capture_editor, package_archive=args.package))
