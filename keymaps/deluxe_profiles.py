"""Transactional Deluxe editing API. Call from Blender's main thread."""

from collections import defaultdict
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from .profile_draft import Draft
from .registration import RegistrationService
from .profile_storage import decode_profile, encode_profile
from .catalog_changes import CatalogChanges
from .preview_state import PreviewCache
from .event_overlap import potential_overlaps

from ..Lib.commonUtils.formats.jsonType import JSONFile
from ..Lib.commonUtils.persistence.locking import file_lock
from ..Lib.commonUtils.runtime.operations import MutationIncomplete
from . import keymap_utils as runtime
from . import default_bindings, deluxe_catalog
from .keymap_utils import resolve_scope
from .dispatch_policy import reviewed_chain, reviewed_groups
from .deluxe_resolver import Resolver, capture_candidate, command_addon, profile_assignment_id, selector_status
from .deluxe_schema import (ProfileError, independent_commands,
                            require, same_value, selector_descriptor, validate_catalog)


class ProfileStore:
    """Transactional catalog editing with a runtime apply callback."""

    @classmethod
    def open_user(cls, catalog_path, profile_path, preferences, install, **options):
        """Open a personal overlay; preserve old installed-catalog edits once."""
        catalog_path, profile_path = Path(catalog_path), Path(profile_path)
        factory_path = catalog_path.with_name('factory-defaults.json')
        factory = deluxe_catalog.load(factory_path) if factory_path.exists() else None
        issue = ''
        try:
            defaults = deluxe_catalog.load(catalog_path)
        except (OSError, ValueError) as error:
            if factory is None:
                raise
            defaults, issue = factory, str(error)
        factory = factory if factory is not None else defaults
        if not profile_path.exists() and not same_value(defaults, factory):
            # The immutable release snapshot distinguishes pre-overlay user edits
            # from publisher defaults. Keep the full original before migrating.
            profile_path.parent.mkdir(parents=True, exist_ok=True)
            with file_lock(profile_path.with_suffix('.lock')) as acquired:
                require(acquired, 'Another Blender process is migrating this profile')
                if not profile_path.exists():
                    backup = profile_path.with_name('legacy-installed-catalog.json')
                    if backup.exists() and not same_value(JSONFile(backup).read_json(), defaults):
                        from .catalog_inventory import digest
                        backup = backup.with_name('legacy-installed-catalog-' + digest(defaults)[:12] + '.json')
                    if not backup.exists():
                        JSONFile(backup).write_json(defaults, compact=True)
                    JSONFile(profile_path).write_json(encode_profile(factory, defaults), compact=True)
        store = cls(factory, profile_path, preferences, install, **options)
        if issue and not store.load_issue:
            store.load_issue = 'invalid_installed_catalog_using_factory'
            store.load_error = issue
        return store

    @classmethod
    def open_catalog(cls, path, preferences, install, *, allowed=lambda: True, install_toggle=None):
        """Edit the active add-on's full catalog in place."""
        path = Path(path)
        errors = []
        for source in (path, path.with_suffix('.previous.json')):
            try:
                defaults = deluxe_catalog.load(source)
                return cls(defaults, path, preferences, install, allowed=allowed,
                           edit_defaults=True, install_toggle=install_toggle)
            except (OSError, ValueError, RecursionError) as error:
                errors.append(str(error))
        raise ProfileError('Cannot open Deluxe keymaps: ' + errors[0])

    def __init__(self, defaults, path, preferences, install, *, allowed=lambda: True, edit_defaults=False,
                 install_toggle=None):
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
        self._install_toggle = install_toggle
        self._preview_cache = None
        self._applied_draft = None
        self._validated_draft = None
        self._allowed = allowed
        self._closed = False
        self._generation = 0
        self._revision = self._disk_revision()
        self.load_issue = None
        self.load_error = ''
        self._catalog, self.load_issue = self._read()
        self.registration = RegistrationService(self.resolver, self._preferences,
            self.runtime_catalog, lambda: self._catalog, self._allowed)
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

    @property
    def has_unsaved_edits(self):
        return self._live_catalog is not None and not same_value(self._live_catalog, self._catalog)

    def preview_draft(self, draft, *, candidate=None):
        """Try the draft in Blender without publishing any files."""
        self.validate(draft)
        candidate = draft.snapshot() if candidate is None else candidate
        previous = self.runtime_catalog()
        cache = self._preview_cache
        incremental = (cache is not None and self._install_toggle is not None
                       and cache.stamp == self._applied_draft
                       and same_value(cache.catalog, previous)
                       and cache.environment == self.preview_environment(previous))
        if not same_value(candidate, previous):
            try:
                changed = None
                if incremental:
                    changes = CatalogChanges.between(previous, candidate)
                    plan = changes.replan(self.resolver, self._preferences(), previous, candidate, cache.plan)
                    changed = self._install_toggle(candidate, previous, (cache.plan, plan))
                if changed is None:
                    self._install(candidate, previous)
                else:
                    self._refresh_preview(draft, candidate, plan, changes, changed)
            except BaseException:
                self._applied_draft = self._preview_cache = self._validated_draft = None
                self._install(previous, None)
                raise
        self._live_catalog = None if same_value(candidate, self._catalog) else candidate
        self._applied_draft = draft, draft.serial

    def cancel_preview(self):
        self._applied_draft = None
        self._preview_cache = None
        if self._live_catalog is not None:
            self._install(self._catalog, None)
            self._live_catalog = None

    def toggle_enabled(self, draft, table, id_, updates):
        """Apply a Boolean-only edit to an already validated, live draft.

        Return None when a structural edit, stale view or runtime change requires
        the normal validation path. No files or unchanged view metadata are rebuilt.
        """
        self._check_draft(draft)
        cache = self._preview_cache
        if (self._install_toggle is None or table not in {'categories', 'sections', 'assignments', 'suppressions'}
                or cache is None or cache.stamp != (draft, draft.serial)
                or self._applied_draft != (draft, draft.serial)
                or cache.environment != self.preview_environment(draft._catalog)):
            return None
        require(set(updates) <= ({'enabled', 'active'} if table == 'assignments' else {'enabled'})
                and all(type(value) is bool for value in updates.values()), 'Expected Boolean binding choices')
        row = draft._catalog[table][id_]
        require(not row.get('required') and (table in {'categories', 'sections'}
                or not draft._catalog['sections'][row['section']].get('required')),
                'Required bindings cannot be toggled')
        previous = self.runtime_catalog()
        updated = {**row, **updates}
        candidate = {**previous, table: {**previous[table], id_: updated}}
        changes = CatalogChanges.between(previous, candidate)
        new_plan = changes.replan(self.resolver, self._preferences(), previous, candidate, cache.plan)
        try:
            changed = self._install_toggle(candidate, previous, (cache.plan, new_plan))
        except BaseException:
            self._applied_draft = self._preview_cache = None
            self._install(previous, None)
            raise
        if changed is None:
            return None
        draft.update(table, id_, **updates)
        self._live_catalog = candidate
        self._applied_draft = draft, draft.serial
        preview = self._refresh_preview(draft, candidate, new_plan, changes, changed)
        self._validated_draft = (draft, draft.serial, self._preview_cache.environment)
        return preview

    def _refresh_preview(self, draft, candidate, new_plan, changes, native_changed):
        """Patch the read model after a verified edit; retain untouched metadata."""
        cache = self._preview_cache
        preview, active = cache.view, cache.active
        sections, new_groups = new_plan
        assignment_ids = set(native_changed[0]) | changes.assignments
        rule_ids = set(native_changed[1]) | changes.suppressions
        ids = assignment_ids | rule_ids
        live = self.registration_results(ids)
        for key in ids:
            preview['runtime'].pop(key, None)
        preview['runtime'].update(live)
        preview['sections'] = sections
        for key in changes.rows['commands']:
            if key in candidate['commands']:
                preview['commands'][key] = self.resolver.describe_command(candidate['commands'][key])
            else:
                preview['commands'].pop(key, None)
        for key in assignment_ids:
            if key not in candidate['assignments']:
                preview['assignments'].pop(key, None)
                continue
            definition = candidate['assignments'][key]
            preview['assignments'][key] = dict(
                eligible=bool(definition.get('required') or sections[definition['section']] and definition.get('enabled', True)),
                editable=not (definition.get('required') or candidate['sections'][definition['section']].get('required')),
                availability=preview['commands'][definition['command']]['availability'],
                active=definition.get('active', True), registered=live.get(key, (None, None))[0] == 'applied')
        for key in rule_ids:
            if key not in candidate['suppressions']:
                preview['suppressions'].pop(key, None)
                continue
            definition = candidate['suppressions'][key]
            preview['suppressions'][key] = dict(self._suppression_status(definition, candidate),
                eligible=bool(sections[definition['section']] and definition.get('enabled', True)),
                registered=live.get(key, (None, None))[0] == 'applied')
        if assignment_ids:
            active = {pair: [i for i in values if i not in assignment_ids] for pair,values in active.items()}
            active = defaultdict(list, {pair:values for pair,values in active.items() if values})
            scopes = set()
            config = runtime.get_addon_keyconfig()
            for requests in new_groups.values():
                for request in requests:
                    key = profile_assignment_id(request.request_id)
                    if key in assignment_ids and request.active:
                        scope = resolve_scope(request.scope, config)
                        active[scope, request.event].append(key)
                        scopes.add(scope)
            for key in assignment_ids:
                preview['inherited_conflicts'].pop(key, None)
            inherited = self._inherited_conflicts(active, scopes)
            preview['inherited_conflicts'].update({k:v for k,v in inherited.items() if k in assignment_ids})
            approved = reviewed_groups(candidate)
            def reviewed(values):
                return reviewed_chain(candidate, values, approved)
            preview['conflicts'] = tuple(tuple(values) for values in active.values() if len(values) > 1 and not reviewed(values))
            preview['potential_overlaps'] = potential_overlaps(active)
        self._preview_cache = PreviewCache(draft, draft.serial, candidate, preview, new_plan, active,
                                          self.preview_environment(candidate))
        return preview

    def cached_preview_token(self):
        return self._preview_cache.token

    def begin(self):
        require(not self._closed, 'Deluxe profile editor has been unloaded')
        return Draft(self, (self._generation, self._revision), self._catalog)

    def close(self):
        self._closed = True
        self._live_catalog = None

    def restore_stock_add(self):
        return self.registration.restore_stock_add()

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
        self.profile_conflicts = ()
        try:
            stored = deluxe_catalog.load(self.path, migrate=False) if self.edit_defaults else self._file.read_json()
            decoded = None if self.edit_defaults else self._decode_profile(stored)
            original = stored if self.edit_defaults else decoded.catalog
            catalog = independent_commands(original)
            self._validate(catalog)
            self.needs_migration = not same_value(original, catalog) or bool(decoded and decoded.migrated)
            self.profile_conflicts = decoded.conflicts if decoded else ()
            return catalog, None
        except FileNotFoundError:
            if not self.edit_defaults:
                return self.defaults(), None
        except (OSError, ValueError, RecursionError) as error:
            self.load_error = str(error)
        try:
            stored = (deluxe_catalog.load(self.path.with_suffix('.previous.json'), migrate=False)
                      if self.edit_defaults else self._backup.read_json())
            catalog = independent_commands(stored if self.edit_defaults else self._decode_profile(stored).catalog)
            self._validate(catalog)
            return catalog, 'invalid_profile_recovered_previous'
        except (OSError, ValueError, RecursionError):
            return self.defaults(), 'invalid_profile_recovered_defaults'

    def _decode_profile(self, document):
        baseline = self._defaults if 'profile_version' in document else self._overlay_defaults
        return decode_profile(baseline, document)

    def _validate(self, catalog, *, rna_baseline=None):
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
        self.resolver.validate(catalog, self._defaults, previous=rna_baseline)

    def validate(self, draft):
        self._check_draft(draft)
        environment = self.preview_environment(draft._catalog)
        stamp = draft, draft.serial, environment
        if self._validated_draft != stamp:
            cache = self._preview_cache
            previous = (cache.catalog if cache and cache.draft is draft
                        and cache.environment == self.preview_environment(cache.catalog) else None)
            self._validate(draft._catalog, rna_baseline=previous)
            self._validated_draft = stamp

    def _check_draft(self, draft):
        require(not self._closed, 'Deluxe profile editor has been unloaded')
        require(isinstance(draft, Draft) and draft._store is self, 'Draft belongs to a different profile')
        draft._open()
        require(draft._revision == (self._generation, self._revision), 'Profile edit is stale')

    def preview(self, draft=None):
        """Return stored/effective state, command metadata and runtime diagnostics."""
        if draft is not None:
            self.validate(draft)
            cache = self._preview_cache
            if cache and cache.stamp == (draft, draft.serial) and cache.environment == self.preview_environment(cache.catalog):
                # Runtime diagnostics can change independently of this draft.
                if cache.token == self.preview_token(cache.catalog):
                    return cache.view
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
        approved = reviewed_groups(catalog)
        conflicts = tuple(tuple(ids) for ids in active.values()
                          if len(ids) > 1 and not reviewed_chain(catalog, ids, approved))
        required = {id_ for id_, row in catalog['sections'].items() if row.get('required')}
        live = self.registration_results()
        preview = {
            'load_issue': self.load_issue,
            'sections': state,
            'assignments': {id_: {'eligible': bool(row.get('required') or state[row['section']] and row.get('enabled', True)),
                                  'active': row.get('active', True),
                                  'editable': row['section'] not in required and not row.get('required'),
                                  'availability': commands[row['command']]['availability'],
                                  'registered': live.get(id_, (None, None))[0] == 'applied'}
                            for id_, row in assignments.items()},
            'commands': commands, 'conflicts': conflicts, 'inherited_conflicts': inherited,
            'potential_overlaps': potential_overlaps(active),
            'suppressions': {id_: {**self._suppression_status(row, catalog),
                                   'eligible': bool(state[row['section']] and row.get('enabled', True)),
                                   'registered': live.get(id_, (None, None))[0] == 'applied'}
                             for id_, row in catalog['suppressions'].items()},
            'runtime': live,
        }
        if draft is not None:
            self._preview_cache = PreviewCache(draft, draft.serial, draft.snapshot(), preview, (state, groups), active,
                                               self.preview_environment(catalog))
            if same_value(catalog, self.runtime_catalog()):
                self._applied_draft = draft, draft.serial
        return preview

    def preview_token(self, catalog):
        """Cheap invalidation for browsing; edits still validate before applying."""
        return self.preview_environment(catalog) + (tuple(sorted(self.registration_results().items())),)

    def preview_environment(self, catalog):
        """Native config/provider identities shared by both editor apply paths."""
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
        addons = {command_addon(command) for command in catalog['commands'].values()} - {''}
        configs = []
        for role in ('default', 'addon', 'user', 'active'):
            try:
                config = runtime.configuration(role)
                configs.append((role, getattr(config, 'as_pointer', lambda: id(config))(),
                                len(tuple(config.keymaps))))
            except runtime.Pending:
                configs.append((role, None))
        return (self._generation, self._allowed(), self._preferences().keymap.enable_keymaps,
                tuple(configs), tuple(rna), tuple((name, runtime.provider_enabled(name)) for name in sorted(addons)))

    @staticmethod
    def _inherited_conflicts(active, scopes=None):
        """Report exact event overlap with the built-in base by assignment ID."""
        matches = defaultdict(list)
        try:
            config = runtime.configuration('default')
            owned_modal = runtime.owned_item_tokens(config)
            for map_ in config.keymaps:
                scope = runtime.capture_scope(map_)
                if scopes is not None and scope not in scopes:
                    continue
                for item in map_.keymap_items:
                    if not item.active or (runtime.native_identity(map_), runtime.native_identity(item), item.id) in owned_modal:
                        continue
                    try:
                        event = runtime.capture_event(item)
                    except runtime.Pending:
                        continue
                    for id_ in active.get((scope, event), ()):
                        matches[id_].append(item.propvalue if scope.is_modal else item.idname)
        except runtime.Pending:
            pass
        return {id_: tuple(targets) for id_, targets in matches.items()}

    def _suppression_status(self, row, catalog):
        selector = selector_descriptor(row['selector'])
        if row.get('disable'):
            status, reason = default_bindings.status(
                selector, explicit_properties=row.get('explicit_properties', False))
            return {'status': status, 'reason': reason}
        replacement = (self.resolver.target(catalog['commands'][row['replacement']])
                       if 'replacement' in row else None)
        status, reason = selector_status(selector, replacement)
        return {'status': status, 'reason': reason}

    def apply(self, draft):
        """Install then publish. Restore the committed runtime if either step fails."""
        self.validate(draft)
        candidate = deepcopy(draft._catalog)
        stored = candidate if self.edit_defaults else encode_profile(self._defaults, candidate)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with file_lock(self._lock) as acquired:
            require(acquired, 'Another Blender process is saving this profile')
            require(self._disk_revision() == self._revision != 'unreadable', 'Profile file changed on disk')
            if not self.load_issue and not self.needs_migration and same_value(candidate, self._catalog):
                draft.discard()
                return self.snapshot()
            previous = self._catalog
            # Keep an independently validated recovery copy before changing runtime.
            backup = previous if self.edit_defaults else encode_profile(self._defaults, previous)
            self._backup.write_json(backup, compact=True)
            try:
                if not same_value(candidate, self.runtime_catalog()):
                    self._install(candidate, self.runtime_catalog())
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
            self.profile_conflicts = ()
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
        return self.registration.plan(catalog, required_only=required_only)

    def registration_results(self, ids=None):
        return self.registration.registration_results(ids)

    def check_registration(self, catalog, before, **options):
        return self.registration.check_registration(catalog, before, **options)

    def update_registration(self, candidate, previous, **options):
        return self.registration.update_registration(candidate, previous, **options)

    def register(self, catalog=None, **options):
        return self.registration.register(catalog, **options)

    @staticmethod
    def capture_binding(map_, item, source_role):
        return capture_candidate(map_, item, source_role)
