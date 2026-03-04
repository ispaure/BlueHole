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

    settings: bpy.props.EnumProperty(
        name='Settings',
        description='Settings to display',
        items=[
            ('NAMEGEN', 'Easy Name Generator', 'Creates mesh name matching naming convention, preventing user error.'),
            ('MANUAL',  'Manual Name Entry',   'Creates mesh matching user-given name, regardless of naming conventions.'),
        ],
        default='NAMEGEN',
    )

    preview: bpy.props.EnumProperty(
        name='Preview',
        items=[('PREVIEW', 'Preview', 'Preview name(s) that will be created.')],
        default='PREVIEW',
    )

    # TYPE and their index position (same intent as hierarchy; use your prefix list)
    mesh_types = {'Mesh Asset': 0, 'Mesh Kit Asset': 1, 'Skeletal Mesh': 2}
    prefix_items = [(k, k, '') for k in mesh_types.keys()]
    asset_type: bpy.props.EnumProperty(
        name='Type',
        description="The selected mesh type. Affects the name prefix.",
        items=prefix_items,
    )

    # NAME
    asset_name: bpy.props.StringProperty(
        name='Name',
        description="Name of the asset. Will be the center part of the mesh name.",
        default='InsertName',
    )

    # VERSION BATCH
    version_batch: bpy.props.BoolProperty(
        name='Batch',
        description='When enabled, allows the creation of multiple meshes in one go.',
        default=False,
    )

    # VERSION (SINGLE)
    version_suffix: bpy.props.IntProperty(
        name='Number',
        description="Version (number) of the mesh. Affects the name suffix.",
        default=1,
    )

    # VERSION SUFFIX_START
    version_suffix_start: bpy.props.IntProperty(
        name='Number (Start)',
        description='When using batch mode, defines the first version (number) to create.',
        default=1,
    )

    # VERSION SUFFIX_END
    version_suffix_end: bpy.props.IntProperty(
        name='Number (End)',
        description='When using batch mode, defines the last version (number) to create.',
        default=1,
    )

    # VERSION (LETTER)
    version_suffix_letter: bpy.props.StringProperty(
        name='Letter',
        description='Letter(s) suffix at end-of-name.',
        default='',
    )

    # INCLUDE DEFAULT MESH
    include_default_mesh: bpy.props.BoolProperty(
        name='Include Default Mesh',
        description='Whether to include the default icosphere mesh as the asset mesh.',
        default=False,
    )

    # INCLUDE SELECTED OBJECTS
    include_selected_obj: bpy.props.BoolProperty(
        name='Use Selection',
        description=(
            "If enabled: "
            "• 1 selected mesh: rename the active mesh. "
            "• 2+ selection: create a new Asset Mesh root and parent selection under it."
        ),
        default=True,
    )

    def execute(self, context):

        mesh_name_lst = self.result_mesh_name_lst()
        if not mesh_name_lst:
            self.report({'WARNING'}, "No mesh name could be generated.")
            return {'CANCELLED'}

        # Manual mode sanity
        if self.settings == 'MANUAL' and not self.asset_name.strip():
            self.report({'WARNING'}, "Name cannot be empty.")
            return {'CANCELLED'}

        # ---------------------------------------------------------------------
        # Selection-based creation / rename
        # ---------------------------------------------------------------------
        if self.include_selected_obj:
            sel = list(context.selected_objects)
            active = context.active_object

            if not sel:
                self.report({'WARNING'}, "No objects selected.")
                return {'CANCELLED'}

            # If batch is enabled, we still only use the first generated name
            target_name = mesh_name_lst[0]

            # Case A: exactly one selected mesh -> rename it
            if len(sel) == 1 and active and active.type == 'MESH':
                active.name = target_name
                active.parent = None  # ensure scene root
                return {'FINISHED'}

            # Case B: multiple selection -> create a Mesh root, parent selection under it
            # Create a "mesh container" object (empty mesh datablock so it's still type MESH)
            mesh_data = bpy.data.meshes.new(target_name)
            root = bpy.data.objects.new(target_name, mesh_data)
            context.collection.objects.link(root)
            root.parent = None  # scene root

            # Parent selection under root (preserve world transforms)
            inv = root.matrix_world.inverted()
            for obj in sel:
                if obj == root:
                    continue
                obj.parent = root
                obj.matrix_parent_inverse = inv

            return {'FINISHED'}

        # ---------------------------------------------------------------------
        # Non-selection mode: create new mesh object(s)
        # ---------------------------------------------------------------------
        created_any = False
        for mesh_name in mesh_name_lst:
            if self.include_default_mesh:
                bpy.ops.mesh.primitive_ico_sphere_add()
                obj = context.active_object
                if obj is None:
                    continue
                obj.name = mesh_name
                obj.parent = None
                created_any = True
            else:
                mesh_data = bpy.data.meshes.new(mesh_name)
                obj = bpy.data.objects.new(mesh_name, mesh_data)
                context.collection.objects.link(obj)
                obj.parent = None
                created_any = True

        return {'FINISHED'} if created_any else {'CANCELLED'}

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
            col.prop(self, "asset_type")

        box = layout.box()
        box.label(text='Name')
        col = box.column()
        col.prop(self, "asset_name")

        # Easy Name Generator Specific
        if self.settings == 'NAMEGEN':
            box = layout.box()
            box.label(text='Suffix')
            col = box.column()
            col.prop(self, "version_batch")
            if self.version_batch:
                col.prop(self, "version_suffix_start")
                col.prop(self, "version_suffix_end")
            else:
                col.prop(self, "version_suffix")
                col.prop(self, "version_suffix_letter")

        # Preview
        mesh_to_create_lst = self.result_mesh_name_lst()
        box = layout.box()
        col = box.column()
        col.prop(self, 'preview', expand=True)

        if mesh_to_create_lst:
            box.label(text=mesh_to_create_lst[0])
            if len(mesh_to_create_lst) > 1:
                box.label(text='...')
                box.label(text=mesh_to_create_lst[-1])

        # Advanced
        box = layout.box()
        box.label(text='Advanced Options')
        col = box.column()
        row = col.row()
        row.prop(self, "include_default_mesh")
        row.prop(self, "include_selected_obj")

    def result_mesh_name_lst(self):
        """
        Find full name of meshes to create, from given parameters.
        Mirrors the Asset Hierarchy naming approach.
        """
        result_mesh_name_lst = []

        if self.settings == 'NAMEGEN':
            # Determine prefix from selected type
            prefix = ''
            for key, idx in self.mesh_types.items():
                if key in self.asset_type:
                    # Reuse your existing prefix source (same as hierarchies)
                    prefix = get_hierarchy_prefix_lst()[idx]
                    break

            if self.version_batch:
                for i in range(self.version_suffix_start, self.version_suffix_end + 1):
                    name = f"{prefix}{self.asset_name}_{format(i, '02')}"
                    result_mesh_name_lst.append(name)
            else:
                name = f"{prefix}{self.asset_name}_{format(self.version_suffix, '02')}"
                if len(self.version_suffix_letter) > 0:
                    name += f"{self.version_suffix_letter}"
                result_mesh_name_lst.append(name)

        elif self.settings == 'MANUAL':
            result_mesh_name_lst.append(self.asset_name)

        return result_mesh_name_lst

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


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

