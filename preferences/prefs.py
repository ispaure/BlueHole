""" Class Holding all the Blue Hole Preferences in a neat, ordered fashion. """

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://github.com/ispaure/BlueHole

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------

import bpy


# ----------------------------------------------------------------------------------------------------------------------
# CODE


def addon_module_name() -> str:
    # e.g. "BlueHole-beta.preferences" -> "BlueHole-beta"
    return __package__.split('.', 1)[0]


def _addon_prefs():
    addon_name: str = addon_module_name()
    addon = bpy.context.preferences.addons.get(addon_name)
    if addon is None:
        return None
    return addon.preferences


class _GeneralPrefs:
    """
    Wrapper for Blue Hole general preferences to provide
    live access to Blender properties with attribute-style syntax.
    """
    def __init__(self, general):
        self._general = general

    # -----------------------------------------------------------
    # GENERAL PROPS
    # -----------------------------------------------------------
    @property
    def active_environment(self) -> str:
        return self._general.active_environment

    @active_environment.setter
    def active_environment(self, value: str):
        self._general.active_environment = value


class _PieKeymapPrefs:
    """
    Wrapper for Blue Hole pie keymap preferences to provide
    live access to Blender properties with attribute-style syntax.
    """
    def __init__(self, pie):
        self._pie = pie

    @property
    def enable_pie_keymaps(self) -> bool:
        return self._pie.enable_pie_keymaps

    @enable_pie_keymaps.setter
    def enable_pie_keymaps(self, value: bool):
        self._pie.enable_pie_keymaps = value


class _SelectionKeymapPrefs:
    """
    Wrapper for Blue Hole selection keymap preferences to provide
    live access to Blender properties with attribute-style syntax.
    """
    def __init__(self, selection):
        self._selection = selection

    @property
    def enable_selection_keymaps(self) -> bool:
        return self._selection.enable_selection_keymaps

    @enable_selection_keymaps.setter
    def enable_selection_keymaps(self, value: bool):
        self._selection.enable_selection_keymaps = value

    @property
    def enable_selection_more_less(self) -> bool:
        return self._selection.enable_selection_more_less

    @enable_selection_more_less.setter
    def enable_selection_more_less(self, value: bool):
        self._selection.enable_selection_more_less = value

    @property
    def enable_selection_tool_switch(self) -> bool:
        return self._selection.enable_selection_tool_switch

    @enable_selection_tool_switch.setter
    def enable_selection_tool_switch(self, value: bool):
        self._selection.enable_selection_tool_switch = value


class _TransformKeymapPrefs:
    """
    Wrapper for Blue Hole transform keymap preferences to provide
    live access to Blender properties with attribute-style syntax.
    """
    def __init__(self, transform):
        self._transform = transform

    @property
    def enable_transform_keymaps(self) -> bool:
        return self._transform.enable_transform_keymaps

    @enable_transform_keymaps.setter
    def enable_transform_keymaps(self, value: bool):
        self._transform.enable_transform_keymaps = value

    @property
    def enable_transform_tool_shortcuts(self) -> bool:
        return self._transform.enable_transform_tool_shortcuts

    @enable_transform_tool_shortcuts.setter
    def enable_transform_tool_shortcuts(self, value: bool):
        self._transform.enable_transform_tool_shortcuts = value


class _MeshKeymapPrefs:
    """
    Wrapper for Blue Hole mesh keymap preferences to provide
    live access to Blender properties with attribute-style syntax.
    """
    def __init__(self, mesh):
        self._mesh = mesh

    @property
    def enable_mesh_keymaps(self) -> bool:
        return self._mesh.enable_mesh_keymaps

    @enable_mesh_keymaps.setter
    def enable_mesh_keymaps(self, value: bool):
        self._mesh.enable_mesh_keymaps = value


class _NavigationKeymapPrefs:
    """
    Wrapper for Blue Hole navigation keymap preferences to provide
    live access to Blender properties with attribute-style syntax.
    """
    def __init__(self, navigation):
        self._navigation = navigation

    @property
    def enable_navigation_keymaps(self) -> bool:
        return self._navigation.enable_navigation_keymaps

    @enable_navigation_keymaps.setter
    def enable_navigation_keymaps(self, value: bool):
        self._navigation.enable_navigation_keymaps = value

    @property
    def enable_navigation_viewport_movement(self) -> bool:
        return self._navigation.enable_navigation_viewport_movement

    @enable_navigation_viewport_movement.setter
    def enable_navigation_viewport_movement(self, value: bool):
        self._navigation.enable_navigation_viewport_movement = value

    @property
    def enable_navigation_viewport_axis(self) -> bool:
        return self._navigation.enable_navigation_viewport_axis

    @enable_navigation_viewport_axis.setter
    def enable_navigation_viewport_axis(self, value: bool):
        self._navigation.enable_navigation_viewport_axis = value


