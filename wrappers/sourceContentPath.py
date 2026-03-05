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

from typing import *
from pathlib import Path

from ..Lib.commonUtils.osUtils import get_os, OS
from ..Lib.commonUtils.debugUtils import *
from ..preferences.prefs import prefs
from . import perforceWrapper as p4Wrapper


# ----------------------------------------------------------------------------------------------------------------------
# GLOBAL CACHE

_valid_sc_path: Optional[Path] = None


# ----------------------------------------------------------------------------------------------------------------------
# CODE


def _safe_iterdir(path: Path, *, tool_name: str) -> Iterable[Path]:
    """
    Yield children of a directory, but never raise if a folder is unreadable.
    """
    try:
        yield from path.iterdir()
    except PermissionError:
        log(Severity.DEBUG, tool_name, f'Permission denied while scanning: "{path}"')
    except FileNotFoundError:
        # Folder disappeared / race condition
        log(Severity.DEBUG, tool_name, f'Folder not found while scanning: "{path}"')
    except OSError as e:
        # Best-effort catch-all for odd filesystem cases
        log(Severity.DEBUG, tool_name, f'OS error while scanning "{path}": {e}')


def get_valid_source_content_path() -> Optional[Path]:
    """
    Resolve and cache the Source Content path used by Blue Hole.

    Order of resolution:
    1. Cached value
    2. Primary path from preferences
    3. Alternate path from preferences
    4. Perforce workspace search (up to 2 directory levels)

    Returns:
        Path to Source Content directory, or None if not found.
    """

    global _valid_sc_path

    tool_name = 'Get Source Content Path'

    # Return cached value
    if _valid_sc_path is not None:
        return _valid_sc_path

    # Determine OS-specific preference paths
    match get_os():
        case OS.WIN:
            path_to_attempt_lst = [
                prefs().bridge.sc_path,
                prefs().bridge.sc_path_alternate
            ]
        case OS.MAC:
            path_to_attempt_lst = [
                prefs().bridge.sc_path_mac,
                prefs().bridge.sc_path_mac_alternate
            ]
        case OS.LINUX:
            path_to_attempt_lst = [
                prefs().bridge.sc_path_linux,
                prefs().bridge.sc_path_linux_alternate
            ]
        case _:
            log(Severity.CRITICAL, tool_name, 'Unsupported OS!')
            raise RuntimeError('Unsupported OS')  # IDE quieting

    # Attempt to resolve paths from preferences
    for path_str in path_to_attempt_lst:

        if not path_str:
            continue

        path = Path(path_str).expanduser()

        log(Severity.DEBUG, tool_name, f'Trying: "{path}"')

        if path.is_dir():
            _valid_sc_path = path.resolve()
            log(Severity.DEBUG, tool_name, f'Using Source Content path (from preference): "{_valid_sc_path}"')
            return _valid_sc_path

    msg = 'No valid Source Content path found in preferences. Fallback to expensive search methods.'
    log(Severity.WARNING, tool_name, msg)

    # Attempt to resolve through Perforce Workspace Root and Perforce folder structure
    if prefs().sc.source_control_enable and prefs().sc.source_control_solution == 'perforce':

        client_root = Path(p4Wrapper.P4Info().client_root)

        log(Severity.DEBUG, tool_name, f'Perforce client root detected: "{client_root}"')

        if client_root.is_dir():

            # Level 0 (root)
            sc = client_root / "SourceContent"
            if sc.is_dir():
                log(Severity.DEBUG, tool_name, f'Found SourceContent (Perforce) at level 0: "{sc}"')
                _valid_sc_path = sc.resolve()
                return _valid_sc_path

            # Level 1
            for lvl1 in _safe_iterdir(client_root, tool_name=tool_name):
                if not lvl1.is_dir():
                    continue

                sc = lvl1 / "SourceContent"
                if sc.is_dir():
                    log(Severity.DEBUG, tool_name, f'Found SourceContent (Perforce) at level 1: "{sc}"')
                    _valid_sc_path = sc.resolve()
                    return _valid_sc_path

                # Level 2
                for lvl2 in _safe_iterdir(lvl1, tool_name=tool_name):
                    if not lvl2.is_dir():
                        continue

                    sc = lvl2 / "SourceContent"
                    if sc.is_dir():
                        log(Severity.DEBUG, tool_name, f'Found SourceContent (Perforce) at level 2: "{sc}"')
                        _valid_sc_path = sc.resolve()
                        return _valid_sc_path

        log(Severity.DEBUG, tool_name, 'Perforce fallback search did not find a SourceContent folder.')

    # No valid path found
    log(Severity.ERROR, tool_name, 'No valid Source Content path found in preferences or source control.')
    return None
