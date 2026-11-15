# Blue Hole validation

## Deluxe category 03

`python3 -m unittest discover -s tests -p 'test_keymap_category03.py' -q` checks
historical reconciliation evidence and retained operator behavior. Category
04/05 tests retain their reference reconciliation checks. The production
catalog's full ordered binding digest and category/subsection isolation are
checked by `test_deluxe_profiles.py` against the JSON runtime.

`blender_keymap_category03.py` and its handler/ordinary/editor helpers are
historical migration fixtures for the removed Python declarations. Directly
running that driver reports its retirement. Use the current runtime and
performance drivers below to exercise the JSON implementation. Historical
native findings remain in the [category receipt](../docs/deluxe-keymaps-category03.md).
`keymap_native_evidence.unpack_native()` expands the receipt's shared snapshots
and verifies their hashes and the complete document hash. Full sanitized run
receipts remain under ignored `test-results` with their hashes recorded in the
checked-in receipt; packing removes duplication without dropping evidence fields.

## Deluxe runtime keymaps

`python3 -m unittest discover -s tests -p 'test_keymap_runtime.py' -q` checks
exact ownership, replacement gates, rollback, bounded reconciliation and lifecycle.
The GUI driver `tests/blender_keymap_runtime.py` exercises the integrated runtime
with a real installed provider and disposable resources. See the
[runtime contract and native command](../docs/deluxe-keymaps-runtime.md).

Run `python -m unittest discover -s tests -v` for the existing adapter contracts.
They use isolated fixtures and the actual vendored library without Blender startup.
They do not connect to Perforce or validate add-on registration.

## Deluxe keymap baseline

`python3 -m unittest discover -s tests -p 'test_keymap_baseline.py' -v` checks
the read-only Blender exporter, deterministic row/duplicate identities, conservative
comparisons, collisions, and ownership ledger. Sanitized native fixtures are in
`tests/fixtures/deluxe_keymaps/`; private captures and disposable resources belong
only under ignored `test-results/deluxe-keymaps-baseline/`.

See [the baseline receipt](../docs/deluxe-keymaps-baseline.md) for snapshot/comparison
commands, GUI isolation, source preservation, actual input outcomes, and unresolved
rows. Development source on `blender-5.2.2/alpha` was tested with the explicitly
approved Blender 4.5.1 reference app. Only disposable compatibility-test copies
lowered the declared minimum; this does not establish Blender 5.2.2 compatibility.

## Embedded shared-library smoke test

With an installed Blender executable, run from the repository root:

```sh
python tests/blender_shared_smoke.py --blender "/path/to/Blender"
```

The launcher selects background factory startup, disables blend-file autoexecution
and supplies temporary user resource/configuration folders before Blender starts.
The script reuses selected existing portable shared regression modules for streams,
range buffers, batch outcomes, publication, recovery envelopes, provider boundaries,
renaming, content inventories, INI/text preservation, merge models, format
registration, SSE and JSON/XML. Selected unencrypted ZIP extraction cases need no
optional cryptography dependency. Blue Hole retains only namespace/lifecycle and
embedded-command checks; shared assertions stay in their library test owners.
Both standalone and vendored namespaces load the actual committed vendor copy and
keep separate registries. The consumer pie-action tests also run in this suite. Legacy diagnostic dialogs are disabled during the suite.
It neither registers Blue Hole nor opens or saves user projects/preferences.
Failures produce a nonzero process status; no additional packages are installed.

The printed JSON records Blender, embedded Python, the shared revision and test/skip
counts. Skipped platform cases do not establish coverage.
Passing on an older Blender establishes only those portable contracts in that
runtime. It does not establish compatibility of the target branch's registration,
operators, UI or exports. Use the declared target Blender for those separate checks.

## Pie action dependency contract

Pie action descriptors use the existing string menu-ID form of pie_menu_action.
Menus depend on the actions they draw; declaration metadata does not import those
menus back. tests/test_pie_actions.py rejects that dependency and checks all target
IDs against literal menu declarations, without registering or executing the UI.
The test also requires the retained actions to match actual UI references.
Shortcut bindings now live only in JSON.

Selected archive cases also check late source changes at ZIP publication and
one-pass removal selections. They use plain ZIP fixtures without optional
encryption packages and do not register the add-on.

The portable member-rebuilding module checks retained-name and stored-name
iterators, container comments, ordering, attributes, cancellation and size bounds.

Portable wiki catalog and directory snapshot/cache cases exercise junction-safe
traversal in the embedded Python version, including versions before pathlib
added `Path.is_junction`. Viewer tests remain in their Qt host suite.

## Deluxe lifecycle performance

