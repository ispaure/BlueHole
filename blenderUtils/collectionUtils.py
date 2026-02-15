"""
Blue Hole functions to get collections. Not used anywhere yet but could be useful in the future.
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

import bpy


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

def get_or_add_collection_if_not_exist(name):
    """
    Gets a collection (if collection with name already exists), else adds a collection (with name)
    :param name: Name of collection to get or create
    :param type: str
    :return: Collection
    """
    if get_collection(name) is None:
        return add_collection(name)
    else:
        return get_collection(name)


def add_collection(name):
    """
    Create collection with given name
    :param name: Collection name
    :type name: str
    """
    bpy.ops.collection.create(name=name)
    bpy.context.scene.collection.children.link(bpy.data.collections[name])
    return bpy.data.collections[name]


def get_collection(name):
    """
    Get a collection object by name
    :param name: Name of collection to get
    :type name: str
    """
    if bpy.data.collections.get(name):
        return bpy.data.collections.get(name)
    else:
        return None
