These tables cover common artist shortcuts from the
[bundled Deluxe profile](../../../keymaps/deluxe-defaults.json) for Blender
5.2.2. Rows marked **Blender** come from the built-in Blender preset. The
**Add-on** column shows dependencies and optional integrations. For the
full list and your saved changes, open **Addon Settings > Keymaps > Assignments**
in Blue Hole preferences. The **Sections** tab controls which shortcut groups
are enabled. See the [Deluxe guide](../README.md) for setup.

> [!NOTE] Mouse-related acronyms
> - LMB: Left Mouse Button
> - MMB: Middle Mouse Button
> - RMB: Right Mouse Button

# 📖 TABLE OF CONTENTS

- [💾 SYSTEM](#-system)
- [📷 CAMERA NAVIGATION](#-camera-navigation)
- [🪟 LAYOUT](#-layout)
- [👉 SELECTION](#-selection)
- [Transform](#transform)
- [🧊 MODELING MODE](#-modeling-mode)
- [UV EDITOR](#uv-editor)
- [🎨 SCULPTING MODE](#-sculpting-mode)
- [Add-on shortcuts](#add-on-shortcuts)
- [Additional information](#additional-information)

# 💾 **SYSTEM**

## Scene Management

| **Action** | **Keymap 1** | **Keymap 2** | **Note/Status** | **Add-on** |
| --- | --- | --- | --- | --- |
| Save | Ctrl + S | Cmd + S | Blender | |
| Save As | Ctrl + Shift + S | Cmd + Shift + S | Blue Hole Save As | |
| Undo | Ctrl + Z | | Blender | |
| Redo | Ctrl + Shift + Z | Ctrl + Y / Cmd + Y | The Y shortcuts are from Deluxe | |
| Repeat Last | G | | Screen and UV Editor | |
| Search Menu | Space Bar | | 3D View and Image Editor. Tab is also assigned in several editors, including UV and Outliner | |
| Export FBX | Ctrl + Shift + E | | | Blender FBX (bundled) |

## Asset Management

| **Action** | **Keymap 1** | **Keymap 2** | **Note/Status** | **Add-on** |
| --- | --- | --- | --- | --- |
| Add / Create | Shift + A | | Blender Add menu. The Deluxe Add pie uses click-drag in the 3D View | |
| Duplicate | Shift + D | | Blender, in Object Mode and Mesh Edit Mode | |
| Duplicate Linked | Alt + D | | Blender, in Object Mode. The Outliner has a Deluxe linked duplicate on Shift + D | |
| Delete | Alt + Shift + D | Delete | Deluxe 3D View assignment and Blender Object Mode binding, respectively | |
| Join Groups | Ctrl + J | | Object Mode. Blender Join is inherited when Group Pro is unavailable | Group Pro (required) |
| Copy / Paste Objects | Ctrl + C | Ctrl + V | Blender 3D View copy buffer and paste buffer | |

## Collections / Parenting

| **Action** | **Keymap 1** | **Keymap 2** | **Note/Status** | **Add-on** |
| --- | --- | --- | --- | --- |
| Move to Collection | Ctrl + G / Cmd + G | M | Deluxe in the Outliner. M is Blender's Object Mode shortcut | |
| Link to Collection | Ctrl + Shift + M / Cmd + Shift + M | Shift + M | Deluxe in the Outliner. Shift + M is Blender's Object Mode shortcut | |
| Parent | Ctrl + P | | Blender, Object Mode | |
| Clear Parent | Alt + P | | Blender, Object Mode | |
| Extend Selection to Parent | Shift + Wheel Up | Shift + Wheel Right | Object Mode | |
| Extend Selection to Child | Shift + Wheel Down | Shift + Wheel Left | Object Mode | |

## Show / Hide

| **Action** | **Keymap 1** | **Keymap 2** | **Note/Status** | **Add-on** |
| --- | --- | --- | --- | --- |
| Hide Selection | H | | Blender, Object and Mesh Edit modes | |
| Reveal Hidden | Alt + H | | Blender, Object and Mesh Edit modes | |
| Isolate Selection / Local View | Shift + I | Numpad / | 3D View. Numpad / is inherited from Blender | |
| Hide Selection in UV | Ctrl + H | | UV Editor | |
| Hide Masked Geometry | Ctrl + H | | Sculpt Mode | |

# 📷 **CAMERA NAVIGATION**

## 3D Viewport

| **Action** | **Keymap 1** | **Keymap 2** | **Note/Status** | **Add-on** |
| --- | --- | --- | --- | --- |
| Pan | Alt + MMB Drag | Shift + MMB Drag | Second shortcut uses Blender's default mouse navigation | |
| Zoom | Alt + RMB Drag | Wheel Up/Down | Wheel zoom is inherited from Blender | |
| Orbit | Alt + LMB Drag | MMB Drag | Second shortcut uses Blender's default mouse navigation | |
| Frame Selection | F | Shift + Alt + Wheel Up/Right | | |
| Frame Selection in All Views | Shift + F | | | |
| Frame All | A | Shift + Alt + Wheel Down/Left | A also has inherited selection bindings in some modes | |
| Align to Front Relative to the Current View | Shift + Alt + MMB Click | | | |
| Back / Left / Bottom View | Ctrl + F1 / F2 / F3 | Cmd + F1 / F2 / F3 | Apply the modifier to each function key | |
| View Pie | V | | | |

## 2D Viewport

| **Action** | **Keymap 1** | **Keymap 2** | **Note/Status** | **Add-on** |
| --- | --- | --- | --- | --- |
| Pan | Alt + MMB Drag | Alt + LMB Drag | Image, Clip and View2D maps | |
| Zoom | Alt + RMB Drag | Alt + Wheel Up/Down | Wheel variant is in View2D maps | |
| Frame Selection | F | Shift + Alt + Wheel Up/Right | Image/UV map. F also frames selection in editors such as the Graph Editor and Dopesheet | |
| Frame All | A | Shift + Alt + Wheel Down/Left | Image/UV map | |

# 🪟 **LAYOUT**

| **Action** | **Keymap 1** | **Keymap 2** | **Note/Status** | **Add-on** |
| --- | --- | --- | --- | --- |
| Toggle Quad View | Ctrl + Alt + Q | | Blender | |
| Maximize Editor and Hide Panels | Ctrl + Shift + Tab | | Deluxe Window binding | |
| Maximize Editor | Ctrl + Space | | Blender | |
| Toggle Fullscreen | F11 | | macOS may intercept the key | |
| Toggle Sidebar | N | Ctrl + ] / Cmd + ] | N is inherited from Blender. The bracket aliases are in the 3D View, Dopesheet and Video Sequence Editor | |
| Toggle X-Ray | Alt + Z | | Blender | |
| Quick Favorites | Q | | Blender where the editor has no higher-priority Q shortcut | |
| Preferences | Ctrl + , | Cmd + , | Blender | |

# 👉 **SELECTION**

## Mode

Use the number row above the letters in the 3D View.

| **Action** | **Keymap 1** | **Keymap 2** | **Note/Status** | **Add-on** |
| --- | --- | --- | --- | --- |
| Vertex Select | 1 | | Enters Mesh Edit Mode from Object Mode | |
| Edge Select | 2 | | Enters Mesh Edit Mode from Object Mode | |
| Face Select | 3 | | Enters Mesh Edit Mode from Object Mode | |
| Pose Mode | 3 | | With an armature active | |
| Object Mode | 4 | | Returns from Edit Mode | |
| Sculpt / Vertex Paint / Weight Paint / Texture Paint | 5 / 6 / 7 / 8 | | With a compatible active object | |

## Click and Box

| **Action** | **Keymap 1** | **Keymap 2** | **Note/Status** | **Add-on** |
| --- | --- | --- | --- | --- |
| Click Select | LMB | | 3D View and UV Tweak tools | |
| Extend Selection | Shift + LMB Click | | Deluxe UV binding. Blender's 3D View Shift-click toggles the clicked item | |
| Subtract from Selection | Ctrl + LMB Click | | Deluxe 3D View binding. The UV Box fallback uses a drag | |
| Activate Box Select | Q | | Object, Mesh, Curve and Curves. X-Ray Box is available in Object and Mesh | X-Ray Selection Tools (optional, 4.10.2 verified) |
| Box Select | LMB Drag | RMB Drag | Blender 3D View Box tool and Deluxe UV Box fallback, respectively | |
| Box Select (Add) | Shift + LMB Drag | Shift + RMB Drag | Blender 3D View Box tool and Deluxe UV Box fallback, respectively | |
| Box Select (Subtract) | Ctrl + LMB Drag | Ctrl + RMB Drag / Cmd + RMB Drag | Blender 3D View Box tool and Deluxe UV Box fallback, respectively | |
| Box Select (Intersect) | Ctrl + Shift + LMB Drag | | Blender 3D View Box tool | |

For lasso selection, choose **Select Lasso** from Blender's toolbar. Its default
3D View drag uses LMB, with Shift to add and Ctrl to subtract.

## Circle / Paint

| **Action** | **Keymap 1** | **Keymap 2** | **Note/Status** | **Add-on** |
| --- | --- | --- | --- | --- |
| Circle Select (Add) | Shift + MMB | | 3D View and UV Editor | |
| Circle Select (Subtract) | Ctrl + MMB | | 3D View and UV Editor | |

## Loop / Ring

| **Action** | **Keymap 1** | **Keymap 2** | **Note/Status** | **Add-on** |
| --- | --- | --- | --- | --- |
| Edge Loop Selection | Alt + LMB | Shift + Alt + LMB | Blender Mesh Edit Mode. Shift toggles the loop in the selection | |
| Edge Ring Selection | Ctrl + Alt + LMB | Ctrl + Shift + Alt + LMB | Blender Mesh Edit Mode. Shift toggles the ring in the selection | |
| UV Loop Selection | Alt + LMB Double-Click | Shift + Alt + LMB Double-Click | Shift extends the selection | |

## Miscellaneous

| **Action** | **Keymap 1** | **Keymap 2** | **Note/Status** | **Add-on** |
| --- | --- | --- | --- | --- |
| Select All | A | | Blender Object and Mesh Edit modes. UV uses the shortcuts below | |
| Deselect All | Alt + A | | Blender Object and Mesh Edit modes | |
| Invert Selection | Ctrl + I | | Blender Object and Mesh Edit modes | |
| Grow Selection | Shift + Wheel Up/Right | `]` | Mesh and other editors. The bracket shortcut is for UV | |
| Shrink Selection | Shift + Wheel Down/Left | `[` | Mesh and other editors. The bracket shortcut is for UV | |
| Pick Shortest Path | Ctrl + LMB | | Blender Mesh Edit Mode | |
| Pick Shortest Path (Fill Region) | Ctrl + Shift + LMB | | Blender Mesh Edit Mode | |

# Transform

## Basic Tools

| **Action** | **Keymap 1** | **Keymap 2** | **Note/Status** | **Add-on** |
| --- | --- | --- | --- | --- |
| Move / Rotate / Scale | W / E / R | | 3D View and UV Editor. Supported 3D modes can use autoConstraints | autoConstraints (optional in 3D modes) |
| Move / Rotate / Scale Gizmo | Shift + W / E / R | | Apply Shift to each key. Available in supported 3D modes and in the UV Editor | |

## Constraints and Snapping

| **Action** | **Keymap 1** | **Keymap 2** | **Note/Status** | **Add-on** |
| --- | --- | --- | --- | --- |
| Constrain to X / Y / Z | X / Y / Z | | Blender, during a transform | |
| Constrain to YZ / XZ / XY | Shift + X / Y / Z | | Blender, during a transform. Shift excludes that axis | |
| Toggle Snapping | X | | 3D View and UV Editor, before starting a transform | |
| Snapping Settings | Shift + X | | 3D View | |
| Temporarily Invert Snapping | Hold Ctrl | | Blender, during a transform | |
| Toggle Proportional Editing | O | | Blender. The Deluxe B binding is specific to Particle Edit | |
| Proportional Falloff Menu | Shift + B | Shift + O | Shift + O is inherited from Blender | |
| Increase / Decrease Falloff Radius | Page Up / Page Down | Shift + Wheel Down / Up | Blender, during a proportional transform | |

## 3D Cursor

| **Action** | **Keymap 1** | **Keymap 2** | **Note/Status** | **Add-on** |
| --- | --- | --- | --- | --- |
| Move 3D Cursor | Ctrl + Shift + MMB Drag | | 3D View | |
| Snap Cursor to Selection | Ctrl + Shift + Wheel Up | Ctrl + Shift + Wheel Right | 3D View | |
| Snap Cursor to World Origin | Ctrl + Shift + Wheel Down | Ctrl + Shift + Wheel Left | 3D View | |

# 🧊 **MODELING MODE**

| **Action** | **Keymap 1** | **Keymap 2** | **Note/Status** | **Add-on** |
| --- | --- | --- | --- | --- |
| Smart Delete | Alt + D | | Mesh Edit Mode | Interactive Tools (required) |
| Merge Menu | M | | Blender, Mesh Edit Mode | |
| Extrude Menu | Alt + E | | Blender, Mesh Edit Mode. Deluxe uses E for Rotate | |
| Bevel, Inset Faces, Knife, Bisect, Extrude to Cursor, Spin or Smooth | MMB | | Activate the corresponding Mesh Edit tool first | |
| Delete at Cursor | Shift + MMB Click | | With Poly Build active | |
| Edge Slide, Vertex Slide or Shrink/Fatten | MMB | | Activate the corresponding Mesh Edit tool first | |

# UV EDITOR

| **Action** | **Keymap 1** | **Keymap 2** | **Note/Status** | **Add-on** |
| --- | --- | --- | --- | --- |
| Select All UVs | Ctrl + A | Cmd + A | | |
| Deselect All UVs | Ctrl + Shift + A | Cmd + Shift + A | | |
| Select Linked UVs | LMB Double-Click | Shift + LMB Double-Click | Shift extends the selection | |
| Deselect Linked UVs | Ctrl + LMB Double-Click | | | |
| Activate Box Select | Q | | The UV Editor assigns Box on key release | |
| Place and Move UV Cursor | MMB Drag | | With the UV Cursor tool active | |
| Snap UV Cursor to Selection | Ctrl + Shift + Wheel Up | Ctrl + Shift + Wheel Right | | |
| UV Tool Pie | Shift + RMB | | | |
| UV Action Pie | Ctrl + RMB | | | |
| UV Cursor Pie | Ctrl + Shift + RMB | | | |

# 🎨 **SCULPTING MODE**

| **Action** | **Keymap 1** | **Keymap 2** | **Note/Status** | **Add-on** |
| --- | --- | --- | --- | --- |
| Increase / Decrease Brush Radius | Shift + Wheel Up / Down | Shift + Wheel Right / Left | | |
| Brush Strength | U | Shift + F | Shift + F is inherited from Blender. Deluxe also assigns Ctrl + Space, which macOS can intercept | |
| Clear Mask | Ctrl + A | Cmd + A | | |
| Fill Mask | Ctrl + Shift + A | Cmd + Shift + A | | |
| Apply Box or Line Mask | MMB Drag | | Activate the corresponding tool first | |
| Remove Mask in Box or Line | Ctrl + MMB Drag | Cmd + MMB Drag | Activate the corresponding tool first | |
| Tool Pie | Shift + RMB | | | |
| Action Pie | Ctrl + RMB | | | |
| Toggle Dynamic Topology | Ctrl + D | Cmd + D | | |
| Set Voxel Size | Shift + R | | | |

# Add-on shortcuts

In Blue Hole preferences, **Third-Party Add-ons** shows the integration
controls. **Keymaps > Assignments** shows each shortcut's source and status.

| **Add-on** | **Shortcut** | **When available** | **Fallback** |
| --- | --- | --- | --- |
| X-Ray Selection Tools | Q in Object or Mesh | Activates X-Ray Box with the integration enabled. Tested with 4.10.2 | Blender Box Select |
| autoConstraints | W / E / R in supported 3D modes | Each shortcut uses the corresponding autoConstraints operator when the integration is enabled and that operator is available | Blender Move, Rotate or Scale |
| Interactive Tools | Alt + D in Mesh Edit Mode | Smart Delete runs when the provider operator is available | Blender's existing Alt+D binding remains available |
| Group Pro | Ctrl + J in Object Mode | Uses the Group Pro Join override when its operator is available | Blender Join |
| Blender FBX | Ctrl + Shift + E | Uses the exporter bundled with Blender when its operator is available | A missing exporter leaves this shortcut inactive |

The Reference reference also customized shortcuts from Hard Ops, Boxcutter,
MACHIN3tools, MESHmachine, and Pie Menu Editor. Their installed keymaps and
saved edits can still affect the same keys. For example, the reference bound
Hard Ops Mirror to Alt+X and assigned Pie Menu Editor actions to right-mouse
gestures in some editors. Those reference edits are outside the bundled
Deluxe defaults. The Reference Group Pro Paste override on Ctrl+V is also
outside the bundled profile. Its provider binding and Blender's Paste Buffer
can share that shortcut. See the [Object and Mesh audit](../../../docs/deluxe-keymaps-category04.md#exact-exceptions)
and the [remaining reference exceptions](../../../docs/deluxe-keymaps-category05.md#exact-exceptions-and-03-composition).

# Additional information

## Differences from the old shortcut sheet

- **Object and mesh mode.** `1`, `2` and `3` choose Vertex, Edge and Face Select on a mesh. `3` still enters Pose Mode on an armature. `4` is the dedicated Deluxe shortcut for returning to Object Mode.
- **Selection and visibility.** `Ctrl + A` and `Ctrl + Shift + A` are Deluxe All/None shortcuts in UV. Object and Mesh Edit use Blender's `A` and `Alt + A` where the mode handles them. Isolation uses `Shift + I`. Blender's viewport X-Ray toggle is `Alt + Z`.
- **Legacy gestures.** The old box-invert, modified lasso, 3D loop/ring double-click, and transform wheel-plane shortcuts have no equivalent Deluxe assignment in the bundled catalog. Blender's selection tools and axis keys cover those workflows. The viewport axis drag rows are bundled, and earlier native comparisons did not establish the expected directional drag behavior.

The reference migration also left some exact conflicts and legacy modal or
macro routes deferred. See the [Deluxe guide](../README.md#shortcut-coverage)
for those receipts. The inherited rows in this guide follow the
[Blender 5.2.2 default keymap](https://github.com/blender/blender/blob/v5.2.2/scripts/presets/keyconfig/keymap_data/blender_default.py).

> [!NOTE] macOS
> Cmd is shown where the bundled profile or Blender base provides an alias.
> System shortcuts can take precedence over Blender, including F11 and
> Ctrl + Space.
