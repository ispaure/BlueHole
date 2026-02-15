"""
Object utilities for Blue Hole
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

import mathutils as mathutils

import bpy

from ..commonUtils.debugUtils import *
from . import sceneUtils
from ..preferences.prefs import *


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

def deselect_all():
    """
    Deselects everything
    """
    bpy.ops.object.select_all(action='DESELECT')


def add_object_empty(name, parent=None, dsp_type=0, dsp_size=0.15, lock_transform=False):
    """
    Adds an "Empty" object with given hierarchy_lst
    :param name: Name of object
    :type name: str
    :param parent: (Optional) Parent object under which to create empty object. Root if unspecified
    :type parent: Object (!!-See if can make description here more explicit)
    :param dsp_type: Type of icon to display empty object as
    :type dsp_type: int
    :return:
    """
    dsp_type_array = ['PLAIN_AXES', 'ARROWS', 'SINGLE_ARROW', 'CIRCLE', 'CUBE', 'SPHERE', 'CONE', 'IMAGE']
    new_obj = bpy.data.objects.new(name, None)
    new_obj.empty_display_size = dsp_size
    # Display mode
    new_obj.empty_display_type = dsp_type_array[dsp_type]
    bpy.context.scene.collection.objects.link(new_obj)
    # Parent
    if parent is not None:
        new_obj.parent = parent
    if lock_transform:
        new_obj.lock_location[0] = True
        new_obj.lock_location[1] = True
        new_obj.lock_location[2] = True
        new_obj.lock_rotation[0] = True
        new_obj.lock_rotation[1] = True
        new_obj.lock_rotation[2] = True
        new_obj.lock_scale[0] = True
        new_obj.lock_scale[1] = True
        new_obj.lock_scale[2] = True
    return new_obj


def add_cube(name, parent=None):
    """
    Adds a primitive cube to the scene.
    """
    new_obj = bpy.ops.mesh.primitive_cube_add()
    bpy.context.active_object.name = name
    if parent is not None:
        bpy.context.active_object.parent = parent
    return new_obj


def add_default_icosphere(name, parent=None):
    """
    Adds an icosphere to the scene.
    """
    new_obj = bpy.ops.mesh.primitive_ico_sphere_add(enter_editmode=False,
                                                    align='WORLD',
                                                    location=(0,0,1),
                                                    scale=(0.9999, 0.9999, 0.9999))
    bpy.context.active_object.name = name
    if parent is not None:
        bpy.context.active_object.parent = parent
    return new_obj


def add_asset_hierarchy(hierarchy_lst, include_default_mesh, include_selected_obj, dsp_arrows=True):
    """
    Creates an asset hierarchy from the given name. This asset hierarchy is to be used for sending to other DDC & UE.
    :param hierarchy_lst: Lst of name of root of object hierarchies
    :type hierarchy_lst: lst
    :param include_default_mesh: Should the default icosphere mesh be created inside the new hierarchy?
    :type include_default_mesh: bool
    :param include_selected_obj: Should the selected objects be moved to the new hierarchy?
    :type include_selected_obj: bool
    :param dsp_arrows: Should the empty objects from the hierarchy display as arrows?
    :type dsp_arrows: bool
    :param include_element_render: Should an empty object of type render be created in hierarchy
    :type include_element_render: bool
    :param include_element_collision: Should an empty object of type collision be created in hierarchy
    :type include_element_collision: bool
    :param include_element_sockets: Should an empty object of type sockets be created in hierarchy
    :type include_element_sockets: bool
    """
    log(Severity.DEBUG, 'Add Asset Hierarchy', 'Executing Add Asset Hierarchy Procedure...')

    # Set to Object Mode
    sceneUtils.set_object_mode()

    # Create "Empty" Object Type at root, with given hierarchy_lst
    for hierarchy in hierarchy_lst:

        # Get selection
        selected_obj_lst = get_selection()

        # Deselect everything
        deselect_all()

        if dsp_arrows:
            root_object = add_object_empty(hierarchy, None, 1, 0.2)
        else:
            root_object = add_object_empty(hierarchy, None, 0, 0.2)

        # Create underlying "Empty" objects.

        # Null Meshes
        if prefs().env.create_element_render:
            null_meshes_name = prefs().env.asset_hierarchy_empty_object_meshes  # Name
            null_mesh_object = add_object_empty(null_meshes_name, root_object, 3, 0.15, True)  # Create

            # Default Cube under Render Empty Object
            if include_default_mesh:
                default_cube_suffix = '_placeHolderMesh01'
                add_default_icosphere(hierarchy + default_cube_suffix, null_mesh_object)

            # If there is a single hierarchy and defined to include selection
            if len(hierarchy_lst) == 1 and include_selected_obj:
                if len(selected_obj_lst) > 0:
                    for selected_obj in selected_obj_lst:
                        selected_obj.parent = null_mesh_object

        # Null Collisions
        if prefs().env.create_element_collision:
            null_collisions_name = prefs().env.asset_hierarchy_empty_object_collisions
            add_object_empty(null_collisions_name, root_object, 4, 0.05, True)  # Create

        # Null Sockets
        if prefs().env.create_element_sockets:
            null_sockets_name = prefs().env.asset_hierarchy_empty_object_sockets  # Name
            add_object_empty(null_sockets_name, root_object, 5, 0.05, True)  # Create

        # Deselect everything
        deselect_all()


def get_obj_child(obj):
    """
    Get list of children
    :param obj: Object to get list of children from
    :type obj: Object
    :rtype: lst of Objects
    """
    return obj.children


def get_obj_child_recursive(obj):
    """
    Get list of children objects (recursive)
    :param obj: Object to get list of children (recursively) from
    :type obj: Object
    :rtype: lst of Objects
    """
    child_recursive_lst = []

    def obj_append_get_child(child_obj):
        """
        Function to execute over and over again as long as Object has children
        :param obj: Object to execute the function on
        :type obj: Object
        """
        if child_obj is not obj:
            child_recursive_lst.append(child_obj)
        child_obj_lst = get_obj_child(child_obj)
        if len(child_obj_lst) > 0:
            for child in child_obj_lst:
                obj_append_get_child(child)

    obj_append_get_child(obj)
    return child_recursive_lst


def get_obj_parent(obj):
    """
    Returns the parent object of an object
    """
    return obj.parent


def get_obj_upmost_parent(obj):
    obj_parent = get_obj_parent(obj)
    if obj_parent is not None:
        return get_obj_upmost_parent(obj_parent)
    else:
        return obj


def get_obj_root_lst_type_empty():
    """
    Get a list of the objects at the root of the scene of type 'EMPTY'
    """
    scene_obj_lst = sceneUtils.get_scene_obj_lst()
    scene_root_lst = []
    for scene_obj in scene_obj_lst:
        upmost_parent_obj = get_obj_upmost_parent(scene_obj)
        if upmost_parent_obj not in scene_root_lst:
            if 'EMPTY' in get_obj_type(upmost_parent_obj):
                scene_root_lst.append(upmost_parent_obj)
    return scene_root_lst


def delete_obj(obj):
    """
    Delete an object
    """
    if obj.type == 'MESH':
        # bpy.context.scene.objects.unlink(obj)
        # bpy.data.meshes.remove(obj.data)
        pass
    bpy.data.objects.remove(obj)


def delete_obj_lst(obj_lst):
    """
    Delete an object
    """

    for obj in obj_lst:
        delete_obj(obj)


def delete_obj_recursive(obj):
    """
    Deletes an object as well as everything else underneath it in the hierarchy
    """
    obj_del_lst = get_obj_child_recursive(obj)
    obj_del_lst.append(obj)
    delete_obj_lst(obj_del_lst)


def get_obj_type(obj):
    """
    Returns the object type of an object
    :param obj: Object to get type of
    :type obj: Object
    :rtype: str
    """
    return obj.type


def get_obj_name(obj):
    """
    Returns the hierarchy_lst of an object
    :param obj: Object to get the hierarchy_lst of
    :type obj: Object
    :rtype: str
    """
    return obj.name


def set_obj_name(obj, name):
    """
    Sets the name of an object
    """
    obj.name = name


def select_obj_lst(obj_lst):
    """
    Selects all objects in a list
    :param obj_lst: List of Objects to select
    :type obj_lst: lst
    """
    for obj in obj_lst:
        obj.select_set(True)


def get_obj_by_name(name):
    """
    Gets Blender Object from given hierarchy_lst
    :param name: Name of the Object that will be returned
    :type name: str
    :rtype: Object
    """
    scene_obj_lst = sceneUtils.get_scene_obj_lst()
    for obj in scene_obj_lst:
        if obj.name == name:
            return obj


def get_obj_world_translation(obj):
    """
    Get world translation of given object.
    rtype: Vector?
    """
    return obj.matrix_world.to_translation()


def set_obj_world_translation(obj, vector_xyz):
    """
    Set world translation of given object.
    :param obj: Object
    :type obj: Object
    :param vector_xyz: Vector with X, Y, Z translations
    :type vector_xyz: mathUtils.Vector
    """
    obj.location = vector_xyz


def set_zero_obj_world_translation(obj):
    """
    Set world translation of given object to 0, 0, 0.
    """
    vector_zero_translation = mathutils.Vector((0, 0, 0))
    set_obj_world_translation(obj, vector_zero_translation)


def get_selection():
    """
    Get current selection of objects.
    """
    # TODO: Added 2 lines here... idk if itll break something
    # # before was just the return
    # view_layer = bpy.context.view_layer
    # obj_active = view_layer.objects.active
    return bpy.context.selected_objects
