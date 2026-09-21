"""
Addon-facing lifecycle callbacks exposed by Blue Hole.

These callbacks allow external Blender addons to listen for Blue Hole events
without coupling Blue Hole directly to those addons.

The callbacks in this module are informational notifications only:
- Callback return values are ignored.
- Exceptions raised by listeners are caught and logged.
- Listener failures do not stop or alter the export operation.
- Export begin/end events are emitted once per top-level export/send operation,
  even when multiple Asset Container groups are processed.
"""

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
    """
    Log an exception raised by an external callback without propagating it.

    External callback failures must not interrupt Blue Hole's export flow or
    prevent other registered listeners from receiving the same event.
    """
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
    Register a listener for the beginning of a top-level Asset Container export/send operation.

    The event is emitted once per user-triggered export/send operation, even when
    multiple Asset Container groups are processed.

    This is an informational callback only:
        - The callback return value is ignored.
        - Raising an exception does not stop the export.
        - Exceptions are caught and logged by Blue Hole.

    Typical uses include resetting external validation state, starting an
    external logging session, or preparing aggregate result storage.
    """
    if callback not in EXPORT_BEGIN_CALLBACKS:
        EXPORT_BEGIN_CALLBACKS.append(callback)


def unregister_export_begin_callback(callback: Callable[[], None]):
    """
    Unregister a previously registered export-begin listener.
    """
    if callback in EXPORT_BEGIN_CALLBACKS:
        EXPORT_BEGIN_CALLBACKS.remove(callback)


def register_export_end_callback(callback: Callable[[bool], None]):
    """
    Register a listener for the end of a top-level Asset Container export/send operation.

    The event is emitted once per user-triggered export/send operation, even when
    multiple Asset Container groups are processed.

    The callback receives:
        success:
            True when Blue Hole completed the overall export/send operation successfully.
            False when the operation was cancelled or failed before completion.

    This value describes Blue Hole's overall operation state. It does not
    independently summarize external validation results collected by listeners.

    This is an informational callback only:
        - The callback return value is ignored.
        - Raising an exception does not alter the export result.
        - Exceptions are caught and logged by Blue Hole.
    """
    if callback not in EXPORT_END_CALLBACKS:
        EXPORT_END_CALLBACKS.append(callback)


def unregister_export_end_callback(callback: Callable[[bool], None]):
    """
    Unregister a previously registered export-end listener.
    """
    if callback in EXPORT_END_CALLBACKS:
        EXPORT_END_CALLBACKS.remove(callback)


def emit_export_begin():
    """
    Notify all registered listeners that a top-level Asset Container export/send operation has begun.

    Listener return values are ignored. Exceptions are caught and logged so one
    failing listener cannot interrupt the export or prevent other listeners from
    receiving the event.
    """
    log(Severity.DEBUG, EVENT_LOG_TITLE, 'export_begin')

    for callback in tuple(EXPORT_BEGIN_CALLBACKS):
        try:
            callback()
        except Exception as exc:
            _log_callback_error('export_begin', callback, exc)


def emit_export_end(success: bool):
    """
    Notify all registered listeners that a top-level Asset Container export/send operation has ended.

    Args:
        success:
            True when Blue Hole completed the overall export/send operation successfully.
            False when the operation was cancelled or failed before completion.

    Listener return values are ignored. Exceptions are caught and logged so one
    failing listener cannot alter the final export result or prevent other
    listeners from receiving the event.
    """
    log(Severity.DEBUG, EVENT_LOG_TITLE, f'export_end | Success: {success}')

    for callback in tuple(EXPORT_END_CALLBACKS):
        try:
            callback(success)
        except Exception as exc:
            _log_callback_error('export_end', callback, exc)


def register():
    """
    Register the addon callback module.

    No Blender handlers are registered here; this module exposes a Python-level
    callback API for external addons.
    """
    log(Severity.INFO, TOOL_NAME, f'=== Registering {TOOL_NAME} ===')
    log(Severity.INFO, TOOL_NAME, 'Registration complete')


def unregister():
    """
    Unregister the addon callback module and release all external listener references.

    Clearing the callback lists prevents stale references from surviving Blue Hole
    addon unload/reload cycles during development or addon shutdown.
    """
    log(Severity.INFO, TOOL_NAME, f'=== Unregistering {TOOL_NAME} ===')

    EXPORT_BEGIN_CALLBACKS.clear()
    EXPORT_END_CALLBACKS.clear()

    log(Severity.INFO, TOOL_NAME, 'Unregistration complete')
