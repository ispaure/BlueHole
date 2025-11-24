"""
Blue Hole Menus
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
# IMPORTS


import bpy
import os
import BlueHole.blenderUtils.addon as addon
from BlueHole.blenderUtils.languageUtils import loc_str as loc_str
from BlueHole.blenderUtils.uiUtils import show_label as show_label

# Import Operators
import BlueHole.Operators.dirOp as dirOp
import BlueHole.Operators.impExpOp as impExpOp
import BlueHole.Operators.foodOp as foodOp
import BlueHole.Operators.helpOp as helpOp
import BlueHole.Operators.musicOp as musicOp
import BlueHole.Operators.sendOp as sendOp
import BlueHole.Operators.sortOp as sortOp
import BlueHole.Operators.sourceControlOp as sourceControlOp
import BlueHole.Operators.themeOp as themeOp


# ----------------------------------------------------------------------------------------------------------------------
# MENUS


# Directories Menu
class BLUE_HOLE_MT_directories(bpy.types.Menu):
    bl_label = loc_str('directory_and_hierarchy')

    def draw(self, context):
        layout = self.layout
        layout.operator(impExpOp.SceneAddAssetHierarchy.bl_idname, icon='OUTLINER')

        # Environment Folders
        test_a = os.path.exists(addon.preference().environment.sc_path) or os.path.exists(addon.preference().environment.sc_path_alternate) or os.path.exists(addon.preference().environment.sc_path_mac) or os.path.exists(addon.preference().environment.sc_path_mac_alternate)
        test_b = os.path.exists(addon.preference().general.unity_assets_path) or os.path.exists(addon.preference().general.unity_assets_path_mac)
        test_c = addon.preference().sourcecontrol.source_control_enable and addon.preference().sourcecontrol.source_control_solution == 'perforce'
        if test_a or test_b or test_c:
            layout.separator()
            show_label('ENVIRONMENT', layout)
            if test_a:
                layout.operator(dirOp.OpenSourceContentPath.bl_idname, icon='FILE_FOLDER')
            if test_b:
                layout.operator(dirOp.OpenUnityAssetsPath.bl_idname, icon='FILE_FOLDER')
            if test_c:
                layout.operator(dirOp.OpenP4WorkspaceRootFolder.bl_idname, icon='FILE_FOLDER')

        layout.separator()
        show_label('SOURCE ASSET', layout)
        layout.operator(dirOp.OpenRootFolder.bl_idname, icon='FILE_FOLDER')
        layout.operator(dirOp.OpenReferencesFolder.bl_idname, icon='FILE_FOLDER')
        layout.operator(dirOp.OpenResourcesFolder.bl_idname, icon='FILE_FOLDER')
        layout.operator(dirOp.OpenSpeedTreeMeshesFolder.bl_idname, icon='FILE_FOLDER')
        layout.operator(dirOp.OpenFinalFolder.bl_idname, icon='FILE_FOLDER')
        layout.separator()
        show_label('CONFIG', layout)
        layout.operator(dirOp.OpenUserResourcePath.bl_idname, icon='FILE_FOLDER')


# Export Menu
class BLUE_HOLE_MT_export(bpy.types.Menu):
    bl_label = "Export (to Source Asset Dir.)"

    def draw(self, context):
        layout = self.layout
        show_label('FINAL Folder', layout)
        layout.operator(impExpOp.ExportAllHierarchiesToUE.bl_idname, icon='EXPORT')
        layout.operator(impExpOp.ExportSelectHierarchiesToUE.bl_idname, icon='EXPORT')
        layout.operator(impExpOp.BatchExportSelectedToFinal.bl_idname, icon='EXPORT')
        layout.separator()
        show_label('RESOURCES Folder', layout)
        layout.operator(impExpOp.BatchExportSelectedToResources.bl_idname, icon='EXPORT')
        layout.separator()
        show_label('SPEEDTREE FRONDS Folder', layout)
        layout.operator(impExpOp.BatchExportSelectedToSpeedTree_FBX.bl_idname, icon='EXPORT')
        layout.operator(impExpOp.BatchExportSelectedToSpeedtreeLR_FBX.bl_idname, icon='EXPORT')
        layout.operator(impExpOp.BatchExportSelectedToSpeedtreeHR_FBX.bl_idname, icon='EXPORT')


class BLUE_HOLE_MT_food_delivery(bpy.types.Menu):
    bl_label = loc_str('food_delivery')

    def draw(self, context):
        layout = self.layout
        for cls in foodOp.classes:
            layout.operator(cls.bl_idname, icon='TEMP')


class BLUE_HOLE_MT_help(bpy.types.Menu):
    bl_label = loc_str('help_n_updates')

    def draw(self, context):
        layout = self.layout

        # Show Documentation Section
        show_label('DOCUMENTATION', layout)
        layout.operator(helpOp.OpenGuide.bl_idname, icon='URL')
        layout.operator(helpOp.OpenKeymapsList.bl_idname, icon='URL')
        layout.operator(helpOp.OpenPieMenusList.bl_idname, icon='URL')

        # Show Submit Feedback Button
        layout.separator()
        layout.operator(helpOp.SubmitFeedback.bl_idname, icon='WINDOW')
        layout.operator(helpOp.JoinBHDiscord.bl_idname, icon='FUND')


class BLUE_HOLE_MT_import(bpy.types.Menu):
    bl_label = "Import"

    def draw(self, context):
        layout = self.layout
        show_label('SCALE GUIDES', layout)
        # layout.menu("BLUE_HOLE_MT_import_scale_guides")
        layout.operator(impExpOp.ImportGuide_5_6_ScaleMan.bl_idname, icon='IMPORT')
        layout.operator(impExpOp.ImportGuide_5_10_ScaleMan.bl_idname, icon='IMPORT')
        layout.operator(impExpOp.ImportGuide_5_10_ScaleManCasual.bl_idname, icon='IMPORT')
        layout.operator(impExpOp.ImportGuide_5_10_ScaleManSitting.bl_idname, icon='IMPORT')
        layout.operator(impExpOp.ImportGuide_6_1_ScaleMan.bl_idname, icon='IMPORT')


class BLUE_HOLE_MT_music(bpy.types.Menu):
    bl_label = 'Music'

    def draw(self, context):
        layout = self.layout
        for cls in musicOp.classes:
            layout.operator(cls.bl_idname, icon='SOUND')


class BLUE_HOLE_MT_send(bpy.types.Menu):
    bl_label = "Send (to Game Engine)"

    def draw(self, context):
        layout = self.layout
        # These options are always available, regardless of active environment

        # Unity
        layout.operator(helpOp.SendToUnityDoc.bl_idname, icon='KEYTYPE_EXTREME_VEC')
        layout.operator(sendOp.SendAllHierarchiesToUnity.bl_idname, icon='UV_SYNC_SELECT')
        layout.operator(sendOp.SendSelectedHierarchiesToUnity.bl_idname, icon='UV_SYNC_SELECT')

        layout.separator()

        # Unreal
        layout.operator(helpOp.SendToUnrealDoc.bl_idname, icon='KEYTYPE_EXTREME_VEC')
        layout.operator(sendOp.SendAllHierarchiesToUnreal.bl_idname, icon='UV_SYNC_SELECT')
        layout.operator(sendOp.SendSelectedHierarchiesToUnreal.bl_idname, icon='UV_SYNC_SELECT')


class BLUE_HOLE_MT_sort(bpy.types.Menu):
    bl_label = "Sort"

    def draw(self, context):
        layout = self.layout
        layout.operator(sortOp.SortSelectionOnWorldAxis.bl_idname)
        layout.operator(sortOp.SearchReplaceNameSelection.bl_idname)
        layout.operator(sortOp.BatchRenameSelection.bl_idname)
        layout.operator(sortOp.FlipLastUnderscores.bl_idname)


class BLUE_HOLE_MT_source_control(bpy.types.Menu):
    bl_label = "Source Control"

    def draw(self, context):
        layout = self.layout
        layout.operator(sourceControlOp.P4CheckOutCurrentScene.bl_idname, icon = 'CHECKMARK')
        layout.operator(sourceControlOp.P4DisplayServerInfo.bl_idname, icon = 'INFO')


class BLUE_HOLE_MT_themes(bpy.types.Menu):
    bl_label = "Themes"

    def draw(self, context):
        layout = self.layout
        for cls in themeOp.classes:
            layout.operator(cls.bl_idname, icon='IMAGE_RGB_ALPHA')


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (BLUE_HOLE_MT_directories,
           BLUE_HOLE_MT_export,
           BLUE_HOLE_MT_food_delivery,
           BLUE_HOLE_MT_help,
           BLUE_HOLE_MT_import,
           BLUE_HOLE_MT_music,
           BLUE_HOLE_MT_send,
           BLUE_HOLE_MT_sort,
           BLUE_HOLE_MT_source_control,
           BLUE_HOLE_MT_themes)


# Register
def register():
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
