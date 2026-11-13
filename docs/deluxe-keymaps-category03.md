# Deluxe Navigation, Selection and Transform

Brief 03 reconciles these categories against the accepted
[baseline ledger](deluxe-keymaps-baseline.md) and uses the existing
[reversible runtime](deluxe-keymaps-runtime.md). Category implementation and
native verification are in progress. View Framing, six UV selection additions, Circle Selection, the Gizmo scope correction and Q
PRESS declarations pass portable checks. Bounded native observations are recorded below;
they do not establish complete category parity.

## Base and reconciliation

The accepted comparison base is the built-in **Blender** keyconfig from
`stock-4.5.1`, Blender 4.5.1 LTS build `b0a72b245dcf` on macOS arm64. The category
manifest retains its exact keyconfig options and bundled source hashes. Industry
Compatible is a comparator. The development branch remains
`blender-5.2.2/alpha`; this evidence does not establish native 5.2.2 behavior.

The reference-profile fallback uses SEARCH for spacebar, TOOL for tool-key mode,
and enabled pie click-drag, whereas the accepted stock base uses PLAY, IMMEDIATE,
and disabled pie click-drag. These differences and the separate input preference
`invert_mouse_zoom` are comparison conditions. This category work does not
activate or persist those options.

The separate [category manifest](../tests/fixtures/deluxe_keymaps_category03/manifest.json)
and [reconciliation rows](../tests/fixtures/deluxe_keymaps_category03/reconciliation.jsonl)
account for all 1,032 assigned baseline IDs:

| Audit classification | Rows | Interpretation |
| --- | ---: | --- |
| Existing | 280 | 157 captured Blue Hole rows and 123 complete inherited provider rows |
| Base-equal | 160 | Same positive stock/full semantic occurrence counts |
| Reference-delta | 392 | 140 active full-side candidates and 252 stock-side change observations |
| Unresolved | 200 | 74 schema gaps, 123 absent in both merged controls, three attribution caveats |

Provider inheritance remains explicit on another 44 schema-gated rows. Source
declaration overlap and captured ownership do not prove effective dispatch. In
particular, 66 of the 157 captured owned rows are absent from the development
merged user capture and require targeted verification.

These fixtures are accountability and parity evidence. Production does not load
them to register the entire reference map. Unchanged stock/provider bindings
remain inherited. Confirmed effective reference customizations are authorized for migration relative
to the selected Blender base. Documentation is supporting evidence, not a separate
intent gate. Missing rows or changed positions alone do not establish a removal. The retained-order audit found no
inverted active literal-overlap pair involving these assigned rows. The unchanged
PRECISION token remains inherited despite its changed list position.

## View Framing declarations

View Framing now uses its existing Navigation subfeature toggle and displays its
bindings through the existing action UI. Five actions declare thirteen reviewed
non-stock bindings; each binding cites its accepted ledger row.

| Context/action | Inputs |
| --- | --- |
| 3D View: frame selected | F; Shift-Alt wheel up/right |
| 3D View: frame selected in all regions | Shift-F |
| 3D View: frame all | A; Shift-Alt wheel down/left |
| Image: frame selected | F; Shift-Alt wheel up/right |
| Image: frame all | A; Shift-Alt wheel down/left |

Actual invocation depends on editor/mode/tool handlers. In the accepted full
reference sample, A selected all objects even though a framing candidate existed.
The new declarations preserve that distinction for native verification. Existing
NDOF framing rows remain inherited. Older events are not removed by adding a new
event.

Existing movement/axis, More/Less and Q groups remain. Transform's Modal group
contains operator-launch shortcuts; its Gizmo group contains tool activation.
These are distinct from actual modal-token maps. Category/subfeature defaults
remain enabled while the standard master switch remains opt-in. Pipeline and Pie
retain their existing independent behavior; fresh Deluxe activation belongs to
brief 07.

## UV selection additions

The existing UV More/Less actions now also accept `]` to grow and `[` to shrink
selection, with key repeat enabled. The two exact ledger rows and the existing
Deluxe shortcut table support these alternatives. Their declaration links are
kept separate from the historical audit. All 52 existing wheel declarations
retain their semantics and order. Native bracket input grew four selected UV corners to nine and shrank four to one.

