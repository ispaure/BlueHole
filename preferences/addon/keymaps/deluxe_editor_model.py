"""Draft operations and display values for the Deluxe Preferences editor."""

from collections import deque
from copy import deepcopy
from dataclasses import dataclass
import json
from struct import pack, unpack
from time import monotonic
from uuid import uuid4

from ....keymaps.deluxe_schema import MODIFIERS, assignment_required, require, same_value

SOURCE_LABELS = {'default': 'Blender', 'user': 'User keymap (merged)', 'addon': 'Add-on keymap'}
PHASE_LABELS = {'CLICK_DRAG': 'Drag', 'DOUBLE_CLICK': 'Double Click'}
KEY_LABELS = {
    'LEFTMOUSE': 'Left Mouse', 'MIDDLEMOUSE': 'Middle Mouse', 'RIGHTMOUSE': 'Right Mouse',
    'WHEELUPMOUSE': 'Wheel Up', 'WHEELDOWNMOUSE': 'Wheel Down',
    'WHEELLEFTMOUSE': 'Wheel Left', 'WHEELRIGHTMOUSE': 'Wheel Right',
    'RET': 'Enter', 'ESC': 'Esc', 'OSKEY': 'OS Key',
}
SEARCH_MODIFIERS = {key: key for key in (*MODIFIERS, 'any')}
SEARCH_MODIFIERS.update(control='ctrl', option='alt', cmd='oskey', command='oskey',
                        win='oskey', os='oskey')
SEARCH_KEYS = {'lmb': 'LEFTMOUSE', 'mmb': 'MIDDLEMOUSE', 'rmb': 'RIGHTMOUSE',
               '+': 'NUMPAD_PLUS', '-': 'NUMPAD_MINUS', '*': 'NUMPAD_ASTERIX',
               '/': 'NUMPAD_SLASH', '.': 'NUMPAD_PERIOD', '`': 'ACCENT_GRAVE',
               "'": 'QUOTE'}
STATUS_LABELS = {
    'waiting_for_provider': 'Waiting for add-on',
    'unavailable': 'Unavailable',
    'missing': 'Target missing or changed',
    'ambiguous': 'Multiple matching targets',
    'unsupported': 'Unsupported by the runtime',
    'resolved': 'Exact target resolved',
}


def title(identifier):
    return identifier.replace('_', ' ').title()


def map_type(key):
    if key.startswith('TIMER'):
        return 'TIMER'
    if key == 'TEXTINPUT':
        return 'TEXTINPUT'
    # Blender classifies the legacy smart-zoom token as Keyboard, even though
    # it is exposed alongside mouse inputs in RNA.
    if key != 'MOUSESMARTZOOM' and ('MOUSE' in key or key.startswith('TRACKPAD') or key in {'PEN', 'ERASER'}):
        return 'MOUSE'
    if key.startswith('NDOF'):
        return 'NDOF'
    return 'KEYBOARD'


def key_label(key):
    return KEY_LABELS.get(key, title(key) if len(key) > 1 else key)


def captured_input(previous, event):
    """Keep compatible binding settings when capturing only a new input."""
    kind = map_type(event.type)
    captured = dict(previous)
    if kind != previous.get('map_type', map_type(previous['type'])):
        captured.update(value='PRESS', direction='ANY', repeat=False)
    captured.update(type=event.type, map_type=kind, any=False,
                    **{key: bool(getattr(event, key, False)) for key in MODIFIERS if key != 'hyper'})
    if hasattr(event, 'hyper'):
        captured['hyper'] = bool(event.hyper)
    if kind != 'KEYBOARD' or captured.get('value', 'PRESS') not in {'PRESS', 'ANY'}:
        captured['repeat'] = False
    return captured


def key_filter(query, event_labels):
    """Match typed keys and requested modifiers, including held key modifiers."""
    modifiers = set()
    key_terms = []
    words = query.casefold().split()
    for word in words:
        if word == '+' and len(words) > 1 and words[-1] != '+':
            continue
        for part in filter(None, word.split('+') if word != '+' else (word,)):
            if part in SEARCH_MODIFIERS:
                modifiers.add(SEARCH_MODIFIERS[part])
            else:
                key_terms.append(part)
    matches = []
    for term in key_terms:
        exact = {key for key, label in event_labels.items()
                 if term in (key.casefold(), label.casefold().replace(' ', '_'))}
        if term in SEARCH_KEYS:
            exact.add(SEARCH_KEYS[term])
        matches.append(exact or {key for key, label in event_labels.items()
                                 if term in key.casefold() or term in label.casefold()})

    def accepts(event):
        keys = {event['type'], event.get('key_modifier', 'NONE')} - {'NONE'}
        return (all(event.get(modifier) == 1 for modifier in modifiers)
                and all(keys & choices for choices in matches))

    return accepts


