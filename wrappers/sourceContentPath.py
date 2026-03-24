"""
Source Content path resolution utility for Blue Hole.

This module resolves the root "SourceContent" directory used by the addon,
which is required for export, validation, and engine bridge operations.

Resolution order:
1. Cached path (fast path)
2. User-defined preference paths (primary / alternate, OS-specific)
3. Perforce workspace search (up to 2 directory levels)

The result is cached for performance, and all resolution steps include
detailed logging for debugging and diagnostics.

If multiple SourceContent folders are found in the Perforce workspace,
resolution is aborted to avoid ambiguity.
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

from typing import Iterable, Optional
from pathlib import Path

from ..Lib.commonUtils.osUtils import get_os, OS
from ..Lib.commonUtils.debugUtils import *
from ..preferences.prefs import prefs
from .perforce.p4_info import P4Info

# ----------------------------------------------------------------------------------------------------------------------
# GLOBAL CACHE

_valid_sc_path: Optional[Path] = None

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

SOURCE_CONTENT_FOLDER_NAME = 'SourceContent'
SC_PATH_SEARCH_TOOL_NAME = 'Get Source Content Path'

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def _safe_iterdir(path: Path) -> Iterable[Path]:
    """
    Yield children of a directory, but never raise if a folder is unreadable.
    """
    try:
        yield from path.iterdir()
    except PermissionError:
        log(Severity.DEBUG, SC_PATH_SEARCH_TOOL_NAME, f'Permission denied while scanning: "{path}"')
    except FileNotFoundError:
        # Folder disappeared / race condition
        log(Severity.DEBUG, SC_PATH_SEARCH_TOOL_NAME, f'Folder not found while scanning: "{path}"')
    except OSError as e:
        # Best-effort catch-all for odd filesystem cases
        log(Severity.DEBUG, SC_PATH_SEARCH_TOOL_NAME, f'OS error while scanning "{path}": {e}')


def _get_source_content_pref_paths() -> list[str]:
    """
    Return the OS-specific Source Content paths from preferences, in priority order.
    """
    match get_os():
        case OS.WIN:
            return [
                prefs().bridge.sc_path,
                prefs().bridge.sc_path_alternate,
            ]
        case OS.MAC:
            return [
                prefs().bridge.sc_path_mac,
                prefs().bridge.sc_path_mac_alternate,
            ]
        case OS.LINUX:
            return [
                prefs().bridge.sc_path_linux,
                prefs().bridge.sc_path_linux_alternate,
            ]
        case _:
            log(Severity.CRITICAL, SC_PATH_SEARCH_TOOL_NAME, 'Unsupported OS!')
            raise RuntimeError('Unsupported OS')  # IDE quieting


def _resolve_source_content_from_preferences() -> Optional[Path]:
    """
    Attempt to resolve Source Content from the configured preference paths.
    """
    path_to_attempt_lst = _get_source_content_pref_paths()

    for path_str in path_to_attempt_lst:
        if not path_str:
            continue

        path = Path(path_str).expanduser()

        log(Severity.DEBUG, SC_PATH_SEARCH_TOOL_NAME, f'Trying: "{path}"')

        if path.is_dir():
            resolved_path = path.resolve()
            log(Severity.INFO, SC_PATH_SEARCH_TOOL_NAME, f'Using Source Content path (from preference): "{resolved_path}"')
            return resolved_path

    log(Severity.DEBUG, SC_PATH_SEARCH_TOOL_NAME, 'No valid Source Content directory found in configured preference paths.')
    return None


def _iter_source_content_candidates(client_root: Path) -> Iterable[Path]:
    """
    Yield all SourceContent directory candidates found under the Perforce client root,
    searching at:
        - Level 0 (client root)
        - Level 1 (direct child folders)
        - Level 2 (grandchild folders)
    """
    # Level 0
    sc = client_root / SOURCE_CONTENT_FOLDER_NAME
    if sc.is_dir():
        log(Severity.DEBUG, SC_PATH_SEARCH_TOOL_NAME, f'Found SourceContent (Perforce) at level 0: "{sc}"')
        yield sc.resolve()

    # Level 1
    for lvl1 in _safe_iterdir(client_root):
        if not lvl1.is_dir():
            continue

        sc = lvl1 / SOURCE_CONTENT_FOLDER_NAME
        if sc.is_dir():
            log(Severity.DEBUG, SC_PATH_SEARCH_TOOL_NAME, f'Found SourceContent (Perforce) at level 1: "{sc}"')
            yield sc.resolve()

        # Level 2
        for lvl2 in _safe_iterdir(lvl1):
            if not lvl2.is_dir():
                continue

            sc = lvl2 / SOURCE_CONTENT_FOLDER_NAME
            if sc.is_dir():
                log(Severity.DEBUG, SC_PATH_SEARCH_TOOL_NAME, f'Found SourceContent (Perforce) at level 2: "{sc}"')
                yield sc.resolve()


def _resolve_source_content_from_perforce() -> Optional[Path]:
    """
    Attempt to resolve Source Content from the Perforce workspace layout.

    Returns:
        - Path if exactly one SourceContent folder is found
        - None if none are found
        - None if more than one are found (with a warning)
    """
    if not prefs().sourcecontrol.source_control_enable:
        log(Severity.DEBUG, SC_PATH_SEARCH_TOOL_NAME, 'Source control is disabled. Skipping Perforce Source Content search.')
        return None

    if prefs().sourcecontrol.source_control_solution != 'perforce':
        log(
            Severity.DEBUG,
            SC_PATH_SEARCH_TOOL_NAME,
            f'Source control solution is not Perforce ("{prefs().sourcecontrol.source_control_solution}"). '
            f'Skipping Perforce Source Content search.'
        )
        return None

    p4_info_cls = P4Info()

    if not p4_info_cls.status:
        log(Severity.DEBUG, SC_PATH_SEARCH_TOOL_NAME, 'Perforce connection is invalid. Cannot search for Source Content.')
        return None

    client_root_str = p4_info_cls.client_root
    if not client_root_str:
        log(Severity.DEBUG, SC_PATH_SEARCH_TOOL_NAME, 'Perforce client root is empty. Cannot search for Source Content.')
        return None

    client_root = Path(client_root_str)

    log(Severity.DEBUG, SC_PATH_SEARCH_TOOL_NAME, f'Perforce client root detected: "{client_root}"')

    if not client_root.is_dir():
        log(Severity.DEBUG, SC_PATH_SEARCH_TOOL_NAME, f'Perforce client root is not a valid directory: "{client_root}"')
        return None

    source_content_candidates = list(_iter_source_content_candidates(client_root))

    if not source_content_candidates:
        log(Severity.DEBUG, SC_PATH_SEARCH_TOOL_NAME, 'Perforce fallback search did not find a SourceContent folder.')
        return None

    if len(source_content_candidates) > 1:
        candidates_msg = '\n'.join(f'- "{path}"' for path in source_content_candidates)
        msg = (
            f'Multiple "{SOURCE_CONTENT_FOLDER_NAME}" folders were found while searching through the Perforce '
            f'workspace root (levels 0 to 2).\n\n'
            f'What went wrong:\n'
            f'Blue Hole found more than one possible Source Content folder, so it cannot determine which one '
            f'should be used automatically.\n\n'
            f'Found paths:\n'
            f'{candidates_msg}\n\n'
            f'What to do:\n'
            f'Set the Source Content path explicitly in the Blue Hole preferences so the correct folder is used.\n\n'
            f'Source Content path resolution aborted.'
        )
        log(Severity.WARNING, SC_PATH_SEARCH_TOOL_NAME, msg)
        return None

    resolved_path = source_content_candidates[0]
    log(Severity.INFO, SC_PATH_SEARCH_TOOL_NAME, f'Using Source Content path (from Perforce fallback): "{resolved_path}"')
    return resolved_path


def get_valid_source_content_path() -> Optional[Path]:
    """
    Resolve and cache the Source Content path used by Blue Hole.

    Order of resolution:
    1. Cached value
    2. Primary / alternate path from preferences
    3. Perforce workspace search (up to 2 directory levels)

    Returns:
        Path to Source Content directory, or None if not found.
    """
    global _valid_sc_path

    # Return cached value
    if _valid_sc_path is not None:
        log(Severity.DEBUG, SC_PATH_SEARCH_TOOL_NAME, f'Using cached Source Content path: "{_valid_sc_path}"')
        return _valid_sc_path

    # Attempt preference-based resolution
    pref_path = _resolve_source_content_from_preferences()
    if pref_path is not None:
        _valid_sc_path = pref_path
        return _valid_sc_path

    log(
        Severity.INFO,
        SC_PATH_SEARCH_TOOL_NAME,
        'No valid Source Content path found in preferences. Attempting source control fallback search.'
    )

    # Attempt Perforce-based resolution
    p4_path = _resolve_source_content_from_perforce()
    if p4_path is not None:
        _valid_sc_path = p4_path
        return _valid_sc_path

    # No valid path found
    msg = ('No valid Source Content path found in preferences or source control. '
           'Set a valid Source Content path in Blue Hole preferences.')
    log(Severity.ERROR, SC_PATH_SEARCH_TOOL_NAME, msg)
    return None
