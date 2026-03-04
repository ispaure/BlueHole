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
from ..exportSettings import *
from ... import objectUtils
from ....preferences.prefs import *
from .container import AssetHierarchyContainer
from ..model.assetContainerGroup import AssetContainerGroup

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE

ah_tool_name = 'Asset Hierarchy Exporter (V3)'


class AssetHierarchyContainerGroup(AssetContainerGroup):

    CONTAINERS_NAME = 'Asset Hierarchy'
    CONTAINER_CLASS = AssetHierarchyContainer

    def __init__(self, export_settings: ExportSettings):
        super().__init__(export_settings)

    def _get_root_lst_from_obj_lst(self, obj_lst):
        """
        Returns a List of hierarchy roots from a selection
        """
        # Get list of hierarchy prefixes
        ah_prefix_lst: List[str] = [
            prefs().container.asset_hierarchy_struct_prefix_static_mesh,
            prefs().container.asset_hierarchy_struct_prefix_static_mesh_kit,
            prefs().container.asset_hierarchy_struct_prefix_skeletal_mesh
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
