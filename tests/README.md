# Blue Hole validation

Run `python -m unittest discover -s tests -v` for the existing adapter contracts.
They use isolated fixtures and the actual vendored library without Blender startup.
They do not connect to Perforce or validate add-on registration.

## Embedded shared-library smoke test

With an installed Blender executable, run from the repository root:

```sh
python tests/blender_shared_smoke.py --blender "/path/to/Blender"
```

The launcher selects background factory startup, disables blend-file autoexecution
and supplies temporary user resource/configuration folders before Blender starts.
The script reuses selected existing portable shared regression modules for streams,
range buffers, batch outcomes, publication, recovery envelopes, provider boundaries,
renaming, SSE and JSON/XML. Selected unencrypted ZIP extraction cases need no
optional cryptography dependency. Blue Hole retains only namespace/lifecycle and
embedded-command checks; shared assertions stay in their library test owners.
Both standalone and vendored namespaces load the actual committed vendor copy and
keep separate registries. Legacy diagnostic dialogs are disabled during the suite.
It neither registers Blue Hole nor opens or saves user projects/preferences.
Failures produce a nonzero process status; no additional packages are installed.

The printed JSON records Blender, embedded Python, the shared revision and test/skip
counts. Skipped platform cases do not establish coverage.
Passing on an older Blender establishes only those portable contracts in that
runtime. It does not establish compatibility of the target branch's registration,
operators, UI or exports. Use the declared target Blender for those separate checks.
