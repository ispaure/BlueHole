"""Detached editing records with monotonically increasing revision numbers."""
from copy import deepcopy
from uuid import uuid4
from .deluxe_schema import TABLES, identifier, require, same_value


class Draft:
    """A detached working copy tied to one store revision."""

    def __init__(self, store, revision, catalog):
        self._store = store
        self._revision = revision
        self._catalog = deepcopy(catalog)
        self._closed = False
        self.serial = 0

    def snapshot(self):
        return deepcopy(self._catalog)

    def _open(self):
        require(not self._closed, 'Draft has been closed')

    def put(self, table, id_, row):
        """Insert or replace one complete row. Validation allows multi-step edits."""
        self._open()
        require(table in TABLES and identifier(id_) and isinstance(row, dict), 'Invalid draft entry')
        row = deepcopy(row)
        field = {'assignments': 'command', 'suppressions': 'replacement'}.get(table)
        previous = self._catalog[table].get(id_, {}).get(field) if field else None
        if field and field in row and row[field] in self._catalog['commands']:
            source = row[field]
            if any((other_table, other_id) != (table, id_)
                   for other_table, other_id in self.command_owners(source)):
                row[field] = uuid4().hex
                self._catalog['commands'][row[field]] = deepcopy(self._catalog['commands'][source])
        self._catalog[table][id_] = row
        self.serial += 1
        if previous and previous != row.get(field):
            self._remove_unused_command(previous)

    def command_owners(self, command):
        return tuple((table, id_) for table, field in
                     (('assignments', 'command'), ('suppressions', 'replacement'))
                     for id_, row in self._catalog[table].items() if row.get(field) == command)

    def _remove_unused_command(self, command):
        if not self.command_owners(command):
            self._catalog['commands'].pop(command, None)

    def update(self, table, id_, **fields):
        self.put(table, id_, {**self._catalog[table][id_], **fields})

    def delete(self, table, id_):
        self._open()
        require(table in TABLES, 'Unknown profile table')
        row = self._catalog[table].pop(id_)
        self.serial += 1
        field = {'assignments': 'command', 'suppressions': 'replacement'}.get(table)
        if field and field in row:
            self._remove_unused_command(row[field])

    def uses(self, table, id_):
        """Return assignment IDs affected by an event or command edit."""
        require(table in ('events', 'commands'), 'Use counts require an event or command')
        key = 'event' if table == 'events' else 'command'
        return tuple(id2 for id2, row in self._catalog['assignments'].items() if row[key] == id_)

    def clone(self, table, assignment, *, new_id=None):
        """Give one assignment its own event or command record."""
        self._open()
        require(table in ('events', 'commands'), 'Clone requires an event or command')
        key = 'event' if table == 'events' else 'command'
        source = self._catalog['assignments'][assignment][key]
        new_id = new_id or uuid4().hex
        require(new_id not in self._catalog[table], 'Clone ID already exists')
        self.put(table, new_id, self._catalog[table][source])
        self.update('assignments', assignment, **{key: new_id})
        return new_id

    def add_assignment(self, section, event, command, scope, *, id_=None):
        """Append a user assignment after shipped registrations."""
        id_ = id_ or uuid4().hex
        require(id_ not in self._catalog['assignments'], 'Assignment ID already exists')
        order = max((row['order'] for row in self._catalog['assignments'].values()), default=0)
        self.put('assignments', id_, dict(section=section, event=event, command=command,
                                        scope=scope, order=max(order + 1, 1_000_000), feature=id_))
        return id_

    def stage_suppression(self, section, map_, item, source_role, *, replacement=None, disable=False, id_=None):
        """Capture a selected live row. Passing a saved ID retargets that rule."""
        self._open()
        candidate = self._store.capture_binding(map_, item, source_role)
        if id_ is None and disable:
            id_ = next((key for key, row in self._catalog['suppressions'].items()
                        if row.get('disable') and same_value(row['selector'], candidate['selector'])), None)
        id_ = id_ or uuid4().hex
        rule = {'section': section, 'selector': candidate['selector']}
        if disable:
            rule['disable'] = True
        if replacement is not None:
            rule['replacement'] = replacement
        self.put('suppressions', id_, rule)
        return id_

    def reset(self):
        self._open()
        self._catalog = self._store.defaults()
        self.serial += 1

    def restore(self, snapshot):
        self._open()
        self._catalog = deepcopy(snapshot)
        self.serial += 1

    def discard(self):
        self._closed = True


