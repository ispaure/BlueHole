"""
Enter description
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

import bpy
from bpy.props import *
from ...Lib.commonUtils.osUtils import *
from ..prefs import *

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

class BridgePG(bpy.types.PropertyGroup):

    active_container_group_tab: EnumProperty(
        name="Container Group",
        description="Choose which container group settings to display",
        items=[
            ('ASSET', "Asset Containers", "Asset container identification and structure rules"),
            ('LOOSE', "Loose Mesh", "Loose Mesh batch export (no container required)"),
        ],
        default='ASSET',
    )

    axis_exp_lst = [('X', 'X', ''), ('Y', 'Y', ''), ('Z', 'Z', ''),
                    ('-X', '-X', ''), ('-Y', '-Y', ''), ('-Z', '-Z', '')]

    # Set Game Engine
    engine_lst = [('unreal', 'Unreal', ''),
                  ('unity', 'Unity', ''),
                  ('godot', 'Godot', ''),
                  ('disabled', 'Disabled', '')]
    active_game_engine: EnumProperty(name="Solution",
                                     description="Defines the game engine used for send/export",
                                     items=engine_lst,
                                     default='unreal')

    # SOURCE CONTENT PATHS ---------------------------------------------------------------------------------------------
    sc_path: StringProperty(name='Source Content Root Path',
                            subtype='DIR_PATH',
                            description='Root Directory in which all Source Content Asset Directory Structures '
                                        'reside. \nNeeds to be set for Send to Unreal, Unity or Godot',
                            default='<Define Path Here>')

    sc_path_alternate: StringProperty(name='Source Content Root Path (Alternate)',
                                      subtype='DIR_PATH',
                                      description='Root Directory (Alternate) in which all Source Content Asset Directory Structures '
                                                  'reside. Optional path used as fallback. In case of doubt, ignore.',
                                      default='<Define Alternate Path Here (Optional)>')

    sc_path_mac: StringProperty(name='Source Content Root Path',
                                subtype='DIR_PATH',
                                description='Root Directory in which all Source Content Asset Directory Structures '
                                            'reside. \nNeeds to be set for Send to Unreal, Unity or Godot',
                                default='<Define Path Here>')

    sc_path_mac_alternate: StringProperty(name='Source Content Root Path (Alternate)',
                                          subtype='DIR_PATH',
                                          description='Root Directory (Alternate) in which all Source Content Asset Directory Structures '
                                                      'reside. Optional path used as fallback. In case of doubt, ignore.',
                                          default='<Define Alternate Path Here (Optional)>')

    sc_path_linux: StringProperty(name='Source Content Root Path',
                                  subtype='DIR_PATH',
                                  description='Root Directory in which all Source Content Asset Directory Structures '
                                              'reside. \nNeeds to be set for Send to Unreal, Unity or Godot',
                                  default='<Define Path Here>')

    sc_path_linux_alternate: StringProperty(name='Source Content Root Path (Alternate)',
                                            subtype='DIR_PATH',
                                            description='Root Directory (Alternate) in which all Source Content Asset Directory Structures '
                                                        'reside. Optional path used as fallback. In case of doubt, ignore.',
                                            default='<Define Alternate Path Here (Optional)>')

    # EXPORTS: BATCH SELECTION -----------------------------------------------------------------------------------------

    # Hierarchy Root to 0,0,0
    exp_select_zero_root_transform: BoolProperty(
        name='When enabled, sets the selected objects root transforms to 0 upon export.',
        default=True)

    # EXPORTS: ASSET HIERARCHIES (UNREAL) ------------------------------------------------------------------------------

    # Hierarchy Root to 0,0,0
    ue_bridge_zero_root_transform: BoolProperty(
        name='When enabled, sets the hierarchy root transforms to 0 upon export.',
        default=True)

    # Include animation
    ue_bridge_include_animation: BoolProperty(name='When enabled, includes animation in export.',
                                              default=False)

    # Use Automated Export
    ue_automated: BoolProperty(name='Enable Automated Import in Unreal (bypassing the FBX Import Options Window)',
                               default=True)

    # Import Materials
    ue_import_materials: BoolProperty(name='Enable import of materials in Unreal.', default=False)

    # Import Textures
    ue_import_textures: BoolProperty(name='Enable import of textures in Unreal.', default=False)

    # Override Send operator
    ue_enable_send_override: BoolProperty(
        name="Override Send to Unreal",
        description="Use a custom operator instead of Blue Hole's default Unreal send",
        default=False
    )

    ue_op_send_override: StringProperty(
        name="Send to Unreal Override Operator",
        description=(
            "Operator IDName to run instead of Blue Hole's default Unreal send "
            "(example: wm.my_send_unreal). "
            "This operator will be executed once for every Asset Container being sent. "
            "It will receive a StringProperty named 'path' containing the full file path "
            "to the exported FBX file for that container. "
            "The override operator is responsible for communicating with Unreal and "
            "triggering the asset import using this exported file."
        ),
        default=""
    )

    # EXPORTS: ASSET HIERARCHIES (UNITY) -------------------------------------------------------------------------------

    # Unity Assets Path
    unity_assets_path: StringProperty(name='Unity Project\'s Assets Path',
                                      subtype='DIR_PATH',
                                      description='The Unity Project\'s Assets folder. Needs to be '
                                                  'set for send to Unity',
                                      default='DEFAULT_STR')

    unity_assets_path_mac: StringProperty(name='Unity Project\'s Assets Path',
                                          subtype='DIR_PATH',
                                          description='The Unity Project\'s Assets folder. Needs to be '
                                                      'set for send to Unity',
                                          default='DEFAULT_STR')

    unity_assets_path_linux: StringProperty(name='Unity Project\'s Assets Path',
                                            subtype='DIR_PATH',
                                            description='The Unity Project\'s Assets folder. Needs to be '
                                                        'set for send to Unity',
                                            default='DEFAULT_STR')

    # Hierarchy Root to 0,0,0
    unity_bridge_zero_root_transform: BoolProperty(
        name='When enabled, sets the hierarchy root transforms to 0 upon export.',
        default=True)

    # Include animation
    unity_bridge_include_animation: BoolProperty(name='When enabled, includes animation in export.',
                                                 default=False)

    # Forward Axis
    unity_forward_axis: EnumProperty(name="Forward Axis",
                                     description="Defines the forward axis upon FBX Export (Unity).",
                                     items=axis_exp_lst,
                                     default='-Z'
                                     )

    # Up Axis
    unity_up_axis: EnumProperty(name="Up Axis",
                                description="Defines the up axis upon FBX Export (Unity).",
                                items=axis_exp_lst,
                                default='Y'
                                )

    # EXPORTS: ASSET HIERARCHIES (GODOT) -------------------------------------------------------------------------------

    # Godot Root Path
    godot_project_root_path: StringProperty(name='Godot Project\'s Root Path',
                                            subtype='DIR_PATH',
                                            description='The Godot Project\'s Root Path. Needs to be set for send to Godot',
                                            default='DEFAULT_STR')

    godot_project_root_path_mac: StringProperty(name='Godot Project\'s Root Path',
                                                subtype='DIR_PATH',
                                                description='The Godot Project\'s Root Path. Needs to be set for send to Godot',
                                                default='DEFAULT_STR')

    godot_project_root_path_linux: StringProperty(name='Godot Project\'s Root Path',
                                                  subtype='DIR_PATH',
                                                  description='The Godot Project\'s Root Path. Needs to be set for send to Godot',
                                                  default='DEFAULT_STR')

    # Set Export Format
    godot_export_format: EnumProperty(name="Export Format",
                                      description="Defines the export format used for send/export",
                                      items=[('fbx', 'FBX', ''), ('gltf', 'GLTF', '')],
                                      default='gltf')

    # Hierarchy Root to 0,0,0
    godot_bridge_zero_root_transform: BoolProperty(
        name='When enabled, sets the hierarchy root transforms to 0 upon export.',
        default=True)

    # Include animation
    godot_bridge_include_animation: BoolProperty(name='When enabled, includes animation in export.',
                                                 default=False)

    # Forward Axis
    godot_forward_axis: EnumProperty(name="Forward Axis",
                                     description="Defines the forward axis upon GLTF Export (Godot).",
                                     items=axis_exp_lst,
                                     default='-Z'
                                     )

    # Up Axis
    godot_up_axis: EnumProperty(name="Up Axis",
                                description="Defines the up axis upon GLTF Export (Godot).",
                                items=axis_exp_lst,
                                default='Y'
                                )

    # ------------------------------------------------------------------------------------------------------------------


def label_row(path, prop, row, label=''):
    row.label(text=label)
    row.prop(path, prop, text='')


def draw(preference, context, layout):

    # Lay out environment settings
    enable_rows = prefs().general.active_environment != 'default'

    # -------------------------------------------------------------------------------------------------
    # CONTAINER GROUP TABS (Asset Containers / Loose Mesh)
    # Note: This file keeps settings shared across all Asset Container types (Hierarchy/Mesh/Collection).
    # -------------------------------------------------------------------------------------------------
    row = layout.row()
    row.enabled = enable_rows
    row.prop(preference.bridge, 'active_container_group_tab', expand=True)

    active_group = preference.bridge.active_container_group_tab

    # -------------------------------------------------------------------------------------------------
    # ASSET CONTAINERS (Engine Bridge Settings)
    # -------------------------------------------------------------------------------------------------
    if active_group == 'ASSET':

        # ---------------------------------------------------------------------------------------------
        # ENGINE (Asset Containers)
        # ---------------------------------------------------------------------------------------------
        row = layout.row()
        row.enabled = enable_rows
        row.prop(preference.bridge, 'active_game_engine', text='Selected Game Engine')

        match prefs().bridge.active_game_engine:

            # -----------------------------------------------------------------------------------------
            # UNREAL
            # -----------------------------------------------------------------------------------------
            case 'unreal':
                box = layout.box()
                column = box.column()

                # Source Content paths (per-OS)
                match get_os():
                    case OS.WIN:
                        row = column.row(); row.enabled = enable_rows
                        row.prop(preference.bridge, 'sc_path', text='Source Content')
                        row = column.row(); row.enabled = enable_rows
                        row.prop(preference.bridge, 'sc_path_alternate', text='Source Content (Alternate)')

                    case OS.MAC:
                        row = column.row(); row.enabled = enable_rows
                        row.prop(preference.bridge, 'sc_path_mac', text='Source Content')
                        row = column.row(); row.enabled = enable_rows
                        row.prop(preference.bridge, 'sc_path_mac_alternate', text='Source Content (Alternate)')

                    case OS.LINUX:
                        row = column.row(); row.enabled = enable_rows
                        row.prop(preference.bridge, 'sc_path_linux', text='Source Content')
                        row = column.row(); row.enabled = enable_rows
                        row.prop(preference.bridge, 'sc_path_linux_alternate', text='Source Content (Alternate)')

                # Export behavior
                row = column.row()
                row.enabled = enable_rows
                row.prop(preference.bridge, 'ue_bridge_zero_root_transform', text='Zero Root Transform on Export')
                row.prop(preference.bridge, 'ue_bridge_include_animation', text='Include Animation')

                # Import behavior
                row = column.row()
                row.enabled = enable_rows
                row.prop(preference.bridge, 'ue_automated', text='Automated Import')
                row.prop(preference.bridge, 'ue_import_textures', text='Import Textures')
                row.prop(preference.bridge, 'ue_import_materials', text='Import Materials')

                # -----------------------------------------------------------------------------------------
                # OVERRIDE SEND OPERATOR
                # -----------------------------------------------------------------------------------------
                box_2 = box.box()
                column = box_2.column()

                row = column.row()
                row.enabled = enable_rows
                row.label(text='OVERRIDE SEND OPERATOR')

                row = column.row()
                row.enabled = enable_rows
                row.prop(preference.bridge, 'ue_enable_send_override', text='Override Send to Unreal')

                if prefs().bridge.ue_enable_send_override:
                    row.prop(preference.bridge, 'ue_op_send_override', text='Operator IDName')

            # -----------------------------------------------------------------------------------------
            # UNITY
            # -----------------------------------------------------------------------------------------
            case 'unity':
                box = layout.box()
                column = box.column()

                # Source Content paths (per-OS)
                match get_os():
                    case OS.WIN:
                        row = column.row(); row.enabled = enable_rows
                        row.prop(preference.bridge, 'sc_path', text='Source Content')
                        row = column.row(); row.enabled = enable_rows
                        row.prop(preference.bridge, 'sc_path_alternate', text='Source Content (Alternate)')

                    case OS.MAC:
                        row = column.row(); row.enabled = enable_rows
                        row.prop(preference.bridge, 'sc_path_mac', text='Source Content')
                        row = column.row(); row.enabled = enable_rows
                        row.prop(preference.bridge, 'sc_path_mac_alternate', text='Source Content (Alternate)')

                    case OS.LINUX:
                        row = column.row(); row.enabled = enable_rows
                        row.prop(preference.bridge, 'sc_path_linux', text='Source Content')
                        row = column.row(); row.enabled = enable_rows
                        row.prop(preference.bridge, 'sc_path_linux_alternate', text='Source Content (Alternate)')

                # Unity Assets path (per-OS)
                row = column.row()
                row.enabled = enable_rows
                match get_os():
                    case OS.WIN:
                        row.prop(preference.bridge, 'unity_assets_path', text='Unity Assets')
                    case OS.MAC:
                        row.prop(preference.bridge, 'unity_assets_path_mac', text='Unity Assets')
                    case OS.LINUX:
                        row.prop(preference.bridge, 'unity_assets_path_linux', text='Unity Assets')

                # Export behavior
                row = column.row()
                row.enabled = enable_rows
                row.prop(preference.bridge, 'unity_bridge_zero_root_transform', text='Zero Root Transform on Export')
                row.prop(preference.bridge, 'unity_bridge_include_animation', text='Include Animation')

                # Axis conversion
                row = column.row()
                row.enabled = enable_rows
                row.prop(preference.bridge, 'unity_forward_axis', text='Forward Axis')
                row.prop(preference.bridge, 'unity_up_axis', text='Up Axis')

            # -----------------------------------------------------------------------------------------
            # GODOT
            # -----------------------------------------------------------------------------------------
            case 'godot':
                box = layout.box()
                column = box.column()

                # Source Content paths (per-OS)
                match get_os():
                    case OS.WIN:
                        row = column.row(); row.enabled = enable_rows
                        row.prop(preference.bridge, 'sc_path', text='Source Content')
                        row = column.row(); row.enabled = enable_rows
                        row.prop(preference.bridge, 'sc_path_alternate', text='Source Content (Alternate)')

                    case OS.MAC:
                        row = column.row(); row.enabled = enable_rows
                        row.prop(preference.bridge, 'sc_path_mac', text='Source Content')
                        row = column.row(); row.enabled = enable_rows
                        row.prop(preference.bridge, 'sc_path_mac_alternate', text='Source Content (Alternate)')

                    case OS.LINUX:
                        row = column.row(); row.enabled = enable_rows
                        row.prop(preference.bridge, 'sc_path_linux', text='Source Content')
                        row = column.row(); row.enabled = enable_rows
                        row.prop(preference.bridge, 'sc_path_linux_alternate', text='Source Content (Alternate)')

                # Godot Project Root Path (per-OS)
                row = column.row()
                row.enabled = enable_rows
                match get_os():
                    case OS.WIN:
                        row.prop(preference.bridge, 'godot_project_root_path', text='Godot Project Root')
                    case OS.MAC:
                        row.prop(preference.bridge, 'godot_project_root_path_mac', text='Godot Project Root')
                    case OS.LINUX:
                        row.prop(preference.bridge, 'godot_project_root_path_linux', text='Godot Project Root')

                # Format
                row = column.row()
                row.enabled = enable_rows
                row.prop(preference.bridge, 'godot_export_format', text='Godot Export Format')

                # Export Settings (Related to Format)
                match prefs().bridge.godot_export_format:
                    case 'fbx':
                        # Export behavior
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.bridge, 'godot_bridge_zero_root_transform', text='Zero Root Transform on Export')
                        row.prop(preference.bridge, 'godot_bridge_include_animation', text='Include Animation')

                        # Axis conversion
                        row = column.row()
                        row.enabled = enable_rows
                        row.prop(preference.bridge, 'godot_forward_axis', text='Forward Axis')
                        row.prop(preference.bridge, 'godot_up_axis', text='Up Axis')

                    case 'gltf':
                        row.prop(preference.bridge, 'godot_bridge_include_animation', text='Include Animation')

            case _:
                # No valid engine selected.
                pass

    # -------------------------------------------------------------------------------------------------
    # LOOSE MESH (Batch Export)
    # -------------------------------------------------------------------------------------------------
    elif active_group == 'LOOSE':

        box = layout.box()
        column = box.column()

        row = column.row()
        row.enabled = enable_rows
        row.label(text='Exports each selected mesh as its own file. No prefixes or container structure required.')

        row = column.row()
        row.enabled = enable_rows
        row.prop(preference.bridge, 'exp_select_zero_root_transform', text='Zero Root Transform on Export')


# ----------------------------------------------------------------------------------------------------------------------
# REGISTER / UNREGISTER

def register():
    bpy.utils.register_class(BridgePG)


def unregister():
    bpy.utils.unregister_class(BridgePG)
