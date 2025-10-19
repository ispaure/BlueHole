import bpy
import bmesh
from bpy.props import BoolProperty, EnumProperty


class UnwrapSelected(bpy.types.Operator):
    bl_idname = "uv.toolkit_unwrap_selected"
    bl_label = "Unwrap Selected"
    bl_description = "Unwrap selected faces"
    bl_options = {'REGISTER', 'UNDO'}

    unwrap_method: EnumProperty(
        items=[
            ("ANGLE_BASED", "Angle Based", "", "", 0),
            ("CONFORMAL", "Conformal", "", "", 1)
        ],
        default="ANGLE_BASED",
        name="Method",
        description="Unwrapping method (Angle Based usually gives better results than Conformal. while being somewhat slower)",
    )

    fill_holes: BoolProperty(
        name="Fill Holes",
        default=True,
        description="Virtual fill holes in mesh before unwrapping, to better avoid overlaps and preserve symmetry."
    )

    correct_aspect: BoolProperty(
        name="Correct Aspect",
        default=True,
        description="Map UVs taking image aspect ratio into account."
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        tool_settings = context.scene.tool_settings
        if tool_settings.use_uv_select_sync:
            self.report({'INFO'}, 'Need to disable UV Sync')
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

            pinned_luvs = []
            selected_luvs = []
            initial_seams = []
            selected_faces = [f for f in bm.faces]

            for f in selected_faces:
                for l in f.loops:
                    luv = l[uv_layer]
                    if luv.select:
                        selected_luvs.append(luv)

            if selected_luvs == []:
                bpy.ops.object.mode_set(mode='OBJECT')
                obj.select_set(state=False)
                continue

            for f in selected_faces:
                for l in f.loops:
                    if l.edge.seam:
                        initial_seams.append(l.edge)
                    luv = l[uv_layer]
                    if luv.pin_uv:
                        pinned_luvs.append(luv)
                        luv.pin_uv = False
                    if luv.select:
                        luv.select = False
                    else:
                        luv.pin_uv = True
                        luv.select = True

            bpy.ops.uv.seams_from_islands(mark_seams=True, mark_sharp=False)

            bpy.ops.uv.unwrap(method=self.unwrap_method, fill_holes=self.fill_holes, correct_aspect=self.correct_aspect)

            for f in selected_faces:
                for l in f.loops:
                    l.edge.seam = False
                    luv = l[uv_layer]
                    luv.pin_uv = False
                    luv.select = False

            for luv in pinned_luvs:
                luv.pin_uv = True

            for luv in selected_luvs:
                luv.select = True

            for e in initial_seams:
                e.seam = True

            bpy.ops.object.mode_set(mode='OBJECT')
            obj.select_set(state=False)

        for obj in selected_obj:
            obj.select_set(state=True)

        bpy.ops.object.mode_set(mode='EDIT')
        context.view_layer.objects.active = active_object
        return {'FINISHED'}
