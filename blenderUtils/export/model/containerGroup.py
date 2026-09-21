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

        # Pre-validate all containers before any source-control operation.
        validated_container_lst: List[Container] = []
        for container in self.container_lst:
            if not self.__run_pre_export_override(container):
                continue

            validated_container_lst.append(container)

        # Source Control
        if validated_container_lst and not bypass_sc:
            sc_result = self.__export_source_control_proc(validated_container_lst)
            if not sc_result:
                if prefs().sourcecontrol.source_control_error_aborts_exp:
                    msg = 'There were errors checking out file(s), aborting export!'
                    log(Severity.ERROR, self.CONTAINERS_NAME, msg)
                    return False
                else:
                    msg = 'There were errors checking out file(s), proceeding with export regardless!'
                    log(Severity.WARNING, self.CONTAINERS_NAME, msg)

        # Store current active object.
        view_layer = bpy.context.view_layer
        obj_active = view_layer.objects.active

        try:
            # Export containers that passed pre-validation
            for container in validated_container_lst:
                success: bool = container.export_proc()
                if not success:
                    continue

                # Post-export validation hook.
                if not self.__run_post_export_override(container):
                    continue

                if send and self.export_settings.engine == Engine.UNREAL:
                    result = sendUnreal.trigger_unreal_import(str(container.path))

                    if not result:
                        return False

        finally:
            # Always restore previous active object, even if export/send fails or returns early.
            view_layer.objects.active = obj_active

        log(Severity.INFO, self.CONTAINERS_NAME, 'Finished Export of Containers!')
        return True

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

    def __run_pre_export_override(self, container: Container) -> bool:
        """
        Run the configured pre-export operator for a container.

        The operator must expose the following Blender StringProperty arguments:
            root_name: Blender object name of the container root.
            path: Expected export path as a string.
        """
        if not prefs().bridge.enable_pre_export_override:
            return True

        operator_idname = prefs().bridge.op_pre_export_override.strip()
        if not operator_idname:
            log(
                Severity.CRITICAL,
                self.CONTAINERS_NAME,
                'Pre-export validation override is enabled, but no operator IDName is configured.'
            )
            return False

        return self.__run_export_validation_override(
            operator_idname=operator_idname,
            container=container,
            hook_name='Pre-Export Validation',
        )

    def __run_post_export_override(self, container: Container) -> bool:
        """
        Run the configured post-export operator for a container.

        The operator must expose the following Blender StringProperty arguments:
            root_name: Blender object name of the container root.
            path: Export path as a string.
        """
        if not prefs().bridge.enable_post_export_override:
            return True

        operator_idname = prefs().bridge.op_post_export_override.strip()
        if not operator_idname:
            log(
                Severity.CRITICAL,
                self.CONTAINERS_NAME,
                'Post-export validation override is enabled, but no operator IDName is configured.'
            )
            return False

        return self.__run_export_validation_override(
            operator_idname=operator_idname,
            container=container,
            hook_name='Post-Export Validation',
        )

    def __run_export_validation_override(
            self,
            *,
            operator_idname: str,
            container: Container,
            hook_name: str,
    ) -> bool:
        """
        Execute a configured Blender operator used as an export validation hook.

        Configuration/interface errors are treated as critical Blue Hole integration errors.
        An operator that executes correctly but returns anything other than FINISHED is treated
        as a normal validation failure/cancellation for that container.
        """
        try:
            operator_category, operator_name = operator_idname.split('.', 1)
            operator = getattr(getattr(bpy.ops, operator_category), operator_name)

            self.__validate_operator_string_properties(
                operator=operator,
                operator_idname=operator_idname,
                hook_name=hook_name,
                required_properties=('root_name', 'path'),
            )

            result = operator(
                root_name=container.root.name,
                path=str(container.path),
            )

        except (AttributeError, ValueError, TypeError, RuntimeError) as exc:
            msg = (
                f'{hook_name} operator "{operator_idname}" is invalid or could not be executed.\n\n'
                f'Container: {container.name}\n'
                f'Root Object: {container.root.name}\n'
                f'Export Path: {container.path}\n\n'
                f'Expected operator interface:\n'
                f'  root_name: StringProperty\n'
                f'  path: StringProperty\n\n'
                f'Error: {exc}'
            )
            log(Severity.CRITICAL, self.CONTAINERS_NAME, msg, popup=True)
            return False

        if 'FINISHED' not in result:
            msg = (
                f'{hook_name} failed or was cancelled.\n\n'
                f'Container: {container.name}\n'
                f'Root Object: {container.root.name}\n'
                f'Export Path: {container.path}'
            )
            log(Severity.WARNING, self.CONTAINERS_NAME, msg)
            return False

        return True

    @staticmethod
    def __validate_operator_string_properties(
            *,
            operator,
            operator_idname: str,
            hook_name: str,
            required_properties: tuple[str, ...],
    ) -> None:
        """
        Validate that a Blender operator exposes the required StringProperty arguments.

        Raises:
            RuntimeError:
                If an expected property is missing or is not a Blender STRING property.
        """
        rna_type = operator.get_rna_type()
        operator_properties = {
            prop.identifier: prop
            for prop in rna_type.properties
        }

        for property_name in required_properties:
            prop = operator_properties.get(property_name)

            if prop is None:
                raise RuntimeError(
                    f'{hook_name} operator "{operator_idname}" is missing required '
                    f'StringProperty "{property_name}".'
                )

            if prop.type != 'STRING':
                raise RuntimeError(
                    f'{hook_name} operator "{operator_idname}" property "{property_name}" '
                    f'must be a StringProperty, but its Blender RNA type is "{prop.type}".'
                )

    def __export_source_control_proc(self, container_lst: List[Container]):
        """
        Handle source control steps required before export for the provided containers.
        """
        if not prefs().sourcecontrol.source_control_enable:
            return True

        match prefs().sourcecontrol.source_control_solution:
            case 'perforce':
                p4_file_grp_cls = P4FileGroup()
                for container in container_lst:
                    p4_file_grp_cls.append_p4_file_to_group_from_client_file(str(container.path))
                return p4_file_grp_cls.open_for_edit()

            case _:
                return True  # For now other solutions do not require manual work.
