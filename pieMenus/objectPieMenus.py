# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "GNU General Public License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

from BlueHole.blenderUtils.debugUtils import print_debug_msg as print_debug_msg
from BlueHole.blenderUtils import filterUtils as filterUtils
import BlueHole.blenderUtils.addonUtils as addonUtils


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

import bpy
from bpy.types import (
        Menu,
        Operator,
        )
import os


# Pie Object - Tools
class PIE_MT_Object_Tools(Menu):
    bl_idname = "PIE_MT_object_tools"
    bl_label = "Blue Hole: Object > Tools (Modifiers)"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        if addonUtils.is_addon_enabled_and_loaded('HOps') or filterUtils.check_addon_loaded('hardops'):
            pie.operator("hops.mod_lattice", text="Lattice", icon='MOD_LATTICE')
        else:
            pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')
        # 6 - RIGHT
        if addonUtils.is_addon_enabled_and_loaded('HOps') or filterUtils.check_addon_loaded('hardops'):
            pie.operator("hops.st3_array", text="Array", icon='MOD_ARRAY')
        else:
            pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')
        # 2 - BOTTOM
        if addonUtils.is_addon_enabled_and_loaded('HOps') or filterUtils.check_addon_loaded('hardops'):
            pie.operator("hops.mirror_gizmo", text="Mirror Gizmo", icon='MOD_MIRROR')
        else:
            pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')
        # 8 - TOP
        pie.operator("wm.call_menu_pie", text="Modifiers Options...").name = 'PIE_MT_object_tools_more'
        # 7 - TOP - LEFT
        pie.operator("object.modifier_add", text="Weighted Normal", icon='NORMALS_VERTEX_FACE').type = 'WEIGHTED_NORMAL'
        # 9 - TOP - RIGHT
        if addonUtils.is_addon_enabled_and_loaded('HOps') or filterUtils.check_addon_loaded('hardops'):
            pie.operator("hops.array_twist", text="Twist Array", icon='ALIASED')
        else:
            pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')
        # 3 - BOTTOM - LEFT
        if addonUtils.is_addon_enabled_and_loaded('HOps') or filterUtils.check_addon_loaded('hardops'):
            pie.operator("hops.mod_subdivision", text="Add Subdivision Modifier", icon='MOD_SUBSURF')
        else:
            pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')
        # 1 - BOTTOM - RIGHT
        if addonUtils.is_addon_enabled_and_loaded('HOps') or filterUtils.check_addon_loaded('hardops'):
            pie.operator("hops.radial_array", text="Radial Array", icon='OUTLINER_DATA_POINTCLOUD')
        else:
            pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')


class PIE_MT_Object_Tools_More(Menu):
    bl_idname = "PIE_MT_object_tools_more"
    bl_label = "Blue Hole: Object > Tools (Modifiers) > More"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        pie.separator()
        # 2 - BOTTOM
        if addonUtils.is_addon_enabled_and_loaded('HOps') or filterUtils.check_addon_loaded('hardops'):
            pie.operator("hops.mod_apply", text="Apply Modifier", icon='OUTPUT')
        else:
            pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')
        # 8 - TOP
        pie.operator("object.make_links_data", text="Link/Transfer Data", icon='NETWORK_DRIVE').type = 'MODIFIERS'
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 3 - BOTTOM - LEFT
        pie.separator()
        # 1 - BOTTOM - RIGHT
        pie.separator()


