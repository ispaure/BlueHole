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

# System
import enum
from typing import *
from pathlib import Path

# Blender
import bpy

# Blue Hole
from ..blenderUtils import filterUtils
from ..commonUtils.debugUtils import *
from ..preferences.prefs import *
from ..commonUtils.wrappers import cmdShellWrapper
from ..commonUtils import uiUtils, fileUtils
from ..commonUtils.osUtils import *

# ----------------------------------------------------------------------------------------------------------------------
# USER DEFINED VARIABLES
tool_name = 'Blue Hole [Perforce Wrapper]'
show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE


class P4Info:
    """
    Stores the info from the p4 info command in strings.
    """

    def __init__(self):
        # Define dictionary keys
        self.status = None
        self.user_name = ''
        self.client_name = ''
        self.client_host = ''
        self.client_root = ''
        self.client_stream = ''
        self.client_cwd = ''
        self.peer_address = ''
        self.client_address = ''
        self.server_address = ''
        self.server_root = ''
        self.server_date = ''
        self.server_uptime = ''
        self.server_version = ''
        self.server_id = ''
        self.server_services = ''
        self.server_license = ''
        self.server_license_ip = ''
        self.case_handling = ''

        # Set p4 env settings
        set_p4_env_settings()  # Sets P4 Environment Settings so they are set for later use. Don't know if I need this anywhere else.

        # Update keys
        self.update_fields()

    def update_fields(self):
        # Get the information from p4 info
        info_array = exec_p4_command('p4 info')

        # If could not get info, set status to False
        if "Perforce client error" in info_array[0]:
            self.status = False
            P4ErrorMessage().info_perforce_client_error()
            return

        if "is not recognized" in info_array[0]:
            self.status = False
            P4ErrorMessage().info_not_recognized()
            return

        # Create directory from the output of p4 info
        p4_info_dict = {}
        for item in info_array:

            # If client unknown, perforce connection has not been set properly. Warn user!
            if 'Client unknown.' in item:
                self.status = False
                P4ErrorMessage().info_default_connection()
                return

            if 'Permission denied' in item:
                self.status = False
                match get_os():
                    case OS.WIN:
                        P4ErrorMessage().info_win_p4_cmd_missing()
                    case OS.MAC:
                        p4_macos_path = get_p4_macos_path()
                        P4ErrorMessage().info_mac_p4_cmd_missing(p4_macos_path)
                    case OS.LINUX:
                        p4_linux_path = get_p4_linux_path()
                        P4ErrorMessage().info_linux_p4_cmd_missing(p4_linux_path)
                return

            item_split = item.split(": ")
            p4_info_dict[item_split[0]] = item_split[1]

        # Assign the dictionary keys to the values
        self.status = True
        self.user_name = p4_info_dict['User name']
        self.client_name = p4_info_dict['Client name']
        self.client_host = p4_info_dict['Client host']
        self.client_root = p4_info_dict['Client root']
        self.client_cwd = p4_info_dict['Current directory']
        self.peer_address = p4_info_dict['Peer address']
        self.client_address = p4_info_dict['Client address']
        self.server_address = p4_info_dict['Server address']
        self.server_root = p4_info_dict['Server root']
        self.server_date = p4_info_dict['Server date']
        self.server_uptime = p4_info_dict['Server uptime']

    def is_server_accessible(self, silent=False) -> bool:
        # Check if Perforce server is accessible.
        if self.status is False:
            P4ErrorMessage(silent).info_server_cannot_connect()
            return False
        else:
            P4LogMessage().info_log_server_accessible()
            return True

    def display_info_window(self):
        msg = (f'User name: {self.user_name}\n'
               f'Client name: {self.client_name}\n'
               f'Client root: {self.client_root}\n'
               f'Server address: {self.server_address}\n'
               f'Server uptime: {self.server_uptime}')
        log(Severity.INFO, tool_name, msg, popup=True)


class P4FileStatus(enum.Enum):
    MARKED_FOR_ADD = 'Marked for add'
    NOT_ADDED = 'Not Added'
    MARKED_FOR_DELETE = 'Marked for delete'
    CHECKOUT_BY_ME = 'Checked out by me'
    CHECKOUT_BY_OTHER = 'Checked out by Others'
    LATEST_REVISION = 'Latest Revision'
    NOT_LATEST_REVISION = 'Not Latest Revision'
    INVALID = 'Invalid'


# TODO: Make everything work with files with space in their path. Maybe just need to add "? See p4 cmd doc.


