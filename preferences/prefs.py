""" Class Holding all of the Blue Hole Preferences in a neat, ordered fashion. """

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

bh_addon_name = 'BlueHole'
def addon_module_name() -> str:
    # e.g. "BlueHole-beta.preferences" -> "BlueHole-beta"
    return __package__.split('.', 1)[0]


def _addon_prefs():
    addon_module_name = addon_module_name()
    print('TESTING')
    print(addon_module_name)
    return bpy.context.preferences.addons[addon_module_name].preferences


class _GeneralPrefs:
    """
    Wrapper for Blue Hole general preferences to provide
    live access to Blender properties with attribute-style syntax.
    """
    def __init__(self, general):
        self._general = general

    # -----------------------------------------------------------
    # EXPORTS: BATCH SELECTION
    # -----------------------------------------------------------
    @property
    def exp_select_zero_root_transform(self) -> bool:
        return self._general.exp_select_zero_root_transform

    @exp_select_zero_root_transform.setter
    def exp_select_zero_root_transform(self, value: bool):
        self._general.exp_select_zero_root_transform = value

    # -----------------------------------------------------------
    # EXPORTS: ASSET HIERARCHIES (UNREAL)
    # -----------------------------------------------------------
    @property
    def ue_bridge_zero_root_transform(self) -> bool:
        return self._general.ue_bridge_zero_root_transform

    @ue_bridge_zero_root_transform.setter
    def ue_bridge_zero_root_transform(self, value: bool):
        self._general.ue_bridge_zero_root_transform = value

    @property
    def ue_bridge_include_animation(self) -> bool:
        return self._general.ue_bridge_include_animation

    @ue_bridge_include_animation.setter
    def ue_bridge_include_animation(self, value: bool):
        self._general.ue_bridge_include_animation = value

    @property
    def ue_automated(self) -> bool:
        return self._general.ue_automated

    @ue_automated.setter
    def ue_automated(self, value: bool):
        self._general.ue_automated = value

    @property
    def ue_import_materials(self) -> bool:
        return self._general.ue_import_materials

    @ue_import_materials.setter
    def ue_import_materials(self, value: bool):
        self._general.ue_import_materials = value

    @property
    def ue_import_textures(self) -> bool:
        return self._general.ue_import_textures

    @ue_import_textures.setter
    def ue_import_textures(self, value: bool):
        self._general.ue_import_textures = value

    # -----------------------------------------------------------
    # EXPORTS: ASSET HIERARCHIES (UNITY)
    # -----------------------------------------------------------
    @property
    def unity_assets_path(self) -> str:
        return self._general.unity_assets_path

    @unity_assets_path.setter
    def unity_assets_path(self, value: str):
        self._general.unity_assets_path = value

    @property
    def unity_assets_path_mac(self) -> str:
        return self._general.unity_assets_path_mac

    @unity_assets_path_mac.setter
    def unity_assets_path_mac(self, value: str):
        self._general.unity_assets_path_mac = value

    @property
    def unity_assets_path_linux(self) -> str:
        return self._general.unity_assets_path_linux

    @unity_assets_path_linux.setter
    def unity_assets_path_linux(self, value: str):
        self._general.unity_assets_path_linux = value

    @property
    def unity_bridge_zero_root_transform(self) -> bool:
        return self._general.unity_bridge_zero_root_transform

    @unity_bridge_zero_root_transform.setter
    def unity_bridge_zero_root_transform(self, value: bool):
        self._general.unity_bridge_zero_root_transform = value

    @property
    def unity_bridge_include_animation(self) -> bool:
        return self._general.unity_bridge_include_animation

    @unity_bridge_include_animation.setter
    def unity_bridge_include_animation(self, value: bool):
        self._general.unity_bridge_include_animation = value

    @property
    def unity_forward_axis(self) -> str:
        return self._general.unity_forward_axis

    @unity_forward_axis.setter
    def unity_forward_axis(self, value: str):
        self._general.unity_forward_axis = value

    @property
    def unity_up_axis(self) -> str:
        return self._general.unity_up_axis

    @unity_up_axis.setter
    def unity_up_axis(self, value: str):
        self._general.unity_up_axis = value