The coordinator approved a separate All/None feature for exactly four UV
bindings: Ctrl-A / Ctrl-Shift-A and their macOS Command aliases. Native Ctrl and Command variants selected all 64 UV corners or deselected all
four initially selected corners. Toggling this feature removed only its four rows,
restored them exactly, and preserved the other groups and foreign default rows. None is inherited from the selected Blender
base; Industry lineage for the Command aliases does not make them inherited
when Blender is selected. No other editor or mode is added by analogy.

## Circle Selection

Four exact reference inputs now use a separate Circle toggle: Shift-middle mouse
adds and Ctrl-middle mouse subtracts in the 3D View and UV Editor. The 3D inputs
retain `wait_for_input=True`; UV retains `False`. ADD/SUB properties, radius and
coordinates match the ledger, and the master remains opt-in.

The owned probe matched all four copied-reference selection effects. The actual
production runtime then selected/deselected the target object or four UV corners
without moving the view. Disabling removed only these four rows and restored
stock Shift-middle navigation; reenabling restored selection. Other category
rows and foreign source fields/order stayed unchanged. A production save/reopen
pair also preserved an edited Shift-F20 binding with radius 31 across immediate
save, feature toggles and a fresh process. The same pair preserved Framing F19.

## Ordinary candidate drafts

Twenty-one additional bindings are drafted in existing category modules and
verified against exact accepted scopes, events, targets and declared properties.
Nine are now accepted by coordinator-approved exact-context mechanism reuse,
bringing the implemented candidate count to 32. Twelve declarations remain draft.
Existing subfeature toggles control these drafts.
The seven axis/Local View production inputs produced their expected effects.
The first copied-reference run observed six matching effects, an unchanged first
Ctrl-F1 case, and a strict property-readability comparison failure. Those limits
remain explicit. Ctrl-F1 retains a related scheduled or integrated owner06 spot
check; no dedicated lifecycle rerun is required. The two UV arrow declarations
remain implemented but now have **blocking dispatch mismatches**: the actual
pre-adaptation production inputs left four UV corners selected, while copied-reference Up grew
four to nine and Down shrank four to one. Direct controls worked on both setups.
The accepted baseline has stock Frames Up/Down keyframe-jump rows that are absent
from the reference active map. A 13-observation isolated probe proved those
Frames rows win: arrows jumped from frame 5 to 10/1 without changing UV selection,
while the brackets changed selection and left frame 5 unchanged. Two UV-only
owned Frames guards then produced the intended UV effects and preserved inherited
keyframe jumps in the 3D View. Both removals restored exact source/merged maps;
reinstall restored UV selection. Collection order alone was not used to infer
the winner.

The approved production adaptation replaces the two ineffective local arrow
declarations with one editable Frames binding per arrow, targeting fixed UV-only
guards in the existing selection operator module. The existing More/Less feature
controls them; wheel/bracket declarations, View2D guard scopes and stock/global
rows are unchanged. The first actual production run passed ten effects, including
both arrows, both brackets and inherited outside-UV jumps under real Selection
identities. Its first release failed because the fixture-owned F23 input control
changed order relative to rebuilt owned Pipeline rows. Removing only that control
restored exact foreign identity/source/merged preservation. Cleanup then stopped
at a fixture completeness assertion, although the child exited and host cleanup
passed. Save/reopen was skipped. The revised fixture removes F23 at every matched
endpoint and completes addon shutdown before surfacing cleanup errors; the full
actual toggle sequence and representative saved-edit pair remain pending.

| Existing group | Draft inputs |
| --- | --- |
| Viewport Axis | Ctrl/Command F1–F3 absolute back/left/bottom views |
| Viewport Movement | Alt wheel in/out zoom |
| View Framing | Shift-I Local View |
| More/Less | UV up/down arrows; 3D Escape → Object Select Less |
| Q Tool Switch | Image, Image Paint, Vertex Paint and Weight Paint |
| Transform Gizmo | Image W/E/R tool cycling; UV T tool cycling |
| Transform Modal | Ctrl-Shift middle drag to move the UV cursor |

The 22nd ordinary candidate is exactly Image Paint Alt-A → UV Select All
(INVERT). The coordinator reserved `selection/selection_invert.py` and minimal
Selection wiring, but that feature remains unimplemented until native polling
and copied-reference dispatch prove support in **Image Paint**. The different
stock UV Editor Alt-A context is not a substitute.

