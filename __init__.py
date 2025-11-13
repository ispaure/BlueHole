"""
Blue Hole is a blender addon that was created and written by Marc-André Voyer for Environment Artists.

Highlights are export scripts and Perforce source control integration.
Official GitHUB: https://www.github.com/ispaure/BlueHole
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
# Install PySide6 (Only Custom Library required for Blue Hole -- It's for the User Interface)
try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    import subprocess
    import sys
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PySide6"])
        from PySide6.QtWidgets import QApplication
    except Exception as install_error:
        print("[PIP ERROR] Failed to install PySide6: ", install_error)
        raise install_error
# ----------------------------------------------------------------------------------------------------------------------

# Import Blue Hole Scripts
from .blenderUtils import callbacks
from .UI import headermenu
from .wrappers import perforceWrapper as p4Wrapper
from .blenderUtils import fileUtils as fileUtils
from .blenderUtils import filterUtils as filterUtils
from .preferences import preferences as preferences

# Import Blue Hole Operators
from .blenderOperators import globalDirectories as globalDirectories
from .blenderOperators import globalExport as globalExport
from .blenderOperators import globalFoodDelivery as globalFoodDelivery
from .blenderOperators import globalHelp as globalHelp
from .blenderOperators import globalImport as globalImport
from .blenderOperators import globalOpen as globalOpen
from .blenderOperators import globalSend as globalSend
from .blenderOperators import globalSourceControl as globalSourceControl
from .blenderOperators import globalThemes as globalThemes
from .blenderOperators import globalSpeedTree as globalSpeedTree
from .blenderOperators import globalMusic as globalMusic
from .blenderOperators import globalUnlisted as globalUnlisted
from .blenderOperators import globalSort as globalSort

# Import Env Utils
from .envUtils import envUtils as envUtils

# Import Pie Menus
from .blenderOperators import pieMenusOps as pieMenusOps

# ----------------------------------------------------------------------------------------------------------------------
# PLUGIN INFO

bl_info = {"name": "Blue Hole",
           "author": "Marc-André Voyer",
           "description": "",
           "blender": (4, 5, 1),
           "version": (1, 0, 1),
           "location": "",
           "warning": "",
           "category": "Generic",
           }


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Classes
# Operators in List
menu_and_operator_classes = (globalDirectories,
                             globalExport,
                             globalFoodDelivery,
                             globalHelp,
                             globalImport,
                             globalOpen,
                             globalSend,
                             globalSourceControl,
                             globalThemes,
                             globalMusic,
                             globalUnlisted,
                             globalSort)


# Register
def register():

    # Register Callbacks
    callbacks.register()
    # Register preferences
    preferences.register()

    # Register menus and operators
    for cls in menu_and_operator_classes:
        cls.register()
    # Register Header Menu
    headermenu.register()

    # Source Control: Override Perforce Environment Settings (If set up in preferences)
    p4Wrapper.set_p4_env_settings()

    # Register Current Env Tools
    envUtils.if_environment_missing_set_to_default()  # When a saved environment is no longer available, rever to default
    envUtils.register_current_env()

    # Register pie menus
    pieMenusOps.register()

    # Check for updates
    import BlueHole.blenderUtils.addon as addon
    if addon.preference().help_n_update.auto_update_addon:
        pass
        # TODO: Do an auto-update procedure from GitHub


# Unregister
def unregister():
    # Unregister Callbacks
    callbacks.unregister()

    # Unregister Current Env Tools
    envUtils.unregister_current_env()

    # Unregister preferences
    preferences.unregister()

    # Unregister Header Menu
    headermenu.unregister()

    # Unregister menus and operators
    for cls in menu_and_operator_classes:
        cls.unregister()

    # Unregister pie menus
    pieMenusOps.unregister()


