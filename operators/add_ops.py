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
from ..blenderUtils import objectUtils
from ..blenderUtils.export.exportSettingsPresets import *
from ..blenderUtils.export.model.assetContainerGroup import get_hierarchy_prefix_lst
from ..preferences.prefs import *


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class _BH_NameGenUIMixin:
    """
    Shared name-generation + shared UI blocks for Asset Hierarchy / Asset Mesh.

    What it covers:
    - settings / preview
    - prefix (Type)
    - name
    - suffix (batch/version)
    - preview box (with optional extra lines)

    What it does NOT cover:
    - operator-specific advanced options + structure hints
    - operator-specific execute behavior
    """

    # TYPE and their index position (see env_variables.ini > ObjectHierarchyStructure > prefixes)
    hierarchy_types = {'Mesh Asset': 0, 'Mesh Kit Asset': 1, 'Skeletal Mesh': 2}
    prefix_items = [(k, k, '') for k in hierarchy_types.keys()]

    asset_type: bpy.props.EnumProperty(
        name='Type',
        description="Affects the name's prefix",
        items=prefix_items
    )

    # UI MODE
    settings: bpy.props.EnumProperty(
        name='Settings',
        description='Settings to display',
        items=[
            ('NAMEGEN', 'Easy Name Generator',
             'Creates name matching naming convention, preventing user error.'),
            ('MANUAL', 'Manual Name Entry',
             'Creates name matching user-given name, regardless if it matches naming conventions or not.'),
        ],
        default='NAMEGEN'
    )

    preview: bpy.props.EnumProperty(
        name='Preview',
        items=[('PREVIEW', 'Preview', 'Preview name(s) that will be created.')],
        default='PREVIEW'
    )

    # NAME
    asset_name: bpy.props.StringProperty(
        name='Name',
        description='Name of the asset. Will be the center part of the generated name',
        default='InsertName'
    )

    # VERSION BATCH
    version_batch: bpy.props.BoolProperty(
        name='Batch',
        description='When enabled, allows the creation of multiple items in one go',
        default=False
    )

    # VERSION (SINGLE)
    version_suffix: bpy.props.IntProperty(
        name='Number',
        description='Version (number). Affects the generated name suffix',
        default=1
    )

    # VERSION SUFFIX_START
    version_suffix_start: bpy.props.IntProperty(
        name='Number (Start)',
        description='When using batch mode, defines the first version (number) to create',
        default=1
    )

    # VERSION SUFFIX_END
    version_suffix_end: bpy.props.IntProperty(
        name='Number (End)',
        description='When using batch mode, defines the last version (number) to create',
        default=1
    )

    # VERSION (LETTER)
    version_suffix_letter: bpy.props.StringProperty(
        name='Letter',
        description='Letter(s) suffix at end-of-name.',
        default=''
    )

    # -------------------------------------------------------------------------------------------------
    # SHARED NAMEGEN
    # -------------------------------------------------------------------------------------------------

    def _build_name_lst(self) -> list[str]:
        """
        Shared NAMEGEN/MANUAL name generation.
        """
        result_name_lst: list[str] = []

        if self.settings == 'NAMEGEN':

            def _prefix() -> str:
                p = ''
                for key, idx in self.hierarchy_types.items():
                    if key in self.asset_type:
                        p += get_hierarchy_prefix_lst()[idx]
                return p

            if self.version_batch:
                start = min(self.version_suffix_start, self.version_suffix_end)
                end = max(self.version_suffix_start, self.version_suffix_end)
                for item in range(start, end + 1):
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

    # -------------------------------------------------------------------------------------------------
    # SHARED UI BLOCKS
    # -------------------------------------------------------------------------------------------------

    def _draw_settings_tabs(self, layout):
        column = layout.column(align=True)
        row = column.row(align=True)
        row.prop(self, 'settings', expand=True)

    def _draw_prefix_box(self, layout):
        if self.settings != 'NAMEGEN':
            return
        box = layout.box()
        box.label(text='Prefix')
        col = box.column()
        col.prop(self, "asset_type")

    def _draw_name_box(self, layout):
        box = layout.box()
        box.label(text='Name')
        col = box.column()
        col.prop(self, "asset_name")

    def _draw_suffix_box(self, layout):
        if self.settings != 'NAMEGEN':
            return
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

    def _preview_extra_lines(self, context, name_lst: list[str]) -> list[str]:
        """
        Optional hook: subclasses can override to inject extra preview lines
        displayed under the main preview name.

        Return a list of lines (strings). Each will be rendered indented.
        """
        return []

    def _draw_preview_box(self, layout, context, name_lst: list[str]):
        """
        Preview box showing first/last name, plus optional extra lines.
        """
        box = layout.box()
        col = box.column()
        row = col.row()
        row.prop(self, 'preview', expand=True)

        if name_lst:
            box.label(text=name_lst[0])

            extra_lines = self._preview_extra_lines(context, name_lst)
            for ln in extra_lines:
                box.label(text='   ↳ ' + ln)

            if len(name_lst) > 1:
                box.label(text='...')
                box.label(text=name_lst[-1])
        else:
            box.label(text="(No names generated)", icon='ERROR')


