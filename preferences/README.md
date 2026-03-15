# Preferences System

Blue Hole uses two distinct types of preferences:

- **Addon Preferences**
- **Environment Preferences**

Both types of preferences are accessed through Blender:

`Edit → Preferences → Add-ons → Blue Hole`

These two systems serve different purposes and are managed separately.

---

# 1. Addon Preferences

Addon preferences store **global configuration for the Blue Hole addon**.

These settings are saved inside Blender's addon preferences and apply to
the addon installation regardless of the current working environment.

Examples of addon preferences include:

- keymap feature toggles
- pie menu configuration
- UI display options

These preferences represent **user-level customization**, rather than
project-specific configuration.

Examples of systems controlled by addon preferences:

Keymaps  
 ├ Navigation  
 ├ Selection  
 └ Transform  

Pie Menus _(general configuration)_

Addon preferences are typically stable and do not change between projects
or environments.

---

# 2. Environment Preferences

Environment preferences represent **project or environment-specific
configuration**.

Unlike addon preferences, these settings change depending on the active
working environment.

Each environment stores its configuration in:

`envFiles/<environment_name>/`

Environments can be:

- created
- customized
- deleted

One environment is selected as the **active environment**, and its settings
are used by the addon.

The active environment's preferences are:

- **imported** from `env_variables.ini` when the environment loads
- **exported** to `env_variables.ini` whenever values change
- **reloaded** when switching environments

Because these preferences are stored as `.ini` files, they can easily be:

- version controlled
- shared across teams
- switched between pipelines or projects

Examples of environment-specific configuration may include:

- content directory locations
- pipeline configuration
- external tool paths
- environment-specific project settings

Multiple environments can exist simultaneously, allowing users to switch
between them without affecting global addon preferences.

---

# Design Philosophy

The preference system separates **user customization** from
**project configuration**.

Addon Preferences → control how the addon behaves for the user  
Environment Preferences → control how the addon behaves for a project

This separation allows Blue Hole to support:

- multiple environments
- shared project configurations
- stable user customization
- reproducible pipelines