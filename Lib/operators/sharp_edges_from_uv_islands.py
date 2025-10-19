import bpy
import bmesh


class SharpEdgesFromUvIslands(bpy.types.Operator):
    bl_idname = "uv.toolkit_sharp_edges_from_uv_islands"
    bl_label = "Sharp Edges From UV Islands"
    bl_description = "Sharp Edges From UV Islands"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        current_mode = context.object.mode
        active_object = context.view_layer.objects.active

        if context.object.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        for obj in context.selected_objects:
            context.view_layer.objects.active = obj
            bpy.ops.mesh.customdata_custom_splitnormals_clear()

            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            for f in bm.faces:
                f.smooth = True
                for l in f.loops:
                    l.edge.smooth = True

            if obj.type == 'MESH':
                context.object.data.use_auto_smooth = True
                context.object.data.auto_smooth_angle = 3.14159

        bpy.ops.uv.seams_from_islands(mark_seams=False, mark_sharp=True)

        context.view_layer.objects.active = active_object
        bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}
