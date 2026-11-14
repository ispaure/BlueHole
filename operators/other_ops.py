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
    bl_label = "Enable Deluxe Keymaps"
    bl_options = {'INTERNAL'}

    reviewed: BoolProperty(
        name="I reviewed saved shortcuts and resolved legacy conflicts",
        options={'SKIP_SAVE'},
    )

    def invoke(self, context, _event):
        self.reviewed = False
        if (applyDeluxePrefs.uses_blender_keyconfig(context.window_manager.keyconfigs)
                and applyDeluxePrefs.needs_keymap_review(context, prefs().prefs)):
            return context.window_manager.invoke_props_dialog(self, width=470)
        return self.execute(context)

    def draw(self, _context):
        self.layout.label(text="Review Blender Preferences > Keymap for old Deluxe edits.")
        self.layout.label(text="Keep personal shortcuts and remove any conflicting legacy edits.")
        self.layout.prop(self, 'reviewed')

    def execute(self, context):
        try:
            applyDeluxePrefs.apply_deluxe_prefs(context, prefs().prefs, reviewed=self.reviewed)
        except Exception as error:
            message = str(error) if isinstance(error, (ValueError, applyDeluxePrefs.ActivationError)) else (
                'Blender could not apply Deluxe keymaps. See the Blue Hole log and try again.')
            return _keymap_error(self, context, error, message)
        _report_keymap_preference(self, context, 'Deluxe keymaps enabled.')
        return {'FINISHED'}


class WM_OT_Disable_Deluxe_Keymaps(bpy.types.Operator):
    """Disable Deluxe shortcuts and keep your feature settings"""
    bl_idname = "wm.bh_disable_deluxe_keymaps"
    bl_label = "Disable Deluxe Keymaps"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        applyDeluxePrefs.disable_deluxe_keymaps(context, prefs().prefs)
        _report_keymap_preference(self, context, 'Deluxe keymaps disabled.')
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (
    WM_OT_URLOpen,
    WM_OT_Apply_Deluxe_Prefs,
    WM_OT_Disable_Deluxe_Keymaps,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
