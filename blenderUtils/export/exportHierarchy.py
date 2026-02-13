"""
The January 2026 refactor of exportUtils2. Once done, the old one should be removed and this one used instead.
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

# System
from typing import *

# Blender
import bpy

# Blue Hole
from .. import sourceControlUtils as scUtils
from .exportSettings import *
from ..debugUtils import *
from .. import sceneUtils, objectUtils, filterUtils, sendUnreal
from ...preferences.prefs import *

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE

ah_tool_name = 'Asset Hierarchy Exporter (V3)'


class AssetHierarchy:
    def __init__(self, root, export_settings: ExportSettings):
        self.root = root
        self.export_settings: ExportSettings = export_settings
        self.name = objectUtils.get_obj_name(root)
        self.path: Optional[Path] = None
        self.render = None
        self.collision = None
        self.socket = None
        self.__set_fields()

    def __set_fields(self):
        exp_dir = self.export_settings.exp_dir
        exp_name_incl_ext = f'{self.name}.{self.export_settings.exp_format.lower()}'
        self.path = Path(exp_dir, exp_name_incl_ext)

        # Check that there is only empty-type objects under the root (If Empty Object Render is enabled)
        if self.export_settings.include_render:
            child_obj_tuple = objectUtils.get_obj_child(self.root)
            for child_obj in child_obj_tuple:
                if 'EMPTY' not in objectUtils.get_obj_type(child_obj):
                    self.critical_rogue_object_directly_under_root(self.root, child_obj)

        if self.export_settings.include_render:
            component_name = prefs().env.asset_hierarchy_empty_object_meshes
            component_type = 'Render'
            self.render = self.__get_required_empty_obj(component_name, component_type)

        if self.export_settings.include_collision:
            component_name = prefs().env.asset_hierarchy_empty_object_collisions
            component_type = 'Collision'
            self.collision = self.__get_required_empty_obj(component_name, component_type)

        if self.export_settings.include_socket:
            component_name = prefs().env.asset_hierarchy_empty_object_sockets
            component_type = 'Socket'
            self.socket = self.__get_required_empty_obj(component_name, component_type)

    def __get_required_empty_obj(self, component_name: str, component_type: str):
        child_obj_tuple = objectUtils.get_obj_child(self.root)
        match_obj = None
        for child_obj in child_obj_tuple:
            child_name = objectUtils.get_obj_name(child_obj).split('.')[0]
            if child_name == component_name:
                if match_obj is None:
                    match_obj = child_obj
                else:
                    self.critical_component_duplicated(component_name, component_type)

        if match_obj is None:  # Validate there is not 0 match
            self.critical_component_missing(component_name, component_type)

        return match_obj

    def export(self, send: bool):
        """
        """
        # Check tests
        chk_result = filterUtils.check_tests(ah_tool_name,
                                             check_blend_exist=True,
                                             check_blend_loc_in_dir_structure=True,
                                             check_source_content_root_path_exist=send,
                                             check_blend_in_source_content=send,
                                             check_unity_assets_path_exist=self.export_settings.engine == Engine.UNITY)
        if not chk_result:
            log(Severity.CRITICAL, ah_tool_name, 'Aborting Export')

        # Set to Object Mode
        sceneUtils.set_object_mode()
        # Unselect everything
        sceneUtils.deselect_all()

        # Rename Render, Collision, Socket objects
        if self.render is not None:
            # Have to do three times for this to work... IDK Why. But it works?
            self.render.name = prefs().env.asset_hierarchy_empty_object_meshes
            self.render.name = prefs().env.asset_hierarchy_empty_object_meshes
            self.render.name = prefs().env.asset_hierarchy_empty_object_meshes
        if self.collision is not None:
            # Have to do three times for this to work... IDK Why. But it works?
            self.collision.name = prefs().env.asset_hierarchy_empty_object_collisions
            self.collision.name = prefs().env.asset_hierarchy_empty_object_collisions
            self.collision.name = prefs().env.asset_hierarchy_empty_object_collisions
        if self.socket is not None:
            # Have to do three times for this to work... IDK Why. But it works?
            self.socket.name = prefs().env.asset_hierarchy_empty_object_sockets
            self.socket.name = prefs().env.asset_hierarchy_empty_object_sockets
            self.socket.name = prefs().env.asset_hierarchy_empty_object_sockets

        # Rename collisions
        if self.export_settings.rename_collisions_for_ue:
            self.rename_collisions()

        # Get list of objects
        obj_lst = self.get_obj_lst()

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
            obj_world_translation = objectUtils.get_obj_world_translation(self.root)
            objectUtils.set_zero_obj_world_translation(self.root)
        else:
            print('is not zero root transform')

        # If Preset Is Unity, Fix Transforms of Root Before Export
        if self.export_settings.engine == Engine.UNITY:
            objectUtils.deselect_all()
            # For export to Unity, tweak rotation of root.
            objectUtils.select_obj_lst([self.root])
            bpy.ops.object.transform_apply(rotation=True)
            bpy.ops.transform.rotate(value=-1.57079632679, orient_axis='X', constraint_axis=(True, False, False))
            bpy.ops.object.transform_apply(rotation=True)
            bpy.ops.transform.rotate(value=1.57079632679, orient_axis='X', constraint_axis=(True, False, False))

        # Select Object
        objectUtils.select_obj_lst(obj_lst)

        # Some Exporters Only Use the Active Object
        view_layer = bpy.context.view_layer
        view_layer.objects.active = self.root

        # Create Directory if it doesn't exist already
        self.path.parent.mkdir(parents=True, exist_ok=True)

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
            objectUtils.set_obj_world_translation(self.root, obj_world_translation)

        sceneUtils.deselect_all()

        # SEND TO UNREAL (IF APPLICABLE)
        if send and self.export_settings.engine == Engine.UNREAL:
            result = sendUnreal.trigger_unreal_import(str(self.path))
            if not result:
                return False
        return True

    def get_obj_lst(self):

        # Wipe existing object list
        obj_lst = []
        # Create exclusion list
        excl_lst = []

        # Add root
        obj_lst.append(self.root)

        # Append other stuff
        for component in [self.render, self.collision, self.socket]:
            if component is not None:
                child_obj_lst = objectUtils.get_obj_child_recursive(component)
                if len(child_obj_lst) > 0 or not prefs().env.exclude_element_if_no_child:
                    obj_lst.append(component)
                    for child_obj in child_obj_lst:
                        obj_lst.append(child_obj)
                else:
                    excl_lst.append(component)

        # If render wasn't included, add stuff at the root (but not the excluded components if applicable)
        if not self.export_settings.include_render:
            obj_full_lst = objectUtils.get_obj_child_recursive(self.root)
            for obj in obj_full_lst:
                if obj not in obj_lst and obj not in excl_lst:
                    obj_lst.append(obj)

        return obj_lst

    def rename_collisions(self):
        """ Rename meshes under the collision component, to match Unreal's collision naming. """
        if self.collision is None:
            return

        coll_obj_lst = objectUtils.get_obj_child_recursive(self.collision)
        first_mesh_name = self.get_first_mesh_name()
        counter = 1
        for coll_obj in coll_obj_lst:
            coll_obj.name = f'UCX_{first_mesh_name}_{format(counter, "03")}'
            counter += 1

    def get_first_mesh_name(self) -> str:
        """ Get first mesh name, else sets to 'Template' as fallback. """
        if self.export_settings.include_render:
            render_obj_child_lst = objectUtils.get_obj_child_recursive(self.render)
            for render_obj in render_obj_child_lst:
                if objectUtils.get_obj_type(render_obj) == 'MESH':
                    return objectUtils.get_obj_name(render_obj)
        else:
            root_obj_lst = objectUtils.get_obj_child(self.root)
            for root_obj in root_obj_lst:
                if objectUtils.get_obj_type(root_obj) == 'MESH':
                    return objectUtils.get_obj_name(root_obj)
        return 'Template'

    def critical_rogue_object_directly_under_root(self, root, child):
        exp_root_name = objectUtils.get_obj_name(root)
        child_name = objectUtils.get_obj_name(child)
        msg = (f'The object named {child_name} under the Asset Hierarchy "{exp_root_name}" '
               f'is not of type Empty Object. Please move it within one of the Asset Hierarchy\'s '
               f'required Export Element(s) -- or at least within an Empty Object.\n\n'
               f'Aborting export!')
        log(Severity.CRITICAL, ah_tool_name, msg, popup=True)

    def critical_component_missing(self, component_name, component_type):
        msg = (f'As specified in the Active Environment\'s settings, the Asset Hierarchy Exporter is missing '
               f'a required Export Element ({component_type}) under "{self.name}", which must be named "{component_name}" '
               f'(name can have trailing numbers at the end, such as .013).\n\n'
               f'There are a few solutions:'
               f'\n- Create the required Empty Object (as requested)'
               f'\n- Edit Your Active Environment\'s settings to not require the Export Element of type {component_type} (Bridges Tab)'
               f'\n- The simplest solution is to create a new Asset Hierarchy from scratch using the tool in the Blue Hole Header Menu.\n\n'
               f'Aborting export!')
        log(Severity.CRITICAL, ah_tool_name, msg, popup=True)

    def critical_component_duplicated(self, component_name, component_type):
        msg = (f'The required Export Element named {component_name} under the Asset Hierarchy "{self.name}" of type: {component_type} '
               f'is found more than once. This can happen because of the trailing numbers Blender creates (.001, .002). '
               f'Please fix this issue.\n\n'
               f'Aborting export!')
        log(Severity.CRITICAL, ah_tool_name, msg, popup=True)


