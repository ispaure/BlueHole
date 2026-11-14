"""Draft operations and display values for the Deluxe Preferences editor."""

from collections import Counter
from copy import deepcopy
import json
from struct import pack, unpack
from time import monotonic
from uuid import uuid4

from ....keymaps.deluxe_schema import MODIFIERS, require, same_value

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
    if 'MOUSE' in key or key.startswith(('TRACKPAD', 'MOUSEROTATE')):
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


def context_id(scope):
    return json.dumps([scope['name'], scope.get('space_type', 'EMPTY'), scope.get('region_type', 'WINDOW')])


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
        self.capture_shared = False
        self.store = store
        self.defaults = store.defaults()
        self.draft = store.begin()
        self.saved = store.snapshot()
        self.catalog = self.draft.snapshot()
        self.category = 'navigation' if 'navigation' in self.catalog['categories'] else ''
        self.feature_category = self.category
        self.feature_section = ''
        self.section = ''
        self.assignment = ''
        self.expanded_shortcut = ''
        self.expanded_linked_section = ''
        self.command = ''
        self.command_category = ''
        self.command_section = ''
        self.binding_all = True
        self.binding_category_all = True
        self.binding_context = ''
        self.binding_command = ''
        self.focus_command = False
        self.page = 0
        self.message = ''
        self.dirty = False
        self.preview_error = ''
        self._preview = None
        self._preview_at = 0
        self.ensure_selection()

    def ensure_selection(self):
        """Keep transient tab/filter IDs valid after catalog edits or reloads."""
        categories = self.catalog['categories']
        if self.category not in categories:
            self.binding_all = True
        if self.section not in self.catalog['sections']:
            self.binding_category_all = True
        if self.binding_context not in self.binding_contexts():
            self.binding_context = ''
        if self.binding_command not in self.catalog['commands']:
            self.binding_command = ''
        for category_attr, section_attr in (('category', 'section'),
                                            ('feature_category', 'feature_section')):
            category = getattr(self, category_attr)
            if category not in categories:
                category = next(iter(categories), '')
                setattr(self, category_attr, category)
            sections = self.sections(category)
            if getattr(self, section_attr) not in sections:
                setattr(self, section_attr, next(iter(sections), ''))
        if self.command_category not in categories:
            self.command_category = self.command_section = ''
        elif self.command_section not in self.sections(self.command_category):
            self.command_section = ''

    def binding_contexts(self):
        rows = [row['scope'] for row in self.catalog['assignments'].values()]
        rows += [row['selector']['scope'] for row in self.catalog['suppressions'].values()]
        return {context_id(scope): scope for scope in sorted(rows, key=context_label)}

    def accepts_binding(self, row):
        if not self.binding_all:
            if self.catalog['sections'][row['section']]['category'] != self.category:
                return False
            if not self.binding_category_all and row['section'] != self.section:
                return False
        return ((not self.binding_context or context_id(row['scope']) == self.binding_context)
                and (not self.binding_command or row['command'] == self.binding_command))

    def show_all_bindings(self, command=''):
        self.binding_all = True
        self.binding_category_all = True
        self.binding_context = ''
        self.binding_command = command
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

    def create_command(self, operator='', label='', source=''):
        row = deepcopy(self.catalog['commands'][source]) if source else {'operator': operator, 'properties': {}}
        require('operator' in row, 'Modal tokens cannot be created as ordinary commands')
        if label.strip():
            row['label'] = label.strip()
        self.store.resolver.validate_command(row, 'new-command')
        id_ = uuid4().hex
        self.draft.put('commands', id_, row)
        self.command = id_
        self.command_category = self.command_section = ''
        self.focus_command = True
        self.changed('Command added; create a binding to use it')
        return id_

    def remove_command(self, id_):
        require(not self.draft.uses('commands', id_) and not any(
            row.get('replacement') == id_ for row in self.catalog['suppressions'].values()),
            'Remove or change every binding and replacement rule before deleting this command')
        self.draft.delete('commands', id_)
        self.command = ''
        self.changed('Unused command removed')

    def changed(self, message='Changes staged'):
        self.catalog = self.draft.snapshot()
        self.ensure_selection()
        self.dirty = not same_value(self.catalog, self.saved)
        self._preview = None
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
        if row.get('enabled', True) != enabled:
            self.draft.update(table, id_, enabled=enabled)
            self.changed()

    def preview(self):
        now = monotonic()
        if self._preview is None or now - self._preview_at > 1:
            self._preview = self.store.preview(self.draft)
            self._preview_at = now
        return self._preview

    def discard(self):
        self.store.cancel_preview()
        self.draft.discard()
        self.saved = self.store.snapshot()
        self.draft = self.store.begin()
        self.changed('Draft discarded')

    def apply(self):
        self.saved = self.store.apply(self.draft)
        self.draft = self.store.begin()
        self.changed('Profile saved and applied')

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
        require(not self.catalog['sections'][row['section']].get('required'), 'This shortcut is required')

    def linked_sections(self, linked):
        assignments = self.catalog['assignments']
        totals = Counter(row['section'] for row in assignments.values())
        groups = {}
        for id_ in sorted(linked, key=lambda id_: assignments[id_]['order']):
            groups.setdefault(assignments[id_]['section'], []).append(id_)
        return [(section, ids, totals[section])
                for section, ids in sorted(groups.items(), key=lambda pair: -len(pair[1]))]

    def assignment_status(self, preview, id_):
        row = self.catalog['assignments'][id_]
        state = preview['assignments'][id_]
        if not row.get('enabled', True):
            return 'Disabled', 'CHECKBOX_DEHLT'
        if not preview['sections'][row['section']]:
            return 'Section inactive', 'PAUSE'
        if not state['active']:
            return 'Inactive', 'PAUSE'
        command = preview['commands'][row['command']]
        if command['availability'] == 'waiting_for_provider':
            return f"Waiting for {command['dependency']}", 'INFO'
        if command['availability'] != 'available':
            return 'Command unavailable', 'ERROR'
        return 'Enabled', 'CHECKMARK'

    def stage_event(self, assignment, event, *, shared):
        self.require_editable_assignment(assignment)
        event_id = self.catalog['assignments'][assignment]['event']
        if same_value(self.catalog['events'][event_id], event):
            return
        if shared:
            for id_ in self.draft.uses('events', event_id):
                self.require_editable_assignment(id_)
        elif len(self.draft.uses('events', event_id)) > 1:
            event_id = self.draft.clone('events', assignment)
        self.draft.put('events', event_id, event)
        self.changed()

    def command_ids(self):
        """Filter reusable commands by assignment or rule usage."""
        if not self.command_category:
            return self.catalog['commands'].keys()
        sections = set(self.sections(self.command_category))
        if self.command_section:
            sections.intersection_update({self.command_section})
        return {
            row[key] for table, key in (('assignments', 'command'), ('suppressions', 'replacement'))
            for row in self.catalog[table].values() if row['section'] in sections and key in row
        }

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
            if len(self.draft.uses('commands', command_id)) > 1 or any(
                    row.get('replacement') == command_id for row in self.catalog['suppressions'].values()):
                command_id = self.draft.clone('commands', assignment)
        else:
            for id_ in self.draft.uses('commands', command_id):
                self.require_editable_assignment(id_)
        self.draft.put('commands', command_id, updated)
        self.command = command_id
        self.changed()
