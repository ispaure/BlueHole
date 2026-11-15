# Edit Deluxe keymaps in Blender

Open **Preferences → Add-ons → Blue Hole → Addon Settings → Keymaps** with
Blender's built-in keymap preset. Use **Enable Blue Hole Keymaps & Pie Menus**.
The editor opens on **All Bindings**. Each binding owns its operator and settings. Its section tabs come from the catalog, including an **Addons** section grouped
by provider name. Rows contain at most 12 tabs and are balanced when wrapped.
Pick a section to see its **Enable … Keymaps** checkbox and subsection tabs.
**All Mesh**, for example, includes every Mesh subsection; choosing Modeling
shows **Enable Modeling Keymaps** and its bindings. The required Save As
subsection stays on. Turning off Deluxe hides the editor below its toolbar;
turning off a section hides its subsection tabs and list; turning off a
subsection hides its bindings. These changes preview immediately.

**All Bindings** clears category/subsection filters and search, and shows disabled bindings
marked as inactive. Bindings use Blender's collapsible context hierarchy, with
contexts such as Mesh nested under 3D View. Category and search filters apply
before the tree is drawn. Wide windows keep selection on the left and the
selected binding's editor on the right. Narrow windows put the editor above the list.
The context tree has its own scrollbar and a resize handle. Scrolling it leaves
the inspector in place. Unchanged metadata and tree rows are cached; edits,
filters, context expansion and provider changes refresh the relevant display.

Section and subsection tabs follow catalog additions, renames, ordering and
removals. Their selection and all browsing filters are temporary, never saved
in JSON or Blender preferences. Missing sections fall back to All Bindings;
missing subsections fall back to their parent section. The section's three-dot menu can add subsections, and
rename, reorder or delete the selected empty subsection. There is currently
no top-level section-creation UI.

Sections control organization and enable gates, not Blender dispatch contexts.
Moving an assignment preserves its event, command, scope and priority; its new
section/category enable checkboxes determine eligibility. The catalog contains 1,314 additions and 244 disable/replacement rules.
Missing providers keep their rows and saved choices visible in yellow. Independent
removals stay enabled even if a similarly named addition is unavailable.
**Expand All** opens branches containing matching bindings; **Collapse All**
returns to the roots. Expanding a branch keeps focus there instead of jumping to
the inspector's selected binding.

Click **Save and Apply Changes** to save category/section states and binding
edits to your personal profile, which survives addon updates. Valid edits preview automatically in the running
keymaps without writing JSON. The toolbar identifies unsaved live changes.
If preview fails, the previous working setup stays active and the error is shown.
**Discard** restores the saved setup and drops the draft. Browsing, filtering,
adding bindings and choosing operators do not write JSON.

Enabling and disabling the master switch applies directly. Activation failures
show the next step and restore prior preference choices if runtime setup fails.

- Select a binding to see its key, section and command settings.
  Select **Key-Binding** to search for a shortcut such as `Shift F10` or
  `Ctrl Shift A`. Use **Name** to search by command name, operator ID, Blender
  context, or add-on source such as `Zen UV`. Search respects the active filters.
- To create a number-key mode shortcut, choose the Blender mode command, an
  unmodified number press, and the **Object Non-modal** keymap. Deluxe also
  registers it in **Object Mode** so a compatible mode change runs before
  Blender's collection shortcut. The same rule applies when you recreate an
  assignment. **Enter Object Mode** keeps the collection shortcut available
  when the object is already in Object Mode.
- **Enabled** beside the assignment name turns that Blue Hole binding on or off
  without deleting it. Inactive entries start unchecked; checking one activates it.
  **KEYMAP** contains a **Keyboard / Mouse** selector, key capture,
  event phase and **Repeat** checkbox. Repeat is available for keyboard Press
  or Any events and stays visible but inactive otherwise. Changing to a mouse
  input or a non-repeating phase clears Repeat. Switching input type
  starts from A or Left Mouse, preserving modifiers. Choose the key directly in
  its dropdown (including Escape or None), or click the capture icon to enter
  the desired key or mouse button for that assignment.
  Shortcut edits affect only the selected binding. Escape cancels key capture.
  Modifier buttons cycle through Off, On and Either. Hyper appears on Blender
  versions that support it. All shortcut settings are inline.
- Click **Context** and type a Blender keymap name to change where the
  selected assignment runs. Choosing a result stages the change for that
  assignment. If a shortcut is needed in several contexts, create an
  assignment for each context. Each has independent command settings.
  **Category** and **Subsection** dropdowns sit side by side above **KEYMAP** and
  move the selected binding. Enable
  checkboxes for those groups appear only when browsing their category or subsection.
- **Add New** sits at the bottom of each supported concrete keymap context,
  including empty contexts. Container contexts use a **(Global)** child for their
  own bindings. A new row starts unassigned, with no runtime effect until configured;
  edit its key, operator and properties on the right. There is no global Add Binding
  button, setup dialog or Actions menu.
