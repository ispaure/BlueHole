# Keymap System

This section is responsible for **registering and managing keymaps** for Blue Hole.

Blue Hole's editable shortcuts come from the
[Deluxe catalog](../docs/deluxe-keymap-profiles.md) and use the runtime ownership
ledger. The programmatic action declarations below supply the required Save As
bindings before Deluxe is configured and provide reference coverage for the
migration to JSON.

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



