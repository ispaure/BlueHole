# Deluxe keymaps

For artists and keymap authors, start with the
[keymaps user guide](keymaps_user_guide.md).

[`deluxe-defaults.json`](deluxe-defaults.json) is the master for
[ten section files](deluxe-defaults-sections). `deluxe_catalog.py` assembles and
validates their assignments, commands, events, categories and sections, and
publishes recoverable multi-file saves. Each binding owns its command record. Shared input records and unused legacy
commands stay in the master. Older shared commands become independent on load
and are persisted on explicit save. There is no second Python shortcut
catalog. The required Save As bindings also come from JSON before the user
configures Deluxe and while the Deluxe master switch is off.

`keymaps_register.py` coordinates startup, preference changes and cleanup.
`deluxe_profiles.ProfileStore` loads the catalog, creates drafts, and validates
and publishes **Save and Apply Changes** transactions. `deluxe_resolver.py`
converts enabled entries into runtime requests. `keymap_utils.py` owns those
requests, verifies native bindings, and safely withdraws only its own resources.
Bulk load/unload batches merged-keymap updates while retaining immediate updates
where a native readback proof needs one. `default_bindings.py` owns reversible
disables of unchanged Blender defaults, with exact identity/readback guards.

Category and section enable choices are part of the JSON draft, saved together
with assignments and commands. Drafts preview automatically in Blender; only
Save and Apply Changes writes the catalog, and Discard restores the saved state.
Blender preferences keep the Deluxe master
switch and first-activation marker. Installing a Blue Hole update replaces the
edited catalog. UI menu actions stay in `actions/`; they contain no shortcut
bindings or keymap registration methods.

See the [editor guide](../docs/deluxe-keymap-editor.md),
[profile API](../docs/deluxe-keymap-profiles.md) and
[runtime contract](../docs/deluxe-keymaps-runtime.md) for details. The older
category receipts document migration evidence; their programmatic registration
modules have been retired.
