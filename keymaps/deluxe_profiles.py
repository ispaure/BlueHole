"""Transactional Deluxe editing API. Call from Blender's main thread."""

from collections import defaultdict
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from ..Lib.commonUtils.formats.jsonType import JSONFile
from ..Lib.commonUtils.persistence.locking import file_lock
from ..Lib.commonUtils.runtime.operations import MutationIncomplete
from . import keymap_utils as runtime
from .keymap_action_utils import resolve_scope
from .deluxe_resolver import Resolver, capture_candidate, profile_assignment_id, selector_status
from .deluxe_schema import (ProfileError, TABLES, identifier, merge_profile, profile_overlay,
                            require, same_value, selector_descriptor, validate_catalog)


class Draft:
    """A detached working copy tied to one store revision."""

    def __init__(self, store, revision, catalog):
        self._store = store
        self._revision = revision
        self._catalog = deepcopy(catalog)
        self._closed = False

    def snapshot(self):
        return deepcopy(self._catalog)

    def _open(self):
        require(not self._closed, 'Draft has been closed')

    def put(self, table, id_, row):
        """Insert or replace one complete row. Validation allows multi-step edits."""
        self._open()
        require(table in TABLES and identifier(id_) and isinstance(row, dict), 'Invalid draft entry')
        self._catalog[table][id_] = deepcopy(row)

    def update(self, table, id_, **fields):
        self.put(table, id_, {**self._catalog[table][id_], **fields})

    def delete(self, table, id_):
        self._open()
        require(table in TABLES, 'Unknown profile table')
        del self._catalog[table][id_]

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

    def stage_suppression(self, section, map_, item, source_role, *, replacement=None, id_=None):
        """Capture a selected live row. Passing a saved ID retargets that rule."""
        self._open()
        candidate = capture_candidate(map_, item, source_role)
        id_ = id_ or uuid4().hex
        rule = {'section': section, 'selector': candidate['selector']}
        if replacement is not None:
            rule['replacement'] = replacement
        self.put('suppressions', id_, rule)
        return id_

    def reset(self):
        self._open()
        self._catalog = self._store.defaults()

    def discard(self):
        self._closed = True


