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
from . import default_bindings, deluxe_catalog
from .keymap_utils import resolve_scope
from .deluxe_resolver import Resolver, capture_candidate, profile_assignment_id, selector_status
from .deluxe_schema import (ProfileError, TABLES, identifier, independent_commands, merge_profile, profile_overlay,
                            require, same_value, selector_descriptor, validate_catalog)

ADD_PIE_EVENT = runtime.KeymapEvent('A', value='CLICK_DRAG', shift=True)
ADD_PIE_TARGET = runtime.KeymapTarget('wm.call_menu_pie', {'name': 'BLUEHOLE_MT_pie_add'})
ADD_PIE_SCOPE = runtime.KeymapScope('3D View', 'VIEW_3D')
STOCK_ADD_EVENT = runtime.KeymapEvent('A', shift=True)
STOCK_ADD_MENUS = (('Object Mode', 'VIEW3D_MT_add'), ('Mesh', 'VIEW3D_MT_mesh_add'))


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
        candidate = capture_candidate(map_, item, source_role)
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

    def restore(self, snapshot):
        self._open()
        self._catalog = deepcopy(snapshot)

    def discard(self):
        self._closed = True


class ProfileStore:
    """Transactional catalog editing with a runtime apply callback."""

    @classmethod
    def open_catalog(cls, path, preferences, install, *, allowed=lambda: True):
        """Edit the active add-on's full catalog in place."""
        path = Path(path)
        errors = []
        for source in (path, path.with_suffix('.previous.json')):
            try:
                defaults = deluxe_catalog.load(source)
                return cls(defaults, path, preferences, install, allowed=allowed, edit_defaults=True)
            except (OSError, ValueError, RecursionError) as error:
                errors.append(str(error))
        raise ProfileError('Cannot open Deluxe keymaps: ' + errors[0])

    def __init__(self, defaults, path, preferences, install, *, allowed=lambda: True, edit_defaults=False):
        validate_catalog(defaults)
        self._overlay_defaults = deepcopy(defaults)
        defaults = independent_commands(defaults)
        self._defaults = deepcopy(defaults)
        self._catalog = deepcopy(defaults)
        self.resolver = Resolver(defaults)
        self.path = Path(path)
        self.edit_defaults = edit_defaults
        self._file = JSONFile(self.path)
        self._backup = JSONFile(self.path.with_suffix('.previous.json'))
        self._lock = self.path.with_suffix('.lock')
        self._preferences = preferences
        self._install = install
        self._allowed = allowed
        self._closed = False
        self._stock_add_rows = []
        self._generation = 0
        self._revision = self._disk_revision()
        self.load_issue = None
        self.load_error = ''
        self._catalog, self.load_issue = self._read()
        self._live_catalog = None

    def defaults(self):
        return deepcopy(self._defaults)

    def snapshot(self):
        return deepcopy(self._catalog)

    def section_enabled(self, section):
        """Whether the applied profile and current preferences enable a section."""
        return self._allowed() and self.resolver.section_enabled(self.runtime_catalog(), self._preferences(), section)

    def runtime_catalog(self):
        return self._catalog if self._live_catalog is None else self._live_catalog

    def preview_draft(self, draft):
        """Try the draft in Blender without publishing any files."""
        self.validate(draft)
        candidate = draft.snapshot()
        previous = self.runtime_catalog()
        if not same_value(candidate, previous):
            try:
                self._install(candidate, previous)
            except BaseException:
                self._install(previous, None)
                raise
        self._live_catalog = None if same_value(candidate, self._catalog) else candidate

    def cancel_preview(self):
        if self._live_catalog is not None:
            self._install(self._catalog, None)
            self._live_catalog = None

    def begin(self):
        require(not self._closed, 'Deluxe profile editor has been unloaded')
        return Draft(self, (self._generation, self._revision), self._catalog)

    def close(self):
        self._closed = True
        self._live_catalog = None

    def _defer_stock_add(self):
        """Let Blender distinguish Shift+A tap from drag before opening Add."""
        source = runtime._config('default')
        if not runtime._same(source, runtime._config('active')):
            return
        # Ordinary bindings may still be waiting for the bulk merge. The stock
        # source checks below require the current effective user keymaps.
        runtime._update_merged()
        rows = []
        for name, menu in STOCK_ADD_MENUS:
            scope = resolve_scope(runtime.KeymapScope(name), source)
            if scope.is_tool:
                continue
            target = runtime.KeymapTarget('wm.call_menu', {'name': menu})
            selector = runtime.KeymapSelector(scope, STOCK_ADD_EVENT, target)
            try:
                _, source_map, item = runtime._exact_source(selector)
                runtime._preflight_merged_source(selector)
                merged = runtime._one_map(runtime._config('user'), scope)
                user_item = merged.keymap_items.from_id(item.id)
                if (user_item is None or user_item.is_user_modified or user_item.is_user_defined
                        or runtime._snapshot(user_item, False) != (STOCK_ADD_EVENT, target, True)):
                    continue
            except runtime._Pending:
                # A custom binding or a different Blender keymap takes precedence.
                continue
            rows.append((source_map, item, item.id, target))
        try:
            # Edit the in-memory default source so Blender saves no user keymap delta.
            for row in rows:
                self._stock_add_rows.append(row)
                row[1].value = 'RELEASE'
            if rows:
                runtime._update_merged()
        except Exception:
            self.restore_stock_add()
            raise

    def restore_stock_add(self):
        if not self._stock_add_rows:
            return
        source = runtime._config('default')
        expected = replace(STOCK_ADD_EVENT, value='RELEASE')
        for source_map, item, item_id, target in self._stock_add_rows:
            if (runtime._contains(source.keymaps, source_map)
                    and runtime._contains(source_map.keymap_items, item)
                    and item.id == item_id
                    and runtime._snapshot(item, False) == (expected, target, True)):
                item.value = 'PRESS'
        runtime._request_merged_update()
        self._stock_add_rows.clear()

    def _disk_revision(self):
        if self.edit_defaults:
            return deluxe_catalog.revision(self.path)
        try:
            return sha256(self.path.read_bytes()).digest()
        except FileNotFoundError:
            return None
        except OSError:
            return 'unreadable'

    def _read(self):
        self.load_error = ''
        self.needs_migration = False
        try:
            stored = deluxe_catalog.load(self.path, migrate=False) if self.edit_defaults else self._file.read_json()
            original = stored if self.edit_defaults else merge_profile(self._overlay_defaults, stored)
            catalog = independent_commands(original)
            self._validate(catalog)
            self.needs_migration = not same_value(original, catalog)
            return catalog, None
        except FileNotFoundError:
            if not self.edit_defaults:
                return self.defaults(), None
        except (OSError, ValueError, RecursionError) as error:
            self.load_error = str(error)
        try:
            stored = (deluxe_catalog.load(self.path.with_suffix('.previous.json'), migrate=False)
                      if self.edit_defaults else self._backup.read_json())
            catalog = independent_commands(stored if self.edit_defaults else merge_profile(self._overlay_defaults, stored))
            self._validate(catalog)
            return catalog, 'invalid_profile_recovered_previous'
        except (OSError, ValueError, RecursionError):
            return self.defaults(), 'invalid_profile_recovered_defaults'

    def _validate(self, catalog):
        validate_catalog(catalog)
        commands = [row['command'] for row in catalog['assignments'].values()]
        commands += [row['replacement'] for row in catalog['suppressions'].values() if 'replacement' in row]
        require(len(commands) == len(set(commands)), 'Each binding must own its command settings')
        for table in ('categories', 'sections', 'assignments'):
            for id_, row in catalog[table].items():
                shipped = self._defaults[table].get(id_, {})
                keys = ('switch', 'required') if table != 'assignments' else ('feature', 'samples', 'kind', 'dispatch_group', 'required')
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
            if row['section'] not in required and not row.get('required'):
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
        def reviewed_chain(ids):
            group = assignments[ids[0]].get('dispatch_group')
            return group and all(assignments[id_].get('dispatch_group') == group for id_ in ids)
        conflicts = tuple(tuple(ids) for ids in active.values() if len(ids) > 1 and not reviewed_chain(ids))
        required = {id_ for id_, row in catalog['sections'].items() if row.get('required')}
        live = self.registration_results()
        return {
            'load_issue': self.load_issue,
            'sections': state,
            'assignments': {id_: {'eligible': bool(row.get('required') or state[row['section']] and row.get('enabled', True)),
                                  'active': row.get('active', True),
                                  'editable': row['section'] not in required and not row.get('required'),
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

    def preview_token(self, catalog):
        """Cheap invalidation for browsing; edits still validate before applying."""
        operators = {row['operator'] for row in catalog['commands'].values() if 'operator' in row}
        operators.update(row['selector']['target']['idname'] for row in catalog['suppressions'].values()
                         if 'idname' in row['selector']['target'])
        rna = []
        for id_ in sorted(operators):
            value = self.resolver.describe_operator_token(id_)
            rna.append((id_, value))
        for command in catalog['commands'].values():
            if command.get('operator') in {'wm.call_menu', 'wm.call_menu_pie', 'wm.call_panel'}:
                name = command['properties'].get('name', '')
                rna.append((name, id(getattr(getattr(runtime.bpy, 'types', None), name, None))))
        configs = []
        for role in ('default', 'addon', 'user', 'active'):
            try:
                config = runtime._config(role)
                configs.append((role, getattr(config, 'as_pointer', lambda: id(config))(),
                                len(tuple(config.keymaps))))
            except runtime._Pending:
                configs.append((role, None))
        return (self._generation, self._allowed(), self._preferences().keymap.enable_keymaps,
                tuple(configs), tuple(rna), tuple(self.registration_results().items()))

    @staticmethod
    def _inherited_conflicts(active):
        """Report exact event overlap with the built-in base by assignment ID."""
        matches = defaultdict(list)
        try:
            config = runtime._config('default')
            owned_modal = {(owned.map_pointer, owned.item_pointer, owned.item_id)
                           for handle in runtime._FEATURES.values() for owned in handle._owned.values()
                           if owned.config_pointer == runtime._pointer(config)}
            for map_ in config.keymaps:
                scope = runtime.capture_scope(map_)
                for item in map_.keymap_items:
                    if not item.active or (runtime._pointer(map_), runtime._pointer(item), item.id) in owned_modal:
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
        if row.get('disable'):
            status, reason = default_bindings.status(
                selector, explicit_properties=row.get('explicit_properties', False),
                requires_assignment=row.get('requires_assignment', ''))
            return {'status': status, 'reason': reason}
        replacement = (self.resolver.target(catalog['commands'][row['replacement']])
                       if 'replacement' in row else None)
        status, reason = selector_status(selector, replacement)
        return {'status': status, 'reason': reason}

    def apply(self, draft):
        """Install then publish. Restore the committed runtime if either step fails."""
        self.validate(draft)
        candidate = deepcopy(draft._catalog)
        stored = candidate if self.edit_defaults else profile_overlay(self._overlay_defaults, candidate)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with file_lock(self._lock) as acquired:
            require(acquired, 'Another Blender process is saving this profile')
            require(self._disk_revision() == self._revision != 'unreadable', 'Profile file changed on disk')
            if not self.load_issue and not self.needs_migration and same_value(candidate, self._catalog):
                draft.discard()
                return self.snapshot()
            previous = self._catalog
            # Keep an independently validated recovery copy before changing runtime.
            backup = previous if self.edit_defaults else profile_overlay(self._overlay_defaults, previous)
            self._backup.write_json(backup, compact=True)
            try:
                self._install(candidate, previous)
                require(self._disk_revision() == self._revision, 'Profile file changed during apply')
                try:
                    if self.edit_defaults:
                        self._publish_catalog(candidate)
                    else:
                        self._file.write_json(stored, compact=True)
                except MutationIncomplete as issue:
                    if self.edit_defaults or not issue.result.destination_published:
                        raise
            except BaseException:
                try:
                    self._install(previous, None)
                    self._live_catalog = None
                except Exception as rollback:
                    raise ProfileError('Profile rollback failed. Reload the committed profile.') from rollback
                raise
            self._catalog = candidate
            self._live_catalog = None
            self._revision = self._disk_revision()
            self._generation += 1
            self.load_issue = None
            self.load_error = ''
            self.needs_migration = False
            draft.discard()
            try:
                self._backup.write_json(stored, compact=True)
            except OSError:
                self.load_issue = 'profile_saved_recovery_copy_unavailable'
            return self.snapshot()

    def _publish_catalog(self, catalog):
        deluxe_catalog.publish(self.path, catalog, self._catalog, self._revision)

    def reload(self):
        """Load a compatible profile or retain the last known good catalog."""
        require(not self._closed, 'Deluxe profile editor has been unloaded')
        self.cancel_preview()
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

    def _plan(self, catalog, *, required_only=False):
        if not self._allowed():
            return dict.fromkeys(catalog['sections'], False), {}
        return self.resolver.plan(catalog, self._preferences(), required_only=required_only)

    @staticmethod
    def registration_results():
        results = default_bindings.registration_results()
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
                if self.resolver.describe_command(command)['availability'] != 'available':
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

    @runtime.batch_merged_updates()
    def register(self, catalog=None, *, required_only=False):
        """Register in source order through brief 02's feature ledger."""
        if catalog is None:
            catalog = self.runtime_catalog()
        sections, groups = self._plan(catalog, required_only=required_only)
        total = 0
        add_pie_registered = False
        for owner, requests in groups.items():
            config = runtime.get_addon_keyconfig()
            requests = tuple(replace(request, scope=resolve_scope(request.scope, config))
                             for request in requests)
            handle = runtime.register_feature(owner, assignments=requests)
            total += len(handle.owned_pairs)
            applied = {row.request_id for row in handle.diagnostics if row.status == 'applied'}
            add_pie_registered |= any(
                request.request_id in applied and request.active and request.event == ADD_PIE_EVENT
                and replace(request.scope, is_tool=None) == ADD_PIE_SCOPE and request.scope.is_tool is not True
                and request.target == ADD_PIE_TARGET for request in requests)
        for id_, row in catalog['suppressions'].items():
            if not (sections[row['section']] and row.get('enabled', True)):
                continue
            if row.get('disable'):
                default_bindings.install(id_, selector_descriptor(row['selector']),
                                         explicit_properties=row.get('explicit_properties', False),
                                         requires_assignment=row.get('requires_assignment', ''))
                continue
            request = self.resolver.suppression_request(id_, row, catalog['commands'])
            if request is not None:
                handle = runtime.register_feature('profile:deluxe-' + id_, overrides=(request,))
                total += len(handle.owned_pairs)
        if add_pie_registered:
            self._defer_stock_add()
        return total
