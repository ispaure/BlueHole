"""Blender operators for editing the Deluxe profile in Preferences."""

from copy import deepcopy
from dataclasses import asdict
from itertools import islice
import json
from uuid import uuid4

import bpy
from bpy.props import (BoolProperty, CollectionProperty, EnumProperty, FloatProperty, IntProperty,
                       PointerProperty, StringProperty)

from ....keymaps import deluxe_resolver as resolver, keymap_utils as runtime, keymaps_register, default_bindings
from ....keymaps.deluxe_schema import event_descriptor, require, selector_descriptor, same_value
from .deluxe_editor_model import (Editor, SOURCE_LABELS, captured_input, context_label,
                                 display_value, map_type, shortcut, title, context_id)

_editor = None
_dialog_choices = {}
_context_choices = []
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
    'command': 'Show this command’s settings and the sections that use it',
    'show_command': 'Open the command used by this assignment',
    'show_section_commands': 'Show commands used in this section',
    'show_assignments': 'Show bindings in this subsection',
    'all_bindings': 'Show every binding and clear search, section, command and context filters',
    'command_bindings': 'Show every binding of this command across all sections and contexts',
    'delete_section': 'Stage removal of this empty section',
    'remove_rule': 'Stage removal of this existing-shortcut rule',
    'linked_shortcut': 'Show or hide the sections that share this shortcut',
    'linked_section': 'Show or hide linked assignments in this section',
    'feature_category': 'Show the shortcut groups in this category',
    'feature_section': 'Show this shortcut group’s enable setting and assignments',
}
TOGGLE_TARGETS = {'categories': 'category', 'sections': 'section',
                  'assignments': 'assignment', 'suppressions': 'rule'}
MODIFIER_STATES = [('0', 'Off', 'Require this modifier to be released'),
                   ('1', 'On', 'Require this modifier to be held'),
                   ('-1', 'Either', 'Match whether or not this modifier is held')]


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
            elif control.command:
                command = (_editor.catalog['assignments'][control.assignment]['command']
                           if control.assignment else control.command)
                assignment = control.assignment if state(context).command_edit_scope == 'SINGLE' else ''
                _editor.edit_command(command, control.field, value, assignment)
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
    boolean: BoolProperty(description='Stage a change to this setting', update=inline_update('boolean'), options=TRANSIENT)
    integer: IntProperty(description='Stage a value for the shared command', update=inline_update('integer'), options=TRANSIENT)
    number: FloatProperty(description='Stage a value for the shared command', update=inline_update('number'),
                          precision=6, options=TRANSIENT)
    string: StringProperty(description='Stage a value for the shared command', update=inline_update('string'), options=TRANSIENT)
    option: EnumProperty(description='Stage a choice for this setting', items=inline_options,
                         update=inline_update('option'), options=TRANSIENT)


class BH_PG_deluxe_editor(bpy.types.PropertyGroup):
    def reset_page(self, _context):
        if _editor is not None:
            _editor.page = 0

    def switch_tab(self, context):
        self.search = ''
        self.reset_page(context)

    tab: EnumProperty(items=[('BINDINGS', 'Bindings', 'Browse and edit keymap bindings'),
                            ('COMMANDS', 'Commands', 'Create and edit reusable commands')],
                      options=TRANSIENT, update=switch_tab)
    search_mode: EnumProperty(items=[('NAME', 'Name', 'Search for a command or keymap name'),
                                    ('KEY', 'Key-Binding', 'Type a shortcut, such as Shift F10')],
                              options=TRANSIENT, update=switch_tab)
    search: StringProperty(name='Search', description='Filter the current list using the selected search mode',
                           options=TRANSIENT, update=reset_page)
    show_extra_fields: BoolProperty(name='Show additional Blender settings',
                                    description='Show command settings that currently use Blender’s defaults', options=TRANSIENT)
    live_search: StringProperty(name='Search current bindings',
                                description='Filter existing bindings by command, shortcut or keymap name', options=TRANSIENT,
                                update=lambda self, _context: setattr(self, 'live_page', 0))
    live_source: EnumProperty(name='Source', description='Choose which Blender keyconfig to browse',
                              items=[(key, label, '') for key, label in SOURCE_LABELS.items()],
                              options=TRANSIENT, update=lambda self, _context: setattr(self, 'live_page', 0))
    live_page: IntProperty(description='Choose the page of matching bindings, starting at zero', min=0, options=TRANSIENT)
    command_edit_scope: EnumProperty(items=[('SINGLE', 'This Binding Only', 'Separate settings when this command is shared'),
                                               ('SHARED', 'All Linked Bindings', 'Preview changes everywhere this command is used')],
                                     options=TRANSIENT)
    values: CollectionProperty(type=BH_PG_deluxe_value, options=TRANSIENT)


