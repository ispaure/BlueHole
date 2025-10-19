"""
Exports selection as .fbx in location within asset folder.
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "GNU General Public License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

import BlueHole.envUtils.projectUtils as projectUtils
import BlueHole.blenderUtils.exportUtils2 as exportUtils2


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

def batch_export_selection_to_project_sub_dir(path_append):
    """
    Exports selected asset files in desired location, relative to open project.
    :param path_append: Specifies directory to export to. Has to be an entry of
                        env_variables.ini under "DirectoryStructure" section.
    :type path_append: str
    """
    # Get path of desired sub project directory to export to
    export_dir = projectUtils.get_project_sub_dir(path_append)

    # Batch export selection to FBX. Connects to source control
    exportUtils2.batch_export_selection(export_dir, exp_format='FBX')
    # exportUtils.batch_export_selected_as_fbx(export_dir)
