"""
March 2026 refactor: Asset Hierarchy Container
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2026, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS

# Blue Hole
import bpy
from ..exportSettings import *
from ....Lib.commonUtils.debugUtils import *
from ... import objectUtils
from ....preferences.prefs import *
from .modelContainer import Container

# ----------------------------------------------------------------------------------------------------------------------
# DEBUG

show_verbose = True

# ----------------------------------------------------------------------------------------------------------------------
# CODE


class AssetHierarchyContainer(Container):

    CONTAINER_NAME = 'Asset Hierarchy'

    def __init__(self, root, export_settings: ExportSettings):
        super().__init__(root, export_settings)

        # Asset Hierarchy Specific Fields
        self.render_name = prefs().env.asset_hierarchy_empty_object_meshes
        self.render = self.__get_empty_render()
        self.collision_name = prefs().env.asset_hierarchy_empty_object_collisions
        self.collision = self.__get_empty_collision()
        self.socket_name = prefs().env.asset_hierarchy_empty_object_sockets
        self.socket = self.__get_empty_socket()

        # Validate Hierarchy
        self.__validate_container()

    def __get_empty_render(self):
        """ If "Render Included", Get the "Render" Empty Object at the root of the container """
        if not self.export_settings.include_render:
            return None

        return self.__get_root_empty_object(self.render_name, empty_type='Render')

    def __get_empty_collision(self):
        """ If "Collision Included", Get the "Collision" Empty Object at the root of the container """
        if not self.export_settings.include_collision:
            return None

        return self.__get_root_empty_object(self.collision_name, empty_type='Collision')

    def __get_empty_socket(self):
        """ If "Socket Included", Get the "Socket" Empty Object at the root of the container """
        if not self.export_settings.include_socket:
            return None

        return self.__get_root_empty_object(self.socket_name, empty_type='Socket')

    def __get_root_empty_object(self, empty_name: str, empty_type: str):
        """
        Get an Empty Object at the root of the container.
        Raises:
            - critical_component_missing if no match found
            - critical_component_duplicated if more than one match found
        Note: Matching ignores Blender numeric suffixes (e.g. "Render.001").

        :param empty_name: Base name of the Empty to search for (numeric suffixes like ".001" are ignored).
        :param empty_type: Human-readable component type used in error messages ("Render", "Collision" or "Socket")
        """
        children = objectUtils.get_obj_child(self.root)

        matches = [
            obj for obj in children
            if objectUtils.get_obj_name(obj).split('.')[0] == empty_name
        ]

        if not matches:
            self.__critical_component_missing(empty_name, empty_type)

        if len(matches) > 1:
            self.__critical_component_duplicated(empty_name, empty_type)

        return matches[0]

    def __validate_container(self) -> None:
        """
        Validate container structure for export.

        If render export is enabled, the container root must contain only
        Empty objects (no meshes or other object types directly under root).
        """
        if not self.export_settings.include_render:
            return

        offenders = [obj for obj in objectUtils.get_obj_child(self.root)
                     if objectUtils.get_obj_type(obj) != 'EMPTY']

        if offenders:
            offender_names = [objectUtils.get_obj_name(obj) for obj in offenders]
            self.__critical_rogue_object_directly_under_root(', '.join(offender_names))

    def _rename_before_export(self):

        # Empty Objects
        # Force set naming (do 3 times — it works) for Render, Collision and Socket Empty Object
        self.__force_name(self.render, self.render_name)
        self.__force_name(self.collision, self.collision_name)
        self.__force_name(self.socket, self.socket_name)

        # Collisions (If Collision Folder & Preset Enables Rename Collisions)
        if self.collision is not None and self.export_settings.rename_collisions_for_ue:
            coll_obj_lst = objectUtils.get_obj_child_recursive(self.collision)
            first_mesh_name = self.__get_first_mesh_name()
            counter = 1
            for coll_obj in coll_obj_lst:
                coll_obj.name = f'UCX_{first_mesh_name}_{format(counter, "03")}'
                counter += 1

    def __force_name(self, obj: bpy.types.Object | None, target_name: str) -> None:
        if obj is None:
            return

        existing = bpy.data.objects.get(target_name)

        # If nobody owns the name, just take it
        if existing is None:
            obj.name = target_name
            return

        # If we already own it, nothing to do
        if existing == obj:
            return

        # Free the slot
        tmp_name = f"{target_name}.__tmp__"
        existing.name = tmp_name

        # Claim the clean name
        obj.name = target_name

        # Force Blender to suffix the previous owner
        existing.name = target_name

    def _get_obj_lst(self):

        # Wipe existing object list
        obj_lst = []
        # Create exclusion list
        excl_lst = []

        # Add root
        obj_lst.append(self.root)

        # Append other stuff
        for component in [self.render, self.collision, self.socket]:
            if component is not None:
                child_obj_lst = objectUtils.get_obj_child_recursive(component)
                if len(child_obj_lst) > 0 or not prefs().env.exclude_element_if_no_child:
                    obj_lst.append(component)
                    for child_obj in child_obj_lst:
                        obj_lst.append(child_obj)
                else:
                    excl_lst.append(component)

        # If render wasn't included, add stuff at the root (but not the excluded components if applicable)
        if not self.export_settings.include_render:
            obj_full_lst = objectUtils.get_obj_child_recursive(self.root)
            for obj in obj_full_lst:
                if obj not in obj_lst and obj not in excl_lst:
                    obj_lst.append(obj)

        return obj_lst

    def __get_first_mesh_name(self) -> str:
        """ Get first mesh name, else sets to 'Template' as fallback. """
        if self.export_settings.include_render:
            render_obj_child_lst = objectUtils.get_obj_child_recursive(self.render)
            for render_obj in render_obj_child_lst:
                if objectUtils.get_obj_type(render_obj) == 'MESH':
                    return objectUtils.get_obj_name(render_obj)
        else:
            root_obj_lst = objectUtils.get_obj_child(self.root)
            for root_obj in root_obj_lst:
                if objectUtils.get_obj_type(root_obj) == 'MESH':
                    return objectUtils.get_obj_name(root_obj)
        return 'Template'

    # ----------------------------------------------------------------------------------------------------------------------
    # CRITICAL ERROR MESSAGES

    # --------------------------------
    # CRITICAL: HIERARCHY IS NOT VALID
    # --------------------------------

    def __critical_rogue_object_directly_under_root(self, child):
        child_name = objectUtils.get_obj_name(child)
        msg = (
            f'Asset Hierarchy validation failed.\n\n'
            f'What went wrong:\n'
            f'"{child_name}" is directly under "{self.name}" but is not an Empty object. '
            f'Only Empty objects are allowed directly under the Asset Hierarchy root. '
            f'For example, renderable geometry must be placed under the '
            f'"{prefs().env.asset_hierarchy_empty_object_meshes}" Empty Object.\n\n'
            f'What to do:\n'
            f'Parent "{child_name}" under the appropriate Empty Object within the Asset Hierarchy.\n\n'
            f'Note: This restriction applies when the "Empty Object Render" option is enabled in the '
            f'Environment Settings (Structure tab).\n\n'
            f'Export aborted.'
        )
        log(Severity.CRITICAL, self._get_log_name(), msg, popup=True)

    def __critical_component_missing(self, empty_name: str, empty_type: str):
        msg = (
            f'Asset Hierarchy validation failed.\n\n'
            f'What went wrong:\n'
            f'The required Empty Object "{empty_name}" ({empty_type}) is missing under "{self.name}". '
            f'This Empty Object is required by the Active Environment settings. '
            f'The name may include trailing numbers (for example: "{empty_name}.013").\n\n'
            f'What to do:\n'
            f'Create an Empty object named "{empty_name}" under "{self.name}", or recreate the Asset Hierarchy '
            f'using the Blue Hole Asset Hierarchy creation tool.\n\n'
            f'Note: Empty Object requirements can be adjusted in the Environment Settings (Structure tab).\n\n'
            f'Export aborted.'
        )
        log(Severity.CRITICAL, self._get_log_name(), msg, popup=True)

    def __critical_component_duplicated(self, empty_name: str, empty_type: str):
        msg = (
            f'Asset Hierarchy validation failed.\n\n'
            f'What went wrong:\n'
            f'Multiple Empty Objects named "{empty_name}" ({empty_type}) were found under "{self.name}". '
            f'Only one Empty Object of this type is allowed. This can occur when Blender creates duplicate names '
            f'with numeric suffixes (for example: "{empty_name}.001", "{empty_name}.002").\n\n'
            f'What to do:\n'
            f'Ensure only one Empty Object of type "{empty_type}" exists under "{self.name}". '
            f'Remove or rename any duplicates so that only a single valid Empty Object remains.\n\n'
            f'Export aborted.'
        )

        log(Severity.CRITICAL, self._get_log_name(), msg, popup=True)
