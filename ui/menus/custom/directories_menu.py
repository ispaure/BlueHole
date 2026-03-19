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

# Blender
import bpy

# Blue Hole
from ....blenderUtils.uiUtils import show_label
from ....operators import directory_ops, external_addon_ops
from ....preferences.prefs import *
from ....blenderUtils import blenderFile
from ....Lib.commonUtils.debugUtils import *

# ----------------------------------------------------------------------------------------------------------------------
# MENUS


class BLUE_HOLE_MT_directories(bpy.types.Menu):
    bl_label = 'Directories'
    bl_idname = "BLUE_HOLE_MT_directories"

    def draw(self, context):
        layout = self.layout

        # SCENE
        show_label('SCENE', layout)
        if blenderFile.has_blend_filepath():
            layout.operator(directory_ops.OpenSceneFolder.bl_idname, icon='FILE_FOLDER')
            layout.operator(directory_ops.OpenReferencesFolder.bl_idname, icon='FILE_FOLDER')
            layout.operator(directory_ops.OpenResourcesFolder.bl_idname, icon='FILE_FOLDER')
            layout.operator(directory_ops.OpenSpeedTreeMeshesFolder.bl_idname, icon='FILE_FOLDER')
            layout.operator(directory_ops.OpenFinalFolder.bl_idname, icon='FILE_FOLDER')
        else:
            col = layout.column()
            col.enabled = False
            col.operator(
                external_addon_ops.BH_OT_disabled_notice.bl_idname,
                text='Save .blend file to open Scene folders',
                icon='ERROR'
            )

        # ENGINE
        if prefs().bridge.active_game_engine in ['unreal', 'unity']:
            if os.path.exists(prefs().bridge.sc_path) or os.path.exists(prefs().bridge.sc_path_alternate) or os.path.exists(prefs().bridge.sc_path_mac) or os.path.exists(prefs().bridge.sc_path_mac_alternate) or os.path.exists(prefs().bridge.sc_path_linux) or os.path.exists(prefs().bridge.sc_path_linux_alternate):
                layout.separator()
                show_label('ENGINE', layout)
                layout.operator(directory_ops.OpenSourceContentPath.bl_idname, icon='FILE_FOLDER')
            if prefs().bridge.active_game_engine == 'unity':
                if os.path.exists(prefs().bridge.unity_assets_path) or os.path.exists(prefs().bridge.unity_assets_path_mac) or os.path.exists(prefs().bridge.unity_assets_path_linux):
                    layout.operator(directory_ops.OpenUnityAssetsPath.bl_idname, icon='FILE_FOLDER')

        # SOURCE CONTROL
        if prefs().sourcecontrol.source_control_enable:
            if prefs().sourcecontrol.source_control_solution == 'perforce':
                layout.separator()
                show_label('SOURCE CONTROL', layout)
                layout.operator(directory_ops.OpenP4WorkspaceRootFolder.bl_idname, icon='FILE_FOLDER')

        # CONFIG
        layout.separator()
        show_label('CONFIG', layout)
        layout.operator(directory_ops.OpenUserResourcePath.bl_idname, icon='FILE_FOLDER')


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (
    BLUE_HOLE_MT_directories,
)


# Register
def register():
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
