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
from ....operators import add_ops, external_addon_ops
from ....preferences.prefs import *

# ----------------------------------------------------------------------------------------------------------------------
# MENUS


class BLUE_HOLE_MT_containers(bpy.types.Menu):
    bl_label = 'Asset Containers'
    bl_idname = "BLUE_HOLE_MT_containers"

    def draw(self, context):
        layout = self.layout

        enabled_collection = prefs().container.enable_asset_collection_container
        enabled_hierarchy = prefs().container.enable_asset_hierarchy_container
        enabled_mesh = prefs().container.enable_asset_mesh_container

        has_selection = len(context.selected_objects) > 0
        suffix = " (From Selection)" if has_selection else ""

        if enabled_collection:
            layout.operator(
                add_ops.SceneAddAssetCollection.bl_idname,
                text=f"Asset Collection{suffix}",
                icon='OUTLINER_COLLECTION'
            )

        if enabled_hierarchy:
            layout.operator(
                add_ops.SceneAddAssetHierarchy.bl_idname,
                text=f"Asset Hierarchy{suffix}",
                icon='OUTLINER_OB_EMPTY'
            )

        if enabled_mesh:
            layout.operator(
                add_ops.SceneAddAssetMesh.bl_idname,
                text=f"Asset Mesh{suffix}",
                icon='MESH_CUBE'
            )

        if not (enabled_collection or enabled_hierarchy or enabled_mesh):
            row = layout.row()
            row.enabled = False
            row.operator(
                external_addon_ops.BH_OT_disabled_notice.bl_idname,
                text="All Asset Containers disabled in Preferences",
                icon='ERROR'
            )


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# Menu classes
classes = (
    BLUE_HOLE_MT_containers,
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
