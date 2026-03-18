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

class DirectoryPG(bpy.types.PropertyGroup):
    sc_dir_struct_scenes: StringProperty(name='Scenes',
                                         description='Subdirectory storing .blend scene files',
                                         default='')

    sc_dir_struct_resources: StringProperty(name='Resources',
                                            description='Subdirectory storing temporary work files',
                                            default='RES')

    sc_dir_struct_st: StringProperty(name='Speedtree Fronds',
                                     description='Subdirectory for exporting SpeedTree fronds',
                                     default='RES/ST')

    sc_dir_struct_st_hr: StringProperty(name='Speedtree Fronds (High Res)',
                                        description='Subdirectory for exporting SpeedTree fronds (High-Resolution)',
                                        default='RES/ST/HR')

    sc_dir_struct_st_lr: StringProperty(name='Speedtree Fronds (Low Res)',
                                        description='Subdirectory for exporting SpeedTree fronds (Low-Resolution)',
                                        default='RES/ST/LR')

    sc_dir_struct_ref: StringProperty(name='References',
                                      description='Subdirectory for storing visual references (images, pureRef, etc.)',
                                      default='RES/REF')

    sc_dir_struct_final: StringProperty(name='Final Exports',
                                        description='Subdirectory for final exported .FBX (ie. for Send to Unreal)',
                                        default='')

    sc_dir_struct_msh_bake: StringProperty(name='Mesh Bakes',
                                           description='Subdirectory to export meshes for detail baking '
                                                       'outside Blender',
                                           default='RES/BAKE')


def label_row(path, prop, row, label=''):
    row.label(text=label)
    row.prop(path, prop, text='')


def draw(preference, context, layout):

    # Lay out environment settings
    enable_rows = prefs().general.active_environment != 'default'

    # -------------------------------------------------------------------------------------------------
    # DIRECTORY STRUCTURE TAB
    # -------------------------------------------------------------------------------------------------
    box = layout.box()
    column = box.column()

    row = column.row()
    row.enabled = enable_rows
    row.label(text='Defines the sub-directory layout for the Blender scene and its exported assets and containers.')

    row = column.row()
    row.enabled = enable_rows
    row.label(text='Fields left blank correspond to the root of your current structure.')

    # -------------------------------------------------------------------------------------------------
    # BLENDER (.BLEND)
    # -------------------------------------------------------------------------------------------------
    box = layout.box()
    column = box.column()

    row = column.row()
    row.enabled = enable_rows
    row.label(text='BLENDER (.BLEND)')

    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.directory, 'sc_dir_struct_scenes', text='Scenes')

    # -------------------------------------------------------------------------------------------------
    # WORKING FILES
    # -------------------------------------------------------------------------------------------------
    box = layout.box()
    column = box.column()

    row = column.row()
    row.enabled = enable_rows
    row.label(text='WORKING FILES')

    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.directory, 'sc_dir_struct_resources', text='Resources')

    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.directory, 'sc_dir_struct_ref', text='References')

    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.directory, 'sc_dir_struct_msh_bake', text='Mesh Bakes')

    # -------------------------------------------------------------------------------------------------
    # SPEEDTREE EXPORTS
    # -------------------------------------------------------------------------------------------------
    box_2 = box.box()
    column = box_2.column()

    row = column.row()
    row.enabled = enable_rows
    row.label(text='SPEEDTREE EXPORTS')

    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.directory, 'sc_dir_struct_st', text='SpeedTree Fronds')

    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.directory, 'sc_dir_struct_st_lr', text='SpeedTree Fronds (Low Res)')

    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.directory, 'sc_dir_struct_st_hr', text='SpeedTree Fronds (High Res)')

    # -------------------------------------------------------------------------------------------------
    # SEND & EXPORTS
    # -------------------------------------------------------------------------------------------------
    box = layout.box()
    column = box.column()

    row = column.row()
    row.enabled = enable_rows
    row.label(text='SEND & EXPORTS')

    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.directory, 'sc_dir_struct_final', text='Final')


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

def register():
    bpy.utils.register_class(DirectoryPG)


def unregister():
    bpy.utils.unregister_class(DirectoryPG)