The ordinary fixture separates stock observation, one exact owned probe at a
time, and production-source observation. Five bounded clusters cover all 22
IDs. The seven-handler fixture separately compares middle click, drag and
second-press drag, circle entry versus actual brush selection, Object subtract
and Mesh/UV shortest-path controls. The ordinary fixture now adds a native F23 Window delivery control before each
shortcut and skips unverified input; it retains direct operator effect controls.
Both fixtures check foreign source fields/order. The axis and handler subsets
have run. A wheel-zoom production/reference pair found no view change from either
synthetic WHEELIN/OUT event, although direct zoom changed distance from 10 to 12
or 8.33 on both setups. The positive keyboard control does not establish wheel
event delivery. Both wheel bindings remain unverified; a physical wheel/trackpad
witness belongs in integrated 06 if needed. The copied-reference strict cleanup
check separately failed on 192 property-readability changes, with row IDs/order
and all other fields unchanged. Protected inputs and host resource cleanup passed.
Other ordinary clusters remain pending.

The same UV pair observed no Ctrl-Shift-middle cursor movement in either setup.
Its direct control failed because JSON enum-flag lists were passed to RNA without
conversion to sets. The corrected fixture validates native enum-flag schema and
members using the accepted runtime rules, and captures press, initial motion,
second motion and release snapshots. These fixture changes are not yet natively
verified. The reference UV run also retained a strict 192-row readability
comparison failure; its arrow effects and that failure are reported separately.

## Verification and boundaries

Run the portable category checks with:

```sh
python3 -m unittest discover -s tests -p 'test_keymap_category03.py' -q
```

Forty-seven category checks currently pass. They cover exact assigned IDs and
comparison links, base identity, inherited order, declaration semantics, group
isolation and UI, Gizmo scopes, UV aliases, Q dispatch and box selection evidence,
Transform effects, corrected Selection controls, exact eight-row ownership
transfer, and honest partial native receipts. The affected runtime suite has 69
checks, including nine numeric-array/enum-flag schema checks; Pie has two checks.
The [native receipt](../tests/fixtures/deluxe_keymaps_category03/native.json)
retains 50 factory attempts and fourteen copied-reference attempts. A completed
observation is not a successful process if that process later crashes.
Repeated complete keymap/item snapshots are stored once by SHA-256 in this
receipt. `tests/keymap_native_evidence.py` expands them and verifies every
snapshot plus the complete expanded document before tests inspect it. No evidence
fields are dropped. Full sanitized per-run receipts and their hashes also remain
under ignored `test-results/deluxe-keymaps-category03/sanitized-native/`.

### Proven bounded behavior

- **Navigation:** Alt-left orbit, Alt-middle pan, Alt-right zoom, F/Shift-F and
  the four wheel framing directions changed measured view state. A selected
  objects in both the development fixture and copied reference. Four directional
  axis drags remained unchanged; middle-click front-axis worked. The copied
  reference also left the tested north-axis drag unchanged with Select and Box
  tools. A later controlled handler fixture established that copied-reference
  plain middle drag pans, while the exact owned addon probe rotates. Both rotate
  on second-press drag and do nothing on click followed by movement. This timing
  mismatch remains unresolved. Mesh shortest-path selection worked in both;
  Object subtract and UV shortest-path fixtures still need focused controls.
- **Q and tools:** The original CLICK event produced no wrapper invocation.
  Twenty owned PRESS probes established dispatch in Object, Mesh, Curve and
  Curves across absent, enabled, preference-off, disabled and reenabled provider
  states. The one-line production PRESS correction then passed all twenty cases
  without probe bindings. Object/Mesh selected X-Ray Box when available and
  enabled; all fallback cases selected built-in Box. Four corrected two-stage
  native drags selected the Cube or a mesh vertex using both provider and
  fallback tools. Earlier one-move drags selected nothing and remain inconclusive
  fixture attempts. No provider wrapper implementation changed.
- **Selection:** Both UV brackets and all four All/None aliases changed actual
  UV selection, with independent toggle preservation. Corrected Mesh and legacy
  Curve fixtures prove Shift-wheel grow/shrink. Curves, Lattice and Armature
  also changed selection. The Object parent/child grow case worked; the initial
  shrink case started from a child with no children and is not a valid control.
