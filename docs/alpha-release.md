# Blender 5.2.2 alpha packaging

The adapter exposes Check, Package and Prepare GitHub release on
`blender-5.2.2/alpha` only. Add-on 6.9.21 and Blender compatibility 5.2.2 are
separate identities. No 4.5.1 source or beta/stable promotion is modified.

Use the separate Python 3.12 tooling `.venv` and explicitly install the external
headless manager. Set `BLUEHOLE_SHARED_SOURCE` to a reviewed commonUtils checkout
containing the recorded shared revision. Its exact bytes are checked in a temporary
local checkout without changing the operator's source. `BLUEHOLE_BLENDER` selects
a supported runtime for isolated native acceptance; no preferences are changed.

`python Scripts/release_adapter.py package --output test-results/release/addon.zip`
runs portable tests and shared-copy checks, then creates an installable `BlueHole/`
ZIP from `Scripts/package-files.json`. Manager and hosted artifacts use
`BlueHole-6.9.21-blender5.2.2-alpha.zip`. Unexpected/missing runtime members fail.
Tests, caches, evidence and credentials are excluded. The receipt records exact
source, shared revision, add-on version, Blender compatibility and checksum.
Dirty packages are development-only and cannot be made publishable by relabelling.

Tags use `bluehole-v6.9.21-blender5.2.2-alpha.N`. Preparation requires clean
committed source and rejects tag collisions. Missing native Blender 5.2.2 or hosted
platform acceptance keeps the candidate blocked. The validation jobs have read-only contents permissions; no dispatch is performed
by local preparation.

Draft-only capability is implemented behind exact embedded-source/checksum and
native/hosted evidence checks. It reconciles exact existing drafts before writing
and never overwrites a tag or asset. `create_draft` defaults to false in the
explicitly dispatched candidate workflow. Only its gated draft job has contents
write permission, and it targets the bluehole-alpha-review environment. Configure
required environment reviewers in repository settings before enabling operator use.
The transport never publishes a draft automatically. No upload or dispatch was run
during implementation. Manager/commonUtils pins must be made available remotely
before hosted setup can succeed; no push is performed by this work.

A draft request also requires the SHA256 from an already inspected candidate plus
the exact source commit and tag. The writer compares that reviewed digest to the
newly validated bytes before credential access or upload. First prepare with
`create_draft=false`, inspect the ZIP/embedded identity/destination, then explicitly
request draft creation with its reviewed SHA256. A rebuild that differs stops for
new review. The environment gate is additional protection, not a substitute for
this exact-artifact approval.

## Guided suites and exact-package acceptance

The descriptor declares `portable.contracts`, `blender.integration`,
`package.inspection` and `release.acceptance`. Portable cases remain under `tests/`;
Blender integration stays in `tests/blender_addon_smoke.py`, package checks stay
with the release adapter, and release acceptance stays in `Scripts/validation.py`.
This maps existing owners into contracts, native, integration and acceptance groups
without moving package code or introducing another runtime environment.

Check without a suite now runs portable/shared-copy checks plus the supported
Blender gate. Select Portable contracts for an explicitly portable-only result.
Package runs the portable gates and inspects exact ZIP membership/checksums; it
remains a development package operation. Release preparation additionally installs
that exact ZIP into the smoke test's isolated add-on directories, verifies Blender
5.2.2, exercises enable/import/export/disable cleanup, and checks complete case
inventories with no skips. Native evidence records the tested artifact SHA256;
a successful source-copy smoke test cannot substitute for that ZIP acceptance.
Focused filename patterns apply only to portable Check and cannot narrow releases.

`BLUEHOLE_HOSTED_EVIDENCE` (or the private `tools.hosted_evidence` file reference)
provides exact-source successful macOS/Linux/Windows receipts and a hosted run ID.
Missing hosted or supported native evidence fails the required acceptance phase;
no workflow is dispatched to manufacture it. Per-case JUnit reports and JSON
receipts are retained under ignored `test-results/release/` even on test failure.
Full portable inventory is recomputed at release review, so focused results cannot
be relabelled as complete coverage.

Reviewed GitHub draft runs all preparation and gates once, then pauses on its
explicit upload phase. Continuation consumes the exact manager-approved candidate
and ZIP with their checksums; it never rebuilds for upload. The existing draft
transport rechecks local/native/hosted evidence, and a durable attempt marker stops
blind retry after an uncertain provider outcome. Draft creation remains separate
from publication; beta/stable promotion remains unimplemented.

The project now requires the companion manager's `build_manager.reporting` helper.
Local editable integration can be tested against that implementation. The tracked
manager pin selects the locally reviewed implementation containing reporting. Its
manager and commonUtils commits must be available remotely before hosted/fresh
pinned setup can consume them; local pinning performs no push.
Descriptor changes require renewed trust. Portable controlled-fixture tests are
not real Blender 5.2.2 or GitHub acceptance, and no live publication/dispatch is
performed as part of source implementation.

Hosted draft continuation relocates the downloaded JUnit evidence files into its
own artifact directory before revalidating the complete source, case inventory and
ZIP checksum. It rejects missing or linked evidence before credential access; paths
from a previous runner are not treated as accessible local files.
