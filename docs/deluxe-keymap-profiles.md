# Deluxe keymap profiles

Configured Deluxe reads the [master file](../keymaps/deluxe-defaults.json) and its
[ten section files](../keymaps/deluxe-defaults-sections) on the built-in Blender preset. The catalog preserves source registration order
and feature grouping from cutover `fa7891a`. It contains 803 assignments with independent command records across
10 categories and 46 sections. Four Navigation assignments record intentional
precedence changes for otherwise stock-equivalent rows. The Object Modes
assignment for `3` enters Face Select on meshes and Pose Mode on armatures.
It uses the same Object Mode registration rule as the other mode shortcuts.
The reference ledger is `deluxe-baseline-2026-11-12-v1`. Untouched Blender and add-on bindings are inherited
from the current keyconfig. The reference captures remain verification evidence.

Version 1 separates categories, sections, events, commands, assignments and
suppressions. An assignment joins one event and one typed command in a full map
scope. Its order controls runtime precedence. Category insertion order and section `order` values determine
editor display. Each binding or replacement rule owns its command record, even
when its values match another command. Use the stable IDs as references. Existing feature IDs, shipped
provenance, and the Save As section and its bindings are
code-managed. Commands with different property values retain distinct IDs.
An ordinary command may have an optional `label` for its displayed name.
New ordinary commands accept operator IDs, validated against live RNA when available.
Unavailable operators remain saved but unregistered. An empty operator ID represents
an unassigned new binding and generates no runtime request.
The binding editor chooses operators directly and has no Commands tab. Commands
are stored with their owning section. Shared input records and unused legacy
records remain in the master file. Adding a binding only updates the draft until
Save and Apply Changes.
Menu, tool, context, Blue Hole and provider operator properties can be edited when
their RNA is available. Retargeting a provider binding drops the old provider
metadata and starts with the new operator's defaults. Required bindings remain
read-only. The resolver exposes Blender RNA labels, types, defaults,
allowed enum identifiers, flags, array dimensions and limits for editable fields.
Call `store.resolver.describe_command(command, include_unset=True)` to include
settings available from the known operator's live RNA. Values inherited from
Blender stay absent from the profile until explicitly set.

## Editor API

Use [keymaps_register.deluxe_profile()](../keymaps/keymaps_register.py) from the
Blender main thread after configuring Deluxe. The [editor fixture](../tests/fixtures/deluxe_keymaps_category08/editor.json)
has a shared input across two scopes, Boolean command variants, a disabled
category and a provider command.

| Operation | API |
| --- | --- |
| Browse stored values and defaults | `store.snapshot()`, `store.defaults()` |
| Start an edit | `draft = store.begin()` |
| Inspect a draft | `draft.snapshot()`, `store.preview(draft)` |
| List affected assignments | `draft.uses('events', event_id)` or `draft.uses('commands', command_id)` |
| Edit a binding’s command | `draft.update("commands", command_id, **fields)` |
| Edit one assignment's input | `id = draft.clone('events', assignment_id)`, then update the clone |
| Create, rename, reorder, move or delete | `draft.put()`, `draft.update()`, `draft.delete()`, `draft.add_assignment()` |
| Inspect live binding candidates | `deluxe_resolver.binding_candidates(source_role, map)` |
| Stage or retarget a rule from a selected row | `draft.stage_suppression(section_id, map, item, source_role, disable=True, id_=rule_id)` or `replacement=command_id` |
| Preview without writing; restore saved runtime | `store.preview_draft(draft)`, `store.cancel_preview()` |
| Validate or commit | `store.validate(draft)`, `store.apply(draft)` |
| Discard or reset a draft | `draft.discard()`, `draft.reset()` |
| Reload a file and invalidate older drafts | `store.reload()` |

The preview separates a stored choice from eligibility under the current preset
and Deluxe master switch, native registration, command availability and active state.
It reports exact event collisions in the same map scope and exposes current
runtime diagnostics. A draft preview's registration status describes the live
session. The preview does not predict Blender's context-dependent dispatch.
Assigning an already-owned command creates an independent copy immediately.
Deleting a binding removes its owned command. Legacy shared references are split
on load with stable IDs and identical values; the next explicit save writes the
migration even when no other edits were made. Unused legacy records are retained.
Undo restores the binding and its command together.

A selected inherited source records its exact event, target, typed effective
properties, scope and keyconfig role. The matcher reports missing or edited
targets, ambiguous matches, and unsupported capabilities. A selection from the
merged user keyconfig can resolve to a unique inherited source. A user-only
binding can be stored for review, and the runtime reports it as unsupported.
A supported replacement uses the existing context-specific ordinary or modal
path and withdraws on release. Rules with `disable: true` temporarily disable exact non-modal Blender or add-on shortcuts
through `default_bindings.py`. The original source, item identity, full snapshot
and inherited merged row are checked; user-modified rows are rejected. Unload,
Discard or disable restores only the same unchanged item. Unreadable restoration
is retained for retry; changed or replaced source rows are preserved. Rules
without `disable` or a replacement remain review-only, including older saved
review targets.

