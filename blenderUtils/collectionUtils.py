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
# IMPORTS

import bpy

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def get_or_add_collection_if_not_exist(name: str):
    """
    Get a collection by name, or create it if it does not exist.

    :param name: Name of collection to get or create
    :return: Collection
    """
    collection = get_collection(name)
    if collection is None:
        return add_collection(name)

    return collection


def add_collection(name: str):
    """
    Create a collection with the given name.

    :param name: Collection name
    """
    bpy.ops.collection.create(name=name)
    bpy.context.scene.collection.children.link(bpy.data.collections[name])
    return bpy.data.collections[name]


def get_collection(name: str):
    """
    Get a collection object by name.

    :param name: Name of collection to get
    """
    return bpy.data.collections.get(name)
