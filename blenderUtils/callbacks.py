""" Callbacks to integrate source control to Blender Open/Load/Save """

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://github.com/ispaure/BlueHole

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

import bpy
from . import sourceControlUtils, blenderFile

# ----------------------------------------------------------------------------------------------------------------------
# CODE


@bpy.app.handlers.persistent
def load_pre_handler(dummy):
    print("Event: load_pre")


@bpy.app.handlers.persistent
def load_post_handler(dummy):
    print("Event: load_post")
    if len(blenderFile.get_blend_file_path()) > 0:
        sourceControlUtils.sc_check_blend(silent_mode=False)  # Checks status with perforce and prompt to get latest, checkout, etc.


@bpy.app.handlers.persistent
def save_pre_handler(dummy):
    if len(blenderFile.get_blend_file_path()) > 0:
        sourceControlUtils.sc_check_blend(silent_mode=False)  # Checks status with perforce and prompt to get latest, checkout, etc.
    print("Event: save_pre")


@bpy.app.handlers.persistent
def save_post_handler(dummy):
    print("Event: save_post")


def register():
    print("Registering callbacks...")
    bpy.app.handlers.load_pre.append(load_pre_handler)
    bpy.app.handlers.load_post.append(load_post_handler)
    bpy.app.handlers.save_pre.append(save_pre_handler)
    bpy.app.handlers.save_post.append(save_post_handler)


def unregister():
    print("Unregistering callbacks...")
    bpy.app.handlers.load_pre.remove(load_pre_handler)
    bpy.app.handlers.load_post.remove(load_post_handler)
    bpy.app.handlers.save_pre.remove(save_pre_handler)
    bpy.app.handlers.save_post.remove(save_post_handler)