class P4File:
    def __init__(self, client_file: Union[str, None] = None, depot_file: Union[str, None] = None):
        # Set fields (if they were given, else is None
        self.depotFile: Union[str, None] = depot_file
        self.clientFile: Union[str, None] = client_file
        # If both are none, this is a critical error and script should be prevented from progressing further!
        if self.depotFile is None and self.clientFile is None:
            P4CriticalMessage().p4_file_client_or_depot_path_required(group=False)

        # Set fields to their defaults
        self.status: Union[P4FileStatus, None] = None
        self.file_name: Union[str, None] = None
        self.isMapped: bool = False
        self.notInClientView: bool = False
        self.headAction: Union[str, None] = None
        self.headType = None
        self.headTime = None
        self.headRev = None
        self.headChange = None
        self.headModTime = None
        self.haveRev = None
        self.otherOpen0 = None
        self.otherAction0 = None
        self.otherChange0 = None
        self.otherOpen = None
        self.action = None
        self.change = None
        self.type = None
        self.actionOwner = None
        self.workRev = None

    def update_fields(self, f_stat_dict=None) -> bool:
        # If no dict is given for the refresh, fetch info.
        if f_stat_dict is None:
            f_stat_dict = p4_fstat_dict(self.clientFile)
            if f_stat_dict is not None:
                f_stat_dict = f_stat_dict[0]  # There was no error, get the first (only) item to process.
            else:
                return False  # There was an error, return False as could not process properly.

        self.depotFile = self.key_else_default(f_stat_dict, 'depotFile')
        self.clientFile = self.key_else_default(f_stat_dict, 'clientFile')
        self.headAction = self.key_else_default(f_stat_dict, 'headAction')
        self.headType = self.key_else_default(f_stat_dict, 'headType')
        self.headTime = self.key_else_default(f_stat_dict, 'headTime')
        self.headRev = self.key_else_default(f_stat_dict, 'headRev')
        self.headChange = self.key_else_default(f_stat_dict, 'headChange')
        self.headModTime = self.key_else_default(f_stat_dict, 'headModTime')
        self.haveRev = self.key_else_default(f_stat_dict, 'haveRev')
        self.otherOpen0 = self.key_else_default(f_stat_dict, 'otherOpen0')
        self.otherAction0 = self.key_else_default(f_stat_dict, 'otherAction0')
        self.otherChange0 = self.key_else_default(f_stat_dict, 'otherChange0')
        self.otherOpen = self.key_else_default(f_stat_dict, 'otherOpen')
        self.action = self.key_else_default(f_stat_dict, 'action')
        self.change = self.key_else_default(f_stat_dict, 'change')
        self.type = self.key_else_default(f_stat_dict, 'type')
        self.actionOwner = self.key_else_default(f_stat_dict, 'actionOwner')
        self.workRev = self.key_else_default(f_stat_dict, 'workRev')

        self.file_name = self.clientFile.split('\\')[-1]

        # Give label on if it's mapped or not
        if 'isMapped' in f_stat_dict.keys():
            self.isMapped = True
        else:
            self.isMapped = False

        # Give label on if it's in client view or not
        if 'notInClientView' in f_stat_dict.keys():
            self.notInClientView = True
        else:
            self.notInClientView = False

        # Deduce the simple current status of the file
        self.status = self.get_status()

        # Completed successfully
        return True

    def get_display_name(self):
        # Prefer clientFile as a display name, else use depotFile as fallback. One of the two is guaranteed available.
        if self.clientFile is not None:
            return self.clientFile
        else:
            return self.depotFile

    def key_else_default(self, dictionary: dict, key: str, default_value=None):
        """
        Returns the value of a key from a dict. If key was not found, return default value instead (default is None).
        Prevents unavailable key from being an error.
        :param dictionary: Dictionary to look into for key
        :param key: Key to look for in dictionary
        :param default_value: Value to put if key was not found (can be any type)
        :rtype: Can be any type
        """
        if key in dictionary.keys():
            return dictionary[key]
        else:
            return default_value

    def get_status(self):
        """
        Deduce the simple current status of the file
        :rtype: P4FileStatus
        """
        if self.headAction == 'delete' and self.action == 'add':
            return P4FileStatus.MARKED_FOR_ADD
        if not self.isMapped or self.headAction == 'move/delete' or self.headAction == 'delete':
            return P4FileStatus.NOT_ADDED
        elif self.headAction == 'add' and self.action == 'delete':
            return P4FileStatus.MARKED_FOR_DELETE
        elif self.action == 'add':
            return P4FileStatus.MARKED_FOR_ADD
        elif self.action == 'edit':
            return P4FileStatus.CHECKOUT_BY_ME
        elif self.otherOpen is not None:
            return P4FileStatus.CHECKOUT_BY_OTHER
        elif self.haveRev == self.headRev:
            return P4FileStatus.LATEST_REVISION
        elif self.haveRev != self.headRev:
            return P4FileStatus.NOT_LATEST_REVISION
        else:
            return P4FileStatus.INVALID

    def print_info(self):
        """
        Print some information about the file, for debug purposes
        """
        info = (f'File Name: {self.file_name}\n'
                f'Status: {self.status}\n'
                f'Depot File: {self.depotFile}\n'
                f'Client File: {self.clientFile}\n'
                f'Is Mapped: {self.isMapped}\n'
                f'Not in Client View: {self.notInClientView}\n'
                f'Head Action: {self.headAction}\n'
                f'Head Type: {self.headType}\n'
                f'Head Time: {self.headTime}\n'
                f'Head Revision: {self.headRev}\n'
                f'Head Change: {self.headChange}\n'
                f'Head Modification Time: {self.headModTime}\n'
                f'Have Revision: {self.haveRev}\n'
                f'Other Open 0: {self.otherOpen0}\n'
                f'Other Action 0: {self.otherAction0}\n'
                f'Other Change 0: {self.otherChange0}\n'
                f'Other Open: {self.otherOpen}\n'
                f'Action: {self.action}\n'
                f'Change: {self.change}\n'
                f'Type: {self.type}\n'
                f'Action Owner: {self.actionOwner}\n'
                f'Work Revision: {self.workRev}\n')
        print(info)

    def is_client_file_under_workspace_root(self, p4_info_cls: P4Info, silent: bool = False):
        if self.clientFile is not None:
            normalized_client_root = str(Path(p4_info_cls.client_root))  # Sometime it outputs with / or not, so normalize here.

            # If on Windows, should test in lowercase (not be case-sensitive)
            match get_os():
                case OS.WIN:
                    client_file_str = self.clientFile.lower()
                    client_root_str = normalized_client_root.lower()
                case OS.MAC | OS.LINUX:
                    client_file_str = self.clientFile
                    client_root_str = normalized_client_root

            if client_file_str.startswith(f'{client_root_str}{fileUtils.get_split_character()}'):
                P4LogMessage().under_ws_root(self.get_display_name())
                return True
        P4ErrorMessage(silent).not_under_ws_root(self.get_display_name())
        return False

    def is_in_client_view(self, silent: bool = False):
        if self.notInClientView:
            P4ErrorMessage(silent).not_in_client_view(self.get_display_name())
            return False
        else:
            P4LogMessage().in_client_view(self.get_display_name())
            return True

    def is_free_from_other_checkouts(self, silent: bool = False):
        if self.status is P4FileStatus.CHECKOUT_BY_OTHER:
            P4ErrorMessage(silent).not_free_from_other_checkouts(self.get_display_name())
            return False
        else:
            P4LogMessage().free_from_other_checkouts(self.get_display_name())
            return True

    def is_not_marked_for_delete(self, silent: bool = False):
        if self.status is P4FileStatus.MARKED_FOR_DELETE:
            P4ErrorMessage(silent).marked_for_delete(self.get_display_name())
            return False
        else:
            P4LogMessage().not_marked_for_delete(self.get_display_name())
            return True

    def __run_p4_cmd(self, command: str,
                     incl_status_lst: Union[List[P4FileStatus], None] = None,
                     excl_status_lst: Union[List[P4FileStatus], None] = None):

        # See if command can be run, return if cannot
        if incl_status_lst is not None:
            if not self.status in incl_status_lst:
                return False
        if excl_status_lst is not None:
            if self.status in excl_status_lst:
                return False

        # If add command, create file before checkout if doesn't exist (may be created later)
        if 'p4 add' in command and self.clientFile is not None:
            create_empty_file(self.clientFile)

        # Run command for p4_file
        display_name = self.get_display_name()
        exec_p4_command(f'{command} {display_name}')
    
    def _run_p4_add(self):
        self._callback_pre_add()
        self.__run_p4_cmd(command='p4 add', incl_status_lst=[P4FileStatus.NOT_ADDED])
        self._callback_post_add()
    
    def _run_p4_sync(self):
        self._callback_pre_sync()
        # progress_bar = uiUtils.display_progress_bar(f'{tool_name}: Getting Latest...')
        # progress_bar.update_progress(10)
        self.__run_p4_cmd(command='p4 sync -f', incl_status_lst=[P4FileStatus.NOT_LATEST_REVISION])
        # progress_bar.update_progress(100)
        # progress_bar.dlg.close()
        self._callback_post_sync()
    
    def _run_p4_edit(self):
        self._callback_pre_edit()
        self.__run_p4_cmd(command='p4 edit', excl_status_lst=[P4FileStatus.NOT_ADDED, P4FileStatus.MARKED_FOR_ADD, P4FileStatus.CHECKOUT_BY_ME])
        self._callback_post_edit()
    
    def _callback_pre_add(self):
        pass
    
    def _callback_post_add(self):
        pass
        
    def _callback_pre_sync(self):
        pass
        
    def _callback_post_sync(self):
        pass
        
    def _callback_pre_edit(self):
        pass
        
    def _callback_post_edit(self):
        pass
    
    def open_for_edit(self, silent: bool = False):
        
        msg = ('P4File.open_for_edit: Running single-file open_for_edit, which is costly to run in a loop. Please only use for explicit checkout'
               'requiring user interaction. For batch checkout, use P4FileGroup.open_for_edit instead as it is more optimized!')
        log(Severity.WARNING, tool_name, msg)

        # Perforce Server accessible Check
        p4_info_cls = P4Info()
        if not p4_info_cls.is_server_accessible(silent):
            return False
        elif not self.is_client_file_under_workspace_root(p4_info_cls, silent=True):
            P4ErrorMessage(silent).not_under_ws_root_elaborate(p4_info_cls)
            return False
        
        # Update fields
        result = self.update_fields()
        if not result:  # Fields didn't properly get set
            return False

        # Perform other checks before checkout
        elif not self.is_in_client_view(silent=True):
            P4ErrorMessage(silent).not_in_client_view_elaborate(p4_info_cls)
            return False
        elif not self.is_free_from_other_checkouts(silent=True):
            P4ErrorMessage(silent).not_free_from_other_checkouts_elaborate()
            return False
        elif not self.is_not_marked_for_delete(silent=True):
            P4ErrorMessage(silent).marked_for_delete_elaborate()
            return False

        # Mark not added for add
        if self.status in [P4FileStatus.NOT_ADDED]:
            if silent:
                self._run_p4_add()
            else:
                msg = f'File "{self.file_name}" is not marked for add. Do you want to mark for add?'
                msg_box_result = uiUtils.display_msg_box_ok_cancel(tool_name, msg)
                if msg_box_result:
                    self._run_p4_add()
                else:
                    return False

        # Get latest on files that are not at latest
        if self.status in [P4FileStatus.NOT_LATEST_REVISION]:
            if silent:
                self._run_p4_sync()
            else:
                msg = f'File "{self.file_name}" is not synced to the latest revision. Sync to the latest revision?'
                msg_box_result = uiUtils.display_msg_box_ok_cancel(tool_name, msg)
                if msg_box_result:
                    self._run_p4_sync()
                else:
                    return False

        # Checkout files that re not checked out yet
        if self.status not in [P4FileStatus.NOT_ADDED, P4FileStatus.MARKED_FOR_ADD, P4FileStatus.CHECKOUT_BY_ME]:
            if silent:
                self._run_p4_edit()
            else:
                msg = f'File "{self.file_name}" is not checked out. Check out?'
                msg_box_result = uiUtils.display_msg_box_ok_cancel(tool_name, msg)
                if msg_box_result:
                    self._run_p4_edit()
                else:
                    return False

        # Update fields
        result = self.update_fields()
        if not result:  # Fields didn't properly get set
            return False

        # If not checked out or marked for add, did not succeed
        if self.status not in [P4FileStatus.MARKED_FOR_ADD, P4FileStatus.CHECKOUT_BY_ME]:
            msg = f'File "{self.file_name}" could not be successfully checked out! Check log for details.'
            log(Severity.ERROR, tool_name, msg)
            return False

        return True