class _ObjectKeymapPrefs:
    """
    Wrapper for Blue Hole object keymap preferences to provide
    live access to Blender properties with attribute-style syntax.
    """
    def __init__(self, obj):
        self._object = obj

    @property
    def enable_object_keymaps(self) -> bool:
        return self._object.enable_object_keymaps

    @enable_object_keymaps.setter
    def enable_object_keymaps(self, value: bool):
        self._object.enable_object_keymaps = value


class _PipelineKeymapPrefs:
    """
    Wrapper for Blue Hole pipeline keymap preferences to provide
    live access to Blender properties with attribute-style syntax.
    """
    def __init__(self, pipeline):
        self._pipeline = pipeline

    @property
    def enable_pipeline_keymaps(self) -> bool:
        return self._pipeline.enable_pipeline_keymaps

    @enable_pipeline_keymaps.setter
    def enable_pipeline_keymaps(self, value: bool):
        self._pipeline.enable_pipeline_keymaps = value


class _SculptKeymapPrefs:
    """
    Wrapper for Blue Hole sculpt keymap preferences to provide
    live access to Blender properties with attribute-style syntax.
    """
    def __init__(self, sculpt):
        self._sculpt = sculpt

    @property
    def enable_sculpt_keymaps(self) -> bool:
        return self._sculpt.enable_sculpt_keymaps

    @enable_sculpt_keymaps.setter
    def enable_sculpt_keymaps(self, value: bool):
        self._sculpt.enable_sculpt_keymaps = value


class _UVKeymapPrefs:
    """
    Wrapper for Blue Hole UV keymap preferences to provide
    live access to Blender properties with attribute-style syntax.
    """
    def __init__(self, uv):
        self._uv = uv

    @property
    def enable_uv_keymaps(self) -> bool:
        return self._uv.enable_uv_keymaps

    @enable_uv_keymaps.setter
    def enable_uv_keymaps(self, value: bool):
        self._uv.enable_uv_keymaps = value


class _KeymapPrefs:
    """
    Wrapper for Blue Hole keymap preferences to provide
    live access to Blender properties with attribute-style syntax.
    """
    def __init__(self, keymap):
        self._keymap = keymap

    @property
    def enable_keymaps(self) -> bool:
        return self._keymap.enable_keymaps

    @enable_keymaps.setter
    def enable_keymaps(self, value: bool):
        self._keymap.enable_keymaps = value

    @property
    def pie(self):
        return _PieKeymapPrefs(self._keymap.pie)

    @property
    def selection(self):
        return _SelectionKeymapPrefs(self._keymap.selection)

    @property
    def mesh(self):
        return _MeshKeymapPrefs(self._keymap.mesh)

    @property
    def navigation(self):
        return _NavigationKeymapPrefs(self._keymap.navigation)

    @property
    def object(self):
        return _ObjectKeymapPrefs(self._keymap.object)

    @property
    def pipeline(self):
        return _PipelineKeymapPrefs(self._keymap.pipeline)

    @property
    def sculpt(self):
        return _SculptKeymapPrefs(self._keymap.sculpt)

    @property
    def transform(self):
        return _TransformKeymapPrefs(self._keymap.transform)

    @property
    def uv(self):
        return _UVKeymapPrefs(self._keymap.uv)


class _PiePrefs:
    """
    Wrapper for Blue Hole pie menu preferences to provide
    live access to Blender properties with attribute-style syntax.
    """
    def __init__(self, pie):
        self._pie = pie

    # -----------------------------------------------------------
    # GENERAL PROPS
    # -----------------------------------------------------------
    @property
    def enable_pie_menus(self) -> bool:
        return self._pie.enable_pie_menus

    @enable_pie_menus.setter
    def enable_pie_menus(self, value: bool):
        self._pie.enable_pie_menus = value


