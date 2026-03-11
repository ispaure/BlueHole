"""
Pie menu keymap definitions for Blue Hole.
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

from ...ui.menus.pie import (
    add_pies,
    curve_pies,
    directories_pies,
    global_pies,
    import_export_pies,
    mesh_pies,
    object_pies,
    sculpt_pies,
    uv_pies,
)

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
        menu_idname=global_pies.BLUEHOLE_MT_pie_global_help.bl_idname,
        keymap_name='Window',
        space_type='EMPTY',
        key='F1',
    ),
    PieKeymapDef(
        menu_idname=directories_pies.BLUEHOLE_MT_pie_global_dirs.bl_idname,
        keymap_name='Window',
        space_type='EMPTY',
        key='F3',
    ),
    PieKeymapDef(
        menu_idname=import_export_pies.BLUEHOLE_MT_pie_global_import_export.bl_idname,
        keymap_name='Window',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
        shift=True,
        alt=True,
    ),

    # OBJECT MODE
    PieKeymapDef(
        menu_idname=object_pies.BLUEHOLE_MT_pie_object_action.bl_idname,
        keymap_name='Object Mode',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
    ),
    PieKeymapDef(
        menu_idname=object_pies.BLUEHOLE_MT_pie_object_tool.bl_idname,
        keymap_name='Object Mode',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        shift=True,
    ),
    PieKeymapDef(
        menu_idname=object_pies.BLUEHOLE_MT_pie_object_hide.bl_idname,
        keymap_name='Object Mode',
        space_type='EMPTY',
        key='S',
        value='CLICK_DRAG',
        shift=True,
    ),
    PieKeymapDef(
        menu_idname=import_export_pies.BLUEHOLE_MT_pie_global_import_export.bl_idname,
        keymap_name='Object Mode',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
        shift=True,
        alt=True,
    ),

    # MESH
    PieKeymapDef(
        menu_idname=mesh_pies.BLUEHOLE_MT_pie_mesh_action.bl_idname,
        keymap_name='Mesh',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
    ),
    PieKeymapDef(
        menu_idname=mesh_pies.BLUEHOLE_MT_pie_mesh_tool.bl_idname,
        keymap_name='Mesh',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        shift=True,
    ),
    PieKeymapDef(
        menu_idname=mesh_pies.BLUEHOLE_MT_pie_mesh_hide.bl_idname,
        keymap_name='Mesh',
        space_type='EMPTY',
        key='S',
        value='CLICK_DRAG',
        shift=True,
    ),
    PieKeymapDef(
        menu_idname=uv_pies.BLUEHOLE_MT_pie_mesh_action_uvspecial.bl_idname,
        keymap_name='Mesh',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
        shift=True,
        alt=True,
    ),

    # 3D VIEW
    PieKeymapDef(
        menu_idname=add_pies.BLUEHOLE_MT_pie_add.bl_idname,
        keymap_name='3D View',
        space_type='VIEW_3D',
        key='A',
        value='CLICK_DRAG',
        shift=True,
    ),

    # UV EDITOR
    PieKeymapDef(
        menu_idname=uv_pies.BLUEHOLE_MT_pie_UV_cursor.bl_idname,
        keymap_name='UV Editor',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
        shift=True,
    ),
    PieKeymapDef(
        menu_idname=uv_pies.BLUEHOLE_MT_pie_UV_action_uvspecial.bl_idname,
        keymap_name='UV Editor',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
        shift=True,
        alt=True,
    ),
    PieKeymapDef(
        menu_idname=uv_pies.BLUEHOLE_MT_pie_UV_tool.bl_idname,
        keymap_name='UV Editor',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        shift=True,
    ),
    PieKeymapDef(
        menu_idname=uv_pies.BLUEHOLE_MT_pie_UV_action.bl_idname,
        keymap_name='UV Editor',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
    ),

    # CURVE
    PieKeymapDef(
        menu_idname=curve_pies.BLUEHOLE_MT_pie_curve_tool.bl_idname,
        keymap_name='Curve',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        shift=True,
    ),
    PieKeymapDef(
        menu_idname=curve_pies.BLUEHOLE_MT_pie_curve_action.bl_idname,
        keymap_name='Curve',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
    ),
    PieKeymapDef(
        menu_idname=curve_pies.BLUEHOLE_MT_pie_curve_hide.bl_idname,
        keymap_name='Curve',
        space_type='EMPTY',
        key='S',
        shift=True,
        repeat=True,
    ),

    # SCULPT
    PieKeymapDef(
        menu_idname=sculpt_pies.BLUEHOLE_MT_pie_sculpt_action.bl_idname,
        keymap_name='Sculpt',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
    ),
    PieKeymapDef(
        menu_idname=sculpt_pies.BLUEHOLE_MT_pie_sculpt_tool.bl_idname,
        keymap_name='Sculpt',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        shift=True,
    ),
    PieKeymapDef(
        menu_idname=sculpt_pies.BLUEHOLE_MT_pie_sculpt_simulation.bl_idname,
        keymap_name='Sculpt',
        space_type='EMPTY',
        key='RIGHTMOUSE',
        ctrl=True,
        shift=True,
        alt=True,
    ),
]


def get_all_pie_menu_defs() -> list[PieKeymapDef]:
    """
    Return all declared Blue Hole pie keymap definitions.
    """
    return PIE_MENU_DEFS