- **Transform:** W/E/R changed position, rotation and scale and recorded the
  corresponding Transform operators. Shift-W/E/R selected Move/Rotate/Scale.
  W still translated with Move active. Right-click drew the context menu and a
  face click changed the selected mesh face while Move stayed active. UV W
  translated and Shift-W selected Move. The controlled G comparison below
  establishes a separate reference Repeat Last behavior.
- **Runtime property repair:** Local commit `f2e8b94` validates recognized native
  numeric arrays/matrices and schema-gated enum-flag sets. Native Translate,
  Rotate, Resize, Image Pan and Clip Pan assignment, complete source/merged
  readback and release passed. Edited numeric/flag source rows survived release
  and were removed by the fixture owner. Wrong shape, unknown flags and lossy
  float readback were rejected. The typed Matrix setter preserves logical row
  order. Generic iterables/sets, pointers/collections and new runtime capability
  contexts remain unsupported. The earlier matrix transpose failures remain
  recorded.

### Remaining behavior and failed attempts

The first Dopesheet, Graph, Node and Sequencer Shift-wheel fixtures did not
change selection, despite successful direct controls. A corrected copied-reference
run added native Window/editor sentinels and an unmodified-wheel view control at
the same coordinates. All controls delivered, and **all eight reference selection
inputs then worked**, including contraction of five selected strips to three.
The earlier non-effects cannot establish a reference limitation.

That run's strict cleanup comparison failed because 89 operator-property entries
changed from `RNA_unavailable` to readable values. An offline comparison checked
26 maps and 1,366 items: scope metadata, item identity/event/active/order and all
previously readable properties were unchanged. Previously unreadable values
cannot prove complete preservation. The next recheck used a native Window primer
and two identical baseline snapshots with readable relevant operator properties.
Unknown entries dropped from 119 to 30 before the baseline. All eight selection
effects and input controls passed again, but cleanup made 87 entries unreadable
(85 Node Editor and two Window rows), raising unknowns to 117. Stored property
values and every other captured field/order remained equal; the strict comparison
still failed. The failure and unknowns are retained. The narrow next check must
capture immediately around input-row removal, keyconfig update and control-class
unregistration, then repeat the same readiness protocol after cleanup. It must
retain the immediate failure and require strict equality after settling.
The owned guarded View2D experiment produced all eight selection effects and
restored factory behavior when removed. A later 14-observation run used matching
Dopesheet context and readiness/update lifecycles at three endpoints. Both
releases preserved exact source and foreign merged snapshots; all ten relevant
targets and four foreign sentinels were readable. Forty other unknown entries
remained identical, so their underlying property values remain unproved.

The coordinator approved the production counterpart in three files: two fixed
More/Less operator classes, ordered operator lifecycle wiring and two exact
View2D Shift-wheel declarations in the existing More/Less feature. Its polls
accept only WINDOW-region Dopesheet DOPESHEET, Graph FCURVES, Compositor nodes
with an edit tree and Sequencer SEQUENCER, plus the underlying operator poll.
Portable tests verify rejected contexts and poll-failure pass-through. Production
dispatch reached five passing selection effects before its 75-second host limit:
Dopesheet More/Less, Graph More/Less and Node More, with positive input controls.
The host terminated and cleaned up the owned child; final in-process cleanup and
preservation checks were not reached. The remaining cases, unrelated-editor
pass-through, feature toggles and saved-edit controls remain pending. A 150-second
ceiling is prepared from measured case times. Read-only callback profiling now
covers only the shortcut dispatch interval; its timing benefit is unmeasured.
The next production run reached all eight selection effects in 50.5 seconds.
Its first release failed strict source equality only on two internal IDs for
unrelated Blue Hole Pipeline Save As registrations; all other source fields and
all foreign merged snapshots matched. The shared refresh recreates those owned
rows. The failed receipt and interrupted in-process cleanup remain recorded; the
owned child exited and host resource cleanup passed. A bounded fixture revision
now requires live runtime ownership and registered-pair provenance for exactly
those two generations, compares their semantic fields/order separately, and
keeps every foreign identity strict. The corrected production selection run then
passed all 14 observations, both
toggle cycles and both matched releases, with live ownership proven for exactly
those two recreated Pipeline rows. The outside-context run completed 20
observations and two more exact releases. Image View, NLA, Timeline and nodes
without a tree had positive controls and rejected the selection guard. File
Browser received the keyboard control but its unmodified wheel did not move the
view; Sequencer Preview used hidden-region coordinates [0,0] and sent its control
to the status bar. Those historical observations remain inconclusive. Both
children completed native unregister/watcher shutdown and host resource cleanup.
The corrected File Browser/Preview run then passed eight observations with visible
region coordinates and owned scrollable File Browser content. Every Window control
arrived in its expected WINDOW or PREVIEW region, unmodified wheel changed the
view, and Shift-wheel changed the view without invoking selection or changing it.
Both matched releases preserved foreign identities/fields/order/readability;
native and host cleanup passed.
Existing horizontal declarations stay unchanged. Exact
owner-05 inactive scroll rows stay with that owner for global reconciliation.
Mask's corrected fixture and Particle selection remain unverified.

