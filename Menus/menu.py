"""
Blue Hole Menus
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://github.com/ispaure/BlueHole

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS

# System
import os

# Blender
import bpy

# Blue Hole
from ..blenderUtils.uiUtils import show_label
from ..Operators import dirOp, impExpOp, foodOp, helpOp, musicOp, sendOp, sortOp, sourceControlOp, themeOp, otherOp
from ..preferences.prefs import *
from ..blenderUtils import blenderFile
from ..Lib.commonUtils.debugUtils import *

# ----------------------------------------------------------------------------------------------------------------------
# MENUS


# Directories Menu
class BLUE_HOLE_MT_directories(bpy.types.Menu):
    bl_label = 'Directories and Hierarchy'

    def draw(self, context):
        layout = self.layout
        layout.operator(impExpOp.SceneAddAssetHierarchy.bl_idname, icon='OUTLINER')

        # Environment Folders
        test_a = os.path.exists(prefs().bridge.sc_path) or os.path.exists(prefs().bridge.sc_path_alternate) or os.path.exists(prefs().bridge.sc_path_mac) or os.path.exists(prefs().bridge.sc_path_mac_alternate) or os.path.exists(prefs().bridge.sc_path_linux) or os.path.exists(prefs().bridge.sc_path_linux_alternate)
        test_b = os.path.exists(prefs().bridge.unity_assets_path) or os.path.exists(prefs().bridge.unity_assets_path_mac)
        test_c = prefs().sc.source_control_enable and prefs().sc.source_control_solution == 'perforce'
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
        layout.operator(dirOp.OpenSceneFolder.bl_idname, icon='FILE_FOLDER')
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
        match prefs().bridge.active_game_engine:
            case 'unreal':
                layout.operator(impExpOp.ExportAllHierarchiesToUE.bl_idname, icon='EXPORT')
                layout.operator(impExpOp.ExportSelectHierarchiesToUE.bl_idname, icon='EXPORT')
            case 'unity':
                layout.operator(impExpOp.ExportAllHierarchiesToUnity.bl_idname, icon='EXPORT')
                layout.operator(impExpOp.ExportSelectHierarchiesToUnity.bl_idname, icon='EXPORT')
            case _:
                pass
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
    bl_label = 'Food Delivery'

    def draw(self, context):
        layout = self.layout
        for cls in foodOp.classes:
            layout.operator(cls.bl_idname, icon='TEMP')


class BLUE_HOLE_MT_help(bpy.types.Menu):
    bl_label = 'Help'

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

    @classmethod
    def build_ui_label(cls) -> str:
        """
        Build menu label based on the active engine.
        """
        return f"Send (to {prefs().bridge.active_game_engine.upper()})"

    def draw(self, context):
        layout = self.layout

        match prefs().bridge.active_game_engine:
            case 'unity':
                export_preset = 'UNITY'
                layout.operator(helpOp.SendToUnityDoc.bl_idname, icon='KEYTYPE_EXTREME_VEC')
            case 'unreal':
                export_preset = 'UNREAL'
                layout.operator(helpOp.SendToUnrealDoc.bl_idname, icon='KEYTYPE_EXTREME_VEC')
            case _:
                log(Severity.CRITICAL, self.bl_label, 'Unsupported Active Game Engine')
                return

        # Send Containers Operators
        # All Containers - All in Scene
        label = sendOp.BH_OT_export_containers.build_ui_label(
            export_preset=export_preset,
            send=True,
            send_all=True,
            include_hierarchy=True,
            include_collection=True,
            include_mesh=True,
        )
        op = layout.operator(sendOp.BH_OT_export_containers.bl_idname, text=label, icon='UV_SYNC_SELECT')
        op.export_preset = export_preset
        op.send = True
        op.send_all = True
        op.include_hierarchy = True
        op.include_collection = True
        op.include_mesh = True

        # All Containers - In Selection
        label = sendOp.BH_OT_export_containers.build_ui_label(
            export_preset=export_preset,
            send=True,
            send_all=False,
            include_hierarchy=True,
            include_collection=True,
            include_mesh=True,
        )
        op = layout.operator(sendOp.BH_OT_export_containers.bl_idname, text=label, icon='UV_SYNC_SELECT')
        op.export_preset = export_preset
        op.send = True
        op.send_all = False
        op.include_hierarchy = True
        op.include_collection = True
        op.include_mesh = True

        layout.separator()
        # Submenu to send specific Asset Container types
        layout.menu("BLUE_HOLE_MT_send_specific")


class BLUE_HOLE_MT_send_specific(bpy.types.Menu):
    bl_label = "Specific Asset Container"

    def draw(self, context):
        layout = self.layout
        match prefs().bridge.active_game_engine:
            case 'unity':
                export_preset = 'UNITY'
            case 'unreal':
                export_preset = 'UNREAL'
            case _:
                log(Severity.CRITICAL, self.bl_label, 'Unsupported Active Game Engine')
                return

        # --------------------------------------------------------------------------------------------------------------
        # ASSET COLLECTIONS
        show_label('ASSET COLLECTIONS', layout)

        # Asset Collections - All in Scene
        label = sendOp.BH_OT_export_containers.build_ui_label(
            export_preset=export_preset,
            send=True,
            send_all=True,
            include_hierarchy=False,
            include_collection=True,
            include_mesh=False,
        )
        op = layout.operator(sendOp.BH_OT_export_containers.bl_idname, text=label, icon='UV_SYNC_SELECT')
        op.export_preset = export_preset
        op.send = True
        op.send_all = True
        op.include_hierarchy = False
        op.include_collection = True
        op.include_mesh = False

        # Asset Collections - In Selection
        label = sendOp.BH_OT_export_containers.build_ui_label(
            export_preset=export_preset,
            send=True,
            send_all=False,
            include_hierarchy=False,
            include_collection=True,
            include_mesh=False,
        )
        op = layout.operator(sendOp.BH_OT_export_containers.bl_idname, text=label, icon='UV_SYNC_SELECT')
        op.export_preset = export_preset
        op.send = True
        op.send_all = False
        op.include_hierarchy = False
        op.include_collection = True
        op.include_mesh = False
        layout.separator()

        # --------------------------------------------------------------------------------------------------------------
        # ASSET HIERARCHIES
        show_label('ASSET HIERARCHIES', layout)

        # Asset Hierarchies - All in Scene
        label = sendOp.BH_OT_export_containers.build_ui_label(
            export_preset=export_preset,
            send=True,
            send_all=True,
            include_hierarchy=True,
            include_collection=False,
            include_mesh=False,
        )
        op = layout.operator(sendOp.BH_OT_export_containers.bl_idname, text=label, icon='UV_SYNC_SELECT')
        op.export_preset = export_preset
        op.send = True
        op.send_all = True
        op.include_hierarchy = True
        op.include_collection = False
        op.include_mesh = False

        # Asset Hierarchies - In Selection
        label = sendOp.BH_OT_export_containers.build_ui_label(
            export_preset=export_preset,
            send=True,
            send_all=False,
            include_hierarchy=True,
            include_collection=False,
            include_mesh=False,
        )
        op = layout.operator(sendOp.BH_OT_export_containers.bl_idname, text=label, icon='UV_SYNC_SELECT')
        op.export_preset = export_preset
        op.send = True
        op.send_all = False
        op.include_hierarchy = True
        op.include_collection = False
        op.include_mesh = False
        layout.separator()

        # --------------------------------------------------------------------------------------------------------------
        # ASSET MESHES
        show_label('ASSET MESHES', layout)

        # Asset Meshes - All in Scene
        label = sendOp.BH_OT_export_containers.build_ui_label(
            export_preset=export_preset,
            send=True,
            send_all=True,
            include_hierarchy=False,
            include_collection=False,
            include_mesh=True,
        )
        op = layout.operator(sendOp.BH_OT_export_containers.bl_idname, text=label, icon='UV_SYNC_SELECT')
        op.export_preset = export_preset
        op.send = True
        op.send_all = True
        op.include_hierarchy = False
        op.include_collection = False
        op.include_mesh = True

        # Asset Meshes - In Selection
        label = sendOp.BH_OT_export_containers.build_ui_label(
            export_preset=export_preset,
            send=True,
            send_all=False,
            include_hierarchy=False,
            include_collection=False,
            include_mesh=True,
        )
        op = layout.operator(sendOp.BH_OT_export_containers.bl_idname, text=label, icon='UV_SYNC_SELECT')
        op.export_preset = export_preset
        op.send = True
        op.send_all = False
        op.include_hierarchy = False
        op.include_collection = False
        op.include_mesh = True


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
        if prefs().sc.source_control_solution == 'perforce':
            layout.operator(helpOp.PerforceDoc.bl_idname, icon='KEYTYPE_EXTREME_VEC')
            if len(blenderFile.get_blend_file_path()) > 0:
                layout.operator(sourceControlOp.P4CheckOutCurrentScene.bl_idname, icon='CHECKMARK')
            layout.operator(sourceControlOp.P4DisplayServerInfo.bl_idname, icon='INFO')


class BLUE_HOLE_MT_themes(bpy.types.Menu):
    bl_label = "Themes"

    def draw(self, context):
        layout = self.layout
        for cls in themeOp.classes:
            layout.operator(cls.bl_idname, icon='IMAGE_RGB_ALPHA')


class BLUE_HOLE_MT_update_deluxe(bpy.types.Menu):
    bl_label = "Updates & Deluxe"

    def draw(self, context):
        layout = self.layout
        layout.operator(otherOp.WM_OT_Apply_Deluxe_Prefs.bl_idname)


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
           BLUE_HOLE_MT_send_specific,
           BLUE_HOLE_MT_sort,
           BLUE_HOLE_MT_source_control,
           BLUE_HOLE_MT_themes,
           BLUE_HOLE_MT_update_deluxe)


# Register
def register():
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
