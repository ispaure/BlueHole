# Blue Hole Deluxe
Blue Hole Deluxe is a custom configuration for Blender that changes the userpref.blend file, applying new `keymaps` and `pie menus`. Install instructions here: https://blue-hole.weebly.com/installation.html

## Deluxe Overrides the UserPref.blend preference file!
If you are attached to your current settings, back them up before installing Blue Hole Deluxe.

## Documentation
The Documentation for Blue Hole Deluxe can be accessed in Blender through the Blue Hole header menu.

## Verified installation and recovery

Each preferences/keymap payload is copied to private staging beside its target
and verified before publication. Interrupted or corrupt copies leave the existing
file intact. Publication retains the previous file as `<name>.previous-<id>` in
the same directory and logs its path. Keep those recovery files until the new
configuration has been checked. To restore, close Blender and copy the selected
recovery file back to its original name.

The two files are installed separately. If the second fails, the first may already
be installed; the error lists verified destinations and Blender stays open.
Recovery copies are never cleaned automatically. Existing read-only targets are
made writable only after staging has passed verification. No-replace publication
rejects a target created by another writer; failed restoration retains and reports
the old recovery file. Adapter tests use temporary settings outside Blender; a
live Blender 5.2.2 installation remains a separate validation step.
