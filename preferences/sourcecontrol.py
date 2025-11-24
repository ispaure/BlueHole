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

import bpy
from bpy.props import *

import BlueHole.blenderUtils.addon as addon
import BlueHole.blenderUtils.filterUtils as filterUtils


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
    # Type
    override_modes = [('singleuser-workspace', 'Single User/Workspace', ''), ('multiuser-workspace', 'Multi User/Workspace', '')]
    override_mode: EnumProperty(name="Override Mode",
                                description="Defines the type of override. Single is for a single user/workspace and multi allows for multiple users/workspace based on computer names.",
                                items=override_modes,
                                default='singleuser-workspace')

    # ------------------------------------------------------------------------------------------------------------------
    # OVERRIDE ENVIRONMENT SETTINGS - SINGLE USER
    # Override Environment Settings - Single User/Workspace (Windows)

    win32_env_setting_P4PORT: StringProperty(name = 'Server (P4PORT)',
                                             description = 'Set up environment setting override',
                                             default = '')

    win32_env_setting_P4USER: StringProperty(name = 'User (P4USER)',
                                             description = 'Set up environment setting override',
                                             default = '')

    win32_env_setting_P4CLIENT: StringProperty(name = 'Workspace (P4CLIENT)',
                                             description = 'Set up environment setting override',
                                             default = '')

    # Override Environment Settings - Single User/Workspace (MacOS)
    macos_env_setting_P4PORT: StringProperty(name = 'Server (P4PORT)',
                                             description = 'Set up environment setting for MacOS here, since feature'
                                                           ' is missing from MacOS P4V app',
                                             default = '')

    macos_env_setting_P4USER: StringProperty(name = 'User (P4USER)',
                                             description = 'Set up environment setting for MacOS here, since feature'
                                                           ' is missing from MacOS P4V app',
                                             default = '')

    macos_env_setting_P4CLIENT: StringProperty(name = 'Workspace (P4CLIENT)',
                                             description = 'Set up environment setting for MacOS here, since feature'
                                                           ' is missing from MacOS P4V app',
                                             default = '')

    # ------------------------------------------------------------------------------------------------------------------
    # OVERRIDE ENVIRONMENT SETTINGS - MULTI USER

    # USER 01
    env_setting_user01_computername: StringProperty(name = 'Computer Name',
                                                    description = 'Computer name for that user',
                                                    default = '')

    env_setting_user01_user: StringProperty(name = 'User',
                                                    description = 'Perforce username',
                                                    default = '')

    env_setting_user01_workspace: StringProperty(name = 'Workspace',
                                                    description = 'Perforce workspace name',
                                                    default = '')

    # USER 02
    env_setting_user02_computername: StringProperty(name = 'Computer Name',
                                                    description = 'Computer name for that user',
                                                    default = '')

    env_setting_user02_user: StringProperty(name='User',
                                            description='Perforce username',
                                            default='')

    env_setting_user02_workspace: StringProperty(name='Workspace',
                                                 description='Perforce workspace name',
                                                 default='')

    # USER 03
    env_setting_user03_computername: StringProperty(name = 'Computer Name',
                                                    description = 'Computer name for that user',
                                                    default = '')

    env_setting_user03_user: StringProperty(name='User',
                                            description='Perforce username',
                                            default='')

    env_setting_user03_workspace: StringProperty(name='Workspace',
                                                 description='Perforce workspace name',
                                                 default='')

    # USER 04
    env_setting_user04_computername: StringProperty(name = 'Computer Name',
                                                    description = 'Computer name for that user',
                                                    default = '')

    env_setting_user04_user: StringProperty(name='User',
                                            description='Perforce username',
                                            default='')

    env_setting_user04_workspace: StringProperty(name='Workspace',
                                                 description='Perforce workspace name',
                                                 default='')

    # USER 05
    env_setting_user05_computername: StringProperty(name = 'Computer Name',
                                                    description = 'Computer name for that user',
                                                    default = '')

    env_setting_user05_user: StringProperty(name='User',
                                            description='Perforce username',
                                            default='')

    env_setting_user05_workspace: StringProperty(name='Workspace',
                                                 description='Perforce workspace name',
                                                 default='')

    # USER 06
    env_setting_user06_computername: StringProperty(name = 'Computer Name',
                                                    description = 'Computer name for that user',
                                                    default = '')

    env_setting_user06_user: StringProperty(name='User',
                                            description='Perforce username',
                                            default='')

    env_setting_user06_workspace: StringProperty(name='Workspace',
                                                 description='Perforce workspace name',
                                                 default='')

    # USER 07
    env_setting_user07_computername: StringProperty(name = 'Computer Name',
                                                    description = 'Computer name for that user',
                                                    default = '')

    env_setting_user07_user: StringProperty(name='User',
                                            description='Perforce username',
                                            default='')

    env_setting_user07_workspace: StringProperty(name='Workspace',
                                                 description='Perforce workspace name',
                                                 default='')

    # USER 08
    env_setting_user08_computername: StringProperty(name = 'Computer Name',
                                                    description = 'Computer name for that user',
                                                    default = '')

    env_setting_user08_user: StringProperty(name='User',
                                            description='Perforce username',
                                            default='')

    env_setting_user08_workspace: StringProperty(name='Workspace',
                                                 description='Perforce workspace name',
                                                 default='')

    # USER 09
    env_setting_user09_computername: StringProperty(name = 'Computer Name',
                                                    description = 'Computer name for that user',
                                                    default = '')

    env_setting_user09_user: StringProperty(name='User',
                                            description='Perforce username',
                                            default='')

    env_setting_user09_workspace: StringProperty(name='Workspace',
                                                 description='Perforce workspace name',
                                                 default='')

    # USER 10
    env_setting_user10_computername: StringProperty(name = 'Computer Name',
                                                    description = 'Computer name for that user',
                                                    default = '')

    env_setting_user10_user: StringProperty(name='User',
                                            description='Perforce username',
                                            default='')

    env_setting_user10_workspace: StringProperty(name='Workspace',
                                                 description='Perforce workspace name',
                                                 default='')

    # USER 11
    env_setting_user11_computername: StringProperty(name = 'Computer Name',
                                                    description = 'Computer name for that user',
                                                    default = '')

    env_setting_user11_user: StringProperty(name='User',
                                            description='Perforce username',
                                            default='')

    env_setting_user11_workspace: StringProperty(name='Workspace',
                                                 description='Perforce workspace name',
                                                 default='')

    # USER 12
    env_setting_user12_computername: StringProperty(name = 'Computer Name',
                                                    description = 'Computer name for that user',
                                                    default = '')

    env_setting_user12_user: StringProperty(name='User',
                                            description='Perforce username',
                                            default='')

    env_setting_user12_workspace: StringProperty(name='Workspace',
                                                 description='Perforce workspace name',
                                                 default='')

    # USER 13
    env_setting_user13_computername: StringProperty(name = 'Computer Name',
                                                    description = 'Computer name for that user',
                                                    default = '')

    env_setting_user13_user: StringProperty(name='User',
                                            description='Perforce username',
                                            default='')

    env_setting_user13_workspace: StringProperty(name='Workspace',
                                                 description='Perforce workspace name',
                                                 default='')

    # USER 14
    env_setting_user14_computername: StringProperty(name = 'Computer Name',
                                                    description = 'Computer name for that user',
                                                    default = '')

    env_setting_user14_user: StringProperty(name='User',
                                            description='Perforce username',
                                            default='')

    env_setting_user14_workspace: StringProperty(name='Workspace',
                                                 description='Perforce workspace name',
                                                 default='')

    # USER 15
    env_setting_user15_computername: StringProperty(name = 'Computer Name',
                                                    description = 'Computer name for that user',
                                                    default = '')

    env_setting_user15_user: StringProperty(name='User',
                                            description='Perforce username',
                                            default='')

    env_setting_user15_workspace: StringProperty(name='Workspace',
                                                 description='Perforce workspace name',
                                                 default='')



