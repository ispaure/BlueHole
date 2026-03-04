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
from ..Operators import dirOp, impExpOp, foodOp, helpOp, musicOp, exportSendOp, sortOp, sourceControlOp, themeOp, otherOp
from ..preferences.prefs import *
from ..blenderUtils import blenderFile
from ..Lib.commonUtils.debugUtils import *

# ----------------------------------------------------------------------------------------------------------------------
# MENUS


# Directories Menu
class BLUE_HOLE_MT_directories(bpy.types.Menu):
    bl_label = 'Directories'

    def draw(self, context):
        layout = self.layout

        # SCENE
        show_label('SCENE', layout)
        if blenderFile.is_blend_file_saved():
            layout.operator(dirOp.OpenSceneFolder.bl_idname, icon='FILE_FOLDER')
            layout.operator(dirOp.OpenReferencesFolder.bl_idname, icon='FILE_FOLDER')
            layout.operator(dirOp.OpenResourcesFolder.bl_idname, icon='FILE_FOLDER')
            layout.operator(dirOp.OpenSpeedTreeMeshesFolder.bl_idname, icon='FILE_FOLDER')
            layout.operator(dirOp.OpenFinalFolder.bl_idname, icon='FILE_FOLDER')
        else:
            col = layout.column()
            col.enabled = False
            col.operator(
                "wm.bh_disabled_notice",
                text='Save the .blend file to enable opening scene folders',
                icon='ERROR'
            )

        # ENGINE
        if prefs().bridge.active_game_engine in ['unreal', 'unity']:
            if os.path.exists(prefs().bridge.sc_path) or os.path.exists(prefs().bridge.sc_path_alternate) or os.path.exists(prefs().bridge.sc_path_mac) or os.path.exists(prefs().bridge.sc_path_mac_alternate) or os.path.exists(prefs().bridge.sc_path_linux) or os.path.exists(prefs().bridge.sc_path_linux_alternate):
                layout.separator()
                show_label('ENGINE', layout)
                layout.operator(dirOp.OpenSourceContentPath.bl_idname, icon='FILE_FOLDER')
            if prefs().bridge.active_game_engine == 'unity':
                if os.path.exists(prefs().bridge.unity_assets_path) or os.path.exists(prefs().bridge.unity_assets_path_mac) or os.path.exists(prefs().bridge.unity_assets_path_linux):
                    layout.operator(dirOp.OpenUnityAssetsPath.bl_idname, icon='FILE_FOLDER')

        # SOURCE CONTROL
        if prefs().sc.source_control_enable:
            if prefs().sc.source_control_solution == 'perforce':
                layout.separator()
                show_label('SOURCE CONTROL', layout)
                layout.operator(dirOp.OpenP4WorkspaceRootFolder.bl_idname, icon='FILE_FOLDER')

        # CONFIG
        layout.separator()
        show_label('CONFIG', layout)
        layout.operator(dirOp.OpenUserResourcePath.bl_idname, icon='FILE_FOLDER')


class BLUE_HOLE_MT_containers(bpy.types.Menu):
    bl_label = 'Asset Containers'

    def draw(self, context):
        layout = self.layout

        enabled_collection = prefs().container.enable_asset_collection_container
        enabled_hierarchy = prefs().container.enable_asset_hierarchy_container
        enabled_mesh = prefs().container.enable_asset_mesh_container

        if enabled_collection:
            layout.operator(impExpOp.SceneAddAssetCollection.bl_idname, icon='OUTLINER')

        if enabled_hierarchy:
            layout.operator(impExpOp.SceneAddAssetHierarchy.bl_idname, icon='OUTLINER')

        if enabled_mesh:
            layout.operator(impExpOp.SceneAddAssetMesh.bl_idname, icon='OUTLINER')

        if not (enabled_collection or enabled_hierarchy or enabled_mesh):
            row = layout.row()
            row.enabled = False
            row.operator(
                "wm.bh_disabled_notice",
                text="All Asset Container types are disabled in Preferences",
                icon='ERROR'
            )


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


