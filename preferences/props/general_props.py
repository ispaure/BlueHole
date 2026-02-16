"""
This loads up the Blue Hole Preferences [General] Section. Renamed "Bridges"
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

class GeneralPG(bpy.types.PropertyGroup):

    # EXPORTS: BATCH SELECTION -----------------------------------------------------------------------------------------

    # Hierarchy Root to 0,0,0
    exp_select_zero_root_transform: BoolProperty(name = 'When enabled, sets the selected objects root transforms to 0 upon export.',
                                                  default = True)

    # EXPORTS: ASSET HIERARCHIES (UNREAL) ------------------------------------------------------------------------------

    # Hierarchy Root to 0,0,0
    ue_bridge_zero_root_transform: BoolProperty(name = 'When enabled, sets the hierarchy root transforms to 0 upon export.',
                                                default = True)

    # Include animation
    ue_bridge_include_animation: BoolProperty(name = 'When enabled, includes animation in export.',
                                              default = False)

    # Use Automated Export
    ue_automated: BoolProperty(name = 'Enable Automated Import in Unreal (bypassing the FBX Import Options Window)',
                               default = True)

    # Import Materials
    ue_import_materials: BoolProperty(name='Enable import of materials in Unreal.', default=False)

    # Import Textures
    ue_import_textures: BoolProperty(name='Enable import of textures in Unreal.', default=False)

    # ------------------------------------------------------------------------------------------------------------------

    # EXPORTS: ASSET HIERARCHIES (UNITY) -------------------------------------------------------------------------------

    # Unity Assets Path
    unity_assets_path: StringProperty(name='Unity Project\'s Assets Path',
                                      subtype='DIR_PATH',
                                      description='The Unity Project\'s Assets folder. Needs to be '
                                                  'set for send to Unity',
                                      default='DEFAULT_STR')

    unity_assets_path_mac: StringProperty(name='Unity Project\'s Assets Path',
                                      subtype='DIR_PATH',
                                      description='The Unity Project\'s Assets folder. Needs to be '
                                                  'set for send to Unity',
                                      default='DEFAULT_STR')

    unity_assets_path_linux: StringProperty(name='Unity Project\'s Assets Path',
                                          subtype='DIR_PATH',
                                          description='The Unity Project\'s Assets folder. Needs to be '
                                                      'set for send to Unity',
                                          default='DEFAULT_STR')

    # Hierarchy Root to 0,0,0
    unity_bridge_zero_root_transform: BoolProperty(name = 'When enabled, sets the hierarchy root transforms to 0 upon export.',
                                                default = True)

    # Include animation
    unity_bridge_include_animation: BoolProperty(name = 'When enabled, includes animation in export.',
                                              default = False)

    axis_exp_lst = [('X', 'X', ''), ('Y', 'Y', ''), ('Z', 'Z', ''),
                    ('-X', '-X', ''), ('-Y', '-Y', ''), ('-Z', '-Z', '')]

    # Forward Axis
    unity_forward_axis: EnumProperty(name="Forward Axis",
                                     description="Defines the forward axis upon FBX Export (Unity).",
                                     items=axis_exp_lst,
                                     default='-Z'
                                     )

    # Up Axis
    unity_up_axis: EnumProperty(name="Up Axis",
                                     description="Defines the up axis upon FBX Export (Unity).",
                                     items=axis_exp_lst,
                                     default='Y'
                                     )

    # ------------------------------------------------------------------------------------------------------------------


def label_row(path, prop, row, label=''):
    row.label(text=label)
    row.prop(path, prop, text='')


def draw(preference, context, layout):

    # Lay out environment settings
    enable_rows = prefs().env.active_environment != 'default'

    # SEND ASSET HIERARCHIES TO UNREAL
    box = layout.box()
    column = box.column()
    row = column.row()
    row.enabled = enable_rows
    row.label(text="Send/Export Asset Hierarchies to Unreal")
    # General options
    match get_os():
        case OS.WIN:
            row = column.row()
            row.enabled = enable_rows
            row.prop(preference.environment, 'sc_path', text='Source Content')
            row = column.row()
            row.enabled = enable_rows
            row.prop(preference.environment, 'sc_path_alternate', text='Source Content (Alternate)')

        case OS.MAC:
            row = column.row()
            row.enabled = enable_rows
            row.prop(preference.environment, 'sc_path_mac', text='Source Content')
            row = column.row()
            row.enabled = enable_rows
            row.prop(preference.environment, 'sc_path_mac_alternate', text='Source Content (Alternate)')

        case OS.LINUX:
            row = column.row()
            row.enabled = enable_rows
            row.prop(preference.environment, 'sc_path_linux', text='Source Content')
            row = column.row()
            row.enabled = enable_rows
            row.prop(preference.environment, 'sc_path_linux_alternate', text='Source Content (Alternate)')

    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.general, 'ue_bridge_zero_root_transform', text='Zero Root Transform on Export')
    row.prop(preference.general, 'ue_bridge_include_animation', text='Include Animation')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.general, 'ue_automated', text='Automated Import')
    row.prop(preference.general, 'ue_import_textures', text='Import Textures')
    row.prop(preference.general, 'ue_import_materials', text='Import Materials')

    # EXPORTS: ASSET HIERARCHIES (UNITY)
    box = layout.box()
    column = box.column()
    row = column.row()
    row.enabled = enable_rows
    row.label(text="Send Asset Hierarchies to Unity")
    # General options
    row = column.row()
    row.enabled = enable_rows
    match get_os():
        case OS.WIN:
            row.prop(preference.environment, 'sc_path', text='Source Content')
            row.prop(preference.environment, 'sc_path_alternate', text='Source Content (Alternate)')
        case OS.MAC:
            row.prop(preference.environment, 'sc_path_mac', text='Source Content')
            row.prop(preference.environment, 'sc_path_mac_alternate', text='Source Content (Alternate)')
        case OS.LINUX:
            row.prop(preference.environment, 'sc_path_linux', text='Source Content')
            row.prop(preference.environment, 'sc_path_linux_alternate', text='Source Content (Alternate)')
    row = column.row()
    row.enabled = enable_rows
    match get_os():
        case OS.WIN:
            row.prop(preference.general, 'unity_assets_path', text='Unity Assets')
        case OS.MAC:
            row.prop(preference.general, 'unity_assets_path_mac', text='Unity Assets')
        case OS.LINUX:
            row.prop(preference.general, 'unity_assets_path_linux', text='Unity Assets')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.general, 'unity_bridge_zero_root_transform', text='Zero Root Transform on Export')
    row.prop(preference.general, 'unity_bridge_include_animation', text='Include Animation')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.general, 'unity_forward_axis', text='Forward Axis')
    row.prop(preference.general, 'unity_up_axis', text='Up Axis')

    # EXPORTS: BATCH SELECTION
    box = layout.box()
    column = box.column()
    row = column.row()
    row.enabled = enable_rows
    row.label(text='Export Batch Selection to FBX (ex. for SpeedTree Fronds)')
    row = column.row()
    row.enabled = enable_rows
    row.prop(preference.general, 'exp_select_zero_root_transform', text='Zero Root Transform on Export')