class AssetHierarchies:
    def __init__(self, export_settings: ExportSettings):
        self.export_settings: ExportSettings = export_settings
        self.hierarchies: List[AssetHierarchy] = []

    def set_hierarchies_from_selection(self):
        selection_obj_lst = objectUtils.get_selection()
        root_obj_lst = self.get_hierarchy_root_from_obj_lst(selection_obj_lst)
        self.__set_hierarchies_from_root_obj_lst(root_obj_lst)

    def set_hierarchies_from_scene(self):
        scene_obj_lst = sceneUtils.get_scene_obj_lst()
        root_obj_lst = self.get_hierarchy_root_from_obj_lst(scene_obj_lst)
        self.__set_hierarchies_from_root_obj_lst(root_obj_lst)

    def __set_hierarchies_from_root_obj_lst(self, root_obj_lst) -> bool:
        """ Set the hierarchies from a list of root objects. """

        # Wipe existing list of hierarchies
        self.hierarchies = []

        # If no root, throw error
        if len(root_obj_lst) == 0:
            self.critical_no_hierarchy()
            return False

        # For each root, make a hierarchy class
        for root_obj in root_obj_lst:
            hierarchy = AssetHierarchy(root_obj, self.export_settings)
            self.hierarchies.append(hierarchy)

        return True

    def get_hierarchy_root_from_obj_lst(self, obj_lst):
        """
        Returns a List of hierarchy roots from a selection
        """
        # Get list of hierarchy prefixes
        ah_prefix_lst: List[str] = [
            prefs().env.asset_hierarchy_struct_prefix_static_mesh,
            prefs().env.asset_hierarchy_struct_prefix_static_mesh_kit,
            prefs().env.asset_hierarchy_struct_prefix_skeletal_mesh
        ]

        # Export Root List
        exp_root_lst = []

        # Go through selection to get list of upmost parents. Only add to list if item is not already there
        for obj in obj_lst:

            upmost_parent_obj = objectUtils.get_obj_upmost_parent(obj)

            # Checking if valid root
            if 'EMPTY' in objectUtils.get_obj_type(upmost_parent_obj):  # If Empty, it's a transform
                for ah_prefix in ah_prefix_lst:
                    if objectUtils.get_obj_name(upmost_parent_obj)[:len(ah_prefix)] == ah_prefix:
                        if upmost_parent_obj not in exp_root_lst:
                            exp_root_lst.append(upmost_parent_obj)

        return exp_root_lst

    def export(self, send: bool, skip_sc: bool = False):
        # SOURCE CONTROL
        if not skip_sc:
            sc_file_path_lst: List[Path] = []
            for hierarchy in self.hierarchies:
                sc_file_path_lst.append(hierarchy.path)
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
        for hierarchy in self.hierarchies:
            hierarchy.export(send)

        # SET PREVIOUS SELECTION STATE
        view_layer.objects.active = obj_active

    def critical_no_hierarchy(self):
        # Define the prefix variables first
        static_mesh_prefix = prefs().env.asset_hierarchy_struct_prefix_static_mesh
        kit_prefix = prefs().env.asset_hierarchy_struct_prefix_static_mesh_kit
        skeletal_mesh_prefix = prefs().env.asset_hierarchy_struct_prefix_skeletal_mesh

        # Construct the message
        msg = (f'The {ah_tool_name} could not find an asset hierarchy at the root of the Blender scene. '
               f'If you haven\'t created an asset hierarchy yet, you can do so from the Blue Hole Header Menu. '
               f'If you have and it is not being detected, validate that its name starts with one of the prefixes '
               f'specified in the Active Environment\'s settings. These currently are: "{static_mesh_prefix}", '
               f'"{kit_prefix}" and "{skeletal_mesh_prefix}".\n\n'
               f'Aborting export!')
        log(Severity.CRITICAL, ah_tool_name, msg, popup=True)


def get_hierarchy_prefix_lst():
    """
    Returns list of hierarchy prefix
    """
    prefix_lst = [prefs().env.asset_hierarchy_struct_prefix_static_mesh,
                  prefs().env.asset_hierarchy_struct_prefix_static_mesh_kit,
                  prefs().env.asset_hierarchy_struct_prefix_skeletal_mesh]
    return prefix_lst
