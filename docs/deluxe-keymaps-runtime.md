# Deluxe keymap runtime

Brief 02 provides runtime-owned assignments and scoped replacements. It does not
migrate categories or activate a saved preset. The accepted
[baseline and ledger](deluxe-keymaps-baseline.md) remain unchanged.

The intended Deluxe catalog is a delta from an identified built-in Blender base,
plus scoped overrides of relevant add-on bindings. Unchanged stock and add-on
bindings stay inherited. The 4,509-row baseline inventory is reconciliation and
parity evidence, never a replay catalog. Future versioned JSON profiles should
store intended additions, replacements, removals or disabled targets with exact
scope/provenance and the minimum base, version and dependency metadata needed for
safe reapplication. This runtime consumes explicit requests and does not conflict
with that intent. Brief 02 does not implement that catalog or persistence layer;
no database-engine migration is included, and unsupported exact suppression
remains explicit.

## Category interface

Existing `OperatorAction`, `KeymapBinding`, `ensure_action_keymaps(category,
action)` and `unregister_registered_keymaps(pairs)` callers remain valid. The
adapter resolves dynamic properties once per registration attempt. Category lists
are bound to the registry before registration, so pending requests and recreated
items are also released when a category is disabled.

New code can import the frozen descriptors and registration API from
`keymaps.keymap_utils`:

```python
selector = capture_selector(source_map, source_item, source_role='default',
                            ledger_id='deluxe-baseline-2026-11-12-v1',
                            sample_id=accepted_row_id)
request = KeymapOverride(
    request_id='select-all-replacement',
    selector=selector,
    replacement=KeymapTarget('my_addon.select_one', {'mode': 'FIRST'}),
    capability='ordinary_tail',
    context='stock_object_mode_select_all',
)
handle = register_feature('category.feature', overrides=(request,))
# Inspect handle.diagnostics; registration never claims dispatch was verified.
handle.release()  # Idempotent; releases only this session's exact native items.
```

`capture_selector` is an inspection aid. Future migration code must freeze the
reviewed selector in its declaration and attach its accepted ledger/sample ID;
it must not learn a user's changed binding and then silently replace it.
A name or ledger ID does not prove ownership or provide a capability.

Brief 03's bounded category probe exposed native numeric-array and enum-flag
readback gaps. The current correction accepts fixed-size RNA bool/int/float
arrays through the observed `bpy_prop_array`, `Vector` and `Matrix` classes,
validating complete shape, scalar types and finite values. An RNA ENUM flag uses
readable allowed identifiers and a sorted immutable flag tuple, including the
empty tuple. Explicit flag assignments use a sorted unique tuple; only the
schema-aware setter converts that tuple to Blender's set input. Matrix assignments
use the observed typed setter to preserve logical row order during native
readback. Generic iterable
or set acceptance, pointer/collection support and capability policy are unchanged.
The 69 portable regressions and five affected native assignment/readback/release
cases pass, including edited-source preservation. Evidence is tracked in the
[category receipt](deluxe-keymaps-category03.md). The original
brief 02 native receipt remains historical evidence for its recorded source.

`KeymapScope` includes name, space, region, modal state and observable tool state.
Blender 4.5.1 does not expose tool state; `None` retains that uncertainty. Events
include `any`, tri-state modifiers, hyper when exposed, key modifier, direction,
repeat and map type. Targets contain an operator and complete readable effective
properties, or a modal token. Unknown schemas, unrepresented property types,
ambiguous source maps/items and unproved contexts fail closed. Legacy ordinary
assignments may declare a subset of operator properties; their complete emitted
state is read back and retained for ownership checks.

A feature has at most 16 requests. Registration preflights all new requests and
rolls back its own creations on a later creation or property-setter failure. A
feature ID cannot be reused with different requests until released. Conflicting
owners for the same full scope/event are reported; foreign lookalikes are never
adopted or deleted. Source aliases are compared by native identity and exact
collection membership.

