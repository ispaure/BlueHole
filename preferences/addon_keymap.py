"""
Addon keymap registration and lookup for Blue Hole.
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://github.com/ispaure/BlueHole

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS

import bpy

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

PIE_OBJECT_ACTION = 'BLUEHOLE_MT_pie_object_action'
PIE_OBJECT_TOOL = 'BLUEHOLE_MT_pie_object_tool'
PIE_OBJECT_HIDE = 'BLUEHOLE_MT_pie_object_hide'
PIE_GLOBAL_IMPORT_EXPORT = 'BLUEHOLE_MT_pie_global_import_export'

PIE_CURVE_TOOL = 'BLUEHOLE_MT_pie_curve_tool'
PIE_CURVE_ACTION = 'BLUEHOLE_MT_pie_curve_action'
PIE_CURVE_HIDE = 'BLUEHOLE_MT_pie_curve_hide'

PIE_SCULPT_ACTION = 'BLUEHOLE_MT_pie_sculpt_action'
PIE_SCULPT_TOOL = 'BLUEHOLE_MT_pie_sculpt_tool'
PIE_SCULPT_SIMULATION = 'BLUEHOLE_MT_pie_sculpt_simulation'

PIE_MESH_ACTION = 'BLUEHOLE_MT_pie_mesh_action'
PIE_MESH_TOOL = 'BLUEHOLE_MT_pie_mesh_tool'
PIE_MESH_HIDE = 'BLUEHOLE_MT_pie_mesh_hide'
PIE_MESH_ACTION_UVSPECIAL = 'BLUEHOLE_MT_pie_mesh_action_uvspecial'

PIE_ADD = 'BLUEHOLE_MT_pie_add'

PIE_UV_CURSOR = 'BLUEHOLE_MT_pie_UV_cursor'
PIE_UV_ACTION_UVSPECIAL = 'BLUEHOLE_MT_pie_UV_action_uvspecial'
PIE_UV_TOOL = 'BLUEHOLE_MT_pie_UV_tool'
PIE_UV_ACTION = 'BLUEHOLE_MT_pie_UV_action'

# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU DEFS

PIE_MENU_DEFS = [
    # -------------------------------------------------------------------------------------------------
    # OBJECT MODE
    # -------------------------------------------------------------------------------------------------
    {
        'menu_idname': PIE_OBJECT_ACTION,
        'label': 'Object Action',
        'keymap_name': 'Object Mode',
        'space_type': 'VIEW_3D',
        'region_type': 'WINDOW',
        'key': 'RIGHTMOUSE',
        'value': 'PRESS',
        'ctrl': True,
        'shift': False,
        'alt': False,
        'repeat': False,
    },
    {
        'menu_idname': PIE_OBJECT_TOOL,
        'label': 'Object Tool',
        'keymap_name': 'Object Mode',
        'space_type': 'VIEW_3D',
        'region_type': 'WINDOW',
        'key': 'RIGHTMOUSE',
        'value': 'PRESS',
        'ctrl': False,
        'shift': True,
        'alt': False,
        'repeat': False,
    },
    {
        'menu_idname': PIE_OBJECT_HIDE,
        'label': 'Object Hide',
        'keymap_name': 'Object Mode',
        'space_type': 'VIEW_3D',
        'region_type': 'WINDOW',
        'key': 'S',
        'value': 'CLICK_DRAG',
        'ctrl': False,
        'shift': True,
        'alt': False,
        'repeat': False,
    },
    {
        'menu_idname': PIE_GLOBAL_IMPORT_EXPORT,
        'label': 'Global Import / Export',
        'keymap_name': 'Object Mode',
        'space_type': 'VIEW_3D',
        'region_type': 'WINDOW',
        'key': 'RIGHTMOUSE',
        'value': 'PRESS',
        'ctrl': True,
        'shift': True,
        'alt': True,
        'repeat': False,
    },

    # -------------------------------------------------------------------------------------------------
    # CURVE
    # -------------------------------------------------------------------------------------------------
    {
        'menu_idname': PIE_CURVE_TOOL,
        'label': 'Curve Tool',
        'keymap_name': 'Curve',
        'space_type': 'VIEW_3D',
        'region_type': 'WINDOW',
        'key': 'RIGHTMOUSE',
        'value': 'PRESS',
        'ctrl': False,
        'shift': True,
        'alt': False,
        'repeat': False,
    },
    {
        'menu_idname': PIE_CURVE_ACTION,
        'label': 'Curve Action',
        'keymap_name': 'Curve',
        'space_type': 'VIEW_3D',
        'region_type': 'WINDOW',
        'key': 'RIGHTMOUSE',
        'value': 'PRESS',
        'ctrl': True,
        'shift': False,
        'alt': False,
        'repeat': False,
    },
    {
        'menu_idname': PIE_CURVE_HIDE,
        'label': 'Curve Hide',
        'keymap_name': 'Curve',
        'space_type': 'VIEW_3D',
        'region_type': 'WINDOW',
        'key': 'S',
        'value': 'PRESS',
        'ctrl': False,
        'shift': True,
        'alt': False,
        'repeat': True,
    },

    # -------------------------------------------------------------------------------------------------
    # SCULPT
    # -------------------------------------------------------------------------------------------------
    {
        'menu_idname': PIE_SCULPT_ACTION,
        'label': 'Sculpt Action',
        'keymap_name': 'Sculpt',
        'space_type': 'VIEW_3D',
        'region_type': 'WINDOW',
        'key': 'RIGHTMOUSE',
        'value': 'PRESS',
        'ctrl': True,
        'shift': False,
        'alt': False,
        'repeat': False,
    },
    {
        'menu_idname': PIE_SCULPT_TOOL,
        'label': 'Sculpt Tool',
        'keymap_name': 'Sculpt',
        'space_type': 'VIEW_3D',
        'region_type': 'WINDOW',
        'key': 'RIGHTMOUSE',
        'value': 'PRESS',
        'ctrl': False,
        'shift': True,
        'alt': False,
        'repeat': False,
    },
    {
        'menu_idname': PIE_SCULPT_SIMULATION,
        'label': 'Sculpt Simulation',
        'keymap_name': 'Sculpt',
        'space_type': 'VIEW_3D',
        'region_type': 'WINDOW',
        'key': 'RIGHTMOUSE',
        'value': 'PRESS',
        'ctrl': True,
        'shift': True,
        'alt': True,
        'repeat': False,
    },

    # -------------------------------------------------------------------------------------------------
    # MESH
    # -------------------------------------------------------------------------------------------------
    {
        'menu_idname': PIE_MESH_ACTION,
        'label': 'Mesh Action',
        'keymap_name': 'Mesh',
        'space_type': 'VIEW_3D',
        'region_type': 'WINDOW',
        'key': 'RIGHTMOUSE',
        'value': 'PRESS',
        'ctrl': True,
        'shift': False,
        'alt': False,
        'repeat': False,
    },
    {
        'menu_idname': PIE_MESH_TOOL,
        'label': 'Mesh Tool',
        'keymap_name': 'Mesh',
        'space_type': 'VIEW_3D',
        'region_type': 'WINDOW',
        'key': 'RIGHTMOUSE',
        'value': 'PRESS',
        'ctrl': False,
        'shift': True,
        'alt': False,
        'repeat': False,
    },
    {
        'menu_idname': PIE_MESH_HIDE,
        'label': 'Mesh Hide',
        'keymap_name': 'Mesh',
        'space_type': 'VIEW_3D',
        'region_type': 'WINDOW',
        'key': 'S',
        'value': 'CLICK_DRAG',
        'ctrl': False,
        'shift': True,
        'alt': False,
        'repeat': False,
    },
    {
        'menu_idname': PIE_MESH_ACTION_UVSPECIAL,
        'label': 'Mesh UV Special',
        'keymap_name': 'Mesh',
        'space_type': 'VIEW_3D',
        'region_type': 'WINDOW',
        'key': 'RIGHTMOUSE',
        'value': 'PRESS',
        'ctrl': True,
        'shift': True,
        'alt': True,
        'repeat': False,
    },

    # -------------------------------------------------------------------------------------------------
    # 3D VIEW
    # -------------------------------------------------------------------------------------------------
    {
        'menu_idname': PIE_ADD,
        'label': 'Add',
        'keymap_name': '3D View',
        'space_type': 'VIEW_3D',
        'region_type': 'WINDOW',
        'key': 'A',
        'value': 'CLICK_DRAG',
        'ctrl': False,
        'shift': True,
        'alt': False,
        'repeat': False,
    },

    # -------------------------------------------------------------------------------------------------
    # UV EDITOR
    # -------------------------------------------------------------------------------------------------
    {
        'menu_idname': PIE_UV_CURSOR,
        'label': 'UV Cursor',
        'keymap_name': 'UV Editor',
        'space_type': 'IMAGE_EDITOR',
        'region_type': 'WINDOW',
        'key': 'RIGHTMOUSE',
        'value': 'PRESS',
        'ctrl': True,
        'shift': True,
        'alt': False,
        'repeat': False,
    },
    {
        'menu_idname': PIE_UV_ACTION_UVSPECIAL,
        'label': 'UV UV Special',
        'keymap_name': 'UV Editor',
        'space_type': 'IMAGE_EDITOR',
        'region_type': 'WINDOW',
        'key': 'RIGHTMOUSE',
        'value': 'PRESS',
        'ctrl': True,
        'shift': True,
        'alt': True,
        'repeat': False,
    },
    {
        'menu_idname': PIE_UV_TOOL,
        'label': 'UV Tool',
        'keymap_name': 'UV Editor',
        'space_type': 'IMAGE_EDITOR',
        'region_type': 'WINDOW',
        'key': 'RIGHTMOUSE',
        'value': 'PRESS',
        'ctrl': False,
        'shift': True,
        'alt': False,
        'repeat': False,
    },
    {
        'menu_idname': PIE_UV_ACTION,
        'label': 'UV Action',
        'keymap_name': 'UV Editor',
        'space_type': 'IMAGE_EDITOR',
        'region_type': 'WINDOW',
        'key': 'RIGHTMOUSE',
        'value': 'PRESS',
        'ctrl': True,
        'shift': False,
        'alt': False,
        'repeat': False,
    },
]

# ----------------------------------------------------------------------------------------------------------------------
# RUNTIME STORAGE

addon_keymaps = []

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def _find_matching_kmi(km, idname: str, menu_name: str | None = None):
    """
    Find a matching keymap item inside a keymap.
    """
    if km is None:
        return None

    for kmi in km.keymap_items:
        if kmi.idname != idname:
            continue

        if menu_name is not None and getattr(kmi.properties, 'name', None) != menu_name:
            continue

        return kmi

    return None


def _find_menu_def(menu_idname: str):
    """
    Return the pie menu definition dict for the given menu idname.
    """
    for pie_def in PIE_MENU_DEFS:
        if pie_def['menu_idname'] == menu_idname:
            return pie_def
    return None


def _new_keymap(kc, pie_def: dict):
    """
    Create or get the keymap matching the given pie menu definition.
    """
    km = kc.keymaps.get(pie_def['keymap_name'])
    if km is None:
        km = kc.keymaps.new(
            name=pie_def['keymap_name'],
            space_type=pie_def['space_type'],
            region_type=pie_def['region_type'],
        )
    return km


def _remove_existing_menu_from_keyconfig(kc, menu_idname: str):
    """
    Remove all existing wm.call_menu_pie keymap items matching this menu idname
    from the given keyconfig.

    This helps clean up old/stale bindings if you moved a pie menu to a new context.
    """
    if kc is None:
        return

    for km in kc.keymaps:
        items_to_remove = []

        for kmi in km.keymap_items:
            if kmi.idname != 'wm.call_menu_pie':
                continue

            if getattr(kmi.properties, 'name', None) != menu_idname:
                continue

            items_to_remove.append(kmi)

        for kmi in items_to_remove:
            try:
                km.keymap_items.remove(kmi)
            except Exception:
                pass


def ensure_pie_menu_keymap(pie_def: dict):
    """
    Ensure a single addon keymap exists for this pie menu definition.

    Returns:
        tuple[km, kmi, created_new]
    """
    wm = bpy.context.window_manager
    if wm is None:
        return None, None, False

    kc = wm.keyconfigs.addon
    if kc is None:
        return None, None, False

    # Remove stale instances of this menu from addon keyconfig first,
    # so changed contexts / shortcuts don't leave duplicates behind.
    _remove_existing_menu_from_keyconfig(kc, pie_def['menu_idname'])

    km = _new_keymap(kc, pie_def)

    kmi = km.keymap_items.new(
        'wm.call_menu_pie',
        type=pie_def['key'],
        value=pie_def['value'],
        ctrl=pie_def['ctrl'],
        shift=pie_def['shift'],
        alt=pie_def['alt'],
    )
    kmi.properties.name = pie_def['menu_idname']
    kmi.active = True

    # Keyboard repeat support when applicable
    if hasattr(kmi, 'repeat'):
        kmi.repeat = pie_def.get('repeat', False)

    addon_keymaps.append((km, kmi))
    return km, kmi, True


def find_pie_menu_keymap(
        menu_idname: str,
        keymap_name: str | None = None,
        check_user: bool = True,
        check_addon: bool = True,
        check_default: bool = False
):
    """
    Find the keymap item for a given pie menu.

    Returns:
        tuple[keyconfig, keymap, keymap_item] or (None, None, None)
    """
    wm = bpy.context.window_manager
    if wm is None:
        return None, None, None

    pie_def = _find_menu_def(menu_idname)

    keyconfigs_to_check = []
    if check_user and wm.keyconfigs.user is not None:
        keyconfigs_to_check.append(wm.keyconfigs.user)
    if check_addon and wm.keyconfigs.addon is not None:
        keyconfigs_to_check.append(wm.keyconfigs.addon)
    if check_default and wm.keyconfigs.default is not None:
        keyconfigs_to_check.append(wm.keyconfigs.default)

    preferred_keymap_names = []
    if keymap_name is not None:
        preferred_keymap_names.append(keymap_name)
    elif pie_def is not None:
        preferred_keymap_names.append(pie_def['keymap_name'])

    for kc in keyconfigs_to_check:
        # First try the preferred/expected keymap
        for km_name in preferred_keymap_names:
            km = kc.keymaps.get(km_name)
            if km is None:
                continue

            kmi = _find_matching_kmi(km, 'wm.call_menu_pie', menu_idname)
            if kmi is not None:
                return kc, km, kmi

        # Then fallback to searching every keymap
        for km in kc.keymaps:
            kmi = _find_matching_kmi(km, 'wm.call_menu_pie', menu_idname)
            if kmi is not None:
                return kc, km, kmi

    return None, None, None


def get_all_pie_menu_defs() -> list[dict]:
    """
    Return all pie menu definitions for UI drawing.
    """
    return PIE_MENU_DEFS


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER


def register():
    """
    Register addon default keymaps.
    """
    for pie_def in PIE_MENU_DEFS:
        ensure_pie_menu_keymap(pie_def)


def unregister():
    """
    Unregister addon keymaps created by this module.
    """
    for km, kmi in reversed(addon_keymaps):
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass

    addon_keymaps.clear()
