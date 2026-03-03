"""
March 2026 refactor: Mesh Container
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

# Blue Hole
from ..exportSettings import *
from .modelContainer import Container

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE


class MeshContainer(Container):
    def __init__(self, mesh, export_settings: ExportSettings):
        super().__init__(mesh, export_settings)

    def _rename_before_export(self):
        pass  # No renames required for MeshContainer

    def _get_obj_lst(self):
        return [self.root]  # MeshContainer only has one object to export
