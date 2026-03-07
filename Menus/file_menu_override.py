"""
Full Override of the Blender File menu to place "Blue Hole Save As" directly under Save.
This is required for proper source control on Save As operations.

NOTE:
This file overrides Blender's TOPBAR_MT_file.draw.
If Blender updates the File menu in a future version,
this file may need to be updated to match.
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

# Blender
import bpy

# Blue Hole
from ..Lib.commonUtils.debugUtils import *

# ----------------------------------------------------------------------------------------------------------------------
# GLOBALS

ORIGINAL_TOPBAR_MT_FILE_DRAW = None

# ----------------------------------------------------------------------------------------------------------------------
# MENU OVERRIDE


def draw_topbar_mt_file_blue_hole(self, context):
    """
    Full override of Blender's File menu.

    This intentionally replaces the default TOPBAR_MT_file draw function so that
    Blue Hole Save As can be placed directly under Blender's native Save As.
    """
    layout = self.layout
    layout.operator_context = 'INVOKE_DEFAULT'

    # --------------------------------------------------------------------------------------------------------------
    # NEW / OPEN
    layout.menu("TOPBAR_MT_file_new", text="New", icon='FILE_NEW')
    layout.operator("wm.open_mainfile", text="Open...", icon='FILE_FOLDER')
    layout.menu("TOPBAR_MT_file_open_recent", text="Open Recent")
    layout.operator("wm.revert_mainfile", text="Revert")

    # --------------------------------------------------------------------------------------------------------------
    # RECOVER
    layout.menu("TOPBAR_MT_file_recover", text="Recover")

    # --------------------------------------------------------------------------------------------------------------
    # SAVE
    layout.separator()
    layout.operator("wm.save_mainfile", text="Save", icon='FILE_TICK')
    # layout.operator("wm.save_as_mainfile", text="Save As...")
    layout.operator("wm.bh_save_as_mainfile", text="Save As...")
    layout.operator("wm.save_as_mainfile", text="Save Copy...").copy = True
    layout.operator("wm.save_mainfile", text="Save Incremental").incremental = True

    # --------------------------------------------------------------------------------------------------------------
    # LINK / APPEND / DATA PREVIEWS
    layout.separator()
    layout.operator("wm.link", text="Link...", icon='LINK_BLEND')
    layout.operator("wm.append", text="Append...", icon='APPEND_BLEND')
    layout.operator("wm.previews_batch_generate", text="Data Previews")

    # --------------------------------------------------------------------------------------------------------------
    # IMPORT / EXPORT / EXPORT ALL COLLECTIONS
    layout.separator()
    layout.menu("TOPBAR_MT_file_import", text="Import")
    layout.menu("TOPBAR_MT_file_export", text="Export")
    layout.operator("wm.collection_export_all", text="Export All Collections")

    # --------------------------------------------------------------------------------------------------------------
    # EXTERNAL DATA / CLEANUP
    layout.separator()
    layout.menu("TOPBAR_MT_file_external_data", text="External Data")
    layout.menu("TOPBAR_MT_file_cleanup", text="Clean Up")

    # --------------------------------------------------------------------------------------------------------------
    # DEFAULTS
    layout.separator()
    layout.menu("TOPBAR_MT_file_defaults", text="Defaults")

    # --------------------------------------------------------------------------------------------------------------
    # QUIT
    layout.separator()
    layout.operator("wm.quit_blender", text="Quit", icon='QUIT')


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER


def register():
    global ORIGINAL_TOPBAR_MT_FILE_DRAW

    print("Registering File menu override...")

    if ORIGINAL_TOPBAR_MT_FILE_DRAW is None:
        ORIGINAL_TOPBAR_MT_FILE_DRAW = bpy.types.TOPBAR_MT_file.draw

    bpy.types.TOPBAR_MT_file.draw = draw_topbar_mt_file_blue_hole
    log(Severity.DEBUG, 'File Menu Override', 'TOPBAR_MT_file.draw overridden')


def unregister():
    global ORIGINAL_TOPBAR_MT_FILE_DRAW

    print("Unregistering File menu override...")

    if ORIGINAL_TOPBAR_MT_FILE_DRAW is not None:
        bpy.types.TOPBAR_MT_file.draw = ORIGINAL_TOPBAR_MT_FILE_DRAW
        ORIGINAL_TOPBAR_MT_FILE_DRAW = None
        log(Severity.DEBUG, 'File Menu Override', 'TOPBAR_MT_file.draw restored')
