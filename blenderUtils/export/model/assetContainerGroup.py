"""
The March 2026 refactor of exportUtils2, but only section about individual asset exports.
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

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

# Blue Hole
from abc import abstractmethod
from ..exportSettings import *
from ....Lib.commonUtils.debugUtils import *
from ....preferences.prefs import *
from ... import filterUtils, sceneUtils, objectUtils
from .containerGroup import ContainerGroup


# ----------------------------------------------------------------------------------------------------------------------
# CODE

class AssetContainerGroup(ContainerGroup):

    CONTAINERS_NAME = 'Asset'
    CONTAINER_CLASS = None

    def __init__(self, export_settings: ExportSettings):
        super().__init__(export_settings)

    def set_containers_from_selection(self):

        # Get list of objects (Selection)
        obj_lst = objectUtils.get_selection()

        # Set Container from Object List
        self._set_containers_from_obj_lst(obj_lst)

        # Throw error if no containers
        if len(self.container_lst) == 0:
            self.__critical_set_containers_selection_missing()

    def set_containers_from_scene(self):

        # Get list of objects (Scene)
        obj_lst = sceneUtils.get_scene_obj_lst()

        # Set Container from Object List
        self._set_containers_from_obj_lst(obj_lst)

        # Throw error if no containers
        if len(self.container_lst) == 0:
            self.__critical_set_containers_scene_missing()

    def _set_containers_from_obj_lst(self, obj_lst):
        # Reset
        self.container_lst = []

        # Get hierarchy roots
        root_obj_lst = self._get_root_lst_from_obj_lst(obj_lst)

        # For each root, make a hierarchy class
        for root_obj in root_obj_lst:
            hierarchy = self.CONTAINER_CLASS(root_obj, self.export_settings)
            self.container_lst.append(hierarchy)

    @abstractmethod
    def _get_root_lst_from_obj_lst(self, obj_lst):
        """Must be implemented by subclasses to define containers from scene. """
        pass

    def _export_checks(self, send: bool):
        # Validate Source Content
        validate_source_content: bool = True if self.export_settings.engine == Engine.UNREAL and send else False
        check_source_content_root_path_exist: bool = validate_source_content
        check_blend_in_source_content: bool = validate_source_content

        # Validate Unity Assets Path
        check_unity_assets_path_exist = True if self.export_settings.engine == Engine.UNITY and send else False

        # Check tests
        chk_result = filterUtils.check_tests(self.CONTAINERS_NAME,
                                             check_blend_exist=True,
                                             check_blend_loc_in_dir_structure=True,
                                             check_source_content_root_path_exist=check_source_content_root_path_exist,
                                             check_blend_in_source_content=check_blend_in_source_content,
                                             check_unity_assets_path_exist=check_unity_assets_path_exist)
        return chk_result

    # ----------------------------------------------------------------------------------------------------------------------
    # CRITICAL ERROR MESSAGES

    def __critical_set_containers_scene_missing(self):
        # Define the prefix variables first
        static_mesh_prefix = prefs().container.asset_hierarchy_struct_prefix_static_mesh
        kit_prefix = prefs().container.asset_hierarchy_struct_prefix_static_mesh_kit
        skeletal_mesh_prefix = prefs().container.asset_hierarchy_struct_prefix_skeletal_mesh

        # Collect prefixes
        prefixes = [
            static_mesh_prefix,
            kit_prefix,
            skeletal_mesh_prefix,
        ]

        # Remove None / empty values and deduplicate while preserving order
        unique_prefixes = list(dict.fromkeys(p for p in prefixes if p))

        # Format prefix string
        formatted_prefixes = ", ".join(f'"{p}"' for p in unique_prefixes)

        # Construct the message
        msg = (
            f'{self.CONTAINERS_NAME} validation failed.\n\n'
            f'What went wrong:\n'
            f'No Asset Hierarchy was found. Asset Hierarchies must be created '
            f'using a valid prefix defined in the Active Environment Settings.\n\n'
            f'What to do:\n'
            f'Create a new Asset Hierarchy using the Blue Hole Header Menu, or ensure your existing Asset Hierarchy '
            f'uses one of the required prefixes.\n\n'
            f'Valid prefixes: {formatted_prefixes}\n\n'
            f'Export aborted.'
        )

        log(Severity.CRITICAL, self.CONTAINERS_NAME, msg, popup=True)

    def __critical_set_containers_selection_missing(self):
        # Define the prefix variables first
        static_mesh_prefix = prefs().container.asset_hierarchy_struct_prefix_static_mesh
        kit_prefix = prefs().container.asset_hierarchy_struct_prefix_static_mesh_kit
        skeletal_mesh_prefix = prefs().container.asset_hierarchy_struct_prefix_skeletal_mesh

        # Construct the message
        msg = (
            f'{self.CONTAINERS_NAME} validation failed.\n\n'
            f'What went wrong:\n'
            f'No valid Asset Hierarchy was found in the current selection. Asset Hierarchies must exist at the root '
            f'of the scene and use a valid prefix defined in the Active Environment Settings.\n\n'
            f'What to do:\n'
            f'Select at least one Asset Hierarchy at the root of the scene, and ensure its name uses one of the required prefixes.\n\n'
            f'Valid prefixes:\n'
            f'"{static_mesh_prefix}", "{kit_prefix}", "{skeletal_mesh_prefix}"\n\n'
            f'Export aborted.'
        )
        log(Severity.CRITICAL, self.CONTAINERS_NAME, msg, popup=True)


def get_hierarchy_prefix_lst():
    """
    Returns list of hierarchy prefix
    """
    prefix_lst = [prefs().container.asset_hierarchy_struct_prefix_static_mesh,
                  prefs().container.asset_hierarchy_struct_prefix_static_mesh_kit,
                  prefs().container.asset_hierarchy_struct_prefix_skeletal_mesh]
    return prefix_lst
