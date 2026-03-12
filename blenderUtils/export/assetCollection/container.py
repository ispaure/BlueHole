"""
March 2026 refactor: Asset Collection Container.
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

# ----------------------------------------------------------------------------------------------------------------------
# CODE


class AssetCollectionContainer(Container):

    CONTAINER_NAME = 'Asset Collection'

    def __init__(self, mesh, export_settings: ExportSettings):
        super().__init__(mesh, export_settings)

    def _rename_before_export(self):
        pass  # No renames required for AssetCollectionContainer

    def _get_obj_lst(self):
        return [self.root]  # AssetCollectionContainer only exports one object
