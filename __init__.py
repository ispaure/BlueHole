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
from .Menus import headerMenu
from .wrappers import perforceWrapper as p4Wrapper
from .blenderUtils import fileUtils as fileUtils
from .blenderUtils import filterUtils as filterUtils
from .preferences import preferences as preferences

# Import Blue Hole Operators
from .Operators import dirOp as dirOp
from .Operators import envOp as envOp
from .Operators import externalAddonOp as externalAddonOp
from .Operators import foodOp as foodOp
from .Operators import helpOp as helpOp
from .Operators import impExpOp as impExpOp
from .Operators import musicOp as musicOp
from .Operators import otherOp as otherOp
from .Operators import sendOp as sendOp
from .Operators import sortOp as sortOp
from .Operators import sourceControlOp as sourceControlOp
from .Operators import themeOp as themeOp

# Import Env Utils
from .envUtils import envUtils as envUtils

# Import Menus
from .Menus import menu as menu
from .Menus import pieMenu as pieMenu

# ----------------------------------------------------------------------------------------------------------------------
# PLUGIN INFO

bl_info = {"name": "Blue Hole",
           "author": "Marc-André Voyer",
           "description": "",
           "blender": (4, 5, 1),
           "version": (1, 0, 1),
           "location": "",
           "warning": "",
           "category": "Generic"
           }


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Classes
# Operators in List
operator_file_lst = (dirOp,
                     envOp,
                     externalAddonOp,
                     foodOp,
                     helpOp,
                     impExpOp,
                     musicOp,
                     otherOp,
                     sendOp,
                     sortOp,
                     sourceControlOp,
                     themeOp)

menu_file_lst = (menu, pieMenu)


# Register
def register():

    # Register Callbacks
    callbacks.register()
    # Register preferences
    preferences.register()

    # Register operators
    for file in operator_file_lst:
        file.register()

    # Register menus
    for file in menu_file_lst:
        file.register()

    # Register Header Menu
    headerMenu.register()

    # Source Control: Override Perforce Environment Settings (If set up in preferences)
    p4Wrapper.set_p4_env_settings()

    # Register Current Env Tools
    envUtils.if_environment_missing_set_to_default()  # When a saved environment is no longer available, rever to default
    envUtils.register_current_env()


# Unregister
def unregister():
    # Unregister Callbacks
    callbacks.unregister()

    # Unregister Current Env Tools
    envUtils.unregister_current_env()

    # Unregister preferences
    preferences.unregister()

    # Unregister Header Menu
    headerMenu.unregister()

    # Register operators
    for file in operator_file_lst:
        file.unregister()

    # Register menus
    for file in menu_file_lst:
        file.unregister()
