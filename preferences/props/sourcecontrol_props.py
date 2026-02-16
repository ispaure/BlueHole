"""
This loads up the Blue Hole Preferences [Source Control] Section
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

class SourceControlPG(bpy.types.PropertyGroup):

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

    # Override Environment Settings - Single User/Workspace (MacOS)
    linux_env_setting_p4port: StringProperty(name = 'Server (P4PORT)',
                                             description = 'Set up environment setting for Linux here, since feature'
                                                           ' is missing from Linux P4V app',
                                             default = '')

    linux_env_setting_p4user: StringProperty(name = 'User (P4USER)',
                                             description = 'Set up environment setting for Linux here, since feature'
                                                           ' is missing from Linux P4V app',
                                             default = '')

    linux_env_setting_p4client: StringProperty(name = 'Workspace (P4CLIENT)',
                                             description = 'Set up environment setting for Linux here, since feature'
                                                           ' is missing from Linux P4V app',
                                             default = '')

    # ------------------------------------------------------------------------------------------------------------------
    # P4 PARALLEL PATH (FOR MAC AND LINUX)
    p4v_app_path_mac: StringProperty(name='p4v.app',
                                     subtype='FILE_PATH',
                                     description='The path to the "p4v.app" application, which is used to make calls to the Perforce server.',
                                     default='DEFAULT_STR')

    p4_parallel_path_linux: StringProperty(name='Perforce\'s p4_parallel path',
                                           subtype='FILE_PATH',
                                           description='The path to the "p4_parallel" file, which is the executable on Linux used to make calls to the Perforce server. It is located within the Perforce installation.',
                                           default='DEFAULT_STR')



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

            # Decide what to display (based on platform)
            match get_os():
                case OS.WIN:
                    p4_port_var_str = 'win32_env_setting_p4port'
                    p4_user_var_str = 'win32_env_setting_p4user'
                    p4_client_var_str = 'win32_env_setting_p4client'
                    p4_parallel_str = None
                    p4_parallel_name = None
                case OS.MAC:
                    p4_port_var_str = 'macos_env_setting_p4port'
                    p4_user_var_str = 'macos_env_setting_p4user'
                    p4_client_var_str = 'macos_env_setting_p4client'
                    p4_parallel_str = 'p4v_app_path_mac'
                    p4_parallel_name = 'p4v.app'
                case OS.LINUX:
                    p4_port_var_str = 'linux_env_setting_p4port'
                    p4_user_var_str = 'linux_env_setting_p4user'
                    p4_client_var_str = 'linux_env_setting_p4client'
                    p4_parallel_str = 'p4_parallel_path_linux'
                    p4_parallel_name = 'p4_parallel file'
                case _:
                    return

            # Display Row to override (not by default on Windows)
            if get_os() == OS.WIN:
                row.prop(preference.sourcecontrol, 'win32_env_override', text='Override P4V Environment Settings')

            # If Windows set to override or other platform, show fields
            if prefs().sc.win32_env_override or get_os() in [OS.MAC, OS.LINUX]:
                row = column.row()
                row.label(text=f"Environment Settings [{get_os().value}]:")
                row = column.row()
                row.enabled = enable_rows
                row.prop(preference.sourcecontrol, p4_port_var_str, text='Server (P4PORT)')
                row = column.row()
                row.enabled = enable_rows
                row.prop(preference.sourcecontrol, p4_user_var_str, text='User (P4USER)')
                row = column.row()
                row.enabled = enable_rows
                row.prop(preference.sourcecontrol, p4_client_var_str, text='Workspace (P4CLIENT)')

            # If macOS or Linux, p4_parallel path
            if get_os() in [OS.MAC, OS.LINUX]:
                row = column.row()
                row.enabled = enable_rows
                row.prop(preference.sourcecontrol, p4_parallel_str, text=p4_parallel_name)