`python3 tests/blender_keymap_performance.py --blender /path/to/Blender --output
test-results/keymap-performance` runs the current checkout in an isolated GUI
with factory preferences. It records three load/unload cycles, three Deluxe
toggle cycles, merged-update counts, and separate CPU profiles. Application
startup and profiling overhead are excluded from the cycle timings. It also
checks stable merged bindings, complete owned-resource cleanup, and preservation
of a native Preferences shortcut edit across refresh and disable/enable. It also
edits category/section choices through native checkbox properties, verifies JSON
persistence after reopening the store, and checks that legacy preference switches
cannot override the catalog. Draft toggles must update the live keymaps without writing JSON. Discard
restores saved behavior. Native checks also compare every offered input type
against Blender's classification and cover Repeat changes when switching inputs
or event phases,
the 24 shipped default disables, artist-created add-on disables, provider source
removal/recreation, context-menu source detection, and save/reopen of a
disposable userpref.blend to reject leaked preview deltas. Add `--capture-editor` to capture the Sections
UI enabled and with its subsection, category and master disabled, plus
the scrollable binding tree, binding inspector and a live default-disable rule.
The report includes editor draw timings. The checks
also verify checkbox reset on Discard and draft preservation across master
toggles. On macOS the child is confined to the output directory with network access denied.
The test does not load or save the user's preferences.

The embedded driver also compiles vendored production Python sources without
importing their optional toolkits. Syntax acceptance is separate from import,
registration and runtime behavior.

## Shared-library contract audit

`test_shared_contracts.py` resolves the add-on's shared imports and checks callable
argument shapes against the actual vendored modules. It also checks function global
bindings, including names brought in through wildcard exports, without importing
or registering Blender consumer modules. Blender property factory names are an
explicit static allowlist; the native check below validates the loaded modules.
The embedded smoke suite includes these checks and preserves namespace isolation.

## Native add-on fixture check

```sh
python tests/blender_addon_smoke.py --blender "/path/to/Blender"
```

This driver copies tracked add-on files into a temporary package and starts Blender
with factory settings and private user resources. It enables/disables the add-on
twice, checks preference and shared Perforce providers, inspects live function
bindings, exercises save callbacks with source control disabled, exports a fixture
mesh through Blue Hole to FBX and GLB, verifies position restoration, and checks
operator/timer/handler/keymap cleanup. It neither connects to a Perforce server nor
sends assets to an engine. Temporary projects, exports and settings are removed
when the process exits; the printed JSON records the exercised phases.

For an explicitly chosen older-runtime check, add `--test-minimum-version 4.5.1`.
Only the temporary copy's `bl_info` minimum changes; the checkout keeps its declared
version. A pass in Blender 4.5.1 validates those fixture workflows there and does
not establish Blender 5.2.2 compatibility or interactive viewport behavior.

On October 23, 2026, the 5.2.2 alpha source passed both the embedded shared suite
and native registration/save/FBX/GLB fixture checks in Blender 4.5.1 LTS/Python 3.11.
The vendor copy is byte-checked against its recorded commonUtils commit. Shared
workflow documentation uses canonical repository URLs because `.github` files are
intentionally excluded from vendored packages.

Split-catalog regressions in `test_deluxe_catalog.py` cover shared record relocation,
section addition/removal, malformed and duplicate JSON, broken references, stale
external edits, rollback, and interrupted-save recovery. The native performance
driver fingerprints every catalog file during previews and captures the in-field
**Input Key…** prompt as well as the binding/default-rule panels.

`blender_zenuv.py` uses an explicitly supplied Logistics checkout, Blender binary,
and private add-on library to install legacy Zen UV into disposable resources,
upgrade through Logistics' real `AddonLibrary.apply`, then dispatch the two Deluxe
UV gestures in a foreground Blender window. It verifies removal of the old module
and absence of legacy `BH_Keymaps.py`. macOS confinement blocks network access and
writes outside the test output; temporary presets are removed on exit. The
4.5.1 case lowers only the copied Blue Hole compatibility declaration.

```sh
python3 tests/blender_zenuv.py --blender /path/to/Blender --version 5.2.2 \
  --logistics-source /path/to/logistics --library /path/to/Blender_Addons_Library \
  --output test-results/zenuv-540/blender-522
```

The Other reorganization is checked against the historical ordered binding
fingerprint while normalizing only organizational owner names. The native merged
keymap digest also matches the catalog before reorganization. Capture checks
verify that selecting another keyboard key preserves Repeat without writing JSON.

The lifecycle driver also verifies the context-grouped binding editor,
category filters and name/key search, direct context creation, typed operator
suggestions, menu properties, unavailable operator persistence, category moves, and independent
command settings for bindings that use the same operator. It exercises operator
changes, reset, undo, deletion, save/reload, and preview cleanup. Catalog files
remain unchanged until Save and Apply Changes. Editor captures include the
context tree and the selected binding's command settings.
