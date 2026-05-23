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
from pathlib import Path
from bpy.props import StringProperty
from ..Lib.commonUtils.debugUtils import *
from ..blenderUtils.export import exportSettingsPresets
from ..blenderUtils.export.model.container import ContainerDummy
from ..preferences.prefs import prefs
from ..unrealUtils import renameUnreal

# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class BH_OT_rename_in_outliner_and_unreal(bpy.types.Operator):
    bl_idname = "bh.rename_in_outliner_and_unreal"
    bl_label = "Rename (in Outliner and Unreal) [Experimental]"
    bl_description = "Rename Container in Outliner and in Unreal (and resolve changes in source-control if applicable)"

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

        ah_prefix_lst: List[str] = [
            prefs().container.asset_hierarchy_struct_prefix_static_mesh,
            prefs().container.asset_hierarchy_struct_prefix_static_mesh_kit,
            prefs().container.asset_hierarchy_struct_prefix_skeletal_mesh,
        ]

        valid_prefix_str = ', '.join(ah_prefix_lst)

        if not self.is_valid_asset_hierarchy_root(root_obj):

            msg = (f'Cannot rename "{root_obj.name}" because it is not a valid Asset Container root. It must have '
                   f'one of these as prefix: {valid_prefix_str}.')
            log(Severity.ERROR, self.bl_label, msg, popup=True)
            return {'CANCELLED'}

        has_prefix = False
        for ah_prefix in ah_prefix_lst:
            if self.new_name.startswith(ah_prefix):
                has_prefix = True
                break

        if not has_prefix:
            msg = (f'Cannot rename "{root_obj.name}" to "{self.new_name}" because the new name does not have '
                   f'one of these as prefix: {valid_prefix_str}.')
            log(Severity.ERROR, self.bl_label, msg, popup=True)
            return {'CANCELLED'}

        # ------------------------------------------------------------------------------------------------------------------
        # Resolve .uasset path (Before)

        export_settings = exportSettingsPresets.get_export_settings(
            exportSettingsPresets.ExportSettingsPreset.UNREAL
        )

        container = ContainerDummy(root_obj, export_settings)

        before_uasset_path: Path = container.get_path_uasset()

        # ------------------------------------------------------------------------------------------------------------------
        # RENAME IN BLENDER

        # Renaming in Outliner
        old_name = root_obj.name
        root_obj.name = self.new_name

        # ------------------------------------------------------------------------------------------------------------------
        # Resolve .uasset path (After)

        export_settings = exportSettingsPresets.get_export_settings(
            exportSettingsPresets.ExportSettingsPreset.UNREAL
        )

        container = ContainerDummy(root_obj, export_settings)

        after_uasset_path: Path = container.get_path_uasset()

        # ------------------------------------------------------------------------------------------------------------------
        # RENAME IN UE

        renameUnreal.trigger_unreal_rename(before_uasset_path, after_uasset_path)

        # ------------------------------------------------------------------------------------------------------------------
        # FINAL MESSAGE

        msg = (
            f'Renamed "{old_name}" -> "{self.new_name}" in Blender\'s Outliner and in Unreal.\n\n'
            f'The associated Unreal asset was successfully renamed. However, the exported source file '
            f'used by the Asset Container export pipeline (such as the .FBX file) still uses the previous name.\n\n'
            f'It is recommended to re-export the Asset Container to Unreal so the exported source files are recreated '
            f'using the updated asset name.\n\n'
            f'Note:\n'
            f'Automatic renaming of the exported source file (.FBX) and related Source Control operations '
            f'(such as Perforce checkout/move support) are planned for a future update of this tool.'
        )

        log(Severity.INFO, self.bl_label, msg, popup=True)

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
