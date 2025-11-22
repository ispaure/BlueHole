"""
Operators for sorting things
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


import bpy
import BlueHole.blenderUtils.sortUtils as sortUtils


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class SortSelectionOnWorldAxis(bpy.types.Operator):

    bl_idname = "wm.bh_sort_selection_world_axis"
    bl_label = "Sort (Selection) on World Axis"
    bl_description = "Sorts selected objects on a world axis, with specified offset"
    bl_options = {'INTERNAL'}

    # PROPERTIES
    # Number of Axis
    settings: bpy.props.EnumProperty(
        name = 'Settings',
        description = 'Settings to display',
        items = [('1AXIS', '1-Axis', 'Sort items in a straight line'),
                 ('2AXIS', '2-Axis [COMING SOON]', 'Sort items on a 2D grid. (Rows & Columns)')],
        default = '1AXIS')

    # 1-Axis
    axis_items = [('X', 'X', ''), ('Y', 'Y', ''), ('Z', 'Z', '')]
    world_axis: bpy.props.EnumProperty(name="World Axis",
                                        description="World Axis on which to sort selection.",
                                        items=axis_items,
                                        default='X'
                                        )

    # 2-Axis
    axis_items = [('XY', 'XY', ''), ('XZ', 'XZ', ''), ('YZ', 'YZ', '')]
    world_axis_2d: bpy.props.EnumProperty(name="World Axis",
                                        description="2 World Axis on which to sort selection.",
                                        items=axis_items,
                                        default='XY'
                                        )

    # Distance
    distance: bpy.props.FloatProperty(name="Distance (Meters)",
                                      description="Distance (in meters) to separate item pivots.",
                                      default=5)

    # Row Amount
    row_amt: bpy.props.IntProperty(name="Row Amount",
                                   description="Number of items to show in a given row.",
                                   default=10)

    #
    # def execute(self, context):
    #     return {'FINISHED'}

    # env_items_lst = envUtils.get_env_lst_enum_property()
    # # Active Environment
    # active_environment = bpy.props.EnumProperty(name="Active Environment",
    #                                  description="Defines the project directory structure.",
    #                                  items=env_items_lst,
    #                                  default='default'
    #                                  )

    def execute(self, context):
        if self.settings=='1AXIS':
            sortUtils.sort_selected(self.world_axis, self.distance)
        elif self.settings=='2AXIS':
            pass
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        column = layout.column(align=True)
        row = column.row(align=True)
        row.prop(self, 'settings', expand=True)

        # DISPLAY PARAMETERS

        # If 1-Axis
        if self.settings=='1AXIS':
            row = column.row()
            row.prop(self, 'world_axis')
            row = column.row()
            row.prop(self, 'distance')

        # If 2-Axis
        if self.settings=='2AXIS':
            row = column.row()
            row.prop(self, 'world_axis_2d')
            row = column.row()
            row.prop(self, 'distance')
            row = column.row()
            row.prop(self, 'row_amt')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class SearchReplaceNameSelection(bpy.types.Operator):

    bl_idname = "wm.bh_search_replace_name_selection"
    bl_label = "Search and Replace Name (Selection)"
    bl_description = "Search and replace in name of selected objects."
    bl_options = {'INTERNAL'}

    # PROPERTIES
    # Search
    search: bpy.props.StringProperty(name="Search", description="String to search for.", default='')

    # Replace
    replace: bpy.props.StringProperty(name="Replace", description="String to replace.", default='')

    def execute(self, context):
        sortUtils.search_replace_name_selected(self.search, self.replace)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class BatchRenameSelection(bpy.types.Operator):

    bl_idname = "wm.bh_batch_rename_selection"
    bl_label = "Batch Rename (Selection)"
    bl_description = "Rename objects in selection (with appended numbers at the end, example: \"_01\" )"
    bl_options = {'INTERNAL'}

    # PROPERTIES
    # Name
    name: bpy.props.StringProperty(name="Name", description="Base name of objects", default='')

    # Padding
    padding_choices = [('Automatic', 'Automatic', ''), ('1', '1', 'Example: _1'),
                       ('2', '2', 'Example: _01'), ('3', '3', 'Example: _001')]
    padding: bpy.props.EnumProperty(name="Padding",
                                    description="Amount of padding to add to numbers.",
                                    items=padding_choices,
                                    default='Automatic')

    def execute(self, context):
        sortUtils.batch_rename_selected(self.name, self.padding)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class FlipLastUnderscores(bpy.types.Operator):

    bl_idname = "wm.bh_flip_underscores"
    bl_label = "Flip Text On Each Sides of Last Underscore"
    bl_description = "Flips text between each sides of the last underscore."
    bl_options = {'INTERNAL'}

    def execute(self, context):
        sortUtils.flip_text_last_underscore()
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (SortSelectionOnWorldAxis,
           SearchReplaceNameSelection,
           BatchRenameSelection,
           FlipLastUnderscores)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators
