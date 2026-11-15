"""Blender operators for editing the Deluxe profile in Preferences."""

from copy import deepcopy
from dataclasses import asdict
import json
from uuid import uuid4

import addon_utils
import bpy
from bpy.props import (BoolProperty, CollectionProperty, EnumProperty, FloatProperty, IntProperty,
                       PointerProperty, StringProperty)

from ....keymaps import deluxe_resolver as resolver, keymap_utils as runtime, keymaps_register, default_bindings
from ....keymaps.deluxe_schema import event_descriptor, require, selector_descriptor, same_value
from .deluxe_editor_model import (Editor, SOURCE_LABELS, captured_input, context_label,
                                 display_value, map_type, scope_key, shortcut, title, context_id)

_editor = None
_dialog_choices = {}
_context_choices = []
_undo_keymap = None
WM_PROPERTY = 'bh_deluxe_editor'
ERRORS = (ValueError, KeyError, IndexError, OSError, RuntimeError, ReferenceError)
HIDDEN = {'HIDDEN', 'SKIP_SAVE'}
TRANSIENT = {'SKIP_SAVE'}

EDIT_DESCRIPTIONS = {
    'apply': ('Save assignments, commands and section choices to this Blue Hole installation. '
              'Installing a Blue Hole update replaces these changes'),
    'discard': 'Discard staged edits and return to the last applied profile',
    'reload': 'Reload the keymap catalog from disk and discard staged edits',
    'reset': 'Stage the catalog loaded when the editor opened',
    'category': 'Browse assignments in this category',
    'section': 'Browse assignments in this section',
    'assignment': 'Show the shortcut and settings for this assignment',
    'expand_binding_context': 'Show bindings in this keymap context',
    'collapse_binding_context': 'Hide bindings in this keymap context',
    'expand_binding_contexts': 'Expand every context containing matching bindings',
    'collapse_binding_contexts': 'Collapse the tree to its top-level contexts',
    'show_assignments': 'Show bindings in this subsection',
    'all_bindings': 'Show every binding and clear search and category filters',
    'delete_section': 'Stage removal of this empty section',
    'remove_rule': 'Stage removal of this existing-shortcut rule',
    'feature_category': 'Show the shortcut groups in this category',
    'feature_section': 'Show this shortcut group’s enable setting and assignments',
}
TOGGLE_TARGETS = {'categories': 'category', 'sections': 'section',
                  'assignments': 'assignment', 'suppressions': 'rule'}


def editor():
    global _editor
    store = keymaps_register.deluxe_profile()
    if _editor is None or _editor.store is not store:
        _editor = Editor(store)
    return _editor


def redraw(context):
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'PREFERENCES':
                area.tag_redraw()


class EditorOperator:
    def run(self, context, action):
        try:
            current = editor()
            action(current)
        except ERRORS as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        redraw(context)
        return {'FINISHED'}

    def execute(self, context):
        try:
            return self.run(context, self.stage)
        finally:
            self.release_choices()

    def cancel(self, _context):
        self.release_choices()

    def release_choices(self):
        key = getattr(self, 'choice_key', '')
        if key:
            _dialog_choices.pop(key, None)


_inline_enums = {}
_syncing_inline = False
INLINE_VALUES = {'BOOLEAN': 'boolean', 'INT': 'integer', 'FLOAT': 'number',
                 'STRING': 'string', 'ENUM': 'option'}
EVENT_MODIFIERS = ('shift', 'ctrl', 'alt', 'oskey', 'hyper')
INPUT_TYPES = (('KEYBOARD', 'Keyboard', 'Bind a keyboard key'),
               ('MOUSE', 'Mouse', 'Bind a mouse button or wheel'))


def operator_search(_self, _context, edit_text):
    """Native string suggestions allow choosing a live operator or typing an ID."""
    terms = edit_text.casefold().split()
    for namespace in dir(bpy.ops):
        if namespace.startswith('_'):
            continue
        for name in dir(getattr(bpy.ops, namespace)):
            if name.startswith('_'):
                continue
            id_ = f'{namespace}.{name}'
            rna = resolver._operator_rna(id_)
            if rna is not None and all(term in f'{id_} {rna.name}'.casefold() for term in terms):
                yield id_, rna.name


def inline_options(control, _context):
    return _inline_enums.get(control.choices_key, [])


def inline_update(prop):
    def update(control, context):
        if _syncing_inline or _editor is None:
            return
        try:
            value = getattr(control, prop)
            if control.table:
                _editor.set_enabled(control.table, control.entry, value)
            elif control.field in {'binding_category', 'binding_section'}:
                if control.field == 'binding_category':
                    _editor.move_binding(control.assignment, category=value)
                else:
                    _editor.move_binding(control.assignment, section=value)
            elif prop == 'operator_id':
                _editor.require_editable_assignment(control.assignment)
                command = _editor.catalog['assignments'][control.assignment]['command']
                _editor.change_command_operator(command, value)
            elif control.command:
                command = (_editor.catalog['assignments'][control.assignment]['command']
                           if control.assignment else control.command)
                _editor.edit_command(command, control.field, value, control.assignment)
            else:
                stage_event_field(_editor, control.assignment, control.field, value)
        except ERRORS as error:
            _editor.message = str(error)
        redraw(context)
    return update