def label_row(path, prop, row, label=''):
    row.label(text=label)
    row.prop(path, prop, text='')


def draw(preference, context, layout):

    # Enable edits
    enable_rows = addon.preference().environment.active_environment != 'default'

    box = layout.box()
    column = box.column()
    row = column.row()
    row.enabled = enable_rows
    row.label(text="Source Control")

    # # Enable Source Control
    row.alignment = 'LEFT'
    row.prop(preference.sourcecontrol, 'source_control_enable', text='Enable')

    if addon.preference().sourcecontrol.source_control_enable:
        row.prop(preference.sourcecontrol, 'source_control_error_aborts_exp', text='Abort Exports on Error')
        row = column.row()
        row.enabled = enable_rows
        row.prop(preference.sourcecontrol, 'source_control_solution', text='Solution')

        # CREATE PERFORCE BOX WITH SETTINGS
        if addon.preference().sourcecontrol.source_control_solution == 'perforce':
            box = layout.box()
            column = box.column()
            row = column.row()
            row.enabled = enable_rows
            row.label(text='Perforce')
            if filterUtils.filter_platform('win'):
                row.prop(preference.sourcecontrol, 'win32_env_override', text='Override P4V Environment Settings')

                if addon.preference().sourcecontrol.win32_env_override:
                    row.prop(preference.sourcecontrol, 'override_mode', text='Override Mode')
                    row = column.row()
                    row.enabled = enable_rows
                    row.label(text="Override Environment Settings:")
                    row = column.row()
                    row.enabled = enable_rows
                    row.prop(preference.sourcecontrol, 'win32_env_setting_P4PORT', text='Server (P4PORT)')
                    if addon.preference().sourcecontrol.override_mode == 'singleuser-workspace':
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'win32_env_setting_P4USER', text='User (P4USER)')
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'win32_env_setting_P4CLIENT', text='Workspace (P4CLIENT)')
                        # Offer to Apply Override
                        row = column.row()
                        row.enabled = enable_rows
                        row.operator('wm.bh_set_p4_env_settings', text='Apply Override Settings')
                    elif addon.preference().sourcecontrol.override_mode == 'multiuser-workspace':
                        row = column.row()
                        row.enabled = enable_rows
                        row.label(text="Users:")

                        # List all users and settings
                        #User-01
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'env_setting_user01_computername', text='Computer Name')
                        row.prop(preference.sourcecontrol, 'env_setting_user01_user', text='User')
                        row.prop(preference.sourcecontrol, 'env_setting_user01_workspace', text='Workspace')
                        #User-02
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'env_setting_user02_computername', text='Computer Name')
                        row.prop(preference.sourcecontrol, 'env_setting_user02_user', text='User')
                        row.prop(preference.sourcecontrol, 'env_setting_user02_workspace', text='Workspace')
                        #User-03
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'env_setting_user03_computername', text='Computer Name')
                        row.prop(preference.sourcecontrol, 'env_setting_user03_user', text='User')
                        row.prop(preference.sourcecontrol, 'env_setting_user03_workspace', text='Workspace')
                        #User-04
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'env_setting_user04_computername', text='Computer Name')
                        row.prop(preference.sourcecontrol, 'env_setting_user04_user', text='User')
                        row.prop(preference.sourcecontrol, 'env_setting_user04_workspace', text='Workspace')
                        #User-05
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'env_setting_user05_computername', text='Computer Name')
                        row.prop(preference.sourcecontrol, 'env_setting_user05_user', text='User')
                        row.prop(preference.sourcecontrol, 'env_setting_user05_workspace', text='Workspace')
                        #User-06
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'env_setting_user06_computername', text='Computer Name')
                        row.prop(preference.sourcecontrol, 'env_setting_user06_user', text='User')
                        row.prop(preference.sourcecontrol, 'env_setting_user06_workspace', text='Workspace')
                        #User-07
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'env_setting_user07_computername', text='Computer Name')
                        row.prop(preference.sourcecontrol, 'env_setting_user07_user', text='User')
                        row.prop(preference.sourcecontrol, 'env_setting_user07_workspace', text='Workspace')
                        #User-08
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'env_setting_user08_computername', text='Computer Name')
                        row.prop(preference.sourcecontrol, 'env_setting_user08_user', text='User')
                        row.prop(preference.sourcecontrol, 'env_setting_user08_workspace', text='Workspace')
                        #User-09
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'env_setting_user09_computername', text='Computer Name')
                        row.prop(preference.sourcecontrol, 'env_setting_user09_user', text='User')
                        row.prop(preference.sourcecontrol, 'env_setting_user09_workspace', text='Workspace')
                        #User-10
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'env_setting_user10_computername', text='Computer Name')
                        row.prop(preference.sourcecontrol, 'env_setting_user10_user', text='User')
                        row.prop(preference.sourcecontrol, 'env_setting_user10_workspace', text='Workspace')
                        #User-11
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'env_setting_user11_computername', text='Computer Name')
                        row.prop(preference.sourcecontrol, 'env_setting_user11_user', text='User')
                        row.prop(preference.sourcecontrol, 'env_setting_user11_workspace', text='Workspace')
                        #User-12
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'env_setting_user12_computername', text='Computer Name')
                        row.prop(preference.sourcecontrol, 'env_setting_user12_user', text='User')
                        row.prop(preference.sourcecontrol, 'env_setting_user12_workspace', text='Workspace')
                        #User-13
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'env_setting_user13_computername', text='Computer Name')
                        row.prop(preference.sourcecontrol, 'env_setting_user13_user', text='User')
                        row.prop(preference.sourcecontrol, 'env_setting_user13_workspace', text='Workspace')
                        #User-14
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'env_setting_user14_computername', text='Computer Name')
                        row.prop(preference.sourcecontrol, 'env_setting_user14_user', text='User')
                        row.prop(preference.sourcecontrol, 'env_setting_user14_workspace', text='Workspace')
                        #User-15
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.sourcecontrol, 'env_setting_user15_computername', text='Computer Name')
                        row.prop(preference.sourcecontrol, 'env_setting_user15_user', text='User')
                        row.prop(preference.sourcecontrol, 'env_setting_user15_workspace', text='Workspace')


            # Environment Settings Override (Impacts MacOS Only)
            if filterUtils.filter_platform('mac'):
                row = column.row()
                row.label(text="Environment Settings:")
                row = column.row()
                row.enabled = enable_rows
                row.prop(preference.sourcecontrol, 'macos_env_setting_P4PORT', text='Server (P4PORT)')
                row = column.row()
                row.enabled = enable_rows
                row.prop(preference.sourcecontrol, 'macos_env_setting_P4USER', text='User (P4USER)')
                row = column.row()
                row.enabled = enable_rows
                row.prop(preference.sourcecontrol, 'macos_env_setting_P4CLIENT', text='Workspace (P4CLIENT)')
