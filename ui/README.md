# UI System

The UI section defines Blue Hole's user interface elements inside Blender.

This includes:

- pie menus
- menu entries
- menu extensions
- menu overrides
- context-sensitive UI behavior

The UI layer is responsible for **presentation and integration with Blender's
existing interface**, while most functional logic lives in operators and
other systems.

---

# Pie Menus

A large part of the UI is implemented through Blender pie menus.

Pie menus are declared using standard Blender `Menu` classes.

Example:

```python
class BLUEHOLE_MT_pie_global_help(bpy.types.Menu):
    bl_idname = "BLUEHOLE_MT_pie_global_help"
    bl_label = "Blue Hole: Help"
```

Pie menus may contain:

- direct operator calls
- entry helper functions
- sub-pie menus
- separators

Pie entries use `OperatorAction` through helper functions such as
`draw_operator_action()` to draw sub-menus.

---

# Entry Functions

Many UI elements are implemented through **entry helper functions**.

These functions encapsulate UI logic such as:

- checking preferences
- enabling or disabling entries
- displaying error messages
- calling operators

Example:
```python
def add_asset_mesh(pie):
    if prefs().container.enable_asset_mesh_container:
        pie.operator(add_ops.SceneAddAssetMesh.bl_idname)
    else:
        col = pie.column()
        col.enabled = False
        col.operator(
            add_ops.SceneAddAssetMesh.bl_idname,
            text="Mesh Containers disabled in Preferences",
            icon='ERROR'
        )
```

This approach allows the UI to remain **context-aware** while keeping
menu declarations readable.

---

# Menu Extensions

Blue Hole extends Blender's existing menus by appending or prepending
entries.

Example:

```python
bpy.types.VIEW3D_MT_add.prepend(draw_blue_hole_add_menu)
```

These extensions allow Blue Hole features to integrate naturally into
Blender’s interface without replacing native functionality.

---

# Menu Overrides

Some menus are fully overridden when deeper integration is required.

Example: overriding the File menu to insert a custom **Blue Hole Save As**
operator for source control workflows.

Example override target:
`TOPBAR_MT_file.draw`

The original draw function is stored and restored when the addon is
disabled.

This allows Blue Hole to modify Blender's UI while remaining reversible.

---

# Context-Sensitive UI

Many UI elements adapt dynamically depending on:

- the current scene state
- the active environment
- addon preferences
- environment preferences

For example:

- some entries only appear when a scene is loaded
- others depend on enabled container systems
- some menu entries become disabled when features are turned off

This ensures the UI reflects the **current capabilities and configuration
of the environment**.

---

# Header Integration

Blue Hole also writes entries into Blender's header menus to expose
common functionality.

These entries can adapt to context and environment state, allowing
important tools to remain accessible without opening additional menus.

---

# OperatorAction Usage

The UI system currently uses `OperatorAction` in limited cases,
primarily when drawing sub-pie menus.

In most areas the UI still calls operators directly.

Over time the UI may transition further toward `OperatorAction`
definitions to reduce duplication between UI and keymap systems.

---

# Design Goals

The UI system aims to:

- integrate seamlessly with Blender's interface
- remain context-aware
- keep menu declarations readable
- avoid duplicating operator logic
- support environment-driven behavior

