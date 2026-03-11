"""
Registration and runtime management for Blue Hole pie menu keymaps.
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

from ...Lib.commonUtils.debugUtils import *
from ..keymap_utils import (
    get_addon_keyconfig,
    get_or_create_keymap,
    remove_matching_kmis,
)
from .pie_keymaps_defs import PIE_MENU_DEFS, PieKeymapDef

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# RUNTIME STORAGE

registered_pie_keymaps = []

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def remove_existing_pie_menu_from_keyconfig(kc, pie_def: PieKeymapDef):
    """
    Remove existing keymap items for the given pie menu from the given keyconfig.
    """
    if kc is None:
        return

    km = kc.keymaps.get(pie_def.keymap_name)
    if km is None:
        return

    remove_matching_kmis(
        km,
        idname='wm.call_menu_pie',
        property_name='name',
        property_value=pie_def.menu_idname,
    )


def ensure_pie_menu_keymap(pie_def: PieKeymapDef):
    """
    Ensure a Blue Hole pie menu keymap exists in Blender's addon keyconfig.
    """
    kc = get_addon_keyconfig()
    if kc is None:
        return None, None, False

    remove_existing_pie_menu_from_keyconfig(kc, pie_def)

    km = get_or_create_keymap(
        kc,
        keymap_name=pie_def.keymap_name,
        space_type=pie_def.space_type,
        region_type=pie_def.region_type,
    )
    if km is None:
        return None, None, False

    kmi = km.keymap_items.new(
        'wm.call_menu_pie',
        type=pie_def.key,
        value=pie_def.value,
        ctrl=pie_def.ctrl,
        shift=pie_def.shift,
        alt=pie_def.alt,
    )
    kmi.properties.name = pie_def.menu_idname
    kmi.active = True

    if hasattr(kmi, 'repeat'):
        kmi.repeat = pie_def.repeat

    registered_pie_keymaps.append((km, kmi))
    return km, kmi, True

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
    log(Severity.INFO, 'Blue Hole Pie Keymaps', 'Registering pie keymaps...')
    unregister()

    for pie_def in PIE_MENU_DEFS:
        ensure_pie_menu_keymap(pie_def)

    log(Severity.INFO, 'Blue Hole Pie Keymaps', 'Registering pie keymaps completed!')


def unregister():
    for km, kmi in reversed(registered_pie_keymaps):
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass

    registered_pie_keymaps.clear()
