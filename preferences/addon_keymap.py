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

from dataclasses import dataclass
import bpy
from ..Lib.commonUtils.debugUtils import *

from ..Menus.pieMenu import (
    addPieMenus,
    curvePieMenus,
    globalPieMenus,
    meshPieMenus,
    objectPieMenus,
    sculptPieMenus,
    uvPieMenus
)

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# DATACLASS


@dataclass(frozen=True)
class PieKeymapDef:
    menu_idname: str
    keymap_name: str
    space_type: str
    key: str
    value: str = 'PRESS'
    ctrl: bool = False
    shift: bool = False
    alt: bool = False
    repeat: bool = False
    region_type: str = 'WINDOW'


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU DEFS

PIE_MENU_DEFS: list[PieKeymapDef] = [

    # WINDOW
    PieKeymapDef(
        menu_idname=globalPieMenus.MT_pie_global_help.bl_idname,
        keymap_name='Window',
        space_type='EMPTY',
        key='F1',
    ),
    PieKeymapDef(
        menu_idname=globalPieMenus.MT_pie_global_dirs.bl_idname,
        keymap_name='Window',
        space_type='EMPTY',
        key='F3',
    ),
    PieKeymapDef(
        menu_idname=globalPieMenus.MT_pie_global_import_export.bl_idname,
        keymap_name='Window',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
        shift=True,
        alt=True,
    ),

    # OBJECT MODE
    PieKeymapDef(
        menu_idname=objectPieMenus.MT_pie_object_action.bl_idname,
        keymap_name='Object Mode',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
    ),
    PieKeymapDef(
        menu_idname=objectPieMenus.MT_pie_object_tool.bl_idname,
        keymap_name='Object Mode',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        shift=True,
    ),
    PieKeymapDef(
        menu_idname=objectPieMenus.MT_pie_object_hide.bl_idname,
        keymap_name='Object Mode',
        space_type='EMPTY',
        key='S',
        value='CLICK_DRAG',
        shift=True,
    ),
    PieKeymapDef(
        menu_idname=globalPieMenus.MT_pie_global_import_export.bl_idname,
        keymap_name='Object Mode',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
        shift=True,
        alt=True,
    ),

    # MESH
    PieKeymapDef(
        menu_idname=meshPieMenus.MT_pie_mesh_action.bl_idname,
        keymap_name='Mesh',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
    ),
    PieKeymapDef(
        menu_idname=meshPieMenus.MT_pie_mesh_tool.bl_idname,
        keymap_name='Mesh',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        shift=True,
    ),
    PieKeymapDef(
        menu_idname=meshPieMenus.MT_pie_mesh_hide.bl_idname,
        keymap_name='Mesh',
        space_type='EMPTY',
        key='S',
        value='CLICK_DRAG',
        shift=True,
    ),
    PieKeymapDef(
        menu_idname=uvPieMenus.MT_pie_mesh_action_uvspecial.bl_idname,
        keymap_name='Mesh',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
        shift=True,
        alt=True,
    ),

    # 3D VIEW
    PieKeymapDef(
        menu_idname=addPieMenus.MT_pie_add.bl_idname,
        keymap_name='3D View',
        space_type='VIEW_3D',
        key='A',
        value='CLICK_DRAG',
        shift=True,
    ),

    # UV EDITOR
    PieKeymapDef(
        menu_idname=uvPieMenus.MT_pie_UV_cursor.bl_idname,
        keymap_name='UV Editor',
        space_type='IMAGE_EDITOR',
        key='RIGHTMOUSE',
        ctrl=True,
        shift=True,
    ),
    PieKeymapDef(
        menu_idname=uvPieMenus.MT_pie_UV_action_uvspecial.bl_idname,
        keymap_name='UV Editor',
        space_type='IMAGE_EDITOR',
        key='RIGHTMOUSE',
        ctrl=True,
        shift=True,
        alt=True,
    ),
    PieKeymapDef(
        menu_idname=uvPieMenus.MT_pie_UV_tool.bl_idname,
        keymap_name='UV Editor',
        space_type='IMAGE_EDITOR',
        key='RIGHTMOUSE',
        shift=True,
    ),
    PieKeymapDef(
        menu_idname=uvPieMenus.MT_pie_UV_action.bl_idname,
        keymap_name='UV Editor',
        space_type='IMAGE_EDITOR',
        key='RIGHTMOUSE',
        ctrl=True,
    ),

    # CURVE
    PieKeymapDef(
        menu_idname=curvePieMenus.MT_pie_curve_tool.bl_idname,
        keymap_name='Curve',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        shift=True,
    ),
    PieKeymapDef(
        menu_idname=curvePieMenus.MT_pie_curve_action.bl_idname,
        keymap_name='Curve',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
    ),
    PieKeymapDef(
        menu_idname=curvePieMenus.MT_pie_curve_hide.bl_idname,
        keymap_name='Curve',
        space_type='EMPTY',
        key='S',
        shift=True,
        repeat=True,
    ),

    # SCULPT
    PieKeymapDef(
        menu_idname=sculptPieMenus.MT_pie_sculpt_action.bl_idname,
        keymap_name='Sculpt',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
    ),
    PieKeymapDef(
        menu_idname=sculptPieMenus.MT_pie_sculpt_tool.bl_idname,
        keymap_name='Sculpt',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        shift=True,
    ),
    PieKeymapDef(
        menu_idname=sculptPieMenus.MT_pie_sculpt_simulation.bl_idname,
        keymap_name='Sculpt',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
        shift=True,
        alt=True,
    ),
]

