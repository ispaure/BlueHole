"""
Operators for music
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
from BlueHole.blenderUtils.fileUtils import open_url


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


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators
