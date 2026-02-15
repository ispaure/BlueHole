"""
Blue Hole functions to read through Sections & Values from a config (.ini) file.
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

import configparser

from . import fileUtils
from ..commonUtils.debugUtils import *
from ..commonUtils import configUtils
from .platformUtils import *


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True
name = filename = os.path.basename(__file__)

# ----------------------------------------------------------------------------------------------------------------------
# CODE

def get_current_env_cfg_value(section, value):
    """
    Retrieve a value from the current environment config file. If value not stored in file, use the one from the default
    :param section: Name of section in which the value you want is found.
    :type section: str
    :param value: Name of the value you want to get as return
    :type value: str
    :rtype: str
    """
    return_value = configUtils.config_section_map(fileUtils.get_current_env_var_path(), section, value)
    if return_value is not None:
        return return_value
    else:
        return_value = configUtils.config_section_map(fileUtils.get_default_env_var_path(), section, value)
        if return_value is None:
            msg = 'Could not find value {value} in section {section} in either the current env config file or the ' \
                  'default. Please add missing value to one of those files.'.format(value=value, section=section)
            log(Severity.ERROR, name, msg, popup=True)
        return return_value


def get_url_db_value(section, value):
    """
    Retrieve a value from Blue Hole's URL database file
    """
    return configUtils.config_section_map(fileUtils.get_bh_url_db_file_path(), section, value)
