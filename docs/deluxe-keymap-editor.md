# Edit Deluxe keymaps in Blender

Open **Preferences → Add-ons → Blue Hole → Addon Settings → Keymaps** after
configuring Deluxe on the Blender preset. **Sections** is the default view.
Use its category and section checkboxes to stage which shortcut groups are
enabled, then click **Apply Changes**. Assignments and Commands put their list
beside the selected item's settings in wide windows. In narrow windows the
settings appear below the list. Assignment search spans all sections. The
category and section menus browse one section at a time when search is empty.

- Select an assignment to see its shortcut, keymap context, command source
  and section. The section link opens its assignments and the checkbox stages its enabled
  state. **View Commands** and **View Assignments** switch between views for
  that section. Select **Key-Binding** in Assignments to type a shortcut such
  as `Shift F10` or `Ctrl Shift A`. Use **Name** to search by command name,
  operator ID, or keymap.
- Click the key in the detail pane to capture a new key for that assignment.
  Expand **Linked assignments** to see the contexts affected by **Capture for
  All**. Escape cancels capture. The pane places the key, event phase,
  and keyboard repeat above the modifier buttons. **Advanced Shortcut** offers
  the full event settings and shared editing.
- Click **Keymap Context** and type a Blender keymap name to change where the
  selected assignment runs. Choosing a result stages the change for that
  assignment. If a shortcut is needed in several contexts, create an
  assignment for each context and reuse the same shortcut and command.
  **Assignment Settings** also lets you move an assignment to another section
  or choose an existing command, shortcut and keymap. To add a mapping, add a section from the menu
  beside the section selector or select an existing one,
  choose **Add Assignment**, and select those three entries. **New Shortcut**
  adds an input to the library for reuse in Assignment Settings.
- The **Commands** tab has its own category and section filters based on where
  each command is used. Picking a category or section clears the text search.
  **All Categories** includes unused commands. The
  selected command shows configured settings. Expand **Additional Blender
  Settings** to see the remaining fields discovered from the operator.
  Edit a field inline to change all uses. Use
  the **×** beside a configured value to restore Blender's default. The
  duplicate icon in an assignment's command settings opens the field dialog
  with a **This assignment only** option, which clones the command.
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
  **Discard** drops staged edits. **Reset Draft** and **Reload Profile** are
  in the **Profile** menu. Reset stages the shipped catalog.
  **Reload Profile** reads the current file and drops the draft after a
  successful reload. **Save Recovered Profile** publishes recovered settings
  after reviewing them. **Reset Feature Switches** acts on the separate Blender
  preference switches.

The [profile API contract](deluxe-keymap-profiles.md) describes persistence,
validation and recovery. The existing Blender Keymap preferences retain
control of inherited bindings and native saved edits.
