"""Immutable keymap contracts; no Blender state, imports, or side effects."""
from collections.abc import Mapping
from dataclasses import dataclass, field
import math

EVENT_FIELDS = ('type', 'value', 'any', 'shift', 'ctrl', 'alt', 'oskey',
                'hyper', 'key_modifier', 'direction', 'repeat', 'map_type')
SCOPE_FIELDS = ('name', 'space_type', 'region_type', 'is_modal', 'is_tool')

def freeze(value):
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is float and math.isfinite(value):
        return 0.0 if value == 0 else value
    if isinstance(value, Mapping):
        return tuple(sorted((str(k), freeze(v)) for k, v in value.items()))
    if isinstance(value, (tuple, list)):
        return tuple(freeze(v) for v in value)
    raise ValueError('unreadable_property_schema')


@dataclass(frozen=True)
class KeymapScope:
    name: str
    space_type: str = 'EMPTY'
    region_type: str = 'WINDOW'
    is_modal: bool = False
    is_tool: bool | None = None


@dataclass(frozen=True)
class KeymapEvent:
    type: str
    value: str = 'PRESS'
    any: bool = False
    shift: bool | int = False
    ctrl: bool | int = False
    alt: bool | int = False
    oskey: bool | int = False
    hyper: bool | int | None = False
    key_modifier: str = 'NONE'
    direction: str = 'ANY'
    repeat: bool = False
    map_type: str = 'KEYBOARD'


@dataclass(frozen=True)
class KeymapTarget:
    idname: str = ''
    properties: tuple = ()
    modal_value: str = ''

    def __post_init__(self):
        object.__setattr__(self, 'properties', freeze(dict(self.properties)))
        if bool(self.idname) == bool(self.modal_value):
            raise ValueError('Target requires exactly one operator or modal token')


@dataclass(frozen=True)
class KeymapAssignment:
    request_id: str
    scope: KeymapScope
    event: KeymapEvent
    target: KeymapTarget
    ledger_id: str = ''
    sample_id: str = ''
    declared_properties_only: bool = False
    active: bool = True
    requires_operator: bool = False
    required_class: str = ''
    required_addon: str = ''
    dispatch_group: str = ''


@dataclass(frozen=True)
class KeymapSelector:
    scope: KeymapScope
    event: KeymapEvent
    target: KeymapTarget
    source_role: str = 'default'
    ledger_id: str = ''
    sample_id: str = ''

@dataclass(frozen=True)
class KeymapOverride:
    request_id: str
    selector: KeymapSelector
    replacement: KeymapTarget
    capability: str = ''
    context: str = ''
    ledger_id: str = ''
    sample_id: str = ''
    replacement_event: KeymapEvent | None = field(default=None, init=False)
    replacement_active: bool = field(default=True, init=False)

    def __post_init__(self):
        if isinstance(self.replacement, KeymapAssignment):
            assignment = self.replacement
            object.__setattr__(self, 'replacement_event', assignment.event)
            object.__setattr__(self, 'replacement_active', assignment.active)
            object.__setattr__(self, 'replacement', assignment.target)


@dataclass(frozen=True)
class KeymapDiagnostic:
    owner_id: str
    request_id: str
    status: str
    reason: str
    ledger_id: str = ''
    sample_id: str = ''
    observed_role: str = ''
    observed_context: str = ''
    pending_capability: str = ''
    dispatch_evidence: bool = False


