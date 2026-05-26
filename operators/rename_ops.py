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
from typing import List, Type
from pathlib import Path
from bpy.props import StringProperty
from ..Lib.commonUtils.debugUtils import *
from ..blenderUtils.export import exportSettingsPresets
from ..blenderUtils.export.model.container import ContainerDummy
from ..blenderUtils.export.model.containerGroup import ContainerGroup
from ..blenderUtils import objectUtils
from ..preferences.prefs import prefs
from ..unrealUtils import renameUnreal
from ..blenderUtils.export.model import containerUtils

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

        # Get valid prefixes
        ah_prefix_lst: List[str] = [
            prefs().container.asset_hierarchy_struct_prefix_static_mesh,
            prefs().container.asset_hierarchy_struct_prefix_static_mesh_kit,
            prefs().container.asset_hierarchy_struct_prefix_skeletal_mesh,
        ]

        valid_prefix_str = ', '.join(ah_prefix_lst)

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
        is_found_container: bool = False
        for container_grp_cls in container_grp_cls_lst:
            for container in container_grp_cls.container_lst:
                if container.root == root_obj:
                    is_found_container = True
                    break
            if is_found_container:
                break

        if not is_found_container:
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
            msg = f'Could not rename asset in Unreal to path "{after_uasset_path}" as it already exists.'
            log(Severity.ERROR, self.bl_label, msg, popup=True)
            return {'CANCELLED'}

        # Rename in UE
        result = renameUnreal.trigger_unreal_rename(before_uasset_path, after_uasset_path)

        if not result:
            # If not result / unsuccessful, revert the name on the asset
            msg = f'Since could not rename successfully in Unreal, reverting name back on asset to "{old_name}".'
            log(Severity.WARNING, self.bl_label, )
            root_obj.name = old_name

        # Final message (it worked!)

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