class BH_PG_deluxe_value(bpy.types.PropertyGroup):
    table: StringProperty(options=HIDDEN)
    entry: StringProperty(options=HIDDEN)
    command: StringProperty(options=HIDDEN)
    assignment: StringProperty(options=HIDDEN)
    field: StringProperty(options=HIDDEN)
    choices_key: StringProperty(options=HIDDEN)
    operator_id: StringProperty(name='Operator', description='Choose an available operator or type its ID',
                                search=operator_search, search_options={'SUGGESTION', 'SORT'},
                                update=inline_update('operator_id'), options=TRANSIENT)
    binding_enabled: BoolProperty(name='Enabled', description='Enable or disable this Blue Hole binding without deleting it',
                                  update=inline_update('binding_enabled'), options=TRANSIENT)
    repeat: BoolProperty(description='Repeat this shortcut while its key is held', update=inline_update('repeat'), options=TRANSIENT)
    any_modifier: BoolProperty(description='Match this shortcut regardless of which modifiers are held',
                               update=inline_update('any_modifier'), options=TRANSIENT)
    boolean: BoolProperty(description='Turn this option on or off', update=inline_update('boolean'), options=TRANSIENT)
    integer: IntProperty(description='Change this setting for the selected binding', update=inline_update('integer'), options=TRANSIENT)
    number: FloatProperty(description='Change this setting for the selected binding', update=inline_update('number'),
                          precision=6, options=TRANSIENT)
    string: StringProperty(description='Change this setting for the selected binding', update=inline_update('string'), options=TRANSIENT)
    option: EnumProperty(description='Choose a value for this setting', items=inline_options,
                         update=inline_update('option'), options=TRANSIENT)


class BH_PG_deluxe_binding_row(bpy.types.PropertyGroup):
    kind: StringProperty(options=TRANSIENT)
    target: StringProperty(options=TRANSIENT)
    label: StringProperty(options=TRANSIENT)
    shortcut: StringProperty(options=TRANSIENT)
    icon: StringProperty(options=TRANSIENT)
    tooltip: StringProperty(options=TRANSIENT)
    depth: IntProperty(options=TRANSIENT)
    expanded: BoolProperty(options=TRANSIENT)
    removable: BoolProperty(options=TRANSIENT)
    rule: BoolProperty(options=TRANSIENT)
    pending: BoolProperty(options=TRANSIENT)
    scope: StringProperty(options=TRANSIENT)
    section: StringProperty(options=TRANSIENT)


class BH_PG_deluxe_editor(bpy.types.PropertyGroup):
    def select_binding(self, context):
        if _syncing_inline or _editor is None or not 0 <= self.binding_index < len(self.binding_rows):
            return
        row = self.binding_rows[self.binding_index]
        if row.kind == 'binding':
            _editor.assignment = row.target
            self.list_selection = row.target
            self.list_focus = ''
            redraw(context)

    def reset_page(self, _context):
        if _editor is not None:
            _editor.page = 0

    def switch_tab(self, context):
        self.search = ''
        self.reset_page(context)

    search_mode: EnumProperty(items=[('NAME', 'Name', 'Search for a command or keymap name'),
                                    ('KEY', 'Key-Binding', 'Type a shortcut, such as Shift F10')],
                              options=TRANSIENT, update=switch_tab)
    search: StringProperty(name='Search', description='Filter the current list using the selected search mode',
                           options=TRANSIENT, update=reset_page)
    values: CollectionProperty(type=BH_PG_deluxe_value, options=TRANSIENT)
    binding_rows: CollectionProperty(type=BH_PG_deluxe_binding_row, options=TRANSIENT)
    binding_index: IntProperty(default=-1, update=select_binding, options=TRANSIENT)
    rows_key: StringProperty(options=TRANSIENT)
    list_selection: StringProperty(options=TRANSIENT)
    list_focus: StringProperty(options=TRANSIENT)


def sync_binding_rows(view, key, rows, selection, *, focus_context=''):
    """Rebuild native list storage only when its contents or expansion change."""
    global _syncing_inline
    _syncing_inline = True
    try:
        if focus_context:
            view.list_focus = focus_context
        elif view.list_selection != selection:
            view.list_focus = ''
        rebuilt = view.rows_key != key
        if rebuilt:
            view.binding_rows.clear()
            for values in rows():
                row = view.binding_rows.add()
                for name, value in values.items():
                    setattr(row, name, value)
            view.rows_key = key
        if view.list_focus:
            # Expansion is navigation, not a request to reveal the inspector's
            # selection. Keep native list focus on the header just clicked.
            view.binding_index = next((index for index, row in enumerate(view.binding_rows)
                                       if row.kind == 'context' and row.target == view.list_focus), -1)
            view.list_selection = selection
        elif rebuilt or view.list_selection != selection:
            view.binding_index = next((index for index, row in enumerate(view.binding_rows)
                                       if row.kind == 'binding' and row.target == selection), -1)
            view.list_selection = selection
    finally:
        _syncing_inline = False


