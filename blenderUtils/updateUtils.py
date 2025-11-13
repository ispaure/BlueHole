"""
Scripts to update Blue Hole (download or upload) to Dropbox cloud service.
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

from pathlib import Path
import os

import BlueHole.blenderUtils.fileUtils as fileUtils
import BlueHole.blenderUtils.filterUtils as filterUtils
import BlueHole.blenderUtils.uiUtils as uiUtils
from BlueHole.blenderUtils.debugUtils import print_debug_msg as print_debug_msg
import BlueHole.blenderUtils.addon as addon
import BlueHole.blenderUtils.configUtils as configUtils
import BlueHole.envUtils.envUtils as envUtils
import datetime
from datetime import date

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

# ----------------------------------------------------------------------------------------------------------------------
# DEFINE UPDATE PRESETS

# Addon-Only Update Preset
addon_only_update_preset = ['Addon-Only Edition',
                            False,
                            {'Addon': ['scripts/addons/BlueHole',
                                       'mainline/bh_addon.zip',
                                       configUtils.get_url_db_value('Update-Mainline', 'bh_addon')]}]


# Addon-Only (Beta) Update Preset
addon_only_beta_update_preset = ['Addon-Only Edition (Beta)',
                                 True,
                                 {'Addon': ['scripts/addons/BlueHole',
                                            'beta/bh_addon.zip',
                                            configUtils.get_url_db_value('Update-Mainline', 'bh_addon')]}]

# Deluxe Update Preset
deluxe_update_preset = ['Deluxe Edition',
                        False,
                        {'Addon': ['scripts/addons/BlueHole',
                                   'mainline/bh_addon.zip',
                                   configUtils.get_url_db_value('Update-Mainline', 'bh_addon')],
                         'Startup Blend File': ['config/startup.blend',
                                                'mainline/startup.blend',
                                                configUtils.get_url_db_value('Update-Mainline', 'startup_blend')],
                         'Userpref Blend File': ['config/userpref.blend',
                                                 'mainline/userpref.blend',
                                                 configUtils.get_url_db_value('Update-Mainline', 'userpref_blend')],
                         'Hotkeys Blend File': ['scripts/presets/keyconfig',
                                                'mainline/hotkeys.zip',
                                                configUtils.get_url_db_value('Update-Mainline', 'hotkeys_blend')],
                         'MACHIN3tools': ['scripts/addons/MACHIN3tools',
                                          'mainline/MACHIN3tools.zip',
                                          configUtils.get_url_db_value('Update-Mainline', 'machin3')],
                         'TimeStamp': ['scripts/addons/BlueHole/timestamp.txt',
                                       'mainline/timestamp.txt',
                                       configUtils.get_url_db_value('Update-Mainline', 'timestamp')],
                         'interactivetoolsblender-master': ['scripts/addons/interactivetoolsblender-master',
                                                            'mainline/interactivetoolsblender-master.zip',
                                                            configUtils.get_url_db_value('Update-Mainline', 'interactivetoolsblender-master')]
                         }]

# Deluxe (Beta) Update Preset
deluxe_beta_update_preset = ['Deluxe Edition (Beta)',
                             True,
                             {'Addon': ['scripts/addons/BlueHole',
                                        'beta/bh_addon.zip',
                                        configUtils.get_url_db_value('Update-Beta', 'bh_addon')],
                              'Startup Blend File': ['config/startup.blend',
                                                     'beta/startup.blend',
                                                     configUtils.get_url_db_value('Update-Beta', 'startup_blend')],
                              'Userpref Blend File': ['config/userpref.blend',
                                                      'beta/userpref.blend',
                                                      configUtils.get_url_db_value('Update-Beta', 'userpref_blend')],
                              'Hotkeys Blend File': ['scripts/presets/keyconfig',
                                                     'beta/hotkeys.zip',
                                                     configUtils.get_url_db_value('Update-Beta', 'hotkeys_blend')],
                              'MACHIN3tools': ['scripts/addons/MACHIN3tools',
                                               'beta/MACHIN3tools.zip',
                                               configUtils.get_url_db_value('Update-Beta', 'machin3')],
                              'TimeStamp': ['scripts/addons/BlueHole/timestamp.txt',
                                            'beta/timestamp.txt',
                                            configUtils.get_url_db_value('Update-Beta', 'timestamp')],
                              'interactivetoolsblender-master': ['scripts/addons/interactivetoolsblender-master',
                                                                 'beta/interactivetoolsblender-master.zip',
                                                                 configUtils.get_url_db_value('Update-Beta', 'interactivetoolsblender-master')]
                              }]


# Update Presets List (Add variables for presets right above here)
update_preset_lst = [addon_only_update_preset,
                     addon_only_beta_update_preset,
                     deluxe_update_preset,
                     deluxe_beta_update_preset]

# ----------------------------------------------------------------------------------------------------------------------
# Define Cloud path (for pushing updates)
cloud_path_win32 = 'C:\\Users\\marca\\Yagi Dropbox\\Marc-Andre Voyer\\Shared\\Blue Hole'
cloud_path_macos = '/Users/marca/Yagi Dropbox/Marc-Andre Voyer/Shared/Blue Hole'
# ----------------------------------------------------------------------------------------------------------------------


# # Defines the addon versions
# class AddonVersion:
#     def __init__(self):
#         self.version_id = ''
#         self.beta = False
#         # Blue Hole Package Items
#         self.pkg_items = {}


def get_addon_version_dict():
    """
    Create an addon version class from given parameters. Used to push or pull an update.
    """
    addon_version_dict = {}
    for update_preset in update_preset_lst:
        # Create a new key with info
        addon_version_dict[update_preset[0]] = [update_preset[1], update_preset[2]]

    return addon_version_dict


def check_update():
    """
    Checks if Blue Hole Blender Addon is up to date, and if can be updated.
    :return:
    """
    # Debug message
    msg = '\n\nForce check for Blue Hole Update...'
    print_debug_msg(msg, show_verbose)

    # Define which version is currently installed
    print_debug_msg('Checking which Blue Hole version is installed; Deluxe or Addon-Only', show_verbose)
    is_deluxe = addon.preference().help_n_update.update_version == 'Deluxe'
    if is_deluxe:
        print_debug_msg('Blue Hole Deluxe detected!', show_verbose)
    else:
        print_debug_msg('Blue Hole Addon-Only detected!', show_verbose)

    # Local timestamp path
    local_timestamp_path = fileUtils.get_blue_hole_user_addon_path() + '/timestamp.txt'
    # Website timestamp path
    website_timestamp_path = fileUtils.get_blue_hole_user_addon_path() + '/timestamp_website.txt'

    # Download timestamp file from Dropbox (mainline)
    fileUtils.download_dropbox_file(deluxe_update_preset[2]['TimeStamp'][2], website_timestamp_path)

    # Get local time
    with open(local_timestamp_path) as file:
        local_time = file.readlines()[0]

    # Get website time
    with open(website_timestamp_path) as file:
        website_time = file.readlines()[0]

    print_debug_msg('Local Time: ' + local_time, show_verbose)
    print_debug_msg('Website Time: ' + website_time, show_verbose)

    if int(website_time) > int(local_time):
        print_debug_msg('Website has newer version, triggering update process...', show_verbose)
        if is_deluxe:
            install_addon_update('Deluxe Edition', auto=True)
        else:
            install_addon_update('Addon-Only Edition', auto=True)
    else:
        print_debug_msg('Website does not have newer version, do not proceed with update', show_verbose)


def create_timestamp():
    """
    Creates a .txt file with a timestamp within the plugin/addon
    """

    # Timestamp file path
    timestamp_path = str(Path(fileUtils.get_blue_hole_user_addon_path() + '/timestamp.txt'))

    # Get current time
    current_time = int(datetime.datetime.utcnow().timestamp())

    # Remove existing timestamp file
    os.remove(timestamp_path)

    # Create new timestamp file
    with open(timestamp_path, 'a') as f:
        f.write(str(current_time))


def upload_addon_update(beta=False):
    """
    Main function to update the Blue Hole Blender Addon.
    """

    # Prompt for confirmation
    if beta:
        version = 'Beta'
    else:
        version = 'Mainline'
    msg = 'You are about to upload Blue Hole ' + version + ' to the Cloud. Press OK to confirm.'
    result = uiUtils.show_dialog_box('Blue Hole Upload Update', msg)

    # User Accepted Prompt
    if result:

        # Create or update timestamp file in addon
        create_timestamp()

        # Move other environments out of the way
        env_dict = envUtils.get_env_dict()
        temp_folder = fileUtils.get_resource_path_user() + '/temp'
        Path(temp_folder).mkdir(parents=True, exist_ok=True)
        moved_lst = []
        for key, value in env_dict.items():
            if 'default' not in key:
                if fileUtils.get_resource_path_user() in value:
                    source = value
                    destination = temp_folder + '/' + key
                    fileUtils.copy_dir(source, destination)
                    fileUtils.delete_dir(source)
                    moved_lst.append([source, destination])

        # List of source-destination for upload
        source_dest_lst = []

        # Get list of source/destination with matching version (mainline or beta)
        for key, value in get_addon_version_dict().items():
            msg = '\nLooking if update preset "' + key + '" matches upload parameter.'
            print_debug_msg(msg, show_verbose)
            if beta == value[0]:
                print_debug_msg('Preset matches upload parameter.', show_verbose)
                print_debug_msg('Gathering sources and destinations...', show_verbose)
                for copy_item_key, copy_item_value in value[1].items():
                    print_debug_msg('Name of item to copy: ' + copy_item_key, show_verbose)

                    # Get absolute source path
                    source_pth = str(Path(fileUtils.get_resource_path_user() + '/' + copy_item_value[0]))

                    # Get absolute destination path
                    if filterUtils.filter_platform('win'):
                        dest_pth = str(Path(cloud_path_win32 + '/' + copy_item_value[1]))
                    elif filterUtils.filter_platform('mac'):
                        dest_pth = str(Path(cloud_path_macos + '/' + copy_item_value[1]))
                    else:
                        print('Fatal Error: Did not account for non Windows or Mac OS.')
                        dest_pth = None

                    print_debug_msg('Source Path (Absolute): ' + source_pth, show_verbose)
                    print_debug_msg('Destination (Absolute): ' + dest_pth, show_verbose)

                    # If entry already there, do not add to list.
                    already_there = False
                    for source_dest in source_dest_lst:
                        if source_dest[0] == source_pth:
                            already_there = True

                    if not already_there:
                        source_dest_lst.append([source_pth, dest_pth])
            else:
                print_debug_msg('Preset does not match upload parameter.', show_verbose)

        # Send files to cloud
        for source_dest in source_dest_lst:
            print_debug_msg('Transferring source: "' + source_dest[0] + '" to destination: "' + source_dest[1] + '".', show_verbose)

            # If it's a file, copy.
            if os.path.isfile(source_dest[0]):
                fileUtils.copy_file(source_dest[0], source_dest[1])
            # If it's a directory, compress.
            else:
                fileUtils.zip_file(source_dest[0], source_dest[1])

        # If was mainline, make a copy of bh_addon.zip in previous version folder
        if not beta:
            time_given = str(date.today()).replace('/', '-')
            if filterUtils.filter_platform('win'):
                fileUtils.copy_file(cloud_path_win32 + '\\mainline\\bh_addon.zip', cloud_path_win32 +
                                    '\\mainline\\previous_versions\\bh_addon_' + time_given + '.zip')
            elif filterUtils.filter_platform('mac'):
                fileUtils.copy_file(cloud_path_macos + '/mainline/bh_addon.zip', cloud_path_macos +
                                    '/mainline/previous_versions/bh_addon_' + time_given + '.zip')

        # Put back environments where they go
        for moved in moved_lst:
            fileUtils.copy_dir(moved[1], moved[0])
            fileUtils.delete_dir(moved[1])

        # Show process is completed.
        return True

    # User Declined Prompt, Cancelling Update/Upload
    else:
        uiUtils.show_dialog_box('Blue Hole Upload Update', 'Update Cancelled!')
        return False


def install_addon_update(version_id, auto=False):
    """
    Main function to update the Blue Hole Blender Addon.
    :param version_id: Version to update.
    """
    # Get Relevant Update Preset
    addon_preset = get_addon_version_dict()[version_id]

    # Prompt for confirmation
    if auto:
        msg = 'A new version of Blue Hole ' + version_id + ' is available from the website. If you wish, you can ' \
                                                           'update now. Please do not close Blender during the ' \
                                                           'update process. ' \
                                                           '\nYou will be notified when the update is completed.' \
                                                           '\nPress OK if you wish to proceed with the update.'
    else:
        msg = 'You are about to update Blue Hole ' + version_id + '. Please do not close Blender during the update ' \
                                                              'process.' \
                                                              '\nYou will be notified when the update is complete.' \
                                                              '\nPress OK to Continue.'
    result = uiUtils.show_dialog_box('Blue Hole Upload Update', msg)

    if result:
        # Download Files from Dropbox
        print_debug_msg('Downloading update files...', show_verbose)
        for key, value in addon_preset[1].items():

            # DETERMINE DOWNLOAD DESTINATION DIRECTORY AND FILE PATH

            # Base Path (Blender preferences)
            base_path = fileUtils.get_resource_path_user()

            # Download Path
            download_destination_path = str(Path(base_path + '/' + value[0]))

            # Download File Name
            if filterUtils.filter_platform('win'):
                dl_file_name = download_destination_path.split('\\')[-1]
            elif filterUtils.filter_platform('mac'):
                dl_file_name = download_destination_path.split('/')[-1]
            else:
                print_debug_msg('Critical error! OS is not supported', show_verbose)
                return False

            # If target destination doesn't have an extension, it means we're dealing with compressed folder in zip
            # file. So we need to add the extension to it
            if '.' not in dl_file_name:
                download_destination_path += '.zip'

            # Download directory. Just need to remove the file name.
            download_destination_dir = ''

            if filterUtils.filter_platform('win'):
                download_destination_dir_lst = download_destination_path.split('\\')[:-1]
                for item in download_destination_dir_lst:
                    download_destination_dir += item
                    download_destination_dir += '\\'

            elif filterUtils.filter_platform('mac'):
                download_destination_dir_lst = download_destination_path.split('/')[:-1]
                for item in download_destination_dir_lst:
                    download_destination_dir += item
                    download_destination_dir += '/'
            else:
                print_debug_msg('Critical error! OS is not supported', show_verbose)
                return False

            # If folder path hadn't been created already, make it.
            # Useful in preventing bugs where user haven't created their folders yet.
            Path(download_destination_dir).mkdir(parents=True, exist_ok=True)

            # Download file to path
            try:
                fileUtils.download_dropbox_file(value[2], download_destination_path)
                # If file is .zip, extract to proper location
                if download_destination_path[-4:] == '.zip':
                    print_debug_msg('This is ZIP! Extracting...', show_verbose)
                    fileUtils.unzip_file(download_destination_path, download_destination_dir)
            except:
                msg = 'Blue Hole could not be updated successfully. Please reinstall from the official website: ' \
                      '\n\nblue-hole.weebly.com'
                uiUtils.show_dialog_box('Blue Hole', msg)

        # Prompt for confirmation
        msg = 'Blue Hole has been updated to: ' + version_id + '. Please restart Blender for changes to take effect!'
        uiUtils.show_dialog_box('Blue Hole Update', msg)
