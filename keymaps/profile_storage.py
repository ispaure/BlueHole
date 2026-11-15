"""Versioned personal overlays and deterministic three-way catalog updates.

The baseline makes edits meaningful after shipped defaults change. Personal
values win overlapping edits; required bindings and code-owned metadata follow
the new release. Conflicts are returned to the UI, never silently discarded.
"""
from copy import deepcopy
from dataclasses import dataclass

from .deluxe_schema import (TABLES, ProfileError, assignment_required, independent_commands,
                            merge_profile, record, require, same_value, validate_catalog)

PROFILE_VERSION = 2
MISSING = object()
MANAGED = ('feature', 'samples', 'kind', 'dispatch_group', 'required')


@dataclass(frozen=True)
class ProfileRead:
    catalog: dict
    conflicts: tuple[str, ...] = ()
    migrated: bool = False


def encode_profile(defaults, catalog):
    changes, deleted = {}, {}
    for table in TABLES:
        shipped, edited = defaults[table], catalog[table]
        patches = {key: None for key in shipped.keys() - edited.keys()}
        removals = {}
        for id_, row in edited.items():
            original = shipped.get(id_, {})
            patch = {key: deepcopy(value) for key, value in row.items()
                     if key not in original or not same_value(value, original[key])}
            if patch or id_ not in shipped:
                patches[id_] = patch
            if fields := sorted(original.keys() - row.keys()):
                removals[id_] = fields
        if patches:
            changes[table] = patches
        if removals:
            deleted[table] = removals
    return {'profile_version': PROFILE_VERSION, 'schema_version': 1,
            'catalog_version': defaults['catalog_version'], 'base': 'Blender',
            'baseline': deepcopy(defaults), 'changes': changes, 'deleted_fields': deleted}


def _apply_document(document):
    baseline = document['baseline']
    validate_catalog(baseline)
    result = deepcopy(baseline)
    for table, rows in document['changes'].items():
        require(table in TABLES and isinstance(rows, dict), 'Invalid personal profile changes')
        for id_, patch in rows.items():
            if patch is None:
                result[table].pop(id_, None)
            else:
                require(isinstance(patch, dict), 'Invalid personal profile row')
                result[table][id_] = {**result[table].get(id_, {}), **deepcopy(patch)}
    for table, rows in document.get('deleted_fields', {}).items():
        require(table in TABLES and isinstance(rows, dict), 'Invalid deleted profile fields')
        for id_, fields in rows.items():
            require(isinstance(fields, list) and all(isinstance(field, str) for field in fields), 'Invalid deleted fields')
            require(id_ in result[table], 'Deleted fields reference a missing profile entry')
            for field in fields:
                result[table][id_].pop(field, None)
    validate_catalog(result)
    return result


def _merge(old, personal, shipped, path, conflicts):
    if same_value(personal, old):
        return shipped
    if same_value(shipped, old) or same_value(personal, shipped):
        return personal
    if all(isinstance(value, dict) for value in (old, personal, shipped)):
        # A retargeted command owns its complete property schema.
        if 'operator' in old and (personal.get('operator') != old['operator'] or
                shipped.get('operator') != old['operator'] and
                not same_value(personal.get('properties'), old.get('properties'))):
            if shipped.get('operator') != old['operator']:
                conflicts.append(path + ': command changed on both sides; personal command retained')
            return personal
        result = {}
        for key in sorted(old.keys() | personal.keys() | shipped.keys()):
            value = _merge(old.get(key, MISSING), personal.get(key, MISSING),
                           shipped.get(key, MISSING), path + '.' + key, conflicts)
            if value is not MISSING:
                result[key] = value
        return result
    conflicts.append(path + ': changed on both sides; personal choice retained')
    return personal


def _restore_references(result, personal, defaults, previous, conflicts):
    def ensure(table, id_):
        if id_ in result[table]:
            return
        source = next((catalog[table][id_] for catalog in (personal, defaults, previous)
                       if id_ in catalog[table]), None)
        require(source is not None, f'Missing migrated {table} reference {id_}')
        result[table][id_] = deepcopy(source)
        if table in ('categories', 'sections') and id_ not in personal[table] and not source.get('required'):
            result[table][id_]['enabled'] = False
        conflicts.append(f'{table}.{id_}: retained because a binding still uses it')
    for row in result['assignments'].values():
        for field, table in (('command', 'commands'), ('event', 'events'), ('section', 'sections')):
            ensure(table, row[field])
    for row in result['suppressions'].values():
        ensure('sections', row['section'])
        if 'replacement' in row:
            ensure('commands', row['replacement'])
    for row in result['sections'].values():
        ensure('categories', row['category'])


def decode_profile(defaults, document):
    require(isinstance(document, dict), 'Expected a personal profile object')
    if 'profile_version' not in document:
        return ProfileRead(independent_commands(merge_profile(defaults, document)), migrated=True)
    require(type(document['profile_version']) is int and document['profile_version'] == PROFILE_VERSION,
            'Unsupported personal profile version')
    record(document, ('profile_version', 'schema_version', 'catalog_version', 'base',
                      'baseline', 'changes'), ('deleted_fields',))
    require(document.get('base') == 'Blender' and document.get('schema_version') == 1,
            'Incompatible personal profile base')
    personal = independent_commands(_apply_document(document))
    previous = independent_commands(document['baseline'])
    if same_value(previous, defaults):
        return ProfileRead(personal)
    conflicts = []
    result = {key: deepcopy(defaults[key]) for key in ('schema_version', 'catalog_version', 'base')}
    for table in TABLES:
        result[table] = deepcopy(_merge(previous[table], personal[table], defaults[table], table, conflicts))
    for id_, old in previous['assignments'].items():
        if id_ in defaults['assignments'] or id_ not in personal['assignments']:
            continue
        row = personal['assignments'][id_]
        edited = not same_value(row, old) or any(not same_value(
            personal[table].get(row[field]), previous[table].get(old[field]))
            for field, table in (('command', 'commands'), ('event', 'events')))
        if edited:
            result['assignments'][id_] = deepcopy(row)
            conflicts.append(f'assignments.{id_}: retired upstream; personal binding retained')
    # Required bindings and registration provenance belong to the new release.
    for table in ('categories', 'sections'):
        for id_, row in defaults[table].items():
            if row.get('required'):
                result[table][id_] = deepcopy(row)
    for id_, row in defaults['assignments'].items():
        if assignment_required(defaults, row):
            if not same_value(result['assignments'].get(id_), row):
                conflicts.append(f'assignments.{id_}: required binding follows the new release')
            result['assignments'][id_] = deepcopy(row)
            for field, table in (('command', 'commands'), ('event', 'events')):
                result[table][row[field]] = deepcopy(defaults[table][row[field]])
    _restore_references(result, personal, defaults, previous, conflicts)
    next_order = max(1_000_000, max((r['order'] for r in defaults['assignments'].values()), default=0) + 1)
    used_orders = set()
    for id_, row in sorted(result['assignments'].items(), key=lambda item: (item[0] not in defaults['assignments'], item[1]['order'])):
        source = defaults['assignments'].get(id_)
        for key in MANAGED:
            if source is not None and key in source:
                row[key] = deepcopy(source[key])
            else:
                row.pop(key, None)
        row.setdefault('feature', id_)
        if source is None or row['order'] in used_orders:
            row['order'] = next_order
            next_order += 1
        used_orders.add(row['order'])
    result = independent_commands(result)
    validate_catalog(result)
    return ProfileRead(result, tuple(conflicts), migrated=True)
