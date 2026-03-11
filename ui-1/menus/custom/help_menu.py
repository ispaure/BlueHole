"""
Blue Hole Menus
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

# Blender
import bpy

# Blue Hole
from ....blenderUtils.uiUtils import show_label
from ....operators import help_ops

# ----------------------------------------------------------------------------------------------------------------------
# MENUS


class BLUE_HOLE_MT_help(bpy.types.Menu):
    bl_label = 'Help'
    bl_idname = "BLUE_HOLE_MT_help"

    def draw(self, context):
        layout = self.layout

        # Show Documentation Section
        show_label('DOCUMENTATION', layout)
        layout.operator(help_ops.OpenGuide.bl_idname, icon='URL')
        layout.operator(help_ops.OpenKeymapsList.bl_idname, icon='URL')
        layout.operator(help_ops.OpenPieMenusList.bl_idname, icon='URL')

        # Show Submit Feedback Button
        layout.separator()
        layout.operator(help_ops.SubmitFeedback.bl_idname, icon='WINDOW')
        layout.operator(help_ops.JoinBHDiscord.bl_idname, icon='FUND')


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (
    BLUE_HOLE_MT_help,
)


# Register
def register():
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
