"""Callbacks to integrate source control to Blender Open/Load/Save"""

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
from bpy.app.handlers import persistent
import BlueHole.blenderUtils.sourceControlUtils as scUtils


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

@persistent
def load_pre_handler(scene):
    print("Event: load_pre")


@persistent
def load_post_handler(scene):
    print("Event: load_post")
    scUtils.sc_check_blend(silent_mode=True)  # Checks status with perforce and prompt to get latest, checkout, etc.


@persistent
def save_pre_handler(scene):
    print("Event: save_pre")


@persistent
def save_post_handler(scene):
    print("Event: save_post")
    scUtils.sc_check_blend(silent_mode=True)  # Checks status with perforce and prompt to get latest, checkout, etc.


class OBJECT_OT_dummy(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.dummy"
    bl_label = "Dummy operator"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("Dummy operator executing")
        return {'FINISHED'}


def call_load_handlers(scene):

    for func in bpy.app.handlers.load_pre:
        func(scene)

    for func in bpy.app.handlers.load_post:
        func(scene)

    print("Load handlers called (should only occur on addon enabling / reload)")

    # bpy.app.handlers.scene_update_post.remove(call_load_handlers)


def register():
    print("Registering callbacks...")
    # other stuff here!
    bpy.app.handlers.load_pre.append(load_pre_handler)
    bpy.app.handlers.load_post.append(load_post_handler)
    bpy.app.handlers.save_pre.append(save_pre_handler)
    bpy.app.handlers.save_post.append(save_post_handler)
    bpy.app.handlers.depsgraph_update_post.append(call_load_handlers)


def unregister():
    print("Unregistering callbacks...")
    bpy.app.handlers.load_pre.remove(load_pre_handler)
    bpy.app.handlers.load_post.remove(load_post_handler)
    bpy.app.handlers.save_pre.remove(save_pre_handler)
    bpy.app.handlers.save_post.remove(save_post_handler)
