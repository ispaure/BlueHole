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
from ..prefs import *

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

class ContainerPG(bpy.types.PropertyGroup):

    # -------------------------------------------------------------------------------------------------
    # ENABLE ASSET CONTAINER TYPES
    # -------------------------------------------------------------------------------------------------

    enable_asset_hierarchy_container: BoolProperty(
        name="Asset Hierarchy",
        description="Enable Asset Hierarchy containers for this environment",
        default=True
    )

    enable_asset_mesh_container: BoolProperty(
        name="Asset Mesh",
        description="Enable Asset Mesh containers for this environment",
        default=True
    )

    enable_asset_collection_container: BoolProperty(
        name="Asset Collection",
        description="Enable Asset Collection containers for this environment",
        default=True
    )

    # -------------------------------------------------------------------------------------------------
    # UI - REMEMBER ACTIVE SUBMENUS
    # -------------------------------------------------------------------------------------------------

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
            ('HIERARCHY',  "Asset Hierarchy",  "Asset Hierarchy container settings"),
            ('MESH',       "Asset Mesh",       "Asset Mesh container settings"),
            ('COLLECTION', "Asset Collection", "Asset Collection container settings"),
        ],
        default='HIERARCHY',
    )

    # -------------------------------------------------------------------------------------------------
    # ASSET HIERARCHY STRUCTURE
    # -------------------------------------------------------------------------------------------------

    asset_hierarchy_struct_prefix_static_mesh: StringProperty(
        name="Static Mesh",
        description="Prefix for Asset Hierarchies created with static mesh type",
        default='DEFAULT_STR'
    )

    asset_hierarchy_struct_prefix_static_mesh_kit: StringProperty(
        name="Static Mesh Kit",
        description="Prefix for Asset Hierarchies created with static mesh kit type",
        default='DEFAULT_STR'
    )

    asset_hierarchy_struct_prefix_skeletal_mesh: StringProperty(
        name="Skeletal Mesh",
        description="Prefix for Asset Hierarchies created with skeletal mesh kit type",
        default='DEFAULT_STR'
    )

    # -------------------------------------------------------------------------------------------------
    # EXCLUDE IF NO CHILDREN
    # -------------------------------------------------------------------------------------------------

    descript_msg = (
        'When enabled, excludes elements from being part of the export if they are empty. '
        'For example, if Empty Object "Collision" is found to have no children underneath it, '
        'even though it is present in the Asset Hierarchy, it will not be part of the exported file. '
        'This is cleaner and the recommended method for Unity as there is less bloat.'
    )

    exclude_element_if_no_child: BoolProperty(
        name="Exclude Element if no Child",
        description=descript_msg
    )

    # -------------------------------------------------------------------------------------------------
    # CREATE ELEMENTS
    # -------------------------------------------------------------------------------------------------

    create_element_render: BoolProperty(
        name="Render",
        description=(
            'Whether to include "Render" as part of new asset hierarchies and '
            'whether to require it upon export'
        ),
        default=True
    )

    create_element_collision: BoolProperty(
        name="Collision",
        description=(
            'Whether to include "Collision" as part of new asset hierarchies and '
            'whether to require it upon export'
        ),
        default=True
    )

    create_element_sockets: BoolProperty(
        name="Sockets",
        description=(
            'Whether to include "Sockets" as part of new asset hierarchies and '
            'whether to require it upon export'
        ),
        default=False
    )

    # -------------------------------------------------------------------------------------------------
    # NAME ELEMENTS
    # -------------------------------------------------------------------------------------------------

    asset_hierarchy_empty_object_meshes: StringProperty(
        name="Render Meshes",
        description=(
            "Name of empty object within asset hierarchy "
            "which will contain rendered meshes"
        ),
        default='DEFAULT_STR'
    )

    asset_hierarchy_empty_object_collisions: StringProperty(
        name="Collision Meshes",
        description=(
            "Name of empty object within asset hierarchy "
            "which will contain collision meshes"
        ),
        default='DEFAULT_STR'
    )

    asset_hierarchy_empty_object_sockets: StringProperty(
        name="Sockets",
        description=(
            "Name of empty object within asset hierarchy "
            "which will contain sockets"
        ),
        default='DEFAULT_STR'
    )