# Pie Object - Hide
class PIE_MT_Object_Hide(Menu):
    bl_idname = "PIE_MT_object_hide"
    bl_label = "Blue Hole: Object > Hide"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("object.hide_view_clear", text="Reveal Hidden [All]").select = True
        # 6 - RIGHT
        if addonUtils.is_addon_enabled_and_loaded('MACHIN3tools'):
            pie.operator("machin3.focus", text="Isolate Selection [Toggle]").method = 'LOCAL_VIEW'
        else:
            pie.operator("wm.disabled_addon_machin3tools", text="Can't Show; MACHIN3tools add-on disabled!!!", icon='ERROR')
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        pie.operator("object.hide_view_set", text="Hide Selection")
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# Pie Object - Action
class PIE_MT_Object_Action(Menu):
    bl_idname = "PIE_MT_object_action"
    bl_label = "Blue Hole: Object > Action"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("object.location_clear", text="Clear Location", icon='FILE_REFRESH').clear_delta = False
        # 6 - RIGHT
        pie.operator("object.join", text="Join", icon='SELECT_EXTEND')
        # 2 - BOTTOM
        pie.operator("wm.call_menu_pie", text="More...").name = 'PIE_MT_object_action_more'
        # 8 - TOP
        pie.operator("wm.call_menu_pie", text="Select...").name = 'PIE_MT_object_action_select'
        # 7 - TOP - LEFT
        button = pie.operator("object.transform_apply", text="Apply Object Transform", icon='MOD_DATA_TRANSFER')
        button.location = True
        button.rotation = True
        button.scale = True
        # 9 - TOP - RIGHT
        if addonUtils.is_addon_enabled_and_loaded('interactivetoolsblender'):
            pie.operator("mesh.quick_pivot", text="Quick Pivot Setup", icon='ORIENTATION_GLOBAL')
        else:
            pie.operator("wm.disabled_addon_interactive_tools", text="Can't Show; InteractiveTools add-on disabled!!!",
                         icon='ERROR')
        # 1 - BOTTOM - LEFT
        pie.operator("object.parent_clear", text="Clear Parent", icon='LAYER_USED').type = 'CLEAR_KEEP_TRANSFORM'
        # 3 - BOTTOM - RIGHT
        button_2 = pie.operator("object.parent_set", text="Make Parent", icon='CON_TRACKTO')
        button_2.type = 'OBJECT'
        button_2.keep_transform = True


# Pie Object - Action Select
class PIE_MT_Object_Action_Select(Menu):
    bl_idname = "PIE_MT_object_action_select"
    bl_label = "Blue Hole: Object > Action > Select"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("object.select_grouped", text="Select Children", icon='PARTICLE_DATA').type = 'CHILDREN_RECURSIVE'
        # 6 - RIGHT
        pie.operator("object.select_grouped", text="Select Parent", icon='DRIVER').type = 'PARENT'
        # 2 - BOTTOM
        pie.operator("object.select_all", text="Invert", icon='OVERLAY').type = 'INVERT'
        # 8 - TOP
        pie.operator("object.select_grouped", text="Select Grouped", icon='GROUP').type = 'COLLECTION'
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


# Pie Object - Action More
class PIE_MT_Object_Action_More(Menu):
    bl_idname = "PIE_MT_object_action_more"
    bl_label = "Blue Hole: Object > Action > More"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("view3d.clean_mesh", text="Clean", icon='SHADERFX')
        # 6 - RIGHT
        if filterUtils.check_addon_loaded('HOps') or filterUtils.check_addon_loaded('hardops'):
            pie.operator("hops.apply_modifiers", text="Apply Modifiers", icon='MODIFIER_DATA')
        else:
            pie.operator("wm.disabled_addon_hardops", text="Can't Show; HardOps add-on disabled!!!", icon='ERROR')
        # 2 - BOTTOM
        pie.operator("object.duplicates_make_real", text="Make Instances Real", icon='UNLINKED')
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        pie.operator("object.convert", text="Convert to Curve", icon='MOD_CURVE').target = 'CURVE'
        # 9 - TOP - RIGHT
        pie.operator("object.convert", text="Convert to Mesh", icon='OUTLINER_OB_CURVE').target = 'MESH'
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


classes = (
    PIE_MT_Object_Hide,
    PIE_MT_Object_Tools,
    PIE_MT_Object_Tools_More,
    PIE_MT_Object_Action,
    PIE_MT_Object_Action_Select,
    PIE_MT_Object_Action_More
    )

addon_keymaps = []


def register():
    for cls in classes:
        print_debug_msg('Loading Pie Menu: ' + cls.bl_idname, show_verbose)
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
