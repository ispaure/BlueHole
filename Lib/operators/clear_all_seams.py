import bpy
import bmesh


class ClearAllSeams(bpy.types.Operator):
    bl_idname = "uv.toolkit_clear_all_seams"
    bl_label = "Clear All Seams"
    bl_description = "Clear all seams"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        active_object = context.view_layer.objects.active

        for obj in context.selected_objects:
            context.view_layer.objects.active = obj

            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            for e in bm.edges:
                e.seam = False

            bmesh.update_edit_mesh(me)
        context.view_layer.objects.active = active_object
        return {'FINISHED'}
