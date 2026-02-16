"""
Pie Menu operators pertaining to HardOps
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS

# Blue Hole
from ....blenderUtils import addonUtils


# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU BUTTON

def quick_pipe(pie):
    if addonUtils.is_addon_enabled_and_loaded('hardops') or addonUtils.is_addon_enabled_and_loaded('HOps'):
        # TODO: Find equivalent if HardOps not installed
        pie.operator("hops.edge2curve", text="Quick Pipe", icon='OUTLINER_OB_GREASEPENCIL')
    else:
        pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')


def twist_array(pie):
    if addonUtils.is_addon_enabled_and_loaded('HOps') or addonUtils.is_addon_enabled_and_loaded('hardops'):
        pie.operator("hops.array_twist", text="Twist Array", icon='ALIASED')
    else:
        pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')


def lattice(pie):
    if addonUtils.is_addon_enabled_and_loaded('HOps') or addonUtils.is_addon_enabled_and_loaded('hardops'):
        pie.operator("hops.mod_lattice", text="Lattice", icon='MOD_LATTICE')
    else:
        pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')


def subdiv_modifier(pie):
    if addonUtils.is_addon_enabled_and_loaded('HOps') or addonUtils.is_addon_enabled_and_loaded('hardops'):
        pie.operator("hops.mod_subdivision", text="Add Subdivision Modifier", icon='MOD_SUBSURF')
    else:
        pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')


def radial_array(pie):
    if addonUtils.is_addon_enabled_and_loaded('HOps') or addonUtils.is_addon_enabled_and_loaded('hardops'):
        pie.operator("hops.radial_array", text="Radial Array", icon='OUTLINER_DATA_POINTCLOUD')
    else:
        pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')


def array(pie):
    if addonUtils.is_addon_enabled_and_loaded('HOps') or addonUtils.is_addon_enabled_and_loaded('hardops'):
        pie.operator("hops.st3_array", text="Array", icon='MOD_ARRAY')
    else:
        pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')


def modifier_toggle(pie):
    if addonUtils.is_addon_enabled_and_loaded('HOps') or addonUtils.is_addon_enabled_and_loaded('hardops'):
        pie.operator('hops.bool_toggle_viewport', text='Modifier Toggle', icon='QUIT').all_modifiers = True
    else:
        pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')


def apply_modifier(pie):
    if addonUtils.is_addon_enabled_and_loaded('HOps') or addonUtils.is_addon_enabled_and_loaded('hardops'):
        pie.operator("hops.mod_apply", text="Apply Modifier", icon='OUTPUT')
    else:
        pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')


# TODO: Investigate why there is two of this, maybe one is an old command. they both have a button in use in UI
def apply_modifier_2(pie):
    if addonUtils.is_addon_enabled_and_loaded('HOps') or addonUtils.is_addon_enabled_and_loaded('hardops'):
        pie.operator("hops.apply_modifiers", text="Apply Modifiers", icon='MODIFIER_DATA')
    else:
        pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')
