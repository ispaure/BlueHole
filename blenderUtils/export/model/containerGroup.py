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
import json
from pathlib import Path
from typing import *
from urllib.parse import unquote

import bpy

from ... import filterUtils
from ....unrealUtils import sendUnreal
from ..exportSettings import *
from ....Lib.commonUtils.runtime.diagnostics import *
from ....preferences.prefs import *
from ....Lib.commonUtils.integrations.wrappers.perforce import P4FileGroup, P4FileStatus, P4Info
from ....Lib.commonUtils.integrations.wrappers.perforce.p4_utils import exec_p4_arguments
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
        source_control = prefs().sourcecontrol
        gltfs_with_untracked_buffers: set[Path] = set()
        if (validated_container_lst and not bypass_sc and source_control.source_control_enable
                and source_control.source_control_solution == 'perforce'):
            sc_result, gltfs_with_untracked_buffers = self.__prepare_perforce_export(validated_container_lst)
            if not sc_result:
                if source_control.source_control_error_aborts_exp:
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

                if container.path in gltfs_with_untracked_buffers:
                    try:
                        buffer = self.__exported_buffer(container.path)
                        if buffer is not None:
                            if not exec_p4_arguments(['add', '-t', 'binary', str(buffer)]).success:
                                raise RuntimeError(f'Perforce could not open {buffer.name} for add.')
                            gltfs_with_untracked_buffers.remove(container.path)
                    except (OSError, ValueError, RuntimeError) as error:
                        log(Severity.ERROR, self.CONTAINERS_NAME, f'glTF buffer: {error}')
                        if source_control.source_control_error_aborts_exp:
                            return False

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

    def __prepare_perforce_export(self, containers: list[Container]) -> tuple[bool, set[Path]]:
        paths = dict.fromkeys(container.path for container in containers)
        gltfs = [path for path in paths if path.suffix.lower() == '.gltf']
        gltfs_with_untracked_buffers = set()
        if gltfs:
            # Resolve the configured workspace before querying possible buffers.
            if not P4Info().is_server_accessible():
                return False, set()
            companions = P4FileGroup()
            for path in gltfs:
                companions.append_p4_file_to_group_from_client_file(str(path.with_suffix('.bin')))
            if not companions.update_fields_client_n_depot():
                return False, set()
            for path, file in zip(gltfs, companions.get_p4_file_lst(), strict=True):
                if file.status == P4FileStatus.NOT_ADDED:
                    gltfs_with_untracked_buffers.add(path)
                else:
                    paths[path.with_suffix('.bin')] = None

        batch = P4FileGroup()
        for path in paths:
            batch.append_p4_file_to_group_from_client_file(str(path))
        if not batch.open_for_edit():
            return False, set()
        return True, gltfs_with_untracked_buffers

    @staticmethod
    def __exported_buffer(gltf_path: Path) -> Path | None:
        # Bufferless exports can leave a same-named .bin from an earlier export.
        # Only the manifest identifies the companion for this export.
        buffer = gltf_path.with_suffix('.bin')
        try:
            with gltf_path.open(encoding='utf-8') as stream:
                document = json.load(stream)
            for entry in document.get('buffers', ()):
                if unquote(entry.get('uri', '')) == buffer.name:
                    if buffer.stat().st_size == entry['byteLength'] > 0:
                        return buffer
                    raise ValueError(f'{buffer.name} does not match the exported glTF buffer length.')
        except (AttributeError, TypeError, KeyError) as error:
            raise ValueError(f'Could not read the exported buffers in {gltf_path.name}.') from error
        return None