# ----------------------------------------------------------------------------------------------------------------------
# OPERATORS


class SceneAddAssetHierarchy(bpy.types.Operator):

    bl_idname = "wm.bh_scene_add_asset_hierarchy"
    bl_label = "Asset Hierarchy"
    bl_description = "Create an Asset Hierarchy in the scene."

    settings: bpy.props.EnumProperty(
        name='Settings',
        description='Settings to display',
        items=[
            ('NAMEGEN', 'Easy Name Generator',
             'Creates hierarchy name matching naming convention, preventing user error.'),
            ('MANUAL', 'Manual Name Entry',
             'Creates hierarchy matching user-given name, regardless if it matches naming conventions or not.'),
        ],
        default='NAMEGEN'
    )

    preview: bpy.props.EnumProperty(
        name='Preview',
        items=[('PREVIEW', 'Preview', 'Preview name of Hierarchies that will be created.')],
        default='PREVIEW'
    )

    # TYPE and their index position (see env_variables.ini > ObjectHierarchyStructure > prefixes)
    hierarchy_types = {'Mesh Asset': 0, 'Mesh Kit Asset': 1, 'Skeletal Mesh': 2}
    prefix_items = []
    for key in hierarchy_types.keys():
        prefix_items.append((key, key, ''))

    asset_type: bpy.props.EnumProperty(
        name='Type',
        description="Affects the hierarchy name's prefix",
        items=prefix_items
    )

    # NAME
    asset_name: bpy.props.StringProperty(
        name='Name',
        description="Name of the asset. Will be the center part of the hierarchy name",
        default='InsertName'
    )

    # VERSION BATCH
    version_batch: bpy.props.BoolProperty(
        name='Batch',
        description='When enabled, allows the creation of multiple hierarchies in one go',
        default=False
    )

    # VERSION (SINGLE)
    version_suffix: bpy.props.IntProperty(
        name='Number',
        description="Version (number). Affects the hierarchy name's suffix",
        default=1
    )

    # VERSION SUFFIX_START
    version_suffix_start: bpy.props.IntProperty(
        name='Number (Start)',
        description='When using batch mode, defines the first version (number) to create',
        default=1
    )

    # VERSION SUFFIX_END
    version_suffix_end: bpy.props.IntProperty(
        name='Number (End)',
        description='When using batch mode, defines the last version (number) to create',
        default=1
    )

    # VERSION (LETTER)
    version_suffix_letter: bpy.props.StringProperty(
        name='Letter',
        description='Letter(s) suffix at end-of-name.',
        default=''
    )

    # CONTENT
    include_default_mesh: bpy.props.BoolProperty(
        name='Include Default Mesh',
        description='Whether to include the default icosphere mesh as part of the hierarchy',
        default=False
    )

    dsp_empty_obj_arrows: bpy.props.BoolProperty(
        name='Display as Arrows',
        description='When set to true, display Empty Objects as XYZ Arrows',
        default=True
    )

    include_selected_obj: bpy.props.BoolProperty(
        name='Use Selection',
        description=(
            "When enabled, parents the current selection under the hierarchy.\n"
            "If disabled, a hierarchy is created without using the current selection."
        ),
        default=False
    )

    # -------------------------------------------------------------------------------------------------
    # EXECUTE
    # -------------------------------------------------------------------------------------------------

    def execute(self, context):

        name_lst = self.result_hierarchy_lst()
        if not name_lst:
            self.report({'WARNING'}, "No names generated.")
            return {'CANCELLED'}

        # If user enabled selection but there is no selection, don't fail by default.
        if self.include_selected_obj and not context.selected_objects:
            self.include_selected_obj = False

        # If using selection, default mesh should never be used (even if previously checked).
        if self.include_selected_obj:
            self.include_default_mesh = False

        objectUtils.add_asset_hierarchy(
            name_lst,
            self.include_default_mesh,
            self.include_selected_obj,
            self.dsp_empty_obj_arrows
        )
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
        hierarchy_to_create_lst = self.result_hierarchy_lst()
        box = layout.box()
        col = box.column()

        row = col.row()
        row.prop(self, 'preview', expand=True)

        if hierarchy_to_create_lst:
            box.label(text=hierarchy_to_create_lst[0])

            # Show structure preview (now always valid: content goes under Render if enabled, else root)
            if prefs().container.create_element_render:
                box.label(text='   ↳ ' + prefs().container.asset_hierarchy_empty_object_meshes)
            if prefs().container.create_element_collision:
                box.label(text='   ↳ ' + prefs().container.asset_hierarchy_empty_object_collisions)
            if prefs().container.create_element_sockets:
                box.label(text='   ↳ ' + prefs().container.asset_hierarchy_empty_object_sockets)

            if len(hierarchy_to_create_lst) > 1:
                box.label(text='...')
                box.label(text=hierarchy_to_create_lst[-1])

        # Advanced Options
        box = layout.box()
        box.label(text='Advanced Options')
        col = box.column()

        row = col.row(align=True)
        row.prop(self, 'include_selected_obj')

        sub = row.row(align=True)
        sub.enabled = not self.include_selected_obj
        sub.prop(self, "include_default_mesh")

        row = col.row()
        row.prop(self, "dsp_empty_obj_arrows")

        if self.include_selected_obj and not context.selected_objects:
            hint = col.row()
            hint.label(text="No selection detected: selection will be ignored.", icon='INFO')

        if self.version_batch and self.include_selected_obj:
            hint = col.row()
            hint.enabled = False
            hint.label(text="Use Selection only applies meaningfully when creating a single hierarchy.", icon='INFO')

    # -------------------------------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------------------------------

    def result_hierarchy_lst(self):
        """
        Find full name of hierarchies to create, from given parameters.
        """
        result_hierarchy_lst = []

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
                    result_hierarchy_lst.append(nm)
            else:
                nm = _prefix()
                nm += self.asset_name
                nm += '_' + str(format(self.version_suffix, '02'))
                if len(self.version_suffix_letter) > 0:
                    nm += '' + self.version_suffix_letter
                result_hierarchy_lst.append(nm)

        elif self.settings == 'MANUAL':
            result_hierarchy_lst.append(self.asset_name)

        return result_hierarchy_lst

    def invoke(self, context, event):
        # Default "Use Selection" based on whether there is a selection
        self.include_selected_obj = bool(context.selected_objects)

        # If Use Selection is defaulted on, default mesh should not be used.
        if self.include_selected_obj:
            self.include_default_mesh = False

        return context.window_manager.invoke_props_dialog(self)


