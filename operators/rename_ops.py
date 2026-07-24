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
from typing import List, Type, Optional
from pathlib import Path
from bpy.props import StringProperty
from ..Lib.commonUtils.debugUtils import *
from ..blenderUtils.export import exportSettingsPresets
from ..blenderUtils.export.model.container import ContainerDummy, Container
from ..blenderUtils.export.model.containerGroup import ContainerGroup
from ..blenderUtils import objectUtils
from ..preferences.prefs import prefs
from ..unrealUtils import renameUnreal, communicateUnreal
from ..blenderUtils.export.model import containerUtils
from ..wrappers.perforce import p4_file
from ..Lib.commonUtils import fileUtils

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

        # Test Unreal connection before asking for a new name
        if not communicateUnreal.test_unreal_connection(silent=False):
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

        # Get valid prefixes
        ah_prefix_lst: List[str] = [
            prefs().container.asset_hierarchy_struct_prefix_static_mesh,
            prefs().container.asset_hierarchy_struct_prefix_static_mesh_kit,
            prefs().container.asset_hierarchy_struct_prefix_skeletal_mesh,
        ]

        valid_prefix_str = ', '.join(ah_prefix_lst)

        # Validate the selected name starts with one of the prefix
        start_with_prefix: bool = False
        for ah_prefix in ah_prefix_lst:
            if self.new_name.startswith(ah_prefix):
                start_with_prefix = True
                break

        if not start_with_prefix:
            msg = (f'Cannot use new name "{self.new_name}" as it doesn\'t start with one of '
                   f'these prefixes: {valid_prefix_str}')
            log(Severity.ERROR, self.bl_label, msg, popup=True)
            return {'CANCELLED'}

        # This is for unreal, get unreal settings
        export_settings = exportSettingsPresets.get_export_settings(exportSettingsPresets.ExportSettingsPreset.UNREAL)

        # Get all the valid container groups
        container_groups: List[Type] = containerUtils.get_container_groups_all()

        # Set the groups to have all the containers in the scene
        container_grp_cls_lst = []
        for container_grp in container_groups:
            container_grp_cls = container_grp(export_settings)
            container_grp_cls.set_containers_from_scene(silent_if_empty=True)
            container_grp_cls_lst.append(container_grp_cls)

        # Get the upmost root of the current object (all hierarchies have a root object)
        root_obj = objectUtils.get_obj_upmost_parent(obj)

        # Make sure that this lines up with an existing asset container
        found_container: Optional[Container] = None
        for container_grp_cls in container_grp_cls_lst:
            for container in container_grp_cls.container_lst:
                if container.root == root_obj:
                    found_container = container
                    break

        if found_container is None:
            msg = (f'Cannot rename "{root_obj.name}" because it is not a valid Asset Container in this environment. '
                   f'Most likely it is missing one of these as prefix: {valid_prefix_str}. If you are unsure what '
                   f'is the issue, feel free to recreate this Asset Container from the Blue Hole header menu.')
            log(Severity.ERROR, self.bl_label, msg, popup=True)
            return {'CANCELLED'}

        # Make sure that the new name isn't already chosen for a container group
        for container_grp_cls in container_grp_cls_lst:
            for container in container_grp_cls.container_lst:
                if self.new_name == container.name:
                    msg = (f'Cannot rename "{root_obj.name}" to "{self.new_name}" because that name is already in use '
                           f'for an existing {container.CONTAINER_NAME}. Please pick a different name')
                    log(Severity.ERROR, self.bl_label, msg, popup=True)
                    return {'CANCELLED'}

        # Resolve pre-change .uasset path
        pre_container_grp = ContainerDummy(root_obj, export_settings)
        before_uasset_path: Path = pre_container_grp.get_path_uasset()
        if not os.path.isfile(str(before_uasset_path)):
            msg = f'Could not rename asset in Unreal at path "{before_uasset_path}", as it doesn\'t currently exist.'
            log(Severity.ERROR, self.bl_label, msg, popup=True)
            return {'CANCELLED'}

        # Renaming in Outliner
        old_name = root_obj.name
        root_obj.name = self.new_name

        # Resolve post-change .uasset path
        post_container_grp = ContainerDummy(root_obj, export_settings)
        after_uasset_path: Path = post_container_grp.get_path_uasset()
        if os.path.isfile(str(after_uasset_path)):
            root_obj.name = old_name  # Revert to the last name
            msg = f'Could not rename asset in Unreal to path "{after_uasset_path}" as it already exists.'
            log(Severity.ERROR, self.bl_label, msg, popup=True)
            return {'CANCELLED'}

        # Rename in UE
        result = renameUnreal.trigger_unreal_rename(before_uasset_path, after_uasset_path)

        if not result:
            # If not result / unsuccessful, revert the name on the asset
            msg = f'Since could not rename successfully in Unreal, reverting name back on asset to "{old_name}".'
            log(Severity.WARNING, self.bl_label, msg, popup=True)
            root_obj.name = old_name
            return {'CANCELLED'}

        # Checkout current .FBX (if exists -- it should)
        # Need to get the new container of proper type to determine the path

        # Did this before but need a refresh
        # Set the groups to have all the containers in the scene
        container_grp_cls_lst = []
        for container_grp in container_groups:
            container_grp_cls = container_grp(export_settings)
            container_grp_cls.set_containers_from_scene(silent_if_empty=True)
            container_grp_cls_lst.append(container_grp_cls)

        container_accounting_for_rename: Optional[Container] = None
        for container_grp_cls in container_grp_cls_lst:
            for container in container_grp_cls.container_lst:
                if container.name == self.new_name:
                    container_accounting_for_rename = container

        if container_accounting_for_rename is None:
            msg = f'Fatal error, could not locate container "{self.new_name}" after rename!'
            log(Severity.CRITICAL, self.bl_label, msg)
            return {'CANCELLED'}

        # 1. Checkout .FBX (if present on disk and not already checked out)
        if prefs().sourcecontrol.source_control_enable:
            if prefs().sourcecontrol.source_control_solution == 'perforce':
                old_path = found_container.path
                if not os.path.isfile(str(old_path)):
                    msg = (f'Previous named "{old_path}" Path did not exist, so could not move to new location. '
                           f'Recommend re-exporting this hierarchy from Blender.')
                    log(Severity.ERROR, self.bl_label, msg, popup=True)
                    return {'CANCELLED'}
                new_path = container_accounting_for_rename.path
                old_p4_file = p4_file.P4File(str(old_path))
                old_p4_file.open_for_edit(silent=True, allow_sync=True)
                # 2. Do P4 Move
                old_p4_file.run_p4_move(str(new_path))

        if os.path.isfile(str(found_container.path)):
            # Move file
            fileUtils.copy_file(found_container.path, container_accounting_for_rename.path)
            # Delete file
            if os.path.isfile(str(found_container.path)):
                file_to_delete = fileUtils.File(found_container.path)
                file_to_delete.delete_file()

        # Final message (it worked!)
        msg = (
            f'Renamed "{old_name}" -> "{self.new_name}" in Blender\'s Outliner and in Unreal.\n\n'
            f'The associated Unreal asset was successfully renamed. Exported source files used by the '
            f'Asset Container export pipeline (such as the .FBX file) were also renamed to match the updated asset name.\n\n'
            f'Relevant Source Control operations required for the rename/move were automatically performed '
            f'(such as Perforce checkout and move support where applicable).\n\n'
            f'The Asset Container and its associated exported source files are now fully synchronized with the updated name.'
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
