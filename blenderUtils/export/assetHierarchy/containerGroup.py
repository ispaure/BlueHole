"""
March 2026 refactor of exportUtils2 for Asset Hierarchy exports.
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
from typing import *

# Blue Hole
from ..exportSettings import *
from ... import objectUtils
from ....preferences.prefs import *
from .container import AssetHierarchyContainer
from ..model.assetContainerGroup import AssetContainerGroup

# ----------------------------------------------------------------------------------------------------------------------
# CODE

ah_tool_name = 'Asset Hierarchy Exporter (V3)'


class AssetHierarchyContainerGroup(AssetContainerGroup):

    CONTAINERS_NAME = 'Asset Hierarchies'
    CONTAINER_CLASS = AssetHierarchyContainer

    def __init__(self, export_settings: ExportSettings):
        super().__init__(export_settings)

    def _get_root_lst_from_obj_lst(self, obj_lst):
        """
        Return a list of valid Asset Hierarchy roots from an object list.
        """
        ah_prefix_lst: List[str] = [
            prefs().container.asset_hierarchy_struct_prefix_static_mesh,
            prefs().container.asset_hierarchy_struct_prefix_static_mesh_kit,
            prefs().container.asset_hierarchy_struct_prefix_skeletal_mesh,
        ]

        exp_root_lst = []

        # Go through objects to get the list of upmost parents.
        # Only add an item if it is not already present and uses a valid prefix.
        for obj in obj_lst:
            upmost_parent_obj = objectUtils.get_obj_upmost_parent(obj)

            # Check whether the root is a valid hierarchy root.
            if 'EMPTY' in objectUtils.get_obj_type(upmost_parent_obj):
                for ah_prefix in ah_prefix_lst:
                    if objectUtils.get_obj_name(upmost_parent_obj)[:len(ah_prefix)] == ah_prefix:
                        if upmost_parent_obj not in exp_root_lst:
                            exp_root_lst.append(upmost_parent_obj)

        return exp_root_lst
