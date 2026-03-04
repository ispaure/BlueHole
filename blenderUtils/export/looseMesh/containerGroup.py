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
from ..exportSettings import *
from ....Lib.commonUtils.debugUtils import *
from ... import objectUtils, projectUtils
from ....preferences.prefs import *
from .container import LooseMeshContainer
from ..model.containerGroup import ContainerGroup

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE

ah_tool_name = 'Asset Individual Exporter (V3)'


class LooseMeshContainerGroup(ContainerGroup):

    CONTAINERS_NAME = 'Meshes'

    def __init__(self, export_settings: ExportSettings):
        super().__init__(export_settings)

    def set_containers_from_selection(self):
        selection_obj_lst = objectUtils.get_selection()

        # Wipe existing list of meshes
        self.container_lst = []

        # For each selected mesh, make a ExportMesh class
        for obj in selection_obj_lst:
            mesh_container_cls = LooseMeshContainer(obj, self.export_settings)
            self.container_lst.append(mesh_container_cls)

        # If no selection, throw error
        if len(self.container_lst) == 0:
            self.__critical_set_containers_selection_missing()
            return False

        return True

    def set_containers_from_scene(self):
        msg = f'Set Containers from Scene unsupported for {self.CONTAINERS_NAME}.'
        log(Severity.CRITICAL, self.CONTAINERS_NAME, msg)

    # ----------------------------------------------------------------------------------------------------------------------
    # CRITICAL ERROR MESSAGES

    def __critical_set_containers_selection_missing(self):
        # Construct the message
        msg = f'The {ah_tool_name} could not export meshes because the selection was empty. Aborting export!'
        log(Severity.CRITICAL, ah_tool_name, msg, popup=True)


def batch_export_loose_mesh(path_append):
    """
    Exports selected asset files in desired location, relative to open project.
    :param path_append: Specifies directory to export to. Has to be an entry of
                        env_variables.ini under "DirectoryStructure" section.
    :type path_append: str
    """
    # Get path of desired subproject directory to export to
    exp_dir = str(projectUtils.get_project_sub_dir(path_append))

    # Create ExportSettings Class
    exp_set_cls = ExportSettings(
        # EXPORT OPTIONS
        exp_format='FBX',
        exp_dir=Path(exp_dir),
        zero_root_transform=prefs().bridge.exp_select_zero_root_transform,

        # INCLUDED ELEMENTS
        include_render=False,
        include_collision=False,
        include_socket=False,

        # FBX SPECIFIC OPTIONS
        axis_up="Z",
        axis_fwd="-Y",
        mesh_smooth_type="FACE",
        bake_anim=False,
        apply_scale_options="FBX_SCALE_NONE",
        rename_collisions_for_ue=False,  # adjust if needed

        # ENGINE
        engine=Engine.UNDEFINED)

    export_meshes = LooseMeshContainerGroup(exp_set_cls)
    export_meshes.set_containers_from_selection()
    export_meshes.export_proc(send=False)
