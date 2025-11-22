"""
Operators that did not fit in another category
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
# IMPORTS


import webbrowser

import bpy
from bpy.props import *


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


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (WM_OT_URLOpen,
           BH_OT_MOD_Decimate,
           WM_OT_MergeLast
           )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators
