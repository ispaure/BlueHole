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
The action catalog, fields, key bindings and registration code remain unchanged.

Selected archive cases also check late source changes at ZIP publication and
one-pass removal selections. They use plain ZIP fixtures without optional
encryption packages and do not register the add-on.

The portable member-rebuilding module checks retained-name and stored-name
iterators, container comments, ordering, attributes, cancellation and size bounds.

Portable wiki catalog and directory snapshot/cache cases exercise junction-safe
traversal in the embedded Python version, including versions before pathlib
added `Path.is_junction`. Viewer tests remain in their Qt host suite.

The embedded driver also compiles vendored production Python sources without
importing their optional toolkits. Syntax acceptance is separate from import,
registration and runtime behavior.
