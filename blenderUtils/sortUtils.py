"""
Sort utilities for Blue Hole.
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
import os

from . import objectUtils
from ..Lib.commonUtils.debugUtils import *

# ----------------------------------------------------------------------------------------------------------------------
# GLOBALS

sort_utils_name = filename = os.path.basename(__file__)

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def sort_selected(world_axis, distance, second_world_axis=None, item_amt_per_row=None):
    """
    Sort selected object pivot points on an axis using the given distance.

    :param world_axis: World axis ('X', 'Y', or 'Z') on which to sort objects, starting at 0, 0, 0
    :param distance: Distance at which to separate object pivot points
    :param second_world_axis: Optional second world axis for 2D sorting
    :param item_amt_per_row: Optional item count per row for 2D sorting
    """
    obj_sel = objectUtils.get_selection()

    obj_sel_dict = {}
    obj_name_lst = []
    for obj in obj_sel:
        obj_sel_dict[obj.name] = obj
        obj_name_lst.append(obj.name)

    obj_name_lst.sort()

    counter = 0

    for obj_name in obj_name_lst:
        sort_distance = counter * distance

        # TODO: Implement subsequent rows.
        if world_axis == 'X':
            translation_vector = mathutils.Vector((sort_distance, 0, 0))
        elif world_axis == 'Y':
            translation_vector = mathutils.Vector((0, sort_distance, 0))
        elif world_axis == 'Z':
            translation_vector = mathutils.Vector((0, 0, sort_distance))
        else:
            log(Severity.ERROR, 'Sort Selection Tool', 'World Axis is Invalid!')
            return False

        objectUtils.set_obj_world_translation(obj_sel_dict[obj_name], translation_vector)
        counter += 1

    return True


def search_replace_name_selected(search, replace):
    """
    Search and replace text in the names of selected objects.
    """
    obj_sel = objectUtils.get_selection()
    for obj in obj_sel:
        obj_name = objectUtils.get_obj_name(obj)
        obj.name = obj_name.replace(search, replace)


def flip_text_last_underscore():
    """
    Flip the last two underscore-separated parts of selected object names.
    """
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

        log(Severity.DEBUG, sort_utils_name, f'Reconstructed name: "{obj_name_reconstruct}"')
        obj.name = obj_name_reconstruct


def batch_rename_selected(name, padding):
    """
    Batch rename selected objects using the given name and padding parameter
    (for example: Mesh_01, Mesh_02).

    :param name: Base name to assign to objects
    :param padding: Padding type
    """

    def no_input_name():
        msg = 'No Input Name was given for objects. Please try again.'
        log(Severity.ERROR, sort_utils_name, msg)

    def no_selection():
        msg = 'No object was selected for the operation. Select at least one object and try again.'
        log(Severity.ERROR, sort_utils_name, msg)

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
            log(
                Severity.ERROR,
                sort_utils_name,
                'This script was not made to work with more than 999 objects. Please adjust the script if needed.',
            )
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

    return True
