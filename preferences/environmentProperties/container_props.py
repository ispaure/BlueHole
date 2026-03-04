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

    active_container_group_tab: EnumProperty(
        name="Container Group",
        description="Choose which container group settings to display",
        items=[
            ('ASSET', "Asset Containers", "Asset container identification and structure rules"),
            ('LOOSE', "Loose Mesh", "Loose Mesh batch export (no container required)"),
        ],
        default='ASSET',
    )

    active_container_settings_tab: EnumProperty(
        name="Container Type",
        description="Choose which container type settings to display",
        items=[
            ('HIERARCHY', "Asset Hierarchy", "Asset Hierarchy container settings"),
            ('MESH', "Asset Mesh", "Asset Mesh container settings"),
            ('COLLECTION', "Asset Collection", "Asset Collection container settings"),
        ],
        default='HIERARCHY',
    )

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

    # -------------------------------------------------------------------------------------------------
    # CONTAINERS (Tab Intro)
    # -------------------------------------------------------------------------------------------------
    box = layout.box()
    column = box.column()

    row = column.row()
    row.enabled = enable_rows
    row.label(text='Containers define how scene objects are grouped into exportable assets.')

    row = column.row()
    row.enabled = enable_rows
    row.label(text='This tab controls container identification (prefixes) and container structure rules.')

    row = column.row()
    row.enabled = enable_rows
    row.label(text='Use the Blue Hole header menu to create containers.')

    # -------------------------------------------------------------------------------------------------
    # CONTAINER GROUP TABS (Asset Containers / Loose Mesh)
    # -------------------------------------------------------------------------------------------------
    box = layout.box()
    column = box.column()

    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.container, 'active_container_group_tab', expand=True)

    active_group = preference.container.active_container_group_tab

    # -------------------------------------------------------------------------------------------------
    # ASSET CONTAINERS
    # -------------------------------------------------------------------------------------------------
    if active_group == 'ASSET':

        box = layout.box()
        column = box.column()

        row = column.row()
        row.enabled = enable_rows
        row.label(text='Asset Containers define exportable assets at the scene root.')

        # -------------------------------------------------------------------------------------------------
        # ASSET CONTAINERS - REQUIRED PREFIXES
        # -------------------------------------------------------------------------------------------------
        row = column.row()
        row.enabled = enable_rows
        row.label(text='Asset Containers are detected when their root name starts with one of these prefixes.')

        row = column.row()
        row.enabled = enable_rows
        row.prop(preference.container, 'asset_hierarchy_struct_prefix_static_mesh', text='Static Mesh Prefix')

        row = column.row()
        row.enabled = enable_rows
        row.prop(preference.container, 'asset_hierarchy_struct_prefix_static_mesh_kit', text='Static Mesh Kit Prefix')

        row = column.row()
        row.enabled = enable_rows
        row.prop(preference.container, 'asset_hierarchy_struct_prefix_skeletal_mesh', text='Skeletal Mesh Prefix')

        # Spacer
        row = column.row()
        row.enabled = enable_rows
        row.label(text='')

        # -------------------------------------------------------------------------------------------------
        # CONTAINER TYPE TABS (Hierarchy / Mesh / Collection)
        # -------------------------------------------------------------------------------------------------
        tab_row = column.row()
        tab_row.enabled = enable_rows
        tab_row.prop(preference.container, 'active_container_settings_tab', expand=True)

        active_tab = preference.container.active_container_settings_tab

        # -------------------------------------------------------------------------------------------------
        # ACTIVE ASSET CONTAINER SETTINGS
        # -------------------------------------------------------------------------------------------------
        if active_tab == 'HIERARCHY':

            box_2 = box.box()
            column2 = box_2.column()

            row = column2.row()
            row.enabled = enable_rows
            row.label(text='Requirements: Empty object at the scene root (must use a valid prefix).')

            row = column2.row()
            row.enabled = enable_rows
            row.label(text='Optional child Empty objects:')

            row = column2.row()
            row.enabled = enable_rows
            row.prop(preference.container, 'create_element_render', text='Render [Nests Visual Meshes]')
            if prefs().container.create_element_render:
                row.prop(preference.container, 'asset_hierarchy_empty_object_meshes', text='Name')

            row = column2.row()
            row.enabled = enable_rows
            row.prop(preference.container, 'create_element_collision', text='Collision [Nests Collisions]')
            if prefs().container.create_element_collision:
                row.prop(preference.container, 'asset_hierarchy_empty_object_collisions', text='Name')

            row = column2.row()
            row.enabled = enable_rows
            row.prop(preference.container, 'create_element_sockets', text='Sockets [Nests Sockets]')
            if prefs().container.create_element_sockets:
                row.prop(preference.container, 'asset_hierarchy_empty_object_sockets', text='Name')

            row = column2.row()
            row.enabled = enable_rows
            row.label(text='Child group behavior:')

            row = column2.row()
            row.enabled = enable_rows
            row.prop(preference.container, 'exclude_element_if_no_child', text='Exclude empty child groups from export')

        elif active_tab == 'MESH':

            box_2 = box.box()
            column2 = box_2.column()

            row = column2.row()
            row.enabled = enable_rows
            row.label(text='Requirements: Mesh object at the scene root (must use a valid prefix).')

            row = column2.row()
            row.enabled = enable_rows
            row.label(text='No structure rules for this container type.')

        elif active_tab == 'COLLECTION':

            box_2 = box.box()
            column2 = box_2.column()

            row = column2.row()
            row.enabled = enable_rows
            row.label(text='Requirements: Collection at the scene root (must use a valid prefix).')

            row = column2.row()
            row.enabled = enable_rows
            row.label(text='No structure rules for this container type.')

    # -------------------------------------------------------------------------------------------------
    # LOOSE MESH (Batch Export)
    # -------------------------------------------------------------------------------------------------
    elif active_group == 'LOOSE':

        box = layout.box()
        column = box.column()

        row = column.row()
        row.enabled = enable_rows
        row.label(text='Exports each selected mesh as its own file. No prefixes or container structure required.')

        # Optional: keep a settings sub-box for visual symmetry
        box_2 = box.box()
        column = box_2.column()

        row = column.row()
        row.enabled = enable_rows
        row.label(text='SETTINGS')

        row = column.row()
        row.enabled = enable_rows
        row.label(text='No settings for Loose Mesh.')
