""" Class holding all the Blue Hole preferences through live proxy access. """

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

# ----------------------------------------------------------------------------------------------------------------------
# CODE


def addon_module_name() -> str:
    """
    Return the root add-on module name.

    Example:
        "BlueHole.preferences" -> "BlueHole"
        "BlueHole-beta.preferences" -> "BlueHole-beta"
    """
    return __package__.split('.', 1)[0]


def _addon_prefs():
    """
    Return the Blue Hole AddonPreferences instance, or None if it is unavailable.
    """
    addon_name: str = addon_module_name()
    addon = bpy.context.preferences.addons.get(addon_name)

    if addon is None:
        return None

    return addon.preferences


class _PrefsProxy:
    """
    Generic live proxy around Blender preference/property-group objects.

    This preserves the existing call pattern:
        prefs().keymap.transform.enable_transform_tools_modal

    without requiring one manual wrapper property per Blender property.
    """

    __slots__ = ('_target',)

    def __init__(self, target):
        object.__setattr__(self, '_target', target)

    def __getattr__(self, name):
        target = object.__getattribute__(self, '_target')
        value = getattr(target, name)

        # Wrap nested Blender PropertyGroups / structs so chained access keeps working.
        if hasattr(value, 'bl_rna'):
            return _PrefsProxy(value)

        return value

    def __setattr__(self, name, value):
        target = object.__getattribute__(self, '_target')
        setattr(target, name, value)

    def __bool__(self):
        return object.__getattribute__(self, '_target') is not None

    @property
    def _raw(self):
        """
        Return the raw wrapped Blender object.
        """
        return object.__getattribute__(self, '_target')

    def is_ready(self) -> bool:
        """
        Return True if the wrapped target exists.
        """
        return object.__getattribute__(self, '_target') is not None


class BHPrefs:
    """
    Root Blue Hole preferences accessor.

    Keeps the existing public usage style:
        prefs().general.active_environment
        prefs().keymap.enable_keymaps
        prefs().thirdparty.auto_constraints.enable_transform_tools_modal_autoconstraint
    """

    @property
    def prefs(self):
        return _addon_prefs()

    def is_ready(self) -> bool:
        return self.prefs is not None

    def __getattr__(self, name):
        p = self.prefs

        if p is None:
            raise AttributeError(
                f'Blue Hole preferences are not available, cannot access "{name}".'
            )

        value = getattr(p, name)

        if hasattr(value, 'bl_rna'):
            return _PrefsProxy(value)

        return value

    def __bool__(self):
        return self.prefs is not None


def prefs() -> BHPrefs:
    return BHPrefs()
