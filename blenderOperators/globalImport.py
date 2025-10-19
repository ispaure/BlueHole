"""
Adds Blue Hole Blender Operators [Import]
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "GNU General Public License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

import bpy

import BlueHole.blenderUtils.importUtils as importUtils
import BlueHole.blenderUtils.debugUtils as debugUtils
from BlueHole.blenderUtils.uiUtils import show_label as show_label
import BlueHole.envUtils.envUtils as envUtils


# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

debugUtils.print_debug_msg('\nLoading Import Menu and Operators...', show_verbose)


# ----------------------------------------------------------------------------------------------------------------------
# MENUS

class BLUE_HOLE_MT_import(bpy.types.Menu):
    bl_label = "Import"

    def draw(self, context):
        layout = self.layout
        show_label('SCALE GUIDES', layout)
        # layout.menu("BLUE_HOLE_MT_import_scale_guides")
        layout.operator(ImportGuide_5_6_ScaleMan.bl_idname, icon='IMPORT')
        layout.operator(ImportGuide_5_10_ScaleMan.bl_idname, icon='IMPORT')
        layout.operator(ImportGuide_5_10_ScaleManCasual.bl_idname, icon='IMPORT')
        layout.operator(ImportGuide_5_10_ScaleManSitting.bl_idname, icon='IMPORT')
        layout.operator(ImportGuide_6_1_ScaleMan.bl_idname, icon='IMPORT')

        # Draw additional operators from the active environment (if available)
        envUtils.draw_current_env_menu_items('globalImport', layout)


class BLUE_HOLE_MT_import_scale_guides(bpy.types.Menu):
    bl_label = "Scale Guides"

    def draw(self, context):
        layout = self.layout
        for cls in classes:
            layout.operator(cls.bl_idname)


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS

class ImportGuide_5_6_ScaleMan(bpy.types.Operator):

    bl_idname = "wm.bh_imp_guide_5_6_scaleman"
    bl_label = "Scaleman (5'6)"

    def execute(self, context):
        importUtils.import_default_env_scale_guide('5_6_scaleman.obj')
        return {'FINISHED'}


class ImportGuide_5_10_ScaleMan(bpy.types.Operator):

    bl_idname = "wm.bh_imp_guide_5_10_scaleman"
    bl_label = "Scaleman (5'10)"

    def execute(self, context):
        importUtils.import_default_env_scale_guide('5_10_scaleman.obj')
        return {'FINISHED'}


class ImportGuide_5_10_ScaleManCasual(bpy.types.Operator):

    bl_idname = "wm.bh_imp_guide_5_10_scaleman_casual"
    bl_label = "Scaleman (5'10) Casual"

    def execute(self, context):
        importUtils.import_default_env_scale_guide('5_10_scaleman_CasualPose.fbx')
        return {'FINISHED'}


class ImportGuide_5_10_ScaleManSitting(bpy.types.Operator):

    bl_idname = "wm.bh_imp_guide_5_10_scaleman_sitting"
    bl_label = "Scaleman (5'10) Sitting"

    def execute(self, context):
        importUtils.import_default_env_scale_guide('5_10_scaleman_SittingPose.fbx')
        return {'FINISHED'}


class ImportGuide_6_1_ScaleMan(bpy.types.Operator):

    bl_idname = "wm.bh_imp_guide_6_1_scaleman"
    bl_label = "Scaleman (6'1)"

    def execute(self, context):
        importUtils.import_default_env_scale_guide('6_1_scaleman.obj')
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister
classes = (ImportGuide_5_6_ScaleMan,
           ImportGuide_5_10_ScaleMan,
           ImportGuide_5_10_ScaleManCasual,
           ImportGuide_5_10_ScaleManSitting,
           ImportGuide_6_1_ScaleMan,
           )


# Register
def register():
    # Register Menus
    bpy.utils.register_class(BLUE_HOLE_MT_import)
    bpy.utils.register_class(BLUE_HOLE_MT_import_scale_guides)
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    # Unregister Menus
    bpy.utils.unregister_class(BLUE_HOLE_MT_import)
    bpy.utils.unregister_class(BLUE_HOLE_MT_import_scale_guides)
    # Unregister Operators
    for cls in classes:
        bpy.utils.unregister_class(cls)


# ----------------------------------------------------------------------------------------------------------------------
# End of File Debug Message
debugUtils.print_debug_msg('Import Menu and Operators Loaded!', show_verbose)
