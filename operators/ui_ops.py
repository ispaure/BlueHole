"""
UI Operators
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

# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


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


# Runtime-only UI state (not saved in preferences)
draw_action_feature_keymaps_dropdown_state = {}


class WM_OT_BH_ToggleUISection(bpy.types.Operator):
    """Toggle a temporary UI section state"""
    bl_idname = "wm.bh_toggle_ui_section"
    bl_label = "Toggle UI Section"
    bl_options = {'INTERNAL'}

    section_key: StringProperty()

    def execute(self, context):
        current_value = draw_action_feature_keymaps_dropdown_state.get(self.section_key, False)
        draw_action_feature_keymaps_dropdown_state[self.section_key] = not current_value
        return {'FINISHED'}



# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (
    BH_OT_set_active_prefs_tab,
    WM_OT_BH_ToggleUISection,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
