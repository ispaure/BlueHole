# Deluxe keymap baseline

This is the native baseline for brief 01, captured on November 12, 2026. The
development source is `blender-5.2.2/alpha` at
`ea3acf8300881fbbac540dbd7f3194af8693dc17`; its declared Blender version remains
5.2.2. The user-approved test executable is **Blender 4.5.1 LTS**, build
`b0a72b245dcf`, on macOS arm64. No Blender 5.2.2 execution is claimed.

The ledger ID is **`deluxe-baseline-2026-11-12-v1`**. It records observed binding
candidates and controlled differences. It is not a claim that every candidate
dispatches in every editor, tool, mode, or operator-poll context. Brief 06 owns
the broader native parity checks; brief 02 must preserve the uncertainty recorded
here when choosing its override contract. The coordinator owns acceptance and
dispatch of the next brief.

## Evidence and reproduction

The sanitized evidence lives in `tests/fixtures/deluxe_keymaps/`:

| Artifact | Purpose |
| --- | --- |
| `capture-manifest.json` | Build, input hashes, options, readiness, add-on availability, source preservation, and native input outcomes |
| `reconciliation-ledger.json` / `.jsonl` | Dataset header and one record per relevant semantic row, with exactly one owner in 03–05 |
| `comparison-index.json` / `comparison-deltas.jsonl` | Controlled comparisons and links between before/after row occurrences |
| `collision-candidates.jsonl` | Deduplicated same-map event-overlap candidates and their observed order in each capture |
| `sample-stock.json`, `sample-full.json` | Small, sanitized native subsets accepted by the snapshot/comparison tooling |
| `contract-cases.json` | Actual navigation, selection, and transform-modal examples for 02 and 06 |
| `input-preference-effect.json` | Controlled native mouse-zoom inversion test |
| `cleanup-receipt.json` | Final source hashes, exited owned processes, and removal of resource copies |
| `missing-addon-impact.json` | Fourteen absent configured entries and 171 unresolved reference operator candidates, with attribution limits |

From the repository root:

```sh
python3 -m unittest discover -s tests -p 'test_keymap_baseline.py' -v
mkdir -p test-results/deluxe-keymaps-baseline
python3 tests/blender_keymap_baseline.py \
  --compare tests/fixtures/deluxe_keymaps/sample-stock.json \
            tests/fixtures/deluxe_keymaps/sample-full.json \
  --output test-results/deluxe-keymaps-baseline/sample-comparison.json
```

The exporter is read-only. In an **already verified disposable Blender GUI
session**, after add-on and keyconfig readiness, the Python console can run:

```python
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("baseline", REPOSITORY / "tests/blender_keymap_baseline.py")
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)
baseline.write_snapshot(OWNED_OUTPUT / "private-snapshot.json", baseline.capture_snapshot())
```

`REPOSITORY` and `OWNED_OUTPUT` are resolved `Path` values. A prepared launch can
equivalently use `--python tests/blender_keymap_baseline.py -- --capture OUTPUT`.
That CLI exports the state at invocation; it does not wait for registration or
establish isolation. Use the timer/readiness procedure below for authoritative
captures. Never treat factory background startup alone as reference evidence.

Full private snapshots, sanitized launch diagnostics, receipts, and the local
capture harness are retained in ignored `test-results/deluxe-keymaps-baseline/`.
The full harness is environment-specific; the committed exporter and comparison
fixtures have no reference-machine paths. Proprietary add-on code, binary
preferences, and copied resource trees are excluded from Git and packages.

## Isolation and capture procedure

The reference app and its shared portable profile are called `<reference app>`
and `<reference profile>` throughout the evidence. Resolve them privately. The
app itself was executed read-only; no app copy or original preference write was
needed.

1. Hash the reference and packaged `BH_Keymaps.py` and `userpref.blend` inputs.
   Create byte copies in an owned, ignored session directory; reject internal
   resource symlinks. Never hardlink source preferences or add-ons.
2. Set all five existing `BLENDER_USER_RESOURCES`, `BLENDER_USER_CONFIG`,
   `BLENDER_USER_SCRIPTS`, `BLENDER_USER_EXTENSIONS`, and
   `BLENDER_USER_DATAFILES` directories to that session. Also redirect temporary
   and cache output; set `PYTHONDONTWRITEBYTECODE=1` and disable Python user-site
   imports. The native confinement policy denies network access and all writes
   except beneath the owned session and to the null device.
3. First prove factory GUI startup with `--factory-startup --disable-autoexec
   --offline-mode`. Assert Blender's resolved resource/config/script/extension/
   data paths match the redirects. The proof passed with one GUI window and
   only eight bundled factory add-ons. Disable preference autosave immediately.