class _BLUE_HOLE_MT_export_base(bpy.types.Menu):
    """
    Base menu that can render either Send or Export depending on SEND flag.
    Do not register this class.
    """
    SEND: bool = True  # overridden by subclasses

    @classmethod
    def build_ui_label(cls) -> str:
        verb = "Send" if cls.SEND else "Export"
        to_or_for = "to" if cls.SEND else "for"
        return f"{verb} ({to_or_for} {prefs().bridge.active_game_engine.upper()})"

    def _draw_common(self, context, layout):

        # --------------------------------------------------------------------------------------------------------------
        # ENGINE / FINAL SECTION
        # Engine Doc + preset
        match prefs().bridge.active_game_engine:
            case 'unity':
                export_preset = 'UNITY'
                if self.SEND:
                    layout.operator(helpOp.SendToUnityDoc.bl_idname, icon='KEYTYPE_EXTREME_VEC')
                else:
                    show_label('Directory: FINAL', layout)
            case 'unreal':
                export_preset = 'UNREAL'
                if self.SEND:
                    layout.operator(helpOp.SendToUnrealDoc.bl_idname, icon='KEYTYPE_EXTREME_VEC')
                else:
                    show_label('Directory: FINAL', layout)
            case _:
                log(Severity.CRITICAL, self.bl_label, 'Unsupported Active Game Engine')
                return

        if not self.SEND:  # If not sending, offer button to open the folder
            layout.operator(dirOp.OpenFinalFolder.bl_idname, icon='FILE_FOLDER')

        # Helper to reduce repetition
        def add_button(*, send_all, include_hierarchy, include_collection, include_mesh):
            icon = 'UV_SYNC_SELECT' if self.SEND else 'EXPORT'
            label = exportSendOp.BH_OT_export_containers.build_ui_label(
                export_preset=export_preset,
                send=self.SEND,
                send_all=send_all,
                include_hierarchy=include_hierarchy,
                include_collection=include_collection,
                include_mesh=include_mesh,
            )
            op = layout.operator(exportSendOp.BH_OT_export_containers.bl_idname, text=label, icon=icon)
            op.export_preset = export_preset
            op.send = self.SEND
            op.send_all = send_all
            op.include_hierarchy = include_hierarchy
            op.include_collection = include_collection
            op.include_mesh = include_mesh

        enabled_hierarchy = prefs().container.enable_asset_hierarchy_container
        enabled_collection = prefs().container.enable_asset_collection_container
        enabled_mesh = prefs().container.enable_asset_mesh_container

        enabled_count = int(enabled_hierarchy) + int(enabled_collection) + int(enabled_mesh)

        if enabled_count >= 1:
            # All Containers - All in Scene (only include enabled types)
            add_button(
                send_all=True,
                include_hierarchy=enabled_hierarchy,
                include_collection=enabled_collection,
                include_mesh=enabled_mesh,
            )

            # All Containers - In Selection (only include enabled types)
            add_button(
                send_all=False,
                include_hierarchy=enabled_hierarchy,
                include_collection=enabled_collection,
                include_mesh=enabled_mesh,
            )

            # Submenu for specific container types (only useful if 2+ enabled)
            if enabled_count >= 2:
                if self.SEND:
                    layout.menu("BLUE_HOLE_MT_send_specific")
                else:
                    layout.menu("BLUE_HOLE_MT_export_specific")

        else:
            row = layout.row()
            row.enabled = False
            row.operator(
                "wm.bh_disabled_notice",
                text="All Asset Container types are disabled in Preferences",
                icon='ERROR'
            )

        # --------------------------------------------------------------------------------------------------------------
        # RESOURCE SECTION
        if not self.SEND:
            layout.separator()
            show_label('Directory: RESOURCES', layout)
            layout.operator(dirOp.OpenResourcesFolder.bl_idname, icon='FILE_FOLDER')
            layout.operator(impExpOp.BatchExportSelectedToResources.bl_idname, icon='EXPORT')

        # --------------------------------------------------------------------------------------------------------------
        # SPEEDTREE SECTION
        if not self.SEND:
            layout.separator()
            show_label('Directory: SPEEDTREE', layout)
            layout.operator(dirOp.OpenSpeedTreeMeshesFolder.bl_idname, icon='FILE_FOLDER')
            layout.operator(impExpOp.BatchExportSelectedToSpeedTree_FBX.bl_idname, icon='EXPORT')
            layout.operator(impExpOp.BatchExportSelectedToSpeedtreeLR_FBX.bl_idname, icon='EXPORT')
            layout.operator(impExpOp.BatchExportSelectedToSpeedtreeHR_FBX.bl_idname, icon='EXPORT')


class BLUE_HOLE_MT_send(_BLUE_HOLE_MT_export_base):
    bl_idname = "BLUE_HOLE_MT_send"
    bl_label = "Send (to Game Engine)"
    SEND = True

    def draw(self, context):
        self._draw_common(context, self.layout)