# ----------------------------------------------------------------------------------------------------------------------
# RUNTIME STORAGE

addon_keymaps = []

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def _find_matching_kmi(km, idname: str, menu_name: str | None = None):
    if km is None:
        return None

    for kmi in km.keymap_items:
        if kmi.idname != idname:
            continue

        if menu_name is not None and getattr(kmi.properties, 'name', None) != menu_name:
            continue

        return kmi

    return None


def _find_menu_def(menu_idname: str) -> PieKeymapDef | None:
    for pie_def in PIE_MENU_DEFS:
        if pie_def.menu_idname == menu_idname:
            return pie_def
    return None


def _new_keymap(kc, pie_def: PieKeymapDef):
    return kc.keymaps.new(
        name=pie_def.keymap_name,
        space_type=pie_def.space_type,
        region_type=pie_def.region_type,
    )


def _remove_existing_menu_from_keyconfig(kc, pie_def: PieKeymapDef):
    if kc is None:
        return

    for km in kc.keymaps:
        if km.name != pie_def.keymap_name:
            continue

        items_to_remove = []

        for kmi in km.keymap_items:
            if kmi.idname != 'wm.call_menu_pie':
                continue

            if getattr(kmi.properties, 'name', None) != pie_def.menu_idname:
                continue

            items_to_remove.append(kmi)

        for kmi in items_to_remove:
            try:
                km.keymap_items.remove(kmi)
            except Exception:
                pass


def ensure_pie_menu_keymap(pie_def: PieKeymapDef):
    print(f'[BH] ensure start | {pie_def.keymap_name} | {pie_def.menu_idname}')

    wm = bpy.context.window_manager
    print(f'[BH] wm = {wm}')
    if wm is None:
        print('[BH] wm is None')
        return None, None, False

    kc = wm.keyconfigs.addon
    print(f'[BH] kc.addon = {kc}')
    if kc is None:
        print('[BH] kc.addon is None')
        return None, None, False

    _remove_existing_menu_from_keyconfig(kc, pie_def)

    km = _new_keymap(kc, pie_def)
    print(f'[BH] km = {km.name if km else None}')

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

    addon_keymaps.append((km, kmi))
    print(f'[BH] created | {km.name} | {kmi.idname} | {kmi.properties.name}')
    return km, kmi, True


def find_pie_menu_keymap(
        menu_idname: str,
        keymap_name: str | None = None,
        check_user: bool = True,
        check_addon: bool = True,
        check_default: bool = False
):
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
        preferred_keymap_names.append(pie_def.keymap_name)

    for kc in keyconfigs_to_check:
        for km_name in preferred_keymap_names:
            km = kc.keymaps.get(km_name)
            if km is None:
                continue

            kmi = _find_matching_kmi(km, 'wm.call_menu_pie', menu_idname)
            if kmi is not None:
                return kc, km, kmi

        for km in kc.keymaps:
            kmi = _find_matching_kmi(km, 'wm.call_menu_pie', menu_idname)
            if kmi is not None:
                return kc, km, kmi

    return None, None, None


def get_all_pie_menu_defs() -> list[PieKeymapDef]:
    return PIE_MENU_DEFS


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER

def register():
    log(Severity.INFO, 'Blue Hole Addon Keymaps', 'Registering Keymaps...')
    unregister()
    for pie_def in PIE_MENU_DEFS:
        ensure_pie_menu_keymap(pie_def)
    log(Severity.INFO, 'Blue Hole Addon Keymaps', 'Registering Keymaps completed!')


def unregister():
    for km, kmi in reversed(addon_keymaps):
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass

    addon_keymaps.clear()
