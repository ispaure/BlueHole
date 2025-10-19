"""
Adds Blue Hole Blender Operators [Music]
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "GNU General Public License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

import bpy

from BlueHole.blenderUtils.fileUtils import open_url
import BlueHole.blenderUtils.debugUtils as debugUtils
import BlueHole.envUtils.envUtils as envUtils


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

# Start of File Debug Message
debugUtils.print_debug_msg('\nLoading Music Menu and Operators...', show_verbose)


# ----------------------------------------------------------------------------------------------------------------------
# MENUS

class BLUE_HOLE_MT_music(bpy.types.Menu):
    bl_label = 'Music'

    def draw(self, context):
        layout = self.layout
        for cls in classes:
            layout.operator(cls.bl_idname, icon='SOUND')
        # Draw additional operators from the active environment (if available)
        envUtils.draw_current_env_menu_items('globalMusic', layout)

# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class MusicGenshinImpactOST(bpy.types.Operator):

    bl_idname = "wm.bh_music_genshinimpact_ost"
    bl_label = 'Genshin Impact Soundtrack'

    def execute(self, context):
        open_url('https://www.youtube.com/watch?v=nGDk6JqfQu0&ab_channel=BunnyHelp')
        return {'FINISHED'}


class MusicLoFiHipHopRadio(bpy.types.Operator):

    bl_idname = "wm.bh_music_lofi"
    bl_label = 'Lofi Hip Hop Radio'

    def execute(self, context):
        open_url('https://www.youtube.com/watch?v=5qap5aO4i9A&ab_channel=ChilledCow')
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (MusicGenshinImpactOST,
           MusicLoFiHipHopRadio
           )


# Register
def register():
    # Register Menu
    bpy.utils.register_class(BLUE_HOLE_MT_music)
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    # Unregister Menu
    bpy.utils.unregister_class(BLUE_HOLE_MT_music)
    # Unregister Operators
    for cls in classes:
        bpy.utils.unregister_class(cls)


# ----------------------------------------------------------------------------------------------------------------------
# End of File Debug Message
debugUtils.print_debug_msg('Music Menu and Operators Loaded!', show_verbose)
