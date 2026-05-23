"""
March 2026 refactor: Model Container.
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
from pathlib import Path

import bpy

from ..exportSettings import Engine, ExportSettings
from ... import objectUtils, sceneUtils
from ....Lib.commonUtils import fileUtils
from ....Lib.commonUtils.debugUtils import *

# ----------------------------------------------------------------------------------------------------------------------
# CODE


class Container(ABC):
    """
    Generic Container class.
    """

    CONTAINER_NAME = 'Model'

    def __init__(self, root, export_settings: ExportSettings):
        self.root = root
        self.export_settings: ExportSettings = export_settings
        self.name: str = self.__get_name()
        self.path: Path = self.__get_path()

    def __get_path(self) -> Path:
        exp_dir = self.export_settings.exp_dir
        exp_name_incl_ext = f'{self.name}.{self.export_settings.exp_format.lower()}'
        return Path(exp_dir, exp_name_incl_ext)

    def __get_name(self) -> str:
        name = objectUtils.get_obj_name(self.root)

        # Check that the name does not contain clearly invalid characters.
        for char in name:
            if char in ['\\', '/', ':']:
                self.__critical_root_illegal_char(name)

        return name

    def _get_log_name(self) -> str:
        return f'{self.CONTAINER_NAME}: {self.name}'

    def export_proc(self):
        """
        Run the export procedure for this container.
        """
        made_visible: list[object] = []
        root_translation = None
        success = False
        try:
            sceneUtils.set_object_mode()
            sceneUtils.deselect_all()

            # Rename elements before export (can be customized per instance).
            self._rename_before_export()

            # Get list of objects to export (can be customized per instance).
            obj_lst = self._get_obj_lst()

            # Validate before any visibility/transform/export mutation.
            objectUtils.validate_obj_lst_in_view_layer(obj_lst)

            # Make invisible objects visible.
            made_visible = []
            for obj in obj_lst:
                if not obj.visible_get():
                    obj.hide_set(False)
                    made_visible.append(obj)

            # If zero root transform is enabled, store root position and move to origin.
            if self.export_settings.zero_root_transform:
                root_translation = objectUtils.get_obj_world_translation(self.root)
                objectUtils.set_zero_obj_world_translation(self.root)

            # If exporting to Unity, apply a custom rotation to the root.
            if self.export_settings.engine == Engine.UNITY:
                self.__permanently_apply_unity_rotation_to_root()

            objectUtils.select_obj_lst(obj_lst)

            view_layer = bpy.context.view_layer
            view_layer.objects.active = self.root

            self.__export()

            success = True

        except RuntimeError:
            msg = (
                f'{self.CONTAINER_NAME} export cancelled.\n\n'
                f'Container: {self.name}\n\n'
                f'The export was aborted because one or more objects could not be selected.\n'
                f'See previous error message for detailed diagnostics.'
            )

            log(Severity.ERROR, self._get_log_name(), msg, popup=True)

        finally:
            # Restore visibility.
            for obj in made_visible:
                obj.hide_set(True)

            # Restore previous root position.
            if root_translation is not None:
                objectUtils.set_obj_world_translation(self.root, root_translation)

            sceneUtils.deselect_all()

        return success

    @abstractmethod
    def _rename_before_export(self) -> None:
        """
        Must be implemented by subclasses to define renames before export.
        """
        pass

    @abstractmethod
    def _get_obj_lst(self):
        """
        Must be implemented by subclasses to get the export selection.
        """
        pass

    def __permanently_apply_unity_rotation_to_root(self):
        """
        If exporting to Unity, permanently affect the root rotation.

        This seems to solve orientation correctly in a lasting way.
        """
        objectUtils.deselect_all()  # Unsure if needed, but keeping for now
        objectUtils.select_obj_lst([self.root])
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.transform.rotate(value=-1.57079632679, orient_axis='X', constraint_axis=(True, False, False))
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.transform.rotate(value=1.57079632679, orient_axis='X', constraint_axis=(True, False, False))
        objectUtils.deselect_all()

    def __export(self):
        """
        Export the container and ensure the target directory and file state are valid first.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Force file to be writable, even if checkout was unsuccessful.
        file_cls = fileUtils.File(self.path)
        file_cls.make_writable()

        if self.export_settings.exp_format == 'FBX':
            msg = f'Exporting ".{self.export_settings.exp_format}" file to "{self.path}"...'
            log(Severity.INFO, 'Blue Hole Export', msg)
            bpy.ops.export_scene.fbx(
                filepath=str(self.path),
                use_selection=True,
                axis_forward=self.export_settings.axis_fwd,
                axis_up=self.export_settings.axis_up,
                mesh_smooth_type=self.export_settings.mesh_smooth_type,
                use_mesh_modifiers=True,
                apply_scale_options=self.export_settings.apply_scale_options,
                bake_anim=self.export_settings.bake_anim,
            )
        elif self.export_settings.exp_format in ['GLTF', 'GLB']:
            msg = f'Exporting ".{self.export_settings.exp_format}" file to "{self.path}"...'
            log(Severity.INFO, 'Blue Hole Export', msg)
            bpy.ops.export_scene.gltf(
                filepath=str(self.path),
                use_selection=True,
                export_animations=self.export_settings.bake_anim,
                export_format='GLTF_SEPARATE' if self.export_settings.exp_format == 'GLTF' else 'GLB'  # Embed all in one file
            )
        else:
            msg = f'Export Format of "{self.export_settings.exp_format}" is not implemented in Blue Hole!'
            log(Severity.CRITICAL, 'Container Export', msg)

    # ------------------------------------------------------------------------------------------------------------------
    # CRITICAL ERROR MESSAGES

    def __critical_root_illegal_char(self, name):
        msg = (
            f'{self.CONTAINER_NAME} Container validation failed.\n\n'
            f'What went wrong:\n'
            f'The Asset Hierarchy root "{name}" contains illegal characters. '
            f'The following characters are not allowed in Asset Hierarchy names: "\\", "/", ":"\n\n'
            f'These characters are restricted because they can cause issues with file paths, '
            f'export operations, and downstream tools such as game engines or source control systems.\n\n'
            f'What to do:\n'
            f'Rename the Asset Hierarchy root "{name}" to remove any illegal characters. '
            f'Use only letters, numbers, underscores, and other safe characters.\n\n'
            f'Export aborted.'
        )

        log(Severity.CRITICAL, f'{self.CONTAINER_NAME}: {name}', msg, popup=True)
