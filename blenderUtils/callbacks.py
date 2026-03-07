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

_sc_check_pending = False
_sc_check_timer_running = False


# ----------------------------------------------------------------------------------------------------------------------
# HELPERS

def _log(msg: str) -> None:
    if show_verbose:
        print(msg)


def _has_blend_file() -> bool:
    return len(blenderFile.get_blend_file_path()) > 0


def _is_ui_ready() -> bool:
    wm = bpy.context.window_manager
    if wm is None:
        return False

    if not wm.windows:
        return False

    window = wm.windows[0]
    if window is None:
        return False

    screen = window.screen
    if screen is None:
        return False

    if not screen.areas:
        return False

    return True


def _deferred_sc_check_timer():
    """
    Run after Blender returns to its normal event loop.
    Keep retrying until a real UI exists, then invoke the operator once.
    """
    global _sc_check_pending
    global _sc_check_timer_running

    if not _sc_check_pending:
        _sc_check_timer_running = False
        _log("SC timer stopped: nothing pending")
        return None

    if not _has_blend_file():
        _sc_check_pending = False
        _sc_check_timer_running = False
        _log("SC timer stopped: no blend file")
        return None

    if not _is_ui_ready():
        _log("SC timer waiting for UI...")
        return 0.1

    _log("SC timer invoking startup operator")
    _sc_check_pending = False
    _sc_check_timer_running = False

    try:
        bpy.ops.wm.bh_sc_startup_check('INVOKE_DEFAULT')
    except Exception as ex:
        print(f"Failed to invoke startup SC operator: {ex}")

    return None


def _queue_startup_sc_check() -> None:
    global _sc_check_pending
    global _sc_check_timer_running

    if not _has_blend_file():
        _log("SC startup check not queued: no blend file")
        return

    _sc_check_pending = True

    if _sc_check_timer_running:
        _log("SC startup check already queued")
        return

    _sc_check_timer_running = True
    bpy.app.timers.register(_deferred_sc_check_timer, first_interval=0.0)
    _log("SC startup check queued")


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS

class WM_OT_bh_sc_startup_check(bpy.types.Operator):
    """
    Deferred source-control startup check.
    Runs only after Blender has returned to the event loop.
    """
    bl_idname = "wm.bh_sc_startup_check"
    bl_label = "Blue Hole Source Control Startup Check"

    def invoke(self, context, event):
        _log("Startup SC operator invoke")
        return self.execute(context)

    def execute(self, context):
        _log("Startup SC operator execute")

        if not _has_blend_file():
            _log("Startup SC operator cancelled: no blend file")
            return {'CANCELLED'}

        try:
            sourceControlUtils.sc_check_blend(
                silent_mode=False
            )  # Checks status with perforce and prompt to get latest, checkout, etc.
        except Exception as ex:
            print(f"Startup SC check failed: {ex}")
            return {'CANCELLED'}

        return {'FINISHED'}


class OBJECT_OT_dummy(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.dummy"
    bl_label = "Dummy operator"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("Dummy operator executing")
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# HANDLERS

@bpy.app.handlers.persistent
def load_pre_handler(scene):
    print("Event: load_pre")


@bpy.app.handlers.persistent
def load_post_handler(scene):
    print("Event: load_post")
    _queue_startup_sc_check()


@bpy.app.handlers.persistent
def save_pre_handler(scene):
    print("Event: save_pre")
    if _has_blend_file():
        sourceControlUtils.sc_check_blend(
            silent_mode=False
        )  # Checks status with perforce and prompt to get latest, checkout, etc.


@bpy.app.handlers.persistent
def save_post_handler(scene):
    print("Event: save_post")


# ----------------------------------------------------------------------------------------------------------------------
# DEV HELPER

def call_load_handlers(scene):
    for func in bpy.app.handlers.load_pre:
        func(scene)

    for func in bpy.app.handlers.load_post:
        func(scene)

    print("Load handlers called (should only occur on addon enabling / reload)")

    # bpy.app.handlers.scene_update_post.remove(call_load_handlers)


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER

_CLASSES = (
    WM_OT_bh_sc_startup_check,
    OBJECT_OT_dummy,
)


def register():
    print("Registering callbacks...")

    for cls in _CLASSES:
        bpy.utils.register_class(cls)

    if load_pre_handler not in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.append(load_pre_handler)

    if load_post_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_post_handler)

    if save_pre_handler not in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.append(save_pre_handler)

    if save_post_handler not in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.append(save_post_handler)

    # # supposedly not needed anymore and throws errors
    # bpy.app.handlers.depsgraph_update_post.append(call_load_handlers)


def unregister():
    global _sc_check_pending
    global _sc_check_timer_running

    print("Unregistering callbacks...")

    if load_pre_handler in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.remove(load_pre_handler)

    if load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_post_handler)

    if save_pre_handler in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(save_pre_handler)

    if save_post_handler in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.remove(save_post_handler)

    for cls in reversed(_CLASSES):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass

    _sc_check_pending = False
    _sc_check_timer_running = False
