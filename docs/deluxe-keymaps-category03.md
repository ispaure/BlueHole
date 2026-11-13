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
Twelve are now accepted by coordinator-approved exact-context mechanism reuse,
bringing the implemented candidate count to 35. Nine declarations remain draft.
Existing subfeature toggles control these drafts.
The seven axis/Local View production inputs produced their expected effects.
The first copied-reference run observed six matching effects, an unchanged first
Ctrl-F1 case, and a strict property-readability comparison failure. Those limits
remain explicit. Ctrl-F1 retains a related scheduled or integrated owner06 spot
check; no dedicated lifecycle rerun is required. The two UV arrow declarations
had dispatch mismatches before the approved handler adaptation: the actual
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
passed. Save/reopen was skipped. That failed attempt remains in the receipt.
The revised fixture removes F23 at every matched endpoint and completes addon
shutdown before surfacing cleanup errors. Batch24 then passed all 13 actual
production observations, two installs and two matched releases. Foreign source
identities, fields, order and readability stayed exact; only the two proven owned
Pipeline generations were compared separately. The inactive F17 repeat-enabled
override survived immediate save, feature toggles and a hash-bound fresh process,
with the declared source unchanged. All three children completed native watcher
and ownership cleanup; saved inputs and disposable resources were removed.
The two arrow dispatch blockers are resolved at the recorded production hashes.
Owner05 retains global Frames behavior; owner06 still verifies composition.

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
second motion and release snapshots. Batch25 ran that cursor-only comparison.
Exact source/merged admission and Window delivery passed on both configurations;
all four phases left the cursor, UV coordinates, selection and view unchanged.
The direct control now polls true and returns FINISHED with a nonzero value, but
still moves nothing. Completion without an observable effect is not a positive
cursor control. The row remains unresolved, with no parity or unavailability
claim and no identical rerun planned. Production preservation and shutdown passed;
the reference again failed the strict comparison on 192 readability changes.
Both children exited, all owned resources were removed and protected inputs were
unchanged. A future different probe needs a basic cursor-state control, such as
supported cursor placement, separated from evidence that translate moves it.

## Verification and boundaries

Run the portable category checks with:

```sh
python3 -m unittest discover -s tests -p 'test_keymap_category03.py' -q
```

One hundred and one category checks currently pass. They cover exact assigned IDs and
comparison links, base identity, inherited order, declaration semantics, group
isolation and UI, Gizmo scopes, UV aliases, Q dispatch and box selection evidence,
Transform effects, corrected Selection controls, exact eight-row ownership
transfer, and honest partial native receipts. The affected runtime suite has 69
checks, including nine numeric-array/enum-flag schema checks; Pie has two checks.
The [native receipt](../tests/fixtures/deluxe_keymaps_category03/native.json)
retains65 factory attempts and21 copied-reference attempts. A completed
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

Required native work includes a positive cursor-effect control, Image framing/pan/zoom, the axis reference readiness
check, remaining ordinary clusters,
and focused middle-mouse and modal/tool probes. G behavior and production persistence are accepted; composed UV/global
parity remains. Existing proofs need no broader
rerun unless affected source changes.

Of 140 active full-side delta candidates, 38 have implemented declarations:
thirteen framing, six UV selection additions, four Circle inputs and twelve
ordinary declarations accepted through explicit mechanism reuse, plus Object
Subtract Selection accepted after batch31 and Extend Selection by Center after
batch34, plus ordinary UV Extend after batch38. Exactly eight UV-specific Q,
loop/linked and Tweak fallback rows were explicitly transferred to 04. The
remaining 94 stay with 03: 10 ordinary candidates (nine declarations still draft), 67 currently
unsupported or unproved handler/modal/tool/replacement cases, 13 observations of
active-role absence, and four conflicting bindings. Active-role absence alone
does not prove unavailability. Each has row-specific next steps in the refreshed
reconciliation proposal. The two implemented UV arrow dispatch mismatches are
resolved by batch24; the historical failed comparisons remain recorded.
These counts describe disposition, not native parity.
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

The current mechanism partition contains 94 remaining IDs: ordinary
declarations (10), modal events (33), middle-mouse tool dispatch (19), selection
replacement/fallback (19), navigation timing/context (5), release confirmation
(4), and conflicting reference intentions (4). Registration/persistence proof
can be reused where source, selector and context warrant it. Twelve ordinary rows
were explicitly approved for reuse. Ctrl-F1 retains its spot check. The two UV
arrow checks exposed dispatch mismatches subsequently resolved by actual
production behavior and representative persistence checks in batch24.
A source-bound single-step launcher retains the exact wheel comparison and shared
lifecycle/control commands. Another native allocation is required for further
families; the inconclusive wheel pair will not be repeated unchanged.