class BlendP4File(P4File):
    # TODO: Handle sync (exit > sync > reload scene)
    def __init__(self, client_file: Union[str, None] = None, depot_file: Union[str, None] = None):
        if client_file is None:
            log(Severity.CRITICAL, tool_name, 'BlendP4File: Input client_file is Invalid! Received None.')
        elif client_file.count('.') < 1:
            log(Severity.CRITICAL, tool_name, f'BlendP4File: Input client_file "{client_file}" should be a .BLEND file path (incl. extension).')
        elif client_file.split('.')[-1] != 'blend':
            log(Severity.CRITICAL, tool_name, f'BlendP4File: Meant to receive a client_file with a .BLEND extension. Invalid Path: {client_file}')
        super().__init__(client_file, depot_file)

    def open_blend_for_edit(self, silent: bool = False):
        # Initial Checks
        check_result = filterUtils.check_tests('Check Out Current Blend Scene',
                                               check_blend_exist=True,
                                               check_source_control_enable=True,
                                               silent_mode=silent
                                               )
        if not check_result:
            return False

        super().open_for_edit(silent=silent)

    def _callback_post_sync(self):
        bpy.ops.wm.open_mainfile(filepath=self.clientFile)


class P4FileGroup:
    """
    Optimized way of working (batch calls), use this instead of running P4File in a forloop whenever possible.
    """

    def __init__(self):
        self.__p4_file_lst: List[P4File] = []

    def get_p4_file_lst(self) -> List[P4File]:
        return self.__p4_file_lst

    def append_p4_file_to_group_from_client_file(self, client_file):
        p4_file = P4File(client_file=client_file)
        self.__p4_file_lst.append(p4_file)

    def append_p4_file_to_group_from_depot_file(self, depot_file):
        p4_file = P4File(depot_file=depot_file)
        self.__p4_file_lst.append(p4_file)

    def get_p4_file_with_client_file_dict(self) -> Dict[str, P4File]:
        p4_file_dict = {}
        for p4_file in self.__p4_file_lst:
            if p4_file.clientFile is not None:
                p4_file_dict[p4_file.clientFile] = p4_file
        return p4_file_dict

    def get_p4_file_with_depot_file_and_no_client_file(self):
        p4_file_with_client_file_dict = self.get_p4_file_with_client_file_dict()
        p4_file_dict = {}
        for p4_file in self.__p4_file_lst:
            if p4_file not in p4_file_with_client_file_dict.values():
                if p4_file.depotFile is not None:
                    p4_file_dict[p4_file.depotFile] = p4_file
                else:
                    P4CriticalMessage().p4_file_client_or_depot_path_required(group=True)
        return p4_file_dict

    def update_fields_client_n_depot(self):
        """
        Create dictionary of clientFile & depotFile and update fields and match.
        """

        # Update fields for Dict [clientFile (str), P4File]
        client_file_p4_file_dict = self.get_p4_file_with_client_file_dict()
        if not self.update_fields_by_matching_key('clientFile', client_file_p4_file_dict):
            return False

        # Update fields for Dict [depotFile (str), P4File]
        depot_file_p4_file_dict = self.get_p4_file_with_depot_file_and_no_client_file()
        if not self.update_fields_by_matching_key('depotFile', depot_file_p4_file_dict):
            return False

        # Completed
        return True

    def update_fields_by_matching_key(self, fstat_key: str, p4_file_dict: Dict[str, P4File]):
        """
        Batch operation. Updates the fields of a dictionary of P4 Files, where the key is either clientFile or
        depotFile. A fstat_key parameter is given, saying what's the key (clientFile or depotFile)
        """
        if fstat_key not in ['depotFile', 'clientFile']:
            log(Severity.CRITICAL, tool_name, 'Update fields by matching key: fstat_key is invalid')
            return False

        file_path_string_lst = self.append_lst_to_string_max_length(p4_file_dict.keys(), ' ', 1000, quotation_marks=True)
        call_counter = 0
        for file_path_string in file_path_string_lst:
            # Print number of call executed, to give progress feedback...
            call_counter += 1
            log(Severity.DEBUG, tool_name, f'Issuing Call (from {fstat_key}) # {call_counter} of {len(file_path_string_lst)}')

            # Inquire and get results as a lst of dicts
            result_dicts_lst = p4_fstat_dict(file_path_string)
            if not result_dicts_lst:
                return False  # There was an error fetching the dict

            for result_dict in result_dicts_lst:
                result_match_key = result_dict[fstat_key]
                match_p4_file: Optional[P4File] = None

                # If on Windows and cannot find key, attempt by ignoring case. Other platform YOLO it that way too.
                if result_match_key not in p4_file_dict.keys():
                    result_match_key_lower = result_match_key.lower()
                    for original_key in p4_file_dict.keys():
                        original_key_lower = original_key.lower()
                        if original_key_lower == result_match_key_lower:
                            match_p4_file = p4_file_dict[original_key]
                            break
                else:
                    match_p4_file = p4_file_dict[result_match_key]

                if match_p4_file is not None:
                    match_p4_file.update_fields(result_dict)
                else:
                    msg = f'Could not match key {fstat_key} {result_match_key} to a P4File!'
                    log(Severity.ERROR, tool_name, msg)
                    return False

        return True  # Worked properly for all

    def force_get_latest(self):
        self.__run_p4_cmd_on_p4_file_lst(command='p4 sync -f')

    def __run_p4_cmd_on_p4_file_lst(self, command: str,
                                    incl_status_lst: Union[List[P4FileStatus], None] = None,
                                    excl_status_lst: Union[List[P4FileStatus], None] = None):
        # Run command for p4_file with clientFile
        file_path_with_client_file_dict = self.get_p4_file_with_client_file_dict()
        # Filter
        filtered_file_path_with_client_file_dict = {}
        for key, p4_file in file_path_with_client_file_dict.items():
            include = True
            if incl_status_lst is not None:
                if p4_file.status not in incl_status_lst:
                    include = False
            if excl_status_lst is not None:
                if p4_file.status in excl_status_lst:
                    include = False
            if include:
                filtered_file_path_with_client_file_dict[key] = p4_file
        # If command is to add a file, and it's not present on disk already, a dummy file must be created. This only applies to clientFile (disk path), not depotPath (server path)
        if 'p4 add' in command:
            for p4_file in filtered_file_path_with_client_file_dict.values():
                if not os.path.isfile(p4_file.clientFile):
                    create_empty_file(p4_file.clientFile)
        # Create string
        file_path_string_lst = self.append_lst_to_string_max_length(filtered_file_path_with_client_file_dict.keys(), ' ', 1000, quotation_marks=True)
        call_counter = 0
        for file_path_string in file_path_string_lst:
            # Print number of call executed, to give progress feedback...
            call_counter += 1
            log(Severity.DEBUG, tool_name,
                'Issuing Call (from clientFile) #' + str(call_counter) + ' of ' + str(len(file_path_string_lst)))
            exec_p4_command(f'{command} {file_path_string}')

        # Run command for p4_file with depotFile (and no clientFile)
        file_path_with_depot_file_dict = self.get_p4_file_with_depot_file_and_no_client_file()
        # Filter
        filtered_file_path_with_depot_file_dict = {}
        for key, p4_file in file_path_with_depot_file_dict.items():
            include = True
            if incl_status_lst is not None:
                if p4_file.status not in incl_status_lst:
                    include = False
            if excl_status_lst is not None:
                if p4_file.status in excl_status_lst:
                    include = False
            if include:
                filtered_file_path_with_depot_file_dict[key] = p4_file
        # Create string
        file_path_string_lst = self.append_lst_to_string_max_length(filtered_file_path_with_depot_file_dict.keys(), ' ', 1000, quotation_marks=True)
        call_counter = 0
        for file_path_string in file_path_string_lst:
            # Print number of call executed, to give progress feedback...
            call_counter += 1
            log(Severity.DEBUG, tool_name,
                'Issuing Call (from depotFile) #' + str(call_counter) + ' of ' + str(len(file_path_string_lst)))
            exec_p4_command(f'{command} {file_path_string}')

    def open_for_edit(self):
        """
        Accurate method of opening files for edit (Get latest if needed, only checks out if not checked out yet, warning if someone else has the file, etc.)
        """

        # Check Perforce server is accessible
        p4_info_cls = P4Info()
        if not p4_info_cls.is_server_accessible():
            return False
        if not self.is_client_file_under_workspace_root(p4_info_cls):
            return False

        # Update fields
        result = self.update_fields_client_n_depot()
        if not result:  # Fields didn't properly get set
            return False

        # Perform Checks before Proceeding
        if not self.is_in_client_view(p4_info_cls):
            return False
        if not self.is_free_from_other_checkouts():
            return False
        if not self.is_not_marked_for_delete():
            return False

        # Mark not added for add
        self.__run_p4_cmd_on_p4_file_lst(command='p4 add', incl_status_lst=[P4FileStatus.NOT_ADDED])

        # Get latest on files that are not at latest
        self.__run_p4_cmd_on_p4_file_lst(command='p4 sync -f', incl_status_lst=[P4FileStatus.NOT_LATEST_REVISION])

        # Checkout files that re not checked out yet
        self.__run_p4_cmd_on_p4_file_lst(command='p4 edit',
                                         excl_status_lst=[P4FileStatus.NOT_ADDED,
                                                          P4FileStatus.MARKED_FOR_ADD,
                                                          P4FileStatus.CHECKOUT_BY_ME])

        # Update fields
        result = self.update_fields_client_n_depot()
        if not result:  # Fields didn't properly get set
            return False

        # If got here with no issue, completed successfully
        return True

    def is_client_file_under_workspace_root(self, p4_info_cls: P4Info) -> bool:
        # Validate all clientFile entries for asset are under the current workspace root
        p4_ws_root = p4_info_cls.client_root
        not_under_ws_root = []
        for p4_file in self.__p4_file_lst:
            if not p4_file.is_client_file_under_workspace_root(p4_info_cls, silent=True):
                not_under_ws_root.append(p4_file)
        # If at least one clientFile was not under the workspace root, show error dialogue and exit process
        if len(not_under_ws_root) > 0:
            P4ErrorMessage().not_under_ws_root_elaborate(p4_info_cls)
            return False
        return True

    def is_in_client_view(self, p4_info_cls: P4Info) -> bool:
        # Check if not in client view
        not_in_client_view = []
        for p4_file in self.__p4_file_lst:
            if not p4_file.is_in_client_view(silent=True):
                not_in_client_view.append(p4_file)
        # If at least one file was not in client view, show error dialogue and exit process
        if len(not_in_client_view) > 0:
            P4ErrorMessage().not_in_client_view_elaborate(p4_info_cls)
            return False
        return True

    def is_free_from_other_checkouts(self) -> bool:
        # Check if files are checked out by somebody else
        p4_checked_out_others_lst = []
        for p4_file in self.__p4_file_lst:
            if not p4_file.is_free_from_other_checkouts():
                p4_checked_out_others_lst.append(p4_file)
        # If at least one file was checked out by others, display error message.
        if len(p4_checked_out_others_lst) > 0:
            P4ErrorMessage().not_free_from_other_checkouts_elaborate()
            return False
        return True

    def is_not_marked_for_delete(self):
        # Check if files are marked for delete elsewhere
        p4_marked_delete_lst = []
        for p4_file in self.__p4_file_lst:
            if not p4_file.is_not_marked_for_delete():
                p4_marked_delete_lst.append(p4_file)
        # If at least one file was marked for delete elsewhere, display error message.
        if len(p4_marked_delete_lst) > 0:
            P4ErrorMessage().marked_for_delete_elaborate()
            return False  # Did not run as intended.
        return True

    def append_lst_to_string_max_length(self, lst, split_str, max_str_length, quotation_marks=False):
        """
        Append elements of a list to a string (if the result is less than specific string maximum length). When limit is
        to be reached, append to a second string and so on, so forth.
        :param lst: List of elements to append to the string(s)
        :type lst: lst
        :param split_str: Segment to put in-between appends
        :type split_str: str
        :param max_str_length: Maximum character length allowed for a string
        :type max_str_length: int
        :param quotation_marks: When true, puts quotation marks at start/end of each element in list
        :type quotation_marks: bool
        """
        # Create strings of limited length
        file_str_lst = []
        file_str = ''
        for item in lst:
            if quotation_marks:
                item = '"' + item + '"'
            if len(file_str) + len(item) + len(split_str) > max_str_length:  # If longer than max length
                file_str_lst.append(file_str)  # Append string to list of strings to execute
                file_str = ''  # Reset string
            file_str += item + split_str

        # Add what is left in file_str to file_str_lst
        if file_str != '':
            file_str_lst.append(file_str)

        # Remove the in-between at the end of each string of the array.
        file_str_lst_final = []
        for string in file_str_lst:
            file_str_lst_final.append(string[:-len(split_str)])

        # Return array of strings
        return file_str_lst


