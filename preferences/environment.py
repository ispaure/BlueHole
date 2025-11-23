"""
This loads up the Blue Hole Preferences [Environment] Section. Renamed "Structure"
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

import bpy
from bpy.props import *
from pathlib import Path

import BlueHole.blenderUtils.addon as addon
import BlueHole.Utils.env as env
import BlueHole.blenderUtils.filterUtils as filterUtils


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

class bc(bpy.types.PropertyGroup):

    # Get list of environments
    env_enum_prop_lst = env.get_env_lst_enum_property()

    # Active Environment
    active_environment: EnumProperty(name="Active Environment",
                                     description="Defines the project directory structure.",
                                     items=env_enum_prop_lst,
                                     default='default'
                                     )

    # Source Content Root Path
    sc_path: StringProperty(name='Source Content Root Path',
                            subtype='DIR_PATH',
                            description='Root Directory in which all Source Content Asset Directory Structures '
                                        'reside. \nNeeds to be set for Send to Unreal & Send to Unity',
                            default='DEFAULT_STR')

    sc_path_alternate: StringProperty(name='Source Content Root Path (Alternate)',
                            subtype='DIR_PATH',
                            description='Root Directory (Alternate) in which all Source Content Asset Directory Structures '
                                        'reside. Optional path used as fallback. In case of doubt, ignore.',
                            default='DEFAULT_STR')

    sc_path_mac: StringProperty(name='Source Content Root Path',
                            subtype='DIR_PATH',
                            description='Root Directory in which all Source Content Asset Directory Structures '
                                        'reside. \nNeeds to be set for Send to Unreal & Send to Unity',
                            default='DEFAULT_STR')

    sc_path_mac_alternate: StringProperty(name='Source Content Root Path (Alternate)',
                            subtype='DIR_PATH',
                            description='Root Directory (Alternate) in which all Source Content Asset Directory Structures '
                                        'reside. Optional path used as fallback. In case of doubt, ignore.',
                            default='DEFAULT_STR')

    # Source Content: Asset Directory Structure
    # Defines the structure for storage of a source content asset (work files such as .blend files, temp .fbx, etc.)

    sc_dir_struct_scenes: StringProperty(name = 'Scenes',
                                         description = 'Subdirectory storing .blend scene files',
                                         default = 'DEFAULT_STR')

    sc_dir_struct_resources: StringProperty(name='Resources',
                                            description='Subdirectory storing temporary work files',
                                            default='DEFAULT_STR')

    sc_dir_struct_st: StringProperty(name='Speedtree Fronds',
                                     description='Subdirectory for exporting SpeedTree fronds',
                                     default='DEFAULT_STR')

    sc_dir_struct_st_hr: StringProperty(name='Speedtree Fronds (High Res)',
                                        description='Subdirectory for exporting SpeedTree fronds (High-Resolution)',
                                        default='DEFAULT_STR')

    sc_dir_struct_st_lr: StringProperty(name='Speedtree Fronds (Low Res)',
                                        description='Subdirectory for exporting SpeedTree fronds (Low-Resolution)',
                                        default='DEFAULT_STR')

    sc_dir_struct_ref: StringProperty(name='References',
                                      description='Subdirectory for storing visual references (images, pureRef, etc.)',
                                      default='DEFAULT_STR')

    sc_dir_struct_final: StringProperty(name='Final Exports',
                                        description='Subdirectory for final exported .FBX (ie. for Send to Unreal)',
                                        default='DEFAULT_STR')

    sc_dir_struct_msh_bake: StringProperty(name='Mesh Bakes',
                                           description='Subdirectory to export meshes for detail baking '
                                                       'outside Blender',
                                           default='DEFAULT_STR')

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

    # # Draw Environment specific settings, if available.
    # # Determine path to current environment
    # current_env_path = envUtils.get_env_lst()[addon.preference().environment.active_environment]
    # # Determine path to preference file
    # python_module_path = str(Path(current_env_path + '/env_preferences.py'))
    # imp_module = importUtils.import_python_module_absolute_path(python_module_path)
    # if imp_module is not None:
    #     imp_module.draw(preference, context, layout)

    # Lay out environment settings
    enable_rows = addon.preference().environment.active_environment != 'default'

    # Source Content Path
    box = layout.box()
    column = box.column()
    row = column.row()
    row.enabled = enable_rows
    row.label(text="Source Content Root Path: Contains all art source files for your project.")

    if filterUtils.filter_platform('win'):

        row = column.row()
        row.enabled = enable_rows
        row.prop(preference.environment, 'sc_path', text='Source Content')

        row = column.row()
        row.enabled = enable_rows
        row.prop(preference.environment, 'sc_path_alternate', text='Source Content (Alternate)')

    elif filterUtils.filter_platform('mac'):

        row = column.row()
        row.enabled = enable_rows
        row.prop(preference.environment, 'sc_path_mac', text='Source Content')

        row = column.row()
        row.enabled = enable_rows
        row.prop(preference.environment, 'sc_path_mac_alternate', text='Source Content (Alternate)')

    # Asset Directory Structure
    box = layout.box()
    column = box.column()
    row = column.row()
    row.enabled = enable_rows
    row.label(text='Source Asset Directory: Define your working files\' directory structure.')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.environment, 'sc_dir_struct_scenes', text='Scenes')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.environment, 'sc_dir_struct_resources', text='Resources')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.environment, 'sc_dir_struct_st', text='SpeedTree Fronds')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.environment, 'sc_dir_struct_st_lr', text='(ST Low Res)')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.environment, 'sc_dir_struct_st_hr', text='(ST High Res)')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.environment, 'sc_dir_struct_ref', text='References')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.environment, 'sc_dir_struct_final', text='Final Exports')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.environment, 'sc_dir_struct_msh_bake', text='Mesh Bakes')

    # Give proper separation
    row = column.row()
    row.label(text='')

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
    row.prop(preference.environment, 'asset_hierarchy_struct_prefix_static_mesh', text='Static Mesh')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.environment, 'asset_hierarchy_struct_prefix_static_mesh_kit', text='Static Mesh Kit')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.environment, 'asset_hierarchy_struct_prefix_skeletal_mesh', text='Skeletal Mesh')
    row = column.row()
    row.enabled = enable_rows
    row.label(text='Empty Objects: ')
    row.prop(preference.environment, 'exclude_element_if_no_child', text='Exclude if no Child')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.environment, 'create_element_render', text='Render')
    if addon.preference().environment.create_element_render:
        row.prop(preference.environment, 'asset_hierarchy_empty_object_meshes', text='Name')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.environment, 'create_element_collision', text='Collision')
    if addon.preference().environment.create_element_collision:
        row.prop(preference.environment, 'asset_hierarchy_empty_object_collisions', text='Name')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.environment, 'create_element_sockets', text='Socket')
    if addon.preference().environment.create_element_sockets:
        row.prop(preference.environment, 'asset_hierarchy_empty_object_sockets', text='Name')
