# Deluxe keymaps

Enable Blue Hole and select the built-in **Blender** keymap preset. In Blue
Hole's **Addon Settings → Keymaps**, choose **Enable Keymaps** or **Use Keymap
Editor** to open the Deluxe catalog. You can also choose **Enable Deluxe
Keymaps** under **Updates & Deluxe** in the Blue Hole header menu. Blue Hole
adds the shortcuts and pies at runtime. Every feature group starts enabled in
a fresh profile.

Use **Addon Settings > Keymaps**, **Pie Menus**, and **Third-Party Add-ons** in
Blue Hole preferences to change features. **Disable Deluxe Keymaps** removes
the runtime catalog and its pie shortcuts and keeps your feature choices for
the next enable. Blender saves the Blue Hole activation and feature switches
on normal exit if **Auto-Save Preferences** is enabled. Otherwise choose
**Save Preferences** in Blender to keep the choice across sessions. The
shortcut editor's **Save and Apply Changes** writes assignment edits to
`keymaps/deluxe-defaults.json` in the active Blue Hole installation.
The standard Blue Hole Save As shortcut is part of Blue Hole's pipeline while
the add-on is enabled. Disable Blue Hole to restore the stock Save As shortcut.

**Reset Deluxe Feature Switches** restores the Blue Hole keymap, pie, and
supported third-party shortcut switches to their Deluxe defaults. It leaves
the current activation state and your Blender bindings in place. **Invert
Mouse Zoom** is available in the Keymaps panel as a separate Blender input
preference. Set it to match your preferred zoom direction.

## Move an existing profile to runtime Deluxe

The previous installer copied both a preset and a preferences file. The new
version waits for a reviewed switch when it finds evidence of that installation.
It also asks you to review saved keymap edits on first Deluxe activation.
Blender can carry saved edits across a preset switch, and their origins can be
ambiguous.

1. Save your current Blender preferences. Choose **Back Up Saved Keymap Setup**
   under **Updates & Deluxe**. The command reports a new recovery directory
   next to the saved preferences. It copies the saved settings and available
   preset. Keep any older recovery copies too.
2. In **Preferences > Keymap**, select **Blender**. Review saved customizations
   and resolve shortcuts that came from the old Deluxe setup. Keep personal
   bindings. If you are unsure which edits to keep, use your current setup
   until you can review them. You can compare against a pre-Deluxe backup
   in a separate Blender profile if one is available.
3. Choose **Enable Deluxe Keymaps** and confirm your review. Check your
   shortcuts, then use Blender's **Save Preferences** when ready.

To return to the previous setup, disable Deluxe and select the old preset in
**Preferences > Keymap**. To recover the exact settings from the backup, close
Blender and keep a copy of your current files first. Restore the saved
`userpref.blend` and, if needed, the matching preset to the active profile.
That restores other preferences as of the backup too. The runtime activation
keeps the legacy preset, recovery copies, ordinary preferences, and installed
add-ons in place.

## Shortcut coverage

Shortcuts that need external add-ons depend on those add-ons being installed
and enabled. Supported overrides wait for the provider's bindings. Known
gaps include unsupported native modal bindings, the two Zen UV shortcuts in
the factory-profile test, and the SpaceMouse Roll CCW pair whose hardware
behavior still needs verification. Some composed UV, Sculpt, Tool Pie, and
export workflows still need native parity checks. The detailed exceptions are
recorded in the [Navigation, Selection and Transform](../../docs/deluxe-keymaps-category03.md),
[Object, Mesh and UV](../../docs/deluxe-keymaps-category04.md), and
[Sculpt, Pipeline, Other and Pie](../../docs/deluxe-keymaps-category05.md)
receipts. The original preset and preference snapshot are available in Git
history. The source checkout and installable ZIP use the runtime catalog.
