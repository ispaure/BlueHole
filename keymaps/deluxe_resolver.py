"""Resolve profile data through known operators and the existing selector matcher."""

from collections import defaultdict
from dataclasses import asdict, replace
import json

import bpy

from . import keymap_utils as runtime
from .deluxe_schema import (ProfileError, SOURCE_ROLES, event_descriptor, require, same_value,
                            scope_descriptor, selector_descriptor)

# A replacement may use only an already proved context and capability. Generic
# per-item suppression remains a stored choice with an unsupported diagnostic.
PROOFS = {
    ('default', 'Object Mode', 'object.select_all', 'A'):
        ('ordinary_tail', 'stock_object_mode_select_all'),
    ('addon', '3D View Generic', 'machin3.toggle_smooth', 'TAB'):
        ('ordinary_tail', 'machin3tools_object_toggle_smooth'),
    ('default', 'Transform Modal Map', 'PRECISION', 'LEFT_SHIFT'):
        ('modal_head', 'transform_translate_precision_cancel'),
}
MODAL_TOKENS = frozenset({'CANCEL'})
# The stock Select All proof uses a consuming, known selection command.
REPLACEMENT_COMMANDS = ({'operator': 'object.select_all', 'properties': {'action': 'DESELECT'}},)
ROUTING_OPERATORS = {
    'wm.call_menu', 'wm.call_menu_pie', 'wm.call_panel', 'wm.context_menu_enum',
    'wm.context_toggle', 'wm.radial_control', 'wm.tool_set_by_id',
}
COMMAND_ERRORS = (AttributeError, KeyError, ReferenceError, RuntimeError, TypeError, ValueError)


def _enum(prop):
    return tuple(item.identifier for item in prop.enum_items if item.identifier)


def _rna_enums(class_name, names):
    cls = getattr(getattr(bpy, 'types', None), class_name, None)
    if cls is None:
        return {}
    return {name: _enum(cls.bl_rna.properties[name]) for name in names}


def _operator_rna(idname):
    namespace, name = idname.split('.')
    try:
        return getattr(getattr(bpy.ops, namespace), name).get_rna_type()
    except COMMAND_ERRORS:
        return None


def _field(prop):
    kind = prop.type
    if kind not in {'BOOLEAN', 'INT', 'FLOAT', 'ENUM', 'STRING'}:
        return {'type': kind, 'editable': False}
    array = getattr(prop, 'is_array', False)
    flags = kind == 'ENUM' and prop.is_enum_flag
    if array:
        shape = tuple(n for n in prop.array_dimensions if n)
        value = list(prop.default_array)
        if len(shape) == 2:
            # Matrix RNA stores columns. Profiles use logical rows.
            value = [value[row::shape[0]] for row in range(shape[0])]
    else:
        shape = ()
        value = sorted(prop.default_flag) if flags else prop.default
    return {
        'label': prop.name, 'type': kind, 'editable': not prop.is_readonly,
        'default': value, 'values': _enum(prop) if kind == 'ENUM' else (),
        'flags': flags, 'shape': shape,
        'minimum': getattr(prop, 'hard_min', None), 'maximum': getattr(prop, 'hard_max', None),
        'max_length': getattr(prop, 'length_max', 0) if kind == 'STRING' else 0,
    }


def _valid_field(field, value):
    kind = field['type']
    if field['flags']:
        return (isinstance(value, list) and all(isinstance(item, str) for item in value)
                and value == sorted(set(value)) and all(item in field['values'] for item in value))
    scalar = {'BOOLEAN': bool, 'INT': int, 'FLOAT': float, 'ENUM': str, 'STRING': str}[kind]

    def check(part, shape):
        if shape:
            return (isinstance(part, list) and len(part) == shape[0]
                    and all(check(item, shape[1:]) for item in part))
        if type(part) is not scalar:
            return False
        if kind == 'ENUM':
            return part in field['values']
        if kind in ('FLOAT', 'INT'):
            return field['minimum'] <= part <= field['maximum']
        if kind == 'STRING' and field['max_length']:
            return len(part) <= field['max_length']
        return True

    return check(value, field['shape'])


def _switch(preferences, path):
    if not path:
        return True
    value = preferences
    for part in path.split('.'):
        value = getattr(value, part)
    return bool(value)


def _selector_key(selector):
    target = selector.target
    return (selector.source_role, selector.scope.name, target.idname or target.modal_value,
            selector.event.type)


def _proof(selector):
    key = _selector_key(selector)
    if key[0] == 'active':
        key = ('default', *key[1:])
    return PROOFS.get(key)


def selector_data(selector):
    result = {'scope': asdict(selector.scope), 'event': asdict(selector.event),
              'source_role': selector.source_role}
    target = selector.target
    if target.modal_value:
        result['target'] = {'modal_value': target.modal_value}
    else:
        result['target'] = {'idname': target.idname,
                            'properties': json.loads(json.dumps(dict(target.properties)))}
    for key in ('ledger_id', 'sample_id'):
        if value := getattr(selector, key):
            result[key] = value
    return result


