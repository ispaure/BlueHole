# Deluxe Object, Mesh and UV keymaps

Brief 04 starts from `deb10aa1ddfdce9fce6a299336ce71b008288d3a` on
`blender-5.2.2/alpha`. It uses the [01 ledger](deluxe-keymaps-baseline.md),
[02 runtime](deluxe-keymaps-runtime.md), and [03 handoff](deluxe-keymaps-category03.md).
The baseline reference is Blender 4.5.1 LTS.

| Category | Editable bindings | Full-side exceptions | Groups |
| --- | ---: | ---: | --- |
| Object | 14 | 12 | Mode Switching, Object Actions |
| Mesh | 10 | 26 | Modeling Shortcuts, Mesh Tool Shortcuts |
| UV | 15 | 15 | UV Selection, UV Tool, UV Action Shortcuts |

The audit covers 302 assigned ledger IDs and all eight UV transfers. The full
merged reference contains 92 distinct rows whose counts exceed both the stock
and preset/override-free controls. The other 218 are 130 stock-equal rows,
nine provider-inherited rows, 39 stock-side reductions and 40 rows absent from
both full and stock merged maps. The stock-side reductions and absent rows are
listed by ID in the [bulk receipt](../tests/fixtures/deluxe_keymaps_category04/bulk-catalog.json).
Ordinary assignments preserve inherited bindings and use the captured scope,
event, activation and explicit preset properties. Merged-only deltas use the
readable effective properties in the ledger.

The groups default on and use the existing global and category switches.
Category Preferences shows uniquely matched bindings in Blender's merged
keyconfig. After changing an event or property used for matching, continue
editing that binding in Blender Preferences under Keymap. Registration filters
the ordered declarations by group and appends them in reverse reference order
within each map, matching Blender's forward-prepend add-on merge. This preserves
per-map order among these declarations, including across UV feature groups.
The bulk comparison does not establish native order against separate categories
or inherited handlers.

All eight UV transfers are declared. UV Editor Q/RELEASE invokes
`wm.tool_set_by_id` with `name='builtin.select_box'` and `cycle=False`.
`space_type` is unset. It composes with the cycling Image Q/PRESS in 03.
The other transfers are the five modified or unmodified left double-click loop
and linked picks and the two right-press Tweak fallback selections in their
exact named Image Editor tool map. The local UV G action remains with 03 and
Screen G remains with 05.

## Exact exceptions

The [bulk receipt](../tests/fixtures/deluxe_keymaps_category04/bulk-catalog.json)
gives each affected ledger ID, event, map, target, position and known competing
IDs.

- **13 Knife modal tokens** need an applicable reversible modal capability.
- **13 macro rows** need runtime support for nested RNA properties, including
  Edit Mesh extrusion, loop cut, Poly Build and rip macros and the UV Rip tool.
  UV Stitch exposes a collection and requires separate runtime support.
- **15 unavailable operator schemas** cover four Cablerator rows,
  `mesh.prop_edit_pie` and ten UV Toolkit rows. Duplicate UV Toolkit occurrences
  are recorded with their counts.
- **Five Object Non-modal fallbacks** share the exact scope/event of an earlier
  reference row on 1, 2, 3, 6 or 7. The runtime rejects two active owners with
  the same scope/event. The catalog keeps the first reference row in each pair.
- **Two Tab replacements and Zen UV S/Press** overlap inherited stock actions.
  No existing proof context covers Object Non-modal Tab, Image Tab or UV S.
  The related UV S/Click hide row also depends on the press remaining unconsumed
  and is recorded with both press competitors.
- **Ctrl+V in 3D View** has an exact provider-inherited Paste Group occurrence.
  The extra reference occurrence has the same fields and the existing runtime
  has no applicable priority proof for its relationship with stock Paste Buffer.
- **Zen UV Shift+Ctrl+wheel down** follows the unavailable UV Toolkit cursor
  binding on the exact same event. Installing only the later row would promote
  it ahead of the reference winner. The distinct wheel-left binding is included.

