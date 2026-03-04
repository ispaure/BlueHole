"""
Import/Export Operators
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
from ..blenderUtils import objectUtils, importUtils
from ..blenderUtils.export.exportSettingsPresets import *
from ..blenderUtils.export.looseMesh.containerGroup import batch_export_loose_mesh
from ..blenderUtils.export.model.assetContainerGroup import get_hierarchy_prefix_lst
from ..blenderUtils.export.assetHierarchy.containerGroup import AssetHierarchyContainerGroup
from ..blenderUtils.export.assetCollection.containerGroup import AssetCollectionContainerGroup
from ..blenderUtils.export.assetMesh.containerGroup import AssetMeshContainerGroup
from ..preferences.prefs import *
from ..Lib.commonUtils import uiUtils


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class BatchExportSelectedToFinal(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_final"
    bl_label = 'Batch Export (Selection) to FINAL Folder'
    bl_description = 'Batch exports selected meshes using their names as file names in the FINAL Folder'

    def execute(self, context):
        batch_export_loose_mesh(prefs().directory.sc_dir_struct_final)
        return {'FINISHED'}


class BatchExportSelectedToResources(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_resources"
    bl_label = 'Batch Export (Selection) to RESOURCES Folder'

    def execute(self, context):
        batch_export_loose_mesh(prefs().directory.sc_dir_struct_resources)
        return {'FINISHED'}


class BatchExportSelectedToSpeedTree_FBX(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_speedtree_fbx"
    bl_label = 'Batch Export (Selection) to SPEEDTREE Folder'
    bl_description = 'Batch exports selected meshes using their names as file names in the SPEEDTREE MSH Folder'

    def execute(self, context):
        batch_export_loose_mesh(prefs().directory.sc_dir_struct_st)
        return {'FINISHED'}


class BatchExportSelectedToSpeedtreeLR_FBX(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_speedtree_lr_fbx"
    bl_label = 'Batch Export (Selection) to SPEEDTREE-LR Folder'
    bl_description = 'Batch exports selected meshes using their names as file names in the SPEEDTREE MSH -> LR Folder'

    def execute(self, context):
        batch_export_loose_mesh(prefs().directory.sc_dir_struct_st_lr)
        return {'FINISHED'}


class BatchExportSelectedToSpeedtreeHR_FBX(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_speedtree_hr_fbx"
    bl_label = 'Batch Export (Selection) to SPEEDTREE-HR Folder'
    bl_description = 'Batch exports selected meshes using their names as file names in the SPEEDTREE MSH -> HR Folder'

    def execute(self, context):
        batch_export_loose_mesh(prefs().directory.sc_dir_struct_st_hr)
        return {'FINISHED'}


class BatchExportSelectedToBakeFBX(bpy.types.Operator):
    bl_idname = "wm.bh_batch_export_select_to_bake_fbx"
    bl_label = 'Batch Export (Selection) to BAKE Folder'
    bl_description = 'Batch exports selected meshes using their names as file names in the MSH BAKE Folder'

    def execute(self, context):
        batch_export_loose_mesh(prefs().directory.sc_dir_struct_msh_bake)
        return {'FINISHED'}


class SceneAddAssetHierarchy(bpy.types.Operator):

    bl_idname = "wm.bh_scene_add_asset_hierarchy"
    bl_label = "Add Asset Hierarchy"
    bl_description = 'Add Asset Hierarchy of given name to scene, in which objects are placed.'

    settings: bpy.props.EnumProperty(
        name = 'Settings',
        description = 'Settings to display',
        items = [('NAMEGEN', 'Easy Name Generator', 'Creates hierarchy name matching naming convention, preventing user error.'),
                 ('MANUAL', 'Manual Name Entry', 'Creates hierarchy matching user-given name, regardless if it matches naming conventions or not.')],
        default = 'NAMEGEN')

    preview: bpy.props.EnumProperty(name='Preview',items=[('PREVIEW', 'Preview', 'Preview name of Hierarchies that will be created.')], default='PREVIEW')

    # TYPE and their index position (see env_variables.ini > ObjectHierarchyStructure > prefixes)
    hierarchy_types = {'Mesh Asset': 0, 'Mesh Kit Asset': 1, 'Skeletal Mesh': 2}
    prefix_items = []
    for key in hierarchy_types.keys():
        prefix_items.append((key, key, ''))
    asset_type: bpy.props.EnumProperty(name='Type',
                                        description='The selected type of mesh. Affects the hierarchy name\'s prefix',
                                        items=prefix_items)

    # NAME
    asset_name: bpy.props.StringProperty(name='Name',
                                          description='Name of the asset for which the hierarchy is created. Will be the center part of the hierarchy name',
                                          default='InsertName')

    # VERSION BATCH
    version_batch: bpy.props.BoolProperty(name='Batch',
                                           description='When enabled, allows the creation of multiple hierarchies in one go',
                                           default=False)

    # VERSION (SINGLE)
    version_suffix: bpy.props.IntProperty(name='Number',
                                           description='Version (number) of the hierarchy. Affects the hierarchy name\'s suffix',
                                           default=1)

    # VERSION SUFFIX_START
    version_suffix_start: bpy.props.IntProperty(name='Number (Start)',
                                                 description='When using batch mode, defines the first version (number) to create',
                                                 default=1)

    # VERSION SUFFIX_END
    version_suffix_end: bpy.props.IntProperty(name='Number (End)',
                                               description='When using batch mode, defines the last version (number) to create',
                                               default=1)

    # VERSION (LETTER)
    version_suffix_letter: bpy.props.StringProperty(name='Letter',
                                                     description='Letter(s) suffix at end-of-name.',
                                                     default='')

    # INCLUDE DEFAULT MESH
    include_default_mesh: bpy.props.BoolProperty(name='Include Default Mesh',
                                                  description='Whether to include the default icosphere mesh as part of the hierarchy',
                                                  default=False)

    # DISPLAY EMPTY OBJECTS AS ARROWS
    dsp_empty_obj_arrows: bpy.props.BoolProperty(name='Display as Arrows',
                                                  description='When set to true, display Empty Objects as XYZ Arrows',
                                                  default=True)

    # INCLUDE SELECTED OBJECTS
    include_selected_obj: bpy.props.BoolProperty(name='Include Selection in Render',
                                                  description='Whether to parent currently selected objects as part of the hierarchy.',
                                                  default=True)

    def execute(self, context):
        objectUtils.add_asset_hierarchy(self.result_hierarchy_lst(),
                                        self.include_default_mesh,
                                        self.include_selected_obj,
                                        self.dsp_empty_obj_arrows)
        return {'FINISHED'}

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        column = layout.column(align=True)
        row = column.row(align=True)
        row.prop(self, 'settings', expand=True)

        # DISPLAY PARAMETERS

        # Easy Name Generator Specific
        if self.settings == 'NAMEGEN':
            # Create box for prefix
            box = layout.box()
            box.label(text='Prefix')
            column = box.column()
            row = column.row()
            row.prop(self, "asset_type")

        box = layout.box()
        box.label(text='Name')
        column = box.column()
        row = column.row()
        row.prop(self, "asset_name")

        # Easy Name Generator Specific
        if self.settings == 'NAMEGEN':
            # Create box for suffix
            box = layout.box()
            box.label(text='Suffix')
            column = box.column()
            row = column.row()
            row.prop(self, "version_batch")
            if self.version_batch:
                row = column.row()
                row.prop(self, "version_suffix_start")
                row = column.row()
                row.prop(self, "version_suffix_end")
            else:
                row = column.row()
                row.prop(self, "version_suffix")
                row = column.row()
                row.prop(self, "version_suffix_letter")

        # DISPLAY LIST OF HIERARCHIES TO CREATE
        hierarchy_to_create_lst = self.result_hierarchy_lst()
        box = layout.box()
        column = box.column()

        row = column.row()
        row.prop(self, 'preview', expand=True)
        box.label(text=hierarchy_to_create_lst[0])
        if prefs().container.create_element_render:
            box.label(text='   ↳ ' + prefs().container.asset_hierarchy_empty_object_meshes)
        if prefs().container.create_element_collision:
            box.label(text='   ↳ ' + prefs().container.asset_hierarchy_empty_object_collisions)
        if prefs().container.create_element_sockets:
            box.label(text='   ↳ ' + prefs().container.asset_hierarchy_empty_object_sockets)
        if len(hierarchy_to_create_lst) > 1:
            row = column.row()
            box.label(text='...')
            row = column.row()
            box.label(text=hierarchy_to_create_lst[-1])

        # DISPLAY ADVANCED OPTIONS
        box = layout.box()
        box.label(text='Advanced Options')
        column = box.column()
        row = column.row()
        row.prop(self, "include_default_mesh")
        row.prop(self, "dsp_empty_obj_arrows")
        row = column.row()
        if len(hierarchy_to_create_lst) == 1 and prefs().container.create_element_render:
            row.prop(self, 'include_selected_obj')

        # for hierarchy in hierarchy_to_create_lst:
        #     row = column.row()
        #     box.label(text=hierarchy)

    def result_hierarchy_lst(self):
        """
        Find full name of hierarchies to create, from given parameters.
        """
        result_hierarchy_lst = []
        if self.settings == 'NAMEGEN':
            if self.version_batch:
                for item in range(self.version_suffix_start, self.version_suffix_end + 1):
                    result_hierarchy_name = ''
                    for key, value in self.hierarchy_types.items():
                        if key in self.asset_type:
                            result_hierarchy_name += get_hierarchy_prefix_lst()[value]
                    result_hierarchy_name += self.asset_name
                    result_hierarchy_name += '_' + str(format(item, '02'))
                    result_hierarchy_lst.append(result_hierarchy_name)
            else:
                result_hierarchy_name = ''
                for key, value in self.hierarchy_types.items():
                    if key in self.asset_type:
                        result_hierarchy_name += get_hierarchy_prefix_lst()[value]
                result_hierarchy_name += self.asset_name
                result_hierarchy_name += '_' + str(format(self.version_suffix, '02'))
                if len(self.version_suffix_letter) > 0:
                    result_hierarchy_name += '' + self.version_suffix_letter
                result_hierarchy_lst.append(result_hierarchy_name)
        elif self.settings == 'MANUAL':
            result_hierarchy_lst.append(self.asset_name)

        # Return list of hierarchies
        return result_hierarchy_lst

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class SceneAddAssetCollection(bpy.types.Operator):

    bl_idname = "wm.bh_scene_add_asset_collection"
    bl_label = "Add Asset Collection"
    bl_description = "Add Asset Collection of given name to scene."

    def execute(self, context):
        log(Severity.CRITICAL, self.bl_label, f'{self.bl_label} has not yet been implemented.')
        return {'CANCELLED'}


class SceneAddAssetMesh(bpy.types.Operator):

    bl_idname = "wm.bh_scene_add_asset_mesh"
    bl_label = "Add Asset Mesh"
    bl_description = "Add Asset Mesh of given name to scene."

    # -------------------------------------------------------------------------------------------------
    # UI MODE
    # -------------------------------------------------------------------------------------------------

    settings: bpy.props.EnumProperty(
        name='Settings',
        description='Settings to display',
        items=[
            ('NAMEGEN', 'Easy Name Generator', 'Creates a mesh name matching naming convention, preventing user error.'),
            ('MANUAL',  'Manual Name Entry',   'Creates mesh matching user-given name, regardless of naming conventions.'),
        ],
        default='NAMEGEN'
    )

    preview: bpy.props.EnumProperty(
        name='Preview',
        items=[('PREVIEW', 'Preview', 'Preview names that will be created.')],
        default='PREVIEW'
    )

    # -------------------------------------------------------------------------------------------------
    # TYPE (same concept as hierarchies: uses your prefix list)
    # -------------------------------------------------------------------------------------------------

    # TYPE and their index position (see env_variables.ini > ObjectHierarchyStructure > prefixes)
    hierarchy_types = {'Mesh Asset': 0, 'Mesh Kit Asset': 1, 'Skeletal Mesh': 2}
    prefix_items = []
    for key in hierarchy_types.keys():
        prefix_items.append((key, key, ''))

    asset_type: bpy.props.EnumProperty(
        name='Type',
        description="Affects the mesh name's prefix",
        items=prefix_items
    )

    # -------------------------------------------------------------------------------------------------
    # NAME
    # -------------------------------------------------------------------------------------------------

    asset_name: bpy.props.StringProperty(
        name='Name',
        description="Name of the asset. Will be the center part of the mesh name",
        default='InsertName'
    )

    # -------------------------------------------------------------------------------------------------
    # VERSIONING
    # -------------------------------------------------------------------------------------------------

    version_batch: bpy.props.BoolProperty(
        name='Batch',
        description='When enabled, allows the creation of multiple Asset Mesh roots in one go',
        default=False
    )

    version_suffix: bpy.props.IntProperty(
        name='Number',
        description="Version (number). Affects the mesh name's suffix",
        default=1
    )

    version_suffix_start: bpy.props.IntProperty(
        name='Number (Start)',
        description='When using batch mode, defines the first version (number) to create',
        default=1
    )

    version_suffix_end: bpy.props.IntProperty(
        name='Number (End)',
        description='When using batch mode, defines the last version (number) to create',
        default=1
    )

    version_suffix_letter: bpy.props.StringProperty(
        name='Letter',
        description='Letter(s) suffix at end-of-name.',
        default=''
    )

    # -------------------------------------------------------------------------------------------------
    # CONTENT
    # -------------------------------------------------------------------------------------------------

    include_default_mesh: bpy.props.BoolProperty(
        name='Include Default Mesh',
        description='Whether to create a default primitive mesh for newly created Asset Mesh roots',
        default=False
    )

    include_selected_obj: bpy.props.BoolProperty(
        name='Use Selection',
        description=(
            "If enabled:\n"
            "• 1 selected mesh: rename the active mesh.\n"
            "• 2+ selected meshes: create a new Asset Mesh root and parent selection under it.\n"
            "If disabled: creates a new Asset Mesh root mesh."
        ),
        default=True
    )

    # -------------------------------------------------------------------------------------------------
    # EXECUTE
    # -------------------------------------------------------------------------------------------------

    def execute(self, context):

        # If operator is executed without invoke() (scripts/search), auto-disable selection behavior
        # when there is no selection, to avoid failing by default.
        if self.include_selected_obj and not context.selected_objects:
            self.include_selected_obj = False

        # Resolve names
        name_lst = self.result_asset_mesh_name_lst()
        if not name_lst:
            self.report({'WARNING'}, "No names generated.")
            return {'CANCELLED'}

        # Selection handling
        sel_meshes = [o for o in context.selected_objects if o.type == 'MESH']

        # Batch mode: always create new roots (no special selection behavior)
        if self.version_batch:
            created = 0
            for nm in name_lst:
                self._create_asset_mesh_root(context, nm)
                created += 1
            self.report({'INFO'}, f"Created {created} Asset Mesh root(s).")
            return {'FINISHED'}

        # Single mode:
        nm = name_lst[0]

        if self.include_selected_obj and len(sel_meshes) > 0:

            # 1 selected mesh => rename active (or that mesh)
            if len(sel_meshes) == 1:
                obj = context.active_object if (context.active_object and context.active_object.type == 'MESH') else sel_meshes[0]
                obj.name = nm
                obj.parent = None
                obj.matrix_parent_inverse.identity()

                self.report({'INFO'}, f'Renamed mesh to "{nm}".')
                return {'FINISHED'}

            # 2+ selected meshes => create root and parent under it
            root = self._create_asset_mesh_root(context, nm)
            for o in sel_meshes:
                # avoid parenting the root to itself if it was selected for some reason
                if o == root:
                    continue
                o.parent = root
                o.matrix_parent_inverse = root.matrix_world.inverted()

            self.report({'INFO'}, f'Created "{nm}" and parented {len(sel_meshes)} mesh(es).')
            return {'FINISHED'}

        # No selection usage => create new root
        self._create_asset_mesh_root(context, nm)
        self.report({'INFO'}, f'Created "{nm}".')
        return {'FINISHED'}

    # -------------------------------------------------------------------------------------------------
    # UI
    # -------------------------------------------------------------------------------------------------

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        column = layout.column(align=True)
        row = column.row(align=True)
        row.prop(self, 'settings', expand=True)

        # Easy Name Generator Specific
        if self.settings == 'NAMEGEN':
            box = layout.box()
            box.label(text='Prefix')
            col = box.column()
            row = col.row()
            row.prop(self, "asset_type")

        box = layout.box()
        box.label(text='Name')
        col = box.column()
        row = col.row()
        row.prop(self, "asset_name")

        # Easy Name Generator Specific
        if self.settings == 'NAMEGEN':
            box = layout.box()
            box.label(text='Suffix')
            col = box.column()
            row = col.row()
            row.prop(self, "version_batch")

            if self.version_batch:
                row = col.row()
                row.prop(self, "version_suffix_start")
                row = col.row()
                row.prop(self, "version_suffix_end")
            else:
                row = col.row()
                row.prop(self, "version_suffix")
                row = col.row()
                row.prop(self, "version_suffix_letter")

        # Preview
        name_lst = self.result_asset_mesh_name_lst()
        box = layout.box()
        col = box.column()
        row = col.row()
        row.prop(self, 'preview', expand=True)

        if name_lst:
            box.label(text=name_lst[0])
            if len(name_lst) > 1:
                box.label(text='...')
                box.label(text=name_lst[-1])

        # Advanced Options
        box = layout.box()
        box.label(text='Advanced Options')
        col = box.column()

        row = col.row()
        row.prop(self, "include_default_mesh")

        # Only show "Use Selection" in non-batch mode (so behavior is predictable)
        if not self.version_batch:
            row = col.row()
            row.prop(self, "include_selected_obj")

            if self.include_selected_obj and not context.selected_objects:
                row = col.row()
                row.label(text="No selection: a new Asset Mesh root will be created.", icon='INFO')

    # -------------------------------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------------------------------

    def invoke(self, context, event):
        # Auto-toggle "Use Selection" based on current selection, each time the dialog opens
        self.include_selected_obj = bool(context.selected_objects)
        return context.window_manager.invoke_props_dialog(self)

    def result_asset_mesh_name_lst(self):
        """
        Find full name(s) of Asset Mesh root(s) to create, from given parameters.
        """
        result_name_lst = []

        if self.settings == 'NAMEGEN':

            def _prefix() -> str:
                p = ''
                for key, idx in self.hierarchy_types.items():
                    if key in self.asset_type:
                        p += get_hierarchy_prefix_lst()[idx]
                return p

            if self.version_batch:
                for item in range(self.version_suffix_start, self.version_suffix_end + 1):
                    nm = _prefix()
                    nm += self.asset_name
                    nm += '_' + str(format(item, '02'))
                    result_name_lst.append(nm)
            else:
                nm = _prefix()
                nm += self.asset_name
                nm += '_' + str(format(self.version_suffix, '02'))
                if len(self.version_suffix_letter) > 0:
                    nm += '' + self.version_suffix_letter
                result_name_lst.append(nm)

        elif self.settings == 'MANUAL':
            result_name_lst.append(self.asset_name)

        return result_name_lst

    def _create_asset_mesh_root(self, context, name: str) -> bpy.types.Object:
        """
        Create an Asset Mesh root object at the scene root.
        If include_default_mesh is True, create a primitive mesh; otherwise create an empty mesh datablock.
        """
        if self.include_default_mesh:
            # Create a primitive (cheap + obvious in viewport)
            bpy.ops.mesh.primitive_ico_sphere_add()
            obj = context.active_object
            obj.name = name
        else:
            # Create an empty mesh datablock (valid mesh object, no geometry)
            mesh_data = bpy.data.meshes.new(name=f"{name}_DATA")
            obj = bpy.data.objects.new(name, mesh_data)
            context.collection.objects.link(obj)
            context.view_layer.objects.active = obj
            obj.select_set(True)

        # Ensure it's at scene root (no parent)
        obj.parent = None
        obj.matrix_parent_inverse.identity()

        return obj


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
           BatchExportSelectedToSpeedTree_FBX,
           BatchExportSelectedToSpeedtreeLR_FBX,
           BatchExportSelectedToSpeedtreeHR_FBX,
           BatchExportSelectedToFinal,
           BatchExportSelectedToBakeFBX,
           BatchExportSelectedToResources,
           SceneAddAssetHierarchy,
           SceneAddAssetCollection,
           SceneAddAssetMesh)


def register():
    # Register Operators
    for cls in classes:
        bpy.utils.register_class(cls)


# Unregister
def unregister():
    # Unregister Operators
    for cls in classes:
        bpy.utils.unregister_class(cls)  # Unregister Operators