def state(context):
    return getattr(context.window_manager, WM_PROPERTY)


def inline_value(view, field, prop, value, *, command='', assignment='', table='', entry='', items=()):
    """Bind a native widget to transient RNA, with changes staged in the draft."""
    global _syncing_inline
    name = f'{table}:{entry}:{field}' if table else f'{command}:{assignment}:{field}'
    control = view.values.get(name)
    _syncing_inline = True
    try:
        if control is None:
            control = view.values.add()
            control.name = name
            control.table, control.entry = table, entry
            control.command, control.assignment, control.field = command, assignment, field
        if items:
            control.choices_key = repr(items)
            if control.choices_key not in _inline_enums:
                _inline_enums[control.choices_key] = choices(
                    (item, title(item), '') if isinstance(item, str) else item for item in items)
        if getattr(control, prop) != value:
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
        if action in ('command_category', 'command_section'):
            group = 'category' if action == 'command_category' else 'section'
            return f'Filter commands by this {group}' if target else f'Clear the command {group} filter'
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
                return f"Show assignment details for {event} in {context_label(row['scope'])}"
        return EDIT_DESCRIPTIONS.get(action, cls.bl_label)

    def invoke(self, context, event):
        if self.action in {'reset', 'reload', 'delete_section', 'remove_command'}:
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
        if self.action in {'show_assignments', 'all_bindings', 'command_bindings'}:
            def show_bindings(current):
                view = state(context)
                view.tab, view.search = 'BINDINGS', ''
                current.show_all_bindings(self.target if self.action == 'command_bindings' else '')
                if self.action == 'show_assignments':
                    current.select_section(self.target)
            return self.run(context, show_bindings)
        if self.action in {'show_command', 'show_section_commands', 'command_category', 'command_section'}:
            def show(current):
                view = state(context)
                if self.action in {'command_category', 'command_section'}:
                    if self.action == 'command_category':
                        current.command_category, current.command_section = self.target, ''
                    else:
                        current.command_section = self.target
                    view.search = ''
                    current.page = 0
                    return
                view.tab = 'COMMANDS'
                assignment = current.catalog['assignments'].get(self.target, {})
                section = assignment.get('section', self.target)
                current.command_section = '' if assignment else section
                current.command_category = '' if assignment else current.catalog['sections'][section]['category']
                current.command = assignment.get('command', '')
                current.focus_command = bool(assignment)
                view.search = ''
                current.page = 0

            return self.run(context, show)
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
        elif action in {'assignment', 'command'}:
            setattr(current, action, target)
        elif action == 'linked_shortcut':
            current.expanded_shortcut = '' if current.expanded_shortcut == target else target
            current.expanded_linked_section = ''
        elif action == 'linked_section':
            current.expanded_linked_section = '' if current.expanded_linked_section == target else target
        elif action == 'feature_category':
            current.select_category(target)
        elif action == 'feature_section':
            current.select_section(target)
        elif action == 'all_subsections':
            current.binding_category_all = True
            current.assignment, current.page = '', 0
        elif action == 'clear_context':
            current.binding_context = ''
            current.page = 0
        elif action == 'clear_command_filter':
            current.binding_command = ''
            current.page = 0
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
        elif action == 'remove_command':
            current.remove_command(target)
        elif action == 'remove_rule':
            current.draft.delete('suppressions', target)
            current.changed()