def p4_fstat_dict(file_path_string, silent_mode=False) -> Optional[List[Dict[str, str]]]:
    """
    Get p4 fstat results, cleaned as an array of dicts (1 dict per item)
    """

    # If file_path isn't enclosed in quotation marks, enclose.
    if '"' not in file_path_string[0]:
        file_path_string = '"' + file_path_string + '"'

    # Get status of files
    result_array = exec_p4_command("p4 fstat {}".format(file_path_string))

    result_dicts_lst = []
    result_dict = {}

    # Transform status of files in easily understood dict
    for i in result_array:
        if 'Your session has expired, please login again' in i:
            if not silent_mode:
                msg = 'Your session has expired. Please login again from Perforce. Aborting!'
                log(Severity.ERROR, tool_name, msg, popup=True)
            return None
        elif ' - no such file(s).' in i:
            result_dict = {'clientFile': i.replace(' - no such file(s).', '')}
            result_dicts_lst.append(result_dict)
            result_dict = {}
        elif ' - file(s) not in client view.' in i:
            result_dict = {'clientFile': i.replace(' - file(s) not in client view.', ''), 'notInClientView': True}
            result_dicts_lst.append(result_dict)
            result_dict = {}
        else:
            i = i.replace('... ', '')
            if len(i) > 0:
                split_i = i.split(' ')
                split_i_up_to_last = ''
                split_i_length = len(split_i)
                for idx, value in enumerate(split_i):
                    if idx > 0:
                        if idx < split_i_length - 1:
                            split_i_up_to_last += value + ' '
                        else:
                            split_i_up_to_last += value
                result_dict[split_i[0]] = split_i_up_to_last
            else:
                result_dicts_lst.append(result_dict)
                result_dict = {}

    return result_dicts_lst


