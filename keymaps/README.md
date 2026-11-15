# Deluxe keymaps

For artists and keymap authors, start with the
[keymaps user guide](keymaps_user_guide.md).

[`deluxe-defaults.json`](deluxe-defaults.json) is the master for
[eleven section files](deluxe-defaults-sections). `deluxe_catalog.py` assembles and
validates their assignments, commands, events, categories and sections, and
publishes recoverable multi-file saves. Each binding owns its command record. Shared input records and unused legacy
commands stay in the master. Older shared commands become independent on load
and are persisted on explicit save. There is no second Python shortcut
catalog. The required Save As bindings also come from JSON before the user
configures Deluxe and while the Deluxe master switch is off.

The runtime has explicit boundaries:

| Layer | Responsibility |
| --- | --- |
| `descriptors.py`, `deluxe_schema.py` | Immutable requests and pure catalog validation; no Blender import |
| `catalog_plan.py`, `catalog_changes.py` | Compile ordered features and identify affected dependencies |
| `deluxe_resolver.py`, `provider_policy.py` | Live RNA, availability and reviewed provider capabilities |
| `profile_draft.py`, `profile_storage.py` | Detached edits and versioned personal three-way overlays |
| `deluxe_profiles.py`, `preview_state.py` | Transaction coordination and cached editor read model |
| `registration.py` | Execute context-preserving plan deltas and own temporary stock adjustments |
| `keymap_utils.py`, `default_bindings.py` | Native ownership, readback, independent disables and cleanup |
| `keymaps_register.py` | Main-thread lifecycle, bounded reconciliation and the unload barrier |

Normal saves go to Blender's `CONFIG/bluehole/keymaps.json`, outside the addon.
Updates merge new defaults with personal choices and report overlapping edits.
**Keymap Settings → Edit Shipped Defaults** explicitly enables catalog authoring.
Regenerate `factory-defaults.json` with `python Scripts/keymap_inventory.py
--write-factory keymaps/factory-defaults.json` when publishing changed defaults;
the portable suite rejects a stale factory snapshot.

Draft changes preview immediately; Save publishes, Discard restores the saved
catalog. Boolean edits reuse validated metadata; structural edits validate the
schema and changed RNA before applying. All edits retain order within affected
native contexts. The runtime never installs or stamps a saved `userpref.blend`.
Disables are independent rules: an unavailable addition cannot turn its source
back on. UI menu actions stay in `actions/` and declare no shortcut bindings.

`dispatch-chains.json` records 39 reviewed chains and their semantic signatures.
Its evidence level is structural order, not a claim that every provider dispatch
was tested. Changes to command, scope, input or member order revoke an exemption.
Wildcard/modifier overlap hints are informational. Unknown native schemas and
unproved replacements remain pending rather than guessing a source.

See the [editor guide](../docs/deluxe-keymap-editor.md),
[profile API](../docs/deluxe-keymap-profiles.md) and
[runtime contract](../docs/deluxe-keymaps-runtime.md) for details. The older
category receipts document migration evidence; their programmatic registration
modules have been retired.
