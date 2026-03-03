"""
The March 2026 refactor of exportUtils2. Once done, the old one should be removed and this one used instead.
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

# System
from typing import *

# Blue Hole
from .exportSettings import *
from ...Lib.commonUtils.debugUtils import *
from .. import sceneUtils, objectUtils, filterUtils
from ...preferences.prefs import *
from containers.assetHierarchyContainer import AssetHierarchyContainer
from containers.modelContainers import Containers

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE

ah_tool_name = 'Asset Hierarchy Exporter (V3)'


class AssetHierarchies(Containers):

    CONTAINERS_NAME = 'Asset Hierarchies'

    def __init__(self, export_settings: ExportSettings):
        super().__init__(export_settings)

    def set_containers_from_selection(self):

        # Get list of objects (Selection)
        obj_lst = objectUtils.get_selection()

        # Set Container from Object List
        self.__set_containers_from_obj_lst(obj_lst)

        # Throw error if no containers
        if len(self.container_lst) == 0:
            self.__critical_set_containers_selection_missing()

    def set_containers_from_scene(self):

        # Get list of objects (Scene)
        obj_lst = sceneUtils.get_scene_obj_lst()

        # Set Container from Object List
        self.__set_containers_from_obj_lst(obj_lst)

        # Throw error if no containers
        if len(self.container_lst) == 0:
            self.__critical_set_containers_scene_missing()

    def __set_containers_from_obj_lst(self, obj_lst):
        # Reset
        self.container_lst = []

        # Append list of Asset Hierarchy
        self.container_lst.append(self.__get_asset_hierarchy_lst_from_obj_lst(obj_lst))

        # Append list of Collection Asset Hierarchy
        # TODO: Implement

    def __get_asset_hierarchy_lst_from_obj_lst(self, obj_lst):

        # Get root objects
        root_obj_lst = self.__get_hierarchy_root_lst_from_obj_lst(obj_lst)

        container_lst = []
        # For each root, make a hierarchy class
        for root_obj in root_obj_lst:
            hierarchy = AssetHierarchyContainer(root_obj, self.export_settings)
            container_lst.append(hierarchy)

        return container_lst

    def __get_hierarchy_root_lst_from_obj_lst(self, obj_lst):
        """
        Returns a List of hierarchy roots from a selection
        """
        # Get list of hierarchy prefixes
        ah_prefix_lst: List[str] = [
            prefs().env.asset_hierarchy_struct_prefix_static_mesh,
            prefs().env.asset_hierarchy_struct_prefix_static_mesh_kit,
            prefs().env.asset_hierarchy_struct_prefix_skeletal_mesh
        ]

        # Export Root List
        exp_root_lst = []

        # Go through selection to get list of upmost parents. Only add to list if item is not already there
        for obj in obj_lst:

            upmost_parent_obj = objectUtils.get_obj_upmost_parent(obj)

            # Checking if valid root
            if 'EMPTY' in objectUtils.get_obj_type(upmost_parent_obj):  # If Empty, it's a transform
                for ah_prefix in ah_prefix_lst:
                    if objectUtils.get_obj_name(upmost_parent_obj)[:len(ah_prefix)] == ah_prefix:
                        if upmost_parent_obj not in exp_root_lst:
                            exp_root_lst.append(upmost_parent_obj)

        return exp_root_lst

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
        static_mesh_prefix = prefs().env.asset_hierarchy_struct_prefix_static_mesh
        kit_prefix = prefs().env.asset_hierarchy_struct_prefix_static_mesh_kit
        skeletal_mesh_prefix = prefs().env.asset_hierarchy_struct_prefix_skeletal_mesh

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
            f'{ah_tool_name} validation failed.\n\n'
            f'What went wrong:\n'
            f'No Asset Hierarchy was found. Asset Hierarchies must be created '
            f'using a valid prefix defined in the Active Environment Settings.\n\n'
            f'What to do:\n'
            f'Create a new Asset Hierarchy using the Blue Hole Header Menu, or ensure your existing Asset Hierarchy '
            f'uses one of the required prefixes.\n\n'
            f'Valid prefixes: {formatted_prefixes}\n\n'
            f'Export aborted.'
        )

        log(Severity.CRITICAL, ah_tool_name, msg, popup=True)

    def __critical_set_containers_selection_missing(self):
        # Define the prefix variables first
        static_mesh_prefix = prefs().env.asset_hierarchy_struct_prefix_static_mesh
        kit_prefix = prefs().env.asset_hierarchy_struct_prefix_static_mesh_kit
        skeletal_mesh_prefix = prefs().env.asset_hierarchy_struct_prefix_skeletal_mesh

        # Construct the message
        msg = (
            f'{ah_tool_name} validation failed.\n\n'
            f'What went wrong:\n'
            f'No valid Asset Hierarchy was found in the current selection. Asset Hierarchies must exist at the root '
            f'of the scene and use a valid prefix defined in the Active Environment Settings.\n\n'
            f'What to do:\n'
            f'Select at least one Asset Hierarchy at the root of the scene, and ensure its name uses one of the required prefixes.\n\n'
            f'Valid prefixes:\n'
            f'"{static_mesh_prefix}", "{kit_prefix}", "{skeletal_mesh_prefix}"\n\n'
            f'Export aborted.'
        )
        log(Severity.CRITICAL, ah_tool_name, msg, popup=True)


def get_hierarchy_prefix_lst():
    """
    Returns list of hierarchy prefix
    """
    prefix_lst = [prefs().env.asset_hierarchy_struct_prefix_static_mesh,
                  prefs().env.asset_hierarchy_struct_prefix_static_mesh_kit,
                  prefs().env.asset_hierarchy_struct_prefix_skeletal_mesh]
    return prefix_lst
