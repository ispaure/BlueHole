"""Callbacks to integrate source control with Blender open/load/save events."""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://github.com/ispaure/BlueHole

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = 'MIT License'
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS

import bpy

from . import blenderFile, sourceControlUtils
from ..Lib.commonUtils.debugUtils import *

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

TOOL_NAME = 'Callbacks'
EVENT_LOG_TITLE = 'Callback Event'

# ----------------------------------------------------------------------------------------------------------------------
# GLOBALS

SKIP_NEXT_SAVE_PRE_SC_CHECK: bool = False

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def _log_callback_event(event_name: str):
    log(Severity.DEBUG, EVENT_LOG_TITLE, f'{event_name} | Blender Filepath: "{blenderFile.get_blend_file_path()}"')


# ----------------------------------------------------------------------------------------------------------------------
# CODE


@bpy.app.handlers.persistent
def load_pre_handler(dummy):
    _log_callback_event('load_pre')


@bpy.app.handlers.persistent
def load_post_handler(dummy):
    _log_callback_event('load_post')

    if blenderFile.has_blend_filepath():
        sourceControlUtils.sc_check_blend(
            blenderFile.get_blend_file_path(),
            allow_sync=True,
            silent_mode=False,
        )


@bpy.app.handlers.persistent
def save_pre_handler(dummy):
    global SKIP_NEXT_SAVE_PRE_SC_CHECK

    _log_callback_event('save_pre')

    if SKIP_NEXT_SAVE_PRE_SC_CHECK:
        SKIP_NEXT_SAVE_PRE_SC_CHECK = False
        log(Severity.DEBUG, EVENT_LOG_TITLE, 'save_pre | Skipping source control check for custom Save As flow')
        return

    if blenderFile.has_blend_filepath():
        sourceControlUtils.sc_check_blend(
            blenderFile.get_blend_file_path(),
            allow_sync=False,
            silent_mode=False,
        )


@bpy.app.handlers.persistent
def save_post_handler(dummy):
    _log_callback_event('save_post')


def register():
    log(Severity.INFO, TOOL_NAME, f'=== Registering {TOOL_NAME} ===')
    bpy.app.handlers.load_pre.append(load_pre_handler)
    bpy.app.handlers.load_post.append(load_post_handler)
    bpy.app.handlers.save_pre.append(save_pre_handler)
    bpy.app.handlers.save_post.append(save_post_handler)
    log(Severity.INFO, TOOL_NAME, 'Registration complete')


def unregister():
    log(Severity.INFO, TOOL_NAME, f'=== Unregistering {TOOL_NAME} ===')
    bpy.app.handlers.load_pre.remove(load_pre_handler)
    bpy.app.handlers.load_post.remove(load_post_handler)
    bpy.app.handlers.save_pre.remove(save_pre_handler)
    bpy.app.handlers.save_post.remove(save_post_handler)
    log(Severity.INFO, TOOL_NAME, 'Unregistration complete')
