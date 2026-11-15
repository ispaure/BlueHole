"""Resolve profile data through known operators and the existing selector matcher."""

from collections import defaultdict
from dataclasses import asdict, replace
import json

import bpy

from . import keymap_utils as runtime
from . import default_bindings
from .catalog_plan import CatalogPlanner, profile_assignment_id
from .provider_policy import command_addon
from .deluxe_schema import (OPERATOR, ProfileError, SOURCE_ROLES, event_descriptor, properties, require, same_value,
                            scope_descriptor, selector_descriptor)

# A replacement may use only an already proved context and capability. Generic
# review-only selectors remain inert; explicit default disables use default_bindings.
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
COMMAND_ERRORS = (AttributeError, KeyError, ReferenceError, RuntimeError, TypeError, ValueError)


def _enum(prop):
    return tuple(item.identifier for item in prop.enum_items if item.identifier)


def _rna_enums(class_name, names):
    cls = getattr(getattr(bpy, 'types', None), class_name, None)
    if cls is None:
        return {}
    return {name: _enum(cls.bl_rna.properties[name]) for name in names}


def _operator_rna(idname):
    if not OPERATOR.fullmatch(idname):
        return None
    namespace, name = idname.split('.')
    try:
        return getattr(getattr(bpy.ops, namespace), name).get_rna_type()
    except COMMAND_ERRORS:
        return None


def _field(prop):
    kind = prop.type
    # SKIP_SAVE controls Blender's last-used operator values. Keymaps
    # supply their own explicit values on each invocation.
    if (kind not in {'BOOLEAN', 'INT', 'FLOAT', 'ENUM', 'STRING'}
            or getattr(prop, 'is_hidden', False)):
        return {'label': prop.name, 'type': kind, 'editable': False}
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
        'enum_items': (tuple((item.identifier, getattr(item, 'name', item.identifier),
                              getattr(item, 'description', ''))
                             for item in prop.enum_items if item.identifier)
                       if kind == 'ENUM' else ()),
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
        runtime.exact_source(selector)
        runtime.verify_merged_source(selector)
    except runtime.Pending as issue:
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
        runtime.verify_override(runtime.KeymapOverride('preview', selector, replacement, *proof))
    except runtime.Pending as issue:
        return ('missing' if issue.status == 'pending' else 'unsupported'), issue.reason
    return 'resolved', ''


def _inherited_source(selector):
    matches = []
    for role in ('default', 'addon'):
        candidate = replace(selector, source_role=role)
        try:
            runtime.exact_source(candidate)
            matches.append(candidate)
        except runtime.Pending as issue:
            if issue.reason.startswith('ambiguous'):
                return selector, issue.reason
    if len(matches) > 1:
        return selector, 'ambiguous_source'
    return (matches[0] if matches else selector), ''


def capture_candidate(map_, item, source_role):
    """Capture an actual selected row, with source membership checked immediately."""
    require(source_role in SOURCE_ROLES, 'Invalid keyconfig source')
    try:
        config = runtime.configuration(source_role)
        if not runtime.contains_native(config.keymaps, map_):
            raise ProfileError('Selected map does not belong to that keyconfig')
        selector = runtime.capture_selector(map_, item, source_role=source_role)
    except runtime.Pending as issue:
        raise ProfileError(issue.reason) from issue
    if source_role == 'user':
        managed = default_bindings.managed_rule(map_, item)
        if managed:
            selector = managed[1]
        # The merged map is not a source. Reuse the matcher to link to one
        # exact inherited source. User-only rows can still be staged explicitly.
        selector, issue = (selector, '') if managed else _inherited_source(selector)
        if issue:
            return {'selector': selector_data(selector), 'active': bool(item.active),
                    'status': 'ambiguous', 'reason': issue, 'can_replace': False, 'can_disable': False}
    status, reason = selector_status(selector)
    return {'selector': selector_data(selector), 'active': bool(item.active),
            'status': status, 'reason': reason, 'can_replace': _proof(selector) is not None,
            'can_disable': default_bindings.status(selector)[0] == 'resolved'}


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


