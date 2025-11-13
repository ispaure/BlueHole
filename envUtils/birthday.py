"""
This will display a Happy Birthday message
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

from datetime import date

from BlueHole.blenderUtils.configUtils import get_current_env_cfg_value as get_current_env_cfg_value
from BlueHole.blenderUtils.debugUtils import print_debug_msg as print_debug_msg
from BlueHole.blenderUtils.uiUtils import show_dialog_box as show_dialog_box


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

def happy_birthday_calendar():
    birthday_info_lst = get_current_env_cfg_value('BirthdayCalendar', 'birthdays').split(',\n')
    birthday_info_dict = {}
    for birthday_info in birthday_info_lst:
        birthday_info_dict[birthday_info.split(':')[0]] = birthday_info.split(':')[-1].split('-')
    print_debug_msg('Birthday info dict: ' + str(birthday_info_dict), show_verbose)
    print_debug_msg('Date today: ' + str(date.today()), show_verbose)
    for key, value in birthday_info_dict.items():
        if value[1] + '-' + value[2] == str(date.today())[5:]:
            if value[0] == 'en':
                show_dialog_box('Happy Birthday!', 'Happy Birthday ' + key + '!' + ' Have a wonderful day. :)')
            elif value[0] == 'fr':
                show_dialog_box('Bonne fête ', 'Bonne fête ' + key + '!' + ' Passe une belle journée. :)')
            elif value[0] == 'jp':
                show_dialog_box('お誕生日おめでとう！', '' + key + '!' + ' お誕生日おめでとうございます :)')
