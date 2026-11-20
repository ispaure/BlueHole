"""
Operators that did not fit in another category
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
from bpy.props import *
from ..Lib.commonUtils.integrations.web import open_url
from ..Lib.commonUtils.runtime.diagnostics import Severity, log
from ..overlays.deluxe import applyDeluxePrefs
from ..preferences.prefs import prefs
from ..keymaps import keymap_utils
from ..keymaps.event_overlap import events_overlap

# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


def _keymap_error(operator, context, error, message):
    log(Severity.ERROR, operator.bl_label, f'{type(error).__name__}: {message}')
    if not bpy.app.background:
        def draw(menu, _context):
            menu.layout.label(text=message)

        context.window_manager.popup_menu(draw, title=operator.bl_label, icon='ERROR')
    operator.report({'WARNING'}, message)
    return {'CANCELLED'}


def _report_keymap_preference(operator, context, message):
    if not context.preferences.use_preferences_save:
        message += ' Use Save Preferences to keep this choice after restarting Blender.'
    operator.report({'INFO'}, message)


class WM_OT_URLOpen(bpy.types.Operator):
    """Open a website in the web-browser"""
    bl_idname = "wm.bh_open_url"
    bl_label = ""
    bl_options = {'INTERNAL'}

    url: StringProperty(
        name="URL",
        description="URL to open",
    )

    def execute(self, _context):
        open_url(self.url)
        return {'FINISHED'}


class WM_OT_Apply_Deluxe_Prefs(bpy.types.Operator):
    """Enable the Deluxe shortcut catalog on the built-in Blender preset"""
    bl_idname = "wm.bh_apply_deluxe_prefs"
    bl_label = "Enable Blue Hole Keymaps & Pie Menus"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        try:
            applyDeluxePrefs.apply_deluxe_prefs(context, prefs().prefs)
        except Exception as error:
            message = str(error) if isinstance(error, (ValueError, applyDeluxePrefs.ActivationError)) else (
                'Blender could not apply Deluxe keymaps. See the Blue Hole log and try again.')
            return _keymap_error(self, context, error, message)
        _report_keymap_preference(self, context, 'Blue Hole Keymaps & Pie Menus enabled.')
        return {'FINISHED'}


class WM_OT_Disable_Deluxe_Keymaps(bpy.types.Operator):
    """Disable Deluxe shortcuts and keep your feature settings"""
    bl_idname = "wm.bh_disable_deluxe_keymaps"
    bl_label = "Disable Blue Hole Keymaps & Pie Menus"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        applyDeluxePrefs.disable_deluxe_keymaps(context, prefs().prefs)
        _report_keymap_preference(self, context, 'Blue Hole Keymaps & Pie Menus disabled.')
        return {'FINISHED'}


class WM_OT_BH_dopesheet_frame_jump(bpy.types.Operator):
    """Jump to the scene boundary from the Dope Sheet window"""
    bl_idname = 'wm.bh_dopesheet_frame_jump'
    bl_label = 'Dope Sheet Frame Jump'
    bl_options = {'INTERNAL'}

    end: BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        area, region = context.area, context.region
        return (area is not None and area.type == 'DOPESHEET_EDITOR'
                and region is not None and region.type == 'WINDOW'
                and bpy.ops.screen.frame_jump.poll())

    def execute(self, context):
        return bpy.ops.screen.frame_jump(end=self.end)


_STOCK_NODE_LINK = keymap_utils.KeymapSelector(
    keymap_utils.KeymapScope('Node Editor', 'NODE_EDITOR'),
    keymap_utils.KeymapEvent('LEFTMOUSE', 'CLICK_DRAG', map_type='MOUSE'),
    keymap_utils.KeymapTarget('node.link', {
        'delay': .5, 'detach': False, 'drag_start': (0.0, 0.0),
        'inside_padding': 2.0, 'max_speed': 26.0, 'outside_padding': 0.0,
        'speed_ramp': 1.0, 'zoom_influence': .5,
    }))


def _stock_node_link_available():
    selector = _STOCK_NODE_LINK
    try:
        default = keymap_utils.configuration('default')
        if not keymap_utils.same_identity(keymap_utils.configuration('active'), default):
            return False
        _, _, source = keymap_utils.exact_source(selector)
        merged = keymap_utils.matching_map(keymap_utils.configuration('user'), selector.scope)
        item = merged.keymap_items.from_id(source.id)
        if (item is None or item.is_user_modified or item.is_user_defined
                or keymap_utils.snapshot_item(item, False) != (selector.event, selector.target, True)):
            return False
        return not any(
            row.active and (row.is_user_modified or row.is_user_defined)
            and events_overlap(keymap_utils.capture_event(row), selector.event)
            for row in merged.keymap_items)
    except (keymap_utils.Pending, AttributeError, ReferenceError, RuntimeError):
        return False


class NODE_OT_BH_link_socket(bpy.types.Macro):
    """Give Blender's inherited socket drag first refusal over Deluxe node movement"""
    bl_idname = 'node.bh_link_socket'
    bl_label = 'Link Node Socket'
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO', 'BLOCKING'}

    @classmethod
    def poll(cls, context):
        area, region = context.area, context.region
        return (area is not None and area.type == 'NODE_EDITOR'
                and region is not None and region.type == 'WINDOW'
                and _stock_node_link_available())


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (
    WM_OT_URLOpen,
    WM_OT_Apply_Deluxe_Prefs,
    WM_OT_Disable_Deluxe_Keymaps,
    WM_OT_BH_dopesheet_frame_jump,
    NODE_OT_BH_link_socket,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # A native macro forwards the original click-drag event and its press
    # coordinates to Blender's socket hit test.
    NODE_OT_BH_link_socket.define('NODE_OT_link').properties.detach = False


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
