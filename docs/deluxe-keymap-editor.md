# Edit Deluxe keymaps in Blender

Open **Preferences → Add-ons → Blue Hole → Addon Settings → Keymaps** with
Blender's built-in keymap preset. Click **Enable Deluxe Keymaps**.
The editor has two tabs: **Bindings** and **Commands**. Bindings starts with
**All Bindings**. Its single row of section tabs comes from the catalog:
Mesh, Navigation, Object, Pipeline, Sculpt, Selection, Transform, UV, Other and Pie.
Pick a section to see its **Enable … Keymaps** checkbox and subsection tabs.
**All Mesh**, for example, includes every Mesh subsection; choosing Modeling
shows **Enable Modeling Keymaps** and its bindings. The required Save As
subsection stays on. Turning off Deluxe hides the editor below its toolbar;
turning off a section hides its subsection tabs and list; turning off a
subsection hides its bindings. These changes preview immediately.

**Blender Context** is an independent searchable filter, such as 3D View,
Mesh, or UV Editor. It combines with the selected section/subsection and text
search. **All Bindings** clears all filters, including search and command,
and shows disabled bindings too, marked as inactive. This makes it possible
to inspect every use of a shared command. Bindings stay in one scrolling list; wide windows
show Command, Keymap Binding and Context columns beside the selected binding's
settings. Narrow windows place the settings above the list.

Section and subsection tabs follow catalog additions, renames, ordering and
removals. Their selection and all browsing filters are temporary, never saved
in JSON or Blender preferences. Missing sections fall back to All Bindings;
missing subsections fall back to their parent section; missing contexts clear
the context filter. The section's three-dot menu can add subsections, and
rename, reorder or delete the selected empty subsection. There is currently
no top-level section-creation UI.

Sections control organization and enable gates, not Blender dispatch contexts.
Moving an assignment preserves its event, command, scope and priority; its new
section/category enable checkboxes determine eligibility. The catalog cleanup
moved 272 former Other bindings into Navigation (editor views), Selection
(editor selection), Transform (editor transforms/snapping), Sculpt (painting),
Object (Outliner/modifiers/creation/curves and text), Pipeline (files/render),
Mesh and UV. All 803 binding definitions are retained. The remaining 158 Other
bindings have General, Animation, Nodes, Sequencer, Tracking & Masks, Text & Info,
Particles and Images subsections. The ten top-level tabs are unchanged.

Click **Save and Apply Changes** to save category/section states and all other
catalog edits together. Valid edits preview automatically in the running
keymaps without writing JSON. The toolbar identifies unsaved live changes.
If preview fails, the previous working setup stays active and the error is shown.
**Discard** restores the saved setup and drops the draft. Browsing, filtering,
creating commands and linking bindings do not write JSON.

If activation asks for a review, inspect saved Blender keymap customizations
before proceeding. Activation failures show the next step in Blender and log
the failure. If the runtime cannot rebuild the shortcuts, activation restores
the prior preference choices.

- Select a binding to see its key, section and command settings.
  **View Command** opens the reusable command in the full Commands library.
  Select **Key-Binding** to search for a shortcut such as `Shift F10` or
  `Ctrl Shift A`. Use **Name** to search by command name, operator ID, Blender
  context, or add-on source such as `Zen UV`. Search respects the active filters.
- To create a number-key mode shortcut, choose the Blender mode command, an
  unmodified number press, and the **Object Non-modal** keymap. Deluxe also
  registers it in **Object Mode** so a compatible mode change runs before
  Blender's collection shortcut. The same rule applies when you recreate an
  assignment. **Enter Object Mode** keeps the collection shortcut available
  when the object is already in Object Mode.
- The checkbox beside the assignment name enables that assignment.
  **Keymap Binding** contains a **Keyboard / Mouse** selector, key capture,
  event phase and **Repeat** checkbox. Repeat is available for keyboard Press
  or Any events and stays visible but inactive otherwise. Switching input type
  starts from A or Left Mouse, preserving modifiers. Click the key to capture
  the desired key or mouse button for that assignment.
  Expand **Shared Shortcut** to see the linked assignments grouped by
  section, with each assignment's context and enabled state. **Change All**
  asks for confirmation before capturing a shortcut for the whole group,
  including inactive assignments. Escape cancels capture. **Advanced
  Shortcut** opens the full event settings for the selected assignment.
- Click **Keymap Context** and type a Blender keymap name to change where the
  selected assignment runs. Choosing a result stages the change for that
  assignment. If a shortcut is needed in several contexts, create an
  assignment for each context and reuse the same shortcut and command.
  **Binding Settings** also lets you move an assignment to another section
  or choose an existing command, shortcut and Blender context. To add a binding,
  choose **Add Binding** and select its subsection, command, input and context.
  **Actions → New Shortcut** adds an input to the library for reuse in Binding Settings.
- **Commands** is the complete reusable library, including unused commands.
  Its optional section/subsection filters follow where commands are used;
  commands themselves do not belong to sections. **New Command** chooses a
  registered Blender operator and optional name. **Duplicate** creates an
  independent variation. **Add Binding** opens the binding dialog with that
  command already selected. **Delete Unused** is available only when no binding
  or replacement rule refers to the command.