def state(context):
    return getattr(context.window_manager, WM_PROPERTY)


def inline_value(view, field, prop, value, *, command='', assignment='', table='', entry='', items=()):
    """Bind a native widget to transient RNA, with changes staged in the draft."""
    global _syncing_inline
    name = f'{table}:{entry}:{field}' if table else f'{command}:{assignment}:{field}'
    control = view.values.get(name)
    reset_value = control is None
    _syncing_inline = True
    try:
        if control is None:
            control = view.values.add()
            control.name = name
            control.table, control.entry = table, entry
            control.command, control.assignment, control.field = command, assignment, field
        if items:
            choices_key = repr(items)
            reset_value = reset_value or control.choices_key != choices_key
            control.choices_key = choices_key
            if control.choices_key not in _inline_enums:
                _inline_enums[control.choices_key] = choices(
                    (item, title(item), '') if isinstance(item, str) else item for item in items)
        # A new or shortened enum has no valid current value until initialized.
        # Reading it first produces RNA warnings and can return an empty token.
        if reset_value or getattr(control, prop) != value:
            setattr(control, prop, value)
    finally:
        _syncing_inline = False
    return control


class BH_OT_deluxe_edit(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_edit'
    bl_label = 'Edit Deluxe Profile'

    action: StringProperty(options=HIDDEN)
    target: StringProperty(options=HIDDEN)

    @classmethod
    def description(cls, _context, props):
        action, target = props.action, props.target
        if action == 'page' and target.isdecimal():
            return f'Go to page {int(target) + 1}'
        if action == 'order':
            direction = 'up' if target == '-1' else 'down'
            return f'Move this section {direction} in its category'
        if action in TOGGLE_TARGETS:
            label = TOGGLE_TARGETS[action]
            row = _editor.catalog[action].get(target) if _editor is not None else None
            if row is None:
                return f'Toggle this {label} in the draft'
            verb = 'Disable' if row.get('enabled', True) else 'Enable'
            return f'{verb} this {label} in the draft'
        if action == 'assignment' and _editor is not None:
            row = _editor.catalog['assignments'].get(props.target)
            if row:
                event = shortcut(_editor.catalog['events'][row['event']])
                origin = _editor.binding_origin(props.target, _editor.preview())[1]
                return f"{origin}\n{event} in {context_label(row['scope'])}"
            if props.target in _editor.catalog['suppressions']:
                return _editor.binding_origin(props.target, _editor.preview())[1]
        if action == 'remove_rule':
            return 'Remove this rule and restore the Blender keymap; Undo restores the rule'
        return EDIT_DESCRIPTIONS.get(action, cls.bl_label)

    def invoke(self, context, event):
        if self.action in {'reset', 'reload', 'delete_section'}:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        if self.action == 'restore_default':
            section = editor().catalog['suppressions'][self.target]['section']
            self.action = 'remove_rule'
            result = super().execute(context)
            if result == {'FINISHED'}:
                open_assignment_section(context, section)
            return result
        if self.action in {'show_assignments', 'all_bindings'}:
            def show_bindings(current):
                view = state(context)
                view.search = ''
                current.show_all_bindings()
                if self.action == 'show_assignments':
                    current.select_section(self.target)
            return self.run(context, show_bindings)
        return super().execute(context)

    def stage(self, current):
        action, target = self.action, self.target
        if action == 'apply':
            current.apply()
        elif action == 'discard':
            current.discard()
        elif action == 'reload':
            current.reload()
        elif action == 'reset':
            current.draft.reset()
            current.changed('Initial catalog staged')
        elif action == 'category':
            current.select_category(target)
        elif action == 'assignment':
            setattr(current, action, target)
        elif action in {'expand_binding_context', 'collapse_binding_context'}:
            current.binding_context_expansion[target] = action == 'expand_binding_context'
            current.binding_focus_context = target
        elif action in {'expand_binding_contexts', 'collapse_binding_contexts'}:
            cached = current.display_cache.get('bindings')
            if cached is not None:
                current.expand_binding_contexts(cached[1][1], action == 'expand_binding_contexts')
        elif action == 'feature_category':
            current.select_category(target)
        elif action == 'feature_section':
            current.select_section(target)
        elif action == 'all_subsections':
            current.binding_category_all = True
            current.assignment, current.page = '', 0
        elif action == 'section':
            current.select_section(target)
        elif action == 'page':
            current.page = int(target)
        elif action == 'order':
            current.reorder_section(int(target))
        elif action in TOGGLE_TARGETS:
            row = current.catalog[action][target]
            current.set_enabled(action, target, not row.get('enabled', True))
        elif action == 'delete_section':
            row = current.catalog['sections'][target]
            require(not row.get('required'), 'This section is required')
            require(all(item['section'] != target for table in ('assignments', 'suppressions')
                        for item in current.catalog[table].values()), 'Move or remove entries before deleting this section')
            current.draft.delete('sections', target)
            current.section = ''
            current.changed()
        elif action == 'remove_rule':
            current.draft.delete('suppressions', target)
            current.changed()


class BH_OT_deluxe_undo(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_undo'
    bl_label = 'Undo Keymap Edit'
    bl_description = 'Undo the last staged Blue Hole keymap edit (Cmd+Z or Ctrl+Z)'

    @classmethod
    def poll(cls, context):
        if (_editor is None or not _editor.can_undo or context.area is None
                or context.area.type != 'PREFERENCES' or context.region is None
                or context.region.type != 'WINDOW' or context.preferences.active_section != 'ADDONS'):
            return False
        module = __package__.split('.')[0]
        addon = context.preferences.addons.get(module)
        if addon is None:
            return False
        prefs = addon.preferences
        if (prefs.main_settings != 'GENERAL_ADDON' or prefs.general_addon_settings != 'KEYMAP'
                or not prefs.keymap.deluxe_configured or not prefs.keymap.enable_keymaps
                or not keymaps_register.runtime_keymaps_allowed(context, prefs.keymap)):
            return False
        info = next((addon_utils.module_bl_info(mod)
                     for mod in addon_utils.modules(refresh=False) if mod.__name__ == module), None)
        if not info or not info['show_expanded']:
            return False
        wm = context.window_manager
        if info['support'] not in wm.addon_support or wm.addon_filter not in {'All', 'User', info['category']}:
            return False
        return any(wm.addon_search.casefold() in info[key].casefold() for key in ('name', 'author', 'category'))

    def stage(self, current):
        current.undo()


class BH_OT_deluxe_remove_assignment(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_remove_assignment'
    bl_label = 'Remove Binding'
    bl_description = 'Remove this binding and its command settings'

    assignment: StringProperty(options=HIDDEN)

    def invoke(self, context, _event):
        return self.execute(context)

    def stage(self, current):
        current.require_editable_assignment(self.assignment)
        current.draft.delete('assignments', self.assignment)
        current.assignment = ''
        current.changed()


class BH_OT_deluxe_section(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_section'
    bl_label = 'Name Section'

    section: StringProperty(options=HIDDEN)
    name: StringProperty(name='Section name', maxlen=48, options=TRANSIENT)

    @classmethod
    def description(cls, _context, props):
        return 'Rename this section in the draft' if props.section else 'Add a section to the selected category'

    def invoke(self, context, _event):
        self.name = editor().catalog['sections'][self.section]['label'] if self.section else ''
        return context.window_manager.invoke_props_dialog(self, width=320)

    def stage(self, current):
        current.edit_section(self.name, self.section or None)


def enum_items(operator, key):
    """RNA callbacks can receive OperatorProperties without Python state."""
    return _dialog_choices.get(getattr(operator, 'choice_key', ''), {}).get(key, [])


def bind_choices(operator, items):
    operator.choice_key = uuid4().hex
    _dialog_choices[operator.choice_key] = items


def choices(rows):
    return [(id_, label, description, index) for index, (id_, label, description) in enumerate(rows, 1)]


def assignment_scopes(current, keyconfigs):
    """Include existing Deluxe contexts and the current preset's ordinary keymaps."""
    scopes = {}
    for catalog in (current.catalog, current.defaults):
        for row in catalog['assignments'].values():
            scope = row['scope']
            scopes.setdefault(scope_key(scope), scope)
    for config in (keyconfigs.active, keyconfigs.default):
        if config is None:
            continue
        for map_ in config.keymaps:
            try:
                scope = runtime.capture_scope(map_)
            except runtime._Pending:
                continue
            if not scope.is_modal and not scope.is_tool and ' Tool:' not in scope.name:
                descriptor = dict(name=scope.name, space_type=scope.space_type, region_type=scope.region_type)
                scopes.setdefault(scope_key(descriptor), descriptor)
    return sorted(scopes.values(), key=lambda scope: context_label(scope).casefold())


class BH_OT_deluxe_context(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_context'
    bl_label = 'Keymap Context'
    bl_description = 'Search for the Blender keymap where this assignment should run'
    bl_property = 'scope'

    assignment: StringProperty(options=HIDDEN)
    scope: EnumProperty(items=lambda _self, _context: _context_choices, options=TRANSIENT)

    def invoke(self, context, _event):
        global _context_choices
        try:
            current = editor()
            current.require_editable_assignment(self.assignment)
            scopes = assignment_scopes(current, context.window_manager.keyconfigs)
        except ERRORS as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        # Blender creates a new operator from the search result's RNA properties.
        _context_choices = choices((json.dumps(scope), context_label(scope), '') for scope in scopes)
        context.window_manager.invoke_search_popup(self)
        return {'INTERFACE'}

    def stage(self, current):
        current.require_editable_assignment(self.assignment)
        row = current.catalog['assignments'][self.assignment]
        if self.scope:
            scope = json.loads(self.scope)
            if scope_key(row['scope']) != scope_key(scope):
                shipped = current.defaults['assignments'].get(self.assignment)
                if shipped and scope_key(shipped['scope']) == scope_key(scope):
                    scope = shipped['scope']
                current.draft.update('assignments', self.assignment, scope=scope)
                current.changed()


class BH_OT_deluxe_add_binding(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_add_binding'
    bl_label = 'Add New'
    bl_description = 'Add an unassigned binding in this Blender context and edit it on the right'

    scope: StringProperty(options=HIDDEN)
    section: StringProperty(options=HIDDEN)

    def stage(self, current):
        scope = json.loads(self.scope)
        available = assignment_scopes(current, bpy.context.window_manager.keyconfigs)
        require(any(scope_key(item) == scope_key(scope) for item in available), 'This keymap context is unavailable')
        current.add_binding(scope, self.section)
        state(bpy.context).search = ''


def command_name(current, id_):
    command = current.catalog['commands'][id_]
    meta = current.preview()['commands'][id_]
    if not command.get('properties') or not meta['editable']:
        return meta['label']
    fields = meta['fields']
    variants = [f"{fields[name].get('label', title(name))} {display_value(value)}"
                for name, value in command['properties'].items() if fields.get(name, {}).get('editable')]
    return ' · '.join([meta['label'], *variants[:3]])


def stage_input(current, assignment, event):
    descriptor = event_descriptor(event)
    for name, values in resolver.input_options()['event'].items():
        require(getattr(descriptor, name) in values, f'Unsupported input {name}')
    current.stage_event(assignment, event)


def stage_event_field(current, assignment, field, value):
    row = current.catalog['assignments'][assignment]
    event = dict(current.catalog['events'][row['event']])
    previous_kind = event.get('map_type', map_type(event['type']))
    event[field] = value
    if field == 'map_type':
        require(value in {'KEYBOARD', 'MOUSE'}, 'Choose Keyboard or Mouse')
        if map_type(event['type']) != value:
            event.update(type='A' if value == 'KEYBOARD' else 'LEFTMOUSE',
                         value='PRESS', direction='ANY', repeat=False)
    elif field == 'type':
        event['map_type'] = map_type(value)
        if event['map_type'] != previous_kind:
            event.update(value='PRESS', direction='ANY', repeat=False)
    elif field == 'any':
        event.update(dict.fromkeys(EVENT_MODIFIERS, -1 if value else False))
    if field in {'type', 'map_type', 'value'} and (
            event.get('map_type', map_type(event['type'])) != 'KEYBOARD'
            or event.get('value', 'PRESS') not in {'PRESS', 'ANY'}):
        event['repeat'] = False
    stage_input(current, assignment, event)


class BH_OT_deluxe_inline_edit(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_inline_edit'
    bl_label = 'Edit Keymap Setting'

    assignment: StringProperty(options=HIDDEN)
    command: StringProperty(options=HIDDEN)
    field: StringProperty(options=HIDDEN)

    @classmethod
    def description(cls, _context, props):
        if props.command:
            return 'Reset this command setting to Blender’s default'
        return 'Cycle this modifier through Off, On and Either for this assignment'

    def stage(self, current):
        if self.command:
            assignment = self.assignment
            command = current.catalog['assignments'][self.assignment]['command'] if self.assignment else self.command
            current.edit_command(command, self.field, None, assignment, unset=True)
            return
        require(self.field in EVENT_MODIFIERS, 'Unknown modifier')
        row = current.catalog['assignments'][self.assignment]
        event = current.catalog['events'][row['event']]
        value = event.get(self.field) or False
        stage_event_field(current, self.assignment, self.field, {-1: False, False: True, True: -1}[value])


class BH_OT_deluxe_capture(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_capture'
    bl_label = 'Input Key'

    assignment: StringProperty(options=HIDDEN)
    bl_description = 'Capture a key or mouse button for this binding'

    def invoke(self, context, _event):
        return self.execute(context)

    def execute(self, context):
        try:
            current = editor()
            current.require_editable_assignment(self.assignment)
            event_id = current.catalog['assignments'][self.assignment]['event']
            event_data = current.catalog['events'][event_id]
        except ERRORS as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        self._draft = current.draft
        self._event_id = event_id
        self._event_data = event_data
        self._area = context.area
        current.capture_assignment = self.assignment
        current.message = ''
        context.window_manager.modal_handler_add(self)
        redraw(context)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        if _editor is not None:
            _editor.capture_assignment = ''
        redraw(context)

    def modal(self, context, event):
        if _editor is None or _editor.draft is not self._draft:
            self.cancel(context)
            return {'CANCELLED'}
        if event.type in {'ESC', 'WINDOW_DEACTIVATE'}:
            _editor.message = 'Capture cancelled'
            self.cancel(context)
            return {'CANCELLED'}
        if event.value != 'PRESS' or event.type in {
                'LEFT_SHIFT', 'RIGHT_SHIFT', 'LEFT_CTRL', 'RIGHT_CTRL', 'LEFT_ALT', 'RIGHT_ALT',
                'OSKEY', 'HYPER', 'NONE', 'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'} or event.type.startswith('TIMER'):
            return {'RUNNING_MODAL'}
        self.cancel(context)
        captured = captured_input(self._event_data, event)

        def stage_capture(current):
            row = current.catalog['assignments'].get(self.assignment)
            require(row and row['event'] == self._event_id
                    and current.catalog['events'][self._event_id] == self._event_data,
                    'The shortcut changed. Capture it again.')
            stage_input(current, self.assignment, captured)

        return self.run(context, stage_capture)


class BH_OT_deluxe_field(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_field'
    bl_label = 'Edit Command Setting'

    command: StringProperty(options=HIDDEN)
    choice_key: StringProperty(options=HIDDEN)
    field: StringProperty(options=HIDDEN)
    assignment: StringProperty(options=HIDDEN)
    boolean: BoolProperty(options=TRANSIENT)
    integer: IntProperty(options=TRANSIENT)
    number: FloatProperty(options=TRANSIENT, precision=6)
    string: StringProperty(options=TRANSIENT)
    option: EnumProperty(items=lambda self, _: enum_items(self, 'values'), options=TRANSIENT)
    enabled: BoolProperty(name='Flag enabled', options=TRANSIENT)
    use_default: BoolProperty(name='Use Blender default', description='Remove the explicitly configured value',
                              options=TRANSIENT)

    @classmethod
    def description(cls, _context, props):
        return 'Edit this setting for the selected binding'

    def invoke(self, context, _event):
        current = editor()
        row = current.catalog['commands'][self.command]
        self._meta = current.store.resolver.describe_command(row, include_unset=True)['fields'][self.field]
        if not self._meta['editable']:
            return {'CANCELLED'}
        self._value = row['properties'].get(self.field, self._meta['default'])
        self._draft = current.draft
        self._choices = {'values': choices((value, title(value), '') for value in self._meta['values'])}
        bind_choices(self, self._choices)
        if self._meta['flags']:
            self._choices['component'] = self._choices['values']
            if self._meta['values']:
                self.component = self._meta['values'][0]
                self.select_component(context)
        elif self._meta['shape']:
            shape = self._meta['shape']
            positions = ((i,) for i in range(shape[0])) if len(shape) == 1 else (
                (i, j) for i in range(shape[0]) for j in range(shape[1]))
            self._indices = {str(i): position for i, position in enumerate(positions)}
            self._choices['component'] = choices((id_, ' / '.join(str(i + 1) for i in position), '')
                                                 for id_, position in self._indices.items())
            self.component = '0'
            self.select_component(context)
        else:
            setattr(self, self._property, self._value)
        return context.window_manager.invoke_props_dialog(self, width=440, confirm_text='Stage Setting')

    @property
    def _property(self):
        return {'BOOLEAN': 'boolean', 'INT': 'integer', 'FLOAT': 'number',
                'STRING': 'string', 'ENUM': 'option'}[self._meta['type']]

    def select_component(self, _context):
        if not hasattr(self, '_value') or getattr(self, '_loaded_component', None) == self.component:
            return
        self._loaded_component = self.component
        if self._meta['flags']:
            self.enabled = self.component in self._value
            return
        part = self._value
        for index in self._indices[self.component]:
            part = part[index]
        setattr(self, self._property, part)

    component: EnumProperty(name='Component', items=lambda self, _: enum_items(self, 'component'),
                            update=select_component, options=TRANSIENT)

    def draw(self, _context):
        self.layout.label(text='Blender default: ' + display_value(self._meta['default']))
        if self._meta['explicit']:
            self.layout.prop(self, 'use_default')
        controls = self.layout.column()
        controls.enabled = not self.use_default
        if self._meta['shape'] or self._meta['flags']:
            controls.prop(self, 'component', text='Flag' if self._meta['flags'] else 'Component')
            self.select_component(_context)
        name = 'enabled' if self._meta['flags'] else self._property
        controls.prop(self, name, text=self._meta['label'])

    def stage(self, current):
        require(current.draft is self._draft, 'The draft changed. Reopen the command setting.')
        assignment = self.assignment
        if self.use_default:
            current.edit_command(self.command, self.field, None, assignment, unset=True)
            return
        if self._meta['flags']:
            flags = set(self._value)
            if self.enabled:
                flags.add(self.component)
            else:
                flags.discard(self.component)
            value = sorted(flags)
        elif self._meta['shape']:
            updated = deepcopy(self._value)
            parent = updated
            *indices, final = self._indices[self.component]
            for index in indices:
                parent = parent[index]
            parent[final] = getattr(self, self._property)
            value = updated
        else:
            value = getattr(self, self._property)
        current.edit_command(self.command, self.field, value, assignment)


def operator_button(layout, action, text='', target='', **kwargs):
    op = layout.operator(BH_OT_deluxe_edit.bl_idname, text=text, **kwargs)
    op.action = action
    op.target = target
    return op


def known_replacement(candidate):
    """Offer only the stock ordinary proof already exercised by the runtime."""
    command = {'operator': 'object.select_all', 'properties': {'action': 'DESELECT'}}
    selector = selector_descriptor(candidate['selector'])
    state, _ = resolver.selector_status(selector, resolver.Resolver.target(command))
    return command if state == 'resolved' else None


class BH_OT_deluxe_stage_binding(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_stage_binding'
    bl_label = 'Review Existing Shortcut'
    bl_description = 'Disable an inherited Blender or add-on shortcut with a reversible Blue Hole rule'

    section: StringProperty(options=HIDDEN)
    rule: StringProperty(options=HIDDEN)
    source: StringProperty(options=HIDDEN)
    map_pointer: StringProperty(options=HIDDEN)
    item_pointer: StringProperty(options=HIDDEN)
    item_id: IntProperty(options=HIDDEN)
    signature: StringProperty(options=HIDDEN)
    choice_key: StringProperty(options=HIDDEN)
    destination: EnumProperty(name='Section', items=lambda self, _: enum_items(self, 'section'), options=TRANSIENT)
    open_editor: BoolProperty(options=HIDDEN)
    disable_binding: BoolProperty(name='Disable binding with Blue Hole',
                                  description='Preview a reversible disable, saved to JSON only with Save and Apply Changes',
                                  options=TRANSIENT)
    use_replacement: BoolProperty(name='Replace Select All with Deselect All', options=TRANSIENT)

    def selected(self, context):
        require(self.source in SOURCE_LABELS, 'Choose a keymap source')
        config = getattr(context.window_manager.keyconfigs, self.source)
        require(config is not None, 'The keymap source is no longer available')
        for map_ in config.keymaps:
            if str(map_.as_pointer()) != self.map_pointer:
                continue
            for item in map_.keymap_items:
                if item.id == self.item_id and str(item.as_pointer()) == self.item_pointer:
                    candidate = resolver.capture_candidate(map_, item, self.source)
                    require(json.dumps(candidate['selector'], sort_keys=True) == self.signature,
                            'The binding changed. Pick it again.')
                    return map_, item, candidate
        raise ValueError('The binding is gone. Pick it again.')

    def invoke(self, context, _event):
        try:
            _, _, self._candidate = self.selected(context)
            self._replacement = known_replacement(self._candidate)
            current = editor()
            self._draft = current.draft
            section_choices = choices((id_, f"{current.catalog['categories'][row['category']]['label']} / {row['label']}", '')
                                      for id_, row in current.catalog['sections'].items() if not row.get('required'))
            require(bool(section_choices), 'Add a section for this rule first')
            bind_choices(self, {'section': section_choices})
            self.destination = self.section if self.section in {row[0] for row in section_choices} else section_choices[0][0]
            saved_rule = current.catalog['suppressions'].get(self.rule, {})
            self.disable_binding = bool(self._candidate['can_disable'] and
                                        (saved_rule.get('disable') or not saved_rule))
            self.use_replacement = bool(self._replacement and
                                        current.catalog['suppressions'].get(self.rule, {}).get('replacement'))
        except ERRORS as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, width=480, confirm_text='Stage Rule')

    def draw(self, _context):
        selector = self._candidate['selector']
        target = selector['target']
        self.layout.label(text=f"{target.get('idname', target.get('modal_value'))} · {shortcut(selector['event'])}")
        self.layout.label(text=f"{context_label(selector['scope'])} · {SOURCE_LABELS[selector['source_role']]}")
        self.layout.prop(self, 'destination')
        for name, value in target.get('properties', {}).items():
            self.layout.label(text=f'{title(name)}: {display_value(value)}')
        disable = self.layout.row()
        disable.enabled = self._candidate['can_disable']
        disable.prop(self, 'disable_binding')
        if self._replacement:
            replacement = self.layout.row()
            replacement.enabled = not self.disable_binding
            replacement.prop(self, 'use_replacement')
        if self.disable_binding:
            self.layout.label(text='Previews immediately. Discard restores the saved setup.', icon='INFO')
        elif not self._replacement or not self.use_replacement:
            self.layout.label(text='Review only: this rule will not change the binding.', icon='INFO')
        if not self._candidate['can_disable']:
            self.layout.label(text='Only unchanged, non-modal Blender or add-on bindings can be disabled here.')

    def execute(self, context):
        def stage(current):
            require(current.draft is self._draft, 'The draft changed. Pick the binding again.')
            section = current.catalog['sections'][self.destination]
            require(not section.get('required'), 'This section is required')
            map_, item, candidate = self.selected(context)
            require(not self.disable_binding or candidate['can_disable'], 'This inherited binding cannot be disabled')
            command = known_replacement(candidate) if self.use_replacement and not self.disable_binding else None
            require(not self.use_replacement or self.disable_binding or command is not None, 'Replacement is no longer available')
            replacement = None
            if command:
                replacement = next((id_ for id_, row in current.catalog['commands'].items() if row == command), None)
                if replacement is None:
                    replacement = uuid4().hex
                    current.draft.put('commands', replacement, command)
            current.draft.stage_suppression(self.destination, map_, item, self.source,
                                            replacement=replacement, disable=self.disable_binding, id_=self.rule or None)
            current.changed()

        try:
            result = self.run(context, stage)
            if result == {'FINISHED'} and self.open_editor:
                open_assignment_section(context, self.destination)
            return result
        finally:
            self.release_choices()


def open_assignment_section(context, section):
    prefs = context.preferences.addons[__package__.split('.')[0]].preferences
    prefs.main_settings, prefs.general_addon_settings = 'GENERAL_ADDON', 'KEYMAP'
    bpy.ops.wm.bh_deluxe_edit(action='show_assignments', target=section)
    bpy.ops.preferences.addon_show(module=__package__.split('.')[0])


def native_assignment(current, map_, item):
    owned = runtime.owned_request_for_merged_item(map_, item)
    if owned is not None and ':deluxe-' in owned[0]:
        id_ = resolver.profile_assignment_id(owned[1])
        if id_ in current.catalog['assignments']:
            return id_
    return None


class BH_OT_deluxe_disable_owned_binding(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_disable_owned_binding'
    bl_label = 'Disable Binding with Blue Hole'
    bl_description = ('Disable this Blue Hole addition in its existing binding settings. '
                      'Preview immediately; Save and Apply Changes makes it persistent')

    assignment: StringProperty(options=HIDDEN)
    map_pointer: StringProperty(options=HIDDEN)
    item_pointer: StringProperty(options=HIDDEN)
    item_id: IntProperty(options=HIDDEN)

    def execute(self, context):
        def disable(current):
            config = context.window_manager.keyconfigs.user
            selected = next(((map_, item) for map_ in config.keymaps
                             if str(map_.as_pointer()) == self.map_pointer
                             for item in map_.keymap_items
                             if item.id == self.item_id and str(item.as_pointer()) == self.item_pointer), None)
            require(selected is not None and native_assignment(current, *selected) == self.assignment,
                    'The binding changed. Pick it again.')
            current.set_enabled('assignments', self.assignment, False)

        result = self.run(context, disable)
        if result == {'FINISHED'}:
            current = editor()
            open_assignment_section(context, current.catalog['assignments'][self.assignment]['section'])
            current.assignment = self.assignment
            redraw(context)
        return result


def draw_binding_context(self, context):
    """Extend right-click on native KeyMapItem properties, using the exact row."""
    item = getattr(context, 'button_pointer', None)
    map_ = getattr(context, 'keymap', None)
    if not isinstance(item, bpy.types.KeyMapItem) or map_ is None:
        return
    try:
        current = editor()
        assignment = native_assignment(current, map_, item)
        if assignment is not None:
            current.require_editable_assignment(assignment)
            self.layout.separator()
            op = self.layout.operator(BH_OT_deluxe_disable_owned_binding.bl_idname,
                                      text='Disable Binding with Blue Hole')
            op.assignment = assignment
            op.map_pointer, op.item_pointer, op.item_id = str(map_.as_pointer()), str(item.as_pointer()), item.id
            return
        candidate = resolver.capture_candidate(map_, item, 'user')
        managed = default_bindings.managed_rule(map_, item)
        if managed:
            self.layout.separator()
            operator_button(self.layout, 'restore_default', 'Restore Binding with Blue Hole', managed[0])
        elif candidate['can_disable']:
            self.layout.separator()
            op = self.layout.operator(BH_OT_deluxe_stage_binding.bl_idname, text='Disable Binding with Blue Hole…')
            op.section, op.source, op.open_editor = current.feature_section, 'user', True
            op.map_pointer, op.item_pointer, op.item_id = str(map_.as_pointer()), str(item.as_pointer()), item.id
            op.signature = json.dumps(candidate['selector'], sort_keys=True)
    except (*ERRORS, runtime._Pending):
        return


classes = (
    BH_PG_deluxe_value, BH_PG_deluxe_binding_row, BH_PG_deluxe_editor,
    BH_OT_deluxe_edit, BH_OT_deluxe_remove_assignment, BH_OT_deluxe_inline_edit,
    BH_OT_deluxe_undo, BH_OT_deluxe_section, BH_OT_deluxe_add_binding, BH_OT_deluxe_context,
    BH_OT_deluxe_capture, BH_OT_deluxe_field,
    BH_OT_deluxe_stage_binding, BH_OT_deluxe_disable_owned_binding,
)


def register():
    global _undo_keymap
    for cls in classes:
        bpy.utils.register_class(cls)
    setattr(bpy.types.WindowManager, WM_PROPERTY, PointerProperty(type=BH_PG_deluxe_editor, options=TRANSIENT))
    bpy.types.UI_MT_button_context_menu.append(draw_binding_context)
    config = bpy.context.window_manager.keyconfigs.addon
    if config is not None:
        keymap = config.keymaps.find('Preferences', space_type='PREFERENCES', region_type='WINDOW')
        created = keymap is None
        if created:
            keymap = config.keymaps.new(name='Preferences', space_type='PREFERENCES', region_type='WINDOW')
        items = [keymap.keymap_items.new(BH_OT_deluxe_undo.bl_idname, 'Z', 'PRESS', **{modifier: True})
                 for modifier in ('oskey', 'ctrl')]
        _undo_keymap = config, keymap, created, items


def unregister():
    global _editor, _undo_keymap
    _editor = None
    if _undo_keymap is not None:
        config, keymap, created, items = _undo_keymap
        _undo_keymap = None
        try:
            for item in items:
                keymap.keymap_items.remove(item)
            if created and not keymap.keymap_items:
                config.keymaps.remove(keymap)
        except ReferenceError:
            pass
    bpy.types.UI_MT_button_context_menu.remove(draw_binding_context)
    _dialog_choices.clear()
    _context_choices.clear()
    _inline_enums.clear()
    delattr(bpy.types.WindowManager, WM_PROPERTY)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
