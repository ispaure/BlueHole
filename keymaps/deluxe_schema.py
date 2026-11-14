"""Versioned data and merge rules for Deluxe keymap profiles."""

from collections import Counter
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import fields
import math
import re

from .keymap_utils import KeymapEvent, KeymapScope, KeymapSelector, KeymapTarget

SCHEMA_VERSION = 1
TABLES = ('categories', 'sections', 'events', 'commands', 'assignments', 'suppressions')
ID = re.compile(r'[a-z0-9][a-z0-9_.-]{0,95}\Z')
TOKEN = re.compile(r'[A-Z][A-Z0-9_]*\Z')
PROPERTY = re.compile(r'[a-zA-Z][a-zA-Z0-9_]*\Z')
OPERATOR = re.compile(r'[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\Z')
EVENT_FIELDS = {field.name for field in fields(KeymapEvent)}
SCOPE_FIELDS = {field.name for field in fields(KeymapScope)}
MODIFIERS = ('shift', 'ctrl', 'alt', 'oskey', 'hyper')
SOURCE_ROLES = ('default', 'active', 'addon', 'user')


class ProfileError(ValueError):
    """The profile or edit could not be applied."""


def require(condition, message):
    if not condition:
        raise ProfileError(message)


def record(value, required, optional=()):
    require(isinstance(value, dict), 'Expected an object')
    missing = set(required) - value.keys()
    unknown = value.keys() - set(required) - set(optional)
    require(not missing, 'Missing fields: ' + ', '.join(sorted(missing)))
    require(not unknown, 'Unknown fields: ' + ', '.join(sorted(unknown)))
    return value


def identifier(value):
    return isinstance(value, str) and ID.fullmatch(value) is not None


def text(value):
    return isinstance(value, str) and 0 < len(value) <= 256 and not any(ord(c) < 32 for c in value)


def token(value):
    return text(value) and TOKEN.fullmatch(value) is not None


def toggle(row, key, default=True):
    value = row.get(key, default)
    require(type(value) is bool, f'{key} must be a boolean')
    return value


def property_value(value, depth=0):
    if type(value) in (bool, int, str):
        return not isinstance(value, str) or len(value) <= 4096 and '\0' not in value
    if type(value) is float:
        return math.isfinite(value)
    return (depth < 2 and isinstance(value, list) and len(value) <= 64
            and all(property_value(part, depth + 1) for part in value))


def properties(value):
    require(isinstance(value, dict) and all(
        isinstance(name, str) and PROPERTY.fullmatch(name) and property_value(part)
        for name, part in value.items()), 'Invalid typed operator properties')
    return value


def event_descriptor(row):
    event = KeymapEvent(**record(row, ('type',), EVENT_FIELDS - {'type'}))
    require(all(token(getattr(event, key)) for key in
                ('type', 'value', 'key_modifier', 'direction', 'map_type')), 'Invalid event token')
    for key in ('any', 'repeat'):
        toggle(row, key, False)
    for key in MODIFIERS:
        value = getattr(event, key)
        require((type(value) in (bool, int) and value in (-1, 0, 1))
                or (key == 'hyper' and value is None), f'Invalid {key} modifier')
    return event


def scope_descriptor(row):
    scope = KeymapScope(**record(row, ('name',), SCOPE_FIELDS - {'name'}))
    require(text(scope.name) and token(scope.space_type) and token(scope.region_type),
            'Invalid keymap scope')
    toggle(row, 'is_modal', False)
    require(scope.is_tool is None or type(scope.is_tool) is bool, 'Invalid tool scope')
    return scope


def selector_descriptor(row):
    record(row, ('scope', 'event', 'source_role', 'target'), ('ledger_id', 'sample_id'))
    scope = scope_descriptor(row['scope'])
    event = event_descriptor(row['event'])
    target = record(row['target'], ('modal_value',) if scope.is_modal else ('idname', 'properties'))
    if scope.is_modal:
        require(token(target['modal_value']), 'Invalid modal value')
    else:
        require(isinstance(target['idname'], str) and OPERATOR.fullmatch(target['idname']),
                'Invalid selector operator')
        properties(target['properties'])
    require(row['source_role'] in SOURCE_ROLES, 'Invalid selector source role')
    require(all(identifier(row[key]) for key in ('ledger_id', 'sample_id') if key in row),
            'Invalid selector provenance')
    return KeymapSelector(scope, event, KeymapTarget(**target), row['source_role'],
                          row.get('ledger_id', ''), row.get('sample_id', ''))


@contextmanager
def row_location(table, id_):
    try:
        yield
    except ProfileError as error:
        issue = ProfileError(f'{table}[{id_!r}]: {error}')
        issue.location = (table, id_)
        raise issue from error


