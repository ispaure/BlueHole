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


def get_url_db_value(section, value):
    """
    Retrieve a value from Blue Hole's URL database file
    """
    return configUtils.config_section_map(fileUtils.get_bh_url_db_file_path(), section, value)