def label_row(path, prop, row, label=''):
    row.label(text=label)
    row.prop(path, prop, text='')


def draw(preference, context, layout):

    # Lay out environment settings
    enable_rows = prefs().general.active_environment != 'default'

    # -------------------------------------------------------------------------------------------------
    # CONTAINERS - SINGLE OUTER BOX
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
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.container, 'active_container_group_tab', expand=True)

    active_group = preference.container.active_container_group_tab

    # -------------------------------------------------------------------------------------------------
    # ASSET CONTAINERS
    # -------------------------------------------------------------------------------------------------
    if active_group == 'ASSET':

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

        # -------------------------------------------------------------------------------------------------
        # ENABLE ASSET CONTAINER TYPES
        # -------------------------------------------------------------------------------------------------
        box_enable = column.box()
        column_enable = box_enable.column()

        row = column_enable.row()
        row.enabled = enable_rows
        row.label(text='Enabled Asset Container Types:')

        row = column_enable.row(align=True)
        row.enabled = enable_rows
        row.prop(preference.container, 'enable_asset_hierarchy_container', text='Hierarchy')
        row.prop(preference.container, 'enable_asset_mesh_container', text='Mesh')
        row.prop(preference.container, 'enable_asset_collection_container', text='Collection')

        # -------------------------------------------------------------------------------------------------
        # CONTAINER TYPE TABS (Hierarchy / Mesh / Collection)
        # -------------------------------------------------------------------------------------------------
        enabled_hierarchy = preference.container.enable_asset_hierarchy_container
        enabled_mesh = preference.container.enable_asset_mesh_container
        enabled_collection = preference.container.enable_asset_collection_container

        allowed_tabs: list[str] = []
        if enabled_hierarchy:
            allowed_tabs.append('HIERARCHY')
        if enabled_mesh:
            allowed_tabs.append('MESH')
        if enabled_collection:
            allowed_tabs.append('COLLECTION')

        # Edge case: nothing enabled
        if not allowed_tabs:
            row = column.row()
            row.enabled = enable_rows
            row.label(text='No Asset Container types are enabled for this environment.', icon='ERROR')
            return

        # Auto-fallback if current selection is disabled
        active_tab = preference.container.active_container_settings_tab
        if active_tab not in allowed_tabs:
            preference.container.active_container_settings_tab = allowed_tabs[0]
            active_tab = preference.container.active_container_settings_tab

        tab_row = column.row(align=True)
        tab_row.enabled = enable_rows

        def _tab_button(tab_id: str, label: str):
            btn = tab_row.operator(
                "wm.bh_set_active_container_settings_tab",
                text=label,
                depress=(active_tab == tab_id),
            )
            btn.tab = tab_id

        if enabled_hierarchy:
            _tab_button('HIERARCHY', 'Asset Hierarchy')
        if enabled_mesh:
            _tab_button('MESH', 'Asset Mesh')
        if enabled_collection:
            _tab_button('COLLECTION', 'Asset Collection')

        # -------------------------------------------------------------------------------------------------
        # ACTIVE ASSET CONTAINER SETTINGS
        # -------------------------------------------------------------------------------------------------
        box_2 = column.box()
        column2 = box_2.column()

        if active_tab == 'HIERARCHY':

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

            row = column2.row()
            row.enabled = enable_rows
            row.label(text='Requirements: Mesh object at the scene root (must use a valid prefix).')

            row = column2.row()
            row.enabled = enable_rows
            row.label(text='No structure rules for this container type.')

        elif active_tab == 'COLLECTION':

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

        row = column.row()
        row.enabled = enable_rows
        row.label(text='Exports each selected mesh as its own file. No prefixes or container structure required.')

        box_2 = column.box()
        column2 = box_2.column()

        row = column2.row()
        row.enabled = enable_rows
        row.label(text='SETTINGS')

        row = column2.row()
        row.enabled = enable_rows
        row.label(text='No settings for Loose Mesh.')
