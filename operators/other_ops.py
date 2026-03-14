"""
Operators that did not fit in another category
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

# Blender
import bpy
from bpy.props import *
from ..Lib.commonUtils.webUtils import open_url
from ..overlays.deluxe import applyDeluxePrefs

# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class WM_OT_URLOpen(bpy.types.Operator):
    """Open a website in the web-browser"""
    bl_idname = "wm.bh_open_url"
    bl_label = ""
    bl_options = {'INTERNAL'}

    url: StringProperty(
        name="URL",
        description="URL to open",
    )

    def execute(self, _context):
        open_url(self.url)
        return {'FINISHED'}


class WM_OT_Apply_Deluxe_Prefs(bpy.types.Operator):
    """ Apply Blue Hole Deluxe Preferences """
    bl_idname = "wm.bh_apply_deluxe_prefs"
    bl_label = "Apply DELUXE Preferences"
    bl_options = {'INTERNAL'}

    def execute(self, _context):
        applyDeluxePrefs.apply_deluxe_prefs()
        return {'FINISHED'}


class BH_OT_set_active_prefs_tab(bpy.types.Operator):
    bl_idname = "wm.bh_set_active_prefs_tab"
    bl_label = "Set Preferences Tab"
    bl_options = {'INTERNAL'}

    prop_path: StringProperty(name="Property Path", default="")
    tab: StringProperty(name="Tab", default="")

    def execute(self, context):
        addon = context.preferences.addons.get(__package__.split('.')[0])
        if not addon:
            self.report({'ERROR'}, 'Addon preferences not found')
            return {'CANCELLED'}

        target = addon.preferences

        try:
            parts = self.prop_path.split('.')
            for attr in parts[:-1]:
                target = getattr(target, attr)

            setattr(target, parts[-1], self.tab)

        except Exception as exc:
            self.report({'ERROR'}, f'Failed to set tab: {exc}')
            return {'CANCELLED'}

        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (
    WM_OT_URLOpen,
    WM_OT_Apply_Deluxe_Prefs,
    BH_OT_set_active_prefs_tab
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
