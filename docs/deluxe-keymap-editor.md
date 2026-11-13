# Edit Deluxe keymaps in Blender

Open **Preferences → Add-ons → Blue Hole → Addon Settings → Keymaps** after
configuring Deluxe on the Blender preset. Assignments show the command,
shortcut, keymap context and source. Search spans all sections. The category
and section menus browse one section at a time when search is empty.

- Select an assignment and use **Capture for This Assignment** to give it its
  own shortcut. **Capture for All** changes the shared shortcut across the
  listed contexts. Escape cancels capture. **Edit Shortcut** exposes the key,
  event phase, modifiers, drag direction, key modifier and repeat.
- **Assignment Settings** lets you move the assignment or choose an existing
  command, shortcut and keymap. To add a mapping, add or select a section,
  choose **Add Assignment**, and select those three entries. **New Shortcut**
  adds an input to the library for reuse in Assignment Settings.
- The **Commands** tab has its own category and section filters based on where
  each command is used. **All Categories** includes unused commands. The
  selected command shows configured settings and additional Blender settings
  discovered from the operator. Edit a field there to change all uses, or
  choose **Use Blender default** to remove its explicit value. The assignment inspector also offers
  **This assignment only** in the field dialog, which clones the command.
  Boolean, integer, float, string, enum, enum-flag and fixed numeric array
  controls follow the resolver's RNA metadata. Flag and array controls edit
  one member at a time. Menu/tool routes and provider-managed values are
  read-only. A missing provider leaves its assignments and settings visible.
- **Disable Existing Shortcut** opens the live binding picker for the selected
  section. Choose the source and search by command, key or keymap. Review the
  selected row's event and properties before staging it. The existing proved
  Object Mode Select All route can replace Select All with Deselect All.
  Generic suppression targets can be staged and reviewed with an unsupported
  status. Use **Pick Again** when a rule's target changes or becomes ambiguous.
- **Apply Changes** writes the profile and applies it through the runtime.
  **Discard** drops staged edits. **Reset Draft** stages the shipped catalog.
  **Reload Profile** reads the current file and drops the draft after a
  successful reload. **Save Recovered Profile** publishes recovered settings
  after reviewing them. **Reset Feature Switches** acts on the separate Blender
  preference switches.

The [profile API contract](deluxe-keymap-profiles.md) describes persistence,
validation and recovery. The existing Blender Keymap preferences retain
control of inherited bindings and native saved edits.
