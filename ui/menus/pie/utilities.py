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
from ....Lib.commonUtils.osUtils import *
from ....operators import external_addon_ops
from ....blenderUtils.operatorUtils import op_exists

# ----------------------------------------------------------------------------------------------------------------------
# HELPER FUNCTIONS


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
            col = pie.column()
            col.enabled = False
            return col.operator(
                external_addon_ops.WM_OT_unsupported_os.bl_idname,
                text=f'{text} (Unsupported on {get_os().value})',
                icon='ERROR'
            )

    if op_exists(op_idname):
        btn = pie.operator(op_idname, text=f'{text} [{addon_name}]', icon=icon)
        if btn and props:
            for k, v in props.items():
                # if property doesn't exist, avoid raising during draw
                if hasattr(btn, k):
                    setattr(btn, k, v)
        return btn

    col = pie.column()
    col.enabled = False
    return col.operator(
        external_addon_ops.BH_OT_addon_missing.bl_idname,
        text=f'{text} (Requires {addon_name})',
        icon='ERROR'
    )
