# Blue Hole  
### Streamlined Blender Environment & Pipeline Toolkit

![Blue Hole Logo](https://blue-hole.weebly.com/uploads/2/2/1/6/2216891/published/image.png?1653836439)

![Blender](https://img.shields.io/badge/Blender-4.5%2B-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)
![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)

Blue Hole is a **free Blender addon and workflow environment** designed to streamline production workflows, particularly for **game development and studio pipelines**.

It provides a curated collection of tools, keymaps, pie menus, and pipeline integrations that transform Blender into a **production-ready environment** inspired by professional DCC tools such as **3ds Max, MODO, and Maya**.

Blue Hole focuses on:

- faster interaction
- predictable workflows
- pipeline integration
- project environments
- artist-friendly tools

The goal is to create a **consistent and efficient workspace** where artists can focus on creating content rather than fighting configuration and setup.

---

# Core Features

## Environment System

Blue Hole introduces the concept of **Environments**.

An environment represents a **project configuration** controlling pipeline settings such as:

- source content paths
- export directories
- asset directory structures
- container configuration
- game engine bridge settings
- source control settings

Each environment stores its configuration in:
`envFiles/<environment_name>/env_variables.ini`

This allows teams to:

- maintain multiple project setups
- share pipeline configurations
- version control environment settings
- switch between projects easily

---

# Game Engine Bridges

Blue Hole simplifies sending assets from Blender into game engines.

### Game Engine Bridges (Unreal, Unity & Godot)

Send assets directly from Blender to Game Engines while preserving:

- Folder Structure
- Export Settings
- Transform Rules

---

# Asset Containers

Blue Hole provides structured **container systems** to organize assets inside Blender scenes.

Containers help enforce production-ready hierarchies for export pipelines.

Available systems include:

- **Asset Hierarchy Containers**
- **Asset Mesh Containers**
- **Asset Collection Containers**

These tools help maintain consistent scene structure across artists and projects.

---

# Batch Export Tools

Export assets from Blender in structured formats suitable for production pipelines.

Features include:

- batch export workflows
- project-based directory structures
- engine-ready exports
- configurable transform options

This reduces repetitive export steps and keeps assets consistent.

---

# Source Control Integration

Blue Hole integrates directly with multiple version control systems:

- **Perforce**
- **Plastic SCM**
- **Git**

Source control features include:

- checkout workflows
- synchronization
- add/edit operations
- workspace validation
- safe file handling

Commands are wrapped internally to provide **safe behavior inside Blender**.

---

# Custom Keymap System

Blue Hole includes a modular **keymap system** designed for speed and consistency.

Keymap features include:

- transform tool shortcuts
- viewport navigation improvements
- selection enhancements
- transform modal tools
- gizmo shortcuts
- pie menu triggers

Keymap features can be enabled or disabled directly in the **addon preferences**.

⚠️ **Note:**  
Some keymaps are still transitioning to a fully programmatic system.  
By switching to Blue Hole Deluxe mode, Blue Hole will still overwrite Blender's `userpref.blend`, to offer all features. This is preceeded by a very clear warning dialog window.

---

# Contextual Pie Menus

Blue Hole includes **artist-focused pie menus** designed to reduce menu navigation.

Pie menus provide fast access to:

- tools
- transforms
- utilities
- configuration menus
- help and documentation

Menus adapt to context where appropriate.

---

# Blue Hole Header Menu

Blue Hole adds a **header menu inside Blender** that exposes many pipeline tools.

From this menu you can access:

- export tools
- container creation
- bridge tools
- environment features
- source control utilities
- help and documentation

This keeps important production tools easily accessible.

---

# Pipeline Utilities

Blue Hole includes several utilities to assist production workflows.

Examples include:

- object sorting tools
- asset hierarchy generation
- renaming utilities
- environment validation helpers
- pipeline configuration tools

These remove common friction points in day-to-day work.

---

# Philosophy

Blue Hole is built around several core ideas.

### Efficiency

Artists should not need to navigate complex menus or repeat tedious tasks.

Blue Hole reduces friction through:

- hotkeys
- pie menus
- automation
- structured workflows

---

### Consistency

Switching between tools should not require relearning workflows.

Blue Hole borrows interaction patterns familiar to artists coming from:

- Maya
- MODO
- 3ds Max
- game engine editors

---

### Context Awareness

Tools adapt to the current situation.

Blue Hole features frequently react to:

- selection state
- active environment
- pipeline configuration
- project structure

---

### Pipeline Friendly

Modern pipelines involve multiple tools and teams.

Blue Hole is designed to integrate with:

- game engines
- version control systems
- structured asset pipelines
- multi-environment projects

---

# Installation

Installation instructions are available on the Blue Hole website:

https://blue-hole.weebly.com/installation.html

Blue Hole requires **Blender 4.5.1 or newer**.

---

# Documentation & Support

**Website**  
https://blue-hole.weebly.com

**Feedback / Issues**  
https://blue-hole.weebly.com/contact.html

---

# License

MIT License

Copyright (c) 2026 Marc-Andre Voyer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files to deal in the Software
without restriction.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.

---

### Third Party Code

This repository includes code derived from:

Epic Games – Blender Tools  
https://github.com/EpicGamesExt/BlenderTools  

which is included under its respective license in `Lib/send2ue`.
