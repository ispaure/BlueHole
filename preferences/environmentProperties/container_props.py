"""
Enter description
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
from bpy.props import *
from ...Lib.commonUtils.osUtils import *
from ..prefs import *

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

class ContainerPG(bpy.types.PropertyGroup):
    # Asset Hierarchy Structure
    asset_hierarchy_struct_prefix_static_mesh: StringProperty(name='Static Mesh',
                                                              description='Prefix for Asset Hierarchies created with '
                                                                          'static mesh type',
                                                              default='DEFAULT_STR')

    asset_hierarchy_struct_prefix_static_mesh_kit: StringProperty(name='Static Mesh Kit',
                                                                  description='Prefix for Asset Hierarchies created '
                                                                              'with static mesh kit type',
                                                                  default='DEFAULT_STR')

    asset_hierarchy_struct_prefix_skeletal_mesh: StringProperty(name='Skeletal Mesh',
                                                                description='Prefix for Asset Hierarchies created '
                                                                            'with skeletal mesh kit type',
                                                                default='DEFAULT_STR')

    # EXCLUDE IF NO CHILDREN

    descript_msg = 'When enabled, excludes elements from being part of the export if they are empty. For example, if ' \
                   'Empty Object "Collision" is found to have no children underneath it, even though it is present in' \
                   ' the Asset Hierarchy, it will not be part of the exported file. This is cleaner and the ' \
                   'recommended method for Unity as there is less bloat.'
    exclude_element_if_no_child: BoolProperty(name='Exclude Element if no Child',
                                              description=descript_msg)

    # CREATE ELEMENT: RENDER
    create_element_render: BoolProperty(name='Render',
                                        description='Whether to include "Render" as part of new asset hierarchies and whether to require it upon export',
                                        default=True)

    # CREATE ELEMENT: COLLISION
    create_element_collision: BoolProperty(name='Collision',
                                           description='Whether to include "Collision" as part of new asset hierarchies and whether to require it upon export',
                                           default=True)

    # CREATE ELEMENT: SOCKETS
    create_element_sockets: BoolProperty(name='Sockets',
                                         description='Whether to include "Sockets" as part of new asset hierarchies and whether to require it upon export',
                                         default=False)

    # NAME ELEMENTS

    asset_hierarchy_empty_object_meshes: StringProperty(name='Render Meshes',
                                                        description='Name of empty object within asset hierarchy '
                                                                    'which will contain rendered meshes',
                                                        default='DEFAULT_STR')

    asset_hierarchy_empty_object_collisions: StringProperty(name='Collision Meshes',
                                                            description='Name of empty object within asset hierarchy '
                                                                        'which will contain collision meshes',
                                                            default='DEFAULT_STR')

    asset_hierarchy_empty_object_sockets: StringProperty(name='Sockets',
                                                         description='Name of empty object within asset hierarchy '
                                                                     'which will contain sockets',
                                                         default='DEFAULT_STR')


def label_row(path, prop, row, label=''):
    row.label(text=label)
    row.prop(path, prop, text='')


def draw(preference, context, layout):

    # Lay out environment settings
    enable_rows = prefs().general.active_environment != 'default'

    # Asset Directory Structure
    box = layout.box()
    column = box.column()

    # Asset Hierarchy Structure
    box = layout.box()
    column = box.column()
    row = column.row()
    row.enabled = enable_rows
    row.label(text='Asset Hierarchy: Define the structure of individually exported containers.')
    row = column.row()
    row.enabled = enable_rows
    row.label(text='Prefixes')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.container, 'asset_hierarchy_struct_prefix_static_mesh', text='Static Mesh')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.container, 'asset_hierarchy_struct_prefix_static_mesh_kit', text='Static Mesh Kit')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.container, 'asset_hierarchy_struct_prefix_skeletal_mesh', text='Skeletal Mesh')
    row = column.row()
    row.enabled = enable_rows
    row.label(text='Empty Objects: ')
    row.prop(preference.container, 'exclude_element_if_no_child', text='Exclude if no Child')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.container, 'create_element_render', text='Render')
    if prefs().container.create_element_render:
        row.prop(preference.container, 'asset_hierarchy_empty_object_meshes', text='Name')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.container, 'create_element_collision', text='Collision')
    if prefs().container.create_element_collision:
        row.prop(preference.container, 'asset_hierarchy_empty_object_collisions', text='Name')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.container, 'create_element_sockets', text='Socket')
    if prefs().container.create_element_sockets:
        row.prop(preference.container, 'asset_hierarchy_empty_object_sockets', text='Name')
