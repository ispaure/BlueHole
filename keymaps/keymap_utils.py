"""
Shared keymap utilities for Blue Hole.
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
# KEYMAP HELPERS


def get_window_manager():
    """
    Return Blender's window manager, or None if unavailable.
    """
    return bpy.context.window_manager


def get_addon_keyconfig():
    """
    Return Blender's addon keyconfig, or None if unavailable.
    """
    wm = get_window_manager()
    if wm is None:
        return None

    return wm.keyconfigs.addon


def get_keyconfig_sequence(
        check_user: bool = True,
        check_addon: bool = True,
        check_default: bool = False
):
    """
    Return the ordered list of keyconfigs to inspect.
    """
    wm = get_window_manager()
    if wm is None:
        return []

    keyconfigs = []

    if check_user and wm.keyconfigs.user is not None:
        keyconfigs.append(wm.keyconfigs.user)

    if check_addon and wm.keyconfigs.addon is not None:
        keyconfigs.append(wm.keyconfigs.addon)

    if check_default and wm.keyconfigs.default is not None:
        keyconfigs.append(wm.keyconfigs.default)

    return keyconfigs


def get_or_create_keymap(kc, keymap_name: str, space_type: str, region_type: str = 'WINDOW'):
    """
    Return an existing keymap if found, otherwise create it.
    """
    if kc is None:
        return None

    km = kc.keymaps.get(keymap_name)
    if km is not None:
        return km

    return kc.keymaps.new(
        name=keymap_name,
        space_type=space_type,
        region_type=region_type,
    )


def find_matching_kmi(km, idname: str, property_name: str | None = None, property_value=None):
    """
    Find the first keymap item matching the given operator idname and optional property value.
    """
    if km is None:
        return None

    for kmi in km.keymap_items:
        if kmi.idname != idname:
            continue

        if property_name is not None:
            if getattr(kmi.properties, property_name, None) != property_value:
                continue

        return kmi

    return None


def remove_matching_kmis(km, idname: str, property_name: str | None = None, property_value=None):
    """
    Remove all keymap items matching the given operator idname and optional property value.
    """
    if km is None:
        return

    items_to_remove = []

    for kmi in km.keymap_items:
        if kmi.idname != idname:
            continue

        if property_name is not None:
            if getattr(kmi.properties, property_name, None) != property_value:
                continue

        items_to_remove.append(kmi)

    for kmi in items_to_remove:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
