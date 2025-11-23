Here is the list of **Key Mappings** relevant to artists in Blender.

# 📖 Table of Contents
---
Feel free to use this Table of Contents. You can also search this page for any keyword such as `collection` to find its keymap quicly.
- [🖱️ Mouse Input](#️-mouse-input)
- [💾 SYSTEM](#-system)
- [📷 CAMERA NAVIGATION](#-camera-navigation)
- [🪟 LAYOUT](#-layout)
- [👉 SELECTION](#-selection)
- [❄️ TRANFORM](#️-tranform)
- [🧊 MODELING MODE](#-modeling-mode)
- [🎨 SCULPTING MODE](#-sculpting-mode)
- [🥧 FULL PIE MENU LIST](#-full-pie-menu-list)
- [❓ ADDITIONAL INFORMATION](#-additional-information)


# 🖱️ Mouse Input Acronyms
---
To simplify this document, some acronyms are used for mouse inputs.

| **Acronym** | **Mouse Input**     |
| ----------- | ------------------- |
| LMB         | Left Mouse Button   |
| RMB         | Right Mouse Button  |
| MMB         | Middle Mouse Button |
| MW          | Mouse Wheel         |


# 💾 **SYSTEM**
---
Basic keymaps to load, save, undo/redo.

## Scene Management

| **Action**          | **Keymap 1**     | **Keymap 2**    | **Note/Status** |
| ------------------- | ---------------- | --------------- | --------------- |
| Save                | Ctrl + S         | Cmd + S         |                 |
| Save As             | Ctrl + Shift + S | Cmd + Shift + S |                 |
| Undo                | Ctrl + Z         |                 |                 |
| Redo                | Ctrl + Shift + Z | Ctrl + Y        |                 |
| Drop Active Tool    | Q                |                 |                 |
| Redo Last Operation | G                |                 |                 |
| Search Menu         | Space Bar        |                 |                 |
## Asset Management

| **Action**                                | **Keymap 1**    | **Keymap 2** | **Note/Status** |
| ----------------------------------------- | --------------- | ------------ | --------------- |
| Add / Create (Various Items)              | Shift + A       |              |                 |
| Duplicate (Regular) *(Mesh Mode Only)*    | Ctrl + D        |              |                 |
| Duplicate (Instance) *(Object Mode Only)* | Shift + D       |              |                 |
| Duplicate (Special) *(Object Mode Only)*  | N/A             |              |                 |
| Delete                                    | Alt + D         | Delete       |                 |
| Delete Menu                               | Alt + Shift + D |              |                 |
| Copy                                      | Ctrl + C        |              |                 |
| Paste                                     | Ctrl + V        |              |                 |
## Asset Grouping / Parenting (Object Mode Only)

| **Action**          | **Keymap 1**       | **Keymap 2**     | **Description**                                                                               |
| ------------------- | ------------------ | ---------------- | --------------------------------------------------------------------------------------------- |
| Group Selection     | Ctrl + G           |                  | Groups the selected objects                                                                   |
| Add to Group        | Shift + G          |                  | Add entire selection to the group of the last selected object (last object must have a group) |
| Remove from Group   | Alt + G            |                  |                                                                                               |
| Move to collection  | C                  |                  |                                                                                               |
| Parent              | P                  |                  |                                                                                               |
| Clear Parent        | Shift + P          |                  |                                                                                               |
| Select Parent       | Shift + Wheel Up   | LMB Double-Click |                                                                                               |
| Select Childs       | Shift + Wheel Down |                  |                                                                                               |
| Walk Up Hierarchy   | Ctrl + Wheel Up    |                  |                                                                                               |
| Walk Down Hierarchy | Ctrl + Wheel Down  |                  |                                                                                               |


## Show / Hide

| **Action**                 | **Keymap 1** | **Keymap 2** | **Note/Status**               |
| -------------------------- | ------------ | ------------ | ----------------------------- |
| Hide Selection             | Ctrl + H     |              |                               |
| Reveal Hidden [All]        | Alt + H      |              |                               |
| Isolate Selection (Toggle) | Alt + S      | S            | ==Works in Object Mode Only== |


# 📷 **CAMERA NAVIGATION**
---
## 3D Viewport
How to navigate 3D viewports, such as the **Modeling** and **Sculpting** viewports. The basic Pan/Zoom/Rotate is akin to Maya's navigation.

| **Action**                                 | **Keymap 1**           | **Keymap 2**             | **Note/Status** |
| ------------------------------------------ | ---------------------- | ------------------------ | --------------- |
| Pan                                        | Alt + MMB Drag         | MMB Drag                 |                 |
| Zoom                                       | Alt + RMB Drag         | Wheel Up/Down            |                 |
| Rotate                                     | Alt + LMB Drag         | Double-click MMB Drag    |                 |
| Focus (Selection)                          | F                      | Alt + Shift + Wheel Up   |                 |
| Focus (All)                                | A                      | Alt + Shift + Wheel Down |                 |
| Set Orthographic View in Current Direction | Alt + Shift + MMB Drag | Alt + Shift + MMB        |                 |
| Rotate Orthographic View in Next Direction | Alt + Shift + LMB Drag |                          |                 |
## 2D Viewport
How to navigate 2D viewports, such as the **UV Editor** and **Shader Editor**. The basic Pan/Zoom is akin to Maya's navigation.

| **Action**        | **Keymap 1**   | **Keymap 2**             | **Note/Status** |
| ----------------- | -------------- | ------------------------ | --------------- |
| Pan               | Alt + MMB Drag | MMB Drag                 |                 |
| Zoom              | Alt + RMB Drag | MW Up/Down               |                 |
| Focus (Selection) | F              | Alt + Shift + Wheel Up   |                 |
| Focus (All)       | A              | Alt + Shift + Wheel Down |                 |

# 🪟 **LAYOUT**
---

| **Action**                         | **Keymap 1**        | **Keymap 2** | **Note/Status**                                            |
| ---------------------------------- | ------------------- | ------------ | ---------------------------------------------------------- |
| Toggle 4 view (3D + orthographics) | Ctrl + Tab          |              |                                                            |
| Maximize Viewport Size             | Ctrl + Shift + Tab  |              |                                                            |
| Toggle Fullscreen Mode             | F11                 |              | Existing system shortcut on macOS, cannot bind to Blender. |
| Toggle Side Panel                  | N                   |              |                                                            |
| Toggle Library                     | Ctrl + Space        |              | Existing system shortcut on macOS, cannot bind to Blender. |
| X-Ray / Transparency               | Alt + X             |              | ==Broken right now==                                       |
| Quick Favorites                    | Press `Q` two times |              |                                                            |
| Preferences                        | Ctrl + ,            | Cmd + ,      |                                                            |

# 👉 **SELECTION**
---
## Mode

|**Action**|**Keymap 1**|**Keymap 2**|**Note/Status**|
|---|---|---|---|
|Object Mode|4 or Tab|||
|Vertex Mode|1|||
|Edge Mode|2|||
|Face Mode|3|||

## Click

| **Action**              | **Keymap 1**      | **Keymap 2** | **Note/Status**                       |
| ----------------------- | ----------------- | ------------ | ------------------------------------- |
| Click Select (New)      | LMB               |              |                                       |
| Click Select (Add)      | Shift + LMB Click |              |                                       |
| Click Select (Subtract) | Ctrl + LMB Click  |              | ==Not working in UV Editor; FIX !!!== |

## Box

|**Action**|**Keymap 1**|**Keymap 2**|**Note/Status**|
|---|---|---|---|
|Box Select Through (New)|LMB Drag|||
|Box Select Through (Add)|Shift + LMB Drag|||
|Box Select Through (Subtract)|Ctrl + LMB Drag|||
|Box Select (Invert)|Ctrl + Shift + LMB Drag||==Not working in UV Editor; FIX !!!==|

## Lasso

|**Action**|**Keymap 1**|**Keymap 2**|**Note/Status**|
|---|---|---|---|
|Lasso Select (Add)|Ctrl + Shift + Alt + LMB Drag|||
|Lasso Select (Subtract)|Ctrl + Alt + MMB Drag||==Not working in UV Editor; FIX !!!==|

## Circle / Paint

| **Action**                     | **Keymap 1**     | **Keymap 2** | **Note/Status**                                                    |
| ------------------------------ | ---------------- | ------------ | ------------------------------------------------------------------ |
| Circle/Paint Select (New)      | N/A              |              | No key for this; LMB in empty space if you need to reset selection |
| Circle/Paint Select (Add)      | Shift + MMB Drag |              |                                                                    |
| Circle/Paint Select (Subtract) | Ctrl + MMB Drag  |              |                                                                    |

## Loop / Ring

| **Action**                     | **Keymap 1**                      | **Keymap 2** | **Note/Status**                |
| ------------------------------ | --------------------------------- | ------------ | ------------------------------ |
| Edge Loop Selection (New)      | Alt + Double-Click                |              | Works in Edge/Face Mode        |
| Edge Loop Selection (Add)      | Shift + Alt + Double-Click        |              | Works in Edge/Face Mode        |
| Edge Loop Selection (Subtract) | Shift + Alt + Double-Click        |              | Works in Edge/Face Mode        |
| Ring Selection (New)           | Ctrl + Alt + Double-Click         |              | ==Could not get this to work== |
| Ring Selection (Add/Subtract)  | Ctrl + Alt + Shift + Double-Click |              | ==Could not get this to work== |

## Miscellaneous

| **Action**                       | **Keymap 1**                                                                                         | **Keymap 2** | **Note/Status**                                                                          |
| -------------------------------- | ---------------------------------------------------------------------------------------------------- | ------------ | ---------------------------------------------------------------------------------------- |
| Select All                       | Ctrl + A                                                                                             |              |                                                                                          |
| Deselect All                     | Ctrl + Shift + A                                                                                     |              |                                                                                          |
| Invert Selection                 | Ctrl + I                                                                                             |              |                                                                                          |
| Select More / Grow Selection     | Shift + Wheel Up                                                                                     | ]            |                                                                                          |
| Select Less / Shrink Selection   | Shift + Wheel Down                                                                                   | [            |                                                                                          |
| Pick shortest path               | Ctrl + LMB                                                                                           |              |                                                                                          |
| Pick shortest path (fill region) | Ctrl + Shift + LMB                                                                                   |              |                                                                                          |
| Pattern Selection                | 1. LMB Face A<br>2. Shift + LMB Face B<br>3. Ctrl + Wheel Up to extend (Ctrl + Wheel Down to shrink) |              | This is done in three input steps: Select first face, second face and then extend/shrink |
| Group/Parent Selection           | LMB Double-Click                                                                                     |              | ==Seems hit or miss==                                                                    |
| Collection Selection             | Ctrl + LMB Double-Click                                                                              |              | ==Seems hit or miss==                                                                    |


# ❄️ **TRANFORM**
---
## Basic Tools
These are your classic tools to transform objects: Move, Rotate and Scale.

| **Action**        | **Keymap 1** | **Keymap 2** | **Note/Status**                                                      |
| ----------------- | ------------ | ------------ | -------------------------------------------------------------------- |
| Move              | W            |              | Blender's default                                                    |
| Rotate            | E            |              | Blender's default                                                    |
| Scale             | R            |              | Blender's default                                                    |
| Move Gizmo Tool   | Shift + W    |              | Like Maya                                                            |
| Rotate Gizmo Tool | Shift + E    |              | Like Maya                                                            |
| Scale Gizmo Tool  | Shift + R    |              | Like Maya                                                            |
| Shrink Gizmo Size | Wheel Up     |              | Only works when a tool with a gizmo (such as paint select) is active |
| Grow Gizmo Size   | Wheel Down   |              | Only works when a tool with a gizmo (such as paint select) is active |

## Constraints
When transforming objects, choose 3D axis(es) constraints.

| **Action** | **Keymap 1**          | **Keymap 2** | **Note/Status**  |
| ---------- | --------------------- | ------------ | ---------------- |
| X Axis     | MMB Drag in Direction | X            |                  |
| Y Axis     | MMB Drag in Direction | Y            |                  |
| Z Axis     | MMB Drag in Direction | Z            |                  |
| YZ Plane   | Wheel Up              |              |                  |
| XZ Plane   | Wheel Down            |              |                  |
| XY Plane   | Alt + Wheel Down      |              | ==Not working!== |

## Snapping
When transforming objects, adjust snapping.

| **Action**                 | **Keymap 1**                | **Keymap 2** | **Note/Status** |
| -------------------------- | --------------------------- | ------------ | --------------- |
| Toggle Snapping            | X                           |              |                 |
| Snapping Menu              | Shift + X                   |              |                 |
| Toggle Snapping (1 M)      | Hold Ctrl (while transform) |              |                 |
| Smaller increments (10 CM) | Hold Shift                  |              |                 |

## Proportional Editing (Soft Select)
Set a zone of soft influence for the transform.

| **Action**                  | **Keymap 1**                       | **Keymap 2** | **Note/Status**              |
| --------------------------- | ---------------------------------- | ------------ | ---------------------------- |
| Toggle proportional editing | B                                  |              | Anytime                      |
| Falloff types menu          | Shift + B                          |              | Whilst not in transform mode |
| Increase falloff radius     | Tab + Wheel Up (while transform)   | ]            | Whilst using a transform     |
| Decrease falloff radius     | Tab + Wheel Down (while transform) | [            | Whilst using a transform     |

> [!NOTE] Snapping
> Proportional Editing may act strangely if snapping is enabled.
> 

## 3D Cursor

| **Action**                 | **Keymap 1**              | **Keymap 2** | **Note/Status** |
| -------------------------- | ------------------------- | ------------ | --------------- |
| Set 3D Cursor              | Ctrl + Shift + MMB Drag   |              | ==Not working== |
| Set 3D Cursor to Selection | Ctrl + Shift + Wheel Up   |              |                 |
| Set 3D Cursor to Origin    | Ctrl + Shift + Wheel Down |              |                 |

# 🧊 **MODELING MODE**
---

==TODO: Fill this section, create new hotkeys for extrude, merges, etc.==


# 🎨 **SCULPTING MODE**
---

| **Action**           | **Keymap 1**          | **Keymap 2**               | **Note/Status** |
| -------------------- | --------------------- | -------------------------- | --------------- |
| Sculpt Tool Radius   | Shift + Wheel Up/Down | Shift + Space + Drag Mouse |                 |
| Sculpt Tool Hardness | Ctrl + Space          |                            | ==Not working== |


# 🥧 **FULL PIE MENU LIST**
---
Here is a list of the pie menus available to you, as well as some important information:
- Name: Name of the Pie Menu
- Context: Where in Blender can it be triggered/enabled
- Keymap: Which hotkey to press to trigger it
- Origin: From where does it come from
- Description: What is its purpose?

| **Name**                          | **Context**                             | **Keymap**                              | **Origin**                   | **Description**                                                                                                      |
| --------------------------------- | --------------------------------------- | --------------------------------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Shading and Overlays              | 3D Viewport                             | Z                                       | ?                            | Pie Menu to switch between View/Rendering styles, Shading and Normal adjustments.                                    |
| Help                              |                                         | F1                                      | Blue Hole                    | Pie Menu that links to documentation and offers a way to give feedback.                                              |
| Directories                       |                                         | F3                                      | Blue Hole                    | Quickly navigate to commonly used directories.                                                                       |
| Import/Export                     | 3D Viewport (Object Mode only)          | Ctrl + Alt + Shift + RMB                | Blue Hole                    | Pie Menu with quick import-export options.                                                                           |
| Tools                             | Many                                    | Shift + RMB Drag                        | Blue Hole                    | Offers many helpful tools in various contexts such as: Object Mode, Verts/Edge/Face Mode, Curve, Sculpt & UV Mode.   |
| Action                            | Many                                    | Ctrl + RMB Drag                         | Blue                         | Offers many helpful actions in various contexts such as: Object Mode, Verts/Edge/Face Mode, Curve, Sculpt & UV Mode. |
| Action (UV Special)               | 3D Viewport (Mesh Mode only), UV Editor | Ctrl + Alt + Shift + RMB Drag           | Blue Hole                    | Offers helpful options related to UV unwrapping: mark seam, clear seam, unwrap, etc.                                 |
| Cursor and Origin                 | 3D Viewport, UV Editor                  | Ctrl + Shift + RMB                      | Blender & Blue Hole (Hybrid) | Cursor and Origin Options (Menu in 3D Viewport comes with Blender; Menu in UV Editor comes from Blue Hole).          |
| Transform: Pivot and Orientations | 3D Viewport                             | Shift + Alt + RMB                       | ?                            | Set the Orientation target or the Pivot Method, with multiple Presets or set New Custom Orientation.                 |
| Snapping Pie                      | 3D Viewport                             | Ctrl + Alt + RMB                        | ?                            | Quick snapping presets for every modes.                                                                              |
| Quick Align Pie                   | 3D Viewport (Mesh Mode only)            | Alt + W                                 | ?                            | Quick Align Functionalities for Object, Mesh and UV.                                                                 |
| Mode                              | Many                                    | RMB Drag                                | Blender                      | Switch Between any Mode: Object/Vertex/Edge/Face/Curve/Sculpt/UV/Paint/etc.                                          |
| Save, Open, Append                | 3D Viewport                             | Alt + Shift + S                         |                              | Save, Open, Append to Scene Pie                                                                                      |
| Create                            | 3D Viewport                             | Shift + A + Drag Mouse in Any Direction | Blue Hole                    | Create new shapes, curves, etc.                                                                                      |
| Hide                              | 3D Viewport                             | Shift + S + Drag Mouse in Any Direction | Blue Hole                    | Hide Selection, Isolate Selection, Reveal Hidden (All)                                                               |
| Collection                        | 3D Viewport                             | C + Drag Mouse in Any Direction         | Blender                      | Pie Menu for Collections                                                                                             |

# ❓**ADDITIONAL INFORMATION**
---
> [!NOTE] Notes for macOS users
>  - **Command Key**: For most intents and purposes, keymaps using `Ctrl` as a modifier haven't been remapped to `Cmd`.
>  - **Natural Scrolling**: It is recommended to disable `Natural Scrolling` under `Mouse Settings` for a better experience. Else, hotkeys involving the `Mouse Wheel` will be inverted *(eg. Grow Selection will Shrink, Shrink Selection will Grow)*.
> 