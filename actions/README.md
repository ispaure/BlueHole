# Actions System

The actions system provides a reusable description of Blender operators.

Instead of directly invoking operators or defining shortcuts in multiple
places, Blue Hole represents them using `OperatorAction` objects.

An `OperatorAction` acts as a **single source of truth** describing how an
operator should behave across the addon.

---

# OperatorAction

Each action is defined using the `OperatorAction` class.

An `OperatorAction` may contain:

- **operator idname**  
  The Blender operator to execute (string or operator class).

- **text**  
  Optional UI label used when displaying the action in menus or layouts.

- **icon**  
  Optional UI icon.

- **props**  
  Static operator properties passed when the operator is executed.

- **props_fn**  
  Optional callable that returns dynamic operator properties based on context.

- **ui_state_fn**  
  Optional callable returning a UI state used to control whether the action
  should be enabled or disabled in the interface.

- **keymap_bindings**  
  One or more `KeymapBinding` definitions describing the shortcuts that
  should trigger this action.

---

# Keymap Bindings

Keymap shortcuts are declared using `KeymapBinding` objects attached to an
`OperatorAction`.

These bindings describe:

- the keymap where the shortcut exists
- key and modifier combination
- optional drag directions
- region and space type

The keymap system reads these bindings during registration and creates the
corresponding Blender keymap entries.

---

# Reuse Across the Addon

The same `OperatorAction` definitions are reused by multiple systems.

### UI Layouts

Actions can be drawn directly in Blender UI layouts.

This allows menus, panels, and buttons to reference the same action
definition used by shortcuts.

### Keymap Registration

The keymap system reads the `KeymapBinding` entries and registers them
in Blender's key configuration.

### Preferences Display

Addon preferences use `OperatorAction` objects to display the currently
registered shortcuts and allow users to view or modify them.

---

# Design Goals

The actions system exists to avoid duplication and keep operator behavior
consistent across the addon.

Benefits include:

- **Single source of truth** for operator definitions
- **Reusable operator descriptions**
- **Centralized keymap definitions**
- **Consistent UI labels and behavior**
- **Simplified preference integration**

By separating operator descriptions from UI code and keymap registration,
the system keeps Blue Hole modular and easier to maintain.