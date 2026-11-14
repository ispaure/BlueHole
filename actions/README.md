# UI actions

`OperatorAction` describes an operator call, button label/icon, properties and
optional enabled state for menus and panels. `draw_operator_action()` draws it.
`pie_menu_action()` and `menu_action()` create menu-opening actions without
importing the menus, avoiding a dependency cycle.

`actions/pie_actions.py` retains the 25 pie submenu actions used by the UI.
Shortcut declarations and registration live in the
[Deluxe JSON catalog and runtime](../keymaps/README.md). The former Python
keymap declarations, binding helpers and unused pie actions have been removed.
The operators themselves remain in `operators/`, and menu implementations
remain in `ui/`.
