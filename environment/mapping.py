"""
This specifies the mappings for Environment Preferences: It specifies how data in the .INI configuration files ties to
the Blue Hole blender preferences.
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'


# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS

# Blue Hole
from BlueHole.environment.model import Setting

# ----------------------------------------------------------------------------------------------------------------------
# CODE


general_setting_lst = (
    # ------------------- General -------------------
    Setting(pref_path='general.unity_assets_path', ini_section='SendAssetHierarchiesToUnity', ini_value='unity_assets_path', var_type=str),
    Setting(pref_path='general.unity_assets_path_mac', ini_section='SendAssetHierarchiesToUnity', ini_value='unity_assets_path_mac', var_type=str),
    Setting(pref_path='general.unity_forward_axis', ini_section='SendAssetHierarchiesToUnity', ini_value='forward_axis', var_type=str),
    Setting(pref_path='general.unity_up_axis', ini_section='SendAssetHierarchiesToUnity', ini_value='up_axis', var_type=str),
    Setting(pref_path='general.exp_select_zero_root_transform', ini_section='ExportBatchSelectionToFBX', ini_value='zero_root_transform', var_type=bool),
    Setting(pref_path='general.ue_bridge_zero_root_transform', ini_section='SendAssetHierarchiesToUnreal', ini_value='zero_root_transform', var_type=bool),
    Setting(pref_path='general.ue_bridge_include_animation', ini_section='SendAssetHierarchiesToUnreal', ini_value='include_animation', var_type=bool),
    Setting(pref_path='general.unity_bridge_zero_root_transform', ini_section='SendAssetHierarchiesToUnity', ini_value='zero_root_transform', var_type=bool),
    Setting(pref_path='general.unity_bridge_include_animation', ini_section='SendAssetHierarchiesToUnity', ini_value='include_animation', var_type=bool),
    Setting(pref_path='general.ue_automated', ini_section='SendAssetHierarchiesToUnreal', ini_value='is_automated', var_type=bool),
    Setting(pref_path='general.ue_import_materials', ini_section='SendAssetHierarchiesToUnreal', ini_value='import_materials', var_type=bool),
    Setting(pref_path='general.ue_import_textures', ini_section='SendAssetHierarchiesToUnreal', ini_value='import_textures', var_type=bool),
)

environment_setting_lst = (
    # ------------------- Environment -------------------
    Setting(pref_path='environment.sc_path', ini_section='SourceContent', ini_value='sc_root_path', var_type=str),
    Setting(pref_path='environment.sc_path_alternate', ini_section='SourceContent', ini_value='sc_root_path_alternate', var_type=str),
    Setting(pref_path='environment.sc_path_mac', ini_section='SourceContent', ini_value='sc_root_path_mac', var_type=str),
    Setting(pref_path='environment.sc_path_mac_alternate', ini_section='SourceContent', ini_value='sc_root_path_mac_alternate', var_type=str),
    Setting(pref_path='environment.sc_dir_struct_scenes', ini_section='AssetDirectoryStructure', ini_value='path_scenes', var_type=str),
    Setting(pref_path='environment.sc_dir_struct_resources', ini_section='AssetDirectoryStructure', ini_value='path_resources', var_type=str),
    Setting(pref_path='environment.sc_dir_struct_st', ini_section='AssetDirectoryStructure', ini_value='path_speedtree_msh', var_type=str),
    Setting(pref_path='environment.sc_dir_struct_st_hr', ini_section='AssetDirectoryStructure', ini_value='path_speedtree_msh_hr', var_type=str),
    Setting(pref_path='environment.sc_dir_struct_st_lr', ini_section='AssetDirectoryStructure', ini_value='path_speedtree_msh_lr', var_type=str),
    Setting(pref_path='environment.sc_dir_struct_ref', ini_section='AssetDirectoryStructure', ini_value='path_references', var_type=str),
    Setting(pref_path='environment.sc_dir_struct_final', ini_section='AssetDirectoryStructure', ini_value='path_final', var_type=str),
    Setting(pref_path='environment.sc_dir_struct_msh_bake', ini_section='AssetDirectoryStructure', ini_value='path_mshbake', var_type=str),
    Setting(pref_path='environment.asset_hierarchy_struct_prefix_static_mesh', ini_section='AssetHierarchyStructure', ini_value='prefix_static_mesh', var_type=str),
    Setting(pref_path='environment.asset_hierarchy_struct_prefix_static_mesh_kit', ini_section='AssetHierarchyStructure', ini_value='prefix_static_mesh_kit', var_type=str),
    Setting(pref_path='environment.asset_hierarchy_struct_prefix_skeletal_mesh', ini_section='AssetHierarchyStructure', ini_value='prefix_skeletal_mesh', var_type=str),
    Setting(pref_path='environment.asset_hierarchy_empty_object_meshes', ini_section='AssetHierarchyStructure', ini_value='null_render', var_type=str),
    Setting(pref_path='environment.asset_hierarchy_empty_object_collisions', ini_section='AssetHierarchyStructure', ini_value='null_collision', var_type=str),
    Setting(pref_path='environment.asset_hierarchy_empty_object_sockets', ini_section='AssetHierarchyStructure', ini_value='null_socket', var_type=str),
    Setting(pref_path='environment.create_element_render', ini_section='AssetHierarchyStructure', ini_value='create_null_render', var_type=bool),
    Setting(pref_path='environment.create_element_collision', ini_section='AssetHierarchyStructure', ini_value='create_null_collision', var_type=bool),
    Setting(pref_path='environment.create_element_sockets', ini_section='AssetHierarchyStructure', ini_value='create_null_socket', var_type=bool),
    Setting(pref_path='environment.exclude_element_if_no_child', ini_section='AssetHierarchyStructure', ini_value='exclude_null_if_no_child', var_type=bool),
)

source_control_setting_lst = (
    # ------------------- SourceControl -------------------
    Setting(pref_path='sourcecontrol.win32_env_setting_p4port', ini_section='Perforce', ini_value='win32_env_setting_p4port', var_type=str),
    Setting(pref_path='sourcecontrol.win32_env_setting_p4user', ini_section='Perforce', ini_value='win32_env_setting_p4user', var_type=str),
    Setting(pref_path='sourcecontrol.win32_env_setting_p4client', ini_section='Perforce', ini_value='win32_env_setting_p4client', var_type=str),
    Setting(pref_path='sourcecontrol.macos_env_setting_p4port', ini_section='Perforce', ini_value='macos_env_setting_p4port', var_type=str),
    Setting(pref_path='sourcecontrol.macos_env_setting_p4user', ini_section='Perforce', ini_value='macos_env_setting_p4user', var_type=str),
    Setting(pref_path='sourcecontrol.macos_env_setting_p4client', ini_section='Perforce', ini_value='macos_env_setting_p4client', var_type=str),
    Setting(pref_path='sourcecontrol.source_control_solution', ini_section='SourceControl', ini_value='solution', var_type=str),
    Setting(pref_path='sourcecontrol.source_control_enable', ini_section='SourceControl', ini_value='enable', var_type=bool),
    Setting(pref_path='sourcecontrol.source_control_error_aborts_exp', ini_section='SourceControl', ini_value='abort_export_on_error', var_type=bool),
    Setting(pref_path='sourcecontrol.win32_env_override', ini_section='Perforce', ini_value='override_env_setting', var_type=bool),
)
