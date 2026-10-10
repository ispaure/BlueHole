"""Blender-specific callbacks around the shared Perforce file model."""
from typing import Union
import bpy
from ...blenderUtils import filterUtils
from ...Lib.commonUtils.runtime.diagnostics import log, Severity
from ...Lib.commonUtils.integrations.wrappers.perforce.p4_file import P4File
tool_name = 'Blue Hole [Perforce Wrapper]'


class BlendP4File(P4File):
    # TODO: Handle sync (exit > sync > reload scene)
    def __init__(self, client_file: Union[str, None] = None, depot_file: Union[str, None] = None):
        if client_file is None:
            log(Severity.CRITICAL, tool_name, 'BlendP4File: Input client_file is Invalid! Received None.')
        elif client_file.count('.') < 1:
            log(Severity.CRITICAL, tool_name,
                f'BlendP4File: Input client_file "{client_file}" should be a .BLEND file path (incl. extension).')
        elif client_file.split('.')[-1] != 'blend':
            log(Severity.CRITICAL, tool_name,
                f'BlendP4File: Meant to receive a client_file with a .BLEND extension. Invalid Path: {client_file}')
        super().__init__(client_file, depot_file)

    def open_blend_for_edit(self, allow_sync: bool, silent: bool = False):
        # Initial Checks
        check_result = filterUtils.check_tests('Check Out Current Blend Scene',
                                               check_blend_exist=True,
                                               check_source_control_enable=True,
                                               silent_mode=silent
                                               )
        if not check_result:
            return False

        super().open_for_edit(silent=silent, allow_sync=allow_sync)

    def _callback_post_sync(self):
        bpy.ops.wm.open_mainfile(filepath=self.clientFile)
