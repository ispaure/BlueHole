# Deluxe Sculpt, Pipeline, Pie and Other keymaps

Brief 05 starts at `4d5162b92c762235e655f99b97227bdfec8cb905` on
`blender-5.2.2/alpha`. The accepted evidence is
`deluxe-baseline-2026-11-12-v1` from Blender 4.5.1 LTS. The
[bulk receipt](../tests/fixtures/deluxe_keymaps_category05/bulk-catalog.json)
links the catalog, exceptions and retained stock reductions to the exact 01
ledger IDs. Catalog records carry category, group, full reference map and item
indices, and property source. Exception records add a reason and related row
IDs where applicable.

| Category | New bindings | Existing reference bindings |
| --- | ---: | ---: |
| Sculpt | 37 | 0 |
| Pipeline | 1 | 2 |
| Pie | 5 | 11 |
| Other | 430 | 0 |

Of 3,175 assigned IDs, 1,021 have more full merged occurrences than both
stock and the preset/override-free control. The catalog implements 473 of
those IDs and records 548 exceptions. Two implemented Quadriflow shortcuts
each omit one duplicate occurrence. The remaining IDs comprise 566 stock-equal,
175 provider-inherited, 1,111 stock reductions and 302 absent from both full
and stock merged maps. The existing routes in the table come from the
provider-inherited rows owned by Blue Hole.

Sculpt separates Tool Shortcuts, Brush Controls, Masking and Visibility, and
Sculpt Actions. The Tool group holds the captured unassigned Draw binding
(`NONE/PRESS`). The 15 legacy Sculpt brush-selection rows have unavailable
`paint.brush_select` RNA. Their exact brush choices could not be recovered
from the preset, and there is no authorized translation to brush assets.
Sculpt stroke handlers and modal maps stay inherited. The receipt records
tool names in the baseline scope, including Blender 4.5.1's unavailable
`is_tool` readback.

Pipeline's optional Ctrl+Shift+E FBX export uses the Blender FBX exporter with
the captured preset arguments. Both Ctrl+Shift+S and Command+Shift+S invoke
`wm.bh_save_as_mainfile`. The full reference places those Blue Hole rows
before the corresponding `wm.save_as_mainfile` rows in Window. The existing
obligatory action keeps both shortcuts when optional Pipeline or the global
Keymaps switch is off. Existing Save As workflow tests cover new and existing
destinations with mocked Blender and source control. Native Save As and FBX
file output are part of the 06 smoke.

With the existing Keymaps and Pie switches enabled, Pie registers the 11
Blue Hole routes visible in the full reference, in reference-relative order
within each map. Eleven other Blue Hole routes were visible in the no-override
control and absent from the full merged reference. They remain available
under the independent Pie switch when the Deluxe catalog is off. The five
additional editor pies have their own switch within Pie. Unsupported third-party
pies retain exact exceptions.

Other retains each shortcut's native map, including editor, mode and named
tool maps. It includes residual editor commands such as the UV context menu
and Object Add Primitive middle-mouse inputs. The 03–04-owned category
sources stay outside this migration. New feature switches default on under
their existing master switches. Fresh Deluxe activation is the 07 handoff
already recorded by 03.

## Exact exceptions and 03 composition

- **195 active and 24 inactive rows** overlap active inherited events in the
  same native map. The accepted runtime proofs cover different selectors.
  A new active row could move ahead of an inherited handler. An inactive
  owned row cannot disable a live inherited handler.
- **155 operator RNA, 84 provider, 53 property, three event and five modal
  exceptions** require available operator or provider evidence, a readable
  schema, or a specific runtime capability. Examples include legacy Sculpt
  brush selection, reference-only Node Wrangler bindings, nested or collection
  properties and non-default hyper/TEXTINPUT events.
- **23 earlier-reference and four inactive shared-event exceptions** require
  ordering against another route or ownership of both exact events. The
  runtime can reject a second exact owned event. The receipt links the
  relevant competitors.
- **Screen G** `404d0973700b95f4354799748f01445ff8aefb0031509c88fa0c71647bdcfd2b`
  is the repeat-enabled Screen binding to `screen.repeat_last` under Other.
  03 owns the UV-local route. Check that G repeats one action in UV, W and
  Shift+W still work, and stock UV Translate returns with both features off.
