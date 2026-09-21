"""Callbacks exposed by Blue Hole for integration with external Blender addons."""

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

from typing import Callable

from ..Lib.commonUtils.debugUtils import *

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

TOOL_NAME = 'Addon Callbacks'
EVENT_LOG_TITLE = 'Addon Callback Event'

# ----------------------------------------------------------------------------------------------------------------------
# GLOBALS

EXPORT_BEGIN_CALLBACKS: list[Callable[[], None]] = []
EXPORT_END_CALLBACKS: list[Callable[[bool], None]] = []

# ----------------------------------------------------------------------------------------------------------------------
# HELPERS


def _log_callback_error(event_name: str, callback: Callable, exc: Exception):
    callback_name = getattr(callback, '__qualname__', getattr(callback, '__name__', repr(callback)))

    log(
        Severity.ERROR,
        EVENT_LOG_TITLE,
        f'{event_name} | Callback "{callback_name}" failed: {exc}',
    )


# ----------------------------------------------------------------------------------------------------------------------
# EXPORT CALLBACKS


def register_export_begin_callback(callback: Callable[[], None]):
    """
    Register a callback invoked once when an Asset Container export operation begins.
    """
    if callback not in EXPORT_BEGIN_CALLBACKS:
        EXPORT_BEGIN_CALLBACKS.append(callback)


def unregister_export_begin_callback(callback: Callable[[], None]):
    """
    Unregister a previously registered export-begin callback.
    """
    if callback in EXPORT_BEGIN_CALLBACKS:
        EXPORT_BEGIN_CALLBACKS.remove(callback)


def register_export_end_callback(callback: Callable[[bool], None]):
    """
    Register a callback invoked once when an Asset Container export operation ends.

    The callback receives a bool indicating whether the overall export operation completed successfully.
    """
    if callback not in EXPORT_END_CALLBACKS:
        EXPORT_END_CALLBACKS.append(callback)


def unregister_export_end_callback(callback: Callable[[bool], None]):
    """
    Unregister a previously registered export-end callback.
    """
    if callback in EXPORT_END_CALLBACKS:
        EXPORT_END_CALLBACKS.remove(callback)


def emit_export_begin():
    """
    Emit the Asset Container export-begin event to all registered listeners.
    """
    log(Severity.DEBUG, EVENT_LOG_TITLE, 'export_begin')

    for callback in tuple(EXPORT_BEGIN_CALLBACKS):
        try:
            callback()
        except Exception as exc:
            _log_callback_error('export_begin', callback, exc)


def emit_export_end(success: bool):
    """
    Emit the Asset Container export-end event to all registered listeners.
    """
    log(Severity.DEBUG, EVENT_LOG_TITLE, f'export_end | Success: {success}')

    for callback in tuple(EXPORT_END_CALLBACKS):
        try:
            callback(success)
        except Exception as exc:
            _log_callback_error('export_end', callback, exc)


def register():
    log(Severity.INFO, TOOL_NAME, f'=== Registering {TOOL_NAME} ===')
    log(Severity.INFO, TOOL_NAME, 'Registration complete')


def unregister():
    log(Severity.INFO, TOOL_NAME, f'=== Unregistering {TOOL_NAME} ===')

    EXPORT_BEGIN_CALLBACKS.clear()
    EXPORT_END_CALLBACKS.clear()

    log(Severity.INFO, TOOL_NAME, 'Unregistration complete')
