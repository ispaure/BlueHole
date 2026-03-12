"""Callbacks to integrate source control with Blender open/load/save events."""

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

import bpy

from . import blenderFile, sourceControlUtils
from ..Lib.commonUtils.debugUtils import *

# ----------------------------------------------------------------------------------------------------------------------
# GLOBALS

SKIP_NEXT_SAVE_PRE_SC_CHECK: bool = False

# ----------------------------------------------------------------------------------------------------------------------
# CODE


@bpy.app.handlers.persistent
def load_pre_handler(dummy):
    log(Severity.DEBUG, 'Callback Event: load_pre', f'Blender Filepath: "{blenderFile.get_blend_file_path()}"')


@bpy.app.handlers.persistent
def load_post_handler(dummy):
    log(Severity.DEBUG, 'Callback Event: load_post', f'Blender Filepath: "{blenderFile.get_blend_file_path()}"')

    if blenderFile.has_blend_filepath():
        sourceControlUtils.sc_check_blend(
            blenderFile.get_blend_file_path(),
            allow_sync=True,
            silent_mode=False,
        )


@bpy.app.handlers.persistent
def save_pre_handler(dummy):
    global SKIP_NEXT_SAVE_PRE_SC_CHECK

    log(Severity.DEBUG, 'Callback Event: save_pre', f'Blender Filepath: "{blenderFile.get_blend_file_path()}"')

    if SKIP_NEXT_SAVE_PRE_SC_CHECK:
        SKIP_NEXT_SAVE_PRE_SC_CHECK = False
        log(Severity.DEBUG, 'Callback Event: save_pre', 'Skipping source control check for custom Save As flow')
        return

    if blenderFile.has_blend_filepath():
        sourceControlUtils.sc_check_blend(
            blenderFile.get_blend_file_path(),
            allow_sync=False,
            silent_mode=False,
        )


@bpy.app.handlers.persistent
def save_post_handler(dummy):
    log(Severity.DEBUG, 'Callback Event: save_post', f'Blender Filepath: "{blenderFile.get_blend_file_path()}"')


def register():
    log(Severity.DEBUG, 'callbacks.register', 'Registering callbacks...')
    bpy.app.handlers.load_pre.append(load_pre_handler)
    bpy.app.handlers.load_post.append(load_post_handler)
    bpy.app.handlers.save_pre.append(save_pre_handler)
    bpy.app.handlers.save_post.append(save_post_handler)


def unregister():
    log(Severity.DEBUG, 'callbacks.unregister', 'Unregistering callbacks...')
    bpy.app.handlers.load_pre.remove(load_pre_handler)
    bpy.app.handlers.load_post.remove(load_post_handler)
    bpy.app.handlers.save_pre.remove(save_pre_handler)
    bpy.app.handlers.save_post.remove(save_post_handler)
