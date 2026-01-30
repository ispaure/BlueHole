"""
This loads up the Blue Hole Preferences [Source Control] Section
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
# IMPORTS

import bpy
from bpy.props import *

import BlueHole.blenderUtils.filterUtils as filterUtils
from BlueHole.preferences.prefsCls import *


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

class bc(bpy.types.PropertyGroup):

    # Enable Source Control
    source_control_enable: BoolProperty(name = 'Enable Source Control',
                                       description = 'Enables Source Control through Blue Hole scripts',
                                       default = False)

    # Set Source Control Solution
    solution_lst = [('perforce', 'Perforce', ''), ('plastic-scm', 'Plastic SCM', ''), ('git', 'Git', '')]
    source_control_solution: EnumProperty(name="Solution",
                                     description="Defines the source control solution.",
                                     items=solution_lst,
                                     default='perforce'
                                     )

    # Abort Exports on Error
    source_control_error_aborts_exp: BoolProperty(name = 'Abort Exports on Error',
                                                      description = 'If there is a source control error during export'
                                                                    ', will abort said export',
                                                      default = True)

    # ------------------------------------------------------------------------------------------------------------------

    # Override Environment Settings Setting
    # Enable
    win32_env_override: BoolProperty(name = 'Override Environment Settings',
                                       description = 'When enabled, overrides Environment Settings set in P4V',
                                       default = False)

    # ------------------------------------------------------------------------------------------------------------------
    # OVERRIDE ENVIRONMENT SETTINGS - SINGLE USER
    # Override Environment Settings - Single User/Workspace (Windows)

    win32_env_setting_p4port: StringProperty(name = 'Server (P4PORT)',
                                             description = 'Set up environment setting override',
                                             default = '')

    win32_env_setting_p4user: StringProperty(name = 'User (P4USER)',
                                             description = 'Set up environment setting override',
                                             default = '')

    win32_env_setting_p4client: StringProperty(name = 'Workspace (P4CLIENT)',
                                             description = 'Set up environment setting override',
                                             default = '')

    # Override Environment Settings - Single User/Workspace (MacOS)
    macos_env_setting_p4port: StringProperty(name = 'Server (P4PORT)',
                                             description = 'Set up environment setting for MacOS here, since feature'
                                                           ' is missing from MacOS P4V app',
                                             default = '')

    macos_env_setting_p4user: StringProperty(name = 'User (P4USER)',
                                             description = 'Set up environment setting for MacOS here, since feature'
                                                           ' is missing from MacOS P4V app',
                                             default = '')

    macos_env_setting_p4client: StringProperty(name = 'Workspace (P4CLIENT)',
                                             description = 'Set up environment setting for MacOS here, since feature'
                                                           ' is missing from MacOS P4V app',
                                             default = '')


def label_row(path, prop, row, label=''):
    row.label(text=label)
    row.prop(path, prop, text='')


def draw(preference, context, layout):

    # Enable edits
    enable_rows = prefs().env.active_environment != 'default'

    box = layout.box()
    column = box.column()
    row = column.row()
    row.enabled = enable_rows
    row.label(text="Source Control")

    # # Enable Source Control
    row.alignment = 'LEFT'
    row.prop(preference.sourcecontrol, 'source_control_enable', text='Enable')

    if prefs().sc.source_control_enable:
        row.prop(preference.sourcecontrol, 'source_control_error_aborts_exp', text='Abort Exports on Error')
        row = column.row()
        row.enabled = enable_rows
        row.prop(preference.sourcecontrol, 'source_control_solution', text='Solution')

        # CREATE PERFORCE BOX WITH SETTINGS
        if prefs().sc.source_control_solution == 'perforce':
            box = layout.box()
            column = box.column()
            row = column.row()
            row.enabled = enable_rows
            row.label(text='Perforce')
            if filterUtils.filter_platform('win'):
                row.prop(preference.sourcecontrol, 'win32_env_override', text='Override P4V Environment Settings')

                if prefs().sc.win32_env_override:
                    row.prop(preference.sourcecontrol, 'override_mode', text='Override Mode')
                    row = column.row()
                    row.enabled = enable_rows
                    row.label(text="Override Environment Settings:")
                    row = column.row()
                    row.enabled = enable_rows
                    row.prop(preference.sourcecontrol, 'win32_env_setting_p4port', text='Server (P4PORT)')
                    if prefs().sc.override_mode == 'singleuser-workspace':
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'win32_env_setting_p4user', text='User (P4USER)')
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'win32_env_setting_p4client', text='Workspace (P4CLIENT)')
                        # Offer to Apply Override
                        row = column.row()
                        row.enabled = enable_rows
                        row.operator('wm.bh_set_p4_env_settings', text='Apply Override Settings')

            # Environment Settings Override (Impacts MacOS Only)
            if filterUtils.filter_platform('mac'):
                row = column.row()
                row.label(text="Environment Settings:")
                row = column.row()
                row.enabled = enable_rows
                row.prop(preference.sourcecontrol, 'macos_env_setting_p4port', text='Server (P4PORT)')
                row = column.row()
                row.enabled = enable_rows
                row.prop(preference.sourcecontrol, 'macos_env_setting_p4user', text='User (P4USER)')
                row = column.row()
                row.enabled = enable_rows
                row.prop(preference.sourcecontrol, 'macos_env_setting_p4client', text='Workspace (P4CLIENT)')