class _BridgePrefs:
    """
    Wrapper for Blue Hole general preferences to provide
    live access to Blender properties with attribute-style syntax.
    """
    def __init__(self, bridge):
        self._bridge = bridge

    # -----------------------------------------------------------
    # SOURCE CONTENT PATHS
    # -----------------------------------------------------------

    @property
    def sc_path(self) -> str:
        return self._bridge.sc_path

    @sc_path.setter
    def sc_path(self, value: str):
        self._bridge.sc_path = value

    @property
    def sc_path_alternate(self) -> str:
        return self._bridge.sc_path_alternate

    @sc_path_alternate.setter
    def sc_path_alternate(self, value: str):
        self._bridge.sc_path_alternate = value

    @property
    def sc_path_mac(self) -> str:
        return self._bridge.sc_path_mac

    @sc_path_mac.setter
    def sc_path_mac(self, value: str):
        self._bridge.sc_path_mac = value

    @property
    def sc_path_mac_alternate(self) -> str:
        return self._bridge.sc_path_mac_alternate

    @sc_path_mac_alternate.setter
    def sc_path_mac_alternate(self, value: str):
        self._bridge.sc_path_mac_alternate = value

    @property
    def sc_path_linux(self) -> str:
        return self._bridge.sc_path_linux

    @sc_path_linux.setter
    def sc_path_linux(self, value: str):
        self._bridge.sc_path_linux = value

    @property
    def sc_path_linux_alternate(self) -> str:
        return self._bridge.sc_path_linux_alternate

    @sc_path_linux_alternate.setter
    def sc_path_linux_alternate(self, value: str):
        self._bridge.sc_path_linux_alternate = value

    # -----------------------------------------------------------
    # ENGINE SETTINGS
    # -----------------------------------------------------------
    @property
    def active_game_engine(self) -> str:
        return self._bridge.active_game_engine

    @active_game_engine.setter
    def active_game_engine(self, value: str):
        self._bridge.active_game_engine = value

    # -----------------------------------------------------------
    # EXPORTS: BATCH SELECTION
    # -----------------------------------------------------------
    @property
    def exp_select_zero_root_transform(self) -> bool:
        return self._bridge.exp_select_zero_root_transform

    @exp_select_zero_root_transform.setter
    def exp_select_zero_root_transform(self, value: bool):
        self._bridge.exp_select_zero_root_transform = value

    # -----------------------------------------------------------
    # EXPORTS: ASSET HIERARCHIES (UNREAL)
    # -----------------------------------------------------------
    @property
    def ue_bridge_zero_root_transform(self) -> bool:
        return self._bridge.ue_bridge_zero_root_transform

    @ue_bridge_zero_root_transform.setter
    def ue_bridge_zero_root_transform(self, value: bool):
        self._bridge.ue_bridge_zero_root_transform = value

    @property
    def ue_bridge_include_animation(self) -> bool:
        return self._bridge.ue_bridge_include_animation

    @ue_bridge_include_animation.setter
    def ue_bridge_include_animation(self, value: bool):
        self._bridge.ue_bridge_include_animation = value

    @property
    def ue_automated(self) -> bool:
        return self._bridge.ue_automated

    @ue_automated.setter
    def ue_automated(self, value: bool):
        self._bridge.ue_automated = value

    @property
    def ue_import_materials(self) -> bool:
        return self._bridge.ue_import_materials

    @ue_import_materials.setter
    def ue_import_materials(self, value: bool):
        self._bridge.ue_import_materials = value

    @property
    def ue_import_textures(self) -> bool:
        return self._bridge.ue_import_textures

    @ue_import_textures.setter
    def ue_import_textures(self, value: bool):
        self._bridge.ue_import_textures = value

    @property
    def ue_enable_send_override(self) -> bool:
        return self._bridge.ue_enable_send_override

    @ue_enable_send_override.setter
    def ue_enable_send_override(self, value: bool):
        self._bridge.ue_enable_send_override = value

    @property
    def ue_op_send_override(self) -> str:
        return self._bridge.ue_op_send_override

    @ue_op_send_override.setter
    def ue_op_send_override(self, value: str):
        self._bridge.ue_op_send_override = value

    # -----------------------------------------------------------
    # EXPORTS: ASSET HIERARCHIES (UNITY)
    # -----------------------------------------------------------
    @property
    def unity_assets_path(self) -> str:
        return self._bridge.unity_assets_path

    @unity_assets_path.setter
    def unity_assets_path(self, value: str):
        self._bridge.unity_assets_path = value

    @property
    def unity_assets_path_mac(self) -> str:
        return self._bridge.unity_assets_path_mac

    @unity_assets_path_mac.setter
    def unity_assets_path_mac(self, value: str):
        self._bridge.unity_assets_path_mac = value

    @property
    def unity_assets_path_linux(self) -> str:
        return self._bridge.unity_assets_path_linux

    @unity_assets_path_linux.setter
    def unity_assets_path_linux(self, value: str):
        self._bridge.unity_assets_path_linux = value

    @property
    def unity_bridge_zero_root_transform(self) -> bool:
        return self._bridge.unity_bridge_zero_root_transform

    @unity_bridge_zero_root_transform.setter
    def unity_bridge_zero_root_transform(self, value: bool):
        self._bridge.unity_bridge_zero_root_transform = value

    @property
    def unity_bridge_include_animation(self) -> bool:
        return self._bridge.unity_bridge_include_animation

    @unity_bridge_include_animation.setter
    def unity_bridge_include_animation(self, value: bool):
        self._bridge.unity_bridge_include_animation = value

    @property
    def unity_forward_axis(self) -> str:
        return self._bridge.unity_forward_axis

    @unity_forward_axis.setter
    def unity_forward_axis(self, value: str):
        self._bridge.unity_forward_axis = value

    @property
    def unity_up_axis(self) -> str:
        return self._bridge.unity_up_axis

    @unity_up_axis.setter
    def unity_up_axis(self, value: str):
        self._bridge.unity_up_axis = value


