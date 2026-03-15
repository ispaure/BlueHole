# Environment System

The environment system manages Blue Hole's **project-specific configuration**.

Unlike addon preferences, which are global to the addon installation,
environment preferences are meant to change depending on the active
project, pipeline, or working setup.

Each environment corresponds to a folder on disk and stores its settings in
an `.ini` file.

---

# Purpose

The environment system allows Blue Hole to separate:

- **global addon behavior**
- **project / pipeline configuration**

This makes it possible to keep stable user preferences while switching
between different environments with different paths, bridge settings,
container rules, and source control values.

Typical examples of environment-specific settings include:

- source content paths
- Unity / Unreal bridge settings
- asset directory structure
- Perforce connection values
- container naming and structure rules

---

# Environment Storage

Each environment is stored under:

`envFiles/<environment_name>/`

The main configuration file for an environment is:

`env_variables.ini`

This file acts as the persistent storage layer for project-specific
settings.

Multiple environments can exist at the same time, and one of them is
selected as the **active environment**.

---

# Main Responsibilities

The environment section is responsible for:

- tracking which environment is currently active
- discovering available environments on disk
- creating and deleting environments
- mapping Blender preferences to `.ini` values
- importing `.ini` values into Blender preferences
- exporting Blender preference values back to `.ini`
- resolving environment-dependent paths

---

# Main Components

## `envManager`

This module manages high-level environment selection and lookup.

It provides helpers to:

- get the active environment from preferences
- set the active environment
- get the default environment
- ensure the active environment is valid
- list all available environments
- build enum items for Blender UI

It acts as the main entry point for environment discovery and switching.

### Key ideas

- the active environment name is stored in preferences
- the active environment is represented by an `Environment` instance
- if the active environment is missing or invalid, Blue Hole falls back to
  the `default` environment

---

## `model`

This module defines the main data models used by the environment system.

### `Setting`

A `Setting` maps:

- a Blender preference path
- an `.ini` section
- an `.ini` variable name
- a Python value type

It is responsible for synchronizing one setting between Blender
preferences and the environment `.ini` file.

A `Setting` can:

- read a value from `.ini` and apply it to Blender preferences
- read a value from Blender preferences and write it back to `.ini`

### `Environment`

An `Environment` represents one named Blue Hole environment.

It contains:

- the environment name
- the environment folder path
- the `env_variables.ini` path
- the list of mapped `Setting` objects for that environment

It can:

- import `.ini` values into preferences
- export preferences back into `.ini`
- create a new environment from another one
- delete an environment from disk

---

## `mapping`

This module contains the mapping declarations between Blue Hole preference
paths and `.ini` values.

It groups environment-controlled settings into logical categories, such as:

- bridge settings
- directory settings
- container settings
- source control settings

Each entry is declared using a `Setting(...)` object.

This makes the synchronization system explicit and centralized.

### Example responsibilities of mappings

- define which Blender preference belongs to which `.ini` section
- define the expected value type
- define which settings are environment-controlled

The mapping layer is what tells Blue Hole **which preferences belong to the
environment system**.

---

## `envPath`

This module resolves and validates environment-dependent paths.

It provides helpers for operations that need valid project paths at
runtime, such as:

- checking whether configured directories exist
- resolving Unity asset paths
- resolving export target paths
- validating bridge-related folders

This module is mainly focused on **runtime path resolution**, while
`envManager`, `model`, and `mapping` focus on environment persistence and
synchronization.

---

# Import / Export Flow

The environment system keeps Blender preferences and `.ini` files in sync.

## Import

When an environment is loaded:

1. the active environment is resolved
2. its `env_variables.ini` file is read
3. mapped values are converted to the correct Python types
4. those values are applied into Blender preferences

If a value is missing from the active environment, Blue Hole attempts to
fall back to the `default` environment.

## Export

When an environment-controlled preference changes:

1. the current Blender preference value is read
2. the corresponding `.ini` mapping is found
3. the value is converted to string form if needed
4. `env_variables.ini` is updated

This allows the active environment's file to remain the persistent source
of truth for project-specific settings.

---

# Default Environment Fallback

The `default` environment plays a special role.

If the current environment is missing values, Blue Hole can fall back to
the default environment for those settings.

This provides:

- safer initialization
- fewer missing configuration errors
- a common baseline shared across all environments

The default environment also acts as a recovery target if the active
environment becomes invalid or is deleted.

---

# Environment Lifecycle

The environment system supports the full lifecycle of environments.

## Create

A new environment can be created by copying an existing source
environment.

This allows users to start from an existing working configuration instead
of configuring everything from scratch.

## Select

One environment is selected as the active environment and its values are
loaded into Blender preferences.

## Delete

An environment can be deleted from disk.

If the deleted environment was active, Blue Hole automatically falls back
to the default environment and reloads its settings.

---

# Preference Scope

The environment system only controls **environment-specific preferences**.

It does **not** manage global addon preferences such as:

- keymap configuration
- pie menu configuration
- other addon-wide user customization

Those belong to the addon preferences system.

This separation is intentional:

- **Addon Preferences** = user-level customization
- **Environment Preferences** = project / pipeline configuration

---

# Design Goals

The environment system exists to provide:

- switchable project-specific configurations
- `.ini`-backed persistence
- clear separation from global addon preferences
- reusable preference-to-config mappings
- safer fallback behavior through the default environment
- easier sharing and versioning of project settings

By centralizing environment discovery, synchronization, and path
resolution, Blue Hole can support multiple pipelines and projects without
forcing all settings into one global configuration.