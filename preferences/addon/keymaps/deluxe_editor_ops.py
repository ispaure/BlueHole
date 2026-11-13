"""Blender operators for editing the Deluxe profile in Preferences."""

from copy import deepcopy
from dataclasses import asdict
from itertools import islice
import json
from uuid import uuid4

import bpy
from bpy.props import (BoolProperty, EnumProperty, FloatProperty, IntProperty,
                       PointerProperty, StringProperty)

from ....keymaps import deluxe_resolver as resolver, keymap_utils as runtime, keymaps_register
from ....keymaps.deluxe_schema import event_descriptor, require, selector_descriptor
from .deluxe_editor_model import Editor, SOURCE_LABELS, context_label, display_value, map_type, shortcut, title

_editor = None
_dialog_choices = {}
WM_PROPERTY = 'bh_deluxe_editor'
ERRORS = (ValueError, KeyError, IndexError, OSError, RuntimeError, ReferenceError)
HIDDEN = {'HIDDEN', 'SKIP_SAVE'}
TRANSIENT = {'SKIP_SAVE'}


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


class BH_PG_deluxe_editor(bpy.types.PropertyGroup):
    def reset_page(self, _context):
        if _editor is not None:
            _editor.page = 0

    tab: EnumProperty(items=[('ASSIGNMENTS', 'Assignments', ''), ('COMMANDS', 'Commands', '')],
                      options=TRANSIENT, update=reset_page)
    search: StringProperty(name='Search', options=TRANSIENT, update=reset_page)
    live_search: StringProperty(name='Search current bindings', options=TRANSIENT,
                                update=lambda self, _context: setattr(self, 'live_page', 0))
    live_source: EnumProperty(name='Source', items=[(key, label, '') for key, label in SOURCE_LABELS.items()],
                              options=TRANSIENT, update=lambda self, _context: setattr(self, 'live_page', 0))
    live_page: IntProperty(min=0, options=TRANSIENT)


def state(context):
    return getattr(context.window_manager, WM_PROPERTY)


