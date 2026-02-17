"""
Operators related to Blue Hole environments
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

# System
import sys
import subprocess

# Blender
import bpy
from bpy.props import *

# Blue Hole
from ..blenderUtils import blenderFile
from ..environment import envManager, model
from ..Lib.commonUtils import webUtils
from ..Lib.commonUtils.debugUtils import *


# ----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS


def deletable_env_items(self, context):
    items = envManager.get_env_lst_enum_property(exclude_default=True)
    if not items:
        return [("NONE", "No environments to delete", "Only 'default' exists.")]
    return items


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class WM_OT_SetActiveEnvironment(bpy.types.Operator):
    bl_idname = "wm.set_active_environment"
    bl_label = "Set the Active Environment"
    bl_description = 'Set the Active Environment, valid for this Blender session.'
    bl_options = {'INTERNAL'}

    env_items_lst = envManager.get_env_lst_enum_property()
    # Active Environment
    active_environment: bpy.props.EnumProperty(name="Active Environment",
                                     description="Defines the project directory structure.",
                                     items=env_items_lst,
                                     default='default'
                                     )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text='(For CURRENTLY OPENED Blender only.)')
        column = box.column()
        row = column.row()
        row.prop(self, "active_environment")
        box.label(text='To save as default, save Blender Preferences.')

    def execute(self, context):
        envManager.set_pref_current_env(self.active_environment)
        env_cls = envManager.get_env_from_prefs_active_env()
        env_cls.set_pref_from_ini()
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class WM_OT_AddEnvironment(bpy.types.Operator):
    bl_idname = "wm.add_environment"
    bl_label = "Create an Environment"
    bl_options = {'INTERNAL'}

    env_items_lst = envManager.get_env_lst_enum_property()

    add_based_from_environment: bpy.props.EnumProperty(name="Environment",
                                                       description="Environment to base the new one from. "
                                                                   "\nWill be a copy until you modify settings.",
                                                       items=env_items_lst,
                                                       default='default'
                                                       )

    new_environment_name_str: bpy.props.StringProperty(name="New Name",
                                                       description="Defines the name of the new environment",
                                                       default='my_environment'
                                                       )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text='Select an environment to base the new one from.')
        column = box.column()
        row = column.row()
        row.prop(self, "add_based_from_environment")
        row = column.row()
        row.label(text='Enter name of new environment')
        row = column.row()
        row.prop(self, "new_environment_name_str")
        row = column.row()
        row.label(text='WARNING: THIS ACTION WILL SHUT DOWN BLENDER!')
        row = column.row()
        row.label(text='You may want to save your scene before proceeding.')

    def execute(self, context):
        sanitized_name = self.new_environment_name_str.replace(' ', '_').replace('.', '_')
        env_cls = model.Environment(sanitized_name)
        env_cls.add_env(model.Environment(self.add_based_from_environment))
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class WM_OT_DeleteAnEnvironment(bpy.types.Operator):
    bl_idname = "wm.delete_environment"
    bl_label = "Delete an Environment"
    bl_options = {'INTERNAL'}

    deletable_environments: bpy.props.EnumProperty(
        name="Deletable Environments",
        description="Defines the project directory structure.",
        items=deletable_env_items,  # callback
        default=0,                  # ✅ must be int when items is a function
    )

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        items = envManager.get_env_lst_enum_property(exclude_default=True)
        if not items:
            box.label(text="No environments to delete (only 'default' exists).")
        else:
            box.label(text="Select an environment and press OK to delete.")
            box.prop(self, "deletable_environments")

        box.label(text="WARNING: THIS ACTION WILL SHUT DOWN BLENDER!")
        box.label(text="You may want to save your scene before proceeding.")

    def invoke(self, context, event):
        items = envManager.get_env_lst_enum_property(exclude_default=True)
        if not items:
            log(Severity.CRITICAL, "Delete Environment",
                "Cannot delete an environment (no other environment than the default is there).")
            return {'CANCELLED'}

        # optional: force it to first valid env each time
        self.deletable_environments = items[0][0]

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        if self.deletable_environments == "NONE":
            log(Severity.CRITICAL, "Delete Environment",
                "Cannot delete an environment (no other environment than the default is there).")
            return {'CANCELLED'}

        env_cls = model.Environment(self.deletable_environments)
        env_cls.delete_env()
        return {'FINISHED'}


class WM_OT_CustomizeEnvVariables(bpy.types.Operator):
    """Customize the Current Environment Variables in external text-editor"""
    bl_idname = "wm.bh_customize_env_variables"
    bl_label = "Customize Environment Variables..."
    bl_options = {'INTERNAL'}

    def execute(self, _context):
        env_config_path = blenderFile.get_current_env_var_path()
        if sys.platform == 'win32':
            webUtils.open_url(env_config_path)
        else:
            subprocess.call(['open', '-a', 'TextEdit', env_config_path])
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (WM_OT_SetActiveEnvironment,
           WM_OT_CustomizeEnvVariables,
           WM_OT_AddEnvironment,
           WM_OT_DeleteAnEnvironment
           )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators
