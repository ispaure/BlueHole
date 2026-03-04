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
from ..preferences.prefs import prefs

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


class BH_OT_set_active_container_settings_tab(bpy.types.Operator):
    bl_idname = "wm.bh_set_active_container_settings_tab"
    bl_label = "Set Container Settings Tab"
    bl_options = {'INTERNAL'}

    tab: StringProperty(name="Tab", default="")

    def execute(self, context):
        # Use the *actual* addon preferences instance
        addon = context.preferences.addons.get(__package__.split('.')[0])
        if not addon:
            self.report({'ERROR'}, 'Addon preferences not found')
            return {'CANCELLED'}

        addon.preferences.container.active_container_settings_tab = self.tab
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (WM_OT_URLOpen,
           WM_OT_Apply_Deluxe_Prefs,
           BH_OT_set_active_container_settings_tab)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators
