import bpy
import bmesh


class InvertLocal(bpy.types.Operator):
    bl_idname = "uv.toolkit_invert_local"
    bl_label = "Invert Local"
    bl_description = "Invert selection only inside the islands"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        if context.scene.tool_settings.use_uv_select_sync:
            self.report({'INFO'}, "Need to disable UV Sync")
            return {'CANCELLED'}

        active_object = context.view_layer.objects.active

        bpy.ops.object.mode_set(mode='OBJECT')

        selected_obj = [obj for obj in context.selected_objects]

        for obj in selected_obj:
            obj.select_set(state=False)

        for obj in selected_obj:
            context.view_layer.objects.active = obj
            obj.select_set(state=True)

            bpy.ops.object.mode_set(mode='EDIT')

            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            uv_layer = bm.loops.layers.uv.verify()

            selected_luvs = []

            for f in bm.faces:
                for l in f.loops:
                    luv = l[uv_layer]
                    if luv.select:
                        selected_luvs.append(luv)

            bpy.ops.uv.select_linked()

            for luv in selected_luvs:
                luv.select = False

            bpy.ops.object.mode_set(mode='OBJECT')
            obj.select_set(state=False)

        for obj in selected_obj:
            obj.select_set(state=True)

        bpy.ops.object.mode_set(mode='EDIT')
        context.view_layer.objects.active = active_object
        return {'FINISHED'}
