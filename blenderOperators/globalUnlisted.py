"""
Adds Blue Hole Blender Operators [Unlisted]
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

import sys
import webbrowser
import subprocess

import bpy
from bpy.props import *

import BlueHole.blenderUtils.debugUtils as debugUtils
import BlueHole.blenderUtils.fileUtils as fileUtils
import BlueHole.envUtils.envUtils as envUtils
import BlueHole.wrappers.perforceWrapper as p4Wrapper
import BlueHole.envUtils.envUtils2 as envUtils2


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

# Start of File Debug Message
debugUtils.print_debug_msg('\nLoading Unlisted Operators...', show_verbose)


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
        webbrowser.open(self.url)
        return {'FINISHED'}


class WM_OT_SetActiveEnvironment(bpy.types.Operator):
    bl_idname = "wm.set_active_environment"
    bl_label = "Set the Active Environment"
    bl_options = {'INTERNAL'}

    env_items_lst = envUtils.get_env_lst_enum_property()
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
        envUtils2.set_environment(self.active_environment)
        try:
            envUtils.register_current_env()
        except:
            pass
        # msg = 'Load newly set environment?'
        # uiUtils.show_dialog_box('Blue Hole', msg, envUtils.register_current_env)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class WM_OT_AddEnvironment(bpy.types.Operator):
    bl_idname = "wm.add_environment"
    bl_label = "Create an Environment"
    bl_options = {'INTERNAL'}

    env_items_lst = envUtils.get_env_lst_enum_property()

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
        envUtils2.add_env(self.new_environment_name_str, self.add_based_from_environment)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class WM_OT_DeleteAnEnvironment(bpy.types.Operator):
    bl_idname = "wm.delete_environment"
    bl_label = "Delete an Environment"
    bl_options = {'INTERNAL'}

    env_items_lst = envUtils.get_env_lst_enum_property(exclude_default=True)

    if len(env_items_lst) > 0:
        deletable_environments: bpy.props.EnumProperty(name="Deletable Environments",
                                                       description="Defines the project directory structure.",
                                                       items=env_items_lst,
                                                       default=env_items_lst[0][0])
    else:
        deletable_environments: bpy.props.EnumProperty(name="Deletable Environments",
                                                       description="Defines the project directory structure.",
                                                       items=('', '', ''),
                                                       default='')

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text='Select an environment and press OK to delete.')
        column = box.column()
        row = column.row()
        row.prop(self, "deletable_environments")
        row = column.row()
        row.label(text='WARNING: THIS ACTION WILL SHUT DOWN BLENDER!')
        row = column.row()
        row.label(text='You may want to save your scene before proceeding.')

    def execute(self, context):
        envUtils2.delete_env(self.deletable_environments)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class WM_OT_ApplyActiveEnvironment(bpy.types.Operator):
    """
    I think this was only used to Apply Changes in options, which is not necessary anymore (only for custom scripts)
    TODO: Can probably delete this!
    """
    bl_idname = "wm.bh_apply_active_environment"
    bl_label = "LOAD ENV"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        try:
            envUtils.register_current_env()
        except:
            pass
        return {'FINISHED'}


class WM_OT_CustomizeEnvVariables(bpy.types.Operator):
    """Customize the Current Environment Variables in external text-editor"""
    bl_idname = "wm.bh_customize_env_variables"
    bl_label = "Customize Environment Variables..."
    bl_options = {'INTERNAL'}

    def execute(self, _context):
        env_config_path = fileUtils.get_current_env_var_path()
        if sys.platform == 'win32':
            fileUtils.open_url(env_config_path)
        else:
            subprocess.call(['open', '-a', 'TextEdit', env_config_path])
        return {'FINISHED'}


class WM_OT_SetP4EnvSettings(bpy.types.Operator):
    """Set Perforce Environment Settings"""
    bl_idname = "wm.bh_set_p4_env_settings"
    bl_label = "Set Perforce Environment Settings"
    bl_options = {'INTERNAL'}

    def execute(self, _context):
        p4Wrapper.set_p4_env_settings()
        return {'FINISHED'}


class WM_OT_MergeLast(bpy.types.Operator):
    bl_idname = "wm.bh_merge_last"
    bl_label = "Merge Last"
    bl_options = {'INTERNAL'}

    def execute(self, _context):
        try:
            bpy.ops.mesh.merge(type='LAST')
        except:
            bpy.ops.mesh.merge()
        return {'FINISHED'}


class BH_OT_MOD_Decimate(bpy.types.Operator):
    bl_idname = "bh.mod_decimate"
    bl_label = "Adds Decimate Modifier to all Selected Meshes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def invoke(self, context, event):
        for object in [o for o in context.selected_objects if o.type == 'MESH']:
            if event.ctrl:
                self.add_decimate_modifier(context, object, event)
            else:
                if not self.decimate_modifiers(object):
                    self.add_decimate_modifier(context, object, event)
        return {"FINISHED"}

    @staticmethod
    def decimate_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "DECIMATE"]

    def add_decimate_modifier(self, context, object, event):
        decim_mod = object.modifiers.new(name="decimate", type="DECIMATE")
        if event.shift:
            decim_mod.decimate_type = 'UNSUBDIV'
            decim_mod.iterations = 1
        else:
            decim_mod.decimate_type = 'DISSOLVE'
            decim_mod.angle_limit = math.radians(.05)
        decim_mod.delimit = {'NORMAL', 'SHARP'}
        if context.mode == 'EDIT_MESH':
            decim_mod.decimate_type = 'COLLAPSE'
            vg = object.vertex_groups.new(name='Decimate')
            bpy.ops.object.vertex_group_assign()
            decim_mod.vertex_group = vg.name


class WM_OT_disabled_addon_interactive_tools(bpy.types.Operator):
    bl_idname = "wm.disabled_addon_interactive_tools"
    bl_label = "Interactive Tools add-on is not enabled"
    bl_description = "Interactive Tools add-on is required for this button"

    open_prefs: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        self.report({'WARNING'}, "Interactive Tools add-on is not enabled. Enable it in Preferences > Add-ons.")
        if self.open_prefs:
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {'CANCELLED'}


class WM_OT_disabled_addon_machin3tools(bpy.types.Operator):
    bl_idname = "wm.disabled_addon_machin3tools"
    bl_label = "Interactive Tools add-on is not enabled"
    bl_description = "Interactive Tools add-on is required for this button"

    open_prefs: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        self.report({'WARNING'}, "MACHIN3tools add-on is not enabled. Enable it in Preferences > Add-ons.")
        if self.open_prefs:
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {'CANCELLED'}


class WM_OT_disabled_addon_hardops(bpy.types.Operator):
    bl_idname = "wm.disabled_addon_hardops"
    bl_label = "HardOps add-on is not enabled"
    bl_description = "HardOps add-on is required for this button"

    open_prefs: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        self.report({'WARNING'}, "HardOps add-on is not enabled. Enable it in Preferences > Add-ons.")
        if self.open_prefs:
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {'CANCELLED'}


class WM_OT_disabled_addon_mesh_angle(bpy.types.Operator):
    bl_idname = "wm.disabled_addon_mesh_angle"
    bl_label = "Mesh Angle add-on is not enabled"
    bl_description = "Mesh Angle add-on is required for this button"

    open_prefs: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        self.report({'WARNING'}, "Mesh Angle add-on is not enabled. Enable it in Preferences > Add-ons.")
        if self.open_prefs:
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {'CANCELLED'}


class WM_OT_disabled_addon_dreamuv(bpy.types.Operator):
    bl_idname = "wm.disabled_addon_dreamuv"
    bl_label = "DreamUV add-on is not enabled"
    bl_description = "DreamUV add-on is required for this button"

    open_prefs: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        self.report({'WARNING'}, "DreamUV add-on is not enabled. Enable it in Preferences > Add-ons.")
        if self.open_prefs:
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {'CANCELLED'}


class WM_OT_disabled_addon_zen_uv(bpy.types.Operator):
    bl_idname = "wm.disabled_addon_zen_uv"
    bl_label = "Zen UV add-on is not enabled"
    bl_description = "Zen UV add-on is required for this button"

    open_prefs: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        self.report({'WARNING'}, "Zen UV add-on is not enabled. Enable it in Preferences > Add-ons.")
        if self.open_prefs:
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {'CANCELLED'}


class WM_OT_disabled_addon_uv_toolkit(bpy.types.Operator):
    bl_idname = "wm.disabled_addon_uv_toolkit"
    bl_label = "UV Toolkit add-on is not enabled"
    bl_description = "UV Toolkit add-on is required for this button"

    open_prefs: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        self.report({'WARNING'}, "UV Toolkit add-on is not enabled. Enable it in Preferences > Add-ons.")
        if self.open_prefs:
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {'CANCELLED'}


class ZUV_OT_trim_mode(bpy.types.Operator):
    bl_idname = "zuv.set_trim_tool"
    bl_label = "Trim Select Mode"

    def execute(self, context):

        # 1) Set Zen-UV tool mode via context toggle
        bpy.ops.wm.context_toggle(
            data_path="scene.zen_uv.ui.uv_tool.select_trim"
        )

        # 2) Activate the actual Zen-UV tool
        bpy.ops.wm.tool_set_by_id(name="zenuv.uv_tool")

        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (WM_OT_URLOpen,
           WM_OT_SetP4EnvSettings,
           WM_OT_SetActiveEnvironment,
           WM_OT_ApplyActiveEnvironment,
           WM_OT_CustomizeEnvVariables,
           BH_OT_MOD_Decimate,
           WM_OT_AddEnvironment,
           WM_OT_DeleteAnEnvironment,
           WM_OT_MergeLast,
           WM_OT_disabled_addon_interactive_tools,
           WM_OT_disabled_addon_machin3tools,
           WM_OT_disabled_addon_hardops,
           WM_OT_disabled_addon_mesh_angle,
           WM_OT_disabled_addon_dreamuv,
           WM_OT_disabled_addon_zen_uv,
           WM_OT_disabled_addon_uv_toolkit,
           ZUV_OT_trim_mode
           )


# Register
def register():
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    # Unregister Operators
    for cls in classes:
        bpy.utils.unregister_class(cls)


# ----------------------------------------------------------------------------------------------------------------------
# End of File Debug Message
debugUtils.print_debug_msg('Unlisted Operators Loaded!', show_verbose)