def selector_status(selector, replacement=None):
    if selector.source_role == 'user':
        _, issue = _inherited_source(selector)
        return ('ambiguous', issue) if issue else ('unsupported', 'unproved_user_source')
    try:
        runtime._exact_source(selector)
        runtime._preflight_merged_source(selector)
    except runtime._Pending as issue:
        if issue.reason.startswith('ambiguous'):
            state = 'ambiguous'
        elif issue.reason in {'source_missing_or_edited', 'merged_source_missing_or_edited',
                              'merged_source_inactive', 'missing_scope', 'keyconfig_unavailable'}:
            state = 'missing'
        else:
            state = 'unsupported'
        return state, issue.reason
    proof = _proof(selector)
    if replacement is None:
        return 'unsupported', 'replacement_required' if proof else 'unsupported_capability'
    if not proof:
        return 'unsupported', 'unsupported_capability'
    try:
        runtime._preflight_override(runtime.KeymapOverride('preview', selector, replacement, *proof))
    except runtime._Pending as issue:
        return ('missing' if issue.status == 'pending' else 'unsupported'), issue.reason
    return 'resolved', ''


def _inherited_source(selector):
    matches = []
    for role in ('default', 'addon'):
        candidate = replace(selector, source_role=role)
        try:
            runtime._exact_source(candidate)
            matches.append(candidate)
        except runtime._Pending as issue:
            if issue.reason.startswith('ambiguous'):
                return selector, issue.reason
    if len(matches) > 1:
        return selector, 'ambiguous_source'
    return (matches[0] if matches else selector), ''


def capture_candidate(map_, item, source_role):
    """Capture an actual selected row, with source membership checked immediately."""
    require(source_role in SOURCE_ROLES, 'Invalid keyconfig source')
    try:
        config = runtime._config(source_role)
        if not runtime._contains(config.keymaps, map_):
            raise ProfileError('Selected map does not belong to that keyconfig')
        selector = runtime.capture_selector(map_, item, source_role=source_role)
    except runtime._Pending as issue:
        raise ProfileError(issue.reason) from issue
    if source_role == 'user':
        # The merged map is not a source. Reuse the matcher to link to one
        # exact inherited source. User-only rows can still be staged explicitly.
        selector, issue = _inherited_source(selector)
        if issue:
            return {'selector': selector_data(selector), 'active': bool(item.active),
                    'status': 'ambiguous', 'reason': issue, 'can_replace': False}
    status, reason = selector_status(selector)
    return {'selector': selector_data(selector), 'active': bool(item.active),
            'status': status, 'reason': reason, 'can_replace': _proof(selector) is not None}


def binding_candidates(source_role, map_):
    """Enumerate readable candidates in a supplied live map for the editor."""
    candidates = []
    for item in map_.keymap_items:
        try:
            candidates.append(capture_candidate(map_, item, source_role))
        except ProfileError:
            continue
    return tuple(candidates)


def input_options():
    """Return the current Blender event and map enum identifiers."""
    return {
        'event': _rna_enums('KeyMapItem', ('type', 'value', 'direction', 'key_modifier', 'map_type')),
        'scope': _rna_enums('KeyMap', ('space_type', 'region_type')),
    }


class Resolver:
    """Shipped command routes and scopes are the allowlist for profile edits."""

    def __init__(self, defaults):
        self.commands = defaultdict(list)
        for command in (*defaults['commands'].values(), *REPLACEMENT_COMMANDS):
            if 'operator' in command:
                self.commands[command['operator']].append(command)
        self.feature_categories = {row['feature']: defaults['sections'][row['section']]['category']
                                   for row in defaults['assignments'].values()}
        self.scopes = {scope_descriptor(row['scope']) for row in defaults['assignments'].values()}

    def describe_command(self, command):
        if 'modal_value' in command:
            return {'label': command['modal_value'], 'owner': 'Blender', 'dependency': None,
                    'availability': 'available', 'editable': False, 'fields': {}}
        idname = command['operator']
        variants = self.commands.get(idname, ())
        provider = variants[0].get('provider') if variants else None
        rna = _operator_rna(idname)
        locked = idname in ROUTING_OPERATORS or provider is not None or '.bh_' in idname
        editable = rna is not None and not locked
        fields = {}
        if rna is not None:
            for name, value in command['properties'].items():
                prop = rna.properties.get(name)
                field = _field(prop) if prop is not None else {'editable': False, 'type': 'UNKNOWN'}
                field['editable'] = editable and field['editable'] and _valid_field(field, value)
                fields[name] = field
        if rna is None:
            fields = {name: {'editable': False, 'type': 'UNAVAILABLE'} for name in command['properties']}
        label = (rna.name if rna is not None else idname) or idname
        if idname in {'wm.call_menu', 'wm.call_menu_pie', 'wm.call_panel'}:
            name = command['properties']['name']
            label = getattr(getattr(bpy.types, name, None), 'bl_label', None) or name
        return {'label': label, 'owner': provider or ('Blue Hole' if '.bh_' in idname else 'Blender'),
                'dependency': provider, 'availability': ('available' if rna is not None
                                                           else 'waiting_for_provider' if provider
                                                           else 'unavailable'),
                'editable': any(field['editable'] for field in fields.values()), 'fields': fields}

    def validate(self, catalog, baseline):
        """Check editable values against the live RNA and the approved routes."""
        options = input_options()
        for id_, row in catalog['events'].items():
            if same_value(baseline.get('events', {}).get(id_), row):
                continue
            event = event_descriptor(row)
            for key, values in options['event'].items():
                require(getattr(event, key) in values, f'Unknown event {key} in {id_}')
        for id_, row in catalog['commands'].items():
            self.validate_command(row, id_)
        for id_, row in catalog['assignments'].items():
            if same_value(baseline.get('assignments', {}).get(id_), row):
                continue
            scope = scope_descriptor(row['scope'])
            for key, values in options['scope'].items():
                require(getattr(scope, key) in values, f'Unknown scope {key} in {id_}')
            if not same_value(baseline.get('assignments', {}).get(id_, {}).get('scope'), row['scope']):
                require(scope in self.scopes or self._live_scope(scope), f'Unknown keymap scope in {id_}')

    @staticmethod
    def _live_scope(scope):
        for role in ('default', 'addon'):
            try:
                if runtime._maps(runtime._config(role), scope):
                    return True
            except runtime._Pending:
                pass
        return False

    def validate_command(self, row, id_):
        if 'modal_value' in row:
            require(row['modal_value'] in MODAL_TOKENS, f'Unknown modal command {id_}')
            return
        idname = row['operator']
        variants = self.commands.get(idname)
        require(variants and row.get('provider') == variants[0].get('provider'),
                f'Unknown command or provider in {id_}')
        if any(same_value(row, variant) for variant in variants):
            return
        require(idname not in ROUTING_OPERATORS and '.bh_' not in idname and not row.get('provider'),
                f'Command {id_} is code-managed')
        allowed_fields = {key for variant in variants for key in variant['properties']}
        for name, value in row['properties'].items():
            require(name in allowed_fields, f'Unknown editable field {name} in {id_}')
            if any(name in variant['properties'] and same_value(value, variant['properties'][name])
                   for variant in variants):
                continue
            rna = _operator_rna(idname)
            prop = rna.properties.get(name) if rna is not None else None
            field = _field(prop) if prop is not None else {'editable': False}
            require(field['editable'] and _valid_field(field, value), f'Invalid {name} value in {id_}')

    def plan(self, catalog, preferences):
        enabled = bool(preferences.keymap.enable_keymaps)
        sections = catalog['sections']
        categories = catalog['categories']
        state = {}
        for id_, section in sections.items():
            category = categories[section['category']]
            state[id_] = section.get('required', False) or (
                enabled and category.get('enabled', True) and section.get('enabled', True)
                and _switch(preferences, category.get('switch'))
                and _switch(preferences, section.get('switch')))
        groups = {}
        commands = catalog['commands']
        for id_, row in sorted(catalog['assignments'].items(), key=lambda entry: entry[1]['order']):
            if not (state[row['section']] and row.get('enabled', True)):
                continue
            category = self.feature_categories.get(row['feature'], sections[row['section']]['category'])
            owner = 'legacy:' + self._category_label(category) + ':deluxe-' + row['feature']
            scope = scope_descriptor(row['scope'])
            event = event_descriptor(catalog['events'][row['event']])
            command = commands[row['command']]
            samples = row.get('samples', ())
            request = runtime.KeymapAssignment(
                id_, scope, event, self.target(command), declared_properties_only=True,
                active=row.get('active', True), ledger_id=catalog['base']['ledger'] if samples else '',
                sample_id=samples[0] if samples else '')
            groups.setdefault(owner, []).append(request)
        return state, groups

    @staticmethod
    def _category_label(category):
        return 'UV' if category == 'uv' else category.capitalize()

    @staticmethod
    def target(row):
        if 'modal_value' in row:
            return runtime.KeymapTarget(modal_value=row['modal_value'])
        return runtime.KeymapTarget(row['operator'], row['properties'])

    def suppression_request(self, id_, row, commands):
        selector = selector_descriptor(row['selector'])
        replacement = self.target(commands[row['replacement']]) if 'replacement' in row else None
        proof = _proof(selector)
        if replacement is None or proof is None:
            return None
        return runtime.KeymapOverride(id_, selector, replacement, *proof,
                                      ledger_id=selector.ledger_id, sample_id=selector.sample_id)