- The right pane stacks **KEYMAP**, **COMMAND** and **PROPERTIES**. Type in the
  **Operator** field to search registered operator IDs and names, or enter an ID
  for an operator that is not installed yet. Changing
  it starts with the new operator's defaults and leaves every other binding alone.
  There is no separate Commands library or command-linking option.
- **PROPERTIES** shows configured values and Blender defaults together.
  **Reset** beside an overridden value restores Blender's default for this binding.
  Boolean, integer, float, string, enum, enum-flag and fixed numeric array controls
  follow live Blender RNA metadata, including menu names such as
  `wm.call_menu_pie` → `name`. Missing operators remain saved and unregistered;
  their editable properties appear when the operator becomes available.
- **Undo**, Cmd+Z and Ctrl+Z reverse staged edits, including binding deletion,
  operator changes and setting resets. Saving, discarding or reloading clears
  the editor's undo history.
- Additions and default-change rules share the context tree. A **+** icon identifies
  a keymap added by Blue Hole Deluxe; red text with a **−** icon identifies a Blender or add-on
  keymap disable rule. Hover the row for its origin and state. An inactive added binding remains
  an addition, not a disabled Blender default. The **X** at the end of a row removes
  an addition or removes a rule and restores its original shortcut. **Undo** reverses
  either action. **Enable Rule** can temporarily turn a rule off.
  The shipped catalog contains 1,314 additions and 244 disable/replacement rules.
  Rules remain pending until an exact, unique source exists. Historical migration
  receipts record older inventories separately from these current totals.
- In Blender's native **Preferences → Keymap**, right-click the small checkbox
  immediately to the left of a binding's name and choose **Disable Binding with Blue Hole…**. Review its destination
  section and stage it; Blue Hole opens the corresponding bindings area. A
  managed disabled row offers **Restore Binding with Blue Hole** instead.
  On Blue Hole's own additions, **Disable Binding with Blue Hole** disables the
  existing **+** binding and opens it in the editor, without adding a separate
  disable rule. This also supports Undo and Discard. Adding a shortcut does not disable
  another shortcut with the same command, including Blender's original binding.
  The source is detected automatically, including add-on shortcuts. Rules
  follow an add-on being enabled or reloaded after startup; turning a rule,
  its category/subsection, or Deluxe off restores the original shortcut.
  Disables require an exact, unchanged non-modal inherited shortcut. Native user
  customizations, modal/tool maps and ambiguous matches are not modified.
  Disabling Deluxe or unloading Blue Hole restores its managed changes.
  Existing review-only targets remain inert; the supported Select All replacement
  remains available. Other Deluxe additions can overlap or take precedence over
  defaults without deleting them.
- **Save and Apply Changes** writes the profile and applies it through the runtime.
  **Discard** drops staged edits. **Reset Draft** and **Reload Profile** are
  in the gear menu beside **Enable Blue Hole Keymaps & Pie Menus**. Reset stages the catalog
  loaded when the editor opened and previews it.
  **Reload Profile** reads the current file and drops the draft after a
  successful reload. **Save and Apply Changes** publishes recovered settings
  after reviewing them. Category and section choices are saved in the same JSON
  personal profile as assignments and commands. Addon updates preserve that profile. The Deluxe master switch is saved with
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

A disposable Blender 5.2.2 preset verifies context/category filters, direct
operator selection, independent settings on bindings with identical operators,
operator changes, reset, undo, deletion, key capture, save/reload and preview
cleanup. The refactor also preserves all 5,511 effective rows, including their
order, in the tested Blender 5.2.2 plugin preset. This structural comparison does
not claim dispatch coverage for every installed provider.

The [profile API contract](deluxe-keymap-profiles.md) describes persistence,
validation and recovery. The existing Blender Keymap preferences retain
control of inherited bindings and native saved edits.

## Editing the JSON files

Enable **Keymap Settings → Edit Shipped Defaults** to author the addon catalog.
Normal editing saves the personal profile outside these files.

The small [master JSON](../keymaps/deluxe-defaults.json) lists one file per top-level
section in [deluxe-defaults-sections](../keymaps/deluxe-defaults-sections). Section
files contain their subsections, assignments and their independent commands.
Shared input records and unused legacy records remain in the master. Legacy
shared commands are separated on load and persisted on Save and Apply Changes. UI edits preview immediately but only
**Save and Apply Changes** writes these files.

After text-editor changes, use the gear menu's **Validate and Reload JSON Files**.
An invalid quote/comma reports the file, line and column. Invalid records report
their ID and missing field/reference. A bad reload retains the working setup and
shows the error; correct the file and reload again. See the [format and recovery
guide](deluxe-keymap-profiles.md#persistence-and-recovery) for section additions/removals.

During key capture, the clicked binding field reads **Input Key…** until a key or mouse button is captured; **Esc** cancels.