def shortcut(event):
    names = []
    if event.get('any'):
        names.append('Any modifier')
    else:
        for key in MODIFIERS:
            value = event.get(key)
            label = {'ctrl': 'Ctrl', 'oskey': 'OS Key'}.get(key, key.title())
            if value:
                names.append(label + (' (any)' if value == -1 else ''))
    key = event['type']
    names.append(key_label(key))
    if event.get('key_modifier', 'NONE') != 'NONE':
        names.insert(0, KEY_LABELS.get(event['key_modifier'], title(event['key_modifier'])))
    value = event.get('value', 'PRESS')
    suffix = [] if value == 'PRESS' else [PHASE_LABELS.get(value, title(value))]
    if event.get('direction', 'ANY') != 'ANY':
        suffix.append(title(event['direction']))
    if event.get('repeat'):
        suffix.append('Repeat')
    return ' + '.join(names) + (f" ({', '.join(suffix)})" if suffix else '')


def context_label(scope):
    name = scope['name']
    space = scope.get('space_type', 'EMPTY')
    region = scope.get('region_type', 'WINDOW')
    show_space = (space != 'EMPTY' and title(space).casefold() != name.casefold()
                  and not (space == 'VIEW_3D' and '3D View' in name))
    return ' · '.join([name, *([title(space)] if show_space else []),
                       *([title(region)] if region != 'WINDOW' else []),
                       *(['Modal'] if scope.get('is_modal') else [])])


def scope_key(scope):
    return scope['name'], scope.get('space_type', 'EMPTY'), scope.get('region_type', 'WINDOW')


def context_id(scope):
    return json.dumps(scope_key(scope))


@dataclass
class BindingContext:
    id: str
    label: str
    bindings: list
    children: list
    scope: dict | None = None


def binding_context_tree(hierarchy, groups, available_scopes=()):
    """Keep Blender's context order and retain scopes outside its built-in tree."""
    remaining = dict(groups)
    available = {scope_key(scope): scope for scope in available_scopes}
    for key in available:
        remaining.setdefault(key, [])

    def prune(entries, parent=()):
        contexts = []
        for name, space, region, subcontexts in entries:
            key = name, space, region
            # Blender repeats scopes beneath different editors and tools.
            # Each occurrence needs its own expansion and navigation state.
            path = (*parent, key)
            bindings = remaining.pop(key, [])
            children = prune(subcontexts, path)
            scope = available.get(key)
            if subcontexts and (bindings or scope):
                children.insert(0, BindingContext(json.dumps((*path, 'global')), f'{name} (Global)', bindings, [], scope))
                bindings = []
                scope = None
            if bindings or children or scope:
                contexts.append(BindingContext(json.dumps(path), name, bindings, children, scope))
        return contexts

    contexts = prune(hierarchy)
    for key, bindings in sorted(remaining.items()):
        name, space, region = key
        label = context_label({'name': name, 'space_type': space, 'region_type': region})
        contexts.append(BindingContext(json.dumps((key,)), label, bindings, [], available.get(key)))
    return contexts


def binding_context_path(contexts, assignment):
    for context in contexts:
        if assignment in context.bindings:
            return (context.id,)
        path = binding_context_path(context.children, assignment)
        if path:
            return (context.id, *path)
    return ()


def display_value(value):
    if isinstance(value, bool):
        return 'On' if value else 'Off'
    if isinstance(value, list):
        return ', '.join(map(display_value, value)) or 'None'
    return str(value)