class SceneAddAssetCollection(bpy.types.Operator):

    bl_idname = "wm.bh_scene_add_asset_collection"
    bl_label = "Asset Collection"
    bl_description = "Create Asset Collection of given name to scene."

    def execute(self, context):
        log(Severity.CRITICAL, self.bl_label, f'{self.bl_label} has not yet been implemented.')
        return {'CANCELLED'}


class SceneAddAssetMesh(bpy.types.Operator, _BH_NameGenUIMixin):

    bl_idname = "wm.bh_scene_add_asset_mesh"
    bl_label = "Asset Mesh"
    bl_description = "Create Asset Mesh of given name to scene."

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
            "• 0 selected meshes: create a new Asset Mesh root with empty geometry.\n"
            "If disabled: creates a new Asset Mesh root mesh."
        ),
        default=True
    )

    def execute(self, context):

        name_lst = self._build_name_lst()
        if not name_lst:
            self.report({'WARNING'}, "No names generated.")
            return {'CANCELLED'}

        sel_meshes = [o for o in context.selected_objects if o.type == 'MESH']

        if self.version_batch:
            created = 0
            for nm in name_lst:
                self._create_asset_mesh_root(context, nm)
                created += 1
            self.report({'INFO'}, f"Created {created} Asset Mesh root(s).")
            return {'FINISHED'}

        nm = name_lst[0]

        if self.include_selected_obj:

            if len(sel_meshes) == 1:
                obj = context.active_object if (context.active_object and context.active_object.type == 'MESH') else sel_meshes[0]
                obj.name = nm
                obj.parent = None
                obj.matrix_parent_inverse.identity()
                self.report({'INFO'}, f'Renamed mesh to "{nm}".')
                return {'FINISHED'}

            if len(sel_meshes) >= 2:
                root = self._create_asset_mesh_root(context, nm, force_empty_geometry=True)
                for o in sel_meshes:
                    if o == root:
                        continue
                    o.parent = root
                    o.matrix_parent_inverse = root.matrix_world.inverted()
                self.report({'INFO'}, f'Created "{nm}" and parented {len(sel_meshes)} mesh(es).')
                return {'FINISHED'}

            self._create_asset_mesh_root(context, nm, force_empty_geometry=True)
            self.report({'INFO'}, f'Created "{nm}" (empty geometry).')
            return {'FINISHED'}

        self._create_asset_mesh_root(context, nm)
        self.report({'INFO'}, f'Created "{nm}".')
        return {'FINISHED'}

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        self._draw_settings_tabs(layout)
        self._draw_prefix_box(layout)
        self._draw_name_box(layout)
        self._draw_suffix_box(layout)

        name_lst = self._build_name_lst()
        self._draw_preview_box(layout, context, name_lst)

        box = layout.box()
        box.label(text='Advanced Options')
        col = box.column()

        if not self.version_batch:
            row = col.row(align=True)
            row.prop(self, "include_selected_obj")

            sub = row.row(align=True)
            sub.enabled = not self.include_selected_obj
            sub.prop(self, "include_default_mesh")
        else:
            col.prop(self, "include_default_mesh")

    def invoke(self, context, event):
        self.include_selected_obj = any(o.type == 'MESH' for o in context.selected_objects)
        return context.window_manager.invoke_props_dialog(self)

    def _create_asset_mesh_root(
        self,
        context,
        name: str,
        *,
        force_empty_geometry: bool = False,
    ) -> bpy.types.Object:
        """
        Create an Asset Mesh root object at the scene root.

        If force_empty_geometry is True, always create an empty mesh datablock (no geometry),
        regardless of include_default_mesh.

        Otherwise:
            If include_default_mesh is True, create a primitive mesh;
            else create an empty mesh datablock.
        """
        if (not force_empty_geometry) and self.include_default_mesh:
            bpy.ops.mesh.primitive_ico_sphere_add()
            obj = context.active_object
            obj.name = name
        else:
            mesh_data = bpy.data.meshes.new(name=f"{name}_DATA")
            obj = bpy.data.objects.new(name, mesh_data)
            context.collection.objects.link(obj)
            context.view_layer.objects.active = obj
            obj.select_set(True)

        obj.parent = None
        obj.matrix_parent_inverse.identity()
        return obj


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

# List of classes to register/unregister

classes = (SceneAddAssetHierarchy,
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

