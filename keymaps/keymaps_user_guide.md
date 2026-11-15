# Blue Hole keymaps: user guide

Blue Hole Deluxe lets you organize shortcuts, give each shortcut its own command
and settings, and disable specific shortcuts supplied by Blender or other add-ons.
Changes preview immediately. You decide when to save them.

## Open the editor

1. Open Blender's **Preferences → Add-ons → Blue Hole**.
2. Choose **Addon Settings → Keymaps**.
3. Turn on **Enable Deluxe Keymaps**.

Use Blender's built-in keymap preset. If activation asks you to review existing
Blender keymap customizations, read that review before proceeding.

The editor opens on **All Bindings**. The list is on the left and the selected
binding's settings are on the right. Widen Preferences if the settings appear
above the list instead. The list has its own scrollbar and resize handle, so you
can scroll through bindings while keeping their settings visible.

## Understand the rows

| Row | Meaning | What its **X** does |
| --- | --- | --- |
| **+** | A shortcut added by Blue Hole | Deletes that Blue Hole binding |
| **−**, with red text | A rule that disables a particular Blender or add-on shortcut | Removes the rule and restores the original shortcut when it is still managed by Blue Hole |

Hover a row to see its origin and state. Red text identifies a disable rule; it
does not mean the target is necessarily available or currently disabled. Select
the rule to read its status. For example, an add-on rule can be waiting for its
add-on to load.

An inactive **+** row is still a Blue Hole addition. It does not become a **−**
rule when you turn it off. **Undo** reverses a deletion or other staged change.

**Adding a shortcut does not automatically disable another shortcut with the same
command.** For example, Blue Hole's Cmd/Ctrl+Y Redo additions can coexist with
Blender's Shift+Cmd/Ctrl+Z Redo shortcuts. A disable rule targets one particular
binding, not every shortcut that calls `ed.redo`.

## Find a binding

- Choose **Name** to search by a command's name or operator ID, such as `Redo`,
  `ed.redo`, or `wm.call_menu_pie`.
- Choose **Key-Binding** to search for an input, such as `Ctrl Y`, `Cmd Y`,
  `Shift F10`, or `Ctrl Shift A`.
- Pick a category, such as **Mesh**, then a subsection, such as **Tools**, to
  narrow the list. Search uses the current category and subsection filters.
- Choose **All Bindings** to clear those filters and the search.

Expand the arrows to browse Blender contexts. A parent such as **3D View** can
contain **3D View (Global)**, **Mesh**, **Object Mode**, and other contexts.

### Category and context are different

**Category / Subsection** organize the Blue Hole editor and determine which group
enable switches apply. **Context** determines where Blender listens for the
shortcut.

For example, placing a binding in the **Mesh** category does not by itself make
it work only in Mesh Edit Mode. Its **KEYMAP → Context** must also be appropriate.
Moving a binding between categories preserves its shortcut, command, and context.

## Edit a shortcut

Select a **+** row. The right pane contains:

1. **Enabled**: temporarily turn this Blue Hole binding on or off without deleting it.
2. **Category / Subsection**: choose where to organize it.
3. **KEYMAP**: choose its Blender context and input.
4. **COMMAND**: choose what it does.
5. **PROPERTIES**: adjust that command's settings for this binding.

Each binding has independent command settings. Changing one binding's operator
or properties does not change another binding, even if they use the same operator.

### KEYMAP options

| Option | What it controls |
| --- | --- |
| **Context** | The Blender keymap in which the shortcut is registered |
| **Keyboard / Mouse** | The kind of input |
| Key or mouse button | The input to listen for; choose it from the dropdown or use the capture control |
| Event phase | Whether it runs on Press, Release, Drag, Double Click, or another supported event |
| **Repeat** | Whether holding a keyboard key can repeat the command; available for Press and Any events |
| **Any** modifier | Accept any modifier combination |
| **Shift / Ctrl / Alt / Cmd** | Whether each modifier must be held; buttons cycle through Off, On, and Either |
| **Key Modifier** | An additional ordinary key that must be held with the input |
| **Direction** | The direction used for directional events such as dragging |

**Cmd** is the operating-system modifier, also shown as **OS Key** in shortcut
summaries. **Hyper** appears on Blender versions that support it.

Changing to a mouse input or to a phase that cannot repeat clears **Repeat**.
Changing between keyboard keys keeps compatible settings.

Press **Esc** to cancel key capture. To bind Escape itself, choose it directly in
the key dropdown. A command can have several bindings in different contexts;
create and configure each binding separately.

### COMMAND and PROPERTIES

Type into **Operator** to search available commands by name or ID. You can also
enter an operator ID that is not currently available, for example from an add-on
that has not been enabled yet. The binding is kept, but cannot run until that
operator is available. Its editable properties appear when Blender can describe it.

Changing the operator starts with the new operator's defaults. **PROPERTIES**
shows the available settings and their current values. Use **Reset** beside an
overridden value to return that setting to the operator's default.

For example, a pie-menu binding can use:

```text
Operator: wm.call_menu_pie
Name:     BLUEHOLE_MT_pie_add
```

The operator opens a pie menu; its **Name** property chooses which menu to open.

## Add a shortcut

1. Find the Blender context where the shortcut should work.
2. Expand its concrete keymap list, such as **3D View (Global)** or
   **Object Mode (Global)**.
