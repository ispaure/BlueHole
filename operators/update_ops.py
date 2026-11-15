"""Explicit user actions; automatic checks never install an update."""
import bpy
from ..blenderUtils import addon_updates


class BH_OT_check_update(bpy.types.Operator):
    bl_idname = 'wm.bh_check_update'
    bl_label = 'Check for Blue Hole Updates'
    bl_description = 'Find the newest compatible Blender branch in your selected update channel'

    def execute(self, _context):
        try:
            addon_updates.start('check')
        except Exception as error:
            self.report({'WARNING'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class BH_OT_update_addon(bpy.types.Operator):
    bl_idname = 'wm.bh_update_addon'
    bl_label = 'Update Blue Hole'
    bl_description = 'Download and reload Blue Hole in place; preserve custom environments and update the default environment'

    def execute(self, _context):
        try:
            addon_updates.start('install')
        except Exception as error:
            self.report({'WARNING'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


def register():
    for cls in (BH_OT_check_update, BH_OT_update_addon):
        bpy.utils.register_class(cls)


def unregister():
    for cls in (BH_OT_update_addon, BH_OT_check_update):
        bpy.utils.unregister_class(cls)