The combined tools/selection fixture covers ten exact rows in sixteen
context observations per configuration. Image W/E/R/Q each run in VIEW and UV;
Vertex/Weight Paint Q each run with selection masking off and face masking on.
The bundled 4.5.1 tool definitions expose selection/transform tools in UV and
conditionally expose paint selection tools, so a VIEW-only or unmasked failure
cannot establish unavailability. Every observation retains its own reset,
Window delivery, distinct starting-tool evidence and direct control. Factory
and copied-reference configurations require separate children. Batch26 completed
all sixteen observations in each child, with every context and Window control
valid. UV T and masked Vertex/Weight Paint Q produced matching tool changes.
Image/UV Q matched on its first press but production cycled to Circle on the
second while reference stayed on Box; cycling parity remains open.

All fourteen tool direct controls failed because the fixture explicitly passed
captured default `space_type=EMPTY`. The bundled operator uses that value when
the property is set, and derives the actual editor only when it is unset. These
are control errors, not tool-unavailability evidence. A follow-up must record
native property-set state and distinguish a context-derived positive control
from exact keymap readback. Image Paint Invert polled false; Object ESC's direct
control returned CANCELLED. Neither fixture establishes unavailable behavior.
The copied reference also failed strict preservation on 227 rows: readability
changed, and two Weight Paint provider rows exposed four additional properties.
Native IDs, order and other fields were unchanged; newly readable values do not
prove their previous values. Production native shutdown and both host cleanups
passed, with protected input hashes exact and no copied resources remaining.

The coordinator accepted the three exact UV T and masked Vertex/Weight Paint Q
declarations at these tested contexts using the existing ordinary registration
and toggle mechanisms. Their positive effects need no rerun. This acceptance
retains the direct-control and strict reference failures and makes no generalized
dispatch, preservation or availability claim. Image/UV Q cycling remains open.

The read-only Transform Modal Map E witness ran in a copied reference as batch27.
`tests/blender_keymap_category03_modal.py` reuses the ordinary
fixture's input and preservation controls. It requires a native Rotate movement
and exact cancellation control, then observes a known Translate operation,
first E, repeated E, confirmation and extra motion. Geometry snapshots must
show the effects; a changed rotation alone does not identify Trackball. The
24-step fixture retains both exact E token selectors and full source/merged maps,
creates no modal items and enables no runtime capability.

`reference-evidence-1794563307033648000` passed native Rotate/motion/cancel and
Translate/motion controls. First E produced actual rotation with live
`TRANSFORM_OT_rotate`; repeated E produced further rotation with live
`TRANSFORM_OT_trackball`. This identifies the mode independently of the fixture's
geometry-only caveat. RET ended the modal operation, and extra motion changed
nothing. All captured Transform Modal Map snapshots stayed exact.

The overall run failed strict preservation. Source comparisons retained 192
readability changes. Separately, the merged user UV Editor shrank from 318 to
272 rows: 45 `uv.toolkit_center_cursor_and_frame_all` rows and one
`uv.toolkit_distribute` row disappeared. There were also 146 merged readability
changes; surviving IDs and relative order stayed unchanged. The cause of the
foreign row loss is unknown. These failures remain distinct from the observed
E behavior. The child exited after 29.533 seconds, owned controls and all copied
roots were removed, protected inputs were unchanged and the slot was released.

Batch28 `modal_observe-1794564688446795000` ran the matching factory observer
with both helpers identical to batch27. Rotate/motion/cancel and Translate/motion
controls passed. E and repeated E left `TRANSFORM_OT_translate` active, continued
changing location and left rotation unchanged. RET ended the operation and extra
motion changed nothing. This establishes the scoped factory/reference behavior
difference; it does not erase the reference preservation failure.

Factory before-capture/before-shutdown context and complete map-count lists
matched after native keyconfig updates. Full source and merged snapshots also
matched exactly, including every Transform Modal Map. The child completed in
17.4895 seconds. Owned control removal, addon unregister, zero ownership/pending
cleanup/tracked resources and watcher shutdown passed. The owned PID and every
temporary resource root were verified absent; all 40 frozen source hashes and
protected inputs stayed exact. The slot is released, with no repeat allocation.