def get_p4_file_group_from_depot_file_lst(depot_file_lst: List[str]) -> P4FileGroup:
    """
    From a list of depot file paths (Windows/OS-type paths), returns a P4FileGroup (with updated fields)
    """
    log(Severity.DEBUG, tool_name, 'Initiating p4_get_status_dict_from_file_list function!')

    p4_file_group = P4FileGroup()
    for file_path in depot_file_lst:
        p4_file_group.append_p4_file_to_group_from_depot_file(file_path)
    p4_file_group.update_fields_client_n_depot()  # Batch operation, very efficient in perforce calls

    return p4_file_group


def get_p4_file_group_from_client_file_lst(client_file_lst: List[str]) -> P4FileGroup:
    """
    From a list of client file paths (Perforce-type paths), returns a P4FileGroup (with updated fields)
    """
    log(Severity.DEBUG, tool_name, 'Initiating p4_get_status_dict_from_file_list function!')

    p4_file_group = P4FileGroup()
    for file_path in client_file_lst:
        p4_file_group.append_p4_file_to_group_from_client_file(file_path)
    p4_file_group.update_fields_client_n_depot()  # Batch operation, very efficient in perforce calls

    return p4_file_group


# Other file migration under here
def source_control_disabled_dialog():
    """
    Dialog box warns the user source control is currently disabled in Blue Hole preferences.
    """
    message = 'Disregarding Source Control stuff: Source Control is disabled in the Blue Hole addon settings.'
    log(Severity.DEBUG, tool_name, message)


