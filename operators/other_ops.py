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
from ..Lib.commonUtils.integrations.web import open_url
from ..Lib.commonUtils.runtime.diagnostics import Severity, log
from ..overlays.deluxe import applyDeluxePrefs
from ..preferences.prefs import prefs

# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


def _keymap_error(operator, context, error, message):
    log(Severity.ERROR, operator.bl_label, f'{type(error).__name__}: {message}')
    if not bpy.app.background:
        def draw(menu, _context):
            menu.layout.label(text=message)

        context.window_manager.popup_menu(draw, title=operator.bl_label, icon='ERROR')
    operator.report({'WARNING'}, message)
    return {'CANCELLED'}


def _report_keymap_preference(operator, context, message):
    if not context.preferences.use_preferences_save:
        message += ' Use Save Preferences to keep this choice after restarting Blender.'
    operator.report({'INFO'}, message)


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
    """Enable the Deluxe shortcut catalog on the built-in Blender preset"""
    bl_idname = "wm.bh_apply_deluxe_prefs"
    bl_label = "Enable Blue Hole Keymaps & Pie Menus"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        try:
            applyDeluxePrefs.apply_deluxe_prefs(context, prefs().prefs)
        except Exception as error:
            message = str(error) if isinstance(error, (ValueError, applyDeluxePrefs.ActivationError)) else (
                'Blender could not apply Deluxe keymaps. See the Blue Hole log and try again.')
            return _keymap_error(self, context, error, message)
        _report_keymap_preference(self, context, 'Blue Hole Keymaps & Pie Menus enabled.')
        return {'FINISHED'}


class WM_OT_Disable_Deluxe_Keymaps(bpy.types.Operator):
    """Disable Deluxe shortcuts and keep your feature settings"""
    bl_idname = "wm.bh_disable_deluxe_keymaps"
    bl_label = "Disable Blue Hole Keymaps & Pie Menus"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        applyDeluxePrefs.disable_deluxe_keymaps(context, prefs().prefs)
        _report_keymap_preference(self, context, 'Blue Hole Keymaps & Pie Menus disabled.')
        return {'FINISHED'}


class WM_OT_BH_dopesheet_frame_jump(bpy.types.Operator):
    """Jump to the scene boundary from the Dope Sheet window"""
    bl_idname = 'wm.bh_dopesheet_frame_jump'
    bl_label = 'Dope Sheet Frame Jump'
    bl_options = {'INTERNAL'}

    end: BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        area, region = context.area, context.region
        return (area is not None and area.type == 'DOPESHEET_EDITOR'
                and region is not None and region.type == 'WINDOW'
                and bpy.ops.screen.frame_jump.poll())

    def execute(self, context):
        return bpy.ops.screen.frame_jump(end=self.end)


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (
    WM_OT_URLOpen,
    WM_OT_Apply_Deluxe_Prefs,
    WM_OT_Disable_Deluxe_Keymaps,
    WM_OT_BH_dopesheet_frame_jump,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