The existing runtime still supports only its exact same-event
precision-to-cancel modal proof. The next offscreen proposal is limited to two E
aliases copied from observed R ROTATE/TRACKBALL templates in a disposable
fixture, retaining original R behavior, exact ordering, partial-install rollback
and owned user-edit handling. No production declaration or shared runtime was
changed, and the other modal candidates remain unaccepted.


The batch29 disposable probe tested the two native-template aliases.
`tests/blender_keymap_category03_modal_probe.py` admits only the exact native
R/PRESS ROTATE/TRACKBALL templates. Both have repeat disabled; the exact E
selectors require repeat enabled. It changes **both** fields on owned copies,
creates TRACKBALL first and ROTATE second with head insertion, then validates
complete source/merged E readback and ROTATE-before-TRACKBALL order. Original R
and all foreign item fields/relative order remain strict. Complete map metadata
is retained; every release requires full source/merged equality.

The 79 scheduled steps reuse real movement, cancel, live operator identity,
RET and extra-motion controls. They include deliberate first-copy rollback,
E and R while installed, E and R after exact removal, a fresh pair generation,
merged user edits to F18 with ROTATE inactive, and edited-pair removal. Portable
fault tests cover failure after native allocation, a rejected repeat setter and
an address reused by a different native ID. Current-process user-edit readback
and cleanup do not establish saving, reopening, UI integration or edit restoration
through feature toggles. `modal_alias_probe` is test-only; shared runtime and
production declarations remain unchanged. Its strict user-edit failure below blocks this source-copy path. No identical
repeat or shared runtime/production implementation is authorized.

A separate offscreen `ObjectSubtractCases` in the handler fixture schedules only
ten steps for exact Ctrl-click Object subtraction. It isolates a visible target,
projects the same point for native input and direct control, requires F23 delivery,
records press/release and full native candidates, resets selection before the
minimal direct call, and rejects FINISHED without actual deselection. It retains
strict source/merged cleanup. The focused factory `subtract_probe`/`subtract_observe` and copied-reference
`subtract` launcher routes ran as batch30 below; the corrected return predicate is offscreen;
Circle/navigation/shortest-path behavior is not rerun or accepted by this work.


Batch29 `modal_alias_probe-1794565828872658000` passed all five behavioral
cases in 34.4586 seconds: direct Rotate/cancel, E switching with the pair,
R with the pair, factory E after removal and R after removal. Exact emission
included repeat=True and ROTATE-before-TRACKBALL ordering. The deliberate
first-copy rollback and unedited-pair removal restored full snapshots exactly.

After the fresh pair's merged user IDs 61/60 were edited to F18 (ROTATE inactive,
TRACKBALL active), readback passed. Removing owned source copies then changed
**merged stock R IDs 16/17** to F18/repeat=True; ROTATE also became inactive.
Both rows and the user Transform Modal Map became user-modified. All 56 item
IDs/order and map counts stayed unchanged; every other merged map and all
default/active/addon snapshots stayed exact. Matching context/counts therefore
did not establish preservation. This is a concrete production blocker, not an
aggregate-marker exception. The overall native error and complete snapshots
remain retained. No normalization, broad restore or identical repeat is allowed.

Native unregister completed with zero owned/pending/tracked resources and the
watcher stopped. The child and all temporary roots were verified absent, and
protected inputs and 41 frozen source hashes stayed exact. Slot released. The
independent focused subtraction fixture can progress; a materially different
modal persistence path requires separate evidence and review.

Offscreen review of the pinned Blender 4.5.1 `wm_keymap.cc` explains a mechanism
consistent with this result: diff patching falls back from complete binding
equality to operator/modal-result equality, then preserves the matched base ID.
This is source analysis, not a captured native C call trace. The materially
different candidate is a user-defined modal addition with a negative ID: the
source represents these as add-only diffs. A narrow model reproduces batch29's
rebinding and distinguishes add-only removal. User-map RNA admission, identity
through rebuilds, exact edited cleanup, saved ownership and immediate-save/fresh
reopen remain unproved. No alternative production path is implemented.


