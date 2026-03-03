"""
March 2026 refactor: Model Container
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


from abc import ABC, abstractmethod
from pathlib import Path
import bpy
from ..exportSettings import ExportSettings, Engine
from ... import objectUtils, sceneUtils
from ....Lib.commonUtils.debugUtils import *
from ....Lib.commonUtils import fileUtils


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE


class Container(ABC):
    """ Generic Container class """

    CONTAINER_NAME = 'Model'

    def __init__(self, root, export_settings: ExportSettings):
        self.root = root
        self.export_settings: ExportSettings = export_settings
        self.name: str = self.__get_name()
        self.path: Path = self.__get_path()

    def __get_path(self) -> Path:
        exp_dir = self.export_settings.exp_dir
        exp_name_incl_ext = f'{self.name}.{self.export_settings.exp_format.lower()}'
        path = Path(exp_dir, exp_name_incl_ext)
        return path

    def __get_name(self) -> str:
        name = objectUtils.get_obj_name(self.root)

        # Check that the name doesn't have clearly invalid characters
        for char in self.name:
            if char in ['\\', '/', ':']:
                self.__critical_root_illegal_char()

        return name

    def __get_log_name(self) -> str:
        return f'{self.CONTAINER_NAME}: {self.name}'

    def export_proc(self):
        # Set to Object Mode
        sceneUtils.set_object_mode()
        # Unselect everything
        sceneUtils.deselect_all()

        # Rename elements before export (can be customized per-instance)
        self._rename_before_export()

        # Get list of objects (can be customized per-instance)
        obj_lst = self._get_obj_lst()

        # Make invisible objects visible
        made_visible: list[object] = []
        for obj in obj_lst:
            if not obj.visible_get():
                obj.hide_set(False)
                made_visible.append(obj)

        # If Zero Root Transform, Save Root Position and Move to 0,0,0
        if self.export_settings.zero_root_transform:
            root_translation = objectUtils.get_obj_world_translation(self.root)
            objectUtils.set_zero_obj_world_translation(self.root)
        else:
            root_translation = None

        # If Unity, Apply a custom rotation to the root so it lines up the correct way.
        if self.export_settings.engine == Engine.UNITY:
            self.__permanently_apply_unity_rotation_to_root()

        # Select Objects
        objectUtils.select_obj_lst(obj_lst)

        # Set the view layer to the root's
        view_layer = bpy.context.view_layer
        view_layer.objects.active = self.root

        # ---------------------------------------
        # FBX Export on Disk
        self.__export()
        # ---------------------------------------

        # Make invisible objects invisible again
        for obj in made_visible:
            obj.hide_set(True)

        # Set previous root position
        if self.export_settings.zero_root_transform:
            objectUtils.set_obj_world_translation(self.root, root_translation)

        # Deselect all
        sceneUtils.deselect_all()

    @abstractmethod
    def _rename_before_export(self) -> None:
        """Must be implemented by subclasses to define renames before export. """
        pass

    @abstractmethod
    def _get_obj_lst(self):
        """Must be implemented by subclasses to get export selection. """
        pass

    def __permanently_apply_unity_rotation_to_root(self):
        """ If export to Unity, permanently affect the root's rotation. Seems to solve orientation permanently. """
        objectUtils.deselect_all()  # Unsure if needed (selection already empty?), but keeping for now
        objectUtils.select_obj_lst([self.root])
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.transform.rotate(value=-1.57079632679, orient_axis='X', constraint_axis=(True, False, False))
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.transform.rotate(value=1.57079632679, orient_axis='X', constraint_axis=(True, False, False))
        objectUtils.deselect_all()

    def __export(self):
        """ Export the Container (incl. some code to ensure success) """

        # Create Directory if it doesn't exist already
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Force file to be Writable (Yes, even if checkout unsuccessful)
        file_cls = fileUtils.File(self.path)
        file_cls.make_writable()

        # Export scene to FBX
        bpy.ops.export_scene.fbx(filepath=str(self.path),
                                 use_selection=True,
                                 axis_forward=self.export_settings.axis_fwd,
                                 axis_up=self.export_settings.axis_up,
                                 mesh_smooth_type=self.export_settings.mesh_smooth_type,
                                 use_mesh_modifiers=True,
                                 apply_scale_options=self.export_settings.apply_scale_options,
                                 bake_anim=self.export_settings.bake_anim)

    # ----------------------------------------------------------------------------------------------------------------------
    # CRITICAL ERROR MESSAGES

    # --------------------------------
    # CRITICAL: CONTAINER IS NOT VALID
    # --------------------------------

    def __critical_root_illegal_char(self):
        msg = (
            f'{self.CONTAINER_NAME} Container validation failed.\n\n'
            f'What went wrong:\n'
            f'The Asset Hierarchy root "{self.name}" contains illegal characters. '
            f'The following characters are not allowed in Asset Hierarchy names: "\\", "/", ":"\n\n'
            f'These characters are restricted because they can cause issues with file paths, '
            f'export operations, and downstream tools such as game engines or source control systems.\n\n'
            f'What to do:\n'
            f'Rename the Asset Hierarchy root "{self.name}" to remove any illegal characters. '
            f'Use only letters, numbers, underscores, and other safe characters.\n\n'
            f'Export aborted.'
        )

        log(Severity.CRITICAL, self.__get_log_name(), msg, popup=True)
