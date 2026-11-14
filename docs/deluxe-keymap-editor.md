# Edit Deluxe keymaps in Blender

Open **Preferences → Add-ons → Blue Hole → Addon Settings → Keymaps** with
Blender's built-in keymap preset. Click **Enable Keymaps**, or **Use Keymap
Editor** if you already had the older programmatic keymaps enabled.
**Sections** is the default view.
Choose a category tab, then use the category and section checkboxes to stage
which shortcut groups are enabled. Sections show when a saved feature switch
makes a group inactive or an enabled shortcut needs an add-on. Click **Save
and Apply Changes** to save. Assignments shows every result in one list.
When there is room, each assignment has one row with **Command**,
**Shortcut**, and **Context** columns. Wide windows show the selected
assignment's settings beside the list. Narrow windows show those settings
above it. Assignment search spans all sections. The category and section
menus browse one section at a time when search is empty.

If activation asks for a review, **Back Up Saved Keymap Setup** copies the
saved Blender preferences and available preset before you review conflicting
shortcuts. Save Blender Preferences first if there is no saved file. Activation
and backup failures show the next step in Blender and log the failure. If the
runtime cannot rebuild the shortcuts, activation restores the prior preference
choices.

- Select an assignment to see its shortcut, section and command settings.
  **View Command** shows the command's source, such as Blender, Blue Hole or
  a named add-on.
  The section link opens its assignments and the checkbox stages its enabled
  state. **View Commands** and **View Assignments** switch between views for
  that section. Select **Key-Binding** in Assignments to type a shortcut such
  as `Shift F10` or `Ctrl Shift A`. Use **Name** to search by command name,
  operator ID, keymap, or add-on source such as `Zen UV`.
- To create a number-key mode shortcut, choose the Blender mode command, an
  unmodified number press, and the **Object Non-modal** keymap. Deluxe also
  registers it in **Object Mode** so a compatible mode change runs before
  Blender's collection shortcut. The same rule applies when you recreate an
  assignment. **Enter Object Mode** keeps the collection shortcut available
  when the object is already in Object Mode.
- Click the key in the detail pane to capture a new key for that assignment.
  Expand **Shared Shortcut** to see the linked assignments grouped by
  section, with each assignment's context and enabled state. **Change All**
  asks for confirmation before capturing a shortcut for the whole group,
  including inactive assignments. Escape cancels capture. **Advanced
  Shortcut** opens the full event settings for the selected assignment.
- Click **Keymap Context** and type a Blender keymap name to change where the
  selected assignment runs. Choosing a result stages the change for that
  assignment. If a shortcut is needed in several contexts, create an
  assignment for each context and reuse the same shortcut and command.
  **Assignment Settings** also lets you move an assignment to another section
  or choose an existing command, shortcut and keymap. To add a mapping, add a section from the menu
  beside the section selector or select an existing one,
  choose **Add Assignment**, and select those three entries. **Actions → New
  Shortcut** adds an input to the library for reuse in Assignment Settings.
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
  read-only. Add-on commands stay in their workflow sections. When Blender
  has no matching operator, the list shows **Waiting for add-on** and Deluxe
  leaves the shortcut unregistered. The saved choice remains available for
  when the operator loads.
- **Actions → Find Existing Shortcut** opens the live binding picker for the selected
  section. Choose the source and search by command, key or keymap. Review the
  selected row's event and properties before staging it. The existing proved
  Object Mode Select All route can replace Select All with Deselect All.
  Generic suppression targets can be staged and reviewed with an unsupported
  status. Use **Pick Again** when a rule's target changes or becomes ambiguous.
- **Save and Apply Changes** writes the profile and applies it through the runtime.
  **Discard** drops staged edits. **Reset Draft** and **Reload Profile** are
  in the gear menu beside **Enable Keymaps**. Reset stages the shipped catalog.
  **Reload Profile** reads the current file and drops the draft after a
  successful reload. **Save Recovered Profile** publishes recovered settings
  after reviewing them. **Reset Feature Switches** acts on the separate Blender
  preference switches.

## Viewport pie shortcuts

Ctrl+right-click opens the action pie for the current mode, and
Shift+right-click opens its tool pie. Object Mode, Edit Mesh, Edit Curve,
Sculpt and the UV Editor each have their own assignments under **Pie → Menus**.
Ctrl+Shift+Alt+right-click also has mode-specific routes, including the Mesh
UV Special pie and Object Mode Import/Export.

