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

class DirectoryPG(bpy.types.PropertyGroup):
    sc_dir_struct_scenes: StringProperty(name='Scenes',
                                         description='Subdirectory storing .blend scene files',
                                         default='DEFAULT_STR')

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


def label_row(path, prop, row, label=''):
    row.label(text=label)
    row.prop(path, prop, text='')


def draw(preference, context, layout):

    # Lay out environment settings
    enable_rows = prefs().general.active_environment != 'default'

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
