"""
Sort utilities for Blue Hole
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
import mathutils as mathutils

# Blue Hole
import BlueHole.blenderUtils.objectUtils as objectUtils
from BlueHole.blenderUtils.debugUtils import *

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True
sort_utils_name = filename = os.path.basename(__file__)

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def sort_selected(world_axis, distance, second_world_axis=None, item_amt_per_row=None):
    """
    Sorts selected Objects pivot points on axis with distance.
    :param world_axis: World Axis ('X', 'Y' or 'Z') on which to sort Objects, starting at 0, 0, 0.
    :type world_axis: str
    :param distance: Distance at which to separate pivot points of Objects
    :type distance: float
    :param second_world_axis: (Optional; 2D Sort) World Axis ('X', 'Y', or 'Z') on which to sort Objects (subsequent rows).
    :type second_world_axis: str
    :param item_amt_per_row: (Optional; 2D sort) Items to have for each row (before switching to next row)
    :type item_amt_per_row: int
    """
    # Get selection
    obj_sel = objectUtils.get_selection()

    # Store selection in dictionary
    obj_sel_dict = {}
    obj_name_lst = []
    for obj in obj_sel:
        obj_sel_dict[obj.name] = obj
        obj_name_lst.append(obj.name)

    # Sort selection alphabetically
    obj_name_lst.sort()

    # Counter
    counter = 0

    # For objects in the selection
    for obj_name in obj_name_lst:
        # Find distance
        sort_distance = counter * distance

        # Subsequent rows
        # TODO Implement.

        # Get translation
        if world_axis == 'X':
            translation_vector = mathutils.Vector((sort_distance, 0, 0))
        elif world_axis == 'Y':
            translation_vector = mathutils.Vector((0, sort_distance, 0))
        elif world_axis == 'Z':
            translation_vector = mathutils.Vector((0, 0, sort_distance))
        else:
            log(Severity.ERROR, 'Sort Selection Tool', 'World Axis is Invalid!')
            return False

        # Set translation
        objectUtils.set_obj_world_translation(obj_sel_dict[obj_name], translation_vector)

        # Add 1 to counter
        counter += 1

    # When done, return True
    return True

def search_replace_name_selected(search, replace):
    """
    Search and replace name of selected objects
    """
    obj_sel = objectUtils.get_selection()
    for obj in obj_sel:
        obj_name = objectUtils.get_obj_name(obj)
        obj.name = obj_name.replace(search, replace)


def flip_text_last_underscore():
    obj_sel = objectUtils.get_selection()
    for obj in obj_sel:
        obj_name = objectUtils.get_obj_name(obj)
        obj_name_lst = obj_name.split('_')
        obj_name_reconstruct = ''
        for item in obj_name_lst[:-2]:
            obj_name_reconstruct += item
            obj_name_reconstruct += '_'
        obj_name_reconstruct += obj_name_lst[-1]
        obj_name_reconstruct += '_'
        obj_name_reconstruct += obj_name_lst[-2]
        print('DEBUG RECONSTRUCTED NAME IS!!!!!!!!!!!!!!!')
        print(obj_name_reconstruct)
        obj.name = obj_name_reconstruct


def batch_rename_selected(name, padding):
    """
    Batch renames selected objects with given name and padding parameter (Mesh_01, Mesh_02 sort of thing)
    :param name: Base name to be given to objects
    :type name: str
    :param padding: Padding type (string!)
    :type padding: str
    """

    def no_input_name():
        msg = 'No Input Name was given for objects. Please try again.'
        log(Severity.ERROR, sort_utils_name, msg)

    def no_selection():
        msg = 'No object was selected for the operation. Select at least one object and try again.'
        log(Severity.ERROR, sort_utils_name, msg)

    tool_name = 'Batch Rename (Selected)'

    current_sel = objectUtils.get_selection()

    if len(current_sel) < 1:
        no_selection()
        return False

    if len(name) < 1:
        no_input_name()
        return False

    if padding == 'Automatic':
        if len(current_sel) <= 9:
            padding = 1
        elif len(current_sel) <= 99:
            padding = 2
        elif len(current_sel) <= 999:
            padding = 3
        else:
            print('This script was not made to work with more than 999 objects. Please adjust the script if needed')
            return False

    counter = 1
    for item in current_sel:
        if str(padding) == '1':
            item.name = name + '_' + str(counter)
            counter += 1
        if str(padding) == '2':
            if counter <= 9:
                item.name = name + '_0' + str(counter)
            elif counter <= 99:
                item.name = name + '_' + str(counter)
            counter += 1
        if str(padding) == '3':
            if counter <= 9:
                item.name = name + '_00' + str(counter)
            elif counter <= 99:
                item.name = name + '_0' + str(counter)
            else:
                item.name = name + '_' + str(counter)
            counter += 1

    # Achieved successfully
    return True


