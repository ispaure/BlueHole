# Deluxe keymap profiles

Configured Deluxe reads [deluxe-defaults.json](../keymaps/deluxe-defaults.json)
on the built-in Blender preset. The catalog preserves source registration order
and feature grouping from cutover `fa7891a`. It contains 795 assignments across
10 categories and 29 sections. Four Navigation assignments record intentional
precedence changes for otherwise stock-equivalent rows. The reference ledger is
`deluxe-baseline-2026-11-12-v1`. Untouched Blender and add-on bindings are inherited
from the current keyconfig. The reference captures remain verification evidence.

Version 1 separates categories, sections, events, commands, assignments and
suppressions. An assignment joins one event and one typed command in a full map
scope. Its order controls runtime precedence. Category and section order is for
editor display. Use the stable IDs as references. Existing feature IDs, shipped
provenance, the Save As section and its bindings, and preference switch paths are
code-managed. Commands with different property values retain distinct IDs.
Menu, tool and context routes, Blue Hole operator behavior, and provider-managed
fields are read-only. The resolver exposes Blender RNA labels, types, defaults,
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
| Edit a shared event or command | `draft.update(table, id, **fields)` |
| Edit one assignment's event or command | `id = draft.clone(table, assignment_id)`, then update the clone |
| Create, rename, reorder, move or delete | `draft.put()`, `draft.update()`, `draft.delete()`, `draft.add_assignment()` |
| Inspect live binding candidates | `deluxe_resolver.binding_candidates(source_role, map)` |
| Stage or retarget a rule from a selected row | `draft.stage_suppression(section_id, map, item, source_role, replacement=command_id, id_=rule_id)` |
| Validate or commit | `store.validate(draft)`, `store.apply(draft)` |
| Discard or reset a draft | `draft.discard()`, `draft.reset()` |
| Reload a file and invalidate older drafts | `store.reload()` |

The preview separates a stored choice from eligibility under the current preset
and preference gates, native registration, command availability and active state.
It reports exact event collisions in the same map scope and exposes current
runtime diagnostics. A draft preview's registration status describes the live
session. The preview does not predict Blender's context-dependent dispatch.
Reusing a command can change all of its assignment uses. Cloning keeps a
single-assignment edit isolated.

A selected inherited source records its exact event, target, typed effective
properties, scope and keyconfig role. The matcher reports missing or edited
targets, ambiguous matches, and unsupported capabilities. A selection from the
merged user keyconfig can resolve to a unique inherited source. A user-only
binding can be stored for review, and the runtime reports it as unsupported.
A supported replacement uses the existing context-specific ordinary or modal
path and withdraws on release. A suppression without a replacement is stored
with an explicit unsupported diagnostic. This covers a UI that lets an artist
stage and inspect a choice while the generic native disable capability remains
open.

## Persistence and recovery

Apply validates the draft, compares the in-memory and on-disk revisions under
the shared file lock, installs and verifies the candidate runtime, and then
publishes the sparse overlay atomically through commonUtils. A failed install or
prepublication write restores the committed runtime. An interrupted process
restarts from the last published overlay. An unreadable overlay recovers the
known-good in-session profile, recovery copy or shipped defaults and exposes a
diagnostic. The original file is retained until the next explicit Apply. The
recovery copy is refreshed after successful publication.

Compatible catalog updates keep existing IDs and merge the saved fields over
new defaults. This includes disabled categories and sections. Unknown versions
and incompatible bases trigger recovery. Schema and ID changes that would
invalidate saved references require a future explicit migration. Native
Preferences changes remain Blender-managed. The existing Deluxe reset button
restores its Blender preference switches. The profile API's draft reset restores
the shipped profile and takes effect on Apply.

The portable catalog test uses one digest of the ordered pre-conversion groups,
scope, events, command properties and active state. Category 03–05 comparison
tests retain the reference reconciliation and exception evidence. Brief 07's
modal, provider, SpaceMouse and in-process Read Preferences gaps carry forward.