4. In a separate factory launch, intercept `addon_utils.reset_all`, script-path
   refresh, and keyconfig loading before `bpy.ops.wm.read_userpref()` loads the
   copied binary preferences. Temporary empty `AddonPreferences` classes expose
   saved IDProperties without importing third-party add-on code. Redirect
   embedded writable paths, then remove those temporary classes before normal
   add-on registration. The bundled system extension directory remains a
   read-only resource under OS confinement.
5. One installed add-on initially failed because its default preset storage
   attempted a write outside confinement. Six preset-directory preference values
   were then pre-set in the disposable profile. No vendor code was changed and
   confinement was not relaxed. Final captures load 34 add-ons; the other 14
   configured entries are absent from the checked reference profile and bundled
   add-on/extension locations. The manifest gives stable aliases; the private
   module inventory resolves them locally.
6. Restore normal registration, load the requested preset if present, and record
   the actual active configuration. Wait for Blue Hole's initialization timer to
   finish and for three successive identical normalized keyconfig samples.
   Record all default, active, add-on, and user rows before injecting input-test
   fixtures. The final captures all use the same exporter hash.
7. Run bounded native event-dispatch checks in the factory scene. Dismiss startup
   popups and verify a temporary F24 sentinel before interpreting keyboard
   outcomes. Remove the sentinel afterward. Retire only the owned subprocess,
   rehash the source inputs, retain concise evidence, and remove copied resource,
   preference, cache, and recovery trees.