Batch30 compared one copied-reference subtraction child
`reference-evidence-1794566535713559000` (20.01s) and one exact factory probe
`subtract_probe-1794566659165110000` (12.5539s), both at frozen `5320daf`.
Each isolated target stayed selected after PRESS and became unselected on RELEASE.
The F23 callback and direct call shared projected point (2055,1229). After an
independent selected-state reset, the direct call also deselected the target.
Both returned FINISHED with PASS_THROUGH. The frozen fixture incorrectly required
FINISHED alone, so both historical native status errors remain retained. The
predicate is corrected offscreen and tested to reject no effect, cancellation
and unfinished results; the positive reference/factory observations need no rerun.

Factory full source/merged preservation passed, and unregister ended with zero
owned/pending/tracked resources and a stopped watcher. Reference strict comparison
failed separately: 194 source read_issues changes (193 active, one addon), 148
merged read_issues changes, and user UV Editor318→272 from 45 removed
`uv.toolkit_center_cursor_and_frame_all` rows plus one `uv.toolkit_distribute`.
All other fields and surviving relative order stayed exact. The foreign loss
cause remains unknown. Both PIDs and all temporary roots were verified absent,
protected inputs and43 frozen hashes matched, and the slot was released.

Batch30 captured inherited stock Ctrl-LEFTMOUSE/CLICK row109 with center=True,
object=True and deselect=False, but did not exercise stock-only behavior in the
matched isolated scene. The earlier handler probe already had candidate items
and lacked its direct control/isolated target, so it cannot fill that gap.
The narrow production reservation is one ordinary editable view3d.select
Ctrl-LEFTMOUSE/CLICK declaration under a new independent Subtract Selection group.
The approved source draft now registers that declaration through the existing
ordinary action machinery, with its own Subtract Selection toggle and editable
tab. Stock bindings and existing preferences remain unchanged. No shared runtime
capability is added. At the source-draft checkpoint, accounting remained
35 implemented, eight transferred and 97 remaining pending native acceptance.

The prepared `subtract_production` fixture runs six matched trials: selected and
unselected targets with the group off, on, then off again. Each trial resets the
scene, verifies input delivery at the projected target point, and independently
resets selection before its direct positive control. Enabled trials must finish
unselected; stock outcomes are recorded without assuming their behavior. The
fixture checks the actual registered legacy:Selection identity and complete
emitted binding, then performs a second install/release. No candidate is injected
by the test. F23 controls are absent at toggle comparison endpoints. Foreign
source and merged maps remain strict, with only the existing two live-proven
Pipeline source generations compared separately.

All 62 category tests pass. Offscreen scheduling validates six trials and 72
fixture steps. Existing focused modes explicitly leave the new group off unless
their fixture enables it; inspection still covers the default production catalog.
Ordinary editable persistence reuses the accepted mechanism; this checkpoint
does not claim a new native save/reopen run.

Batch31 `subtract_production-1794568237865868000` completed in 50.5662 seconds
at `f6498ac`. All six independently reset trials passed. Before enabling the
group, Ctrl-click kept a selected target selected and selected an unselected
target. With the group enabled, it deselected the selected target and left the
unselected target unselected. Disabling the group restored both observed stock
outcomes. Every trial verified input delivery at (2055,1229), a separately reset
positive direct control and exact source/merged preservation. Direct controls
returned FINISHED with PASS_THROUGH and produced actual deselection.

Both actual production installs used the same legacy:Selection owner and
`0:3D View:LEFTMOUSE:CLICK` request, with exact complete native binding admission.
Both releases and final cleanup passed foreign preservation; the existing two
live-proven Pipeline source generations were compared separately. Native
unregister ended with zero owned/pending/tracked resources and a stopped watcher.
The child PID and every owned temporary root were absent, and all44 frozen source
hashes and protected inputs matched. The slot was released; no other child ran.

This matched off/on/off comparison establishes the production group's effect
in the tested Object-mode scene. It does not trace every internal handler or
establish other modes/editors. The coordinator accepted this exact row with
ordinary lifecycle reuse: accounting is now 36 implemented/eight transferred/96
remaining. Native evidence now retains
59 factory and18 reference attempts, with historical failures unchanged.
All63 category tests pass, including a retained-evidence check of the six-case
matrix, production ownership, exact preservation and native cleanup.

The next independent selection row is 3D View Cmd+Shift+LEFTMOUSE/CLICK
`fee4a4d6ed723ffaa6fff80bdf81c6a3449e33667c182ee2ec2019699bff7d6d`.
Its reference properties retain toggle=True while enabling extend=True. Pinned
Blender 4.5.1 source chooses extend before toggle; selected-and-active is the
discriminating state because stock XOR may preserve a selected inactive target
while activating it. The test-only fixture at `aad0b56` therefore uses six
selected-active/unselected trials with a separate selected bystander: stock,
exact owned candidate, then restored stock. UV/tool rows remain separate.

