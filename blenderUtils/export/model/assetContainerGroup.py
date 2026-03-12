"""
March 2026 refactor of exportUtils2 for individual asset exports.
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

from abc import abstractmethod

from ..exportSettings import *
from ....Lib.commonUtils.debugUtils import *
from ....preferences.prefs import *
from ... import filterUtils, objectUtils, sceneUtils
from .containerGroup import ContainerGroup

# ----------------------------------------------------------------------------------------------------------------------
# CODE


class AssetContainerGroup(ContainerGroup):

    CONTAINERS_NAME = 'Asset'
    CONTAINER_CLASS = None

    def __init__(self, export_settings: ExportSettings):
        super().__init__(export_settings)

    def set_containers_from_selection(self, silent_if_empty: bool):
        # Get list of selected objects
        obj_lst = objectUtils.get_selection()

        # Set containers from object list
        self._set_containers_from_obj_lst(obj_lst)

        # Throw error if no containers were found
        if not silent_if_empty and len(self.container_lst) == 0:
            self.__critical_set_containers_selection_missing()

    def set_containers_from_scene(self, silent_if_empty: bool):
        # Get list of scene objects
        obj_lst = sceneUtils.get_scene_obj_lst()

        # Set containers from object list
        self._set_containers_from_obj_lst(obj_lst)

        # Throw error if no containers were found
        if not silent_if_empty and len(self.container_lst) == 0:
            self.__critical_set_containers_scene_missing()

    def _set_containers_from_obj_lst(self, obj_lst):
        """
        Build the container list from the provided object list.
        """
        self.container_lst = []

        root_obj_lst = self._get_root_lst_from_obj_lst(obj_lst)

        for root_obj in root_obj_lst:
            hierarchy = self.CONTAINER_CLASS(root_obj, self.export_settings)
            self.container_lst.append(hierarchy)

    @abstractmethod
    def _get_root_lst_from_obj_lst(self, obj_lst):
        """
        Must be implemented by subclasses to define containers from an object list.
        """
        pass

    def _export_checks(self, send: bool):
        """
        Run export validation checks based on engine and send mode.
        """
        validate_source_content = self.export_settings.engine == Engine.UNREAL and send
        check_source_content_root_path_exist = validate_source_content
        check_blend_in_source_content = validate_source_content

        check_unity_assets_path_exist = self.export_settings.engine == Engine.UNITY and send

        chk_result = filterUtils.check_tests(
            self.CONTAINERS_NAME,
            check_blend_exist=True,
            check_blend_loc_in_dir_structure=True,
            check_source_content_root_path_exist=check_source_content_root_path_exist,
            check_blend_in_source_content=check_blend_in_source_content,
            check_unity_assets_path_exist=check_unity_assets_path_exist,
        )
        return chk_result

    # ------------------------------------------------------------------------------------------------------------------
    # CRITICAL ERROR MESSAGES

    def __critical_set_containers_scene_missing(self):
        static_mesh_prefix = prefs().container.asset_hierarchy_struct_prefix_static_mesh
        kit_prefix = prefs().container.asset_hierarchy_struct_prefix_static_mesh_kit
        skeletal_mesh_prefix = prefs().container.asset_hierarchy_struct_prefix_skeletal_mesh

        prefixes = [
            static_mesh_prefix,
            kit_prefix,
            skeletal_mesh_prefix,
        ]

        unique_prefixes = list(dict.fromkeys(p for p in prefixes if p))
        formatted_prefixes = ", ".join(f'"{p}"' for p in unique_prefixes)

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
        static_mesh_prefix = prefs().container.asset_hierarchy_struct_prefix_static_mesh
        kit_prefix = prefs().container.asset_hierarchy_struct_prefix_static_mesh_kit
        skeletal_mesh_prefix = prefs().container.asset_hierarchy_struct_prefix_skeletal_mesh

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
    Return the list of valid Asset Hierarchy prefixes.
    """
    prefix_lst = [
        prefs().container.asset_hierarchy_struct_prefix_static_mesh,
        prefs().container.asset_hierarchy_struct_prefix_static_mesh_kit,
        prefs().container.asset_hierarchy_struct_prefix_skeletal_mesh,
    ]
    return prefix_lst
