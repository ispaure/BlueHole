# Deluxe keymaps

Enable Blue Hole and select the built-in **Blender** keymap preset. In Blue
Hole's **Addon Settings → Keymaps**, choose **Enable Blue Hole Keymaps & Pie Menus** to open
the catalog. The same command is available under **Keymaps & Pie Menus** in the
Blue Hole header menu. Blue Hole registers the shortcuts and pies at runtime.

Use the editor's **Sections** tab to enable categories and sections, including
**Pie**. Valid edits preview automatically without saving. **Discard** restores
the saved setup. **Save and Apply Changes** writes those choices, assignments and command
settings to `keymaps/deluxe-defaults.json` and its section files in the active Blue Hole installation.
**Installing a Blue Hole update replaces these edits with the shipped catalog.**
The editor displays this warning on all three tabs. With Logistics' Local source,
the installation links to the checkout, so catalog edits appear in Git.

**Disable Blue Hole Keymaps & Pie Menus** removes the shortcuts and keeps the JSON
choices for the next enable. Blender preferences store the Deluxe master switch
and an internal first-activation marker. Save Blender Preferences to keep that
switch across sessions when Auto-Save Preferences is off. Native edits made in
Blender's own Keymap preferences also remain Blender-managed. The old category,
section and pie preference switches no longer control the Deluxe catalog.

The required Blue Hole Save As shortcuts remain while the add-on is enabled.
**Reset Draft** restores the catalog loaded when the editor opened, and takes
effect immediately as a preview, saved only with **Save and Apply Changes**. **Invert Mouse Zoom** remains a separate
Blender input preference in the gear menu.

## Existing Blender keymap customizations

The installer for the previous Deluxe system copied `BH_Keymaps.py` and
`userpref.blend`. Logistics' Blender 5.2.2-and-newer install/update path does
not apply those payloads. It loads and saves existing Blender preferences to
record the enabled add-on selection, preserving the other saved settings.
Existing legacy files are left in place.

If a profile still uses the old preset, select **Blender** in
**Preferences → Keymap** and review any saved customizations before enabling
Deluxe. Keep personal shortcuts and resolve conflicting edits from the old
setup. The toggle applies directly without a review popup; it does not overwrite
or remove the old profile. The obsolete **Back Up Saved Keymap Setup** command
was removed: copying `userpref.blend` did not back up the current JSON editor.

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