Batch32 `extend_probe-1794569119579631000` completed in 44.1589 seconds.
Stock deselected the selected-active target and selected the unselected target;
the probe kept the selected target selected and selected the unselected target.
Removing the probe restored both stock outcomes. The target ended active and
the bystander stayed selected in all six cases. Exact Shift/OSKEY/Ctrl/Alt and
point (2055,1229) delivery passed, as did every independently reset minimal add
control. Exact candidate admission was addon/user1 only during the two probe
trials and zero in both stock stages. All captured source/merged maps matched
after each release and final cleanup.

Native unregister ended with zero owned/pending/tracked resources and a stopped
watcher. The PID and every owned temporary root were absent; all44 frozen source
hashes and protected inputs matched. Slot released, with no other child.
This establishes the scoped factory probe effect, not copied-reference behavior,
production registration or other-mode parity. Accounting remains36/eight/96.

Batch33 `reference-evidence-1794569668793426000` ran the two inherited reference
states at `c3f7036` in 25.941 seconds. Selected-active stayed selected; unselected
became selected and active; the bystander remained selected. Both exact
Cmd+Shift/point controls and independently reset direct add controls passed.
Complete binding admission was default0/active1/addon0/user1. These observations
match the accepted factory probe.

Both per-trial strict comparisons failed and the native status remains error.
Each trial changed 194 source and 148 merged read_issues fields. User UV Editor
lost 46 foreign rows in the first trial (45 uv.toolkit_center_cursor_and_frame_all
and one uv.toolkit_distribute), then regained those rows in the second. Other
fields and surviving relative order matched; final complete captured maps were
exact. This does not erase transient strict failures or establish their cause.
Both trials released their owned controls, and host cleanup verified the PID and
all copied roots absent. Protected inputs and44 frozen hashes matched; slot
released. All60 prior factory/18 reference records remain unchanged; evidence now
contains60 factory/19 reference attempts.

The matching reference outcomes fulfilled the approved condition for one
ordinary production declaration: Extend Selection by Center, with
center=True/extend=True/toggle=True and the exact Cmd+Shift CLICK event. The
existing Selection feature pattern provides an independent toggle and editable
EXTEND tab. Stock flags, UV/tool declarations and shared runtime are unchanged.
Accounting remains36/eight/96 pending actual production acceptance.

The minimal prepared production check reuses accepted stock/reference controls:
two enabled selected-active/unselected trials, actual registered owner/request
identity, two installs/releases, independent preferences and exact foreign
preservation. Its28 fixture steps add no candidate directly. Existing ordinary
editable persistence is reused; no additional save/reopen or reference child is
proposed. All71 category tests pass, including reference-error retention, exact
editable group registration and the minimal production schedule/effect checks.

Batch34 `extend_production-1794570198118063000` completed in 21.7057 seconds at
`79c2123`. Both actual-production target states ended selected and active, with
the bystander still selected. Exact modifier/point input delivery and both
independently reset direct add controls passed. Complete addon/user admission
matched the reference binding. The same actual legacy:Selection owner and
`0:3D View:LEFTMOUSE:CLICK` request were verified across two installations.
Both releases and final comparison passed, including exact foreign preservation
and the existing separate comparison of two live-proven Pipeline generations.

Native unregister ended with zero owned/pending/tracked resources and a stopped
watcher. The PID and all temporary roots were absent, all45 frozen hashes and
protected inputs matched, and the slot was released. No stock/reference/probe
replay or other child ran. This establishes actual production behavior in the
tested Object-mode scope using the accepted stock/reference controls; it does
not claim other-mode parity or a new save/reopen test. The coordinator accepted
the exact production row using existing ordinary lifecycle and accepted
stock/reference controls. Accounting is now37 implemented/eight transferred/95
remaining; the retained batch33 strict errors remain unchanged.
All72 category tests pass. The lossless receipt contains61 factory/19 reference
attempts; all60 prior factory/19 reference records remain unchanged.

Batch35 `uv_extend_probe-1794571757033229000` retained a fixture error after
15.4821 seconds at `7e61950`. The shared quad's direct UV-coordinate ADD control
selected the unselected target and retained the selected bystander. Both stock
UV Editor Shift+LEFTMOUSE CLICK states completed: selected became unselected;
unselected became selected. Neither changed on PRESS, both changed on RELEASE,
and the exact CLICK pass-through witness ran once per observation. Geometry,
tool and bystander remained unchanged; Shift+F23 confirmed point[1978,1126].

