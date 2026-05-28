"""
Mappings between Blue Hole environment preferences and .ini configuration values.
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

from .model import Setting

# ----------------------------------------------------------------------------------------------------------------------
# CODE


bridge_setting_lst = (

    # Source Content
    Setting(pref_path='bridge.sc_path', ini_section='SourceContent', ini_value='sc_root_path', var_type=str),
    Setting(pref_path='bridge.sc_path_alternate', ini_section='SourceContent', ini_value='sc_root_path_alternate', var_type=str),
    Setting(pref_path='bridge.sc_path_mac', ini_section='SourceContent', ini_value='sc_root_path_mac', var_type=str),
    Setting(pref_path='bridge.sc_path_mac_alternate', ini_section='SourceContent', ini_value='sc_root_path_mac_alternate', var_type=str),
    Setting(pref_path='bridge.sc_path_linux', ini_section='SourceContent', ini_value='sc_root_path_linux', var_type=str),
    Setting(pref_path='bridge.sc_path_linux_alternate', ini_section='SourceContent', ini_value='sc_root_path_linux_alternate', var_type=str),

    # Game Engine: Unity
    Setting(pref_path='bridge.unity_assets_path', ini_section='SendAssetHierarchiesToUnity', ini_value='unity_assets_path', var_type=str),
    Setting(pref_path='bridge.unity_assets_path_mac', ini_section='SendAssetHierarchiesToUnity', ini_value='unity_assets_path_mac', var_type=str),
    Setting(pref_path='bridge.unity_assets_path_linux', ini_section='SendAssetHierarchiesToUnity', ini_value='unity_assets_path_linux', var_type=str),
    Setting(pref_path='bridge.unity_forward_axis', ini_section='SendAssetHierarchiesToUnity', ini_value='forward_axis', var_type=str),
    Setting(pref_path='bridge.unity_up_axis', ini_section='SendAssetHierarchiesToUnity', ini_value='up_axis', var_type=str),
    Setting(pref_path='bridge.unity_bridge_zero_root_transform', ini_section='SendAssetHierarchiesToUnity', ini_value='zero_root_transform', var_type=bool),
    Setting(pref_path='bridge.unity_bridge_include_animation', ini_section='SendAssetHierarchiesToUnity', ini_value='include_animation', var_type=bool),

    # Game Engine: Godot
    Setting(pref_path='bridge.godot_project_root_path', ini_section='SendAssetHierarchiesToGodot', ini_value='godot_project_root_path', var_type=str),
    Setting(pref_path='bridge.godot_project_root_path_mac', ini_section='SendAssetHierarchiesToGodot', ini_value='godot_project_root_path_mac', var_type=str),
    Setting(pref_path='bridge.godot_project_root_path_linux', ini_section='SendAssetHierarchiesToGodot', ini_value='godot_project_root_path_linux', var_type=str),
    Setting(pref_path='bridge.godot_export_format', ini_section='SendAssetHierarchiesToGodot', ini_value='export_format', var_type=str),
    Setting(pref_path='bridge.godot_forward_axis', ini_section='SendAssetHierarchiesToGodot', ini_value='forward_axis', var_type=str),
    Setting(pref_path='bridge.godot_up_axis', ini_section='SendAssetHierarchiesToGodot', ini_value='up_axis', var_type=str),
    Setting(pref_path='bridge.godot_bridge_zero_root_transform', ini_section='SendAssetHierarchiesToGodot', ini_value='zero_root_transform', var_type=bool),
    Setting(pref_path='bridge.godot_bridge_include_animation', ini_section='SendAssetHierarchiesToGodot', ini_value='include_animation', var_type=bool),

    # FBX Exports (Loose)
    Setting(pref_path='bridge.exp_select_zero_root_transform', ini_section='ExportBatchSelectionToFBX', ini_value='zero_root_transform', var_type=bool),

    # Game Engine: Unreal
    Setting(pref_path='bridge.ue_bridge_zero_root_transform', ini_section='SendAssetHierarchiesToUnreal', ini_value='zero_root_transform', var_type=bool),
    Setting(pref_path='bridge.ue_bridge_include_animation', ini_section='SendAssetHierarchiesToUnreal', ini_value='include_animation', var_type=bool),
    Setting(pref_path='bridge.ue_automated', ini_section='SendAssetHierarchiesToUnreal', ini_value='is_automated', var_type=bool),
    Setting(pref_path='bridge.ue_import_materials', ini_section='SendAssetHierarchiesToUnreal', ini_value='import_materials', var_type=bool),
    Setting(pref_path='bridge.ue_import_textures', ini_section='SendAssetHierarchiesToUnreal', ini_value='import_textures', var_type=bool),
    Setting(pref_path='bridge.ue_enable_send_override', ini_section='SendAssetHierarchiesToUnreal', ini_value='enable_send_override', var_type=bool),
    Setting(pref_path='bridge.ue_op_send_override', ini_section='SendAssetHierarchiesToUnreal', ini_value='op_send_override', var_type=str),
    Setting(pref_path='bridge.ue_remote_exec_multicast_group_endpoint_address', ini_section='SendAssetHierarchiesToUnreal', ini_value='remote_exec_multicast_group_endpoint_address', var_type=str),
    Setting(pref_path='bridge.ue_remote_exec_multicast_group_endpoint_port', ini_section='SendAssetHierarchiesToUnreal', ini_value='remote_exec_multicast_group_endpoint_port', var_type=int),
    Setting(pref_path='bridge.ue_remote_exec_multicast_bind_address', ini_section='SendAssetHierarchiesToUnreal', ini_value='remote_exec_multicast_bind_address', var_type=str),
    Setting(pref_path='bridge.ue_remote_exec_command_endpoint_address', ini_section='SendAssetHierarchiesToUnreal', ini_value='remote_exec_command_endpoint_address', var_type=str),
    Setting(pref_path='bridge.ue_remote_exec_command_endpoint_port', ini_section='SendAssetHierarchiesToUnreal', ini_value='remote_exec_command_endpoint_port', var_type=int),

    # Selected Game Engine
    Setting(pref_path='bridge.active_game_engine', ini_section='Engine', ini_value='active_game_engine', var_type=str),
)


directory_setting_lst = (
    Setting(pref_path='directory.sc_dir_struct_scenes', ini_section='AssetDirectoryStructure', ini_value='path_scenes', var_type=str),
    Setting(pref_path='directory.sc_dir_struct_resources', ini_section='AssetDirectoryStructure', ini_value='path_resources', var_type=str),
    Setting(pref_path='directory.sc_dir_struct_st', ini_section='AssetDirectoryStructure', ini_value='path_speedtree_msh', var_type=str),
    Setting(pref_path='directory.sc_dir_struct_st_hr', ini_section='AssetDirectoryStructure', ini_value='path_speedtree_msh_hr', var_type=str),
    Setting(pref_path='directory.sc_dir_struct_st_lr', ini_section='AssetDirectoryStructure', ini_value='path_speedtree_msh_lr', var_type=str),
    Setting(pref_path='directory.sc_dir_struct_ref', ini_section='AssetDirectoryStructure', ini_value='path_references', var_type=str),
    Setting(pref_path='directory.sc_dir_struct_final', ini_section='AssetDirectoryStructure', ini_value='path_final', var_type=str),
    Setting(pref_path='directory.sc_dir_struct_msh_bake', ini_section='AssetDirectoryStructure', ini_value='path_mshbake', var_type=str),
)


container_setting_lst = (
    # -------------------------------------------------------------------------------------------------
    # AssetHierarchyStructure
    # -------------------------------------------------------------------------------------------------
    Setting(pref_path='container.enable_asset_hierarchy_container', ini_section='AssetHierarchyStructure', ini_value='enable_asset_hierarchy_container', var_type=bool),

    Setting(pref_path='container.asset_hierarchy_struct_prefix_static_mesh', ini_section='AssetHierarchyStructure', ini_value='prefix_static_mesh', var_type=str),
    Setting(pref_path='container.asset_hierarchy_struct_prefix_static_mesh_kit', ini_section='AssetHierarchyStructure', ini_value='prefix_static_mesh_kit', var_type=str),
    Setting(pref_path='container.asset_hierarchy_struct_prefix_skeletal_mesh', ini_section='AssetHierarchyStructure', ini_value='prefix_skeletal_mesh', var_type=str),

    Setting(pref_path='container.asset_hierarchy_empty_object_meshes', ini_section='AssetHierarchyStructure', ini_value='null_render', var_type=str),
    Setting(pref_path='container.asset_hierarchy_empty_object_collisions', ini_section='AssetHierarchyStructure', ini_value='null_collision', var_type=str),
    Setting(pref_path='container.asset_hierarchy_empty_object_sockets', ini_section='AssetHierarchyStructure', ini_value='null_socket', var_type=str),

    Setting(pref_path='container.create_element_render', ini_section='AssetHierarchyStructure', ini_value='create_null_render', var_type=bool),
    Setting(pref_path='container.create_element_collision', ini_section='AssetHierarchyStructure', ini_value='create_null_collision', var_type=bool),
    Setting(pref_path='container.create_element_sockets', ini_section='AssetHierarchyStructure', ini_value='create_null_socket', var_type=bool),

    Setting(pref_path='container.exclude_element_if_no_child', ini_section='AssetHierarchyStructure', ini_value='exclude_null_if_no_child', var_type=bool),

    # -------------------------------------------------------------------------------------------------
    # AssetMeshStructure
    # -------------------------------------------------------------------------------------------------
    Setting(pref_path='container.enable_asset_mesh_container', ini_section='AssetMeshStructure', ini_value='enable_asset_mesh_container', var_type=bool),

    # -------------------------------------------------------------------------------------------------
    # AssetCollectionStructure
    # -------------------------------------------------------------------------------------------------
    Setting(pref_path='container.enable_asset_collection_container', ini_section='AssetCollectionStructure', ini_value='enable_asset_collection_container', var_type=bool),
)


source_control_setting_lst = (
    Setting(pref_path='sourcecontrol.win32_env_setting_p4port', ini_section='Perforce', ini_value='win32_env_setting_p4port', var_type=str),
    Setting(pref_path='sourcecontrol.win32_env_setting_p4user', ini_section='Perforce', ini_value='win32_env_setting_p4user', var_type=str),
    Setting(pref_path='sourcecontrol.win32_env_setting_p4client', ini_section='Perforce', ini_value='win32_env_setting_p4client', var_type=str),

    Setting(pref_path='sourcecontrol.macos_env_setting_p4port', ini_section='Perforce', ini_value='macos_env_setting_p4port', var_type=str),
    Setting(pref_path='sourcecontrol.macos_env_setting_p4user', ini_section='Perforce', ini_value='macos_env_setting_p4user', var_type=str),
    Setting(pref_path='sourcecontrol.macos_env_setting_p4client', ini_section='Perforce', ini_value='macos_env_setting_p4client', var_type=str),

    Setting(pref_path='sourcecontrol.linux_env_setting_p4port', ini_section='Perforce', ini_value='linux_env_setting_p4port', var_type=str),
    Setting(pref_path='sourcecontrol.linux_env_setting_p4user', ini_section='Perforce', ini_value='linux_env_setting_p4user', var_type=str),
    Setting(pref_path='sourcecontrol.linux_env_setting_p4client', ini_section='Perforce', ini_value='linux_env_setting_p4client', var_type=str),

    Setting(pref_path='sourcecontrol.source_control_solution', ini_section='SourceControl', ini_value='solution', var_type=str),
    Setting(pref_path='sourcecontrol.source_control_enable', ini_section='SourceControl', ini_value='enable', var_type=bool),
    Setting(pref_path='sourcecontrol.source_control_error_aborts_exp', ini_section='SourceControl', ini_value='abort_export_on_error', var_type=bool),

    Setting(pref_path='sourcecontrol.win32_env_override', ini_section='Perforce', ini_value='override_env_setting', var_type=bool),
    Setting(pref_path='sourcecontrol.p4v_app_path_mac', ini_section='Perforce', ini_value='p4v_app_path_mac', var_type=str),
    Setting(pref_path='sourcecontrol.p4_parallel_path_linux', ini_section='Perforce', ini_value='p4_parallel_path_linux', var_type=str),
)
