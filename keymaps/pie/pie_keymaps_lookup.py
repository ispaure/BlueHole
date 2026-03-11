"""
Lookup helpers for Blue Hole pie menu keymaps.
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

from ..keymap_utils import find_matching_kmi, get_keyconfig_sequence
from .pie_keymaps_defs import PIE_MENU_DEFS, PieKeymapDef

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def find_pie_menu_def(menu_idname: str) -> PieKeymapDef | None:
    """
    Return the declared pie keymap definition for the given menu idname.
    """
    for pie_def in PIE_MENU_DEFS:
        if pie_def.menu_idname == menu_idname:
            return pie_def

    return None


def find_pie_menu_keymap(
        menu_idname: str,
        keymap_name: str | None = None,
        check_user: bool = True,
        check_addon: bool = True,
        check_default: bool = False
):
    """
    Find the real Blender keymap item for a Blue Hole pie menu.
    """
    pie_def = find_pie_menu_def(menu_idname)

    keyconfigs_to_check = get_keyconfig_sequence(
        check_user=check_user,
        check_addon=check_addon,
        check_default=check_default,
    )

    preferred_keymap_names = []

    if keymap_name is not None:
        preferred_keymap_names.append(keymap_name)
    elif pie_def is not None:
        preferred_keymap_names.append(pie_def.keymap_name)

    for kc in keyconfigs_to_check:
        for km_name in preferred_keymap_names:
            km = kc.keymaps.get(km_name)
            if km is None:
                continue

            kmi = find_matching_kmi(
                km,
                idname='wm.call_menu_pie',
                property_name='name',
                property_value=menu_idname,
            )
            if kmi is not None:
                return kc, km, kmi

        for km in kc.keymaps:
            kmi = find_matching_kmi(
                km,
                idname='wm.call_menu_pie',
                property_name='name',
                property_value=menu_idname,
            )
            if kmi is not None:
                return kc, km, kmi

    return None, None, None
