import bpy


class ToggleColorMode(bpy.types.Operator):
    bl_idname = "uv.toolkit_toggle_color_mode"
    bl_label = "Toggle Color Mode"
    bl_description = "Show or hide texture in viewport"

    def execute(self, context):

        for area in bpy.context.workspace.screens[0].areas:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    if space.shading.type != 'WIREFRAME':
                        if space.shading.color_type == 'TEXTURE':
                            space.shading.color_type = 'OBJECT'
                        else:
                            space.shading.color_type = 'TEXTURE'
        return {'FINISHED'}
