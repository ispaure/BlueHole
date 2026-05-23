"""
Object utilities for Blue Hole.
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

import mathutils

import bpy

from ..Lib.commonUtils.debugUtils import *
from ..preferences.prefs import *
from . import sceneUtils

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def deselect_all():
    """
    Deselect all objects.
    """
    bpy.ops.object.select_all(action='DESELECT')


def add_object_empty(name, parent=None, dsp_type=0, dsp_size=0.15, lock_transform=False):
    """
    Add an Empty object with the given settings.

    :param name: Name of object
    :param parent: Optional parent object under which to create the empty
    :param dsp_type: Type of icon to display the empty object as
    :param dsp_size: Size of the empty object icon
    :param lock_transform: Lock the transforms of the empty object
    """
    dsp_type_array = ['PLAIN_AXES', 'ARROWS', 'SINGLE_ARROW', 'CIRCLE', 'CUBE', 'SPHERE', 'CONE', 'IMAGE']

    new_obj = bpy.data.objects.new(name, None)
    new_obj.empty_display_size = dsp_size
    new_obj.empty_display_type = dsp_type_array[dsp_type]

    bpy.context.scene.collection.objects.link(new_obj)

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
    Add a primitive cube to the scene.
    """
    new_obj = bpy.ops.mesh.primitive_cube_add()
    bpy.context.active_object.name = name

    if parent is not None:
        bpy.context.active_object.parent = parent

    return new_obj


def add_default_icosphere(name, parent=None):
    """
    Add an icosphere to the scene.
    """
    new_obj = bpy.ops.mesh.primitive_ico_sphere_add(
        enter_editmode=False,
        align='WORLD',
        location=(0, 0, 1),
        scale=(0.9999, 0.9999, 0.9999),
    )
    bpy.context.active_object.name = name

    if parent is not None:
        bpy.context.active_object.parent = parent

    return new_obj


def add_asset_hierarchy(hierarchy_lst, include_default_mesh, include_selected_obj, dsp_arrows=True):
    """
    Create an asset hierarchy from the given names. This asset hierarchy is used for sending to DDC and UE.

    :param hierarchy_lst: List of root object hierarchy names
    :param include_default_mesh: Should the default icosphere mesh be created inside the new hierarchy?
    :param include_selected_obj: Should the selected objects be moved to the new hierarchy?
    :param dsp_arrows: Should the empty objects from the hierarchy display as arrows?
    """
    log(Severity.DEBUG, 'Add Asset Hierarchy', 'Executing Add Asset Hierarchy Procedure...')

    sceneUtils.set_object_mode()

    for hierarchy in hierarchy_lst:
        selected_obj_lst = get_selection()

        deselect_all()

        if dsp_arrows:
            root_object = add_object_empty(hierarchy, None, 1, 0.2)
        else:
            root_object = add_object_empty(hierarchy, None, 0, 0.2)

        # Decide where exportable content should go:
        # - If Render group exists, content goes under it.
        # - Otherwise, content goes directly under the root.
        content_parent_obj = root_object

        if prefs().container.create_element_render:
            null_meshes_name = prefs().container.asset_hierarchy_empty_object_meshes
            null_mesh_object = add_object_empty(null_meshes_name, root_object, 3, 0.15, True)
            content_parent_obj = null_mesh_object

        # Default placeholder mesh goes under content parent: Render if enabled, otherwise root.
        if include_default_mesh:
            default_cube_suffix = '_placeHolderMesh01'
            add_default_icosphere(hierarchy + default_cube_suffix, content_parent_obj)

        if len(hierarchy_lst) == 1 and include_selected_obj:
            if len(selected_obj_lst) > 0:
                for selected_obj in selected_obj_lst:
                    selected_obj.parent = content_parent_obj

        if prefs().container.create_element_collision:
            null_collisions_name = prefs().container.asset_hierarchy_empty_object_collisions
            add_object_empty(null_collisions_name, root_object, 4, 0.05, True)

        if prefs().container.create_element_sockets:
            null_sockets_name = prefs().container.asset_hierarchy_empty_object_sockets
            add_object_empty(null_sockets_name, root_object, 5, 0.05, True)

        deselect_all()


def get_obj_child(obj):
    """
    Get the direct children of an object.
    """
    return obj.children


def get_obj_child_recursive(obj):
    """
    Get the children of an object recursively.
    """
    child_recursive_lst = []

    def obj_append_get_child(child_obj):
        """
        Recursively append child objects to the list.
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
    Return the parent object of an object.
    """
    return obj.parent


def get_obj_upmost_parent(obj):
    """
    Return the top-most parent of an object.
    """
    obj_parent = get_obj_parent(obj)
    if obj_parent is not None:
        return get_obj_upmost_parent(obj_parent)

    return obj


