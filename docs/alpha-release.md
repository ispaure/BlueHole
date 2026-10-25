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
