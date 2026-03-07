"""Callbacks to integrate source control to Blender Open/Load/Save"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://github.com/ispaure/BlueHole

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

import bpy
from . import sourceControlUtils, blenderFile


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# STATE

_sc_check_timer_registered = False


# ----------------------------------------------------------------------------------------------------------------------
# INTERNAL HELPERS

def _log(msg: str) -> None:
    if show_verbose:
        print(msg)


def _has_valid_blend_path() -> bool:
    return len(blenderFile.get_blend_file_path()) > 0


def _get_ui_override_context() -> dict | None:
    """
    Return a valid UI override context once Blender has finished creating a usable window/screen/area/region.
    Returns None while UI is still not ready.
    """
    wm = bpy.context.window_manager
    if wm is None or not wm.windows:
        return None

    window = wm.windows[0]
    screen = window.screen
    if screen is None or not screen.areas:
        return None

    # Prefer VIEW_3D, but fall back to the first available area
    area = next((area for area in screen.areas if area.type == 'VIEW_3D'), screen.areas[0])
    region = next((region for region in area.regions if region.type == 'WINDOW'), None)

    if region is None:
        return None

    return {
        'window': window,
        'screen': screen,
        'area': area,
        'region': region,
    }


def _run_sc_check_deferred() -> float | None:
    """
    Timer callback.
    Wait until Blender UI is fully ready, then run the source-control prompt once.
    Return a float to retry later, or None to stop the timer.
    """
    global _sc_check_timer_registered

    if not _has_valid_blend_path():
        _log("SC deferred check cancelled: no blend file path")
        _sc_check_timer_registered = False
        return None

    override_ctx = _get_ui_override_context()
    if override_ctx is None:
        _log("SC deferred check waiting for Blender UI...")
        return 0.15

    try:
        _log("SC deferred check running")
        with bpy.context.temp_override(**override_ctx):
            sourceControlUtils.sc_check_blend(silent_mode=False)

    except Exception as ex:
        print(f"Source-control deferred check failed: {ex}")

    _sc_check_timer_registered = False
    return None


def _queue_sc_check() -> None:
    """
    Queue a single deferred source-control check.
    Prevent duplicate timer registration.
    """
    global _sc_check_timer_registered

    if _sc_check_timer_registered:
        _log("SC deferred check already queued")
        return

    if not _has_valid_blend_path():
        _log("SC deferred check not queued: no blend file path")
        return

    _sc_check_timer_registered = True
    bpy.app.timers.register(_run_sc_check_deferred, first_interval=0.25)
    _log("SC deferred check queued")


# ----------------------------------------------------------------------------------------------------------------------
# HANDLERS

@bpy.app.handlers.persistent
def load_pre_handler(scene):
    print("Event: load_pre")


@bpy.app.handlers.persistent
def load_post_handler(scene):
    print("Event: load_post")
    _queue_sc_check()


@bpy.app.handlers.persistent
def save_pre_handler(scene):
    print("Event: save_pre")

    if _has_valid_blend_path():
        sourceControlUtils.sc_check_blend(silent_mode=False)


@bpy.app.handlers.persistent
def save_post_handler(scene):
    print("Event: save_post")


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


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER

def register():
    print("Registering callbacks...")
    bpy.app.handlers.load_pre.append(load_pre_handler)
    bpy.app.handlers.load_post.append(load_post_handler)
    bpy.app.handlers.save_pre.append(save_pre_handler)
    bpy.app.handlers.save_post.append(save_post_handler)

    # # supposedly not needed anymore and throws errors
    # bpy.app.handlers.depsgraph_update_post.append(call_load_handlers)


def unregister():
    global _sc_check_timer_registered

    print("Unregistering callbacks...")

    if load_pre_handler in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.remove(load_pre_handler)

    if load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_post_handler)

    if save_pre_handler in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(save_pre_handler)

    if save_post_handler in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.remove(save_post_handler)

    _sc_check_timer_registered = False
