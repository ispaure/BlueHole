import bpy


class SplitFaces(bpy.types.Operator):
    bl_idname = "uv.toolkit_split_faces"
    bl_label = "Split Faces"
    bl_description = "Split Faces"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        if context.scene.tool_settings.use_uv_select_sync:
            self.report({'INFO'}, "Need to disable UV Sync")
            return {'CANCELLED'}

        bpy.ops.uv.select_split()
        bpy.ops.transform.translate('INVOKE_DEFAULT')

        return {'FINISHED'}