The existing registrar watcher revisits pending disables in bounded batches.
Provider removal retires its old source identity; a new matching source can be
disabled after enable/reload. An in-place native edit is preserved and is not
repeatedly disabled. Add-on merged IDs may differ from source IDs, so their
complete unique merged snapshot is checked instead. No user-keymap delta is
created. Artist-created rules always capture full effective properties.

The legacy migration adds 24 current Blender-default rules and 28 add-on rules.
The audit fixture records all 125 old disabled entries and their decisions.
Imported add-on rules can set `explicit_properties: true`: the old export only
stored explicitly configured properties. These match the complete context and
event plus all those properties against one unique add-on source, then capture
its complete current snapshot before mutation. This mode is never inferred for
new artist-created rules. A missing, ambiguous, edited or unsupported source
remains pending; neither a different shortcut for the same operator nor a
user-only shortcut is substituted.

The editor calls `preview_draft()` after each staged change. It validates and
installs the candidate with rollback to the previous working runtime on failure.
The saved snapshot and files do not change. Master/preset refreshes use the live
candidate, while `cancel_preview()` restores the committed catalog. Closing the
addon drops the preview. Discard and Reload explicitly restore the saved setup.

## Persistence and recovery

**Save and Apply Changes** saves the master and section files in the active Blue Hole
installation. With the Logistics **Local** source, the installation links to
the checkout, so the edit appears in Git. With **GitHub**, the edit goes into
the preset's installed Blue Hole copy. The next Blue Hole update installs its
shipped catalog. Existing per-preset override files stay on disk for reference
and the editor now loads the bundled catalog.

Category and section `enabled` values live in that same JSON catalog. They are
staged and saved with assignments and commands, and updates replace them too.
Legacy category/section preference switches no longer gate the catalog; optional
`switch` paths in older catalogs are ignored. Blender preferences retain the
Deluxe master enable switch and the internal first-activation marker. Native
Blender keymap customizations remain Blender-managed in `userpref.blend`.
The editor displays an update warning above the bindings. The former saved-preferences
backup and feature-switch reset commands have been removed because they did not
manage the JSON catalog.

The master contains metadata, a `section_files` mapping, and input records used
across top-level sections, plus unused records. Each `deluxe-defaults-sections/<category-id>.json`
contains the category definition, its subsections, assignments, default rules,
and commands/events used only there. IDs remain stable when a binding moves;
input records move into or out of the master automatically on save. Labels can
change without renaming files. The storage format is version 1, independent of
the logical schema version. Legacy single-file catalogs migrate on explicit save.

Add a top-level section by adding its stable ID and canonical relative file path
to `section_files` and a matching section document. New subsections belong in
that file's `sections` table. Deleting a subsection requires moving or deleting
its assignments/rules; dangling references are rejected. The UI only deletes
empty subsections. Removing a top-level section from the master removes it from
the next reload; its now-unreferenced file is ignored. A subsequent editor save
retires only files owned by the previously loaded catalog. Unrelated files are
preserved. Active tabs fall back when their selected entry disappears.

Use **Keymap Settings → Validate and Reload JSON Files** after external edits.
Parsing rejects duplicate keys and non-JSON numbers as well as malformed syntax.
Syntax errors show `file:line:column`; record errors identify the file, record ID,
and line where available. Validation covers required fields, types, versions,
unique IDs/order, section membership, and all command/event/section references.
File paths are restricted to the catalog's section folder, without symbolic links.
The working setup remains active after a failed reload; the diagnostic stays
visible. The files are left untouched until an explicit save.

Apply validates the entire draft and fingerprints the master and section files
under the shared lock; external edits block a stale save. It installs/verifies
the candidate runtime, writes a complete recovery snapshot and a transaction
marker, publishes changed section files, and publishes the master last. Failed
publication rolls back the files and runtime. After an interrupted process the
marker prevents loading a partial generation; the validated recovery snapshot is
used instead. **Save Recovered Profile** repairs the catalog explicitly. The
recovery copy is refreshed after success. No partial catalog is installed.

Unknown versions and incompatible bases trigger recovery. **Reset Draft** restores the catalog loaded when
the editor opened, previews it, and writes it only on Apply.

The portable catalog test uses one digest of the ordered pre-conversion groups,
scope, events, command properties and active state. Category 03–05 comparison
tests retain the reference reconciliation and exception evidence. Brief 07's
modal, provider, SpaceMouse and in-process Read Preferences gaps carry forward.
