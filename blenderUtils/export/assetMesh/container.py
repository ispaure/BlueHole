"""
March 2026 refactor: Asset Mesh Container.
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

# Blue Hole
from ..exportSettings import *
from ..model.container import Container
from ... import objectUtils

# ----------------------------------------------------------------------------------------------------------------------
# CODE


class AssetMeshContainer(Container):

    CONTAINER_NAME = 'Asset Mesh'

    def __init__(self, mesh, export_settings: ExportSettings):
        super().__init__(mesh, export_settings)

    def _rename_before_export(self):
        pass  # No renames required for AssetMeshContainer

    def _get_obj_lst(self):
        obj_lst = [self.root]

        child_obj_lst = objectUtils.get_obj_child_recursive(self.root)
        if child_obj_lst:
            obj_lst.extend(child_obj_lst)

        return obj_lst