class ProfileStore:
    """A shipped catalog, a sparse local overlay, and the runtime apply callback."""

    def __init__(self, defaults, path, preferences, install, *, allowed=lambda: True):
        validate_catalog(defaults)
        self._defaults = deepcopy(defaults)
        self._catalog = deepcopy(defaults)
        self.resolver = Resolver(defaults)
        self.path = Path(path)
        self._file = JSONFile(self.path)
        self._backup = JSONFile(self.path.with_suffix('.previous.json'))
        self._lock = self.path.with_suffix('.lock')
        self._preferences = preferences
        self._install = install
        self._allowed = allowed
        self._closed = False
        self._generation = 0
        self._revision = self._disk_revision()
        self.load_issue = None
        self._catalog, self.load_issue = self._read()

    def defaults(self):
        return deepcopy(self._defaults)

    def snapshot(self):
        return deepcopy(self._catalog)

    def section_enabled(self, section):
        """Whether the applied profile and current preferences enable a section."""
        return self._allowed() and self.resolver.section_enabled(self._catalog, self._preferences(), section)

    def begin(self):
        require(not self._closed, 'Deluxe profile editor has been unloaded')
        return Draft(self, (self._generation, self._revision), self._catalog)

    def close(self):
        self._closed = True

    def _disk_revision(self):
        try:
            return sha256(self.path.read_bytes()).digest()
        except FileNotFoundError:
            return None
        except OSError:
            return 'unreadable'

    def _read(self):
        try:
            catalog = merge_profile(self._defaults, self._file.read_json())
            self._validate(catalog)
            return catalog, None
        except FileNotFoundError:
            return self.defaults(), None
        except (OSError, ValueError, RecursionError):
            try:
                catalog = merge_profile(self._defaults, self._backup.read_json())
                self._validate(catalog)
                return catalog, 'invalid_profile_recovered_previous'
            except (OSError, ValueError, RecursionError):
                return self.defaults(), 'invalid_profile_recovered_defaults'

    def _validate(self, catalog):
        validate_catalog(catalog)
        for table in ('categories', 'sections', 'assignments'):
            for id_, row in catalog[table].items():
                shipped = self._defaults[table].get(id_, {})
                keys = ('switch', 'required') if table != 'assignments' else ('feature', 'samples', 'kind')
                for key in keys:
                    expected = shipped.get(key, id_ if key == 'feature' else None)
                    require(row.get(key) == expected, f'Code-managed {key} in {id_}')
        required = {id_ for id_, row in self._defaults['sections'].items() if row.get('required')}
        for section in required:
            require(same_value(catalog['sections'].get(section), self._defaults['sections'][section]),
                    f'Required section {section} is read-only')
            category = self._defaults['sections'][section]['category']
            require(category in catalog['categories'], f'Required section needs category {category}')
        for id_, row in catalog['assignments'].items():
            require(row['section'] not in required or
                    self._defaults['assignments'].get(id_, {}).get('section') in required,
                    'Required section cannot contain user bindings')
        for row in catalog['suppressions'].values():
            require(row['section'] not in required, 'Required section cannot contain suppressions')
        for id_, row in self._defaults['assignments'].items():
            if row['section'] not in required:
                continue
            require(same_value(catalog['assignments'].get(id_), row), 'Required binding is read-only')
            for key, table in (('event', 'events'), ('command', 'commands')):
                require(same_value(catalog[table].get(row[key]), self._defaults[table][row[key]]),
                        'Required event or command is read-only')
        self.resolver.validate(catalog, self._defaults)

    def validate(self, draft):
        self._check_draft(draft)
        self._validate(draft._catalog)

    def _check_draft(self, draft):
        require(not self._closed, 'Deluxe profile editor has been unloaded')
        require(isinstance(draft, Draft) and draft._store is self, 'Draft belongs to a different profile')
        draft._open()
        require(draft._revision == (self._generation, self._revision), 'Profile edit is stale')

    def preview(self, draft=None):
        """Return stored/effective state, command metadata and runtime diagnostics."""
        if draft is not None:
            self.validate(draft)
        catalog = self._catalog if draft is None else draft._catalog
        state, groups = self._plan(catalog)
        assignments = catalog['assignments']
        commands = {id_: self.resolver.describe_command(row) for id_, row in catalog['commands'].items()}
        active = defaultdict(list)
        config = runtime.get_addon_keyconfig()
        for requests in groups.values():
            for request in requests:
                if request.active:
                    scope = resolve_scope(request.scope, config)
                    active[scope, request.event].append(profile_assignment_id(request.request_id))
        inherited = self._inherited_conflicts(active)
        conflicts = tuple(tuple(ids) for ids in active.values() if len(ids) > 1)
        required = {id_ for id_, row in catalog['sections'].items() if row.get('required')}
        live = self.registration_results()
        return {
            'load_issue': self.load_issue,
            'sections': state,
            'assignments': {id_: {'eligible': bool(state[row['section']] and row.get('enabled', True)),
                                  'active': row.get('active', True),
                                  'editable': row['section'] not in required,
                                  'availability': commands[row['command']]['availability'],
                                  'registered': live.get(id_, (None, None))[0] == 'applied'}
                            for id_, row in assignments.items()},
            'commands': commands, 'conflicts': conflicts, 'inherited_conflicts': inherited,
            'suppressions': {id_: {**self._suppression_status(row, catalog),
                                   'eligible': bool(state[row['section']] and row.get('enabled', True)),
                                   'registered': live.get(id_, (None, None))[0] == 'applied'}
                             for id_, row in catalog['suppressions'].items()},
            'runtime': live,
        }

    @staticmethod
    def _inherited_conflicts(active):
        """Report exact event overlap with the built-in base by assignment ID."""
        matches = defaultdict(list)
        try:
            for map_ in runtime._config('default').keymaps:
                scope = runtime.capture_scope(map_)
                for item in map_.keymap_items:
                    if not item.active:
                        continue
                    try:
                        event = runtime.capture_event(item)
                    except runtime._Pending:
                        continue
                    for id_ in active.get((scope, event), ()):
                        matches[id_].append(item.propvalue if scope.is_modal else item.idname)
        except runtime._Pending:
            pass
        return {id_: tuple(targets) for id_, targets in matches.items()}

    def _suppression_status(self, row, catalog):
        selector = selector_descriptor(row['selector'])
        replacement = (self.resolver.target(catalog['commands'][row['replacement']])
                       if 'replacement' in row else None)
        status, reason = selector_status(selector, replacement)
        return {'status': status, 'reason': reason}

    def apply(self, draft):
        """Install then publish. Restore the committed runtime if either step fails."""
        self.validate(draft)
        candidate = deepcopy(draft._catalog)
        overlay = profile_overlay(self._defaults, candidate)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with file_lock(self._lock) as acquired:
            require(acquired, 'Another Blender process is saving this profile')
            require(self._disk_revision() == self._revision != 'unreadable', 'Profile file changed on disk')
            if not self.load_issue and same_value(candidate, self._catalog):
                draft.discard()
                return self.snapshot()
            previous = self._catalog
            # Keep an independently validated recovery copy before changing runtime.
            self._backup.write_json(profile_overlay(self._defaults, previous), compact=True)
            try:
                self._install(candidate, previous)
                require(self._disk_revision() == self._revision, 'Profile file changed during apply')
                try:
                    self._file.write_json(overlay, compact=True)
                except MutationIncomplete as issue:
                    if not issue.result.destination_published:
                        raise
            except BaseException:
                try:
                    self._install(previous, None)
                except Exception as rollback:
                    raise ProfileError('Profile rollback failed. Reload the committed profile.') from rollback
                raise
            self._catalog = candidate
            self._revision = self._disk_revision()
            self._generation += 1
            self.load_issue = None
            draft.discard()
            try:
                self._backup.write_json(overlay, compact=True)
            except OSError:
                self.load_issue = 'profile_saved_recovery_copy_unavailable'
            return self.snapshot()

    def reload(self):
        """Load a compatible overlay or recover the last known good catalog."""
        require(not self._closed, 'Deluxe profile editor has been unloaded')
        revision = self._disk_revision()
        candidate, issue = self._read()
        require(self._disk_revision() == revision, 'Profile changed during reload')
        previous = self._catalog
        if issue or same_value(candidate, previous):
            # A failed read leaves the installed profile in place.
            self._revision = revision
            self._generation += 1
            self.load_issue = issue
            return self.snapshot()
        try:
            self._install(candidate, previous)
            require(self._disk_revision() == revision, 'Profile changed during reload')
        except BaseException:
            self._install(previous, None)
            raise
        self._catalog = candidate
        self._revision = revision
        self._generation += 1
        self.load_issue = issue
        return self.snapshot()

    def _plan(self, catalog):
        if not self._allowed():
            return dict.fromkeys(catalog['sections'], False), {}
        return self.resolver.plan(catalog, self._preferences())

    @staticmethod
    def registration_results():
        results = {}
        for diagnostic in runtime.runtime_diagnostics():
            if ':deluxe-' not in diagnostic.owner_id:
                continue
            id_ = profile_assignment_id(diagnostic.request_id)
            if id_ not in results or diagnostic.status != 'applied':
                results[id_] = (diagnostic.status, diagnostic.reason)
        return results

    def check_registration(self, catalog, before):
        """Reject new registration errors, preserving known or unavailable rows."""
        after = self.registration_results()
        sections, groups = self._plan(catalog)
        for requests in groups.values():
            for request in requests:
                id_ = request.request_id
                if id_ not in catalog['assignments']:
                    continue
                status, reason = after.get(id_, ('pending', 'feature_registration_incomplete'))
                if status == 'applied':
                    continue
                row = catalog['assignments'][id_]
                command = catalog['commands'][row['command']]
                if self.resolver.describe_command(command)['availability'] == 'waiting_for_provider':
                    continue
                unchanged = same_value(self._catalog['assignments'].get(id_), row)
                unchanged = unchanged and all(same_value(self._catalog[table].get(row[key]),
                                                          catalog[table][row[key]])
                                              for key, table in (('command', 'commands'), ('event', 'events')))
                if unchanged and before.get(id_) == (status, reason):
                    continue
                raise ProfileError(f'Cannot register {id_}: {reason}')
        for id_, row in catalog['suppressions'].items():
            if not (sections[row['section']] and row.get('enabled', True)):
                continue
            status, reason = after.get(id_, (None, None))
            if status in (None, 'applied'):
                continue
            if reason in ('creation_or_setter_failed', 'owned_remove_failed',
                          'unsupported_creation_schema', 'created_readback_mismatch',
                          'created_membership_lost', 'conflicting_assignment'):
                raise ProfileError(f'Cannot register replacement {id_}: {reason}')

    def register(self, catalog=None):
        """Register in source order through brief 02's feature ledger."""
        if catalog is None:
            catalog = self._catalog
        sections, groups = self._plan(catalog)
        total = 0
        for owner, requests in groups.items():
            config = runtime.get_addon_keyconfig()
            requests = tuple(replace(request, scope=resolve_scope(request.scope, config))
                             for request in requests)
            handle = runtime.register_feature(owner, assignments=requests)
            total += len(handle.owned_pairs)
        for id_, row in catalog['suppressions'].items():
            if not (sections[row['section']] and row.get('enabled', True)):
                continue
            request = self.resolver.suppression_request(id_, row, catalog['commands'])
            if request is not None:
                handle = runtime.register_feature('profile:deluxe-' + id_, overrides=(request,))
                total += len(handle.owned_pairs)
        return total