The controlled UV G comparison now distinguishes behavior. Both configurations
completed a nonzero rotation through a temporary native F23 control, recorded
`TRANSFORM_OT_rotate` as the last operator, and removed that control before G.
Development G then started a fresh translation. Reference G immediately repeated
the rotation, and subsequent mouse motion did not translate. This is consistent
with the owner-05 **Screen G → Repeat Last** row; the earlier W-then-G sequence
could not distinguish repeat from fresh translation. Ownership is settled: 03
owns the exact local UV Translate selector and UV precedence, 05 owns Screen
Repeat Last, 04 verifies UV composition and 06
integrated parity. One isolated UV Editor G/PRESS → Repeat Last assignment through
the existing runtime passed seven native cases: known Rotate and Translate repeat
exactly once immediately, subsequent motion does not start a new transform, empty
history fails Repeat Last poll and falls through to Translate, W/Shift-W remain
effective, and remove/reinstall restores the expected G behavior. Both releases
preserved all captured source and foreign merged fields/order/readability.

The subsequent immediate-save run edited only the owned merged G row to inactive
F20, saved it, and removed the owned source. Strict snapshot equality failed
solely because the merged UV map's aggregate `is_user_modified` changed from false
to true. All 105 foreign UV rows, their item-level flags/values/order/readability,
and default/active/addon maps matched. The failed receipt is retained, reopen was
skipped, and the saved binary was removed. A prepared follow-up separates that
aggregate marker from exact foreign-row/source comparisons, proves the intended
owned source and user override, and binds a fresh-reader expectation to the saved
preference hash. Brief 02 establishes native saved-diff restoration but does not
explicitly test this aggregate marker.
The next writer attempt stopped at a compound immediate post-save assertion
using the previously held merged RNA wrapper. It did not retain the individual
field values, so it does not identify a runtime defect. Reopen was skipped and
the only created input binary was removed. The revised fixture records each
field before/after save, performs an explicit keyconfig update, reacquires the
exact merged row and then tests the recomputed metadata. It preserves the
immediate-save timing and exact owned-source/foreign comparisons.

The revised writer and fresh reader both passed. The saved wrapper had been
reused for an unrelated empty/ESC item; exact reacquisition recovered the intended
F20/PRESS inactive, repeat-enabled user edit. The original owned G declaration
stayed unchanged, the override survived two releases/reinstalls and a fresh
process, and all foreign source/item fields/order/readability matched. Only the
separately recorded aggregate marker reflected the owned saved edit.

Production now declares one UV Editor/EMPTY/WINDOW G/PRESS binding to
`screen.repeat_last`, with repeat enabled, under the existing Transform Actions
toggle and editable keymap UI. Modal W/E/R and Gizmo controls remain independent.
The public Transform action catalog includes the action. The stock G entry and
global Screen row are unchanged. Portable checks cover the production identity,
toggle and existing controls. Actual production dispatch now passes nine native cases using its real
`legacy:Transform` identity: the repeat/fallback cases, W/Shift-W with Actions
on and off, two installs and two exact releases. Source and foreign merged
snapshots match, and unrelated Transform declarations remain unchanged.
Production immediate save and fresh reopen now pass under that actual identity
as well. The inactive F20 repeat-enabled user override survived both processes
and four releases/reinstalls, with exact original source and foreign data proof.
The hash-bound preference file and expectation manifest were removed after the
reader. Composed owner04/05/06 parity remains open.

