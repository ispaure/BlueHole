"""
Shared operator action helpers for Blue Hole.

This module provides a unified way to describe:
- an operator call
- optional operator properties
- optional UI enabled / disabled state with reason
- optional keymap bindings

The same OperatorAction can then be reused for:
- pie menu buttons
- menus
- panels
- keymap registration

This does NOT replace the Blender operator classes themselves.
It only describes how Blue Hole wants to expose or invoke them.
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://github.com/ispaure/BlueHole

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable
from ..Lib.commonUtils.runtime.diagnostics import *
from ..debug.debug_flags import *

# ----------------------------------------------------------------------------------------------------------------------
# DATACLASSES


@dataclass(frozen=True)
class UIState:
    """
    UI state for an operator action.

    enabled : Whether the UI element is enabled.
    reason  : Optional label shown when disabled (fallbacks to action text).
    icon    : Icon used when the action is disabled.
    """
    enabled: bool = True
    reason: str = ""
    icon: str = 'ERROR'


@dataclass(frozen=True)
class KeymapBinding:
    """
    Keymap binding metadata for an operator action.
    """
    keymap_name: str
    space_type: str
    key: str
    value: str = 'PRESS'
    ctrl: bool | int = False
    shift: bool | int = False
    alt: bool | int = False
    oskey: bool | int = False
    repeat: bool = False
    region_type: str = 'WINDOW'
    direction: str = 'ANY'
    any: bool = False
    hyper: bool | int = False
    key_modifier: str = 'NONE'
    map_type: str | None = None
    active: bool = True
    is_tool: bool | None = None


@dataclass
class OperatorAction:
    """
    Shared description of a Blender operator call.

    operator        : Operator bl_idname string or operator class.
    text            : UI label used when drawing the action.
    icon            : Default UI icon.
    props           : Static operator properties applied to buttons and keymaps.
    props_fn        : Optional callable -> dict of dynamic properties (fn(context)).
    ui_state_fn     : Optional callable -> UIState (fn(context)).
    keymap_bindings : Optional tuple of KeymapBinding definitions.
    """
    operator: str | type
    text: str = ""
    icon: str = 'NONE'
    props: dict[str, Any] = field(default_factory=dict)
    props_fn: Callable[[Any], dict[str, Any]] | None = None
    ui_state_fn: Callable[[Any], UIState] | None = None
    keymap_bindings: tuple[KeymapBinding, ...] = ()

    def get_idname(self) -> str:
        """
        Return the operator bl_idname.
        """
        return resolve_bl_idname(self.operator)

    def get_props(self, context=None) -> dict[str, Any]:
        """
        Return the merged static + dynamic operator properties.
        Dynamic props override static props on duplicate keys.
        """
        result = dict(self.props)

        if self.props_fn is not None:
            dynamic_props = self.props_fn(context) or {}
            result.update(dynamic_props)

        return result

    def get_ui_state(self, context=None) -> UIState:
        """
        Return the current UIState for this action.
        """
        if self.ui_state_fn is None:
            return UIState()

        ui_state = self.ui_state_fn(context)

        if ui_state is None:
            return UIState()

        return ui_state

    def get_label(self) -> str:
        if self.text:
            return self.text

        idname = self.get_idname()

        try:
            import bpy
            op_module, op_name = idname.split(".")
            op = getattr(getattr(bpy.ops, op_module), op_name)
            return op.get_rna_type().name or idname
        except Exception:
            return idname

    def with_keymap_bindings(self, *bindings: KeymapBinding) -> "OperatorAction":
        """
        Return a copy of this action with additional keymap bindings appended.
        """
        return OperatorAction(
            operator=self.operator,
            text=self.text,
            icon=self.icon,
            props=dict(self.props),
            props_fn=self.props_fn,
            ui_state_fn=self.ui_state_fn,
            keymap_bindings=tuple((*self.keymap_bindings, *bindings)),
        )


# ----------------------------------------------------------------------------------------------------------------------
# RESOLVE HELPERS


def resolve_bl_idname(target: str | type) -> str:
    """
    Resolve a Blender bl_idname from either:
    - a raw idname string
    - a Blender class defining bl_idname
    """
    if isinstance(target, str):
        return target

    bl_idname = getattr(target, 'bl_idname', None)

    if not bl_idname:
        raise ValueError(f'Class "{target}" has no valid bl_idname.')

    return bl_idname


# ----------------------------------------------------------------------------------------------------------------------
# PROPERTY HELPERS


def apply_properties(target, props: dict[str, Any]) -> None:
    """
    Apply properties to a Blender operator button or keymap item properties object.
    """
    if target is None or not props:
        return

    for key, value in props.items():
        setattr(target, key, value)


# ----------------------------------------------------------------------------------------------------------------------
# DRAW HELPERS


def draw_operator_action(
        layout,
        action: OperatorAction,
        context=None,
        text: str | None = None,
        icon: str | None = None
):
    """
    Draw an OperatorAction in any Blender layout.

    This works for:
    - normal layouts
    - menu layouts
    - pie layouts

    Optional parameters
    -------------------
    text:
        Optional UI label override. If None, action.text is used.

    icon:
        Optional UI icon override. If None, action.icon is used.

    Returns
    -------
    The created operator UI instance.
    """
    ui_state = action.get_ui_state(context)
    idname = action.get_idname()
    props = action.get_props(context)

    resolved_text = action.text if text is None else text
    resolved_icon = action.icon if icon is None else icon

    if ui_state.enabled:
        op = layout.operator(
            idname,
            text=resolved_text,
            icon=resolved_icon,
        )
    else:
        col = layout.column()
        col.enabled = False
        op = col.operator(
            idname,
            text=ui_state.reason or resolved_text or 'Unavailable',
            icon=ui_state.icon,
        )

    apply_properties(op, props)
    return op


# ----------------------------------------------------------------------------------------------------------------------
# KEYMAP HELPERS


def create_keymap_item(km, action: OperatorAction, binding: KeymapBinding, context=None):
    """Create an exactly owned ordinary binding through the shared runtime."""
    if km is None:
        return None
    from ..keymaps.keymap_utils import get_addon_keyconfig, capture_scope, KeymapScope
    from ..keymaps.keymap_action_utils import ensure_action_keymaps

    config = get_addon_keyconfig()
    try:
        if config is None or not any(candidate == km for candidate in config.keymaps):
            return None
    except (ReferenceError, RuntimeError):
        return None
    scope = KeymapScope(binding.keymap_name, binding.space_type, binding.region_type,
                        False, binding.is_tool)
    observed = capture_scope(km)
    if ((observed.name, observed.space_type, observed.region_type, observed.is_modal)
            != (scope.name, scope.space_type, scope.region_type, scope.is_modal)
            or (scope.is_tool is not None and observed.is_tool != scope.is_tool)):
        return None
    one = OperatorAction(action.operator, props=action.props, props_fn=action.props_fn,
                         keymap_bindings=(binding,))
    pairs = ensure_action_keymaps('Direct', one, context=context,
                                  keyconfig=config)
    return next((item for map_, item in pairs if map_ == km), None)


def create_keymap(kc, binding: KeymapBinding):
    """Resolve the full ordinary map scope for compatibility callers."""
    from ..keymaps.keymap_utils import get_or_create_keymap
    return get_or_create_keymap(kc, binding.keymap_name, binding.space_type,
                               binding.region_type)


def register_operator_action_keymaps(category: str, kc, action: OperatorAction, context=None) -> list[tuple[Any, Any]]:
    """Register atomically; only this session's exact items can be released."""
    from ..keymaps.keymap_action_utils import ensure_action_keymaps
    return ensure_action_keymaps(category, action, context=context, keyconfig=kc)