The 39 stock-side rows identify stock events or occurrences absent from the
full merged reference. Additions on different events leave those stock paths
available. Generic row suppression is outside the accepted runtime capability.
No active-side-only row was treated as an effective merged shortcut. No
confirmed unclassified 04 rows need transfer to Other. The receipt flags
nearby Object and UV rows already assigned to 05 for integration.

## Verification and handoff

Brief 06's UV Cursor follow-up combines the reference's Set Cursor row
(`4e2dc6fd…`, merged position [51, 2]) and Translate row (`653400cb…`,
[51, 3]) into one `uv.bh_place_and_move_cursor` binding under UV Tool Shortcuts.
On unmodified middle press in the UV Cursor tool, it uses the event's region
coordinates to place the cursor, then invokes native Translate with
`cursor_transform=True` and `release_confirm=True`. The Transform catalog's
duplicate event claim was removed. Both full reference IDs and their mapping
remain in the 03 and 04 bulk receipts.

One confined Blender 4.5.1 LTS run (build `b0a72b245dcf`, base `9871112`)
matched the copied reference's cursor coordinates and native Translate modal
state at all eight click and drag observations. The merged map had one active
middle-press binding and no assignment conflict. The process exited 0 in
32.5 seconds, removed the disposable profile, preserved the payload hashes,
and stopped the watcher with zero owned or pending runtime resources.
The local receipt is
`test-results/deluxe-keymaps-category06/candidate-uv-cursor-combined.json`.

The portable bulk check exercises the normal category registers and compares
every emitted row with the 01 ledger and explicit preset properties. It compares
merged per-map order, preference group filtering, release, and coverage
against the 03 transfer and baseline occurrence links.

For 06's combined smoke, use Object Non-modal 1 (Edit Mesh Vertices), middle
mouse in the active Mesh Bevel tool, and UV Q on both phases of two successive
cycles. Observe Box on release using the direct noncycling Box control in the
Image Editor, and exercise the UV selection toggle with a double-click pick or
the right-press Tweak fallback in the applicable tool state. The copied
reference's earlier strict preservation failure and its inconclusive Box
direct-control result remain in the 03 receipt. The original catalog pass used
portable checks. The native follow-up above covers the UV Cursor gesture.

### Object and Mesh native follow-up

In Blender 4.5.1 LTS (`b0a72b245dcf`), middle mouse in the active Mesh
Bevel tool started native Bevel. Moving and releasing increased the cube's
vertex count from 8 to 24 and ended the modal operation. Disabling and
re-enabling Mesh Tool Shortcuts removed and restored its binding.

The [4.5.1 viewport handler order](https://github.com/blender/blender/blob/v4.5.1/source/blender/editors/space_view3d/space_view3d.cc#L336-L403)
puts Object Mode before Object Non-modal. The old `BH_Keymaps.py` preset
supplied its own Object Mode map without the stock collection-number
bindings. A disposable replay activated that preset with factory user
preferences and confirmed that `1` entered vertex Edit Mode. Switching to
the stock Blender base restored all eight stock collection bindings. The
initial Deluxe replay on that base confirmed that disabling only the stock
`1` binding was sufficient to restore vertex Edit Mode.

Deluxe now also registers a matching Object Mode item when an Object Non-modal
assignment uses an unmodified number press for a native command that enters a
mode. Blender prepends that item within Object Mode. The original assignment
continues to dispatch in other modes, and Blender's native command can pass
through to the collection shortcut when the target mode is incompatible.
This rule follows the assignment's current settings, including when it is
recreated under a new ID. The section switch removes both items. `4` returns
to Object Mode from Edit Mode and still selects collection 4 in Object Mode.
The replay covered `1` and `2` on a mesh, `3` on an armature, `4` from Edit
Mode, `5`–`8` on a mesh, and stock collection behavior with `3` on a mesh,
`4` in Object Mode, `Shift+1`, and `1` with the section off. See
`test-results/deluxe-keymaps-category04/mode-numbers/readback.json`.
