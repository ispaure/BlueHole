"""
The new refactor of exportUtils. Once done, the old should redirect to here
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


import os
from pathlib import Path

import bpy

import BlueHole.blenderUtils.sourceControlUtils as scUtils
from BlueHole.blenderUtils.debugUtils import print_debug_msg as print_debug_msg
import BlueHole.blenderUtils.sceneUtils as sceneUtils
import BlueHole.blenderUtils.objectUtils as oUtils
import BlueHole.blenderUtils.fileUtils as fileUtils
from BlueHole.blenderUtils.uiUtils import show_dialog_box as show_dialog_box
import BlueHole.envUtils.projectUtils as projectUtils
import BlueHole.blenderUtils.addon as addon
import BlueHole.blenderUtils.filterUtils as filterUtils
import BlueHole.blenderUtils.objectUtils as objectUtils
import BlueHole.blenderUtils.sendUnreal as sendUnreal
import BlueHole.blenderUtils.configUtils as configUtils
import BlueHole.Utils.env as env
from typing import *


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

ah_tool_name = 'Asset Hierarchy Exporter'


class ExportSettings:
    """
    Stores the Export Settings
    """
    def __init__(self):
        self.exp_dir = ''
        self.exp_format = ''
        self.skip_sc = False
        self.zero_root_transform = False

        # Included Elements
        self.include_render = False
        self.include_collision = False
        self.include_socket = False

        # FBX Specific Settings
        self.axis_up = ''
        self.axis_fwd = ''
        self.mesh_smooth_type = ''
        self.bake_anim = False
        self.apply_scale_options = ''
        self.rename_collisions_for_ue = False


class ExportContainer:
    """
    Stores the information pertaining to what will be exported.
    """
    def __init__(self):
        self.root = None
        self.name = ''
        self.path = ''
        self.sel_lst = []
        self.render_obj = None
        self.collision_obj = None
        self.socket_obj = None


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
    exp_set_cls = ExportSettings()
    exp_set_cls.exp_format = exp_format
    exp_set_cls.exp_dir = exp_dir
    exp_set_cls.zero_root_transform = addon.preference().general.exp_select_zero_root_transform
    exp_set_cls.mesh_smooth_type = 'FACE'
    exp_set_cls.bake_anim = False
    exp_set_cls.apply_scale_options = 'FBX_SCALE_NONE'
    exp_set_cls.axis_fwd = '-Y'
    exp_set_cls.axis_up = 'Z'

    # Get User Selection
    view_layer = bpy.context.view_layer
    obj_active = view_layer.objects.active
    sel_obj_lst = oUtils.get_selection()

    # Assign Export File Paths per Object
    exp_cont_cls_lst = []
    for sel_obj in sel_obj_lst:
        print_debug_msg('Creating Container Class for object named: ' + oUtils.get_obj_name(sel_obj), show_verbose)
        exp_cont = ExportContainer()
        exp_cont.root = sel_obj
        exp_cont.name = oUtils.get_obj_name(sel_obj)
        exp_cont.path = os.path.join(exp_set_cls.exp_dir, exp_cont.name) + '.' + exp_set_cls.exp_format.lower()
        exp_cont.sel_lst = [sel_obj]
        exp_cont_cls_lst.append(exp_cont)

    export_containers(exp_cont_cls_lst, exp_set_cls)


def export_asset_hierarchies(selected_only, preset, is_send, skip_sc=False):
    """
    Exports Asset Hierarchy/Hierarchies, according to settings
    :param selected_only: When True, Only Selected Hierarchies Will Be Sent
    :type selected_only: bool
    :param preset: Which Export Settings to Use (Unreal, Unity, Bridge, etc.)
    :type preset: str
    :param is_send: When True, Not Only Exports But Connects to Engine (Unreal, Unity, etc.)
    :type is_send: bool
    :param skip_sc: When set to True, skips Source Control. Useful when sending hierarchies as part of a bridge, but
                    not to be submitted within SourceContent.
    :type skip_sc: bool
    """

    # Check Tests
    chk_result = filterUtils.check_tests(ah_tool_name,
                                         check_blend_exist=True,
                                         check_blend_loc_in_dir_structure=True)
    if not chk_result:
        return False

    if selected_only:
        chk_result = filterUtils.check_tests(ah_tool_name, check_selection_not_empty=True)
        if not chk_result:
            return False

    if is_send:
        chk_result = filterUtils.check_tests(ah_tool_name,
                                             check_source_content_root_path_exist=True,
                                             check_blend_in_source_content=True)
        if not chk_result:
            return False

    # Create ExportSettings Class
    if preset == 'Unity':
        chk_result = filterUtils.check_tests(ah_tool_name,
                                             check_unity_assets_path_exist=True)
        if not chk_result:
            return False
        exp_set_cls = get_unity_asset_hierarchy_exp_set_cls()

    elif preset == 'Unreal':
        exp_set_cls = get_unreal_asset_hierarchy_exp_set_cls()

    else:
        exp_set_cls = get_bridge_asset_hierarchy_exp_set_cls(preset)
        exp_set_cls.exp_dir.replace('\\', '/')

    # Specify if skip source control
    exp_set_cls.skip_sc = skip_sc

    # Create Export Containers from Given Settings
    static_mesh_prefix = addon.preference().environment.asset_hierarchy_struct_prefix_static_mesh
    static_mesh_kit_prefix = addon.preference().environment.asset_hierarchy_struct_prefix_static_mesh_kit
    skeletal_mesh_kit_prefix = addon.preference().environment.asset_hierarchy_struct_prefix_skeletal_mesh
    ah_prefix_lst = [static_mesh_prefix, static_mesh_kit_prefix, skeletal_mesh_kit_prefix]

    # If Selected ONLY
    if selected_only:
        # Get list of roots of selection for export
        current_sel = oUtils.get_selection()
        exp_root_lst = get_ah_root_lst(ah_prefix_lst, current_sel)
    else:
        # Get list of roots of scene for export
        all_scene = sceneUtils.get_scene_obj_lst()
        exp_root_lst = get_ah_root_lst(ah_prefix_lst, all_scene)

    # Create Containers for Found Roots
    exp_cont_cls_lst = []
    for exp_root in exp_root_lst:
        exp_cont = ExportContainer()
        exp_cont.root = exp_root
        exp_cont.name = oUtils.get_obj_name(exp_root)
        exp_cont.path = os.path.join(exp_set_cls.exp_dir, exp_cont.name) + '.' + exp_set_cls.exp_format.lower()
        exp_cont.sel_lst.append(exp_root)
        exp_cont_cls_lst.append(exp_cont)

    # If there is no hierarchy, throw error
    if exp_cont_cls_lst == 0:
        display_error_code_1_dialog()
        return False

    # See if required exports are in every hierarchy -- and that there is only one!
    for exp_cont_cls in exp_cont_cls_lst:

        # RENDER
        if exp_set_cls.include_render:
            result, render_obj = get_required_empty_obj(exp_cont_cls.root,
                                                        addon.preference().environment.asset_hierarchy_empty_object_meshes,
                                                        'Render',
                                                        do_empty_chk=exp_set_cls.include_render)
            if not result:
                return False
            else:
                exp_cont_cls.render_obj = render_obj
                exp_cont_cls.sel_lst.append(render_obj)
                render_obj_child_lst = oUtils.get_obj_child_recursive(render_obj)

                # Add Children to Export List
                for render_obj_child in render_obj_child_lst:
                    exp_cont_cls.sel_lst.append(render_obj_child)

        excl_lst = []

        # COLLISION
        if exp_set_cls.include_collision:
            result, collision_obj = get_required_empty_obj(exp_cont_cls.root,
                                                           addon.preference().environment.asset_hierarchy_empty_object_collisions,
                                                           'Collision',
                                                           do_empty_chk=exp_set_cls.include_render)
            if not result:
                return False
            else:
                exp_cont_cls.collision_obj = collision_obj
                collision_obj_child_lst = oUtils.get_obj_child_recursive(collision_obj)

                # If For Unreal, Rename According to Conventions
                if exp_set_cls.rename_collisions_for_ue:
                    counter = 1
                    if exp_set_cls.include_render and len(render_obj_child_lst) >= 1:
                        first_mesh_name = oUtils.get_obj_name(render_obj_child_lst[0])
                    elif not exp_set_cls.include_render:
                        # Get children from root
                        root_first_level_child_lst = objectUtils.get_obj_child(exp_cont_cls.root)
                        # Update value if it finds correct type
                        already_found_mesh = False
                        for root_first_level_child in root_first_level_child_lst:
                            if not already_found_mesh:
                                if objectUtils.get_obj_type(root_first_level_child) == 'MESH':
                                    first_mesh_name = objectUtils.get_obj_name(root_first_level_child)
                                    already_found_mesh = True
                        if not already_found_mesh:
                            first_mesh_name = 'Template'
                    else:
                        first_mesh_name = 'Template'
                    for collision_obj_child in collision_obj_child_lst:
                        collision_obj_child.name = 'UCX_' + str(first_mesh_name) + '_' + str(format(counter, '03'))
                        counter += 1

                # If there is at least one item or not told to exclude if empty
                if preset == 'Unity' or preset == 'Unreal':
                    if len(collision_obj_child_lst) > 0 or not addon.preference().environment.exclude_element_if_no_child:
                        # Add Collision Empty Object to Export List
                        exp_cont_cls.sel_lst.append(collision_obj)
                        # Add Children to Export List
                        for collision_obj_child in collision_obj_child_lst:
                            exp_cont_cls.sel_lst.append(collision_obj_child)
                    else:
                        excl_lst.append(collision_obj)  # To make sure it doesn't get added later
                else:
                    # Add Collision Empty Object to Export List
                    exp_cont_cls.sel_lst.append(collision_obj)
                    # Add Children to Export List
                    for collision_obj_child in collision_obj_child_lst:
                        exp_cont_cls.sel_lst.append(collision_obj_child)

        # SOCKET
        if exp_set_cls.include_socket:
            result, socket_obj = get_required_empty_obj(exp_cont_cls.root,
                                                        addon.preference().environment.asset_hierarchy_empty_object_sockets,
                                                        'Socket',
                                                        do_empty_chk=exp_set_cls.include_render)
            if not result:
                return False
            else:
                exp_cont_cls.socket_obj = socket_obj
                socket_obj_child_lst = oUtils.get_obj_child_recursive(socket_obj)

                if preset == 'Unity' or preset == 'Unreal':
                    # If there is at least one item or not told to exclude if empty
                    if len(socket_obj_child_lst) > 0 or not addon.preference().environment.exclude_element_if_no_child:
                        # Add Socket Empty Object to Export List
                        exp_cont_cls.sel_lst.append(socket_obj)
                        # Add Children to Export List
                        for socket_obj_child in socket_obj_child_lst:
                            exp_cont_cls.sel_lst.append(socket_obj_child)
                    else:
                        excl_lst.append(socket_obj)
                else:
                    # Add Socket Empty Object to Export List
                    exp_cont_cls.sel_lst.append(socket_obj)
                    # Add Children to Export List
                    for socket_obj_child in socket_obj_child_lst:
                        exp_cont_cls.sel_lst.append(socket_obj_child)

        # RENDER WASN'T INCLUDED
        if not exp_set_cls.include_render:
            # Render empty object not included, which means we need to include everything within root.
            complete_obj_lst = oUtils.get_obj_child_recursive(exp_cont_cls.root)

            # Avoid adding stuff already added above!
            for obj in complete_obj_lst:
                if obj not in exp_cont_cls.sel_lst and obj not in excl_lst:
                    exp_cont_cls.sel_lst.append(obj)

    # EXPORT
    if preset == 'Unreal' or preset == 'Unity':
        # Export Containers like determined so far
        print('EXPORTING CONTAINERS UNITY STILE')
        print(preset)
        export_containers(exp_cont_cls_lst, exp_set_cls, is_unity=preset == 'Unity')
    elif 'Single Container' in preset.keys():
        if preset['Single Container']:
            # Merge Containers for Single Container Export
            exp_cont_all = ExportContainer()
            exp_cont_all.name = preset['Name']
            exp_cont_all.path = os.path.join(exp_set_cls.exp_dir,
                                             exp_cont_all.name) + '.' + exp_set_cls.exp_format.lower()
            for exp_cont_cls in exp_cont_cls_lst:
                for sel in exp_cont_cls.sel_lst:
                    exp_cont_all.sel_lst.append(sel)
        else:
            # Was a custom export preset but is still separate containers.
            export_containers(exp_cont_cls_lst, exp_set_cls, is_unity=preset == 'Unity')
    else:
        # Merge Containers for Single Container Export
        exp_cont_all = ExportContainer()
        exp_cont_all.name = preset['Name']
        exp_cont_all.path = os.path.join(exp_set_cls.exp_dir, exp_cont_all.name) + '.' + exp_set_cls.exp_format.lower()
        for exp_cont_cls in exp_cont_cls_lst:
            for sel in exp_cont_cls.sel_lst:
                exp_cont_all.sel_lst.append(sel)

        print('EXPORTING SINGLE CONTAINER!!!!!!!!!!!!!!!!!!!!!!!!')
        export_containers([exp_cont_all], exp_set_cls)

    # IS SEND
    if preset is 'Unreal' and is_send:
        for exp_cont_cls in exp_cont_cls_lst:
            result = sendUnreal.trigger_unreal_import(exp_cont_cls.path)
            if not result:
                return False

    return True


def get_required_empty_obj(root_obj, name, type, do_empty_chk=True):
    child_obj_tuple = oUtils.get_obj_child(root_obj)
    match_found = 0
    match_obj = None
    for child_obj in child_obj_tuple:
        # Only do this following check if expecting a Render folder
        if do_empty_chk:
            if 'EMPTY' not in oUtils.get_obj_type(child_obj):
                display_error_code_4_dialog(root_obj, child_obj)
                return False, match_obj
        child_name = oUtils.get_obj_name(child_obj).split('.')[0]
        if child_name == name:
            match_found += 1
            match_obj = child_obj

    if match_found < 1:  # Validate there is not 0 match
        display_error_code_2_dialog(type, name, objectUtils.get_obj_name(root_obj))
        return False, match_obj
    elif match_found > 1:  # Validate there is not more than one match
        display_error_code_3_dialog(type, objectUtils.get_obj_name(root_obj))
        return False, match_obj

    return True, match_obj


def get_ah_root_lst(ah_prefix_lst, sel):
    """
    Returns a root list of asset hierarchies
    """

    # Export Root List
    exp_root_lst = []

    # Go through selection to get list of upmost parents. Only add to list if item is not already there
    for obj in sel:

        upmost_parent_obj = oUtils.get_obj_upmost_parent(obj)

        # Checking if valid root
        if 'EMPTY' in oUtils.get_obj_type(upmost_parent_obj):  # If Empty, it's a transform
            for ah_prefix in ah_prefix_lst:
                if oUtils.get_obj_name(upmost_parent_obj)[:len(ah_prefix)] == ah_prefix:
                    if upmost_parent_obj not in exp_root_lst:
                        exp_root_lst.append(upmost_parent_obj)

    return exp_root_lst


def get_unity_exp_dir_path(quiet: bool = False) -> Optional[Path]:
    # EXPORT OPTIONS
    # Export Format

    # Determine Export Directory
    blend_dir_path = fileUtils.get_blend_directory_path()

    # Blue Hole Prefs Class
    bh_prefs_cls = env.BlueHolePrefs()

    # Get sc path
    sc_path = bh_prefs_cls.get_valid_sc_dir_path(quiet)
    if not sc_path:
        return None
    else:
        sc_path_str = str(sc_path)

    # Get unity assets path
    unity_asset_path = bh_prefs_cls.get_valid_unity_asset_dir_path(quiet)
    if not unity_asset_path:
        return None
    else:
        unity_asset_path_str = str(unity_asset_path)

    # Ensure most chances of swap
    sc_path_str = sc_path_str.replace('\\', '/')
    unity_asset_path_str = unity_asset_path_str.replace('\\', '/')
    blend_dir_path = blend_dir_path.replace('\\', '/')

    # Swap
    exp_dir = blend_dir_path.replace(sc_path_str, unity_asset_path_str)

    # Normalize Path for OS
    return Path(exp_dir)


def get_unity_asset_hierarchy_exp_set_cls():

    # Create ExportSettings Class
    exp_set_cls = ExportSettings()

    # Set Export Format
    exp_set_cls.exp_format = 'FBX'

    # Get export directory
    exp_set_cls.exp_dir = get_unity_exp_dir_path()

    # Zero Root Transform
    exp_set_cls.zero_root_transform = addon.preference().general.unity_bridge_zero_root_transform

    # INCLUDED ELEMENTS
    exp_set_cls.include_render = addon.preference().environment.create_element_render
    exp_set_cls.include_collision = addon.preference().environment.create_element_collision
    exp_set_cls.include_socket = addon.preference().environment.create_element_sockets

    # FBX SPECIFIC OPTIONS
    # Axis Up
    exp_set_cls.axis_up = addon.preference().general.unity_up_axis
    # Axis Forward
    exp_set_cls.axis_fwd = addon.preference().general.unity_forward_axis
    # Mesh Smooth Type
    exp_set_cls.mesh_smooth_type = 'OFF'
    # Bake Animation
    exp_set_cls.bake_anim = addon.preference().general.unity_bridge_include_animation
    # Apply Scale Options
    exp_set_cls.apply_scale_options = 'FBX_SCALE_UNITS'
    # Rename collisions for UE (False because Unity)
    exp_set_cls.rename_collisions_for_ue = False

    return exp_set_cls


def get_unreal_asset_hierarchy_exp_set_cls():

    # Create ExportSettings Class
    exp_set_cls = ExportSettings()

    # EXPORT OPTIONS
    # Export Format
    exp_set_cls.exp_format = 'FBX'
    # Determine Export Directory
    exp_set_cls.exp_dir = projectUtils.get_project_sub_dir('path_final')
    # Zero Root Transform
    exp_set_cls.zero_root_transform = addon.preference().general.ue_bridge_zero_root_transform

    # INCLUDED ELEMENTS
    exp_set_cls.include_render = addon.preference().environment.create_element_render
    exp_set_cls.include_collision = addon.preference().environment.create_element_collision
    exp_set_cls.include_socket = addon.preference().environment.create_element_sockets

    # FBX SPECIFIC OPTIONS
    # Axis Up
    exp_set_cls.axis_up = 'Z'
    # Axis Forward
    exp_set_cls.axis_fwd = '-Y'
    # Mesh Smooth Type
    exp_set_cls.mesh_smooth_type = 'OFF'
    # Bake Animation
    exp_set_cls.bake_anim = addon.preference().general.ue_bridge_include_animation
    # Apply Scale Options
    exp_set_cls.apply_scale_options = 'FBX_SCALE_NONE'
    # Rename collisions for UE
    exp_set_cls.rename_collisions_for_ue = True

    return exp_set_cls


def get_bridge_asset_hierarchy_exp_set_cls(preset_exp_set_dict):
    """
    When using a bridge, allows users to specify the import settings as a dictionary (as they would be defined on their
    application's side). If keys are missing to the dictionary, use a default.
    """

    # Create ExportSettings Class
    exp_set_cls = ExportSettings()

    # EXPORT OPTIONS
    # Export Format
    if 'Format' in preset_exp_set_dict.keys():
        exp_set_cls.exp_format = preset_exp_set_dict['Format']
    else:
        exp_set_cls.exp_format = 'FBX'

    # Determine Export Directory
    if 'Export Directory' in preset_exp_set_dict.keys():
        exp_set_cls.exp_dir = preset_exp_set_dict['Export Directory']
    else:
        exp_set_cls.exp_dir = projectUtils.get_project_sub_dir('path_resources')

    # Zero Root Transform
    # Not supported because exporting multiple hierarchies in one file << This is total bs, adding it if key provided
    if 'Zero Root Transform' in preset_exp_set_dict.keys():
        exp_set_cls.zero_root_transform = preset_exp_set_dict['Zero Root Transform']
    else:
        exp_set_cls.zero_root_transform = False

    # INCLUDED ELEMENTS
    # Usually this is best if tied to the Blue Hole Environment, because it'll be in line with the Create Asset
    # Hierarchy Tool. But you can override if needed, again, with a key.
    if 'Included Elements' in preset_exp_set_dict.keys():
        exp_set_cls.include_render = preset_exp_set_dict['Included Elements']['Render']
        exp_set_cls.include_collision = preset_exp_set_dict['Included Elements']['Collision']
        exp_set_cls.include_socket = preset_exp_set_dict['Included Elements']['Socket']
    else:
        exp_set_cls.include_render = addon.preference().environment.create_element_render
        exp_set_cls.include_collision = addon.preference().environment.create_element_collision
        exp_set_cls.include_socket = addon.preference().environment.create_element_sockets

    # FBX SPECIFIC OPTIONS
    # Axis Up
    if 'Axis Up' in preset_exp_set_dict.keys():
        exp_set_cls.axis_up = preset_exp_set_dict['Axis Up']
    else:
        exp_set_cls.axis_up = 'Z'
    # Axis Forward
    if 'Axis Forward' in preset_exp_set_dict.keys():
        exp_set_cls.axis_fwd = preset_exp_set_dict['Axis Forward']
    else:
        exp_set_cls.axis_fwd = '-Y'
    # Mesh Smooth Type
    if 'Mesh Smooth Type' in preset_exp_set_dict.keys():
        exp_set_cls.mesh_smooth_type = preset_exp_set_dict['Mesh Smooth Type']
    else:
        exp_set_cls.mesh_smooth_type = 'OFF'
    # Bake Animation
    if 'Bake Animation' in preset_exp_set_dict.keys():
        exp_set_cls.bake_anim = preset_exp_set_dict['Bake Animation']
    else:
        exp_set_cls.bake_anim = addon.preference().general.ue_bridge_include_animation
    # Apply Scale Options
    if 'Apply Scale Option' in preset_exp_set_dict.keys():
        exp_set_cls.apply_scale_options = preset_exp_set_dict['Apply Scale Option']
    else:
        exp_set_cls.apply_scale_options = 'FBX_SCALE_NONE'

    if 'Rename Collisions for UE' in preset_exp_set_dict.keys():
        exp_set_cls.rename_collisions_for_ue = preset_exp_set_dict['Rename Collisions for UE']
    else:
        exp_set_cls.rename_collisions_for_ue = False

    return exp_set_cls


def export_containers(exp_cont_cls_lst, exp_set_cls, is_unity=False):
    """
    Export Containers (Asset Hierarchies, Individual Objects, etc.) to disk. And connect to Source Control if required
    """
    print_debug_msg('Initiating Export Containers Procedure...', show_verbose)

    # If not asked to skip Source Control, Continue
    if not exp_set_cls.skip_sc:

        # Retrieve Export File Path List
        exp_file_path_lst = []
        for exp_cont_cls in exp_cont_cls_lst:
            exp_file_path_lst.append(exp_cont_cls.path)

        # Attempt to Open Files for Edit
        if not scUtils.sc_open_edit_file_path_lst(exp_file_path_lst):
            if addon.preference().sourcecontrol.source_control_error_aborts_exp:
                print_debug_msg('There were errors checking out files; Aborting!', show_verbose)
                return False

    # PREPARE SELECTION STATE FOR EXPORT
    print_debug_msg('Preparing Selection State for Exports (Unselect All)', show_verbose)
    view_layer = bpy.context.view_layer
    obj_active = view_layer.objects.active
    # Set to Object Mode
    sceneUtils.set_object_mode()
    # Unselect everything
    sceneUtils.deselect_all()

    # Batch Export Containers
    for exp_cont_cls in exp_cont_cls_lst:
        msg = 'Initiating Export Container Procedure: {container_name}'
        print_debug_msg(msg.format(container_name=exp_cont_cls.name), show_verbose)

        # Rename Render, Collision, Socket objects
        if exp_cont_cls.render_obj is not None:
            # Have to do three times for this to work... IDK Why. But it works?
            exp_cont_cls.render_obj.name = addon.preference().environment.asset_hierarchy_empty_object_meshes
            exp_cont_cls.render_obj.name = addon.preference().environment.asset_hierarchy_empty_object_meshes
            exp_cont_cls.render_obj.name = addon.preference().environment.asset_hierarchy_empty_object_meshes
            print(exp_cont_cls.render_obj.name)
        if exp_cont_cls.collision_obj is not None:
            # Have to do three times for this to work... IDK Why. But it works?
            exp_cont_cls.collision_obj.name = addon.preference().environment.asset_hierarchy_empty_object_collisions
            exp_cont_cls.collision_obj.name = addon.preference().environment.asset_hierarchy_empty_object_collisions
            exp_cont_cls.collision_obj.name = addon.preference().environment.asset_hierarchy_empty_object_collisions
            print(exp_cont_cls.collision_obj.name)
        if exp_cont_cls.socket_obj is not None:
            # Have to do three times for this to work... IDK Why. But it works?
            exp_cont_cls.socket_obj.name = addon.preference().environment.asset_hierarchy_empty_object_sockets
            exp_cont_cls.socket_obj.name = addon.preference().environment.asset_hierarchy_empty_object_sockets
            exp_cont_cls.socket_obj.name = addon.preference().environment.asset_hierarchy_empty_object_sockets
            print(exp_cont_cls.socket_obj.name)

        # Store visibility of objects
        obj_visib_lst = []
        for sel in exp_cont_cls.sel_lst:
            obj_visib_lst.append([sel, sel.visible_get()])

        # Show invisible objects
        for obj in obj_visib_lst:
            if not obj[1]:
                obj[0].hide_set(False)

        # Save Object Position and Move to 0, 0, 0
        if exp_set_cls.zero_root_transform:
            print('is zero root transform')
            obj_world_translation = oUtils.get_obj_world_translation(exp_cont_cls.root)
            oUtils.set_zero_obj_world_translation(exp_cont_cls.root)
        else:
            print('is not zero root transform')

        # If Preset Is Unity, Fix Transforms of Root Before Export
        if is_unity:
            oUtils.deselect_all()
            # For export to Unity, tweak rotation of root.
            objectUtils.select_obj_lst([exp_cont_cls.root])
            bpy.ops.object.transform_apply(rotation=True)
            bpy.ops.transform.rotate(value=-1.57079632679, orient_axis='X', constraint_axis=(True, False, False))
            bpy.ops.object.transform_apply(rotation=True)
            bpy.ops.transform.rotate(value=1.57079632679, orient_axis='X', constraint_axis=(True, False, False))

        # Select Object
        objectUtils.select_obj_lst(exp_cont_cls.sel_lst)

        # Some Exporters Only Use the Active Object
        view_layer.objects.active = exp_cont_cls.root

        # Export to Format
        if exp_set_cls.exp_format == 'FBX':
            export_to_fbx(filepath=exp_cont_cls.path,
                          use_selection=True,
                          axis_forward=exp_set_cls.axis_fwd,
                          axis_up=exp_set_cls.axis_up,
                          mesh_smooth_type=exp_set_cls.mesh_smooth_type,
                          apply_scale_options=exp_set_cls.apply_scale_options,
                          bake_anim=exp_set_cls.bake_anim,
                          use_mesh_modifiers=True)

        # Reset original visibility. Pick the same objects as before (that were hidden originally, set back to hidden)
        for obj in obj_visib_lst:
            if not obj[1]:
                obj[0].hide_set(True)

        # Set Object Position to Previous
        if exp_set_cls.zero_root_transform:
            oUtils.set_obj_world_translation(exp_cont_cls.root, obj_world_translation)

        sceneUtils.deselect_all()

    view_layer.objects.active = obj_active


def export_to_fbx(filepath, use_selection, axis_forward, axis_up, mesh_smooth_type, use_mesh_modifiers,
                  apply_scale_options, bake_anim):
    """
    Exports to FBX
    """
    # Create Directory if it doesn't exist already
    Path(os.path.dirname(filepath)).mkdir(parents=True, exist_ok=True)

    # Export scene to FBX
    bpy.ops.export_scene.fbx(filepath=filepath,
                             use_selection=use_selection,
                             axis_forward=axis_forward,
                             axis_up=axis_up,
                             mesh_smooth_type=mesh_smooth_type,
                             use_mesh_modifiers=use_mesh_modifiers,
                             apply_scale_options=apply_scale_options,
                             bake_anim=bake_anim)


"""
Error Dialogues to Display When Errors Exporting an Asset Hierarchy
"""


def display_error_code_1_dialog():
    msg = 'The Asset Hierarchy Exporter could not find an asset hierarchy at the root of the blender scene. ' \
          'If you haven\'t created an asset hierarchy yet, you can do so from the Blue Hole Header Menu. ' \
          'If you have and it is not being detected, validate that its name starts with one of the prefixes ' \
          'specified in the Active Environment\'s settings. These currently are: "{}", "{}" and "{}".' \
          '\n\nAborting export!' \
          ''.format(addon.preference().environment.asset_hierarchy_struct_prefix_static_mesh,
                    addon.preference().environment.asset_hierarchy_struct_prefix_static_mesh_kit,
                    addon.preference().environment.asset_hierarchy_struct_prefix_skeletal_mesh)
    show_dialog_box(ah_tool_name, msg)


def display_error_code_2_dialog(req_exp_type, req_exp_name, exp_root_name):
    msg = 'As specified in the Active Environment\'s settings, ' \
          'the Asset Hierarchy Exporter is missing a required Export Element ({req_exp_type}) under "{exp_root}"' \
          ', which must be named "{req_exp_name}" ' \
          '(name can have trailing numbers at the end, such as .013). ' \
          '\n\nThere are a few solutions:' \
          '\n-Create the required Empty Object (as requested)' \
          '\n-Edit Your Active Environment\'s settings to not require the ' \
          'Export Element of type {req_exp_type} (Bridges Tab)' \
          '\n-The simplest solution is to create ' \
          'a new Asset Hierarchy from scratch using the tool in the Blue Hole Header Menu.' \
          '\n\nAborting export!'.format(req_exp_type=req_exp_type, req_exp_name=req_exp_name, exp_root=exp_root_name)
    show_dialog_box(ah_tool_name, msg)


def display_error_code_3_dialog(required_exp, exp_root_name):
    msg = 'The required Export Element under the Asset Hierarchy "{exp_root}" of type: {required_exp} is found ' \
          'more than once. This can happen because of the trailing numbers Blender creates (.001, .002). ' \
          'Please fix this issue.' \
          '\n\nAborting export!'.format(required_exp=required_exp, exp_root=exp_root_name)
    show_dialog_box(ah_tool_name, msg)


def display_error_code_4_dialog(exp_root, child):
    exp_root_name = oUtils.get_obj_name(exp_root)
    child_name = oUtils.get_obj_name(child)
    msg = 'The object named {child_name} under the Asset Hierarchy "{exp_root_name}" is not of type Empty Object.' \
          ' Please move it within one of the Asset Hierarchy\'s required Export Element(s) -- or at least within ' \
          'an Empty Object. \n\nAborting export!'.format(exp_root_name=exp_root_name, child_name=child_name)
    show_dialog_box(ah_tool_name, msg)


def display_error_code_7_dialog():
    msg = 'One or more of the selected objects are not part of a valid Asset Hierarchy, as specified in ' \
          'the Active Environment\'s settings. If you are unsure what is wrong, try using the Send All ' \
          'Asset Hierarchies option. You may get more insight.' \
          '\n\nAborting export!'
    show_dialog_box(ah_tool_name, msg)


def display_error_doc():
    fileUtils.open_url(configUtils.get_url_db_value('Tutorial', 'asset_hierarchy_exporter_errors'))


def get_hierarchy_prefix_lst():
    """
    Returns list of hierarchy prefix
    """
    prefix_lst = [addon.preference().environment.asset_hierarchy_struct_prefix_static_mesh,
                  addon.preference().environment.asset_hierarchy_struct_prefix_static_mesh_kit,
                  addon.preference().environment.asset_hierarchy_struct_prefix_skeletal_mesh]
    return prefix_lst