def dialog_box_p4_info():
    """
    Dialog box displays perforce connection information.
    """
    # Initial checks
    check_result = filterUtils.check_tests('Display Server Info',
                                           check_source_control_enable=True,
                                           check_source_control_connection=True)
    if not check_result:
        return False

    # If can connect to perforce, proceed.
    p4_info_cls = P4Info()
    msg = (f'User name: {p4_info_cls.user_name}\n'
           f'Client name: {p4_info_cls.client_name}\n'
           f'Client root: {p4_info_cls.client_root}\n'
           f'Server address: {p4_info_cls.server_address}\n'
           f'Server uptime: {p4_info_cls.server_uptime}')

    log(Severity.INFO, tool_name, msg, popup=True)
    return True


def set_p4_env_settings():
    """
    Set Environment Variables, if configured in User Preferences
    """
    print('Initialize set P4 environment settings')

    # If Source Control is enabled in the Preferences
    if filterUtils.filter_source_control() and prefs().sc.source_control_solution == 'perforce':
        print('Attempting to set P4 environment settings')
        # If platform is Windows
        match get_os():
            case OS.WIN:
                # If preference set to "Override Environment Settings"
                if prefs().sc.win32_env_override:
                    print('Override environment settings is ON')
                    cmd_str = 'p4 set P4USER=' + prefs().sc.macos_env_setting_p4user
                    exec_p4_command(cmd_str)
                    cmd_str = 'p4 set P4PORT=' + prefs().sc.macos_env_setting_p4port
                    exec_p4_command(cmd_str)
                    cmd_str = 'p4 set P4CLIENT=' + prefs().sc.macos_env_setting_p4client
                    exec_p4_command(cmd_str)
            case OS.MAC:
                # If Platform is MacOS, Set automatically as the MacOS P4V Client doesn't have Environment Settings.
                cmd_str = 'p4 set P4USER=' + prefs().sc.macos_env_setting_p4user
                exec_p4_command(cmd_str)
                cmd_str = 'p4 set P4PORT=' + prefs().sc.macos_env_setting_p4port
                exec_p4_command(cmd_str)
                cmd_str = 'p4 set P4CLIENT=' + prefs().sc.macos_env_setting_p4client
                exec_p4_command(cmd_str)
            case OS.LINUX:
                # If Platform is Linux, Set automatically as the MacOS P4V Client doesn't have Environment Settings.
                cmd_str = 'p4 set P4USER=' + prefs().sc.linux_env_setting_p4user
                exec_p4_command(cmd_str)
                cmd_str = 'p4 set P4PORT=' + prefs().sc.linux_env_setting_p4port
                exec_p4_command(cmd_str)
                cmd_str = 'p4 set P4CLIENT=' + prefs().sc.linux_env_setting_p4client
                exec_p4_command(cmd_str)

