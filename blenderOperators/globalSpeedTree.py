"""
Adds Blue Hole Blender Operators [SpeedTree]
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

import bpy
import BlueHole.blenderUtils.fileUtils as fileUtils
import BlueHole.blenderUtils.debugUtils as debugUtils
from BlueHole.blenderUtils.languageUtils import loc_str as loc_str
import BlueHole.envUtils.envUtils as envUtils


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS

# Start of File Debug Message
debugUtils.print_debug_msg('\nLoading Speedtree Atlas Baker Menu and Operators...', show_verbose)


# ----------------------------------------------------------------------------------------------------------------------
# MENUS

class BLUE_HOLE_MT_speedtree(bpy.types.Menu):
    bl_label = 'Speedtree'

    def draw(self, context):
        layout = self.layout
        layout.operator(SpeedTreeBakeDocumentation.bl_idname, icon='KEYTYPE_EXTREME_VEC')
        layout.operator(SpeedTreeBake512.bl_idname)
        layout.operator(SpeedTreeBake1024.bl_idname)
        layout.operator(SpeedTreeBake2048.bl_idname)
        # Draw additional operators from the active environment (if available)
        envUtils.draw_current_env_menu_items('globalSpeedTree', layout)


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class SpeedTreeBakeDocumentation(bpy.types.Operator):

    bl_idname = "wm.bh_st_atlas_baker_show_doc"
    bl_label = '[[[[ ' + 'SPEEDTREE ATLAS BAKER [COMING SOON]' + ' ]]]]'
    bl_description = loc_str('open_doc_page')

    def execute(self, context):
        fileUtils.open_url('https://sites.google.com/view/bluehole/home')
        return{'FINISHED'}


class SpeedTreeBake512(bpy.types.Operator):

    bl_idname = "wm.bh_st_atlas_baker_bake_512"
    bl_label = 'Bake Atlas (512x512) [Coming Soon]'

    def execute(self, context):
        import BlueHole.speedtreeAtlasBaker.runBaker as runBaker
        runBaker.run_blender_atlas_baker(resolution=512)
        return {'FINISHED'}


class SpeedTreeBake1024(bpy.types.Operator):

    bl_idname = "wm.bh_st_atlas_baker_bake_1024"
    bl_label = 'Bake Atlas (1024x1024) [Coming Soon]'

    def execute(self, context):
        import BlueHole.speedtreeAtlasBaker.runBaker as runBaker
        runBaker.run_blender_atlas_baker(resolution=1024)
        return {'FINISHED'}


class SpeedTreeBake2048(bpy.types.Operator):

    bl_idname = "wm.bh_st_atlas_baker_bake_2048"
    bl_label = 'Bake Atlas (2048x2048) [Coming Soon]'

    def execute(self, context):
        import BlueHole.speedtreeAtlasBaker.runBaker as runBaker
        runBaker.run_blender_atlas_baker(resolution=2048)
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (SpeedTreeBakeDocumentation,
           SpeedTreeBake512,
           SpeedTreeBake1024,
           SpeedTreeBake2048
           )


# Register
def register():
    # Register Menu
    bpy.utils.register_class(BLUE_HOLE_MT_speedtree)
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    # Unregister Menu
    bpy.utils.unregister_class(BLUE_HOLE_MT_speedtree)
    # Unregister Operators
    for cls in classes:
        bpy.utils.unregister_class(cls)


# ----------------------------------------------------------------------------------------------------------------------
# End of File Debug Message
debugUtils.print_debug_msg('SpeedTree Atlas Baker Menus and Operators Loaded!', show_verbose)
