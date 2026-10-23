# Blue Hole

Blue Hole adds project settings, asset export tools, keymaps and menus to Blender.
It requires **Blender 5.2.2 or newer** and supports Windows, macOS and Linux;
external tools and individual integrations may have narrower platform support.

Development targets `blender-5.2.2/alpha`. The `blender-4.5.1/*` branches retain
the legacy version for existing installations.

## Install and start

Follow the [installation guide](https://blue-hole.weebly.com/installation.html),
then enable Blue Hole in Blender's add-on preferences. Start with the standard
mode and enable the keymaps and tools you need.

**Deluxe mode replaces Blender's `userpref.blend` after confirmation.** It keeps
a recovery copy of the previous preferences. Read the prompt before accepting;
this affects your Blender setup, not just Blue Hole.

## What you can do

| Tool | Use |
| --- | --- |
| Environments | Switch project paths, export rules, containers and source-control settings. Each environment has `envFiles/<name>/env_variables.ini`. |
| Asset containers | Organize exportable assets as hierarchies, meshes or collections. |
| Batch export | Export configured assets with project directory and transform settings. |
| Engine bridges | Send configured assets to Unreal, Unity or Godot. Set the matching project paths first. |
| Perforce | Query status, add, checkout and sync files using separately installed command-line tools. |
| Keymaps and pie menus | Enable shortcuts for navigation, selection, transforms and commonly used tools. |
| Header menu | Access exports, containers, project directories and help from Blender. |
| Pipeline utilities | Sort, rename and prepare scene objects for your pipeline. |

Perforce is the implemented source-control wrapper. Git and Plastic SCM choices
in the interface do not provide the same complete file-operation workflow.

For a new project, copy an existing environment, select it in preferences and
set its paths before exporting. Environment settings belong to the project;
keymaps and menu preferences belong to your Blender installation.

## Guides and development

- [Environments](environment/README.md): storage, switching and setting mappings.
- [Preferences](preferences/README.md), [keymaps](keymaps/README.md) and [Deluxe mode](overlays/deluxe/README.md).
- [UI](ui/README.md) and [actions](actions/README.md): extending menus and commands.
- [Perforce wrapper](wrappers/README.md): command results and file status.
- [commonUtils](Lib/commonUtils/README.md): the vendored shared utilities.

Run `python -m unittest discover -s tests -v` for adapter checks outside Blender.
GitHub runs them on Windows, macOS and Linux. They check shared command contracts
and preference-installation failure handling; they do not exercise a live engine,
Perforce server or Blender desktop session.

Portable contracts can also run inside Blender's embedded Python with the
[isolated smoke-test launcher](tests/README.md#embedded-shared-library-smoke-test).

The shared copy checker compares `Lib/commonUtils` against the commit recorded in
`Lib/commonUtils.revision`, applying Git line-ending rules. It rejects missing or
obsolete files, changed content and linked files or directories. Unfinished edits
in the source checkout do not change the recorded shared revision.

[Website](https://blue-hole.weebly.com) ·
[Feedback](https://blue-hole.weebly.com/contact.html)

## License

MIT. Copyright © 2026 Marc-André Voyer.
Third-party Blender Tools code retains its own license in `Lib/send2ue`.
