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

# ----------------------------------------------------------------------------------------------------------------------
# DATACLASSES


@dataclass(frozen=True)
class UIState:
    """
    UI state for an operator action.

    enabled:
        Whether the button / menu entry should be enabled.

    reason:
        Optional label to show when disabled.
        If empty, the action's normal text is used instead.

    icon:
        Icon to use when disabled.
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
    ctrl: bool = False
    shift: bool = False
    alt: bool = False
    repeat: bool = False
    region_type: str = 'WINDOW'


@dataclass
class OperatorAction:
    """
    Shared description of a Blender operator call.

    operator:
        Either the operator bl_idname string, or the operator class itself.

    text:
        Default UI label to use when drawing the action in a layout.

    icon:
        Default UI icon.

    props:
        Static operator properties applied both to layout buttons and keymaps.

    props_fn:
        Optional callable returning additional or overriding props.
        Signature: fn(context) -> dict

    ui_state_fn:
        Optional callable returning a UIState.
        Signature: fn(context) -> UIState

    keymap_bindings:
        Optional tuple of keymap bindings for this action.
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
        return resolve_operator_idname(self.operator)

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

    def copy_with(
            self,
            *,
            operator: str | type | None = None,
            text: str | None = None,
            icon: str | None = None,
            props: dict[str, Any] | None = None,
            props_fn: Callable[[Any], dict[str, Any]] | None = None,
            ui_state_fn: Callable[[Any], UIState] | None = None,
            keymap_bindings: Iterable[KeymapBinding] | None = None,
    ) -> "OperatorAction":
        """
        Return a shallow modified copy of this action.
        """
        return OperatorAction(
            operator=self.operator if operator is None else operator,
            text=self.text if text is None else text,
            icon=self.icon if icon is None else icon,
            props=dict(self.props if props is None else props),
            props_fn=self.props_fn if props_fn is None else props_fn,
            ui_state_fn=self.ui_state_fn if ui_state_fn is None else ui_state_fn,
            keymap_bindings=self.keymap_bindings if keymap_bindings is None else tuple(keymap_bindings),
        )

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


def resolve_operator_idname(operator: str | type) -> str:
    """
    Resolve an operator idname from either:
    - a raw bl_idname string
    - a Blender operator class
    """
    if isinstance(operator, str):
        return operator

    bl_idname = getattr(operator, 'bl_idname', None)

    if not bl_idname:
        raise ValueError(f'Operator class "{operator}" has no valid bl_idname.')

    return bl_idname


def resolve_menu_idname(menu: str | type) -> str:
    """
    Resolve a menu idname from either:
    - a raw menu bl_idname string
    - a Blender menu class
    """
    if isinstance(menu, str):
        return menu

    bl_idname = getattr(menu, 'bl_idname', None)

    if not bl_idname:
        raise ValueError(f'Menu class "{menu}" has no valid bl_idname.')

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


def draw_operator_action(layout, action: OperatorAction, context=None):
    """
    Draw an OperatorAction in any Blender layout.

    This works for:
    - normal layouts
    - menu layouts
    - pie layouts

    Returns the created operator UI instance.
    """
    ui_state = action.get_ui_state(context)
    idname = action.get_idname()
    props = action.get_props(context)

    if ui_state.enabled:
        op = layout.operator(
            idname,
            text=action.text,
            icon=action.icon,
        )
    else:
        col = layout.column()
        col.enabled = False
        op = col.operator(
            idname,
            text=ui_state.reason or action.text or 'Unavailable',
            icon=ui_state.icon,
        )

    apply_properties(op, props)
    return op


# ----------------------------------------------------------------------------------------------------------------------
# KEYMAP HELPERS


def create_keymap_item(km, action: OperatorAction, binding: KeymapBinding, context=None):
    """
    Create and return a Blender keymap item for the given action and binding.

    Returns:
        kmi | None
    """
    if km is None:
        return None

    kmi = km.keymap_items.new(
        action.get_idname(),
        type=binding.key,
        value=binding.value,
        ctrl=binding.ctrl,
        shift=binding.shift,
        alt=binding.alt,
    )

    apply_properties(kmi.properties, action.get_props(context))
    kmi.active = True

    if hasattr(kmi, 'repeat'):
        kmi.repeat = binding.repeat

    return kmi


def create_keymap(kc, binding: KeymapBinding):
    """
    Return an existing keymap if found, otherwise create it.
    """
    if kc is None:
        return None

    km = kc.keymaps.get(binding.keymap_name)

    if km is not None:
        return km

    return kc.keymaps.new(
        name=binding.keymap_name,
        space_type=binding.space_type,
        region_type=binding.region_type,
    )


def register_operator_action_keymaps(kc, action: OperatorAction, context=None) -> list[tuple[Any, Any]]:
    """
    Register all keymap bindings attached to this action in the given keyconfig.

    Returns:
        list[(km, kmi)]
    """
    registered = []

    if kc is None:
        return registered

    for binding in action.keymap_bindings:
        km = create_keymap(kc, binding)

        if km is None:
            continue

        kmi = create_keymap_item(km, action, binding, context=context)

        if kmi is not None:
            registered.append((km, kmi))

    return registered


def unregister_registered_keymaps(registered_keymaps: list[tuple[Any, Any]]) -> None:
    """
    Remove all registered keymap items from Blender and clear the given runtime list.
    """
    for km, kmi in reversed(registered_keymaps):
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass

    registered_keymaps.clear()


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
        props={'name': resolve_menu_idname(menu)},
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
        props={'name': resolve_menu_idname(menu)},
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
    """
    Remove all keymap items in the given keymap that match the operator action.
    """
    if km is None:
        return

    items_to_remove = []

    for kmi in km.keymap_items:
        if action_matches_kmi(kmi, action, context=context):
            items_to_remove.append(kmi)

    for kmi in items_to_remove:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass


# ----------------------------------------------------------------------------------------------------------------------
# EXAMPLE USAGE
#
# NORMAL OPERATOR
#
# ADD_ASSET_HIERARCHY = OperatorAction(
#     operator=add_ops.SceneAddAssetHierarchy,
#     text='Add Asset Hierarchy',
#     ui_state_fn=lambda context: (
#         UIState(enabled=False, reason='Hierarchy Containers disabled in Preferences')
#         if not prefs().container.enable_asset_hierarchy_container
#         else UIState()
#     ),
# )
#
# PIE MENU
#
# OBJECT_ACTION_PIE = pie_menu_action(
#     object_pies.BLUEHOLE_MT_pie_object_action,
#     keymap_bindings=(
#         KeymapBinding(
#             keymap_name='Object Mode',
#             space_type='EMPTY',
#             key='RIGHTMOUSE',
#             ctrl=True,
#         ),
#     )
# )
#
# MODE SWITCH
#
# SCULPT_CURVES_MODE = OperatorAction(
#     operator='object.mode_set',
#     text='Sculpt Curves',
#     props={'mode': 'SCULPT_CURVES'},
# )
#
# DRAW
#
# draw_operator_action(layout, ADD_ASSET_HIERARCHY, context)
# draw_operator_action(pie, OBJECT_ACTION_PIE, context)
#
# REGISTER KEYMAPS
#
# registered_keymaps = []
# registered_keymaps.extend(register_operator_action_keymaps(kc, OBJECT_ACTION_PIE))
#
# UNREGISTER KEYMAPS
#
# unregister_registered_keymaps(registered_keymaps)