- **View2D Shift-wheel** `b05ae052799f48555368862eefc12fabd26fb613a79bafdc3b6f1944de86d682`
  and `35f7ab776087679ae004a903fe4e0510bc264a6ab756d3efe624c84faa2c9925`
  record globally disabled scroll in the reference. 03's four-editor
  More/Less guards cover the supported contexts. Global suppression would
  remove outside-editor fallback.
- **Frames Up/Down** `34d2f9ada5856fe81d97c8cf38ca8f02c30624669e704641dbfc259709f4d1b1`
  and `9809f50232defd4f4e71f504ef4fa98049439335ad7b130a0ebe4746ca850345`
  remain stock reductions. 03's UV-scoped guard preserves the frame jump
  in other contexts.

## Behavior choices for unresolved overlaps

The receipt lists the exact native scope, event and competing row IDs through
the ledger. The capture establishes their order in the map. A user decision
is needed where a brief 06 smoke observation and existing evidence leave the
intended result unclear.

| Scope and shortcut | Reference routes in order | Decision if dispatch stays unclear |
| --- | --- | --- |
| Dopesheet / DOPESHEET_EDITOR / WINDOW, Ctrl or Command + Left/Right Arrow on press | `screen.frame_jump` then `anim.start_frame_set` or `anim.end_frame_set` (`502ad189…`, `95e7ce88…`, `bbc9743c…`, `c6122c47…`) | Does a press jump only, set the range only, or do both? If both, should the range use the original or the jumped-to frame? |
| Property Editor / PROPERTIES / WINDOW, Backspace on press | `object.modifier_remove`, legacy `object.gpencil_modifier_remove`, `object.shaderfx_remove`, then `constraint.delete` (`5c108921…`, `9172b5a8…`) | Should the control under the pointer select one removal, with the other actions available as poll fallbacks? |
| Property Editor / PROPERTIES / WINDOW, Ctrl or Command + D on press | `object.modifier_copy`, legacy Grease Pencil modifier copy and shader effect copy, then `constraint.copy` (`38f8a29e…`, `a67d0823…`) | Should the control under the pointer select what is copied? |
| Image Paint / EMPTY / WINDOW, right mouse release | Primary stencil translation (`69c6a9f8…`), then texture-paint context panel (`492b244c…`) | Should release open the panel only when stencil translation cannot run, or after a successful stencil action as well? |
| Node Editor / NODE_EDITOR / WINDOW, Shift+left mouse press | Extend node selection (`9ba89b05…`), then `node.link` (`73f53a2c…`) | Should a socket press start linking while a node-body press extends selection, or should selection also change when a link starts? |
| Preview Tool: Cursor / SEQUENCE_EDITOR / WINDOW, middle mouse press | `sequencer.cursor_set` (`52ccc6d4…`), then cursor `transform.translate` (`5ccac85b…`) | Should the same press position the cursor and start a drag, or should click and drag take separate routes? |

The catalog keeps supported distinct phases. For example the Sculpt
right-mouse click context panel and right-mouse release stencil route retain
their separate events. The explicit exceptions prevent guessing a combined
operator or promoting a later action over an earlier unavailable route.

## Verification and 06 handoff

The portable bulk check exercises the normal category registrars and checks
all 486 rows against the baseline. It checks exact scope, event, properties
and activation, the measured prepend model's reference-relative order
within each category and native map, and feature removal with inherited
sentinels present. Separate category registration can change relative order
between categories. The offline overlap check found no same-map literal event
overlap among emitted 05 rows and prior 03–04 declarations across categories.
Blender dispatch across handlers remains part of 06.

For the combined smoke, exercise Sculpt Shift-wheel brush size, middle mouse
in the active Box Mask tool, and Shift+right mouse for the Sculpt tool pie.
Use a disposable blend and a fresh destination for custom Save As, and
dismiss or export FBX to a disposable location. In Other, check Screen G in
an editor with known Repeat Last history and one scoped Outliner or Node
shortcut. Exercise the 03 View2D and UV arrow composition with its
outside-context fallbacks. The new category pass used existing captures and
portable checks. Blender 4.5.1 native dispatch, FBX file output and combined
toggle behavior await 06.
