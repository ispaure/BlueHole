"""
Code to trigger the Unreal Send Override, that calls in a custom function when specified by the user in lieu of
Blue Hole's vanilla way of executing Unreal code. Offers freedom for use within a studio environment with custom
Unreal setup.
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

from ...preferences.prefs import prefs
from .ue_override_utils import run_unreal_override_operator


# ----------------------------------------------------------------------------------------------------------------------
# CODE

send_ue_name = 'Blue Hole Bridge to Unreal (Send Operator Override)'


def trigger_unreal_import_override(file_path_source: str) -> bool:
    return run_unreal_override_operator(
        op_idname=prefs().bridge.ue_op_send_override,
        log_name=send_ue_name,
        operator_kwargs={
            "path": str(file_path_source),
        },
    )