class _EnvPrefs:
    def __init__(self, env):
        self._env = env

    # ------------------- Active Environment -------------------
    @property
    def active_environment(self) -> str:
        return self._env.active_environment

    @active_environment.setter
    def active_environment(self, value: str):
        self._env.active_environment = value

    # ------------------- Source Content Paths -------------------
    @property
    def sc_path(self) -> str:
        return self._env.sc_path

    @sc_path.setter
    def sc_path(self, value: str):
        self._env.sc_path = value

    @property
    def sc_path_alternate(self) -> str:
        return self._env.sc_path_alternate

    @sc_path_alternate.setter
    def sc_path_alternate(self, value: str):
        self._env.sc_path_alternate = value

    @property
    def sc_path_mac(self) -> str:
        return self._env.sc_path_mac

    @sc_path_mac.setter
    def sc_path_mac(self, value: str):
        self._env.sc_path_mac = value

    @property
    def sc_path_mac_alternate(self) -> str:
        return self._env.sc_path_mac_alternate

    @sc_path_mac_alternate.setter
    def sc_path_mac_alternate(self, value: str):
        self._env.sc_path_mac_alternate = value

    @property
    def sc_path_linux(self) -> str:
        return self._env.sc_path_linux

    @sc_path_linux.setter
    def sc_path_linux(self, value: str):
        self._env.sc_path_linux = value

    @property
    def sc_path_linux_alternate(self) -> str:
        return self._env.sc_path_linux_alternate

    @sc_path_linux_alternate.setter
    def sc_path_linux_alternate(self, value: str):
        self._env.sc_path_linux_alternate = value

    # ------------------- Source Content Directory Structure -------------------
    @property
    def sc_dir_struct_scenes(self) -> str:
        return self._env.sc_dir_struct_scenes

    @sc_dir_struct_scenes.setter
    def sc_dir_struct_scenes(self, value: str):
        self._env.sc_dir_struct_scenes = value

    @property
    def sc_dir_struct_resources(self) -> str:
        return self._env.sc_dir_struct_resources

    @sc_dir_struct_resources.setter
    def sc_dir_struct_resources(self, value: str):
        self._env.sc_dir_struct_resources = value

    @property
    def sc_dir_struct_st(self) -> str:
        return self._env.sc_dir_struct_st

    @sc_dir_struct_st.setter
    def sc_dir_struct_st(self, value: str):
        self._env.sc_dir_struct_st = value

    @property
    def sc_dir_struct_st_hr(self) -> str:
        return self._env.sc_dir_struct_st_hr

    @sc_dir_struct_st_hr.setter
    def sc_dir_struct_st_hr(self, value: str):
        self._env.sc_dir_struct_st_hr = value

    @property
    def sc_dir_struct_st_lr(self) -> str:
        return self._env.sc_dir_struct_st_lr

    @sc_dir_struct_st_lr.setter
    def sc_dir_struct_st_lr(self, value: str):
        self._env.sc_dir_struct_st_lr = value

    @property
    def sc_dir_struct_ref(self) -> str:
        return self._env.sc_dir_struct_ref

    @sc_dir_struct_ref.setter
    def sc_dir_struct_ref(self, value: str):
        self._env.sc_dir_struct_ref = value

    @property
    def sc_dir_struct_final(self) -> str:
        return self._env.sc_dir_struct_final

    @sc_dir_struct_final.setter
    def sc_dir_struct_final(self, value: str):
        self._env.sc_dir_struct_final = value

    @property
    def sc_dir_struct_msh_bake(self) -> str:
        return self._env.sc_dir_struct_msh_bake

    @sc_dir_struct_msh_bake.setter
    def sc_dir_struct_msh_bake(self, value: str):
        self._env.sc_dir_struct_msh_bake = value

    # ------------------- Asset Hierarchy Structure -------------------
    @property
    def asset_hierarchy_struct_prefix_static_mesh(self) -> str:
        return self._env.asset_hierarchy_struct_prefix_static_mesh

    @asset_hierarchy_struct_prefix_static_mesh.setter
    def asset_hierarchy_struct_prefix_static_mesh(self, value: str):
        self._env.asset_hierarchy_struct_prefix_static_mesh = value

    @property
    def asset_hierarchy_struct_prefix_static_mesh_kit(self) -> str:
        return self._env.asset_hierarchy_struct_prefix_static_mesh_kit

    @asset_hierarchy_struct_prefix_static_mesh_kit.setter
    def asset_hierarchy_struct_prefix_static_mesh_kit(self, value: str):
        self._env.asset_hierarchy_struct_prefix_static_mesh_kit = value

    @property
    def asset_hierarchy_struct_prefix_skeletal_mesh(self) -> str:
        return self._env.asset_hierarchy_struct_prefix_skeletal_mesh

    @asset_hierarchy_struct_prefix_skeletal_mesh.setter
    def asset_hierarchy_struct_prefix_skeletal_mesh(self, value: str):
        self._env.asset_hierarchy_struct_prefix_skeletal_mesh = value

    # ------------------- Exclude If No Children -------------------
    @property
    def exclude_element_if_no_child(self) -> bool:
        return self._env.exclude_element_if_no_child

    @exclude_element_if_no_child.setter
    def exclude_element_if_no_child(self, value: bool):
        self._env.exclude_element_if_no_child = value

    # ------------------- Create Elements -------------------
    @property
    def create_element_render(self) -> bool:
        return self._env.create_element_render

    @create_element_render.setter
    def create_element_render(self, value: bool):
        self._env.create_element_render = value

    @property
    def create_element_collision(self) -> bool:
        return self._env.create_element_collision

    @create_element_collision.setter
    def create_element_collision(self, value: bool):
        self._env.create_element_collision = value

    @property
    def create_element_sockets(self) -> bool:
        return self._env.create_element_sockets

    @create_element_sockets.setter
    def create_element_sockets(self, value: bool):
        self._env.create_element_sockets = value

    # ------------------- Name Elements -------------------
    @property
    def asset_hierarchy_empty_object_meshes(self) -> str:
        return self._env.asset_hierarchy_empty_object_meshes

    @asset_hierarchy_empty_object_meshes.setter
    def asset_hierarchy_empty_object_meshes(self, value: str):
        self._env.asset_hierarchy_empty_object_meshes = value

    @property
    def asset_hierarchy_empty_object_collisions(self) -> str:
        return self._env.asset_hierarchy_empty_object_collisions

    @asset_hierarchy_empty_object_collisions.setter
    def asset_hierarchy_empty_object_collisions(self, value: str):
        self._env.asset_hierarchy_empty_object_collisions = value

    @property
    def asset_hierarchy_empty_object_sockets(self) -> str:
        return self._env.asset_hierarchy_empty_object_sockets

    @asset_hierarchy_empty_object_sockets.setter
    def asset_hierarchy_empty_object_sockets(self, value: str):
        self._env.asset_hierarchy_empty_object_sockets = value


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

    @property
    def general(self):
        return _GeneralPrefs(self.prefs.general)

    @property
    def env(self):
        return _EnvPrefs(self.prefs.environment)

    @property
    def sc(self):
        return _SCPrefs(self.prefs.sourcecontrol)

    @property
    def help_n_update(self):
        return _HelpNUpdatePrefs(self.prefs.help_n_update)


_BH_PREFS = None


def prefs() -> BHPrefs:
    global _BH_PREFS
    if _BH_PREFS is None:
        _BH_PREFS = BHPrefs()
    return _BH_PREFS