After candidate insertion, the witness-order assertion failed before sending
the candidate mouse PRESS. No candidate gesture or tool/fallback PRESS trial
ran. The failing code stored counts/maps/order only after that assertion, so the
failed state's precise merged positions were not retained. This is a diagnostic
limit, not evidence of a product selection defect. The two stock observations
remain usable independently of the overall native error.

Final captured source and merged snapshots matched exactly. Fixture cleanup
reported no errors; native owned/pending/tracked resources were zero and the
watcher stopped. PID25137 and all temporary roots were absent, protected inputs
and all45 executed source hashes matched, and the allocation was released.
The lossless receipt now contains62 factory/19 reference attempts; all61 prior
factory/19 reference records remain unchanged. Accounting stays37/eight/95.

The corrected test-only fixture records counts and full map snapshots before
admission checks, then records actual witness/competitor indices before checking
order. Pinned Blender4.5.1 `wm_keymap.cc`, `wm_keymap_addon_add`, prepends each
source item to the merged map. Inserting the owned candidate before the owned
witness in the disposable source therefore places the witness first after that
merge; actual readback must still pass. No stock row or product behavior changes.
The two completed stock CLICK controls are hash-bound and reused only with the
same exact binding, tool, UV geometry/location and projected point. A fresh
proposal has59 steps and ten new observations, retaining separate primary and
fallback PRESS baselines. No identical retry or new allocation is assumed.
All81 category tests pass, including failure-position retention, reversed-merge
ordering, the reduced schedule, native stock effects and strict cleanup.

Batch36 `uv_extend_probe-1794572360320071000` completed its ten new observations
in30.4034 seconds at `6cccfad`. The hash-bound two stock CLICK controls from
batch35 passed the promised same-binding/tool/UV-position/projected-point checks.
Both ordinary UV Editor CLICK candidate states gave additive behavior: selected
stayed selected and unselected became selected on RELEASE. The exact CLICK
witness ran, the selected bystander stayed selected, and geometry/tool state
stayed unchanged. Merged order was witness0, candidate1, stock27.

Both primary and fallback tool PRESS maps were independently reached by their
exact witnesses. Stock toggled the target in both starting states. With the
candidate, both starting states ended unselected on PRESS and stayed unselected
on RELEASE, despite positive independent direct ADD controls. Tool keymap fields
were null; tool IDs and the fallback ID were retained. These effects are
consistent with the source-backed ADD-then-stock-XOR pass-through hypothesis,
but no internal C operator-call sequence was traced. The two PRESS rows remain
unresolved; there is no justification for an equivalent repeat.

All ten input controls, three direct positive controls, per-cell strict map
comparisons and final strict source/merged comparison passed. No fixture cleanup
errors occurred. Native owned/pending/tracked resources were zero, watcher
stopped, PID26059 and all temporary roots absent. All46 frozen inputs and
protected files matched. Batch36 is released; no other child ran. The receipt
contains63 factory/19 reference attempts, with all62 prior factory/19 reference
records unchanged. Accounting remains37/eight/95; this is factory probe evidence,
not copied-reference parity or actual product registration.

A minimal copied-reference fixture is prepared for only ordinary CLICK row
`0e8d690a0470457363cd15ff3448c54325c24261cae1dc525ebff9c3dd459f1d`.
It reuses eleven unchanged geometry/control/input methods, requires the exact
active/user binding with no add-on candidate, and observes two initial states
in16 fixture steps plus two reference-start ESC steps. The two PRESS cells and
candidate insertion are excluded. Strict preservation failures remain failures,
even when the separately recorded selection effects match. The reference
launcher can now accept a shorter positive ceiling up to its existing110-second
maximum; the proposed single child is capped75 seconds. No allocation or launch
is assumed.

The conditional ordinary mapping is an unapplied patch adding one
`SELECTION_UV_EXTEND` declaration (`uv.select`, extend=True, Shift+LEFTMOUSE CLICK
in UV Editor) to the existing Extend group and toggle. The two PRESS bindings
are excluded. It awaits reference evidence and coordinator source approval.
The next grouped investigation is Image Q/W/E/R: four ordinary rows sharing
`wm.tool_set_by_id` context resolution and tool/cycle controls. The known
explicit-default `space_type=EMPTY` control error must be repaired once, with
actual property-set-state captured, while preserving the existing Q second-press
divergence. This offscreen group proposal adds no native allocation or product
change. All85 category tests pass.

