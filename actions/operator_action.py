"""
Shared operator action helpers for Blue Hole.

This module provides a unified way to describe:
- an operator call
- optional operator properties
- optional UI enabled / disabled state with reason

The same OperatorAction can then be reused for:
- pie menu buttons
- menus
- panels

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
from typing import Any, Callable

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


@dataclass
class OperatorAction:
    """
    Shared description of a Blender operator call.

    operator        : Operator bl_idname string or operator class.
    text            : UI label used when drawing the action.
    icon            : Default UI icon.
    props           : Static operator properties applied to buttons.
    props_fn        : Optional callable -> dict of dynamic properties (fn(context)).
    ui_state_fn     : Optional callable -> UIState (fn(context)).
    """
    operator: str | type
    text: str = ""
    icon: str = 'NONE'
    props: dict[str, Any] = field(default_factory=dict)
    props_fn: Callable[[Any], dict[str, Any]] | None = None
    ui_state_fn: Callable[[Any], UIState] | None = None

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
    Apply properties to a Blender operator button properties object.
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
# CONVENIENCE HELPERS


def pie_menu_action(
        menu: str | type,
        *,
        text: str = "",
        icon: str = 'NONE',
        ui_state_fn: Callable[[Any], UIState] | None = None,
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
    )


def menu_action(
        menu: str | type,
        *,
        text: str = "",
        icon: str = 'NONE',
        ui_state_fn: Callable[[Any], UIState] | None = None,
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
    )
