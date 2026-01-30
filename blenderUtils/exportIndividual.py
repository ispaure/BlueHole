"""
The January 2026 refactor of exportUtils2, but only section about individual asset exports.
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS

# Blender
import bpy

# Blue Hole
from BlueHole.blenderUtils.exportSettings import *
from BlueHole.blenderUtils.debugUtils import *
import BlueHole.blenderUtils.sceneUtils as sceneUtils
import BlueHole.blenderUtils.objectUtils as oUtils
import BlueHole.blenderUtils.filterUtils as filterUtils
import BlueHole.blenderUtils.objectUtils as objectUtils
from BlueHole.preferences.prefsCls import *

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE

ah_tool_name = 'Asset Individual Exporter (V3)'


class ExportMesh:
    def __init__(self, mesh, export_settings: ExportSettings):
        self.mesh = mesh
        self.export_settings: ExportSettings = export_settings
        self.name = oUtils.get_obj_name(mesh)
        self.path: Optional[Path] = None
        self.__set_path()

    def __set_path(self):
        exp_dir = self.export_settings.exp_dir
        exp_name_incl_ext = f'{self.name}.{self.export_settings.exp_format.lower()}'
        self.path = Path(exp_dir, exp_name_incl_ext)

    def export(self):
        # Check tests
        chk_result = filterUtils.check_tests(ah_tool_name,
                                             check_blend_exist=True,
                                             check_blend_loc_in_dir_structure=True)
        if not chk_result:
            log(Severity.CRITICAL, ah_tool_name, 'Aborting Export')

        # Set to Object Mode
        sceneUtils.set_object_mode()
        # Unselect everything
        sceneUtils.deselect_all()

        # Get list of objects
        obj_lst = [self.mesh]

        # Store visibility of objects
        obj_visib_lst = []
        for obj in obj_lst:
            obj_visib_lst.append([obj, obj.visible_get()])

        # Show invisible objects
        for obj in obj_visib_lst:
            if not obj[1]:
                obj[0].hide_set(False)

        # Save Object Position and Move to 0, 0, 0
        if self.export_settings.zero_root_transform:
            print('is zero root transform')
            obj_world_translation = oUtils.get_obj_world_translation(self.root)
            oUtils.set_zero_obj_world_translation(self.root)
        else:
            print('is not zero root transform')

        # If Preset Is Unity, Fix Transforms of Root Before Export
        if self.export_settings.engine == Engine.UNITY:
            oUtils.deselect_all()
            # For export to Unity, tweak rotation of root.
            objectUtils.select_obj_lst([self.mesh])
            bpy.ops.object.transform_apply(rotation=True)
            bpy.ops.transform.rotate(value=-1.57079632679, orient_axis='X', constraint_axis=(True, False, False))
            bpy.ops.object.transform_apply(rotation=True)
            bpy.ops.transform.rotate(value=1.57079632679, orient_axis='X', constraint_axis=(True, False, False))

        # Select Object
        objectUtils.select_obj_lst(obj_lst)

        # Some Exporters Only Use the Active Object
        view_layer = bpy.context.view_layer
        view_layer.objects.active = self.mesh

        # Create Directory if it doesn't exist already
        self.path.mkdir(parents=True, exist_ok=True)

        # Export scene to FBX
        bpy.ops.export_scene.fbx(filepath=str(self.path),
                                 use_selection=True,
                                 axis_forward=self.export_settings.axis_fwd,
                                 axis_up=self.export_settings.axis_up,
                                 mesh_smooth_type=self.export_settings.mesh_smooth_type,
                                 use_mesh_modifiers=True,
                                 apply_scale_options=self.export_settings.apply_scale_options,
                                 bake_anim=self.export_settings.bake_anim)

        # Reset original visibility. Pick the same objects as before (that were hidden originally, set back to hidden)
        for obj in obj_visib_lst:
            if not obj[1]:
                obj[0].hide_set(True)

        # Set Object Position to Previous
        if self.export_settings.zero_root_transform:
            oUtils.set_obj_world_translation(self.mesh, obj_world_translation)

        sceneUtils.deselect_all()


class ExportMeshes:
    def __init__(self, export_settings: ExportSettings):
        self.export_settings: ExportSettings = export_settings
        self.exp_mesh_lst: List[ExportMesh] = []

    def set_meshes_from_selection(self):
        selection_obj_lst = oUtils.get_selection()

        # Wipe existing list of meshes
        self.exp_mesh_lst = []

        # If no selection, throw error
        if len(selection_obj_lst) == 0:
            self.critical_no_selection()
            return False

        # For each selected mesh, make a ExportMesh class
        for obj in selection_obj_lst:
            export_msh = ExportMesh(obj, self.export_settings)
            self.exp_mesh_lst.append(export_msh)

        return True

    def export(self, skip_sc: bool = False):
        # SOURCE CONTROL
        if not skip_sc:
            sc_file_path_lst: List[Path] = []
            for exp_mesh in self.exp_mesh_lst:
                sc_file_path_lst.append(exp_mesh.path)
            # Attempt to Open Files for Edit
            if not scUtils.sc_open_edit_file_path_lst(sc_file_path_lst):
                msg = 'There were errors checking out files'
                if prefs().sc.source_control_error_aborts_exp:
                    msg += ' - Aborting!'
                    log(Severity.CRITICAL, ah_tool_name, msg)
                    return False
                else:
                    msg += ' - Proceeding regardless!'
                    log(Severity.WARNING, ah_tool_name, msg)

        # PREPARE SELECTION STATE FOR EXPORT
        msg = 'Preparing Selection State for Exports (Unselect All)'
        log(Severity.DEBUG, ah_tool_name, msg)
        view_layer = bpy.context.view_layer
        obj_active = view_layer.objects.active
        # Set to Object Mode
        sceneUtils.set_object_mode()
        # Unselect everything
        sceneUtils.deselect_all()

        # EXPORT
        for exp_mesh in self.exp_mesh_lst:
            exp_mesh.export()

        # SET PREVIOUS SELECTION STATE
        view_layer.objects.active = obj_active

    def critical_no_selection(self):
        # Construct the message
        msg = f'The {ah_tool_name} could not export meshes because the selection was empty. Aborting export!'
        log(Severity.CRITICAL, ah_tool_name, msg, popup=True)


def batch_export_selection(exp_dir, exp_format='FBX'):
    """
    Batch exports selection as one file per object. Will connect to source control if enabled in user preferences.
    :param exp_dir: Export Directory for Export
    :type exp_dir: str
    :param exp_format: File Format for Export
    :type exp_format: str
    """

    tool_name = 'Batch Export Selection to ' + exp_format

    # Check Tests
    chk_result = filterUtils.check_tests(tool_name,
                                         check_blend_exist=True,
                                         check_blend_loc_in_dir_structure=True,
                                         check_selection_not_empty=True)

    # Exit if was false (had error)
    if chk_result is False:
        return False

    # Create ExportSettings Class
    exp_set_cls = ExportSettings(
        # EXPORT OPTIONS
        exp_format=exp_format,
        exp_dir=Path(exp_dir),
        zero_root_transform=prefs().general.exp_select_zero_root_transform,

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

    export_meshes = ExportMeshes(exp_set_cls)
    export_meshes.set_meshes_from_selection()
    export_meshes.export()