def get_obj_root_lst_type_empty():
    """
    Get a list of root scene objects of type EMPTY.
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
    Delete an object.
    """
    if obj.type == 'MESH':
        # bpy.context.scene.objects.unlink(obj)
        # bpy.data.meshes.remove(obj.data)
        pass

    bpy.data.objects.remove(obj)


def delete_obj_lst(obj_lst):
    """
    Delete a list of objects.
    """
    for obj in obj_lst:
        delete_obj(obj)


def delete_obj_recursive(obj):
    """
    Delete an object and everything underneath it in the hierarchy.
    """
    obj_del_lst = get_obj_child_recursive(obj)
    obj_del_lst.append(obj)
    delete_obj_lst(obj_del_lst)


def get_obj_type(obj):
    """
    Return the object type.
    """
    return obj.type


def get_obj_name(obj):
    """
    Return the name of an object.
    """
    return obj.name


def set_obj_name(obj, name):
    """
    Set the name of an object.
    """
    obj.name = name


def validate_obj_lst_in_view_layer(obj_lst):
    """
    Validate that all objects in a list exist in the active View Layer.

    :param obj_lst: List of objects to validate
    """
    view_layer = bpy.context.view_layer
    invalid_obj_data = []

    for obj in obj_lst:
        if obj.name not in view_layer.objects:
            collections = [col.name for col in obj.users_collection]

            invalid_obj_data.append({
                'name': obj.name,
                'type': obj.type,
                'collections': collections,
                'is_stale': not collections,
            })

    if not invalid_obj_data:
        return

    invalid_obj_lines = []

    for obj_data in invalid_obj_data:
        collections = obj_data['collections']
        collections_str = ', '.join(collections) if collections else 'None / stale object not linked to any collection'

        invalid_obj_lines.append(
            f'- Object: "{obj_data["name"]}"\n'
            f'  Type: "{obj_data["type"]}"\n'
            f'  Collections: "{collections_str}"'
        )

    stale_count = sum(1 for obj_data in invalid_obj_data if obj_data['is_stale'])

    msg = (
        f'Object validation failed.\n\n'
        f'What went wrong:\n'
        f'{len(invalid_obj_data)} object(s) are part of the export list, but are not in the active View Layer '
        f'"{view_layer.name}".\n\n'
        f'Object information:\n'
        f'- Scene: "{bpy.context.scene.name}"\n'
        f'- Active View Layer: "{view_layer.name}"\n\n'
        f'Invalid object(s):\n'
        f'{chr(10).join(invalid_obj_lines)}\n\n'
        f'Why this can happen:\n'
    )

    if stale_count:
        msg += (
            f'{stale_count} object(s) appear to be stale because they are not linked to any collection. '
            f'This can happen when an object was removed from the scene hierarchy, but a Python/export reference '
            f'to it still exists.\n\n'
            f'How to fix stale objects:\n'
            f'In the Outliner, change the display mode to "Blender File", find the stale object under Objects, '
            f'and delete it from the file.\n\n'
        )

    msg += (
        f'Other possible causes:\n'
        f'An object may be inside a collection excluded from the active View Layer, '
        f'or it may belong to another scene/view layer setup.\n\n'
        f'Export aborted before modifying scene state.'
    )

    log(Severity.ERROR, 'Object Validation', msg, popup=True)
    raise RuntimeError(msg)


def select_obj_lst(obj_lst):
    """
    Select all objects in a list.

    :param obj_lst: List of objects to select
    """
    validate_obj_lst_in_view_layer(obj_lst)

    for obj in obj_lst:
        obj.select_set(True)


def get_obj_by_name(name):
    """
    Get a Blender object by name.

    :param name: Name of the object to return
    """
    scene_obj_lst = sceneUtils.get_scene_obj_lst()
    for obj in scene_obj_lst:
        if obj.name == name:
            return obj


def get_obj_world_translation(obj):
    """
    Get the world translation of an object.
    """
    return obj.matrix_world.to_translation()


def set_obj_world_translation(obj, vector_xyz):
    """
    Set the world translation of an object.

    :param obj: Object
    :param vector_xyz: Vector with X, Y, and Z translations
    """
    obj.location = vector_xyz


def set_zero_obj_world_translation(obj):
    """
    Set the world translation of an object to 0, 0, 0.
    """
    vector_zero_translation = mathutils.Vector((0, 0, 0))
    set_obj_world_translation(obj, vector_zero_translation)


def get_selection():
    """
    Get the current object selection.
    """
    # TODO: Added 2 lines here... idk if it'll break something. <- Figure what that is about
    # # before was just the return
    # view_layer = bpy.context.view_layer
    # obj_active = view_layer.objects.active
    return bpy.context.selected_objects
