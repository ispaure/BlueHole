"""Activate Deluxe keymaps and help artists review legacy profiles."""

from hashlib import sha256
from pathlib import Path

import bpy

from ...Lib.commonUtils.runtime.diagnostics import Severity, log

LEGACY_PRESET = 'BH_Keymaps'
LEGACY_PREFERENCES_SIZE = 968903
LEGACY_PREFERENCES_HASH = 'bfa078420cbc20aee76d77f7e4e51f602977e35f62a8e11e82769d9cc14da314'
LOG_TITLE = 'Deluxe Keymaps'


class ActivationError(RuntimeError):
    """An activation failure with instructions suitable for the Preferences UI."""


def _preferences_path():
    return Path(bpy.utils.user_resource('CONFIG', path='userpref.blend'))


def _legacy_preset_path():
    return bpy.utils.preset_find(LEGACY_PRESET, 'keyconfig', display_name=False)


def has_legacy_profile(context):
    """Recognize installer artifacts, including an exact payload without its preset."""
    if legacy_preset_active(context) or _legacy_preset_path():
        return True
    path = _preferences_path()
    try:
        # The previous installer could leave a recovery copy in both locations.
        presets = Path(bpy.utils.user_resource('SCRIPTS', path='presets/keyconfig'))
        if (any(presets.glob(LEGACY_PRESET + '.py.previous-*'))
                and any(path.parent.glob(path.name + '.previous-*'))):
            return True
        return (path.stat().st_size == LEGACY_PREFERENCES_SIZE
                and sha256(path.read_bytes()).hexdigest() == LEGACY_PREFERENCES_HASH)
    except FileNotFoundError:
        return False
    except OSError:
        # An unreadable profile cannot be classified safely.
        return True


def legacy_preset_active(context):
    return context.preferences.keymap.active_keyconfig in {LEGACY_PRESET, 'BH Keymaps'}


def uses_blender_keyconfig(configs):
    return configs.default is not None and configs.active == configs.default


def needs_keymap_review(context, preference):
    if preference.keymap.deluxe_configured:
        return False
    configs = context.window_manager.keyconfigs
    return has_legacy_profile(context) or any(km.is_user_modified for km in configs.user.keymaps)


def _set_keymap_options(context, options, *, activating=False):
    # Set the backing values together and rebuild the runtime once.
    from ...keymaps import keymaps_register

    previous = [(group, name, group.get(name)) for group, name, _ in options]

    def write(group, name, value):
        if value is None:
            if name in group:
                del group[name]
        else:
            group[name] = value

    try:
        for group, name, value in options:
            write(group, name, value)
        count = keymaps_register.refresh()
        if activating and count is None:
            raise ActivationError('The keymap runtime is busy or still starting. Try again shortly.')
        if activating and keymaps_register.keymap_utils.pending_cleanup():
            raise ActivationError('Blender is still releasing prior keymaps. Try again shortly.')
    except Exception:
        for group, name, value in previous:
            write(group, name, value)
        try:
            keymaps_register.refresh()
        except Exception as rollback_error:
            log(Severity.ERROR, LOG_TITLE,
                f'Restoring the prior keymap registrations failed ({type(rollback_error).__name__}).')
            raise ActivationError('The previous preference choices were restored, but Blender could not '
                                  'rebuild their shortcuts. Reopen Blender before trying again.') from rollback_error
        raise
    context.preferences.is_dirty = True


def apply_deluxe_prefs(context, preference, *, reviewed=False):
    log(Severity.INFO, LOG_TITLE, 'Starting Deluxe keymap activation.')
    if (legacy_preset_active(context)
            or not uses_blender_keyconfig(context.window_manager.keyconfigs)):
        raise ValueError('Select Blender in Preferences > Keymap before enabling Deluxe Keymaps.')
    if needs_keymap_review(context, preference) and not reviewed:
        raise ValueError('Review the saved shortcuts before enabling Deluxe keymaps.')

    options = [(preference.keymap, 'deluxe_configured', True),
               (preference.keymap, 'enable_keymaps', True)]
    _set_keymap_options(context, options, activating=True)
    log(Severity.INFO, LOG_TITLE, 'Deluxe keymaps enabled for the Blender preset.')


def disable_deluxe_keymaps(context, preference):
    _set_keymap_options(context, [(preference.keymap, 'enable_keymaps', False)])