def unregister_registered_keymaps(registered_keymaps: list[tuple[Any, Any]]) -> None:
    """Release tracked ownership, including pending bindings in bound categories."""
    from ..keymaps.keymap_utils import release_owned_pairs
    release_owned_pairs(registered_keymaps)


# ----------------------------------------------------------------------------------------------------------------------
# CONVENIENCE HELPERS


def pie_menu_action(
        menu: str | type,
        *,
        text: str = "",
        icon: str = 'NONE',
        ui_state_fn: Callable[[Any], UIState] | None = None,
        keymap_bindings: Iterable[KeymapBinding] = (),
) -> OperatorAction:
    """
    Return an OperatorAction that opens a pie menu with wm.call_menu_pie.

    menu:
        Either the menu bl_idname string, or the Blender menu class.
    """
    return OperatorAction(
        operator='wm.call_menu_pie',
        text=text,
        icon=icon,
        props={'name': resolve_bl_idname(menu)},
        ui_state_fn=ui_state_fn,
        keymap_bindings=tuple(keymap_bindings),
    )


def menu_action(
        menu: str | type,
        *,
        text: str = "",
        icon: str = 'NONE',
        ui_state_fn: Callable[[Any], UIState] | None = None,
        keymap_bindings: Iterable[KeymapBinding] = (),
) -> OperatorAction:
    """
    Return an OperatorAction that opens a normal menu with wm.call_menu.
    """
    return OperatorAction(
        operator='wm.call_menu',
        text=text,
        icon=icon,
        props={'name': resolve_bl_idname(menu)},
        ui_state_fn=ui_state_fn,
        keymap_bindings=tuple(keymap_bindings),
    )


# ----------------------------------------------------------------------------------------------------------------------
# OPTIONAL MATCH HELPERS


def action_matches_kmi(kmi, action: OperatorAction, context=None) -> bool:
    """
    Return True if the given keymap item matches the operator action.

    Note:
        Matching checks operator idname first.
        Then all action props must match on kmi.properties.
    """
    if kmi is None:
        return False

    if kmi.idname != action.get_idname():
        return False

    for key, value in action.get_props(context).items():
        if getattr(kmi.properties, key, None) != value:
            return False

    return True


def remove_matching_action_kmis(km, action: OperatorAction, context=None) -> None:
    """Release matching session-owned items; foreign lookalikes are never deleted."""
    from ..keymaps.keymap_utils import release_owned_pairs, owned_pairs_for_map
    props = action.get_props(context)
    pairs = [(map_, item) for map_, item in owned_pairs_for_map(km)
             if item.idname == action.get_idname()
             and all(getattr(item.properties, name, None) == value
                     for name, value in props.items())]
    release_owned_pairs(pairs)