class Resolver(CatalogPlanner):
    """Shipped command routes and scopes are the allowlist for profile edits."""

    def __init__(self, defaults):
        super().__init__(defaults)
        self.modal_commands = tuple(command for command in defaults['commands'].values()
                                    if 'modal_value' in command) + tuple(
                                        {'modal_value': token} for token in MODAL_TOKENS)
        self.commands = defaultdict(list)
        for command in (*defaults['commands'].values(), *REPLACEMENT_COMMANDS):
            if 'operator' in command:
                self.commands[command['operator']].append(command)
        self.scopes = {scope_descriptor(row['scope']) for row in defaults['assignments'].values()}

    def describe_command(self, command, *, include_unset=False):
        if 'modal_value' in command:
            return {'label': command['modal_value'], 'owner': 'Blender', 'dependency': None,
                    'availability': 'available', 'editable': False, 'fields': {}}
        idname = command['operator']
        variants = self.commands.get(idname, ())
        provider = command.get('provider') or (variants[0].get('provider') if variants else None)
        rna = _operator_rna(idname)
        editable = rna is not None
        fields = {}
        properties = command['properties']
        if rna is not None:
            names = {}
            if include_unset and editable:
                names.update(dict.fromkeys(name for name in rna.properties.keys() if name != 'rna_type'))
            names.update(dict.fromkeys(properties))
            for name in names:
                prop = rna.properties.get(name)
                if name not in properties and (prop is None or getattr(prop, 'is_hidden', False)):
                    continue
                field = _field(prop) if prop is not None else {'editable': False, 'type': 'UNKNOWN'}
                value = properties.get(name, field.get('default'))
                field['editable'] = editable and field['editable'] and _valid_field(field, value)
                field['explicit'] = name in properties
                fields[name] = field
        if rna is None:
            fields = {name: {'editable': False, 'type': 'UNAVAILABLE'} for name in command['properties']}
        label = (rna.name if rna is not None else idname) or 'Unassigned'
        owner = provider or ('Blue Hole' if '.bh_' in idname else 'Blender')
        if idname in {'wm.call_menu', 'wm.call_menu_pie', 'wm.call_panel'}:
            name = command['properties'].get('name', '')
            label = getattr(getattr(bpy.types, name, None), 'bl_label', None) or name or label
            if name.startswith('BLUEHOLE_'):
                owner = 'Blue Hole'
        available = rna is not None
        if idname in {'wm.call_menu', 'wm.call_menu_pie', 'wm.call_panel'}:
            available = available and hasattr(bpy.types, command['properties'].get('name', ''))
        addon = command_addon(command)
        if addon:
            available = available and runtime.provider_enabled(addon)
        return {'label': command.get('label', label), 'owner': owner,
                'dependency': provider, 'availability': ('available' if available
                                                           else 'waiting_for_provider' if provider
                                                           else 'unavailable'),
                'editable': any(field['editable'] for field in fields.values()), 'fields': fields}

    @staticmethod
    def describe_operator_token(idname):
        rna = _operator_rna(idname)
        return None if rna is None else (getattr(rna, 'as_pointer', lambda: id(rna))(), rna.name)

    def validate(self, catalog, baseline):
        """Check edited values against live RNA and supported keymap scopes."""
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
                if runtime.matching_maps(runtime.configuration(role), scope):
                    return True
            except runtime.Pending:
                pass
        return False

    def validate_command(self, row, id_):
        if 'modal_value' in row:
            require(any(row == known for known in getattr(self, 'modal_commands', ())), f'Unknown modal command {id_}')
            return
        idname = row['operator']
        require(isinstance(idname, str) and (not idname or OPERATOR.fullmatch(idname)),
                'Use an operator ID such as wm.call_menu_pie')
        properties(row['properties'])
        variants = self.commands.get(idname)
        variants = variants or ()
        # Provider labels are profile metadata, including retired/missing addons.
        # Native availability and capability checks govern actual registration.
        definition = {key: value for key, value in row.items() if key != 'label'}
        if any(same_value(definition, {key: value for key, value in variant.items() if key != 'label'})
               for variant in variants):
            return
        rna = _operator_rna(idname)
        # Missing add-ons are valid saved choices. RNA validation resumes when
        # their operators become available; no binding is registered meanwhile.
        if rna is None:
            return
        for name, value in row['properties'].items():
            if any(name in variant['properties'] and same_value(value, variant['properties'][name])
                   for variant in variants):
                continue
            prop = rna.properties.get(name) if rna is not None else None
            require(prop is not None and name != 'rna_type', f'Unknown editable field {name} in {id_}')
            field = _field(prop) if prop is not None else {'editable': False}
            require(field['editable'] and _valid_field(field, value), f'Invalid {name} value in {id_}')

    def plan(self, catalog, preferences, *, required_only=False, assignment_ids=None):
        rows = catalog['assignments'].values() if assignment_ids is None else (
            catalog['assignments'][id_] for id_ in assignment_ids)
        operators = {catalog['commands'][row['command']].get('operator') for row in rows}
        available = frozenset(name for name in operators if name and _operator_rna(name) is not None)
        return super().plan(catalog, preferences, required_only=required_only,
                            assignment_ids=assignment_ids, available_operators=available)

    def suppression_request(self, id_, row, commands):
        selector = selector_descriptor(row['selector'])
        replacement = self.target(commands[row['replacement']]) if 'replacement' in row else None
        proof = _proof(selector)
        if replacement is None or proof is None:
            return None
        return runtime.KeymapOverride(id_, selector, replacement, *proof,
                                      ledger_id=selector.ledger_id, sample_id=selector.sample_id)