class BH_OT_deluxe_edit(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_edit'
    bl_label = 'Edit Deluxe Profile'

    action: StringProperty(options=HIDDEN)
    target: StringProperty(options=HIDDEN)

    def invoke(self, context, event):
        if self.action in {'reset', 'reload', 'delete_section', 'remove_assignment'}:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        if self.action == 'show_command':
            def show(current):
                view = state(context)
                view.tab = 'COMMANDS'
                view.search = command_name(current, current.catalog['assignments'][self.target]['command'])
                current.command = current.catalog['assignments'][self.target]['command']

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
            current.changed('Shipped defaults staged')
        elif action == 'category':
            current.category, current.section, current.assignment = target, '', ''
            current.page = 0
        elif action in {'section', 'assignment', 'command'}:
            setattr(current, action, target)
            if action == 'section':
                current.assignment = ''
                current.page = 0
        elif action == 'page':
            current.page = int(target)
        elif action == 'order':
            current.reorder_section(int(target))
        elif action in {'categories', 'sections', 'assignments', 'suppressions'}:
            if action == 'assignments':
                current.require_editable_assignment(target)
            row = current.catalog[action][target]
            require(not row.get('required'), 'This section is required')
            current.draft.update(action, target, enabled=not row.get('enabled', True))
            current.changed()
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
        elif action == 'remove_assignment':
            current.require_editable_assignment(target)
            current.draft.delete('assignments', target)
            current.assignment = ''
            current.changed()


class BH_OT_deluxe_section(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_section'
    bl_label = 'Name Section'

    section: StringProperty(options=HIDDEN)
    name: StringProperty(name='Section name', maxlen=48, options=TRANSIENT)

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


class BH_OT_deluxe_mapping(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_mapping'
    bl_label = 'Assignment Settings'

    assignment: StringProperty(options=HIDDEN)
    choice_key: StringProperty(options=HIDDEN)
    section: EnumProperty(name='Section', items=lambda self, _: enum_items(self, 'section'), options=TRANSIENT)
    command: EnumProperty(name='Command', items=lambda self, _: enum_items(self, 'command'), options=TRANSIENT)
    event_id: EnumProperty(name='Shortcut', items=lambda self, _: enum_items(self, 'event'), options=TRANSIENT)
    scope_id: EnumProperty(name='Keymap', items=lambda self, _: enum_items(self, 'scope'), options=TRANSIENT)

    def invoke(self, context, _event):
        current = editor()
        catalog = current.catalog
        row = catalog['assignments'].get(self.assignment)
        if self.assignment:
            require(row is not None, 'The assignment changed. Select it again.')
            current.require_editable_assignment(self.assignment)
        metadata = current.preview()['commands']
        self._scopes = {}
        for item in (*current.defaults['assignments'].values(), *catalog['assignments'].values()):
            scope = item['scope']
            if scope not in self._scopes.values():
                self._scopes[str(len(self._scopes))] = scope
        self._choices = {
            'section': choices((id_, f"{catalog['categories'][section['category']]['label']} / {section['label']}", '')
                               for id_, section in catalog['sections'].items() if not section.get('required')),
            'command': choices(sorted(((id_, command_name(current, id_), meta['availability'])
                                       for id_, meta in metadata.items() if 'operator' in catalog['commands'][id_]),
                                      key=lambda item: item[1].casefold())),
            'event': choices(sorted(((id_, shortcut(event), f"{len(current.draft.uses('events', id_))} assignments")
                                      for id_, event in catalog['events'].items()), key=lambda item: item[1].casefold())),
            'scope': choices((id_, context_label(scope), '') for id_, scope in
                             sorted(self._scopes.items(), key=lambda item: context_label(item[1]).casefold())),
        }
        if not all(self._choices.values()):
            self.report({'ERROR'}, 'An assignment needs a section, command, shortcut and keymap')
            return {'CANCELLED'}
        bind_choices(self, self._choices)
        section = row['section'] if row else current.section
        self.section = (section if any(choice[0] == section for choice in self._choices['section'])
                        else self._choices['section'][0][0])
        self.command = row['command'] if row else self._choices['command'][0][0]
        self.event_id = row['event'] if row else self._choices['event'][0][0]
        self.scope_id = (next(id_ for id_, scope in self._scopes.items() if scope == row['scope'])
                         if row else self._choices['scope'][0][0])
        self._draft = current.draft
        self._initial = row
        return context.window_manager.invoke_props_dialog(self, width=500, confirm_text='Stage Assignment')

    def draw(self, _context):
        for name in ('section', 'command', 'event_id', 'scope_id'):
            self.layout.prop(self, name)
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
            current.draft.update('assignments', self.assignment, section=self.section,
                                 command=self.command, event=self.event_id, scope=scope)
        else:
            self.assignment = current.draft.add_assignment(self.section, self.event_id, self.command, scope)
        current.section = self.section
        current.category = current.catalog['sections'][self.section]['category']
        current.assignment = self.assignment
        current.changed()


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
    shared: BoolProperty(name='Edit all linked assignments', default=False, options=TRANSIENT)
    key: EnumProperty(name='Key', items=lambda self, _: enum_items(self, 'key'), options=TRANSIENT)
    phase: EnumProperty(name='Phase', items=lambda self, _: enum_items(self, 'phase'), options=TRANSIENT)
    direction: EnumProperty(name='Direction', items=lambda self, _: enum_items(self, 'direction'), options=TRANSIENT)
    key_modifier: EnumProperty(name='Key modifier', items=lambda self, _: enum_items(self, 'modifier'), options=TRANSIENT)
    repeat: BoolProperty(name='Repeat', options=TRANSIENT)
    any_modifier: BoolProperty(name='Any modifier', options=TRANSIENT)

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
        current = editor()
        if self.assignment:
            draw_uses(self.layout, current, 'events', self.assignment, self.shared)
            self.layout.prop(self, 'shared')
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
        stage_input(current, self.assignment, event, self.shared)


for _modifier in ('shift', 'ctrl', 'alt', 'oskey', 'hyper'):
    BH_OT_deluxe_shortcut.__annotations__[_modifier] = EnumProperty(
        name={'ctrl': 'Ctrl', 'oskey': 'OS Key'}.get(_modifier, _modifier.title()),
        items=[('0', 'Off', ''), ('1', 'On', ''), ('-1', 'Either', '')], options=TRANSIENT)


def stage_input(current, assignment, event, shared):
    descriptor = event_descriptor(event)
    for name, values in resolver.input_options()['event'].items():
        require(getattr(descriptor, name) in values, f'Unsupported input {name}')
    if assignment:
        current.stage_event(assignment, event, shared=shared)
    else:
        current.draft.put('events', uuid4().hex, event)
        current.changed('Shortcut added to the library')


def draw_uses(layout, current, table, assignment, shared=True):
    row = current.catalog['assignments'][assignment]
    key = 'event' if table == 'events' else 'command'
    ids = current.draft.uses(table, row[key]) if shared else (assignment,)
    layout.label(text=f'{len(ids)} affected assignment{"s" if len(ids) != 1 else ""}')
    for scope in dict.fromkeys(context_label(current.catalog['assignments'][id_]['scope']) for id_ in ids):
        layout.label(text=scope, icon='DOT')


class BH_OT_deluxe_capture(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_capture'
    bl_label = 'Capture Shortcut'

    assignment: StringProperty(options=HIDDEN)
    shared: BoolProperty(options=HIDDEN)

    def invoke(self, context, _event):
        current = editor()
        if self.assignment:
            current.require_editable_assignment(self.assignment)
        self._draft = current.draft
        self._area = context.area
        current.message = 'Press a key or mouse button. Esc cancels.'
        if self._area:
            self._area.header_text_set(current.message)
        context.window_manager.modal_handler_add(self)
        redraw(context)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        if self._area:
            try:
                self._area.header_text_set(None)
            except ReferenceError:
                pass
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
        return self.run(context, lambda current: stage_input(current, self.assignment, {
            'type': event.type, 'map_type': map_type(event.type), 'shift': event.shift,
            'ctrl': event.ctrl, 'alt': event.alt, 'oskey': event.oskey,
        }, self.shared))


class BH_OT_deluxe_field(EditorOperator, bpy.types.Operator):
    bl_idname = 'wm.bh_deluxe_field'
    bl_label = 'Edit Command Setting'

    command: StringProperty(options=HIDDEN)
    choice_key: StringProperty(options=HIDDEN)
    field: StringProperty(options=HIDDEN)
    assignment: StringProperty(options=HIDDEN)
    single: BoolProperty(name='This assignment only', options=TRANSIENT)
    boolean: BoolProperty(options=TRANSIENT)
    integer: IntProperty(options=TRANSIENT)
    number: FloatProperty(options=TRANSIENT, precision=6)
    string: StringProperty(options=TRANSIENT)
    option: EnumProperty(items=lambda self, _: enum_items(self, 'values'), options=TRANSIENT)
    enabled: BoolProperty(name='Flag enabled', options=TRANSIENT)

    def invoke(self, context, _event):
        current = editor()
        row = current.catalog['commands'][self.command]
        self._meta = current.preview()['commands'][self.command]['fields'][self.field]
        if not self._meta['editable']:
            return {'CANCELLED'}
        self._value = row['properties'][self.field]
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
        if self._meta['shape'] or self._meta['flags']:
            self.layout.prop(self, 'component', text='Flag' if self._meta['flags'] else 'Component')
            self.select_component(_context)
        name = 'enabled' if self._meta['flags'] else self._property
        self.layout.prop(self, name, text=self._meta['label'])

    def stage(self, current):
        require(current.draft is self._draft, 'The draft changed. Reopen the command setting.')
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
        current.edit_command(self.command, self.field, value, self.assignment if self.single else '')


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
    bl_label = 'Disable Existing Shortcut'

    section: StringProperty(options=HIDDEN)
    rule: StringProperty(options=HIDDEN)

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

    section: StringProperty(options=HIDDEN)
    rule: StringProperty(options=HIDDEN)
    source: StringProperty(options=HIDDEN)
    map_pointer: StringProperty(options=HIDDEN)
    item_pointer: StringProperty(options=HIDDEN)
    item_id: IntProperty(options=HIDDEN)
    signature: StringProperty(options=HIDDEN)
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
        current = editor()
        if self.section in current.catalog['sections']:
            self.layout.label(text=f"Section: {current.catalog['sections'][self.section]['label']}")
        for name, value in target.get('properties', {}).items():
            self.layout.label(text=f'{title(name)}: {display_value(value)}')
        if self._replacement:
            self.layout.prop(self, 'use_replacement')
        if not self._replacement or not self.use_replacement:
            self.layout.label(text='The runtime cannot disable this shortcut. Save the target for review.', icon='INFO')

    def execute(self, context):
        def stage(current):
            require(current.draft is self._draft, 'The draft changed. Pick the binding again.')
            section = current.catalog['sections'][self.section]
            require(not section.get('required'), 'This section is required')
            map_, item, candidate = self.selected(context)
            command = known_replacement(candidate) if self.use_replacement else None
            require(not self.use_replacement or command is not None, 'Replacement is no longer available')
            replacement = None
            if command:
                replacement = next((id_ for id_, row in current.catalog['commands'].items() if row == command), None)
                if replacement is None:
                    replacement = uuid4().hex
                    current.draft.put('commands', replacement, command)
            current.draft.stage_suppression(self.section, map_, item, self.source,
                                            replacement=replacement, id_=self.rule or None)
            current.changed()

        return self.run(context, stage)


classes = (
    BH_PG_deluxe_editor, BH_OT_deluxe_edit, BH_OT_deluxe_section, BH_OT_deluxe_mapping,
    BH_OT_deluxe_shortcut, BH_OT_deluxe_capture, BH_OT_deluxe_field,
    BH_OT_deluxe_binding_picker, BH_OT_deluxe_stage_binding,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    setattr(bpy.types.WindowManager, WM_PROPERTY, PointerProperty(type=BH_PG_deluxe_editor, options=TRANSIENT))


def unregister():
    global _editor
    _editor = None
    _dialog_choices.clear()
    delattr(bpy.types.WindowManager, WM_PROPERTY)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
