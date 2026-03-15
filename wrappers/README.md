# Perforce Wrapper

This section provides Blue Hole's wrapper layer around the Perforce
command-line tools.

Its role is to give the addon a **structured, safer, and more Blender-aware**
way to interact with Perforce than issuing raw shell commands directly.

The wrapper is responsible for:

- querying Perforce connection information
- reading file status
- opening files for edit
- syncing files
- marking files for add
- handling batch operations efficiently
- translating Perforce failures into user-facing Blender messages

---

# Purpose

Blue Hole uses Perforce as part of its source control workflow.

Rather than scattering raw `p4` calls throughout the addon, this wrapper
centralizes Perforce behavior into reusable Python classes and helper
functions.

This provides:

- a consistent API for Perforce operations
- centralized error handling
- platform-aware command execution
- safer file state validation before modifying files

---

# Main Components

## `P4Info`

`P4Info` wraps the `p4 info` command and stores information about the
current Perforce connection.

It is used to query and validate:

- user name
- client/workspace name
- client root
- current working directory
- server address
- server uptime
- general connection health

It also performs connection-related checks such as:

- whether the server is accessible
- whether the login token is expired
- whether Perforce is installed and callable

This class is typically used as the first validation step before file
operations are attempted.

---

## `P4File`

`P4File` represents a **single Perforce-tracked file**.

A file may be identified by either:

- `clientFile`
- `depotFile`

`P4File` can:

- query its Perforce metadata through `p4 fstat`
- deduce a simplified status
- validate whether it is safe to work on
- run Perforce commands on itself

It stores detailed Perforce fields such as:

- depot path
- client path
- head revision
- have revision
- file action
- checkout owner
- type
- change number

It also derives a simplified status using `P4FileStatus`.

---

## `P4FileStatus`

`P4FileStatus` is a simplified enum used by Blue Hole to reason about file
state.

Examples include:

- `NOT_ADDED`
- `MARKED_FOR_ADD`
- `MARKED_FOR_DELETE`
- `CHECKOUT_BY_ME`
- `CHECKOUT_BY_OTHER`
- `LATEST_REVISION`
- `NOT_LATEST_REVISION`

This abstraction allows the addon to make decisions without repeatedly
interpreting raw Perforce metadata.

---

## `BlendP4File`

`BlendP4File` is a specialization of `P4File` for `.blend` files.

It adds Blender-specific behavior on top of normal Perforce handling.

Example:

- after syncing a `.blend` file, it can reopen the scene in Blender

This class is intended for source control operations involving the current
Blender scene file.

---

## `P4FileGroup`

`P4FileGroup` is the **batch operation** version of `P4File`.

It is designed for performance.

Instead of running many single-file Perforce commands in a loop,
`P4FileGroup` groups files together and performs fewer, larger Perforce
calls whenever possible.

It supports:

- batch field refresh from `p4 fstat`
- grouped add/edit/sync operations
- grouped validation checks
- mixed client/depot path handling

This is the preferred approach whenever Blue Hole needs to operate on
multiple files at once.

---

# Command Execution

## `exec_p4_command()`

All Perforce shell execution is funneled through `exec_p4_command()`.

This helper ensures that:

- only valid `p4 ...` commands are passed through this path
- Perforce executable resolution is platform-aware
- macOS and Linux can target the configured `p4_parallel` executable
- executable permissions are corrected when necessary
- command execution is delegated to the common shell wrapper

This function acts as the low-level execution boundary between Blue Hole
and the Perforce CLI.

---

# File Status Queries

## `p4_fstat_dict()`

This helper converts `p4 fstat` output into a more usable Python structure.

Instead of working with raw command-line text, Blue Hole converts the
result into:

- a list of dictionaries
- one dictionary per file

This parsed output is then used by `P4File` and `P4FileGroup` to populate
their fields and compute simplified file status.

---

# Validation Flow

Before opening a file for edit, the wrapper performs a sequence of checks.

Typical checks include:

- Perforce server is reachable
- login token is valid
- file is under the active workspace root
- file is inside the workspace view
- file is not checked out by someone else
- file is not marked for delete
- file is synced to the latest revision when required

Only after those checks pass does the wrapper proceed with:

- `p4 add`
- `p4 sync -f`
- `p4 edit`

This keeps source control operations safer and reduces the risk of
invalid or destructive checkout attempts.

---

# Single-File vs Batch Workflows

Blue Hole supports two levels of Perforce workflows.

## Single-file workflow

Use `P4File` when:

- user interaction is required
- confirmation dialogs may appear
- the operation targets one explicit file

Example:

- manually checking out the currently open `.blend` file

## Batch workflow

Use `P4FileGroup` when:

- many files must be processed
- performance matters
- repeated `p4` calls should be minimized

Example:

- preparing a large group of export targets for edit

The batch path is preferred whenever possible.

---

# Environment Integration

The wrapper also integrates with Blue Hole's source control preferences.

## `set_p4_env_settings()`

This function applies configured Perforce environment values when needed.

Depending on the platform and Blue Hole settings, it may set values such as:

- `P4USER`
- `P4PORT`
- `P4CLIENT`

This is especially important on platforms (macOS & Linux) where Perforce environment
configuration is less automatic or must be explicitly overridden.

The wrapper therefore bridges:

- Blue Hole preferences
- operating system specifics
- Perforce command-line execution

---

# Error and Log Messaging

The wrapper separates feedback into three categories:

## `P4LogMessage`

Used for debug and informational logging.

Examples:

- file is in client view
- file is under workspace root
- server is accessible

## `P4ErrorMessage`

Used for recoverable errors.

These messages are written for end users and explain:

- what went wrong
- what to do next
- why the operation was aborted

They are intentionally more descriptive than raw Perforce output.

## `P4CriticalMessage`

Used for invalid internal usage or unrecoverable problems.

Examples:

- creating a `P4File` without a client or depot path
- invalid command usage

---

# Binary File Handling

## `create_empty_binary_file()`

When marking a file for add, Blue Hole may create a small binary template
file first if the file does not yet exist on disk.

This is done to avoid Perforce misclassifying future binary assets
(such as `.blend` or `.fbx` files) as text files.

This behavior is especially important for workflows where files are added
before their final binary contents are written.

---

# Platform Awareness

The wrapper contains explicit operating-system handling for:

- Windows
- macOS
- Linux

This includes:

- locating the correct Perforce executable
- handling execution permissions
- configuring environment settings differently per OS

This allows Blue Hole's Perforce integration to behave consistently across
multiple platforms.

---

# Design Goals

The Perforce wrapper exists to provide:

- a centralized Perforce API for the addon
- safer source control workflows
- better user-facing error reporting
- batch-friendly performance
- Blender-aware behavior for scene files
- cross-platform Perforce execution

By isolating Perforce behavior inside this wrapper, Blue Hole avoids
duplicating fragile command-line logic throughout the addon.