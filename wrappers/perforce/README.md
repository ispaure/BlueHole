# BlueHole Perforce adapter

The generic P4File, P4FileGroup, P4Info, status and message classes live in
[commonUtils.integrations.wrappers.perforce](../../Lib/commonUtils/integrations/wrappers/perforce/README.md).
Callers import generic models directly from that vendored package; former
forwarding modules have been removed.

This package supplies lazy executable, environment and binary-template providers
from BlueHole preferences. Add-on startup calls `initialize_runtime()` before
loading model consumers; provider registration does not read preferences.
BlendP4File stays here because its filter checks and
scene-reload callback depend on Blender. Existing Windows override preferences
continue to use the macOS-named fields, matching the previous implementation.
