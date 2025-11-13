"""
The old version of the export scripts for Blue Hole. Has been refactored in exportUtils2.
Need to make sure all the features are in exportUtils2 now, before I delete this. And redirect stuff
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
import BlueHole.blenderUtils.uiUtils as uiUtils
import BlueHole.blenderUtils.filterUtils as filterUtils
import BlueHole.blenderUtils.objectUtils as objectUtils
import BlueHole.blenderUtils.sendUnreal as sendUnreal
import BlueHole.blenderUtils.configUtils as configUtils


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

def batch_export_selected_as_fbx(export_dir):
    """
    Batch exports selection as one .fbx file per object. Will connect to source control if enabled in user preferences.
    :param export_dir: Directory path to export to
    :type export_dir: str
    """
    tool_name = 'Batch Export to FBX'
    print_debug_msg('Initiating batch export to .FBX in directory: "{}"'.format(export_dir), show_verbose)

    # Initial Checks
    check_result = filterUtils.check_tests(tool_name,
                                           check_blend_exist=True,
                                           check_blend_loc_in_dir_structure=True,
                                           check_selection_not_empty=True)
    if not check_result:
        return False

    # Getting User Selection
    view_layer = bpy.context.view_layer
    obj_active = view_layer.objects.active
    selection = oUtils.get_selection()

    # Set to Object Mode
    sceneUtils.set_object_mode()

    # Unselect everything
    bpy.ops.object.select_all(action='DESELECT')

    # Determine file paths of exports
    obj_and_file_path_lst = []
    file_path_lst = []
    for obj in selection:
        # Determine file name
        name = bpy.path.clean_name(obj.name)
        file_path = os.path.join(export_dir, name)
        file_path = file_path + '.fbx'
        # Append obj alongside file name
        obj_and_file_path_lst.append([obj, file_path])
        file_path_lst.append(file_path)

    # Connect to source control and attempt to mark for add or checkout.
    print_debug_msg('Interfacing with Source Control script...', show_verbose)
    result = scUtils.sc_open_edit_file_path_lst(file_path_lst)

    # If did not succeed, cancel export unless user preferences allow to proceed
    if addon.preference().sourcecontrol.source_control_error_aborts_exp and not result:
        # User already received popup warning about error, so just log to console.
        print_debug_msg('Source Control did not process properly. Aborting export!', show_verbose)
        return False

    for obj in obj_and_file_path_lst:
        print_debug_msg('Preparing export of object named: ' + oUtils.get_obj_name(obj[0]), show_verbose)
        obj[0].select_set(True)

        # Save Object position and move to 0, 0, 0
        if addon.preference().general.exp_select_zero_root_transform:
            obj_world_translation = oUtils.get_obj_world_translation(obj[0])
            oUtils.set_zero_obj_world_translation(obj[0])

        # some exporters only use the active object
        view_layer.objects.active = obj[0]

        # export
        bpy.ops.export_scene.fbx(filepath=obj[1],
                                 use_selection=True,
                                 axis_forward='-Y',
                                 axis_up='Z',
                                 mesh_smooth_type='FACE',
                                 use_mesh_modifiers=True)

        # Set Object position to previous
        if addon.preference().general.exp_select_zero_root_transform:
            oUtils.set_obj_world_translation(obj[0], obj_world_translation)

        obj[0].select_set(False)

        print_debug_msg('Exported object named: ' + oUtils.get_obj_name(obj[0]), show_verbose)

    view_layer.objects.active = obj_active

    for obj in selection:
        obj.select_set(True)

    # Export completed successfully!
    print_debug_msg('Batch Export to FBX has completed successfully!', show_verbose)
    return True


def export_selected_as_fbx(exp_obj_lst, exp_file_path, animation, apply_scale_options, axis_forward, axis_up):
    """
    Exports everything selected together as one fbx, in target folder
    :param exp_obj_lst: List of objects to export (in same file)
    :type exp_obj_lst: lst
    :param exp_file_path: Export path (excl. extension)
    :type exp_file_path: str
    :param animation: When True, exports animation. When False, exports without animation.
    :type animation: bool
    :param apply_scale_options: apply_scale_options (enum in ['FBX_SCALE_NONE', 'FBX_SCALE_UNITS',
                                'FBX_SCALE_CUSTOM', 'FBX_SCALE_ALL'])
    :type apply_scale_options: str
    :param axis_forward: Defines the forward axis upon export
    :type axis_forward: str
    :param axis_up: Defines the up axis upon export
    :type axis_up: str
    """

    view_layer = bpy.context.view_layer

    # Store visibility of objects
    obj_visibility_lst = []
    print('ORIGINAL DATA------------------------------------------------------------------------------------------')
    for exp_obj in exp_obj_lst:
        print(exp_obj.name)
        print(exp_obj.visible_get())
        obj_visibility_lst.append([exp_obj, exp_obj.visible_get()])

    # Show invisible objects
    for obj in obj_visibility_lst:
        if not obj[1]:
            obj[0].hide_set(False)

    # Select objects to export
    oUtils.select_obj_lst(exp_obj_lst)

    print('Exporting FBX...')
    print('settings: FA:{}, UA:{}'.format(axis_forward, axis_up))

    try:
        bpy.ops.export_scene.fbx(filepath=exp_file_path + '.fbx',
                                 use_selection=True,
                                 apply_scale_options=apply_scale_options,
                                 mesh_smooth_type='OFF',
                                 use_mesh_modifiers=True,
                                 bake_anim=animation,
                                 axis_forward=axis_forward,
                                 axis_up=axis_up
                                 )
    except:
        msg = 'The FBX Exporter could not export successfully.' \
              '\nTarget file: {export_path}.fbx' \
              '\nPlease look at the System Console for more details.'
        if filterUtils.filter_platform('win'):
            file_of_error = str(exp_file_path.split('\\')[-1])
        if filterUtils.filter_platform('mac'):
            file_of_error = str(exp_file_path.split('/')[-1])
        else:
            print('Platform not supported')
        uiUtils.show_dialog_box('FBX Exporter', msg.format(export_path=file_of_error))

    # Unselect all
    oUtils.deselect_all()

    # Recall stored visibility
    for obj in obj_visibility_lst:
        object_item = obj[0]
        object_visibility = obj[1]
        if object_visibility:
            object_visibility = False
        else:
            object_visibility = True
        object_item.hide_set(object_visibility)


def get_export_hierarchy_root_lst(obj_lst, hierarchy_prefix):
    """
    Gets export hierarchy(ies) from a list of objects
    :param obj_lst: List of objects to search to find an export hierarchy
    :type obj_lst: List of Objects
    :param hierarchy_prefix: List of prefixes that hierarchy could have.
    :type hierarchy_prefix: lst
    :rtype: lst
    """
    exp_root_lst = []
    print_debug_msg('Filtering scene objects for export hierarchy(ies)...', show_verbose)
    for obj in obj_lst:
        if oUtils.get_obj_parent(obj) is None:  # If none, it's a root object
            if 'EMPTY' in oUtils.get_obj_type(obj):  # If Empty, it's a transform
                for prefix in hierarchy_prefix:
                    if oUtils.get_obj_name(obj)[:len(prefix)] == prefix:  # If prefix, root of export hierarchy
                        print_debug_msg('Found export hierarchy root named: ' + oUtils.get_obj_name(obj), show_verbose)
                        exp_root_lst.append(obj)
    return exp_root_lst


class Hierarchy:
    """
    Define hierarchy class, that will hold parameters used at different parts of the script.
    """
    def __init__(self):
        self.name = ''  # Root
        self.root_obj = None  # Root Empty Object
        self.required_empty_obj = []  # Required empty objects are objects whose children will get exported.
        self.obj_exp_lst = []  # Object export list
        self.render_obj = None  # Render Empty Object
        self.collision_obj = None  # Collision Empty Object
        self.socket_obj = None  # Socket Empty Object


def exp_obj_hierarchies_unreal(selected_only, trigger_import_cmd=False):
    """
    Exports Blender hierarchy/hierarchies to FBX File, according to Preferences.
    :param selected_only: If to only send selected asset hierarchies or all the ones in the scene.
    :type selected_only: bool
    :param trigger_import_cmd: If should communicate with Unreal to trigger import of resulting files within Unreal.
    :type trigger_import_cmd: bool
    """
    def get_obj_hierarchy_exp_struct_unreal():
        exp_struct_dict = {}

        # Render
        empty_obj_name = addon.preference().environment.asset_hierarchy_empty_object_meshes
        if addon.preference().environment.create_element_render:
            exp_struct_dict['Render'] = [empty_obj_name, True]
        else:
            exp_struct_dict['Render'] = [empty_obj_name, False]

        # Collision
        empty_obj_name = addon.preference().environment.asset_hierarchy_empty_object_collisions
        if addon.preference().environment.create_element_collision:
            exp_struct_dict['Collision'] = [empty_obj_name, True]
        else:
            exp_struct_dict['Collision'] = [empty_obj_name, False]

        # Sockets
        empty_obj_name = addon.preference().environment.asset_hierarchy_empty_object_sockets
        if addon.preference().environment.create_element_sockets:
            exp_struct_dict['Socket'] = [empty_obj_name, True]
        else:
            exp_struct_dict['Socket'] = [empty_obj_name, False]

        # Prefixes
        exp_struct_dict['Prefixes'] = get_hierarchy_prefix_lst()

        return exp_struct_dict

    # Export path
    exp_dir = projectUtils.get_project_sub_dir('path_final')

    # Get object hierarchy export structure for Unreal
    object_hierarchy_exp_struct = get_obj_hierarchy_exp_struct_unreal()

    # Get Zero Root Transform Preference
    zero_root_transform = addon.preference().general.ue_bridge_zero_root_transform

    # Get Include Animation Preference
    include_animation = addon.preference().general.ue_bridge_include_animation

    # Export hierarchies
    exported_file_paths = export_obj_hierarchies(exp_dir=exp_dir,
                                                 object_hierarchy_exp_struct=object_hierarchy_exp_struct,
                                                 separate_files=True,
                                                 zero_root_transform=zero_root_transform,
                                                 selected_only=selected_only,
                                                 source_control=True,
                                                 animation=include_animation,
                                                 axis_forward='-Y',
                                                 axis_up='Z')

    # If user wants to trigger import command within Unreal of exported fbx files.
    if trigger_import_cmd:

        for exported_file_path in exported_file_paths:
            result = sendUnreal.trigger_unreal_import(exported_file_path)
            if not result:
                return False

            # If one file doesn't succeed sending, cancel the following ones.
            if not result:
                return False


def exp_obj_hierarchies_unity(selected_only):
    """
    Exports Blender hierarchy/hierarchies to FBX File, according to Preferences.
    """
    tool_name = 'Send Asset Hierarchies to Unity'

    def get_obj_hierarchy_exp_struct_unity():
        exp_struct_dict = {}

        # Render
        empty_obj_name = addon.preference().environment.asset_hierarchy_empty_object_meshes
        if addon.preference().environment.create_element_render:
            exp_struct_dict['Render'] = [empty_obj_name, True]
        else:
            exp_struct_dict['Render'] = [empty_obj_name, False]

        # Collision
        empty_obj_name = addon.preference().environment.asset_hierarchy_empty_object_collisions
        if addon.preference().environment.create_element_collision:
            exp_struct_dict['Collision'] = [empty_obj_name, True]
        else:
            exp_struct_dict['Collision'] = [empty_obj_name, False]

        # Sockets
        empty_obj_name = addon.preference().environment.asset_hierarchy_empty_object_sockets
        if addon.preference().environment.create_element_sockets:
            exp_struct_dict['Socket'] = [empty_obj_name, True]
        else:
            exp_struct_dict['Socket'] = [empty_obj_name, False]

        # Prefixes
        exp_struct_dict['Prefixes'] = get_hierarchy_prefix_lst()

        return exp_struct_dict

    def display_path_error_source_content(path):
        msg = 'The Source Content Root Path specified in the Active Environment\'s preferences could ' \
              'not be reached: "{path}". Please create said directory or edit the Active Environment\'s preferences ' \
              'to point to an existing folder.'.format(path=str(path))
        show_dialog_box(tool_name, msg)

    def display_path_error_unity_assets(path):
        msg = 'The Unity Project\'s Assets Path specified in the Active Environment\'s preferences could ' \
              'not be reached: "{}". Please create said directory or edit the Active Environment\'s preferences ' \
              'to point to an existing Unity Assets folder. Example: "C:\\YourUnityProject\\Assets\\"'.format(str(path))
        show_dialog_box(tool_name, msg)

    def display_path_error_blend(sc_path_seek, blend_path_found):
        msg = 'The opened Blender scene file is not located within the Source Content directory path specified in ' \
              'the Active Environment\'s preferences. ' \
              '\n\nExpected Blender file within: "{sc_path}"\nFound Blender file at: "{blend_path}"' \
              '\n\nThis is required because the Send to Unity\'s script mirrors the folder structure from the ' \
              'Source Content Root Path to the Unity Project\'s Assets Path. Please move your Blender file or edit ' \
              'the Source Content Root Path in the Active Environment\'s ' \
              'preferences.'.format(sc_path=sc_path_seek, blend_path=blend_path_found)
        show_dialog_box(tool_name, msg)

    # ------------------------------------------------------------------------------------------------------------------
    # VALIDATE ENV_VARIABLES.INI has valid SourceContent path for Unity Bridge, and that current .blend file is within.

    # Get SourceContent's directory path from env_variables.ini (the root of where blender files and assets are saved)
    if filterUtils.filter_platform('win'):
        sc_path = str(Path(addon.preference().environment.sc_path))
    elif filterUtils.filter_platform('mac'):
        sc_path = str(Path(addon.preference().environment.sc_path_mac))
    # Validate this path is valid, else throw error
    if not fileUtils.is_path_valid(sc_path):
        display_path_error_source_content(sc_path)
        return False

    # Validate that currently opened blend file has location on disk.
    check_result = filterUtils.check_tests('Export Asset Hierarchy',
                                           check_blend_exist=True)
    if not check_result:
        return False

    # Validate currently opened blend file is within SourceContent
    blend_path = str(Path(fileUtils.get_blend_directory_path()))
    if sc_path not in blend_path:
        display_path_error_blend(sc_path, blend_path)
        return False

    # Get Unity Project's "Assets" sub-folder path from env_variables.ini (the root where Unity assets are to be saved)
    if filterUtils.filter_platform('win'):
        unity_assets_path = str(Path(addon.preference().general.unity_assets_path))
    elif filterUtils.filter_platform('mac'):
        unity_assets_path = str(Path(addon.preference().general.unity_assets_path_mac))
    else:
        return False

    # Validate this path is valid, else throw error
    if not fileUtils.is_path_valid(unity_assets_path):
        display_path_error_unity_assets(unity_assets_path)
        return False

    # ------------------------------------------------------------------------------------------------------------------
    # DETERMINE EXP DIR FROM KNOWN VARIABLES
    project_final_dir = projectUtils.get_project_sub_dir('path_final')
    exp_dir = project_final_dir.replace(sc_path, unity_assets_path)
    # Prevent crash if path already includes last '/' for both windows & macos
    if exp_dir[-1] == '\\' or exp_dir[-1] == '/':
        exp_dir = exp_dir[0:-2]

    # Get object hierarchy export structure for Unreal
    object_hierarchy_exp_struct = get_obj_hierarchy_exp_struct_unity()

    # Get Zero Root Transform Preference
    zero_root_transform = addon.preference().general.unity_bridge_zero_root_transform

    # Get Include Animation Preference
    include_animation = addon.preference().general.unity_bridge_include_animation

    # Get axis forward Preference
    axis_forward = addon.preference().general.unity_forward_axis

    # Get up axis preference
    axis_up = addon.preference().general.unity_up_axis

    # Export hierarchies
    export_obj_hierarchies(exp_dir=exp_dir,
                           object_hierarchy_exp_struct=object_hierarchy_exp_struct,
                           separate_files=True,
                           zero_root_transform=zero_root_transform,
                           selected_only=selected_only,
                           source_control=True,
                           animation=include_animation,
                           apply_scale_options='FBX_SCALE_UNITS',
                           axis_forward=axis_forward,
                           axis_up=axis_up,
                           is_unity=True)


def get_hierarchy_prefix_lst():
    """
    Returns list of hierarchy prefix
    """
    prefix_lst = [addon.preference().environment.asset_hierarchy_struct_prefix_static_mesh,
                  addon.preference().environment.asset_hierarchy_struct_prefix_static_mesh_kit,
                  addon.preference().environment.asset_hierarchy_struct_prefix_skeletal_mesh]
    return prefix_lst


def get_selected_exp_root_lst(hierarchy_prefix):
    """
    Returns a list of asset hierarchies, even if only partially selected.
    :param hierarchy_prefix: List of hierarchy prefixes to search for
    :type hierarchy_prefix: lst
    """

    # Get current selection
    current_sel = oUtils.get_selection()

    # Export root list
    exp_root_lst = []

    # Go through selection to get list of upmost parents. Only add to list if item is not already there
    for obj in current_sel:

        # Debug
        print_debug_msg('Performing iteration on ' + oUtils.get_obj_name(obj), show_verbose)
        print(obj)

        # Getting upmost parent of object
        upmost_parent_obj = oUtils.get_obj_upmost_parent(obj)

        # Checking if valid root
        print_debug_msg('Checking if parent object is of type Empty', show_verbose)
        if 'EMPTY' in oUtils.get_obj_type(upmost_parent_obj):  # If Empty, it's a transform
            print_debug_msg('Was of type empty', show_verbose)
            for prefix in hierarchy_prefix:
                if oUtils.get_obj_name(upmost_parent_obj)[:len(prefix)] == prefix:  # If prefix, root of asset hierarchy
                    print_debug_msg('Found export hierarchy root named: ' + oUtils.get_obj_name(upmost_parent_obj),
                                    show_verbose)
                    if upmost_parent_obj not in exp_root_lst:
                        exp_root_lst.append(upmost_parent_obj)
        else:
            print_debug_msg('Upmost object was not found deem as root', show_verbose)

    return exp_root_lst


def export_obj_hierarchies(exp_dir, object_hierarchy_exp_struct, separate_files=False, zero_root_transform=False,
                           selected_only=False, source_control=True, animation=True,
                           apply_scale_options='FBX_SCALE_NONE', axis_forward='-Y', axis_up='Z', is_unity=False):
    """
    Exports hierarchies, either in one file or separately.
    :param exp_dir: Directory in which to export hierarchies
    :type exp_dir: str
    :param object_hierarchy_exp_struct: Dictionary with information on object hierarchy (and what should get exported).
    :type object_hierarchy_exp_struct: dict
    :param separate_files: When True, exports hierarchies as separate files using hierarchy name.
                           When False, exports hierarchies as a single file using blender file name.
    :type separate_files: bool
    :param zero_root_transform: When True, exports hierarchies with their root pivot set to 0,0,0
    :type zero_root_transform: bool
    :param selected_only: When True, export only selected hierarchies (roots should be the only thing selected)
    :type selected_only: bool
    :param source_control: Define if source control should be used or not
    :type source_control: bool
    :param animation: Defines if animation should be exported or not
    :type animation: bool
    :param apply_scale_options: apply_scale_options (enum in ['FBX_SCALE_NONE', 'FBX_SCALE_UNITS',
                                'FBX_SCALE_CUSTOM', 'FBX_SCALE_ALL'])
    :type apply_scale_options: str
    :param axis_forward: Defines the forward axis upon export
    :type axis_forward: str
    :param axis_up: Defines the up axis upon export
    :type axis_up: str
    :return: the name of the file that has been exported
    :rtype: str or lst (depends on value of parameter separate_files)
    """
    tool_name = 'Asset Hierarchy Exporter exportUtils.py is legacy'
    msg = 'The blenderUtils/exportUtils.py module of Blue Hole is being phased out as it has been refactored as ' \
          'exportUtils2.py. I heavily recommend to adapt your code to use exportUtils2.py as exportUtils.py might ' \
          'be broken or eventually break. Press OK to continue with the export.'
    uiUtils.show_dialog_box('Blue Hole: Obsolete Warning', msg)

    # TODO: Include Hidden Objects

    def display_error_code_1_dialog():
        msg = 'The Asset Hierarchy Exporter could not find an asset hierarchy at the root of the blender scene. ' \
              'If you haven\'t created an asset hierarchy yet, you can do so from the Blue Hole Header Menu. ' \
              'If you have and it is not being detected, validate that its name starts with one of the prefixes ' \
              'specified in the Active Environment\'s settings. These currently are: "{}", "{}" and "{}".' \
              '\n\nAborting export!' \
              ''.format(addon.preference().environment.asset_hierarchy_struct_prefix_static_mesh,
                        addon.preference().environment.asset_hierarchy_struct_prefix_static_mesh_kit,
                        addon.preference().environment.asset_hierarchy_struct_prefix_skeletal_mesh)
        show_dialog_box(tool_name, msg)

    def display_error_code_2_dialog(req_exp, exp_root_name):
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
              '\n\nAborting export!'.format(req_exp_type=req_exp[0], req_exp_name=req_exp[1], exp_root=exp_root_name)
        show_dialog_box(tool_name, msg)

    def display_error_code_3_dialog(required_exp, exp_root_name):
        msg = 'The required Export Element under the Asset Hierarchy "{exp_root}" of type: {required_exp} is found ' \
              'more than once. This can happen because of the trailing numbers Blender creates (.001, .002). ' \
              'Please fix this issue.' \
              '\n\nAborting export!'.format(required_exp=required_exp, exp_root=exp_root_name)
        show_dialog_box(tool_name, msg)

    def display_error_code_4_dialog(exp_root, child):
        exp_root_name = oUtils.get_obj_name(exp_root)
        child_name = oUtils.get_obj_name(child)
        msg = 'The object named {child_name} under the Asset Hierarchy "{exp_root_name}" is not of type Empty Object.' \
              ' Please move it within one of the Asset Hierarchy\'s required Export Element(s) -- or at least within ' \
              'an Empty Object. \n\nAborting export!'.format(exp_root_name=exp_root_name, child_name=child_name)
        show_dialog_box(tool_name, msg)

    def display_error_code_7_dialog():
        msg = 'One or more of the selected objects are not part of a valid Asset Hierarchy, as specified in ' \
              'the Active Environment\'s settings. If you are unsure what is wrong, try using the Send All ' \
              'Asset Hierarchies option. You may get more insight.' \
              '\n\nAborting export!'
        show_dialog_box(tool_name, msg)

    def display_error_doc():
        fileUtils.open_url(configUtils.get_url_db_value('Tutorial', 'asset_hierarchy_exporter_errors'))

    def get_first_mesh_obj(hierarchy_cls):
        """
        Gets the first mesh object in given hierarchy
        """
        for required_null_obj in hierarchy_cls.required_empty_obj:
            null_mesh_name = object_hierarchy_exp_struct['Render'][0]
            if null_mesh_name in required_null_obj.name:
                null_mesh_childs = oUtils.get_obj_child_recursive(required_null_obj)
                for mesh_child in null_mesh_childs:
                    if mesh_child.type == 'MESH':
                        return mesh_child

    def export_procedure(name, root_lst, exp_obj_lst):
        """
        Export procedure, once the selection of objects has been fully decided.
        :param name: Name of file to export (minus extension)
        :type name: str
        :param root_lst: List of root objects that will be exported
        :type root_lst: lst of Objects
        :param exp_obj_lst: List of Objects to export
        :type exp_obj_lst: lst of Objects
        :return: Export file path
        :rtype: str
        """

        # Determine export path
        exp_file_pth = str(Path(exp_dir + '/' + name))
        print_debug_msg('Export path (minus ext.): ' + exp_file_pth, show_verbose)

        # If "Zero Root Transform on Send" set in the preferences, Store Transform X, Y, Z and Set them to 0
        root_transform_lst = []
        if zero_root_transform:
            for root in root_lst:
                root_transform_lst.append([root, oUtils.get_obj_world_translation(root)])
                oUtils.set_zero_obj_world_translation(root)

        if is_unity:
            # For export to Unity, tweak rotation of root.
            objectUtils.select_obj_lst([hierarchy_cls.root_obj])
            bpy.ops.object.transform_apply(rotation=True)
            bpy.ops.transform.rotate(value=-1.57079632679, orient_axis='X', constraint_axis=(True, False, False))
            bpy.ops.object.transform_apply(rotation=True)
            bpy.ops.transform.rotate(value=1.57079632679, orient_axis='X', constraint_axis=(True, False, False))
            bpy.ops.object.select_all(action='DESELECT')

        # Exporting scene
        print_debug_msg('Exporting scene to temp directory...', show_verbose)
        Path(exp_dir).mkdir(parents=True, exist_ok=True)
        export_selected_as_fbx(exp_obj_lst, exp_file_pth, animation, apply_scale_options, axis_forward, axis_up)
        print_debug_msg('Exported scene to temp directory successfully!', show_verbose)

        # If object was hidden, set back as hidden

        # If "Zero Root Transform on Send" set in the preferences, Set back original Root Transform X, Y, Z
        if zero_root_transform:
            for root_transform in root_transform_lst:
                oUtils.set_obj_world_translation(root_transform[0], root_transform[1])

        # Return path of the file that was exported
        return exp_file_pth

    def sc_export_files(hierarchy_cls_lst, source_control):
        """
        Checks files or mark for add before export.
        :param source_control: If source control is to be attempted or not
        :type source_control: bool
        """
        exp_file_path_lst = []
        # List of file paths to export (incl. ext)
        for hierarchy_cls in hierarchy_cls_lst:
            # Determine export path
            exp_file_pth = str(Path(exp_dir + '/' + objectUtils.get_obj_name(hierarchy_cls.root_obj) + '.fbx'))
            print_debug_msg('Export path (incl ext.): ' + exp_file_pth, show_verbose)
            exp_file_path_lst.append(exp_file_pth)

        # If source control is enabled for this specific script
        if source_control:
            # Connect to source control and attempt to mark for add or checkout.
            result = scUtils.sc_open_edit_file_path_lst(exp_file_path_lst)

            # If did not go well, abort export if Source Control Preferences are set to do so.
            if addon.preference().sourcecontrol.source_control_error_aborts_exp:
                if not result:
                    return False

        # If gets here, ran as intended
        return True

    # Set to Object Mode
    sceneUtils.set_object_mode()

    # Initial Checks
    check_result = filterUtils.check_tests('Export Asset Hierarchy',
                                           check_blend_exist=True,
                                           check_blend_loc_in_dir_structure=True)
    if not check_result:
        return False

    # Get hierarchy prefixes
    hierarchy_prefix = object_hierarchy_exp_struct['Prefixes']

    # If Selected ONLY
    if selected_only:
        print_debug_msg('Only selected roots will later get exported!', show_verbose)

        # Get list of roots of selection for export.
        exp_root_lst = get_selected_exp_root_lst(hierarchy_prefix)

        # List of selected objects are the exp_root_lst
        hierarchy_cls_lst = []

        for exp_root in exp_root_lst:
            hierarchy = Hierarchy()
            hierarchy.name = oUtils.get_obj_name(exp_root)
            hierarchy.root_obj = exp_root
            hierarchy_cls_lst.append(hierarchy)

        if len(hierarchy_cls_lst) == 0:
            display_error_code_7_dialog()
            return False

        # Unselect all
        oUtils.deselect_all()

    # If ALL
    else:
        print_debug_msg('All object hierarchies will later get exported!', show_verbose)
        # Unselect all
        oUtils.deselect_all()

        # Get complete list of objects in scene
        print_debug_msg('Getting list of objects in scene...', show_verbose)
        scene_obj_lst = sceneUtils.get_scene_obj_lst()

        # Filtering scene objects for export hierarchy(ies)
        exp_root_lst = get_export_hierarchy_root_lst(scene_obj_lst, hierarchy_prefix)

        # Creating Hierarchy Classes!
        hierarchy_cls_lst = []

        for exp_root in exp_root_lst:
            new_hierarchy = Hierarchy()
            new_hierarchy.name = oUtils.get_obj_name(exp_root)
            new_hierarchy.root_obj = exp_root
            print_debug_msg('Created Hierarchy class named: ' + new_hierarchy.name, show_verbose)
            print_debug_msg('Root object for that hierarchy: ' + str(new_hierarchy.root_obj), show_verbose)
            hierarchy_cls_lst.append(new_hierarchy)

    # If class list is empty, cannot proceed with export. Show proper error message.
    if len(hierarchy_cls_lst) == 0:
        display_error_code_1_dialog()
        return False

    for hierarchy_cls in hierarchy_cls_lst:
        msg = 'Validate export root {name} contain proper Empty Objects for export...'.format(name=hierarchy_cls.name)
        print_debug_msg(msg, show_verbose)
        child_obj_tuple = oUtils.get_obj_child(hierarchy_cls.root_obj)

        # Determine required exports list
        required_exp_lst = []
        if object_hierarchy_exp_struct['Render'][1]:  # If True (was to be enabled)
            required_exp_lst.append(['Render', object_hierarchy_exp_struct['Render'][0]])
        if object_hierarchy_exp_struct['Collision'][1]:  # If True (was to be enabled)
            required_exp_lst.append(['Collision', object_hierarchy_exp_struct['Collision'][0]])
        if object_hierarchy_exp_struct['Socket'][1]:  # If True (was to be enabled)
            required_exp_lst.append(['Socket', object_hierarchy_exp_struct['Socket'][0]])

        # See if required exp are there
        for required_exp in required_exp_lst:
            match_found = 0
            for child in child_obj_tuple:
                if 'EMPTY' not in oUtils.get_obj_type(child):  # Make sure there are no stray objects under root.
                    display_error_code_4_dialog(hierarchy_cls.root_obj, child)
                    return False
                child_name = oUtils.get_obj_name(child).split('.')[0]
                if child_name == required_exp[1]:
                    match_found += 1
                    hierarchy_cls.required_empty_obj.append(child)
                    # See which one it was, and add to class
                    if child_name == addon.preference().environment.asset_hierarchy_empty_object_meshes:
                        hierarchy_cls.render_obj = child
                    if child_name == addon.preference().environment.asset_hierarchy_empty_object_collisions:
                        hierarchy_cls.collision_obj = child
                    if child_name == addon.preference().environment.asset_hierarchy_empty_object_sockets:
                        hierarchy_cls.socket_obj = child
            exp_root_name = oUtils.get_obj_name(hierarchy_cls.root_obj)
            if match_found < 1:  # Validate there is not 0 match
                display_error_code_2_dialog(required_exp, exp_root_name)
                return False
            elif match_found > 1:  # Validate there is not more than one match
                display_error_code_3_dialog(required_exp[0], exp_root_name)
                return False
        print_debug_msg('Validated export roots contain proper Empty Objects!', show_verbose)

        # Rename collision meshes to be in line with Unreal naming conventions.
        # Get first mesh name
        first_mesh_obj = get_first_mesh_obj(hierarchy_cls)
        # If object is root of all collision meshes
        for required_empty_obj in hierarchy_cls.required_empty_obj:
            null_collisions_name = object_hierarchy_exp_struct['Collision'][0]
            if null_collisions_name in required_empty_obj.name:
                print_debug_msg('Found Collision Null! Renaming children to match Unreal naming convention...', show_verbose)
                # Get list of all child objects
                collision_objs = oUtils.get_obj_child_recursive(required_empty_obj)
                # Rename all child objects
                counter = 1
                for collision_obj in collision_objs:
                    collision_obj.name = 'UCX_' + str(first_mesh_obj.name) + '_' + str(format(counter, '03'))
                    counter += 1

        # Create master list of everything to export
        hierarchy_cls.obj_exp_lst.append(hierarchy_cls.root_obj)
        for required_empty_obj in hierarchy_cls.required_empty_obj:
            hierarchy_cls.obj_exp_lst.append(required_empty_obj)
            required_obj_childs = oUtils.get_obj_child_recursive(required_empty_obj)
            for child in required_obj_childs:
                hierarchy_cls.obj_exp_lst.append(child)

    if separate_files:
        exp_file_path_lst = []
        if sc_export_files(hierarchy_cls_lst, source_control):
            for hierarchy_cls in hierarchy_cls_lst:
                # Because Blender can only have unique names, it means if the user has multiple hierarchies, they
                # will have odd names like Render.001, Collision.025, etc. Since we do see the folder names in Unity,
                # we want this to be clean. And can't hurt for Unreal etc. either. So if exporting as separate files, it
                # makes sense to clean this before export of each hierarchy.
                if hierarchy_cls.render_obj is not None:
                    hierarchy_cls.render_obj.name = addon.preference().environment.asset_hierarchy_empty_object_meshes
                if hierarchy_cls.collision_obj is not None:
                    hierarchy_cls.collision_obj.name = addon.preference().environment.asset_hierarchy_empty_object_collisions
                if hierarchy_cls.socket_obj is not None:
                    hierarchy_cls.socket_obj.name = addon.preference().environment.asset_hierarchy_empty_object_sockets
                # Export Asset Hierarchy
                exp_file_path = export_procedure(hierarchy_cls.name, [hierarchy_cls.root_obj], hierarchy_cls.obj_exp_lst)
                exp_file_path_lst.append(exp_file_path)
            return exp_file_path_lst
        else:
            return False
    else:
        export_obj_lst = []
        export_root_lst = []
        for hierarchy_cls in hierarchy_cls_lst:
            for obj_exp in hierarchy_cls.obj_exp_lst:
                export_obj_lst.append(obj_exp)
            export_root_lst.append(hierarchy_cls.root_obj)
        # If source control is enabled for this specific script
        if source_control:
            # Connect to source control and attempt to mark for add or checkout.
            result = scUtils.sc_open_edit_file_path_lst(fileUtils.get_blend_file_name())

            # If did not go well, abort export if Source Control Preferences are set to do so.
            if addon.preference().sourcecontrol.source_control_error_aborts_exp:
                if not result:
                    return False

        exp_file_path = export_procedure(fileUtils.get_blend_file_name(), export_root_lst, export_obj_lst)
        return exp_file_path
