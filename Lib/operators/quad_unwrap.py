import bpy
import bmesh
from mathutils import Vector
from bpy.props import EnumProperty


class QuadUnwrap(bpy.types.Operator):
    bl_idname = "uv.toolkit_quad_unwrap"
    bl_label = "Quad Unwrap"
    bl_description = "Unwrap selection from to contiguous uniform quad layout"
    bl_options = {'UNDO', 'REGISTER'}

    mode: EnumProperty(
        items=[
            ("EVEN", "Even", "", "", 0),
            ("LENGTH", "Length", "", "", 1),
            ("LENGTH_AVERAGE", "Length Average", "", "", 2)
        ],
        default="LENGTH_AVERAGE",
        name="Edge Length Mode",
        description="Method to space UV edge loops.",
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        if context.scene.tool_settings.use_uv_select_sync:
            self.report({'INFO'}, "Need to disable UV Sync")
            return {'CANCELLED'}

        active_object = context.view_layer.objects.active

        current_mesh_select_mode = tuple(context.tool_settings.mesh_select_mode)

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

            luv_verts = []
            selected_luvs = []

            for f in bm.faces:
                for l in f.loops:
                    luv = l[uv_layer]
                    if luv.select:
                        selected_luvs.append(luv)
                        luv_verts.append(l.vert)

            if selected_luvs == []:
                bpy.ops.object.mode_set(mode='OBJECT')
                obj.select_set(state=False)
                continue

            context.scene.tool_settings.use_uv_select_sync = True
            bpy.ops.uv.select_all(action='DESELECT')
            context.tool_settings.mesh_select_mode = False, False, True

            for v in luv_verts:
                v.select = True

            # convert selected vetices to single face
            context.tool_settings.mesh_select_mode = True, False, False
            context.tool_settings.mesh_select_mode = False, False, True

            f = bm.faces.active

            if f is None:
                bpy.ops.object.mode_set(mode='OBJECT')
                obj.select_set(state=False)
                continue

            selected_verts = [v for v in f.verts if v.select]
            if len(selected_verts) != 4:
                bpy.ops.object.mode_set(mode='OBJECT')
                obj.select_set(state=False)
                continue

            bpy.ops.uv.select_linked()

            # Keith (http://wahooney.net) Boshoff 'Quad Unwrap'

            # get uvs and average edge lengths
            luv1 = f.loops[0][uv_layer]
            luv2 = f.loops[1][uv_layer]
            luv3 = f.loops[2][uv_layer]
            luv4 = f.loops[3][uv_layer]

            l1 = ((f.verts[0].co - f.verts[1].co).length + (f.verts[2].co - f.verts[3].co).length) / 2
            l2 = ((f.verts[1].co - f.verts[2].co).length + (f.verts[3].co - f.verts[0].co).length) / 2

            # Try to fit into old coords
            u = ((luv1.uv - luv2.uv).length + (luv3.uv - luv4.uv).length) / 2
            v = ((luv2.uv - luv3.uv).length + (luv4.uv - luv1.uv).length) / 2

            c = (luv1.uv + luv2.uv + luv3.uv + luv4.uv) / 4

            if l1 < l2:
                u = v * (l1 / l2)
            else:
                v = u * (l2 / l1)

            # try to fit into old coords
            luv1.uv = c + Vector((-u, -v)) / 2
            luv2.uv = c + Vector((u, -v)) / 2
            luv3.uv = c + Vector((u, v)) / 2
            luv4.uv = c + Vector((-u, v)) / 2

            bpy.ops.uv.follow_active_quads(mode=self.mode)

            bpy.ops.object.mode_set(mode='OBJECT')
            obj.select_set(state=False)

        for obj in selected_obj:
            obj.select_set(state=True)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        context.scene.tool_settings.use_uv_select_sync = False
        context.view_layer.objects.active = active_object
        context.tool_settings.mesh_select_mode = current_mesh_select_mode
        return {'FINISHED'}