class P4UserWorkspace:
    def __init__(self):
        self.computername = None
        self.username = None
        self.workspace = None


def create_p4_user_workspace_cls(computer_name, username, workspace):
    p4userws_cls = P4UserWorkspace()
    p4userws_cls.computername = computer_name
    p4userws_cls.username = username
    p4userws_cls.workspace = workspace
    return p4userws_cls

# LOG, ERROR, CRITICAL MESSAGES


class P4LogMessage:
    def __init__(self):
        pass

    def log(self, msg):
        log(Severity.DEBUG, tool_name, msg)

    # DEBUG LOGS (NEVER Popup)
    def info_log_server_accessible(self):
        msg = 'Perforce Server is Accessible!'
        self.log(msg)

    def under_ws_root(self, name):
        msg = f'"{name}" is under workspace root.'
        self.log(msg)

    def in_client_view(self, name):
        msg = f'"{name}" is in client view.'
        self.log(msg)

    def free_from_other_checkouts(self, name):
        msg = f'"{name}" is free from other checkouts.'
        self.log(msg)

    def not_marked_for_delete(self, name):
        msg = f'"{name}" is not marked for delete.'
        self.log(msg)


class P4ErrorMessage:
    def __init__(self, silent: bool = False):
        self.silent: bool = silent

    def log_error(self, msg):
        log(Severity.ERROR, tool_name, msg, popup=not self.silent)

    # ERRORS (Popup IF NOT SILENT)
    def info_default_connection(self):
        msg = ('Please properly set the default environment setting in Perforce:\n'
               '1. Open Perforce (P4V) App\n'
               '2. Login to your workspace\n'
               '3. Connection -> Environment Settings\n'
               '4. Uncheck Use current connection for environment settings.\n'
               '5. Fill Server, User, Workspace fields accordingly.\n'
               '6. Press OK\n\n'
               'Aborting Perforce Scripts!')
        self.log_error(msg)

    def info_perforce_client_error(self):
        msg = 'Perforce has client error. See log for details.'
        self.log_error(msg)

    def info_not_recognized(self):
        msg = 'Perforce not recognized. Is Perforce Visual Client Installed? See log for details.'
        self.log_error(msg)

    def info_win_p4_cmd_missing(self):
        msg = 'Perforce permission denied. Very odd for Windows P4 to have this issue. Investigate P4 executable.'
        self.log_error(msg)

    def info_mac_p4_cmd_missing(self, exec_pth):
        msg = ('Perforce parallel (p4_parallel) permission denied. If on macOS, launch executable here once by '
               'right-clicking and selecting "Open": {}. If that does not work (ex. file opens in TextEdit), '
               'you will need to open a terminal window and enter the following followed by the '
               f'executable\'s path: sudo chmod +x {exec_pth}')
        self.log_error(msg)

    def info_linux_p4_cmd_missing(self, exec_pth):
        msg = ('Perforce parallel (p4_parallel) permission denied. If on Linux, you will need to open a terminal '
               f'window and enter the following followed by the executable\'s path: sudo chmod +x {exec_pth}')
        self.log_error(msg)

    def info_server_cannot_connect(self):
        msg = 'Could not connect to Perforce Server! Check your Internet and VPN settings.'
        self.log_error(msg)

    def not_under_ws_root(self, name):
        msg = f'"{name}" is not under the workspace root.'
        self.log_error(msg)

    def not_under_ws_root_elaborate(self, p4_info_cls: P4Info):
        msg = (f'You cannot send Perforce commands for some file(s) because they are not under your current '
               f'workspace tree.\n\n'
               f'Workspace name: "{p4_info_cls.client_name}"\n'
               f'Workspace root: "{p4_info_cls.client_root}"\n\n'
               'Suggestions on how to fix:\n'
               'A) Move designated file(s) under your current workspace tree.\n'
               'B) If the workspace tree is wrong, check your Perforce Environment Settings.\n'
               'See log for further details.')
        self.log_error(msg)

    def not_in_client_view(self, name):
        msg = f'"{name}" is not in client view.'
        self.log_error(msg)

    def not_in_client_view_elaborate(self, p4_info_cls: P4Info):
        msg = ('File(s) could not be checked out as they are not in the Perforce Client\'s view. '
               f'The current Perforce Workspace\'s ({p4_info_cls.client_name}) Mapping does not include the '
               f'location for these items on disk. Please configure this from the P4V Application. '
               f'See log for details.')
        self.log_error(msg)

    def not_free_from_other_checkouts(self, name):
        msg = f'"{name}" is free from other checkouts.'
        self.log_error(msg)

    def not_free_from_other_checkouts_elaborate(self):
        msg = 'File(s) are checked out by other users. See log for details.'
        self.log_error(msg)

    def marked_for_delete(self, name):
        msg = f'"{name}" is not marked for delete.'
        self.log_error(msg)

    def marked_for_delete_elaborate(self):
        msg = 'File(s) are marked for delete. See logs for details.'
        self.log_error(msg)