- Editing in Commands affects every linked binding, including disabled ones.
  The inspector shows the usage count and **View All Bindings**, which clears
  search, section and context filters and shows only that command's bindings.
  In a binding's inspector, command editing defaults to **This Binding Only**:
  shared commands are copied automatically on the first edit; further edits
  reuse the private command. Choose **All Linked Bindings** to edit the shared
  definition explicitly. This applies to inline fields, reset buttons and
  array/flag dialogs.
- Expand **Additional Blender Settings** to see fields using Blender defaults.
  The **×** beside a configured value restores its default. Boolean, integer,
  float, string, enum, enum-flag and fixed numeric array controls follow live
  Blender RNA metadata. Menu/tool routes and provider-managed values remain
  read-only. Missing add-on operators show **Waiting for add-on** and leave
  the binding unregistered until the provider loads.
- **Blender Defaults & Overrides** above the assignment list shows default
  disables, replacements and review-only targets. It follows the same section,
  context and command filters; **All Bindings** shows all rules. **Browse Blender Defaults** opens a searchable live picker.
  Select an exact binding, choose its destination section, and stage
  **Disable binding with Blue Hole**. The disable previews immediately;
  **Save and Apply Changes** persists it. **Restore Binding** removes the rule
  in the draft, and **Enable Rule** can temporarily turn it off.
- In Blender's native **Preferences → Keymap**, right-click a binding's key or
  checkbox and choose **Disable Binding with Blue Hole…**. Review its destination
  section and stage it; Blue Hole opens the corresponding override list. A
  managed disabled row offers **Restore Binding with Blue Hole** instead.
  Disables require an exact, unchanged non-modal Blender default. Native user
  customizations, modal/tool maps and ambiguous matches are not modified.
  Disabling Deluxe or unloading Blue Hole restores its default changes.
  Existing review-only targets remain inert; the supported Select All replacement
  remains available. Other Deluxe additions can overlap or take precedence over
  defaults without deleting them.
- **Save and Apply Changes** writes the profile and applies it through the runtime.
  **Discard** drops staged edits. **Reset Draft** and **Reload Profile** are
  in the gear menu beside **Enable Deluxe Keymaps**. Reset stages the catalog
  loaded when the editor opened and previews it.
  **Reload Profile** reads the current file and drops the draft after a
  successful reload. **Save and Apply Changes** publishes recovered settings
  after reviewing them. Category and section choices are saved in the same JSON
  catalog as assignments and commands. The editor warns that installing a Blue
  Hole update replaces these edits. The Deluxe master switch is saved with
  Blender preferences; legacy feature switches no longer gate the catalog.

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
The shared library now contains [Zen UV 5.4.0](https://zenmastersteam.github.io/Zen-UV/latest/changelog/release_note_5.4.0/),
which uses the extension module `bl_ext.logistics.ZenUV`. Logistics' regular
Launch flow resolves a selected legacy Zen UV identity to that extension,
removes the managed old module, and installs the newest declared-compatible
package before launching. The Blue Hole automatic-update choice does not gate
updates to other selected add-ons. An unselected add-on is not added on launch.

`tests/blender_zenuv.py` exercised the actual Logistics legacy-to-extension
upgrade in disposable presets on Blender 4.5.1, 5.2.2 and 5.3.0. Native
Ctrl+Shift+Wheel Left moved the UV cursor to (0, 1), and Ctrl+Shift+Alt+MMB
fitted selected UVs into the fixture trim on all three. Both operator IDs and
properties remain compatible, so no shortcut substitution was necessary.
The 4.5.1 test changes only the copied Blue Hole minimum version; this branch
still targets 5.2.2. Zen UV itself reports 5.3.0 outside its tested range;
these two successful gestures are not a claim that every Zen UV feature works
on that build. The private provider ZIP is never included in Blue Hole.


Both Zen UV gestures were also replayed in a disposable copy of the Reference
4.5.1 profile. Ctrl+Shift+Wheel Left and the reference-only Wheel Down variant
both moved the UV cursor to (0, 1).
Ctrl+Shift+Alt+MMB fitted the selected UVs inside the active trim. The
Reference keyconfig and preference file hashes matched before and after.

A disposable Blender 5.2.2 preset verifies Bindings and Commands, combined
section/context filters, command creation/duplication and binding reuse,
shared and single-binding command edits and key capture,
typed key search, keymap context changes, inline command settings, and
the supported Select All replacement in the binding picker. Apply,
Discard, Reload Profile and a cold relaunch were also verified.

The [profile API contract](deluxe-keymap-profiles.md) describes persistence,
validation and recovery. The existing Blender Keymap preferences retain
control of inherited bindings and native saved edits.

## Editing the JSON files

The small [master JSON](../keymaps/deluxe-defaults.json) lists one file per top-level
section in [deluxe-defaults-sections](../keymaps/deluxe-defaults-sections). Section
files contain their subsections, assignments and local commands/events; shared
commands/events remain in the master. UI edits preview immediately but only
**Save and Apply Changes** writes these files.

After text-editor changes, use the gear menu's **Validate and Reload JSON Files**.
An invalid quote/comma reports the file, line and column. Invalid records report
their ID and missing field/reference. A bad reload retains the working setup and
shows the error; correct the file and reload again. See the [format and recovery
guide](deluxe-keymap-profiles.md#persistence-and-recovery) for section additions/removals.

During key capture, the clicked binding field reads **Input Key…** until a key or mouse button is captured; **Esc** cancels.