Batch37 `reference-evidence-1794573067246147000` ran the two ordinary CLICK
reference states at `f73559f` in23.15 seconds. Both matched the additive effect:
selected stayed selected, unselected became selected on RELEASE, and the
bystander/geometry/tool remained unchanged. Exact CLICK witnesses, Shift+F23 at
point[1978,1126], active/user candidate admission with no add-on candidate and the
independently reset direct ADD control passed. The cell comparison also passed.

The final comparison retained native status error:227 source read_issues changes
(226 active, one add-on),173 merged read_issues changes, and merged UV Editor
318→272 with46 foreign rows removed (45 uv.toolkit_center_cursor_and_frame_all,
one uv.toolkit_distribute). Other fields and surviving relative order matched;
the cause is unestablished. These strict failures are not normalized or erased.
Owned control rows were absent after cleanup, control class unregister completed,
and no owned cleanup/diagnostic-retention errors remained. PID27237 and all
temporary roots were absent, protected files and45 frozen inputs unchanged, and
batch37 was released. The lossless receipt now contains63 factory/20 reference
attempts, with all63 prior factory/19 reference records unchanged.

Both matching effects and verified owned cleanup satisfy the coordinator's
explicit conditional source authorization. The exact prepared patch now adds
SELECTION_UV_EXTEND to the existing Extend group, using uv.select with extend=True
and Shift+LEFTMOUSE CLICK in UV Editor. No new preference/tab, stock mutation,
tool PRESS binding or shared runtime capability was added. The original Object
Extend action retains its identity; its historical executed source hashes stay
unchanged. The new UV action's portable owner is
`legacy:Selection:de1a2030dc8d4baa0792cff32127ec7f6c081ec3d3dfa7bf5e7764c26a191a80`,
request `0:UV Editor:LEFTMOUSE:CLICK`. Native production identity is still pending.

The minimal actual-production fixture has20 steps/two enabled UV states, one
real group install/release and final preservation comparison, with independent
preferences and complete binding/owned-pair checks. Its temporary witness is
appended after the already registered source so Blender's prepend merge puts
the witness ahead; the actual candidate is never directly inserted or reordered
by the fixture. Controls are absent at toggle endpoints. Existing ordinary
editable persistence and batch35/36 stock/probe controls are reused; there is no
reference, stock, second install or save/reopen replay. No new native allocation
is assumed. All88 category tests pass, including both editable Extend actions,
exact stock preservation, production scheduling/cleanup and retained reference
strict failure. Accounting remains37/eight/95 pending production acceptance.


Batch38 `uv_extend_production-1794574142641917000` at `469b6ac` completed in
18.2231 seconds. Both actual-production states passed: an already selected UV
stayed selected, and an unselected UV became selected on RELEASE after an
unchanged PRESS. The selected bystander, geometry and tool were preserved.
F23 input delivery, exact CLICK witnesses and the independent UV-coordinate ADD
control passed. Runtime ownership and the registered pair matched the declared
UV action; merged order was witness0/candidate1/stock27, with no direct candidate
injection. One real group install/release and the final comparison passed,
separating only the two previously live-proven Pipeline source generations.
Strict cell/control-release comparisons passed; all owned resources were released,
the watcher stopped, PID28641 and all temporary roots were absent, and protected
inputs plus all45 frozen source hashes were unchanged.

The coordinator accepted only ordinary UV CLICK row `0e8d690a…`, bringing current
accounting to38 implemented/eight transferred/94 remaining. The two tool PRESS
rows and batch37's final strict reference failure remain unresolved and retained.
The lossless receipt preserves all63 prior factory and20 reference records and
now contains64 factory/20 reference attempts. All89 category tests pass. The next
work is the exact four-row Image Q/W/E/R shared test-control repair; no production
or runtime change or additional native allocation follows from this acceptance.


The shared Image tool control repair is now prepared as the exact `image_tools`
subset of the unchanged22-row ordinary pool. It schedules Q/W/E/R separately in
VIEW and UV: eight cases, two simulated native key presses and one independently reset
direct control per case,66 shared fixture steps. The existing production and
copied-reference launchers accept the subset. It refuses disposable candidate
insertion and leaves all production declarations/runtime behavior unchanged.
Image Paint Q, UV T, masked paint Q and UV PRESS are excluded.