Earlier G controls lacked repeat history, used stale BMesh data, had no rotation
effect, or ended in a crash. Those attempts remain inconclusive. The latest
successful controls establish the actual operation through native effects/history;
they did not capture the temporary row's exact merged snapshot. Future control
failures must distinguish merged-row admission from physical input delivery.

Earlier Q instrumentation crashed before any Q/provider observation, and its
crash text was removed before retention. The later reference failure also lost
crash text during resource cleanup; retained launch logs and process failures
remain explicit. Both launch paths now retain owned crash files before cleanup.
The reference wrapper records PID, exit status, launch-log hash and retained
crash hashes, including nested temporary paths. Four synthetic retention and
retention-failure checks pass across both launchers without native launch. This repair does not
recover the earlier missing crash text.

The category GUI driver is prepared for registration, navigation, Q, Selection
and Transform observations. It requires the coordinated desktop-input slot and
explicit app/provider inputs. It reuses the accepted isolation recipe: five user
resource redirects, disabled preference autosave, network denial, write
confinement and disposable minimum-version adaptation. Original app/profile and
provider sources remain read-only. Process, source hash, protected-input and
cleanup receipts stay under ignored `test-results/deluxe-keymaps-category03/`.

Required native work includes the two implemented UV arrow dispatch blockers,
the corrected cursor control, Image framing/pan/zoom, the axis reference readiness
check, remaining ordinary clusters,
and focused middle-mouse/subtract and modal/tool probes. G behavior and production persistence are accepted; composed UV/global
parity remains. Existing proofs need no broader
rerun unless affected source changes.

Of 140 active full-side delta candidates, 32 have implemented declarations:
thirteen framing, six UV selection additions, four Circle inputs and nine
ordinary declarations accepted through explicit mechanism reuse. Exactly eight UV-specific Q,
loop/linked and Tweak fallback rows were explicitly transferred to 04. The
remaining 100 stay with 03: 13 ordinary candidates (12 declarations still draft), 70 currently
unsupported or unproved handler/modal/tool/replacement cases, 13 observations of
active-role absence, and four conflicting bindings. Active-role absence alone
does not prove unavailability. Each has row-specific next steps in the refreshed
reconciliation proposal. The two implemented UV arrow rows additionally remain
blocking dispatch reconciliation items. These counts describe disposition, not native parity.
The original 01 ledger is unchanged. Generic UV More/Less, All/None and the W/G
boundary remain with 03; Mesh loop and context-menu declarations retain their
other owners while this brief tests relevant interactions.

Generic suppression/per-item veto is unsupported. Existing ordinary/modal proof
contexts do not automatically authorize these category contexts. Any required
new capability returns to the coordinator with the exact ledger selector,
native result and bounded proof proposal. Owned disposable probes may test
precedence without mutating inherited item fields or bypassing production
capability checks. Industry lineage neither makes a candidate inherited under
Blender nor supplies a reason to defer a confirmed customization. The shared
runtime change remains limited to the approved property normalization repair;
accepted 01/02 fixtures are unchanged. Required gaps keep brief 03 open.

### Shared persistence and remaining work

`tests/blender_keymap_category03_persistence.py` verified the editor and combined
Circle/Framing save/reopen pairs using actual category toggles, exact runtime
ownership, immediate save, merged-item reacquisition and source-bound input
manifests. Complete matched snapshots retain every foreign row; only a proven
owned saved edit can explain its map-level modified flag. All four processes
passed: the inactive editor Shift-F18 override, Framing F19 and Circle Shift-F20
with radius 31 survived immediate saves, off/on cycles and fresh processes.
Original declarations and foreign source rows/order/readability were preserved;
saved preference inputs and their manifests were removed after verified readers.
The corrected File Browser/Preview control cluster also passed using owned
scrollable content and visible-region coordinates.

The ignored mechanism plan partitions all 100 remaining IDs into ordinary
declarations (13), modal events (33), middle-mouse tool dispatch (19), selection
replacement/fallback (22), navigation timing/context (5), release confirmation
(4), and conflicting reference intentions (4). Registration/persistence proof
can be reused where source, selector and context warrant it. Nine ordinary rows
were explicitly approved for reuse. Ctrl-F1 retains its spot check; the two UV
arrow checks exposed dispatch mismatches and now require a fix.
A source-bound single-step launcher retains the exact wheel comparison and shared
lifecycle/control commands. Another native allocation is required for further
families; the inconclusive wheel pair will not be repeated unchanged.