In Object Mode and Edit Mesh, tap Shift+A for the mode's Add menu. Hold
Shift+A and move the mouse to open the Deluxe Add pie. While the default
Shift+A drag assignment is enabled, Deluxe opens the stock Add menus on
release. Disabling or rebinding the pie restores their press behavior.

## Add-on shortcuts

The original **Third-Party Add-ons** tab groups Blue Hole's optional
integrations by add-on. The editor groups assignments by workflow and shows
the command source separately. Search by source to find direct add-on commands.

| Add-on | Where to find it | Availability and fallback |
| --- | --- | --- |
| Group Pro | **Object → Actions** for Join Groups | Ctrl+J requires `object.join_group_override`. Blender Join remains available without Group Pro. |
| Interactive Tools | **Mesh → Modeling** for Smart Delete | Alt+D requires `mesh.smart_delete`. |
| Zen UV | **UV → Tools** for Move Cursor, **UV → Actions** for Fit to Trim | Deluxe checks `uv.zenuv_move_cursor_to` and `uv.zenuv_fit_to_trim` individually. In Blender 4.5.1 without Zen UV, both assignments remained visible as **Waiting for add-on** and neither registered a binding. |
| autoConstraints | **Third-Party Add-ons → Auto Constraints**, with W/E/R in **Transform → Modal tools** | The panel checks `transform.translate_auto_constraint`. Each shortcut checks its own Translate, Rotate or Resize provider operator and uses the corresponding Blender transform when the operator is missing or the integration is off. |
| X-Ray Selection Tools | **Third-Party Add-ons → X-Ray Selection Tools**, with Q in **Selection → Tool switch** | The panel checks `mesh.select_box_xray`. Object and Mesh try their respective X-Ray Box tools when enabled and use Blender's Box Select if activation fails. Curve and Curves use Blender's Box Select. The 4.5.1 replay tested both provider and fallback behavior with X-Ray Selection Tools 4.9.0. |
| Blender FBX | **Pipeline → Export** | Deluxe checks `export_scene.fbx`. The bundled exporter registered in Blender 4.5.1, and Ctrl+Shift+E exported the test mesh. |

The **Third-Party Add-ons** controls reflect whether their Deluxe sections
are enabled. The availability checks read registered Blender operators.
In a disposable Blender 5.2.2 preset, Reference's autoConstraints 1.4.1
received native W/E/R input. In Mesh Edit Mode, Alt+D invoked Interactive
Tools 1.4.1 Smart Delete and removed the selected faces. In Object Mode,
Ctrl+J invoked Group Pro 3.0.6 and joined two test meshes. Their mode-specific
keymaps let the provider commands run ahead of Blender's own bindings.
Without the add-ons, the assignments showed **Waiting for add-on** and
registered no keymap items.

Reference's Zen UV 5.0.3.0 and X-Ray Selection Tools 4.9.0 failed to load
on 5.2.2. Zen UV's two bindings stayed inactive and Q used Blender Box Select.
The [X-Ray Selection Tools 4.10.2 update](https://extensions.blender.org/add-ons/xray-selection-tools/versions/)
loaded in a separate 5.2.2 preset. Q activated X-Ray Box in Object and Mesh
and returned to Blender Box Select after the integration was switched off.
[Zen UV 5.4](https://zenmastersteam.github.io/Zen-UV/latest/) lists support for
Blender 5.2 LTS. The shared add-on library and the Blender installations
checked contain Zen UV 5.0.3.0. Verification of both shortcuts with a
compatible package remains open. The artist guide lists the mappings and
their add-on requirements.

Both Zen UV gestures were also replayed in a disposable copy of the Reference
4.5.1 profile. Ctrl+Shift+Wheel Left and the reference-only Wheel Down variant
both moved the UV cursor to (0, 1).
Ctrl+Shift+Alt+MMB fitted the selected UVs inside the active trim. The
Reference keyconfig and preference file hashes matched before and after.

A disposable Logistics preset on Blender 5.2.2 verified the Sections,
Assignments and Commands views, shared and single-assignment capture,
typed key search, keymap context changes, inline command settings, and
the supported Select All replacement in the binding picker. Apply,
Discard, Reload Profile and a cold relaunch were also verified.

The [profile API contract](deluxe-keymap-profiles.md) describes persistence,
validation and recovery. The existing Blender Keymap preferences retain
control of inherited bindings and native saved edits.
