"""
Reusable utilities for containers
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

from typing import Optional, Type, List

from ..assetHierarchy.containerGroup import AssetHierarchyContainerGroup
from ..assetCollection.containerGroup import AssetCollectionContainerGroup
from ..assetMesh.containerGroup import AssetMeshContainerGroup
from ....preferences.prefs import *


# ----------------------------------------------------------------------------------------------------------------------
# CODE

def get_container_groups(*, include_hierarchy: bool, include_collection: bool, include_mesh: bool) -> List[Type]:
    """
    Get a List (array) of select container groups that you want (chosen by boolean parameters).
    Note: Will omit ones disabled by the current Blue Hole environment settings.
    """
    groups: List[Type] = []
    if include_hierarchy and prefs().container.enable_asset_hierarchy_container:
        groups.append(AssetHierarchyContainerGroup)
    if include_collection and prefs().container.enable_asset_collection_container:
        groups.append(AssetCollectionContainerGroup)
    if include_mesh and prefs().container.enable_asset_mesh_container:
        groups.append(AssetMeshContainerGroup)
    return groups


def get_container_groups_all():
    """
    Get a List (array) of all container groups enabled by the current Blue Hole environment settings.
    """
    return get_container_groups(include_hierarchy=True, include_collection=True, include_mesh=True)