def validate_catalog(catalog):
    record(catalog, ('schema_version', 'catalog_version', 'base', *TABLES))
    require(type(catalog['schema_version']) is int and catalog['schema_version'] == SCHEMA_VERSION,
            'Unsupported profile schema version')
    require(type(catalog['catalog_version']) is int and catalog['catalog_version'] > 0,
            'Invalid catalog version')
    base = record(catalog['base'], ('preset', 'reference_version', 'ledger'))
    require(base['preset'] == 'Blender' and text(base['reference_version'])
            and identifier(base['ledger']), 'Unsupported Blender base')
    for table in TABLES:
        require(isinstance(catalog[table], dict) and all(identifier(key) for key in catalog[table]),
                f'Invalid IDs in {table}')
    for table in ('categories', 'sections'):
        required = ('label', 'category') if table == 'sections' else ('label',)
        for id_, row in catalog[table].items():
            with row_location(table, id_):
                record(row, required, ('enabled', 'order', 'switch', 'required'))
                require(text(row['label']), 'Invalid category or section label')
                toggle(row, 'enabled')
                toggle(row, 'required', False)
                if 'order' in row:
                    require(type(row['order']) is int and row['order'] >= 0, 'Invalid group order')
                if row.get('switch') is not None:
                    require(identifier(row['switch']), 'Invalid preference switch')
                if table == 'sections':
                    require(identifier(row['category']) and row['category'] in catalog['categories'],
                            'Missing section category')
    for id_, row in catalog['events'].items():
        with row_location('events', id_):
            event_descriptor(row)
    for id_, row in catalog['commands'].items():
        with row_location('commands', id_):
            if isinstance(row, dict) and 'modal_value' in row:
                record(row, ('modal_value',))
                require(token(row['modal_value']), 'Invalid modal command')
            else:
                record(row, ('operator', 'properties'), ('provider', 'label'))
                require(isinstance(row['operator'], str) and OPERATOR.fullmatch(row['operator']),
                        'Invalid operator ID')
                properties(row['properties'])
                require('provider' not in row or text(row['provider']), 'Invalid command provider')
                require('label' not in row or text(row['label']), 'Invalid command label')
    orders = set()
    features = Counter()
    last = None
    assignments = catalog['assignments']
    for id_, row in assignments.items():
        with row_location('assignments', id_):
            record(row, ('section', 'feature', 'event', 'command', 'scope', 'order'),
                   ('active', 'enabled', 'samples', 'kind'))
            for key, table in (('section', 'sections'), ('event', 'events'), ('command', 'commands')):
                require(identifier(row[key]) and row[key] in catalog[table], f'Missing {key} reference')
            require(identifier(row['feature']), 'Invalid feature owner')
            scope = scope_descriptor(row['scope'])
            require(not scope.is_modal and scope.is_tool in (None, False)
                    and 'operator' in catalog['commands'][row['command']], 'Unsupported assignment scope or command')
            toggle(row, 'enabled')
            toggle(row, 'active')
            require(row.get('kind', 'addition') in ('addition', 'precedence'), 'Invalid assignment kind')
            order = row['order']
            require(type(order) is int and order >= 0 and order not in orders, 'Invalid or duplicate assignment order')
            orders.add(order)
            require('samples' not in row or isinstance(row['samples'], list)
                    and all(identifier(sample) for sample in row['samples']), 'Invalid assignment provenance')
    for row in sorted(assignments.values(), key=lambda row: row['order']):
        feature = row['feature']
        require(feature == last or feature not in features, 'Feature assignments must be consecutive')
        features[feature] += 1
        last = feature
    require(max(features.values(), default=0) <= 16, 'Feature exceeds runtime request budget')
    for id_, row in catalog['suppressions'].items():
        with row_location('suppressions', id_):
            record(row, ('section', 'selector'), ('enabled', 'replacement', 'disable'))
            require(identifier(row['section']) and row['section'] in catalog['sections'],
                    'Missing suppression section')
            selector_descriptor(row['selector'])
            toggle(row, 'enabled')
            toggle(row, 'disable', False)
            require(not (row.get('disable') and 'replacement' in row), 'Choose disable or replacement')
            if 'replacement' in row:
                require(identifier(row['replacement']) and row['replacement'] in catalog['commands'],
                        'Missing replacement command')
    require(not assignments.keys() & catalog['suppressions'].keys(), 'Duplicate runtime request ID')


def merge_profile(defaults, overlay):
    record(overlay, ('schema_version', 'catalog_version', 'base', 'changes'))
    require(type(overlay['schema_version']) is int and overlay['schema_version'] == SCHEMA_VERSION,
            'Unsupported profile schema version')
    require(type(overlay['catalog_version']) is int
            and 0 < overlay['catalog_version'] <= defaults['catalog_version'], 'Unsupported catalog version')
    require(overlay['base'] == defaults['base']['preset'], 'Incompatible Blender base')
    changes = record(overlay['changes'], (), TABLES)
    result = deepcopy(defaults)
    for table, rows in changes.items():
        require(isinstance(rows, dict) and all(identifier(key) for key in rows), f'Invalid edits in {table}')
        for key, patch in rows.items():
            default = defaults[table].get(key)
            if patch is None:
                require(default is not None, f'Unknown removed {table} ID {key}')
                del result[table][key]
            else:
                require(isinstance(patch, dict), f'Invalid edit for {key}')
                result[table][key] = {**(default or {}), **deepcopy(patch)}
    validate_catalog(result)
    return result


def same_value(left, right):
    """JSON equality that distinguishes Boolean, integer and float choices."""
    if type(left) is not type(right):
        return False
    if isinstance(left, list):
        return len(left) == len(right) and all(map(same_value, left, right))
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(same_value(left[k], right[k]) for k in left)
    return left == right


def profile_overlay(defaults, catalog):
    changes = {}
    for table in TABLES:
        shipped, edited = defaults[table], catalog[table]
        patches = {key: None for key in shipped.keys() - edited.keys()}
        for key, row in edited.items():
            default = shipped.get(key, {})
            require(default.keys() <= row.keys(), f'Cannot remove fields from shipped entry {key}')
            patch = {name: value for name, value in row.items()
                     if name not in default or not same_value(value, default[name])}
            if patch:
                patches[key] = patch
        if patches:
            changes[table] = patches
    return {'schema_version': SCHEMA_VERSION, 'catalog_version': defaults['catalog_version'],
            'base': defaults['base']['preset'], 'changes': changes}