Blender's preference reload refreshes scripts and resets add-ons before keyconfig
reload, which is why interception precedes the binary load. See the
[Blender 4.5.1 preference reload implementation](https://github.com/blender/blender/blob/v4.5.1/source/blender/windowmanager/intern/wm_files.cc)
and [resource-directory implementation](https://github.com/blender/blender/blob/v4.5.1/source/blender/blenkernel/intern/appdir.cc).

## Observed comparison matrix

All rows below came from GUI sessions on the same Blender build. The four layer
controls have identical loaded add-ons, identical add-on semantic multisets, the
same 199 copied-reference Blue Hole registrations, and identical non-keymap input
preferences. Options also match within each active-preset pair.

| Capture | Active config | User candidate rows | Blue Hole registrations |
| --- | --- | ---: | ---: |
| Full reference | BH_Keymaps | 4,263 | 199 |
| Preset omitted | Blender | 4,133 | 199 |
| Saved overrides cleared | BH_Keymaps | 4,481 | 199 |
| Both omitted/cleared | Blender | 4,264 | 199 |
| Packaged pair with copied reference add-ons | BH_Keymaps | 4,260 | 199 |
| Stock | Blender | 3,654 | 0 |
| Industry Compatible | Industry Compatible | 3,140 | 0 |
| Development source in copied reference profile | BH_Keymaps | 4,241 | 199 |

Clearing overrides uses Blender's `KeyMap.restore_to_default()` after loading the
same copied preference input, with a snapshot of map identities and a fresh lookup
and keyconfig update for each reset. Blender's built-in Restore All command
invalidated its collection iterator in one disposable run; the corrected harness
avoids retaining that iterator across mutations. It does not replace unrelated
input or add-on settings with factory defaults. Omitting the preset activates the Blender
fallback. Its comparison therefore combines preset absence **and fallback
behavior**; rows are not attributed to the preset alone.

The cleared case with the preset still active retains modified flags on 12
items in eight maps. Those exact rows are marked ambiguous: distinguish
regenerated preset/runtime state from saved residue before assigning provenance.
The corrected neither case has zero modified items. Earlier exports that used
the built-in reset loop are superseded.

The two preset source hashes match:
`bdd6e34f3df3f0e8e46a1a2e9a22c588f91bc2ae8c69fb0cc3c996f64971fff3`.
The reference preference hash is
`ade8f06480896c1d9129593c820a418d8f0688172c4ff01089c33188ae25b32f`;
the packaged preference hash is
`bfa078420cbc20aee76d77f7e4e51f602977e35f62a8e11e82769d9cc14da314`.
All before/after source hashes matched. The packaged-to-reference comparison has
five additions, two removals, and one disabled binding; it is not an equivalent
preference baseline despite the identical preset files.

Development source was copied with only its declared minimum Blender version
changed from 5.2.2 to 4.5.1 for the authorized compatibility test. The checkout
was unchanged. It loaded successfully but differs from the reference by 23 added
reference occurrences, one removed occurrence, and 38 relative-order changes.
The separate factory development capture registers only two obligatory pipeline
bindings because its master keymap preference defaults off. Neither capture
establishes Blender 5.2.2 compatibility.

## Input outcomes and precedence limits

These are Blender `Window.event_simulate` events dispatched through the GUI, not
direct calls to the tested operators and not an exhaustive manual shortcut tour.
The final reference-layer, packaged, stock, and development-reference checks pass
the keyboard sentinel. Industry's snapshot is valid, but its earlier input probe
predates startup-popup dismissal; its initial negative outcomes are inconclusive.

| Input in Object Mode / 3D View | Full | No preset | No saved overrides | Neither | Development in reference profile |
| --- | --- | --- | --- | --- | --- |
| A, starting with no selection | Selects all three objects | Selects all | No selection | Selects all | Selects all |
| Ctrl-A, starting with no selection | No selection | No selection | Selects all | No selection | No selection |
| Q, starting with Move tool | Move remains active | Move remains active | Move remains active | Move remains active | Move remains active |
| Alt-left-drag | View rotates | No rotation | View rotates | View rotates | No rotation |

An unchanged tool or selection does not identify a menu/polling winner. In
particular, the Q cases remain collision/precedence work for 02/06. The observed
Alt-left-drag difference is a concrete development discrepancy; it must not be
hidden by an equal registration count. The only captured non-keymap input
preference difference from stock is `invert_mouse_zoom`. With the same
Alt-right-drag and starting view distance 10, inversion off produced 8.397436;
inversion on produced 11.742161. The focused receipt records both outcomes and
source preservation.

Final exports include vector and matrix RNA values. Input receipts from earlier
exports were retained only after confirming matching scope, order, targets,
events, activation, user flags, and all previously readable properties. The
neither input case was repeated after the corrected reset changed its bindings.

## Row contract and ownership

`row_id` is a SHA-256 over map scope, operator/modal token, complete available
event fields, effective readable RNA properties, active state, and explicit read
issues. It excludes capture role, Blender's transient item ID, and order.
`occurrence_id` also includes the duplicate ordinal, so identical duplicate
bindings are not collapsed. Map and item order are retained separately. Sample
fixtures use local subset order and preserve the source order as `native_order`.

The four roles may alias the same native keyconfig. The user role is a merged
candidate configuration, not an authoritative list of dispatch winners. Modal
tokens, unavailable schemas, unresolved enums, safe macro property groups,
inactive records, and duplicate occurrences are preserved. `is_tool` is unknown
when the runtime does not expose it; the name-based tool hint is only a hint.

The ledger has **4,509 semantic rows**: **1,032** assigned to 03,
**302** to 04, and **3,175** to 05. Observed Blue Hole runtime ownership takes
precedence; otherwise explicit operator/tool/modal rules assign one owner.
Disabled and residual/third-party/editor/global rows go to 05 unless exact
runtime ownership supplies a category. Classification reasons remain visible
for review. Industry-only comparator rows do not create migration requirements.
Omitted capture/role presence counts mean zero.

Every ledger row links to controlled delta evidence and records exact current
development coverage. An exact candidate or add-on match is not proof that Blue
Hole owns or dispatches it; separate counts identify entries from Blue Hole's
actual registered-item lists. Replacement pairing is conservative and describes
observations, not historical edit provenance.

Collision records mean active, literal event overlap within the same recorded
map scope. Wildcards, tri-state modifiers, key modifiers, drag direction, and
repeat overlap are considered. Cross-map handlers, tools, modal state,
preferences that remap events, and operator polling require native checks; no
winner is inferred from array order. Thousands of potential pairs are not
thousands of confirmed shortcut failures.

## Remaining interpretation and handoff

The 14 missing configured entries and all per-row RNA gaps remain explicit.
Their local aliases must be reconciled with intended reference availability;
absent source files are not attributed to sandbox failure. Rows with unresolved
operators or properties require that availability/schema check before migration.
The impact fixture lists 171 reference candidates whose operator RNA is
unavailable. They cannot all be attributed to the missing add-ons: obsolete
Blender or preset operator names are another possibility. Resolve a missing
module's local alias and capture its registration delta if that source is meant
to be present; record obsolete preference entries explicitly instead of inventing
operator ownership from similar names.
The repaired preset-storage startup case is separately recorded and loaded in
every final layer comparison.

Validation passed 19 focused tests, the documented sample comparison command,
and whitespace checks. The final native exports have no numeric-property
`TypeError` omissions. All owned processes exited, all copied profile/resource/
cache/recovery directories were removed, and no app copy was created. Eighteen
private snapshots remain as evidence under the ignored, owner-only evidence
directory; superseded dumps were removed. Source hashes still matched after
cleanup. No shared pin, runtime/category source, packaging, release, or deployment
path changed.

Use the recorded native rows as 02's input contract. Category owners reconcile
their assigned IDs and disabled/replacement behavior through 03–05. Brief 06
checks unresolved menu winners, cross-map/tool/modal contexts, unavailable add-on
behavior, and the observed development discrepancies. Preserve existing category
work and do not treat this baseline tooling as runtime implementation.