class BLUE_HOLE_MT_export(_BLUE_HOLE_MT_export_base):
    bl_idname = "BLUE_HOLE_MT_export"
    bl_label = "Export (to Game Engine)"
    SEND = False

    def draw(self, context):
        self._draw_common(context, self.layout)


class _BLUE_HOLE_MT_specific_base(bpy.types.Menu):
    SEND: bool = True  # overridden

    def _draw_specific(self, context, layout):
        match prefs().bridge.active_game_engine:
            case 'unity':
                export_preset = 'UNITY'
            case 'unreal':
                export_preset = 'UNREAL'
            case _:
                log(Severity.CRITICAL, self.bl_label, 'Unsupported Active Game Engine')
                return

        enabled_collection = prefs().container.enable_asset_collection_container
        enabled_hierarchy = prefs().container.enable_asset_hierarchy_container
        enabled_mesh = prefs().container.enable_asset_mesh_container

        if not (enabled_collection or enabled_hierarchy or enabled_mesh):
            row = layout.row()
            row.enabled = False
            row.operator(
                "wm.bh_disabled_notice",
                text="All Asset Container types are disabled in Preferences",
                icon='ERROR'
            )
            return

        def add_button(title, *, send_all, include_hierarchy, include_collection, include_mesh):
            icon = 'UV_SYNC_SELECT' if self.SEND else 'EXPORT'
            label = exportSendOp.BH_OT_export_containers.build_ui_label(
                export_preset=export_preset,
                send=self.SEND,
                send_all=send_all,
                include_hierarchy=include_hierarchy,
                include_collection=include_collection,
                include_mesh=include_mesh,
            )
            op = layout.operator(exportSendOp.BH_OT_export_containers.bl_idname, text=label, icon=icon)
            op.export_preset = export_preset
            op.send = self.SEND
            op.send_all = send_all
            op.include_hierarchy = include_hierarchy
            op.include_collection = include_collection
            op.include_mesh = include_mesh

        # Collections
        if enabled_collection:
            show_label('ASSET COLLECTIONS', layout)
            add_button("Collections All",      send_all=True,  include_hierarchy=False, include_collection=True,  include_mesh=False)
            add_button("Collections Selected", send_all=False, include_hierarchy=False, include_collection=True,  include_mesh=False)
            layout.separator()

        # Hierarchies
        if enabled_hierarchy:
            show_label('ASSET HIERARCHIES', layout)
            add_button("Hierarchies All",      send_all=True,  include_hierarchy=True,  include_collection=False, include_mesh=False)
            add_button("Hierarchies Selected", send_all=False, include_hierarchy=True,  include_collection=False, include_mesh=False)
            layout.separator()

        # Meshes
        if enabled_mesh:
            show_label('ASSET MESHES', layout)
            add_button("Meshes All",      send_all=True,  include_hierarchy=False, include_collection=False, include_mesh=True)
            add_button("Meshes Selected", send_all=False, include_hierarchy=False, include_collection=False, include_mesh=True)


class BLUE_HOLE_MT_send_specific(_BLUE_HOLE_MT_specific_base):
    bl_idname = "BLUE_HOLE_MT_send_specific"
    bl_label = "Specific Asset Container"
    SEND = True

    def draw(self, context):
        self._draw_specific(context, self.layout)


class BLUE_HOLE_MT_export_specific(_BLUE_HOLE_MT_specific_base):
    bl_idname = "BLUE_HOLE_MT_export_specific"
    bl_label = "Specific Asset Container"
    SEND = False

    def draw(self, context):
        self._draw_specific(context, self.layout)


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
            layout.operator(sourceControlOp.P4DisplayServerInfo.bl_idname, icon='INFO')

            if blenderFile.is_blend_file_saved():
                layout.operator(sourceControlOp.P4CheckOutCurrentScene.bl_idname, icon='CHECKMARK')
            else:
                col = layout.column()
                col.enabled = False
                col.operator(
                    "wm.bh_disabled_notice",
                    text='Save the .blend file to enable checkout',
                    icon='ERROR'
                )


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
           BLUE_HOLE_MT_export_specific,
           BLUE_HOLE_MT_food_delivery,
           BLUE_HOLE_MT_help,
           BLUE_HOLE_MT_import,
           BLUE_HOLE_MT_music,
           BLUE_HOLE_MT_send,
           BLUE_HOLE_MT_send_specific,
           BLUE_HOLE_MT_sort,
           BLUE_HOLE_MT_containers,
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
