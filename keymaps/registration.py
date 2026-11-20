"""Native execution and verification of compiled catalog plans.

This service owns temporary stock adjustments. Persistence and draft state are
supplied through read-only callbacks; the service never writes profile files.
"""
from dataclasses import replace
from . import keymap_utils as runtime, default_bindings
from .keymap_utils import resolve_scope
from .deluxe_schema import ProfileError, same_value, selector_descriptor
from .deluxe_resolver import profile_assignment_id

ADD_PIE_EVENT = runtime.KeymapEvent('A', value='CLICK_DRAG', shift=True)
ADD_PIE_TARGET = runtime.KeymapTarget('wm.call_menu_pie', {'name': 'BLUEHOLE_MT_pie_add'})
ADD_PIE_SCOPE = runtime.KeymapScope('3D View', 'VIEW_3D')
STOCK_ADD_EVENT = runtime.KeymapEvent('A', shift=True)
STOCK_ADD_MENUS = (('Object Mode', 'VIEW3D_MT_add'), ('Mesh', 'VIEW3D_MT_mesh_add'))


class RegistrationService:
    def __init__(self, resolver, preferences, catalog, saved_catalog, allowed):
        self.resolver = resolver
        self._preferences, self.catalog, self.saved_catalog = preferences, catalog, saved_catalog
        self._allowed = allowed
        self._stock_add_rows = []
        self._stock_restore_pending = False

    def _defer_stock_add(self):
        """Let Blender distinguish Shift+A tap from drag before opening Add."""
        source = runtime.configuration('default')
        if not runtime.same_identity(source, runtime.configuration('active')):
            return
        # Ordinary bindings may still be waiting for the bulk merge. The stock
        # source checks below require the current effective user keymaps.
        runtime.flush_merged()
        rows = []
        for name, menu in STOCK_ADD_MENUS:
            scope = resolve_scope(runtime.KeymapScope(name), source)
            if scope.is_tool:
                continue
            target = runtime.KeymapTarget('wm.call_menu', {'name': menu})
            selector = runtime.KeymapSelector(scope, STOCK_ADD_EVENT, target)
            try:
                _, source_map, item = runtime.exact_source(selector)
                runtime.verify_merged_source(selector)
                merged = runtime.matching_map(runtime.configuration('user'), scope)
                user_item = merged.keymap_items.from_id(item.id)
                if (user_item is None or user_item.is_user_modified or user_item.is_user_defined
                        or runtime.snapshot_item(user_item, False) != (STOCK_ADD_EVENT, target, True)):
                    continue
            except runtime.Pending:
                # A custom binding or a different Blender keymap takes precedence.
                continue
            rows.append((source_map, item, item.id, target))
        try:
            # Edit the in-memory default source so Blender saves no user keymap delta.
            for row in rows:
                self._stock_add_rows.append(row)
                row[1].value = 'RELEASE'
            if rows:
                runtime.flush_merged()
        except Exception:
            self.restore_stock_add()
            raise

    def restore_stock_add(self):
        """Restore only unchanged owned values; retain unreadable rows for retry."""
        if not self._stock_add_rows:
            self._stock_restore_pending = False
            return True
        expected = replace(STOCK_ADD_EVENT, value='RELEASE')
        pending = []
        changed = False
        for row in self._stock_add_rows:
            source_map, item, item_id, target = row
            try:
                source = runtime.configuration('default')
                if (runtime.contains_native(source.keymaps, source_map)
                        and runtime.contains_native(source_map.keymap_items, item)
                        and item.id == item_id
                        and runtime.snapshot_item(item, False) == (expected, target, True)):
                    item.value = 'PRESS'
                    changed = True
            except (runtime.Pending, AttributeError, ReferenceError, RuntimeError, TypeError):
                pending.append(row)
        self._stock_add_rows = pending
        self._stock_restore_pending = bool(pending)
        if changed:
            runtime.request_merged_update()
        return not pending

    @property
    def stock_cleanup_pending(self):
        return self._stock_restore_pending

    def plan(self, catalog, *, required_only=False):
        if not self._allowed():
            return dict.fromkeys(catalog['sections'], False), {}
        return self.resolver.plan(catalog, self._preferences(), required_only=required_only)

    @staticmethod
    def registration_results(ids=None):
        results = default_bindings.registration_results(ids)
        for diagnostic in runtime.runtime_diagnostics():
            if ':deluxe-' not in diagnostic.owner_id:
                continue
            id_ = profile_assignment_id(diagnostic.request_id)
            if ids is not None and id_ not in ids:
                continue
            if id_ not in results or diagnostic.status != 'applied':
                results[id_] = (diagnostic.status, diagnostic.reason)
        return results

    def check_registration(self, catalog, before, *, plan=None, ids=None):
        """Reject new registration errors, preserving known or unavailable rows."""
        after = self.registration_results(ids)
        sections, groups = self.plan(catalog) if plan is None else plan
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
                unchanged = same_value(self.saved_catalog()['assignments'].get(id_), row)
                unchanged = unchanged and all(same_value(self.saved_catalog()[table].get(row[key]),
                                                          catalog[table][row[key]])
                                              for key, table in (('command', 'commands'), ('event', 'events')))
                if unchanged and before.get(id_) == (status, reason):
                    continue
                raise ProfileError(f'Cannot register {id_}: {reason}')
        for id_, row in catalog['suppressions'].items():
            if ids is not None and id_ not in ids:
                continue
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
    def update_registration(self, candidate, previous, *, plans=None, verify=False):
        """Rebuild affected contexts in source order; leave other items intact."""
        old_plan, new_plan = plans if plans is not None else (self.plan(previous), self.plan(candidate))
        old_sections, old_groups = old_plan
        new_sections, new_groups = new_plan
        owners = {owner for owner in old_groups.keys() | new_groups.keys()
                  if old_groups.get(owner) != new_groups.get(owner)}

        def scope_key(scope):
            return scope.name, scope.space_type, scope.region_type, scope.is_modal

        # Recreating just one item could change precedence in a shared shortcut
        # chain. Include its whole context and any feature spanning that context.
        scopes = set()
        groups = list(old_groups.items()) + list(new_groups.items())
        while True:
            for owner, requests in groups:
                if owner in owners:
                    scopes.update(scope_key(request.scope) for request in requests)
            expanded = owners | {owner for owner, requests in groups
                                 if any(scope_key(request.scope) in scopes for request in requests)}
            if expanded == owners:
                break
            owners = expanded

        def rules(catalog, sections):
            return {id_: row for id_, row in catalog['suppressions'].items()
                    if sections[row['section']] and row.get('enabled', True)}
        old_rules, new_rules = rules(previous, old_sections), rules(candidate, new_sections)
        rule_ids = {id_ for id_ in old_rules.keys() | new_rules.keys()
                    if not same_value(old_rules.get(id_), new_rules.get(id_))}
        for id_, row in list(old_rules.items()) + list(new_rules.items()):
            # Independent disables own the inherited source's active flag;
            # rebuilding our additions does not change that source. Overrides
            # create ordered items and must still follow the context rebuild.
            if not row.get('disable') and scope_key(selector_descriptor(row['selector']).scope) in scopes:
                rule_ids.add(id_)
            if 'replacement' in row and not same_value(previous['commands'].get(row['replacement']),
                                                       candidate['commands'].get(row['replacement'])):
                rule_ids.add(id_)
        changed_assignments = {profile_assignment_id(request.request_id) for owner, requests in groups
                               if owner in owners for request in requests}
        ids = changed_assignments | rule_ids
        before = self.registration_results(ids) if verify else None
        for id_ in rule_ids:
            default_bindings.release(id_)
            runtime.release_features(('profile:deluxe-' + id_,))
        if any(owner in owners and any(request.target == ADD_PIE_TARGET for request in requests)
               for owner, requests in groups):
            if not self.restore_stock_add():
                raise ProfileError('Stock Add bindings still await restoration')
        runtime.release_features(owners)
        if self.stock_cleanup_pending or default_bindings.pending_cleanup() or runtime.blocking_cleanup():
            raise ProfileError('Native keymap cleanup is pending')
        self.register(candidate, owners=owners, rule_ids=rule_ids, plan=new_plan)
        if verify:
            self.check_registration(candidate, before, ids=ids,
                                    plan=(new_sections, {k:v for k,v in new_groups.items() if k in owners}))
        return changed_assignments, rule_ids

    @runtime.batch_merged_updates()
    def register(self, catalog=None, *, required_only=False, owners=None, rule_ids=None, plan=None):
        """Register in source order through brief 02's feature ledger."""
        if catalog is None:
            catalog = self.catalog()
        sections, groups = self.plan(catalog, required_only=required_only) if plan is None else plan
        total = 0
        add_pie_registered = False
        for owner, requests in groups.items():
            if owners is not None and owner not in owners:
                continue
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
            if rule_ids is not None and id_ not in rule_ids:
                continue
            if not (sections[row['section']] and row.get('enabled', True)):
                continue
            if row.get('disable'):
                default_bindings.install(id_, selector_descriptor(row['selector']),
                                         explicit_properties=row.get('explicit_properties', False))
                continue
            request = self.resolver.suppression_request(id_, row, catalog['commands'])
            if request is not None:
                handle = runtime.register_feature('profile:deluxe-' + id_, overrides=(request,))
                total += len(handle.owned_pairs)
        if add_pie_registered:
            self._defer_stock_add()
        return total