3. Click **Add New** at the bottom of that list.
4. Set the category/subsection, shortcut, operator, and properties on the right.
5. Try the shortcut in the appropriate Blender editor and mode.
6. Click **Save and Apply Changes** when satisfied.

A new row starts unassigned and has no runtime effect until configured.
**Add New** creates a **+** binding. To create a **−** rule, select the existing
shortcut through Blender's native Keymap page as described below.

## Disable an existing shortcut

Open **Preferences → Keymap** in Blender's left sidebar. This is Blender's native
keymap page, separate from Blue Hole's editor.

1. Search for the shortcut you want to disable. Check its key combination and
   context: several rows can have the same command name.
2. **Right-click the small checkbox immediately to the left of the shortcut's
   name.** Clicking the name or empty row is not the same target. The checkbox's
   context menu has the heading **Active**.
3. Choose **Disable Binding with Blue Hole**.

What happens next depends on who supplies that binding:

| Binding origin | Result |
| --- | --- |
| Blender or another add-on | A dialog lets you choose the destination section. Keep **Disable binding with Blue Hole** checked and click **Stage Rule**. A **−** rule appears in Blue Hole. |
| Blue Hole | The existing **+** binding is turned off and opened in the editor. No extra **−** rule is created. |

The change previews immediately. Finish with **Save and Apply Changes** in the
Blue Hole editor to keep it.

The action requires an identifiable, unchanged binding. A user-created or
natively edited row, ambiguous duplicate, or unsupported modal/tool target may
not offer it. This avoids disabling a different binding that happens to look similar.

### Restore or temporarily re-enable a shortcut

- For a **−** rule, turn off **Enable Rule** to stop applying it temporarily.
  Use its **X** or **Restore Binding** to remove the rule completely.
- A native row already disabled by a Blue Hole rule offers
  **Restore Binding with Blue Hole** in the same right-click menu.
- For an inactive **+** binding, turn **Enabled** back on in the Blue Hole editor.

Restoration preserves later native edits instead of overwriting them. Save the
result with **Save and Apply Changes**.

### Add-on shortcuts

The rule remembers the source automatically. If an add-on is absent, its rule
stays pending. Blue Hole checks for its shortcut when the add-on is enabled or
reloads, including after startup.

A rule matches the context, operator, input, and captured operator properties.
It is not a blanket instruction to disable every shortcut from an add-on. If an
add-on update changes the target, select the rule and check its status; it may
need to be captured again from the new binding.

## Enable or disable a group

Pick a category to access its **Enable … Keymaps** switch. Pick a subsection to
access that subsection's switch. These controls are deliberately kept in their
respective areas rather than shown on **All Bindings**.

Turning a group off withdraws its additions and stops applying its disable
rules. Turning it on restores the group's configured behavior. The required
Save As subsection stays enabled.

The subsection menu can add, rename, reorder, or delete an empty subsection.
There is currently no editor control for creating a top-level category.

## Preview, save, and undo

| Control | Effect |
| --- | --- |
| Live preview | Valid edits update the running keymaps immediately without writing JSON |
| **Save and Apply Changes** | Saves the draft, including binding edits, rules, and category/subsection switches |
| **Discard** | Restores the last saved setup and drops the draft |
| **Undo**, Cmd+Z, or Ctrl+Z in the Blue Hole editor | Reverses the last staged editor change |

Saving, discarding, or reloading clears the editor's undo history. If preview
fails, the previous working setup stays active and the editor reports the error.

The native **Preferences → Keymap** view reflects the live preview: additions
appear there, edits change their inputs, and disabled inherited shortcuts become
unchecked. Turning off a Blue Hole addition removes its registered native row;
its inactive **+** row remains in the Blue Hole editor.

Editing a shortcut directly in Blender's native page does **not** automatically
update Blue Hole's JSON. Likewise, Blender's **Save Preferences** button is not a
substitute for Blue Hole's **Save and Apply Changes**.

### Where changes are saved

Bindings and disable rules are stored in the catalog rooted at
[`deluxe-defaults.json`](deluxe-defaults.json), with category files in
[`deluxe-defaults-sections/`](deluxe-defaults-sections/). Minus rules are saved
alongside additions, in the relevant category file's `suppressions` section.

These files belong to the Blue Hole installation. **Installing a Blue Hole update
can replace edited keymaps.** Keep a copy of the master JSON and the entire
category-files folder before updating if you need to preserve local changes.

## Common questions

**Does adding a command replace every Blender shortcut for that command?**

No. A **+** binding adds a shortcut. A **−** rule disables a specific existing one.

**What if two shortcuts use the same key?**

They may both remain registered. Blender's context and binding order determine
which gets the event. An overlap or conflict message is a reason to review them;
it does not mean Blue Hole has silently disabled the other binding.

**Why does a shortcut work in one editor or mode but not another?**

Check **KEYMAP → Context**, then whether the operator can run in that editor/mode.
Category membership alone does not determine where it runs.

**Why is a red minus rule still waiting?**

Its add-on may not be enabled, or its exact target may have changed. Select the
rule and read its status. The red text marks its purpose, not successful application.

**Where should I change a Blue Hole shortcut?**

Use its **+** row in the Blue Hole editor to keep the change in the catalog. The
native right-click action is also available for disabling it.
