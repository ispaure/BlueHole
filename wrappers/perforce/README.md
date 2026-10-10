# BlueHole Perforce adapter

The generic P4File, P4FileGroup, P4Info, status and message classes live in
[commonUtils.integrations.wrappers.perforce](../../Lib/commonUtils/integrations/wrappers/perforce/README.md).
Existing module imports re-export the shared objects without duplicate implementations.

This package supplies lazy executable, environment and binary-template providers
from BlueHole preferences. BlendP4File stays here because its filter checks and
scene-reload callback depend on Blender. Existing Windows override preferences
continue to use the macOS-named fields, matching the previous implementation.
