"""
Top-level registration and refresh management for Blue Hole keymaps.

This module orchestrates registration, unregistration, and refresh of all
standard keymap categories and pie keymaps.

Child keymap register modules are responsible for:
- determining which actions are enabled
- registering their own keymaps
- storing runtime keymap references
- returning the number of successfully registered keymaps

This module is responsible for:
- registration order
- centralized high-level logging
- total keymap registration summaries
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

from ..Lib.commonUtils.debugUtils import *
from ..debug.debug_flags import *
from .pie import pie_keymaps_register
from . import mesh_keymaps_register
from . import navigation_keymaps_register
from . import object_keymaps_register
from . import pipeline_keymaps_register
from . import sculpt_keymaps_register
from . import selection_keymaps_register
from . import transform_keymaps_register
from . import uv_keymaps_register

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS

TOOL_NAME = 'Keymaps'

# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

keymap_module_lst = (
    mesh_keymaps_register,
    navigation_keymaps_register,
    object_keymaps_register,
    pipeline_keymaps_register,
    sculpt_keymaps_register,
    selection_keymaps_register,
    transform_keymaps_register,
    uv_keymaps_register,
)


def register():
    total_registered_keymaps = 0

    log(Severity.INFO, TOOL_NAME, f'=== Registering {TOOL_NAME} ===')

    # Register standard keymaps
    for module in keymap_module_lst:

        # Verbose header per category
        if is_verbose(VERBOSE_KEYMAPS):
            log(Severity.DEBUG, f'{module.KEYMAP_CATEGORY} Keymaps', 'Registering keymap bindings...')

        registered_count = module.register()
        total_registered_keymaps += registered_count

        log(Severity.INFO, f'{module.KEYMAP_CATEGORY} Keymaps', f'Registered {registered_count} keymaps.')

    # Register pie keymaps
    if is_verbose(VERBOSE_KEYMAPS):
        log(Severity.DEBUG, f'{pie_keymaps_register.KEYMAP_CATEGORY} Keymaps', 'Registering keymap bindings...')

    pie_registered_count = pie_keymaps_register.register()
    total_registered_keymaps += pie_registered_count

    log(Severity.INFO, f'{pie_keymaps_register.KEYMAP_CATEGORY} Keymaps', f'Registered {pie_registered_count} keymaps.')

    log(Severity.INFO, TOOL_NAME, f'Registration complete (Total: {total_registered_keymaps})')


def unregister():
    total_unregistered_keymaps = 0

    log(Severity.INFO, TOOL_NAME, '=== Unregistering Keymaps ===')

    # Unregister pie keymaps first
    pie_unregistered_count = pie_keymaps_register.unregister()
    total_unregistered_keymaps += pie_unregistered_count
    log(Severity.INFO, pie_keymaps_register.KEYMAP_CATEGORY, f'Unregistered {pie_unregistered_count} keymaps.')

    # Unregister standard keymaps in reverse order
    for module in reversed(keymap_module_lst):
        unregistered_count = module.unregister()
        total_unregistered_keymaps += unregistered_count
        log(Severity.INFO, module.KEYMAP_CATEGORY, f'Unregistered {unregistered_count} keymaps.')

    log(Severity.INFO, TOOL_NAME, f'Unregistration complete (Total: {total_unregistered_keymaps})')


def refresh():
    log(Severity.INFO, TOOL_NAME, 'Refreshing keymaps...')
    unregister()
    register()
    log(Severity.INFO, TOOL_NAME, 'Refreshing keymaps completed!')