class _DirectoryPrefs:
    def __init__(self, directory):
        self._directory = directory

    # ------------------- Source Content Directory Structure -------------------
    @property
    def sc_dir_struct_scenes(self) -> str:
        return self._directory.sc_dir_struct_scenes

    @sc_dir_struct_scenes.setter
    def sc_dir_struct_scenes(self, value: str):
        self._directory.sc_dir_struct_scenes = value

    @property
    def sc_dir_struct_resources(self) -> str:
        return self._directory.sc_dir_struct_resources

    @sc_dir_struct_resources.setter
    def sc_dir_struct_resources(self, value: str):
        self._directory.sc_dir_struct_resources = value

    @property
    def sc_dir_struct_st(self) -> str:
        return self._directory.sc_dir_struct_st

    @sc_dir_struct_st.setter
    def sc_dir_struct_st(self, value: str):
        self._directory.sc_dir_struct_st = value

    @property
    def sc_dir_struct_st_hr(self) -> str:
        return self._directory.sc_dir_struct_st_hr

    @sc_dir_struct_st_hr.setter
    def sc_dir_struct_st_hr(self, value: str):
        self._directory.sc_dir_struct_st_hr = value

    @property
    def sc_dir_struct_st_lr(self) -> str:
        return self._directory.sc_dir_struct_st_lr

    @sc_dir_struct_st_lr.setter
    def sc_dir_struct_st_lr(self, value: str):
        self._directory.sc_dir_struct_st_lr = value

    @property
    def sc_dir_struct_ref(self) -> str:
        return self._directory.sc_dir_struct_ref

    @sc_dir_struct_ref.setter
    def sc_dir_struct_ref(self, value: str):
        self._directory.sc_dir_struct_ref = value

    @property
    def sc_dir_struct_final(self) -> str:
        return self._directory.sc_dir_struct_final

    @sc_dir_struct_final.setter
    def sc_dir_struct_final(self, value: str):
        self._directory.sc_dir_struct_final = value

    @property
    def sc_dir_struct_msh_bake(self) -> str:
        return self._directory.sc_dir_struct_msh_bake

    @sc_dir_struct_msh_bake.setter
    def sc_dir_struct_msh_bake(self, value: str):
        self._directory.sc_dir_struct_msh_bake = value