class BH_OT_deluxe_remove_assignment(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_remove_assignment'
    bl_label = 'Remove Binding'
    bl_description = 'Stage removal of this assignment and keep its command and linked assignments'

    assignment: StringProperty(options=HIDDEN)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

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


def scope_key(scope):
    return scope['name'], scope.get('space_type', 'EMPTY'), scope.get('region_type', 'WINDOW')


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


class BH_OT_deluxe_filter_context(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_filter_context'
    bl_label = 'Filter Blender Context'
    bl_property = 'context'

    choice_key: StringProperty(options=HIDDEN)
    context: EnumProperty(items=lambda self, _: enum_items(self, 'context'), options=TRANSIENT)

    def invoke(self, context, _event):
        current = editor()
        bind_choices(self, {'context': choices([('ALL', 'All Contexts', 'Include every Blender keymap'),
            *((id_, context_label(scope), scope['name']) for id_, scope in current.binding_contexts().items())])})
        self.context = current.binding_context or 'ALL'
        context.window_manager.invoke_search_popup(self)
        return {'INTERFACE'}

    def stage(self, current):
        current.binding_context = '' if self.context == 'ALL' else self.context
        current.assignment, current.page = '', 0
        current.ensure_selection()


class BH_OT_deluxe_command(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_command'
    bl_label = 'Create Command'

    source: StringProperty(options=HIDDEN)
    choice_key: StringProperty(options=HIDDEN)
    operator_id: EnumProperty(name='Operator', items=lambda self, _: enum_items(self, 'operator'), options=TRANSIENT)
    label: StringProperty(name='Name', description='Optional descriptive name for this command variation', maxlen=128, options=TRANSIENT)

    def invoke(self, context, _event):
        current = editor()
        self._draft = current.draft
        if self.source:
            source = current.catalog['commands'][self.source]
            self._source = deepcopy(source)
            self.label = current.preview()['commands'][self.source]['label'] + ' Copy'
        else:
            operators = []
            for namespace in dir(bpy.ops):
                if namespace.startswith('_'):
                    continue
                for name in dir(getattr(bpy.ops, namespace)):
                    id_ = f'{namespace}.{name}'
                    if name.startswith('_') or id_ in resolver.ROUTING_OPERATORS or '.bh_' in id_:
                        continue
                    rna = resolver._operator_rna(id_)
                    variants = current.store.resolver.commands.get(id_, ())
                    if rna is not None and not any(row.get('provider') for row in variants):
                        operators.append((id_, f'{rna.name} · {id_}', rna.description or id_))
            bind_choices(self, {'operator': choices(sorted(operators, key=lambda row: row[1].casefold()))})
            if not operators:
                self.report({'ERROR'}, 'No registered operators available')
                self.release_choices()
                return {'CANCELLED'}
            self.operator_id = self._choices_first()
            self.label = ''
        return context.window_manager.invoke_props_dialog(self, width=550, confirm_text='Create Command')

    def _choices_first(self):
        return enum_items(self, 'operator')[0][0]

    def draw(self, _context):
        if self.source:
            self.layout.label(text='Duplicate: ' + command_name(editor(), self.source))
        else:
            self.layout.prop(self, 'operator_id')
        self.layout.prop(self, 'label')
        self.layout.label(text='Configure its settings in Commands, then add a binding.')

    def stage(self, current):
        require(current.draft is self._draft, 'The draft changed. Reopen the command dialog.')
        if self.source:
            require(same_value(current.catalog['commands'].get(self.source), self._source),
                    'The source command changed. Duplicate it again.')
        current.create_command(operator=self.operator_id if not self.source else '', label=self.label, source=self.source)
        view = state(bpy.context)
        view.tab, view.search = 'COMMANDS', ''


class BH_OT_deluxe_mapping(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_mapping'
    bl_label = 'Binding Settings'

    assignment: StringProperty(options=HIDDEN)
    command_hint: StringProperty(options=HIDDEN)
    choice_key: StringProperty(options=HIDDEN)
    section: EnumProperty(name='Section', items=lambda self, _: enum_items(self, 'section'), options=TRANSIENT)
    command: EnumProperty(name='Command', items=lambda self, _: enum_items(self, 'command'), options=TRANSIENT)
    event_id: EnumProperty(name='Keymap Binding', items=lambda self, _: enum_items(self, 'event'), options=TRANSIENT)
    scope_id: EnumProperty(name='Blender Context', items=lambda self, _: enum_items(self, 'scope'), options=TRANSIENT)

    @classmethod
    def description(cls, _context, props):
        if props.assignment:
            return 'Change this binding’s section, command, shortcut or Blender keymap'
        return 'Create a binding from an existing shortcut, a command and a Blender keymap'

    def invoke(self, context, _event):
        current = editor()
        catalog = current.catalog
        row = catalog['assignments'].get(self.assignment)
        if self.assignment:
            require(row is not None, 'The assignment changed. Select it again.')
            current.require_editable_assignment(self.assignment)
        metadata = current.preview()['commands']
        self._scopes = {str(index): scope for index, scope in
                        enumerate(assignment_scopes(current, context.window_manager.keyconfigs))}
        self._choices = {
            'section': choices((id_, f"{catalog['categories'][section['category']]['label']} / {section['label']}", '')
                               for id_, section in catalog['sections'].items() if not section.get('required')),
            'command': choices(sorted(((id_, command_name(current, id_) + ' · ' + catalog['commands'][id_]['operator'],
                                         f"{len(current.draft.uses('commands', id_))} bindings · {meta['availability']}")
                                       for id_, meta in metadata.items() if 'operator' in catalog['commands'][id_]),
                                      key=lambda item: item[1].casefold())),
            'event': choices(sorted(((id_, shortcut(event), f"{len(current.draft.uses('events', id_))} assignments")
                                      for id_, event in catalog['events'].items()), key=lambda item: item[1].casefold())),
            'scope': choices((id_, context_label(scope), '') for id_, scope in self._scopes.items()),
        }
        if not all(self._choices.values()):
            self.report({'ERROR'}, 'An assignment needs a section, command, shortcut and keymap')
            return {'CANCELLED'}
        bind_choices(self, self._choices)
        section = row['section'] if row else current.section
        self.section = (section if any(choice[0] == section for choice in self._choices['section'])
                        else self._choices['section'][0][0])
        self.command = (row['command'] if row else self.command_hint if self.command_hint in catalog['commands']
                        else self._choices['command'][0][0])
        self.event_id = row['event'] if row else self._choices['event'][0][0]
        self.scope_id = (next(id_ for id_, scope in self._scopes.items() if scope_key(scope) == scope_key(row['scope']))
                         if row else self._choices['scope'][0][0])
        if not row and current.binding_context:
            self.scope_id = next((id_ for id_, scope in self._scopes.items() if context_id(scope) == current.binding_context), self.scope_id)
        self._draft = current.draft
        self._initial = row
        return context.window_manager.invoke_props_dialog(self, width=500, confirm_text='Add Binding' if not self.assignment else 'Apply Binding Edit')

    def draw(self, _context):
        for name in ('section', 'command', 'event_id', 'scope_id'):
            self.layout.prop(self, name)
        uses = len(editor().draft.uses('commands', self.command))
        self.layout.label(text=f'Shares command settings with {uses} existing bindings')
        metadata = editor().preview()['commands'].get(self.command, {})
        if metadata.get('dependency'):
            self.layout.label(text=f"{metadata['dependency']} · {title(metadata['availability'])}")

    def stage(self, current):
        require(current.draft is self._draft, 'The draft changed. Reopen assignment settings.')
        scope = self._scopes[self.scope_id]
        if self.assignment:
            current.require_editable_assignment(self.assignment)
            require(current.catalog['assignments'][self.assignment] == self._initial,
                    'The assignment changed. Reopen assignment settings.')
            if scope_key(scope) == scope_key(self._initial['scope']):
                scope = self._initial['scope']
            current.draft.update('assignments', self.assignment, section=self.section,
                                 command=self.command, event=self.event_id, scope=scope)
        else:
            self.assignment = current.draft.add_assignment(self.section, self.event_id, self.command, scope)
        current.changed()
        current.select_section(self.section)
        current.binding_context = current.binding_command = ''
        current.assignment = self.assignment
        view = state(bpy.context)
        view.tab, view.search = 'BINDINGS', ''


def command_name(current, id_):
    command = current.catalog['commands'][id_]
    meta = current.preview()['commands'][id_]
    if not command.get('properties') or not meta['editable']:
        return meta['label']
    fields = meta['fields']
    variants = [f"{fields[name].get('label', title(name))} {display_value(value)}"
                for name, value in command['properties'].items() if fields.get(name, {}).get('editable')]
    return ' · '.join([meta['label'], *variants[:3]])


class BH_OT_deluxe_shortcut(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_shortcut'
    bl_label = 'Edit Shortcut'

    assignment: StringProperty(options=HIDDEN)
    choice_key: StringProperty(options=HIDDEN)
    key: EnumProperty(name='Key', description='Choose the key or input button that triggers the shortcut',
                      items=lambda self, _: enum_items(self, 'key'), options=TRANSIENT)
    phase: EnumProperty(name='Phase', description='Choose when the input triggers the shortcut',
                        items=lambda self, _: enum_items(self, 'phase'), options=TRANSIENT)
    direction: EnumProperty(name='Direction', description='Choose which drag direction triggers the shortcut',
                            items=lambda self, _: enum_items(self, 'direction'), options=TRANSIENT)
    key_modifier: EnumProperty(name='Key modifier', description='Choose an additional key to hold',
                               items=lambda self, _: enum_items(self, 'modifier'), options=TRANSIENT)
    repeat: BoolProperty(name='Repeat', description='Allow a held key to trigger the shortcut repeatedly', options=TRANSIENT)
    any_modifier: BoolProperty(name='Any modifier', description='Match the input regardless of which modifiers are held',
                               options=TRANSIENT)

    @classmethod
    def description(cls, _context, props):
        if props.assignment:
            return 'Edit the key, trigger, direction and modifiers for this assignment only'
        return 'Create a reusable shortcut for the draft. Add an assignment to make it run a command'

    def invoke(self, context, _event):
        current = editor()
        if self.assignment:
            current.require_editable_assignment(self.assignment)
            row = current.catalog['assignments'][self.assignment]
            initial = current.catalog['events'][row['event']]
        else:
            initial = {'type': 'F'}
        self._original = initial
        options = resolver.input_options()['event']
        self._choices = {field: choices((value, title(value), '') for value in options[key])
                         for field, key in (('key', 'type'), ('phase', 'value'),
                                            ('modifier', 'key_modifier'), ('direction', 'direction'))}
        bind_choices(self, self._choices)
        self.key = initial['type']
        self.phase = initial.get('value', 'PRESS')
        self.direction = initial.get('direction', 'ANY')
        self.key_modifier = initial.get('key_modifier', 'NONE')
        self.repeat = initial.get('repeat', False)
        self.any_modifier = initial.get('any', False)
        for key in ('shift', 'ctrl', 'alt', 'oskey', 'hyper'):
            setattr(self, key, str(int(initial.get(key) or 0)))
        self._draft = current.draft
        return context.window_manager.invoke_props_dialog(self, width=475, confirm_text='Stage Shortcut')

    def draw(self, _context):
        for key in ('key', 'phase', 'direction', 'key_modifier'):
            self.layout.prop(self, key)
        row = self.layout.row(align=True)
        row.prop(self, 'repeat')
        row.prop(self, 'any_modifier')
        for key in ('shift', 'ctrl', 'alt', 'oskey', 'hyper'):
            self.layout.prop(self, key)

    def stage(self, current):
        require(current.draft is self._draft, 'The draft changed. Reopen the shortcut.')
        event = dict(type=self.key, value=self.phase, direction=self.direction,
                     key_modifier=self.key_modifier, repeat=self.repeat, any=self.any_modifier,
                     map_type=(self._original.get('map_type', map_type(self.key))
                               if self.key == self._original['type'] else map_type(self.key)))
        event.update({key: int(getattr(self, key)) for key in ('shift', 'ctrl', 'alt', 'oskey', 'hyper')})
        if self.any_modifier:
            event.update({key: -1 for key in ('shift', 'ctrl', 'alt', 'oskey', 'hyper')})
        stage_input(current, self.assignment, event, False)


for _modifier in ('shift', 'ctrl', 'alt', 'oskey', 'hyper'):
    BH_OT_deluxe_shortcut.__annotations__[_modifier] = EnumProperty(
        name={'ctrl': 'Ctrl', 'oskey': 'OS Key'}.get(_modifier, _modifier.title()),
        items=MODIFIER_STATES, options=TRANSIENT)


def stage_input(current, assignment, event, shared):
    descriptor = event_descriptor(event)
    for name, values in resolver.input_options()['event'].items():
        require(getattr(descriptor, name) in values, f'Unsupported input {name}')
    if assignment:
        current.stage_event(assignment, event, shared=shared)
    else:
        current.draft.put('events', uuid4().hex, event)
        current.changed('Shortcut added to the library')


def stage_event_field(current, assignment, field, value):
    row = current.catalog['assignments'][assignment]
    event = dict(current.catalog['events'][row['event']])
    event[field] = value
    if field == 'map_type':
        require(value in {'KEYBOARD', 'MOUSE'}, 'Choose Keyboard or Mouse')
        if map_type(event['type']) != value:
            event.update(type='A' if value == 'KEYBOARD' else 'LEFTMOUSE',
                         value='PRESS', direction='ANY', repeat=False)
    elif field == 'type':
        event['map_type'] = map_type(value)
    elif field == 'any':
        event.update(dict.fromkeys(EVENT_MODIFIERS, -1 if value else False))
    stage_input(current, assignment, event, False)


class BH_OT_deluxe_inline_edit(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_inline_edit'
    bl_label = 'Edit Keymap Setting'

    assignment: StringProperty(options=HIDDEN)
    command: StringProperty(options=HIDDEN)
    field: StringProperty(options=HIDDEN)

    @classmethod
    def description(cls, _context, props):
        if props.command:
            return 'Use Blender’s default for this setting across all assignments that share the command'
        return 'Cycle this modifier through Off, On and Either for this assignment'

    def stage(self, current):
        if self.command:
            assignment = self.assignment if state(bpy.context).command_edit_scope == 'SINGLE' else ''
            command = current.catalog['assignments'][self.assignment]['command'] if self.assignment else self.command
            current.edit_command(command, self.field, None, assignment, unset=True)
            return
        require(self.field in EVENT_MODIFIERS, 'Unknown modifier')
        row = current.catalog['assignments'][self.assignment]
        event = current.catalog['events'][row['event']]
        value = event.get(self.field) or False
        stage_event_field(current, self.assignment, self.field, {-1: False, False: True, True: -1}[value])


def draw_uses(layout, current, table, assignment, shared=True):
    row = current.catalog['assignments'][assignment]
    key = 'event' if table == 'events' else 'command'
    ids = current.draft.uses(table, row[key]) if shared else (assignment,)
    layout.label(text=f'{len(ids)} affected assignment{"s" if len(ids) != 1 else ""}')
    for scope in dict.fromkeys(context_label(current.catalog['assignments'][id_]['scope']) for id_ in ids):
        layout.label(text=scope, icon='DOT')


class BH_OT_deluxe_capture(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_capture'
    bl_label = 'Input Key'

    assignment: StringProperty(options=HIDDEN)
    shared: BoolProperty(options=HIDDEN)

    @classmethod
    def description(cls, _context, props):
        if props.shared:
            return 'Capture a key or mouse button for all linked assignments, including disabled ones'
        return 'Capture a key or mouse button for this assignment only'

    def invoke(self, context, event):
        if not self.shared:
            return self.execute(context)
        try:
            current = editor()
            event_id = current.catalog['assignments'][self.assignment]['event']
            linked = current.draft.uses('events', event_id)
            require(len(linked) > 1, 'This shortcut is no longer shared')
            preview = current.preview()
            for id_ in linked:
                current.require_editable_assignment(id_)
        except ERRORS as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        inactive = sum(not (preview['assignments'][id_]['eligible'] and preview['assignments'][id_]['active'])
                       for id_ in linked)
        message = f'Capture a new shortcut for all {len(linked)} linked assignments.'
        if inactive:
            noun = 'assignment is' if inactive == 1 else 'assignments are'
            message += f' {inactive} {noun} currently inactive and will also change.'
        self._confirmed = current.draft, event_id, current.catalog['events'][event_id], linked
        return context.window_manager.invoke_confirm(
            self, event, title='Change Shared Shortcut', message=message,
            confirm_text=f'Change All {len(linked)}')

    def execute(self, context):
        try:
            current = editor()
            current.require_editable_assignment(self.assignment)
            event_id = current.catalog['assignments'][self.assignment]['event']
            event_data = current.catalog['events'][event_id]
            linked = current.draft.uses('events', event_id)
            if self.shared:
                require(getattr(self, '_confirmed', None) == (current.draft, event_id, event_data, linked),
                        'Confirm the linked assignments before changing the shortcut')
                for id_ in linked:
                    current.require_editable_assignment(id_)
        except ERRORS as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        self._draft = current.draft
        self._event_id = event_id
        self._event_data = event_data
        self._linked = linked
        self._area = context.area
        current.capture_assignment = self.assignment
        current.capture_shared = self.shared
        current.message = ''
        context.window_manager.modal_handler_add(self)
        redraw(context)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        if _editor is not None:
            _editor.capture_assignment = ''
            _editor.capture_shared = False
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
            if self.shared:
                require(current.draft.uses('events', self._event_id) == self._linked,
                        'The linked assignments changed. Capture the shortcut again.')
            stage_input(current, self.assignment, captured, self.shared)

        return self.run(context, stage_capture)


class BH_OT_deluxe_field(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_field'
    bl_label = 'Edit Command Setting'

    command: StringProperty(options=HIDDEN)
    choice_key: StringProperty(options=HIDDEN)
    field: StringProperty(options=HIDDEN)
    assignment: StringProperty(options=HIDDEN)
    single: BoolProperty(name='This binding only', default=True,
                         description='Give this assignment a separate command with its own settings', options=TRANSIENT)
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
        if props.assignment:
            return 'Edit this setting, with the option to make a separate command for this assignment'
        return 'Edit this setting for every assignment that uses this command'

    def invoke(self, context, _event):
        current = editor()
        self.single = bool(self.assignment) and state(context).command_edit_scope == 'SINGLE'
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
        current = editor()
        if self.assignment:
            self.layout.prop(self, 'single')
            draw_uses(self.layout, current, 'commands', self.assignment, not self.single)
        else:
            ids = current.draft.uses('commands', self.command)
            if ids:
                draw_uses(self.layout, current, 'commands', ids[0])
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
        assignment = self.assignment if self.single else ''
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


LIVE_PAGE = 10


def live_rows(context, source, search):
    """Yield searchable live rows, including signatures for exact revalidation."""
    config = getattr(context.window_manager.keyconfigs, source, None)
    if config is None:
        return
    terms = search.casefold().split()
    for map_ in config.keymaps:
        scope = runtime.capture_scope(map_)
        scope_name = context_label(asdict(scope))
        for item in map_.keymap_items:
            operator = item.propvalue if scope.is_modal else item.idname
            label = item.name or operator
            if not operator:
                continue
            try:
                event = asdict(runtime.capture_event(item))
            except runtime._Pending:
                continue
            key = shortcut(event)
            haystack = f'{scope_name} {operator} {label} {key}'.casefold()
            if all(term in haystack for term in terms):
                yield map_, item, label, key, scope_name


def known_replacement(candidate):
    """Offer only the stock ordinary proof already exercised by the runtime."""
    command = {'operator': 'object.select_all', 'properties': {'action': 'DESELECT'}}
    selector = selector_descriptor(candidate['selector'])
    state, _ = resolver.selector_status(selector, resolver.Resolver.target(command))
    return command if state == 'resolved' else None


class BH_OT_deluxe_binding_picker(bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_binding_picker'
    bl_label = 'Find Existing Shortcut'

    section: StringProperty(options=HIDDEN)
    rule: StringProperty(options=HIDDEN)
    defaults: BoolProperty(options=HIDDEN)

    @classmethod
    def description(cls, _context, props):
        if props.rule:
            return 'Choose a different existing binding for this rule'
        return 'Find an existing binding to review and stage a rule. Only supported replacements affect the active keymap'

    def invoke(self, context, _event):
        view = state(context)
        view.live_page = 0
        row = editor().catalog['suppressions'].get(self.rule)
        if row:
            selector = row['selector']
            view.live_source = selector['source_role'] if selector['source_role'] in SOURCE_LABELS else 'default'
            view.live_search = selector['scope']['name']
        else:
            view.live_search = ''
            if self.defaults:
                view.live_source = 'default'
        return context.window_manager.invoke_popup(self, width=650)

    def execute(self, _context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        view = state(context)
        row = layout.row(align=True)
        row.prop(view, 'live_source', text='')
        row.prop(view, 'live_search', text='', icon='VIEWZOOM')
        start = view.live_page * LIVE_PAGE
        items = tuple(islice(live_rows(context, view.live_source, view.live_search), start, start + LIVE_PAGE + 1))
        if not items:
            layout.label(text='No matching bindings')
        for map_, item, label, key, scope in items[:LIVE_PAGE]:
            try:
                candidate = resolver.capture_candidate(map_, item, view.live_source)
            except (ValueError, ReferenceError):
                continue
            box = layout.column(align=True)
            op = box.operator(BH_OT_deluxe_stage_binding.bl_idname, text=f'{label}  ·  {key}', icon='EVENT_A')
            op.section, op.rule, op.source = self.section, self.rule, view.live_source
            op.map_pointer, op.item_pointer = str(map_.as_pointer()), str(item.as_pointer())
            op.item_id = item.id
            # Include the complete selector in the button identity to catch native pointer reuse.
            op.signature = json.dumps(candidate['selector'], sort_keys=True)
            status = 'Active' if item.active else 'Inactive'
            props = candidate['selector']['target'].get('properties', {})
            details = ', '.join(f'{title(key)} {display_value(value)}' for key, value in props.items())
            box.label(text=f'{scope} · {status}' + (f' · {details}' if details else ''))
            if candidate['status'] in {'ambiguous', 'missing'}:
                box.label(text=title(candidate['status']), icon='INFO')
        row = layout.row(align=True)
        row.prop(view, 'live_page', text='Page')
        if len(items) > LIVE_PAGE:
            row.label(text='More results available')


class BH_OT_deluxe_stage_binding(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_stage_binding'
    bl_label = 'Review Existing Shortcut'
    bl_description = 'Inspect the binding and review whether a supported replacement is available'

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
            self.layout.label(text='Only unchanged, non-modal Blender defaults can be disabled here.')

    def execute(self, context):
        def stage(current):
            require(current.draft is self._draft, 'The draft changed. Pick the binding again.')
            section = current.catalog['sections'][self.destination]
            require(not section.get('required'), 'This section is required')
            map_, item, candidate = self.selected(context)
            require(not self.disable_binding or candidate['can_disable'], 'This default binding cannot be disabled')
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


def draw_binding_context(self, context):
    """Extend right-click on native KeyMapItem properties, using the exact row."""
    item = getattr(context, 'button_pointer', None)
    map_ = getattr(context, 'keymap', None)
    if not isinstance(item, bpy.types.KeyMapItem) or map_ is None:
        return
    try:
        current = editor()
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
    BH_PG_deluxe_value, BH_PG_deluxe_editor, BH_OT_deluxe_edit, BH_OT_deluxe_remove_assignment, BH_OT_deluxe_inline_edit,
    BH_OT_deluxe_section, BH_OT_deluxe_mapping, BH_OT_deluxe_context,
    BH_OT_deluxe_filter_context, BH_OT_deluxe_command,
    BH_OT_deluxe_shortcut, BH_OT_deluxe_capture, BH_OT_deluxe_field,
    BH_OT_deluxe_binding_picker, BH_OT_deluxe_stage_binding,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    setattr(bpy.types.WindowManager, WM_PROPERTY, PointerProperty(type=BH_PG_deluxe_editor, options=TRANSIENT))
    bpy.types.UI_MT_button_context_menu.append(draw_binding_context)


def unregister():
    global _editor
    _editor = None
    bpy.types.UI_MT_button_context_menu.remove(draw_binding_context)
    _dialog_choices.clear()
    _context_choices.clear()
    _inline_enums.clear()
    delattr(bpy.types.WindowManager, WM_PROPERTY)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
