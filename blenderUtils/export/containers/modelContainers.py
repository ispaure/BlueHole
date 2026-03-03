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
from abc import ABC, abstractmethod

# Blender
import bpy

# Blue Hole
from ... import sourceControlUtils as scUtils
from ..exportSettings import *
from ....Lib.commonUtils.debugUtils import *
from ... import sceneUtils, objectUtils, filterUtils, sendUnreal
from ....preferences.prefs import *
from modelContainer import Container
from ....wrappers import perforceWrapper as p4Wrapper


class Containers(ABC):

    CONTAINERS_NAME = 'Model'

    def __init__(self, export_settings: ExportSettings):
        self.export_settings: ExportSettings = export_settings
        self.container_lst: List[Container] = []

    @abstractmethod
    def set_containers_from_selection(self):
        """Must be implemented by subclasses to define containers from selection. """
        pass

    @abstractmethod
    def set_containers_from_scene(self):
        """Must be implemented by subclasses to define containers from scene. """
        pass

    def export_proc(self, send: bool, skip_sc: bool = False):

        log(Severity.INFO, self.CONTAINERS_NAME, f'Initiating Export of {len(self.container_lst)} Containers...')

        # Do export checks
        if not self._export_checks(send):
            return False

        # Source Control
        if not skip_sc:
            sc_result = self.__export_source_control_proc()
            if not sc_result:
                if prefs().sc.source_control_error_aborts_exp:
                    msg = 'There were errors checking out files, aborting export!'
                    log(Severity.CRITICAL, self.CONTAINERS_NAME, msg)
                else:
                    msg = 'There were errors checking out files, proceeding with export regardless!'
                    log(Severity.WARNING, self.CONTAINERS_NAME, msg)

        # Storing current selection
        view_layer = bpy.context.view_layer
        obj_active = view_layer.objects.active

        # Exporting hierarchies
        for container in self.container_lst:
            container.export_proc()
            if send and self.export_settings.engine == Engine.UNREAL:
                sendUnreal.trigger_unreal_import(str(container.path))

        # Set Previous selection state
        view_layer.objects.active = obj_active

        log(Severity.INFO, self.CONTAINERS_NAME, 'Finished Export of Containers!')

    def _export_checks(self, send: bool):
        """ Basic checks before export (can be overridden by instance) """
        chk_result = filterUtils.check_tests(self.CONTAINERS_NAME,
                                             check_blend_exist=True,
                                             check_blend_loc_in_dir_structure=True)
        return chk_result

    def __export_source_control_proc(self):

        # If Source Control disabled, flag as correctly completed
        if not prefs().sc.source_control_enable:
            return True

        match prefs().sc.source_control_solution:
            case 'perforce':
                p4_file_grp_cls = p4Wrapper.P4FileGroup()
                for container in self.container_lst:
                    p4_file_grp_cls.append_p4_file_to_group_from_client_file(str(container.path))
                return p4_file_grp_cls.open_for_edit()

            case _:
                return True  # For now other solutions don't require manual work.