class _ContainerPrefs:
    def __init__(self, container):
        self._container = container

    # ------------------- Asset Container Types -------------------

    @property
    def enable_asset_hierarchy_container(self) -> bool:
        return self._container.enable_asset_hierarchy_container

    @enable_asset_hierarchy_container.setter
    def enable_asset_hierarchy_container(self, value: bool):
        self._container.enable_asset_hierarchy_container = value

    @property
    def enable_asset_mesh_container(self) -> bool:
        return self._container.enable_asset_mesh_container

    @enable_asset_mesh_container.setter
    def enable_asset_mesh_container(self, value: bool):
        self._container.enable_asset_mesh_container = value

    @property
    def enable_asset_collection_container(self) -> bool:
        return self._container.enable_asset_collection_container

    @enable_asset_collection_container.setter
    def enable_asset_collection_container(self, value: bool):
        self._container.enable_asset_collection_container = value

    # ------------------- Asset Hierarchy Structure -------------------
    @property
    def asset_hierarchy_struct_prefix_static_mesh(self) -> str:
        return self._container.asset_hierarchy_struct_prefix_static_mesh

    @asset_hierarchy_struct_prefix_static_mesh.setter
    def asset_hierarchy_struct_prefix_static_mesh(self, value: str):
        self._container.asset_hierarchy_struct_prefix_static_mesh = value

    @property
    def asset_hierarchy_struct_prefix_static_mesh_kit(self) -> str:
        return self._container.asset_hierarchy_struct_prefix_static_mesh_kit

    @asset_hierarchy_struct_prefix_static_mesh_kit.setter
    def asset_hierarchy_struct_prefix_static_mesh_kit(self, value: str):
        self._container.asset_hierarchy_struct_prefix_static_mesh_kit = value

    @property
    def asset_hierarchy_struct_prefix_skeletal_mesh(self) -> str:
        return self._container.asset_hierarchy_struct_prefix_skeletal_mesh

    @asset_hierarchy_struct_prefix_skeletal_mesh.setter
    def asset_hierarchy_struct_prefix_skeletal_mesh(self, value: str):
        self._container.asset_hierarchy_struct_prefix_skeletal_mesh = value

    # ------------------- Exclude If No Children -------------------
    @property
    def exclude_element_if_no_child(self) -> bool:
        return self._container.exclude_element_if_no_child

    @exclude_element_if_no_child.setter
    def exclude_element_if_no_child(self, value: bool):
        self._container.exclude_element_if_no_child = value

    # ------------------- Create Elements -------------------
    @property
    def create_element_render(self) -> bool:
        return self._container.create_element_render

    @create_element_render.setter
    def create_element_render(self, value: bool):
        self._container.create_element_render = value

    @property
    def create_element_collision(self) -> bool:
        return self._container.create_element_collision

    @create_element_collision.setter
    def create_element_collision(self, value: bool):
        self._container.create_element_collision = value

    @property
    def create_element_sockets(self) -> bool:
        return self._container.create_element_sockets

    @create_element_sockets.setter
    def create_element_sockets(self, value: bool):
        self._container.create_element_sockets = value

    # ------------------- Name Elements -------------------
    @property
    def asset_hierarchy_empty_object_meshes(self) -> str:
        return self._container.asset_hierarchy_empty_object_meshes

    @asset_hierarchy_empty_object_meshes.setter
    def asset_hierarchy_empty_object_meshes(self, value: str):
        self._container.asset_hierarchy_empty_object_meshes = value

    @property
    def asset_hierarchy_empty_object_collisions(self) -> str:
        return self._container.asset_hierarchy_empty_object_collisions

    @asset_hierarchy_empty_object_collisions.setter
    def asset_hierarchy_empty_object_collisions(self, value: str):
        self._container.asset_hierarchy_empty_object_collisions = value

    @property
    def asset_hierarchy_empty_object_sockets(self) -> str:
        return self._container.asset_hierarchy_empty_object_sockets

    @asset_hierarchy_empty_object_sockets.setter
    def asset_hierarchy_empty_object_sockets(self, value: str):
        self._container.asset_hierarchy_empty_object_sockets = value


