"""Draft operations and display values for the Deluxe Preferences editor."""

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
    names.append(KEY_LABELS.get(key, title(key) if len(key) > 1 else key))
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
    show_space = space != 'EMPTY' and not (space == 'VIEW_3D' and '3D View' in name)
    return ' · '.join([name, *([title(space)] if show_space else []),
                       *([title(region)] if region != 'WINDOW' else []),
                       *(['Modal'] if scope.get('is_modal') else [])])


def display_value(value):
    if isinstance(value, bool):
        return 'On' if value else 'Off'
    if isinstance(value, list):
        return ', '.join(map(display_value, value)) or 'None'
    return str(value)


class Editor:
    """One working draft per loaded profile, shared across Preferences windows."""

    def __init__(self, store):
        self.store = store
        self.defaults = store.defaults()
        self.draft = store.begin()
        self.saved = store.snapshot()
        self.catalog = self.draft.snapshot()
        self.category = 'navigation' if 'navigation' in self.catalog['categories'] else ''
        self.section = ''
        self.assignment = ''
        self.command = ''
        self.command_category = ''
        self.command_section = ''
        self.page = 0
        self.message = ''
        self.dirty = False
        self._preview = None
        self._preview_at = 0

    def changed(self, message='Changes staged'):
        self.catalog = self.draft.snapshot()
        self.dirty = not same_value(self.catalog, self.saved)
        self._preview = None
        self.message = message

    def preview(self):
        now = monotonic()
        if self._preview is None or now - self._preview_at > 1:
            self._preview = self.store.preview(self.draft)
            self._preview_at = now
        return self._preview

    def discard(self):
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
        self.message = 'Profile reloaded'

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

    def stage_event(self, assignment, event, *, shared):
        self.require_editable_assignment(assignment)
        event_id = self.catalog['assignments'][assignment]['event']
        if same_value(self.catalog['events'][event_id], event):
            return
        if shared:
            for id_ in self.draft.uses('events', event_id):
                self.require_editable_assignment(id_)
        else:
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
            command_id = self.draft.clone('commands', assignment)
        else:
            for id_ in self.draft.uses('commands', command_id):
                self.require_editable_assignment(id_)
        self.draft.put('commands', command_id, updated)
        self.command = command_id
        self.changed()
