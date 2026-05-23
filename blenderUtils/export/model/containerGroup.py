"""
March 2026 refactor of exportUtils2.

Once fully validated, the old implementation should be removed and this one used instead.
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

from abc import ABC, abstractmethod
from typing import *

import bpy

from ... import filterUtils
from ....unrealUtils import sendUnreal
from ..exportSettings import *
from ....Lib.commonUtils.debugUtils import *
from ....preferences.prefs import *
from ....wrappers.perforce.p4_file_group import P4FileGroup
from .container import Container

# ----------------------------------------------------------------------------------------------------------------------
# CODE


class ContainerGroup(ABC):

    CONTAINERS_NAME = 'Model'

    def __init__(self, export_settings: ExportSettings):
        self.export_settings: ExportSettings = export_settings
        self.container_lst: List[Container] = []

    @abstractmethod
    def set_containers_from_selection(self, silent_if_empty: bool):
        """
        Must be implemented by subclasses to define containers from selection.
        """
        pass

    @abstractmethod
    def set_containers_from_scene(self, silent_if_empty: bool):
        """
        Must be implemented by subclasses to define containers from scene.
        """
        pass

    def export_proc(self, *, send: bool, bypass_sc: bool = False):
        log(Severity.INFO, self.CONTAINERS_NAME, f'Initiating Export of {len(self.container_lst)} Containers...')

        # Do export checks
        if not self._export_checks(send):
            return False

        # Source Control
        if not bypass_sc:
            sc_result = self.__export_source_control_proc()
            if not sc_result:
                if prefs().sourcecontrol.source_control_error_aborts_exp:
                    msg = 'There were errors checking out files, aborting export!'
                    log(Severity.CRITICAL, self.CONTAINERS_NAME, msg)
                else:
                    msg = 'There were errors checking out files, proceeding with export regardless!'
                    log(Severity.WARNING, self.CONTAINERS_NAME, msg)

        # Store current selection state
        view_layer = bpy.context.view_layer
        obj_active = view_layer.objects.active

        # Export containers
        for container in self.container_lst:
            success: bool = container.export_proc()
            if not success:
                continue

            if send and self.export_settings.engine == Engine.UNREAL:

                # Override Send operator (per-container)
                if prefs().bridge.ue_enable_send_override and prefs().bridge.ue_op_send_override:
                    log(
                        Severity.WARNING,
                        self.CONTAINERS_NAME,
                        f'Send to Unreal override from operator: "{prefs().bridge.ue_op_send_override}"',
                    )
                    op_idname = prefs().bridge.ue_op_send_override.strip()

                    # Expect "category.op_name" (example: "wm.my_send_unreal")
                    if "." not in op_idname:
                        log(Severity.CRITICAL, self.__class__.__name__, f'Invalid operator idname: "{op_idname}"')
                        raise ValueError(f'Invalid operator idname: "{op_idname}"')

                    cat, op = op_idname.split(".", 1)

                    # Call operator and pass FBX file path
                    try:
                        res = getattr(getattr(bpy.ops, cat), op)(path=str(container.path))
                    except Exception as e:
                        log(
                            Severity.CRITICAL,
                            self.__class__.__name__,
                            f'Failed to run override operator "{op_idname}": {e}',
                        )
                        raise

                    # Optional: treat operator cancellation as a hard stop
                    if res == {'CANCELLED'}:
                        return {'CANCELLED'}

                else:
                    # Default behavior
                    sendUnreal.trigger_unreal_import(str(container.path))

        # Restore previous selection state
        view_layer.objects.active = obj_active

        log(Severity.INFO, self.CONTAINERS_NAME, 'Finished Export of Containers!')

    def _export_checks(self, send: bool):
        """
        Basic checks before export. Can be overridden by subclasses.
        """
        chk_result = filterUtils.check_tests(
            self.CONTAINERS_NAME,
            check_blend_exist=True,
            check_blend_loc_in_dir_structure=True,
        )
        return chk_result

    def __export_source_control_proc(self):
        """
        Handle source control steps required before export.
        """
        if not prefs().sourcecontrol.source_control_enable:
            return True

        match prefs().sourcecontrol.source_control_solution:
            case 'perforce':
                p4_file_grp_cls = P4FileGroup()
                for container in self.container_lst:
                    p4_file_grp_cls.append_p4_file_to_group_from_client_file(str(container.path))
                return p4_file_grp_cls.open_for_edit()

            case _:
                return True  # For now other solutions do not require manual work.