class _SCPrefs:
    def __init__(self, sc: bpy.types.PropertyGroup):
        self._sc = sc

    # ----------------- Source Control -----------------

    @property
    def source_control_enable(self) -> bool:
        return self._sc.source_control_enable

    @source_control_enable.setter
    def source_control_enable(self, value: bool):
        self._sc.source_control_enable = value

    @property
    def source_control_solution(self) -> str:
        return self._sc.source_control_solution

    @source_control_solution.setter
    def source_control_solution(self, value: str):
        self._sc.source_control_solution = value

    @property
    def source_control_error_aborts_exp(self) -> bool:
        return self._sc.source_control_error_aborts_exp

    @source_control_error_aborts_exp.setter
    def source_control_error_aborts_exp(self, value: bool):
        self._sc.source_control_error_aborts_exp = value

    # ----------------- Override Environment -----------------

    @property
    def win32_env_override(self) -> bool:
        return self._sc.win32_env_override

    @win32_env_override.setter
    def win32_env_override(self, value: bool):
        self._sc.win32_env_override = value

    @property
    def win32_env_setting_p4port(self) -> str:
        return self._sc.win32_env_setting_p4port

    @win32_env_setting_p4port.setter
    def win32_env_setting_p4port(self, value: str):
        self._sc.win32_env_setting_p4port = value

    @property
    def win32_env_setting_p4user(self) -> str:
        return self._sc.win32_env_setting_p4user

    @win32_env_setting_p4user.setter
    def win32_env_setting_p4user(self, value: str):
        self._sc.win32_env_setting_p4user = value

    @property
    def win32_env_setting_p4client(self) -> str:
        return self._sc.win32_env_setting_p4client

    @win32_env_setting_p4client.setter
    def win32_env_setting_p4client(self, value: str):
        self._sc.win32_env_setting_p4client = value

    @property
    def macos_env_setting_p4port(self) -> str:
        return self._sc.macos_env_setting_p4port

    @macos_env_setting_p4port.setter
    def macos_env_setting_p4port(self, value: str):
        self._sc.macos_env_setting_p4port = value

    @property
    def macos_env_setting_p4user(self) -> str:
        return self._sc.macos_env_setting_p4user

    @macos_env_setting_p4user.setter
    def macos_env_setting_p4user(self, value: str):
        self._sc.macos_env_setting_p4user = value

    @property
    def macos_env_setting_p4client(self) -> str:
        return self._sc.macos_env_setting_p4client

    @macos_env_setting_p4client.setter
    def macos_env_setting_p4client(self, value: str):
        self._sc.macos_env_setting_p4client = value

    @property
    def linux_env_setting_p4port(self) -> str:
        return self._sc.linux_env_setting_p4port

    @linux_env_setting_p4port.setter
    def linux_env_setting_p4port(self, value: str):
        self._sc.linux_env_setting_p4port = value

    @property
    def linux_env_setting_p4user(self) -> str:
        return self._sc.linux_env_setting_p4user

    @linux_env_setting_p4user.setter
    def linux_env_setting_p4user(self, value: str):
        self._sc.linux_env_setting_p4user = value

    @property
    def linux_env_setting_p4client(self) -> str:
        return self._sc.linux_env_setting_p4client

    @linux_env_setting_p4client.setter
    def linux_env_setting_p4client(self, value: str):
        self._sc.linux_env_setting_p4client = value

    @property
    def p4v_app_path_mac(self) -> str:
        return self._sc.p4v_app_path_mac

    @p4v_app_path_mac.setter
    def p4v_app_path_mac(self, value: str):
        self._sc.p4v_app_path_mac = value

    @property
    def p4_parallel_path_linux(self) -> str:
        return self._sc.p4_parallel_path_linux

    @p4_parallel_path_linux.setter
    def p4_parallel_path_linux(self, value: str):
        self._sc.p4_parallel_path_linux = value


class _HelpNUpdatePrefs:
    def __init__(self, help_n_update):
        self._help_n_update = help_n_update

    # ----------------- Updates -----------------

    @property
    def auto_update_addon(self) -> bool:
        return self._help_n_update.auto_update_addon

    @auto_update_addon.setter
    def auto_update_addon(self, value: bool):
        self._help_n_update.auto_update_addon = value

    @property
    def update_version(self) -> str:
        return self._help_n_update.update_version

    @update_version.setter
    def update_version(self, value: str):
        self._help_n_update.update_version = value


class BHPrefs:
    @property
    def prefs(self):
        return _addon_prefs()

    def is_ready(self) -> bool:
        return self.prefs is not None

    @property
    def general(self):
        p = self.prefs
        return None if p is None else _GeneralPrefs(p.general)

    @property
    def directory(self):
        p = self.prefs
        return None if p is None else _DirectoryPrefs(p.directory)

    @property
    def bridge(self):
        p = self.prefs
        return None if p is None else _BridgePrefs(p.bridge)

    @property
    def container(self):
        p = self.prefs
        return None if p is None else _ContainerPrefs(p.container)

    @property
    def sc(self):
        p = self.prefs
        return None if p is None else _SCPrefs(p.sourcecontrol)

    @property
    def pie(self):
        p = self.prefs
        return None if p is None else _PiePrefs(p.pie)

    @property
    def help_n_update(self):
        p = self.prefs
        return None if p is None else _HelpNUpdatePrefs(p.help_n_update)

    @property
    def keymap(self):
        p = self.prefs
        return None if p is None else _KeymapPrefs(p.keymap)


def prefs() -> BHPrefs:
    return BHPrefs()