Historical returned pair objects remain associated with their original request,
so unregistering a copied legacy list also cancels a replacement created by
reconciliation. The association uses the retained Python objects, not a fresh
pointer or a selector match. A live native member must also match the captured
`KeyMapItem.id` before the runtime reads or removes a stored item. Blender's
[RNA removal implementation](https://github.com/blender/blender/blob/v4.5.1/source/blender/makesrna/intern/rna_wm_api.cc)
invalidates the pointer wrapper passed to removal. An unobserved recreation with
the same address **and** native ID cannot be distinguished perfectly through this
API; this runtime does not claim universal author-history proof.

## Supported capabilities

| Capability | Exact evidence scope | Event flow |
| --- | --- | --- |
| Ordinary assignment | Non-modal add-on map, complete emitted readback | Adds its own item; no implicit old-event suppression |
| `ordinary_tail` / `stock_object_mode_select_all` | Object Mode, A/PRESS, stock selection fixture | Native replacement; poll failure and PASS_THROUGH continue the chain |
| `ordinary_tail` / `machin3tools_object_toggle_smooth` | Installed MACHIN3tools, Object mode with a selected mesh, 3D View Generic, Alt+Tab on macOS | Original provider toggles smoothing; consuming replacement takes precedence; poll failure/PASS_THROUGH reach provider |
| `modal_head` / `transform_translate_precision_cancel` | Enumerated Transform Modal Map, translate, LEFT_SHIFT/ANY/PRECISION to existing CANCEL token | The owned head copy cancels a real G-drag; removing it restores baseline behavior |

The installed-provider capability also requires enabled MACHIN3tools preferences,
the tested provider version, and its own exact registered pair in the provider's
`keymaps` registry. An equivalent row without that provider registration is not
eligible. Successful observation records the native ID behind the provider's
retained wrapper; a later different ID through that wrapper is rejected.
Provider disable/reload or an observed change to its registered pair retires the
known generation. Reuse before the first successful observation, or reuse of both
the same address and native ID, remains unobservable; registry provenance does
not establish universal author history. Modal replacement requires the active/default native alias; other
active presets are rejected, and switching away withdraws the owned modal copy.

Ordinary source-tail insertion is supported by the observed forward-prepend
add-on merge, followed by actual merged-order verification. Modal insertion uses
`new_from_item` in the enumerated existing source map. These are separate paths.
The runtime never fabricates an add-on modal map or a no-op modal token.

A generic per-item veto (`suppress_item`) is unsupported. Consuming an event can
also prevent unrelated fallthrough. A replacement must state the intended
context and behavior; poll failure or PASS_THROUGH can reach the original item.
Changing the event is a separate assignment, not removal of the old event.

The synthetic provider is a portable mechanics fixture, not evidence of an
installed add-on. Its test capability is unavailable inside Blender. The
installed X-Ray Selection Tools 4.9.0 toggle failed in its own constructor in
Blender 4.5.1; that attempted provider gate was removed. This does not establish
that other X-Ray Selection Tools operators fail or succeed.

## Lifecycle and diagnostics

One persistent watcher runs every 0.25 seconds when ready. Preference/keyconfig
readiness failures back off to 2 seconds. It processes at most 16 requests per
pass, with a 4 ms deadline checked between atomic features. An individual feature
is indivisible and can exceed that deadline; measured durations belong in the
native receipt. A round-robin cursor prevents smaller features from starving.
Creation failures have bounded per-request retry delay. Unchanged declarations
and source signatures do not recreate items.

The final full-category fixture held 144 features and 146 owned bindings. Twenty
unchanged checks created/removed nothing; the slowest complete watcher call was
9.3 ms. Provider re-registration was observed recovered within 0.695 seconds in
the scripted check. These are measured fixture results, not a hard latency promise.

Late provider registration can restore a pending request. Reconciliation removes
and recreates only the owned item when a relevant later binding overtakes it.
Two such repairs are permitted per request lifetime; repeated overtaking reports
`provider_priority_conflict` instead of fighting the other registrar. A stable
failed merged-order proof withdraws once and waits for a changed source generation
or explicit re-registration. Stale references never authorize deletion of a new
lookalike. A user-deleted owned source item cancels the request.

The global switch disables standard categories while Pipeline retains its
obligatory bindings and Pie follows its independent switch. Startup waits for
preferences and actual keyconfigs. Failure after partial category registration
drains ownership. Unload cancels the watcher and pending initialization even when
initial registration never completed.

Use `handle.diagnostics`, `runtime_diagnostics()`, `runtime_stats()` and
`retained_edits()` for inspection. `pending_cleanup()` reports failed removals.
Exact ownership survives rollback, withdrawal or release failures; that request
cannot create another item until cleanup resolves. A valid pending cleanup row
also blocks other owners or new request IDs from claiming its full scope/event.
Reconciliation and subsequent
registration/cleanup calls retry removal with bounded work. Unload logs any
unresolved cleanup and retains its records rather than hiding an orphan.
Diagnostics include owner/request IDs, the
ledger/sample, role/context, status, reason and missing capability. Common reasons
include `source_missing_or_edited`, `ambiguous_source`, `unsupported_capability`,
`unproved_context`, `conflicting_assignment`, `merged_priority_unproved`,
`creation_or_setter_failed`, and `provider_priority_conflict`. An `applied` result
means structural registration; `dispatch_evidence` stays false. Native event
receipts supply dispatch evidence separately.

## User edits and cleanup

Foreign source/user rows, their active flags, properties, events and relative
order are never rewritten. An edited foreign selector withdraws its owned
replacement. No preference-save interception or preset/profile writing is used.
Immediate edit/save and fresh reopen are tested with the replacement still
present, without an intervening watcher tick. Read-only preflight requires a
unique, active, exact original in the merged user map before creating any
replacement. Twenty subsequent checks of edited targets attempt no recreation.

A normal Preferences edit to a runtime-owned merged binding stays in Blender's
native preference diff. Disabling its source makes that binding dormant; adding
the same declaration again restores the edit. The native tests also exercise
empty-map cleanup and a fresh process. The runtime does not save preferences on
the user's behalf.

A direct RNA edit to an owned **source** item is different from editing the merged
Preferences binding. The runtime transfers the changed source row to explicit
user data, cancels its request and retains a diagnostic record. It never silently
recreates the original. `retained_edits()` reports the remaining row, and global
cleanup logs its presence. Such a row remains visible in the native source and
merged maps and may outlive add-on unload; this is an explicit preservation
limitation, not a claim of zero remaining rows. The native test removes its own
intentional edited fixture row by exact reference after verifying the transfer.

## Validation and remaining gates

The integrated receipt records five successful isolated GUI processes, 13 native
input observations and 15 foreign-row comparisons. MACHIN3tools 1.13.2 DeusEx
supplied the installed provider. The actual add-on watcher handled provider
unregister/re-register; the full lifecycle test exercised repeated global/Pie
switches, category rollback/recovery, an active-keyconfig round trip and two
enable/unload cycles. Every final process exited with no remaining test items,
runtime features or retained fixture edits. The intentionally retained direct
source-edit fixture was explicitly removed by the test, as described above.
Native removal faults covered rollback, release/re-registration and priority
repair; each retained exact ownership, recovered and drained its cleanup queue.
Copied legacy pairs released their reconciled replacement, disabled-provider
lookalikes were rejected, and switching active presets withdrew the modal copy.
The receipt also retains targeted writer/provider and ownership rechecks after
the final review fixes. Pending cleanup blocked both other owners and renamed
requests until removal succeeded. Each case records its tested source and driver
hashes; earlier accepted cases remain evidence for unchanged paths.

The portable result is 60 runtime tests, 19 baseline tests, two Pie tests and
three shared-contract tests. Full repository discovery additionally encountered
six import errors because `build_manager` is unavailable in this environment;
those build/manager dependencies were outside this change.

Portable checks:

```sh
python3 -m unittest discover -s tests -p 'test_keymap_runtime.py' -q
python3 -m unittest discover -s tests -p 'test_keymap_baseline.py' -q
python3 -m unittest discover -s tests -p 'test_pie_actions.py' -q
```

The native driver uses the integrated runtime and the full add-on lifecycle. It
requires an explicitly chosen executable and installed provider source. It copies
the add-on and provider source into disposable resources, redirects all five `BLENDER_USER_*` paths,
disables automatic preference saving, denies network access and confines writes
with macOS `sandbox-exec`. Only its own child processes and resources are cleaned.

```sh
python3 tests/blender_keymap_runtime.py \
  --blender '/path/to/Blender.app/Contents/MacOS/Blender' \
  --provider-source '/path/to/installed/MACHIN3tools' \
  --test-minimum-version 4.5.1
```

The compatibility flag changes only the copied add-on minimum. The development
branch still targets Blender 5.2.2. Native evidence here is Blender 4.5.1 LTS,
build `b0a72b245dcf`; it is not a Blender 5.2.2 execution claim.

The [sanitized integrated receipt](../tests/fixtures/deluxe_keymaps_runtime/integrated-native.json)
records the executed source/test hashes, cases and cleanup checks.
Private process logs and disposable profiles stay under ignored `test-results/`.
The source-active-bit suppression approach remains rejected by the accepted
persistence experiment. Missing providers, unresolved baseline rows, broader
editors/tools/handlers, other modal operators/tokens and full shortcut parity
remain row-specific gates for briefs 03–06. Category migration remains paused
until the coordinator accepts this integrated runtime.
