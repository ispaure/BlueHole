"""
Debug verbosity flags for Blue Hole.

These flags control *detailed (verbose)* logging per subsystem.

- Regular logs (INFO / DEBUG summaries) should always remain enabled.
- Verbose logs are optional and meant for deep inspection / debugging.

Typical usage:

    from ..debug.debug_flags import VERBOSE_KEYMAPS, is_verbose

    if is_verbose(VERBOSE_KEYMAPS):
        log(Severity.DEBUG, tool_name, "Detailed keymap info...")

You can enable all verbose logs at once using VERBOSE_ALL.
"""

# ----------------------------------------------------------------------------------------------------------------------
# GLOBAL OVERRIDE

# Enable all verbose logs regardless of individual flags
VERBOSE_ALL = False


# ----------------------------------------------------------------------------------------------------------------------
# SUBSYSTEM VERBOSE FLAGS

# Actions (operator actions, keymap actions, etc.)
VERBOSE_ACTIONS = False

# Blender utilities (helpers interacting with Blender API)
VERBOSE_BLENDER_UTILS = False

# Environment files (.ini, config files, etc.)
VERBOSE_ENV_FILES = False

# Environment system (env switching, resolving, management)
VERBOSE_ENVIRONMENT = False

# Keymaps (registration, conflicts, bindings)
VERBOSE_KEYMAPS = False

# Core library utilities (commonUtils, cmd wrappers, etc.)
VERBOSE_LIB = False

# Operators (execution flow, parameters, results)
VERBOSE_OPERATORS = False

# Overlays (viewport overlays, drawing, etc.)
VERBOSE_OVERLAYS = False

# Preferences (reading, writing, syncing prefs)
VERBOSE_PREFERENCES = False

# UI (menus, panels, layout drawing)
VERBOSE_UI = False

# Wrappers (Perforce, external tools, bridges, etc.)
VERBOSE_WRAPPERS = False


# ----------------------------------------------------------------------------------------------------------------------
# OPTIONAL HELPERS (CLEAN CALL SITES)

def is_verbose(flag: bool) -> bool:
    """
    Returns True if verbose logging should be enabled for a subsystem.
    """
    return VERBOSE_ALL or flag
