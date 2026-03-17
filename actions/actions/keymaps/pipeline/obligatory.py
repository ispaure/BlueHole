"""
Obligatory Pipeline operators that *MUST* always be bound to a keymap
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

from ....operator_action import OperatorAction, KeymapBinding

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def _save_as_bindings(
        keymap_name: str,
        space_type: str = 'EMPTY',
        region_type: str = 'WINDOW',
) -> tuple[KeymapBinding, ...]:
    """
    Return the default Blue Hole keymap bindings for Save As Mainfile.
    Uses Ctrl+Shift+S on Windows/Linux and Command+Shift+S on macOS.
    """
    return (
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='S',
            ctrl=True,
            shift=True,
        ),
        KeymapBinding(
            keymap_name=keymap_name,
            space_type=space_type,
            region_type=region_type,
            key='S',
            oskey=True,
            shift=True,
        ),
    )


# ----------------------------------------------------------------------------------------------------------------------
# FEATURE: SAVE AS MAINFILE

SAVE_AS_MAINFILE = OperatorAction(
    operator='wm.bh_save_as_mainfile',
    keymap_bindings=_save_as_bindings('Window')
)

# ----------------------------------------------------------------------------------------------------------------------
# ACTION LIST

OBLIGATORY_PIPELINE_ACTIONS: list[OperatorAction] = [
    SAVE_AS_MAINFILE,
]


def get_obligatory_pipeline_actions() -> list[OperatorAction]:
    """
    Return all declared obligatory pipeline operator actions.
    """
    return OBLIGATORY_PIPELINE_ACTIONS
