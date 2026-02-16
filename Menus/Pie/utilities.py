# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'


# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS

import bpy
from typing import *
from ...Lib.commonUtils.osUtils import *

# ----------------------------------------------------------------------------------------------------------------------
# HELPER FUNCTIONS


def open_pie_menu(pie, name: str, text: str, icon: Optional[str]=None):
    # This method opens a small line, not a regular pie menu
    # if icon is not None:
    #     pie.menu(name, text=text, icon=icon)
    # else:
    #     pie.menu(name, text=text)

    # This method opens up a proper pie menu
    if icon is not None:
        pie.operator("wm.call_menu_pie", text=text, icon=icon).name = name
    else:
        pie.operator("wm.call_menu_pie", text=text).name = name


def op_exists(op_idname: str) -> bool:
    """
    True if operator idname like 'hops.mod_lattice' is registered.
    """
    try:
        cat, name = op_idname.split(".", 1)
        op = getattr(getattr(bpy.ops, cat), name)
        op.get_rna_type()   # raises if not registered
        return True
    except Exception:
        return False


def pie_op_or_disabled(
    pie,
    addon_name: str,
    op_idname: str,
    *,
    text: str,
    icon: str = 'NONE',
    props: dict | None = None,
    platform_lst: List[OS] | None = None
):
    if platform_lst is not None:
        if get_os() not in platform_lst:
            return pie.operator("wm.disabled_addon", text=f'{text} (Unsupported on {get_os().value})', icon='ERROR')

    if op_exists(op_idname):
        btn = pie.operator(op_idname, text=text, icon=icon)
        if btn and props:
            for k, v in props.items():
                # if property doesn't exist, avoid raising during draw
                if hasattr(btn, k):
                    setattr(btn, k, v)
        return btn

    return pie.operator("wm.disabled_addon", text=f'{text} (Requires {addon_name})', icon='ERROR')