Before each input, complete overlapping default/active/add-on/merged rows retain
native identities, order, effective properties and separate `is_property_set`
values for space_type/name/cycle/as_fallback; unreadable state remains unknown.
The direct control explicitly supplies its actual IMAGE_EDITOR space, recording
both the original captured EMPTY and the control arguments. Positive control
requires a distinct starting tool, FINISHED and the requested active tool in the
same editor/mode with no modal operator. Missing effects remain inconclusive.
A read-only Python observer wraps only the first/second native input interval
and captures actual wm.tool_set_by_id arguments, property-set states, resolved
space and results. Full overlapping rows are captured again before the second
press. Direct/setup calls are excluded and the previous profiler is restored.
This can distinguish Q cycle calls without claiming that Python dispatch identifies
a particular native keymap item by itself.

The subset also compares full captured merged maps as well as source maps after
removing its F23 control; all strict failures remain errors. Cleanup still
attempts owned-row release if observer shutdown fails. All98 category tests pass,
including an executed fake Q case retaining a second-press Circle outcome while
the separately reset direct control selects Box, unknown explicit-set state,
observer restoration and strict merged failures. The proposed native comparison
is one factory production child and one copied-reference child, each capped75
seconds and run sequentially only under an exact grant. No native child has run
for this repair, no additional mapping is accepted, and accounting stays38/eight/94.


Batch39 executed the frozen Image control pair at59c2d16, strictly sequential:
factory `ordinary_production-1794575338527776000` completed31.4437 seconds;
reference `reference-evidence-1794575403713345000` completed all eight cases in
39.906 seconds but retained native status error at strict preservation.

| Context/input | Factory | Copied reference | Direct control |
| --- | --- | --- | --- |
| VIEW Q/W/E/R | Both tool calls CANCELLED, Sample unchanged | Same | CANCELLED; no positive effect |
| UV Q | Select → Box → Circle; one cycling call per key cycle | Select → Box → Box; cycling then noncycling call per cycle | FINISHED but selects Circle in both; Box positive check remains false |
| UV W/E/R | First input starts Translate/Rotate/Resize; no tool call | Same first input and no tool call | Transform tool selected positively for all three keys in both |

The second UV W/E/R inputs retained separate modal differences: factory remains
Translate/Rotate then switches Resize→Rotate; reference switches Translate→Edge
Slide, Rotate→Trackball and remains Resize. These do not establish ordinary Image
tool-alias dispatch. Every Window delivery, context and distinct-start check
passed. Captured keymap space_type=EMPTY was unset; dispatched tool calls resolved
IMAGE_EDITOR. The corrected controls therefore separate tool availability from
native-handler routing without treating FINISHED as a selection effect.

The exact noncycling companion is UV Editor **Q/RELEASE** row `2cc296fd…`, already
transferred to04. Reference active/user ID281 has name and cycle explicitly set,
space_type unset, cycle=False and no modifiers/repeat. It matches the additional
call after the Image cycling call. This trace spans an entire PRESS/RELEASE cycle;
a phase-separated composition check belongs to04/06. Its exact plan is recorded
in the04 handoff. The03 Image Q PRESS row stays open while preserving its matched
cycling call; no temporary04 dependency or equivalent Q rerun is introduced here.

Factory strict source/merged preservation passed. Reference retained seven merged
map pointer replacements,192 source read_issues changes (191 active, one add-on),
146 merged read_issues changes and UV Editor318→272 from45 foreign
uv.toolkit_center_cursor_and_frame_all plus one uv.toolkit_distribute removal.
Other compared fields and surviving relative order matched; cause remains
unestablished. Full raw snapshots and native error remain, without normalization.
Both F23 controls and Python observers were released; factory unregister and
watcher shutdown passed. PIDs30695/30912 and all temporary roots were absent,
protected inputs and45 frozen source hashes exact. No further allocation remains.

All101 category checks pass. Every prior64 factory/20 reference receipt is
unchanged; totals are65/21. No new candidate is accepted and accounting remains
38/eight/94. The next03 source-only proposal groups four 3D View fallback Circle
RIGHTMOUSE CLICK_DRAG bindings (SET, Shift ADD, Ctrl/Cmd SUB). It requires one
shared projected selection scene, independently positive exact-mode circle
controls, actual fallback-tool readback and per-modifier exact-event witnesses.
No fixture, production mapping, runtime change or new native run is authorized
by that proposal.
