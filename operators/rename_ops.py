"""
Operators to rename stuff.
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
from typing import List
from bpy.props import StringProperty
from ..preferences.prefs import prefs

# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class BH_OT_rename_in_outliner_and_unreal(bpy.types.Operator):
    bl_idname = "bh.rename_in_outliner_and_unreal"
    bl_label = "Rename in Outliner and in Unreal"

    new_name: bpy.props.StringProperty(name="New Name")

    @staticmethod
    def get_hierarchy_root(obj):
        """
        Walk up the parent chain and return the top-most object.
        """
        while obj.parent is not None:
            obj = obj.parent

        return obj

    @staticmethod
    def is_valid_asset_hierarchy_root(obj):
        """
        Check if object name matches a valid Asset Hierarchy prefix.
        """
        ah_prefix_lst: List[str] = [
            prefs().container.asset_hierarchy_struct_prefix_static_mesh,
            prefs().container.asset_hierarchy_struct_prefix_static_mesh_kit,
            prefs().container.asset_hierarchy_struct_prefix_skeletal_mesh,
        ]

        for ah_prefix in ah_prefix_lst:
            if obj.name.startswith(ah_prefix):
                return True

        return False

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if obj is None:
            return False

        root_obj = cls.get_hierarchy_root(obj)

        return cls.is_valid_asset_hierarchy_root(root_obj)

    def invoke(self, context, event):
        obj = context.active_object

        if obj is None:
            return {'CANCELLED'}

        root_obj = self.get_hierarchy_root(obj)

        self.new_name = root_obj.name

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "new_name")

    def execute(self, context):
        obj = context.active_object

        if obj is None:
            return {'CANCELLED'}

        root_obj = self.get_hierarchy_root(obj)

        if not self.is_valid_asset_hierarchy_root(root_obj):
            self.report({'ERROR'}, f'"{root_obj.name}" is not a valid Asset Hierarchy root.')
            return {'CANCELLED'}

        if not self.new_name:
            self.report({'ERROR'}, 'New name cannot be empty.')
            return {'CANCELLED'}

        old_name = root_obj.name
        root_obj.name = self.new_name

        # TODO:
        # Send rename command to Unreal here

        self.report(
            {'INFO'},
            f'Renamed "{old_name}" -> "{self.new_name}"'
        )

        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (
    BH_OT_rename_in_outliner_and_unreal,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
