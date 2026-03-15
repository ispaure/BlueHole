# Keymap System

This section is responsible for **registering and managing keymaps** for Blue Hole.

Keymaps are not defined here directly. Instead, they are created from
`OperatorAction` objects declared in the `actions/` section of the addon.

The keymap system reads those action definitions and registers their
`KeymapBinding` entries into Blender's keyconfig when the addon loads or
when preferences change.

---

# Architecture Overview

The system is divided into two responsibilities:

## 1. Action Declaration (`actions/`)

Operator actions are declared in the `actions/` package using the
`OperatorAction` class.

An `OperatorAction` describes:

- the Blender operator to call
- an optional UI label and icon
- operator properties
- one or more keymap bindings

Example:

```python
OperatorAction(
    operator='transform.translate',
    text='Move Tool (Modal)',
    keymap_bindings=(...)
)
```

## 2. Keymap Registration (`keymaps/`)

The keymap system reads `OperatorAction` definitions and registers their
bindings into Blender.

Each `OperatorAction` may contain one or more `KeymapBinding` entries which
describe how the operator should be triggered.

A `KeymapBinding` defines things such as:

- keymap name (e.g. "3D View", "Mesh", etc.)
- key
- modifier keys
- direction (for drag gestures)
- region type
- space type

During registration the system:

1. Collects all relevant `OperatorAction` objects
2. Reads their `KeymapBinding` definitions
3. Creates the corresponding Blender keymap items
4. Stores them under the addon keyconfig

This ensures keymaps are always generated from the action definitions rather
than being duplicated across the codebase.