class Editor:
    """One working draft per loaded profile, shared across Preferences windows."""

    def __init__(self, store):
        self.capture_assignment = ''
        self.store = store
        self.defaults = store.defaults()
        self.draft = store.begin()
        self.saved = store.snapshot()
        self.catalog = self.draft.snapshot()
        self._undo = deque(maxlen=32)
        self.category = 'navigation' if 'navigation' in self.catalog['categories'] else ''
        self.feature_category = self.category
        self.feature_section = ''
        self.section = ''
        self.assignment = ''
        self.binding_all = True
        self.binding_category_all = True
        self.binding_context_expansion = {}
        self.binding_selection_path = ()
        self.binding_focus_context = ''
        self.page = 0
        self.message = ''
        self.dirty = store.needs_migration
        self.preview_error = ''
        self._preview = None
        self._preview_at = 0
        self._preview_token = None
        self.display_cache = {}
        self.ensure_selection()

    def ensure_selection(self):
        """Keep transient tab/filter IDs valid after catalog edits or reloads."""
        categories = self.catalog['categories']
        if self.category not in categories:
            self.binding_all = True
        if self.section not in self.catalog['sections']:
            self.binding_category_all = True
        for category_attr, section_attr in (('category', 'section'),
                                            ('feature_category', 'feature_section')):
            category = getattr(self, category_attr)
            if category not in categories:
                category = next(iter(categories), '')
                setattr(self, category_attr, category)
            sections = self.sections(category)
            if getattr(self, section_attr) not in sections:
                setattr(self, section_attr, next(iter(sections), ''))

    def accepts_binding(self, row):
        if not self.binding_all:
            if self.catalog['sections'][row['section']]['category'] != self.category:
                return False
            if not self.binding_category_all and row['section'] != self.section:
                return False
        return True

    def show_all_bindings(self):
        self.binding_all = True
        self.binding_category_all = True
        self.assignment, self.page = '', 0

    def select_category(self, category):
        require(category in self.catalog['categories'], 'Section no longer exists')
        self.category = self.feature_category = category
        self.binding_all, self.binding_category_all = False, True
        self.assignment, self.page = '', 0
        self.ensure_selection()

    def select_section(self, section):
        require(section in self.catalog['sections'], 'Subsection no longer exists')
        self.category = self.feature_category = self.catalog['sections'][section]['category']
        self.section = self.feature_section = section
        self.binding_all = self.binding_category_all = False
        self.assignment, self.page = '', 0

    def expand_binding_contexts(self, contexts, expanded):
        def visit(context):
            children = [visit(child) for child in context.children]
            has_bindings = bool(context.bindings) or any(children)
            self.binding_context_expansion[context.id] = bool(expanded and has_bindings)
            return has_bindings
        for context in contexts:
            visit(context)
        self.binding_focus_context = contexts[0].id if contexts else ''

    def configure_binding(self, section, event, operator, scope, *, assignment=''):
        """Create or edit a binding with its own operator configuration."""
        operator = operator.strip().removeprefix('bpy.ops.')
        require(section in self.catalog['sections'] and not self.catalog['sections'][section].get('required'),
                'Choose an editable section')
        require(event in self.catalog['events'], 'Choose a shortcut')
        if assignment:
            self.require_editable_assignment(assignment)
            command = self.catalog['assignments'][assignment]['command']
            updated = self.operator_command(command, operator)
        else:
            command = uuid4().hex
            updated = {'operator': operator, 'properties': {}}
            self.store.resolver.validate_command(updated, command)
        command = self.stage_command(command, updated)
        if assignment:
            self.draft.update('assignments', assignment, section=section, event=event, scope=scope)
        else:
            assignment = self.draft.add_assignment(section, event, command, scope)
        self.changed('Binding updated' if assignment in self.saved['assignments'] else 'Binding added')
        self.select_section(section)
        self.assignment = assignment
        return assignment

    def add_binding(self, scope, section=''):
        """Add an unassigned row directly in a concrete context, without activating a shortcut."""
        if not self.binding_all:
            section = self.section
        choices = [id_ for id_, row in self.catalog['sections'].items() if not row.get('required')
                   and (self.binding_all or row['category'] == self.category)]
        require(bool(choices), 'Create an editable subsection first')
        if section not in choices:
            section = self.section if self.section in choices else choices[0]
        event = uuid4().hex
        command = uuid4().hex
        self.draft.put('events', event, {'type': 'NONE'})
        self.draft.put('commands', command, {'operator': '', 'properties': {}})
        assignment = self.draft.add_assignment(section, event, command, scope)
        self.changed('Binding added')
        self.assignment = assignment
        return assignment

    def move_binding(self, id_, *, category='', section=''):
        table = 'assignments' if id_ in self.catalog['assignments'] else 'suppressions'
        if table == 'assignments':
            self.require_editable_assignment(id_)
        if category:
            choices = [id_ for id_ in self.sections(category) if not self.catalog['sections'][id_].get('required')]
            require(bool(choices), 'Choose a category with an editable subsection')
            section = choices[0]
        require(section in self.catalog['sections'] and not self.catalog['sections'][section].get('required'),
                'Choose an editable subsection')
        self.draft.update(table, id_, section=section)
        if not self.binding_all:
            self.select_section(section)
        self.assignment = id_
        self.changed('Binding category updated')

    def can_change_operator(self, command):
        operator = self.catalog['commands'][command].get('operator')
        return operator is not None and all(
            not assignment_required(self.catalog, self.catalog['assignments'][id_])
            for id_ in self.draft.uses('commands', command))

    def operator_command(self, command, operator):
        original = self.catalog['commands'][command]
        if operator == original['operator']:
            return original
        require(self.can_change_operator(command), 'This binding is required')
        updated = {'operator': operator, 'properties': {}}
        if original.get('label'):
            updated['label'] = original['label']
        self.store.resolver.validate_command(updated, command)
        return updated

    def change_command_operator(self, command, operator):
        operator = operator.strip().removeprefix('bpy.ops.')
        updated = self.operator_command(command, operator)
        self.stage_command(command, updated)
        self.changed('Command operator changed')

    def stage_command(self, command, updated):
        if 'provider' in self.catalog['commands'].get(command, {}) and 'provider' not in updated:
            # Legacy overlay patches cannot remove a field from an existing
            # record. Give a retargeted provider command a new owned record.
            assignment, = self.draft.uses('commands', command)
            command = self.draft.clone('commands', assignment)
        self.draft.put('commands', command, updated)
        return command

    def binding_pending(self, id_, preview):
        if id_ in self.catalog['assignments']:
            state = preview['assignments'][id_]
            return state['availability'] != 'available' or (state['eligible'] and not state['registered'])
        state = preview['suppressions'][id_]
        rule = self.catalog['suppressions'][id_]
        return (rule.get('disable') or 'replacement' in rule) and (
            state['status'] != 'resolved' or state['eligible'] and not state['registered'])

    def binding_origin(self, id_, preview):
        if id_ in self.catalog['assignments']:
            state = preview['assignments'][id_]
            status = ('Active' if state['eligible'] and state['active'] else 'Inactive')
            if status == 'Active' and not state['registered']:
                status = 'Pending registration'
            command = preview['commands'][self.catalog['assignments'][id_]['command']]
            definition = self.catalog['commands'][self.catalog['assignments'][id_]['command']]
            if not definition.get('operator') and 'modal_value' not in definition:
                status = 'Unassigned'
            elif command['availability'] != 'available':
                status = 'Waiting for ' + command['dependency'] if command.get('dependency') else 'Operator unavailable'
            return 'ADD', f'Keymap Added by Blue Hole Deluxe · {status}'
        row = self.catalog['suppressions'][id_]
        state = preview['suppressions'][id_]
        if row.get('disable'):
            source = 'Add-on' if row['selector']['source_role'] == 'addon' else 'Blender'
            description = (f'{source} Keymap Disabled by Blue Hole Deluxe' if state['registered']
                           else f'{source} Keymap Disable Rule · ' + ('Inactive' if not state['eligible'] else 'Pending'))
            return 'REMOVE', description
        if 'replacement' in row:
            return 'FILE_REFRESH', 'Blender Keymap Replaced by Blue Hole Deluxe'
        return 'INFO', 'Blender Keymap Reference · No change applied'

    def changed(self, message='Changes staged', *, remember=True):
        catalog = self.draft.snapshot()
        if remember and not same_value(self.catalog, catalog):
            self._undo.append(self.catalog)
        self.catalog = catalog
        self.ensure_selection()
        self.dirty = self.store.needs_migration or not same_value(self.catalog, self.saved)
        self._preview = None
        self.display_cache.clear()
        self.message = message
        try:
            self.store.preview_draft(self.draft)
        except (ValueError, OSError, RuntimeError, ReferenceError) as error:
            self.preview_error = str(error)
        else:
            self.preview_error = ''

    def set_enabled(self, table, id_, enabled):
        require(table in ('categories', 'sections', 'assignments', 'suppressions'), 'Invalid toggle target')
        if table == 'assignments':
            self.require_editable_assignment(id_)
        row = self.catalog[table][id_]
        require(not row.get('required'), 'This section is required')
        updates = {'enabled': enabled}
        if table == 'assignments' and enabled and not row.get('active', True):
            updates['active'] = True
        if any(row.get(key, True) != value for key, value in updates.items()):
            self.draft.update(table, id_, **updates)
            self.changed()

    def preview(self):
        now = monotonic()
        if self._preview is None or now - self._preview_at > 1:
            token = self.store.preview_token(self.catalog)
            if self._preview is None or token != self._preview_token:
                self._preview = self.store.preview(self.draft)
                self.display_cache.clear()
                self._preview_token = token
            self._preview_at = now
        return self._preview

    @property
    def can_undo(self):
        return bool(self._undo)

    def undo(self):
        require(self.can_undo, 'No staged keymap edits to undo')
        self.draft.restore(self._undo.pop())
        self.changed('Keymap edit undone', remember=False)

    def discard(self):
        self.store.cancel_preview()
        self.draft.discard()
        self.saved = self.store.snapshot()
        self.draft = self.store.begin()
        self._undo.clear()
        self.changed('Draft discarded', remember=False)

    def apply(self):
        self.saved = self.store.apply(self.draft)
        self.draft = self.store.begin()
        self._undo.clear()
        self.changed('Profile saved and applied', remember=False)

    def reload(self):
        self.store.reload()
        self.discard()
        self.message = ('JSON validation failed; kept the saved setup' if self.store.load_issue
                        else 'JSON files validated and reloaded')

    def sections(self, category=None):
        category = self.category if category is None else category
        sections = self.catalog['sections']
        ids = [id_ for id_, row in sections.items() if row['category'] == category]
        return sorted(ids, key=lambda id_: (sections[id_].get('required', False),
                                            sections[id_].get('order', 0)))

    def edit_section(self, name, id_=None):
        name = name.strip()
        require(bool(name), 'Enter a section name')
        ids = self.sections()
        require(all(other == id_ or self.catalog['sections'][other]['label'].casefold() != name.casefold()
                    for other in ids), 'A section already uses that name')
        if id_:
            require(not self.catalog['sections'][id_].get('required'), 'This section is required')
            self.draft.update('sections', id_, label=name)
        else:
            id_ = uuid4().hex
            order = max((self.catalog['sections'][other].get('order', 0) for other in ids), default=-1)
            self.draft.put('sections', id_, {'label': name, 'category': self.category, 'order': order + 1})
        self.section = id_
        self.feature_category, self.feature_section = self.category, id_
        self.binding_all = self.binding_category_all = False
        self.page = 0
        self.changed()

    def reorder_section(self, offset):
        ids = self.sections()
        index = ids.index(self.section)
        other = index + offset
        require(0 <= other < len(ids), 'Section is already at the edge')
        require(not any(self.catalog['sections'][id_].get('required') for id_ in (ids[index], ids[other])),
                'Required sections keep their position')
        ids[index], ids[other] = ids[other], ids[index]
        for order, id_ in enumerate(ids):
            if not self.catalog['sections'][id_].get('required'):
                self.draft.update('sections', id_, order=order)
        self.changed()

    def require_editable_assignment(self, id_):
        row = self.catalog['assignments'][id_]
        require(not assignment_required(self.catalog, row), 'This shortcut is required')

    def stage_event(self, assignment, event):
        self.require_editable_assignment(assignment)
        event_id = self.catalog['assignments'][assignment]['event']
        if same_value(self.catalog['events'][event_id], event):
            return
        if len(self.draft.uses('events', event_id)) > 1:
            event_id = self.draft.clone('events', assignment)
        self.draft.put('events', event_id, event)
        self.changed()

    def edit_command(self, command_id, field, value, assignment='', *, unset=False):
        original = self.catalog['commands'][command_id]
        metadata = self.store.resolver.describe_command(original, include_unset=True)['fields'].get(field, {})
        require(metadata.get('editable'), 'This command field is read-only')
        properties = dict(original['properties'])
        if unset:
            properties.pop(field, None)
        else:
            properties[field] = value
        if same_value(properties, original['properties']):
            return
        updated = {**original, 'properties': properties}
        self.store.resolver.validate_command(updated, command_id)
        if not unset and metadata['type'] == 'FLOAT':
            # RNA stores floats as float32. Persist the value Blender will read back.
            def native_float(part):
                if isinstance(part, list):
                    return [native_float(item) for item in part]
                return unpack('f', pack('f', part))[0]

            properties[field] = native_float(value)
        if assignment:
            self.require_editable_assignment(assignment)
            require(self.catalog['assignments'][assignment]['command'] == command_id,
                    'The assignment command changed. Reopen the field.')
        else:
            for id_ in self.draft.uses('commands', command_id):
                self.require_editable_assignment(id_)
        self.draft.put('commands', command_id, updated)
        self.changed()
