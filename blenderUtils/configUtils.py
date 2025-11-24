"""
Blue Hole functions to read through Sections & Values from a config (.ini) file.
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

import configparser

import BlueHole.blenderUtils.fileUtils as fileUtils
import BlueHole.blenderUtils.uiUtils as uiUtils
from BlueHole.blenderUtils.debugUtils import *


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True
name = filename = os.path.basename(__file__)

# ----------------------------------------------------------------------------------------------------------------------
# CODE

def config_section_map(section, value, cfg_file_path):
    """
    Retrieve a value from a section of a config file.
    :param section: Name of section in which the value you want is found.
    :type section: str
    :param value: Name of the value you want to get as return
    :type value: str
    :param cfg_file_path: Path to the config file to look into
    :type cfg_file_path: str
    :rtype: str
    """
    # Read config file
    config = configparser.ConfigParser(interpolation=None)
    env_config_filepath = cfg_file_path  # Get path of current env config file
    config.read(env_config_filepath)
    config.sections()

    # Retrieve dict
    dict1 = {}
    try:
        options = config.options(section)
    except:
        return None
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    if value in dict1.keys():
        return dict1[value]
    else:
        return None


# TODO: Optimize batching of checks; create class where it only re-triggers file read when I want, so it can get through testing many fields much more quickly.
def config_add_variable(section, variable, value, cfg_file_path):
    """
    Expects variable to not be there already.
    Adds a variable to a config file and sets its value. If required, add its section.
    :param section: Expected section for value
    :type section: str
    :param variable: Variable to create in section
    :type variable: str
    :param value: Value for the variable
    :type value: str
    :param cfg_file_path: Path of the config file
    :type cfg_file_path: str
    """

    # Read the lines from the config file and store in a list
    lines_lst = fileUtils.read_file(cfg_file_path)

    # See if the section is already there
    section_is_there = False
    for line in lines_lst:
        if '[{section}]'.format(section=section) in line:
            section_is_there = True
            break

    # Make list for new lines
    new_lines_lst = []

    # Make new lines to add
    section_line_to_add = '[{section}]'.format(section=section)
    variable_line_to_add = variable + ' = ' + value

    # If section was there, add a line after the section with new variable and value
    if section_is_there:
        for line in lines_lst:
            new_lines_lst.append(line)
            if section_line_to_add in line:
                new_lines_lst.append(variable_line_to_add)
    else:
        # Add the existing lines first
        new_lines_lst = lines_lst
        # At the end, add the new section
        new_lines_lst.append('\n' + section_line_to_add)
        # After, add its variable and value
        new_lines_lst.append(variable_line_to_add)

    # Write the result to the file
    file = open(cfg_file_path, 'w')
    for line in new_lines_lst:
        file.write(line + '\n')
    file.close()


def config_set_variable(section, variable, value, cfg_file_path):
    """
    Expects file to already have the section and variable. It just needs to be set to new value
    """

    # Read the lines from the config file and store in a list
    lines_lst = fileUtils.read_file(cfg_file_path)

    # Make list for new lines
    new_lines_lst = []

    # Determine key lines
    section_line = '[{section}]'.format(section=section)
    variable_line_to_set = variable + ' ='

    in_good_section = False
    for line in lines_lst:
        line_appended_this_round = False
        if section_line in line:
            in_good_section = True
        if in_good_section:
            if variable_line_to_set in line:
                new_lines_lst.append(variable_line_to_set + ' ' + value)
                in_good_section = False
                line_appended_this_round = True
        if not line_appended_this_round:
            new_lines_lst.append(line)

    # Write the result to the file
    file = open(cfg_file_path, 'w')
    for line in new_lines_lst:
        file.write(line + '\n')
    file.close()


def get_current_env_cfg_value(section, value):
    """
    Retrieve a value from the current environment config file. If value not stored in file, use the one from the default
    :param section: Name of section in which the value you want is found.
    :type section: str
    :param value: Name of the value you want to get as return
    :type value: str
    :rtype: str
    """
    return_value = config_section_map(section, value, fileUtils.get_current_env_var_path())
    if return_value is not None:
        return return_value
    else:
        return_value = config_section_map(section, value, fileUtils.get_default_env_var_path())
        if return_value is None:
            msg = 'Could not find value {value} in section {section} in either the current env config file or the ' \
                  'default. Please add missing value to one of those files.'.format(value=value, section=section)
            log(Severity.ERROR, name, msg, popup=True)
        return return_value


def get_url_db_value(section, value):
    """
    Retrieve a value from Blue Hole's URL database file
    """
    return config_section_map(section, value, fileUtils.get_bh_url_db_file_path())
