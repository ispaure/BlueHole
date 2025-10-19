import bpy


class UvSyncMode(bpy.types.Operator):
    bl_idname = "uv.toolkit_sync_mode"
    bl_label = "UV Sync mode"
    bl_description = "UV sync mode"

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        tool_settings = context.scene.tool_settings
        addon_prefs = context.preferences.addons["uv_toolkit"].preferences

        tool_settings.use_uv_select_sync = not tool_settings.use_uv_select_sync

        vertex = (True, False, False)
        edge = (False, True, False)
        face = (False, False, True)

        if tool_settings.use_uv_select_sync:

            self.report({'WARNING'}, 'UV Sync Active')

            if addon_prefs.uv_sync_selection_mode == "enable":
                if tool_settings.uv_select_mode == 'VERTEX':
                    context.tool_settings.mesh_select_mode = vertex
                if tool_settings.uv_select_mode == 'EDGE':
                    context.tool_settings.mesh_select_mode = edge
                if tool_settings.uv_select_mode == 'FACE':
                    context.tool_settings.mesh_select_mode = face

            if addon_prefs.uv_sync_auto_select == "enable":
                bpy.ops.mesh.select_all(action='DESELECT')

        else:
            self.report({'INFO'}, 'UV Sync Disabled')

            if addon_prefs.uv_sync_selection_mode == "enable":
                if tuple(context.tool_settings.mesh_select_mode) == vertex:
                    tool_settings.uv_select_mode = 'VERTEX'
                if tuple(context.tool_settings.mesh_select_mode) == edge:
                    tool_settings.uv_select_mode = 'EDGE'
                if tuple(context.tool_settings.mesh_select_mode) == face:
                    tool_settings.uv_select_mode = 'FACE'

            if addon_prefs.uv_sync_auto_select == "enable":
                bpy.ops.mesh.select_all(action='SELECT')
        return {'FINISHED'}