class P4CriticalMessage:
    def __init__(self):
        pass

    def log_critical(self, msg):
        log(Severity.CRITICAL, tool_name, msg, popup=True)

    # CRITICAL (Popup AND APPLICATION SHUTDOWN)
    def p4_file_client_or_depot_path_required(self, group=False):
        if group:
            error_from = 'P4FileGroup'
        else:
            error_from = 'P4File'
        msg = f'{error_from}: You must specify (at a minimum) either a client_file or depot_file parameter!'
        self.log_critical(msg)


def create_empty_file(file_path):
    """
    Creates an empty file at desired filepath, if it does not exist yet.
    """
    # Create directory (if it doesn't exist yet)
    Path(os.path.dirname(file_path)).mkdir(parents=True, exist_ok=True)
    # Create File
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as fp:
            pass


def get_p4_macos_path() -> str:
    return f'{prefs().sc.p4v_app_path_mac}/Contents/Resources/p4_parallel'  # Complete to get p4_parallel path


def get_p4_linux_path() -> str:
    return prefs().sc.p4_parallel_path_linux


def exec_p4_command(command: str):
    """
    Execute Perforce commands. Based on cmdShellWrapper's exec_cmd,
    but with a few specific things to ensure proper functioning on macOS and Linux.
    """

    # Ensures this is used for Perforce commands, else raise exception and recommend using wrapper directly.
    if not command.startswith('p4 '):
        msg = (f'Command fed to exec_p4_command should always be Perforce commands (start with "p4 "), however '
               f'received "{command}" which does not meet this criteria.')
        log(Severity.CRITICAL, 'Perforce Command', msg)

    # Resolve P4 Path (macOS & Linux need to be pointed to p4_parallel file)
    p4_path: str = {OS.WIN: 'p4', OS.MAC: get_p4_macos_path(), OS.LINUX: get_p4_linux_path()}[get_os()]

    match get_os():
        case OS.MAC | OS.LINUX:
            # p4_parallel path needs to be valid
            if not os.path.isfile(p4_path):
                msg = (f'P4 Parallel path "{p4_path}" is invalid. Verify that Perforce is installed and, if required, '
                       f'update this Path in the Blue Hole addon settings (Source Control Tab).')
                log(Severity.CRITICAL, 'Perforce Command', msg)

            # Set permissions
            cmdShellWrapper.exec_cmd(f'chmod +x "{p4_path}"')

            # Replace p4 in command with the path (in quotes)
            command = f'"{p4_path}" {command[2:]}'

    # Execute the command
    return cmdShellWrapper.exec_cmd(command, time_out=15)
