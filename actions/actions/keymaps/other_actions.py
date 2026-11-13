"""Editor and global shortcuts grouped under Other."""

from ...operator_action import KeymapBinding, OperatorAction

# Blender prepends add-on rows during merge. Register in reverse reference order
# so the merged map retains the order of these declarations.
OTHER_ACTIONS = (
    OperatorAction(
        operator='transform.resize',
        props={'release_confirm': True},
        keymap_bindings=(KeymapBinding(
            'Preview Tool: Scale', 'SEQUENCE_EDITOR', 'MIDDLEMOUSE'),),
    ),
    OperatorAction(
        operator='transform.rotate',
        props={'release_confirm': True},
        keymap_bindings=(KeymapBinding(
            'Preview Tool: Rotate', 'SEQUENCE_EDITOR', 'MIDDLEMOUSE'),),
    ),
    OperatorAction(
        operator='transform.translate',
        props={'release_confirm': True},
        keymap_bindings=(KeymapBinding(
            'Preview Tool: Move', 'SEQUENCE_EDITOR', 'MIDDLEMOUSE'),),
    ),
    OperatorAction(
        operator='sequencer.cursor_set',
        keymap_bindings=(KeymapBinding(
            'Preview Tool: Cursor', 'SEQUENCE_EDITOR', 'MIDDLEMOUSE'),),
    ),
    OperatorAction(
        operator='sequencer.split',
        props={'type': 'SOFT', 'use_cursor_position': True, 'side': 'NO_CHANGE', 'ignore_selection': True},
        keymap_bindings=(KeymapBinding(
            'Sequencer Tool: Blade', 'SEQUENCE_EDITOR', 'MIDDLEMOUSE'),),
    ),
    OperatorAction(
        operator='sequencer.select_box',
        props={'mode': 'SUB', 'tweak': False},
        keymap_bindings=(KeymapBinding(
            'Sequencer Tool: Select Box (fallback)', 'SEQUENCE_EDITOR', 'RIGHTMOUSE',
            value='CLICK_DRAG', ctrl=True),),
    ),
    OperatorAction(
        operator='sequencer.select_box',
        props={'mode': 'SUB', 'tweak': False},
        keymap_bindings=(KeymapBinding(
            'Sequencer Tool: Select Box (fallback)', 'SEQUENCE_EDITOR', 'RIGHTMOUSE',
            value='CLICK_DRAG', oskey=True),),
    ),
    OperatorAction(
        operator='sequencer.select_box',
        props={'mode': 'ADD', 'tweak': False},
        keymap_bindings=(KeymapBinding(
            'Sequencer Tool: Select Box (fallback)', 'SEQUENCE_EDITOR', 'RIGHTMOUSE',
            value='CLICK_DRAG', shift=True),),
    ),
    OperatorAction(
        operator='sequencer.select_box',
        props={'tweak': False},
        keymap_bindings=(KeymapBinding(
            'Sequencer Tool: Select Box (fallback)', 'SEQUENCE_EDITOR', 'RIGHTMOUSE',
            value='CLICK_DRAG'),),
    ),
    OperatorAction(
        operator='view3d.interactive_add',
        props={'wait_for_input': False},
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Object, Add Primitive', 'VIEW_3D', 'MIDDLEMOUSE', ctrl=True),),
    ),
    OperatorAction(
        operator='view3d.interactive_add',
        props={'wait_for_input': False},
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Object, Add Primitive', 'VIEW_3D', 'MIDDLEMOUSE', oskey=True),),
    ),
    OperatorAction(
        operator='view3d.interactive_add',
        props={'wait_for_input': False},
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Object, Add Primitive', 'VIEW_3D', 'MIDDLEMOUSE'),),
    ),
    OperatorAction(
        operator='view3d.ruler_add',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Measure', 'VIEW_3D', 'MIDDLEMOUSE'),),
    ),
    OperatorAction(
        operator='transform.from_gizmo',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Transform', 'VIEW_3D', 'MIDDLEMOUSE', active=False),),
    ),
    OperatorAction(
        operator='node.select_circle',
        props={'wait_for_input': False, 'mode': 'SUB'},
        keymap_bindings=(KeymapBinding(
            'Node Tool: Select Circle (fallback)', 'NODE_EDITOR', 'RIGHTMOUSE',
            value='CLICK_DRAG', ctrl=True),),
    ),
    OperatorAction(
        operator='node.select_circle',
        props={'wait_for_input': False, 'mode': 'SUB'},
        keymap_bindings=(KeymapBinding(
            'Node Tool: Select Circle (fallback)', 'NODE_EDITOR', 'RIGHTMOUSE',
            value='CLICK_DRAG', oskey=True),),
    ),
    OperatorAction(
        operator='node.select_circle',
        props={'wait_for_input': False, 'mode': 'ADD'},
        keymap_bindings=(KeymapBinding(
            'Node Tool: Select Circle (fallback)', 'NODE_EDITOR', 'RIGHTMOUSE',
            value='CLICK_DRAG', shift=True),),
    ),
    OperatorAction(
        operator='node.select_circle',
        props={'wait_for_input': False},
        keymap_bindings=(KeymapBinding(
            'Node Tool: Select Circle (fallback)', 'NODE_EDITOR', 'RIGHTMOUSE',
            value='CLICK_DRAG'),),
    ),
    OperatorAction(
        operator='node.select_box',
        props={'tweak': True, 'mode': 'SUB'},
        keymap_bindings=(KeymapBinding(
            'Node Tool: Select Box (fallback)', 'NODE_EDITOR', 'RIGHTMOUSE', value='CLICK_DRAG',
            ctrl=True),),
    ),
    OperatorAction(
        operator='node.select_box',
        props={'tweak': True, 'mode': 'SUB'},
        keymap_bindings=(KeymapBinding(
            'Node Tool: Select Box (fallback)', 'NODE_EDITOR', 'RIGHTMOUSE', value='CLICK_DRAG',
            oskey=True),),
    ),
    OperatorAction(
        operator='node.select_box',
        props={'tweak': True, 'mode': 'ADD'},
        keymap_bindings=(KeymapBinding(
            'Node Tool: Select Box (fallback)', 'NODE_EDITOR', 'RIGHTMOUSE', value='CLICK_DRAG',
            shift=True),),
    ),
    OperatorAction(
        operator='node.select_box',
        props={'tweak': True},
        keymap_bindings=(KeymapBinding(
            'Node Tool: Select Box (fallback)', 'NODE_EDITOR', 'RIGHTMOUSE', value='CLICK_DRAG'),),
    ),
    OperatorAction(
        operator='node.select',
        props={'deselect_all': True},
        keymap_bindings=(KeymapBinding(
            'Node Tool: Tweak', 'NODE_EDITOR', 'RIGHTMOUSE'),),
    ),
    OperatorAction(
        operator='wm.search_menu',
        keymap_bindings=(KeymapBinding(
            'Clip Dopesheet Editor', 'CLIP_EDITOR', 'TAB'),),
    ),
    OperatorAction(
        operator='clip.graph_delete_knot',
        keymap_bindings=(KeymapBinding(
            'Clip Graph Editor', 'CLIP_EDITOR', 'BACK_SPACE', shift=True),),
    ),
    OperatorAction(
        operator='clip.graph_delete_curve',
        keymap_bindings=(KeymapBinding(
            'Clip Graph Editor', 'CLIP_EDITOR', 'BACK_SPACE'),),
    ),
    OperatorAction(
        operator='clip.graph_select_box',
        keymap_bindings=(KeymapBinding(
            'Clip Graph Editor', 'CLIP_EDITOR', 'Q'),),
    ),
    OperatorAction(
        operator='wm.search_menu',
        keymap_bindings=(KeymapBinding(
            'Clip Graph Editor', 'CLIP_EDITOR', 'TAB'),),
    ),
    OperatorAction(
        operator='wm.call_panel',
        props={'name': 'TOPBAR_PT_name', 'keep_open': False},
        keymap_bindings=(KeymapBinding(
            'Clip Graph Editor', 'CLIP_EDITOR', 'RET'),),
    ),
    OperatorAction(
        operator='clip.hide_tracks',
        props={'unselected': False},
        keymap_bindings=(KeymapBinding(
            'Clip Editor', 'CLIP_EDITOR', 'H', ctrl=True),),
    ),
    OperatorAction(
        operator='clip.delete_track',
        keymap_bindings=(KeymapBinding(
            'Clip Editor', 'CLIP_EDITOR', 'BACK_SPACE'),),
    ),
    OperatorAction(
        operator='clip.delete_marker',
        keymap_bindings=(KeymapBinding(
            'Clip Editor', 'CLIP_EDITOR', 'BACK_SPACE', shift=True),),
    ),
    OperatorAction(
        operator='clip.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Clip Editor', 'CLIP_EDITOR', 'A', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='clip.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Clip Editor', 'CLIP_EDITOR', 'A', shift=True, oskey=True),),
    ),
    OperatorAction(
        operator='clip.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Clip Editor', 'CLIP_EDITOR', 'A', ctrl=True),),
    ),
    OperatorAction(
        operator='clip.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Clip Editor', 'CLIP_EDITOR', 'A', oskey=True),),
    ),
    OperatorAction(
        operator='clip.select_box',
        keymap_bindings=(KeymapBinding(
            'Clip Editor', 'CLIP_EDITOR', 'Q'),),
    ),
    OperatorAction(
        operator='clip.view_zoom_out',
        keymap_bindings=(KeymapBinding(
            'Clip Editor', 'CLIP_EDITOR', 'WHEELOUTMOUSE', alt=True),),
    ),
    OperatorAction(
        operator='clip.view_zoom_in',
        keymap_bindings=(KeymapBinding(
            'Clip Editor', 'CLIP_EDITOR', 'WHEELINMOUSE', alt=True),),
    ),
    OperatorAction(
        operator='wm.search_menu',
        keymap_bindings=(KeymapBinding(
            'Clip Editor', 'CLIP_EDITOR', 'TAB'),),
    ),
    OperatorAction(
        operator='wm.call_panel',
        props={'name': 'TOPBAR_PT_name', 'keep_open': False},
        keymap_bindings=(KeymapBinding(
            'Clip', 'CLIP_EDITOR', 'RET'),),
    ),
    OperatorAction(
        operator='sequencer.sample',
        keymap_bindings=(KeymapBinding(
            'Preview', 'SEQUENCE_EDITOR', 'LEFTMOUSE'),),
    ),
    OperatorAction(
        operator='wm.tool_set_by_id',
        props={'name': 'builtin.select_box', 'cycle': True},
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'Q'),),
    ),
    OperatorAction(
        operator='marker.rename',
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'RET'),),
    ),
    OperatorAction(
        operator='transform.seq_slide',
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'MIDDLEMOUSE', value='CLICK_DRAG'),),
    ),
    OperatorAction(
        operator='transform.seq_slide',
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'W'),),
    ),
    OperatorAction(
        operator='sequencer.select_linked',
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'RIGHT_BRACKET', ctrl=True),),
    ),
    OperatorAction(
        operator='sequencer.select_linked',
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'RIGHT_BRACKET', oskey=True),),
    ),
    OperatorAction(
        operator='sequencer.select_linked_pick',
        props={'extend': True},
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'RIGHT_BRACKET', shift=True),),
    ),
    OperatorAction(
        operator='sequencer.select_less',
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'DOWN_ARROW', repeat=True),),
    ),
    OperatorAction(
        operator='sequencer.select_more',
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'UP_ARROW', repeat=True),),
    ),
    OperatorAction(
        operator='sequencer.select',
        props={'extend': True},
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'LEFTMOUSE', shift=True),),
    ),
    OperatorAction(
        operator='sequencer.select',
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'LEFTMOUSE'),),
    ),
    OperatorAction(
        operator='sequencer.view_selected',
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'F'),),
    ),
    OperatorAction(
        operator='sequencer.meta_toggle',
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'LEFTMOUSE', value='DOUBLE_CLICK'),),
    ),
    OperatorAction(
        operator='sequencer.unlock',
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'L', shift=True, alt=True),),
    ),
    OperatorAction(
        operator='sequencer.unmute',
        props={'unselected': True},
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'M', shift=True, alt=True),),
    ),
    OperatorAction(
        operator='sequencer.unmute',
        props={'unselected': False},
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'M', alt=True),),
    ),
    OperatorAction(
        operator='sequencer.mute',
        props={'unselected': True},
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'M', shift=True),),
    ),
    OperatorAction(
        operator='sequencer.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'A', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='sequencer.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'A', shift=True, oskey=True),),
    ),
    OperatorAction(
        operator='sequencer.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'A', ctrl=True),),
    ),
    OperatorAction(
        operator='sequencer.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'A', oskey=True),),
    ),
    OperatorAction(
        operator='screen.frame_jump',
        props={'end': False},
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'LEFT_ARROW', ctrl=True),),
    ),
    OperatorAction(
        operator='screen.frame_jump',
        props={'end': False},
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'LEFT_ARROW', oskey=True),),
    ),
    OperatorAction(
        operator='screen.frame_jump',
        props={'end': True},
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'RIGHT_ARROW', ctrl=True),),
    ),
    OperatorAction(
        operator='screen.frame_jump',
        props={'end': True},
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'RIGHT_ARROW', oskey=True),),
    ),
    OperatorAction(
        operator='screen.frame_offset',
        props={'delta': 1},
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'RIGHT_ARROW'),),
    ),
    OperatorAction(
        operator='screen.frame_offset',
        props={'delta': -1},
        keymap_bindings=(KeymapBinding(
            'Sequencer', 'SEQUENCE_EDITOR', 'LEFT_ARROW'),),
    ),
    OperatorAction(
        operator='wm.context_toggle',
        props={'data_path': 'space_data.show_region_ui'},
        keymap_bindings=(KeymapBinding(
            'Video Sequence Editor', 'SEQUENCE_EDITOR', 'RIGHT_BRACKET', ctrl=True),),
    ),
    OperatorAction(
        operator='wm.context_toggle',
        props={'data_path': 'space_data.show_region_ui'},
        keymap_bindings=(KeymapBinding(
            'Video Sequence Editor', 'SEQUENCE_EDITOR', 'RIGHT_BRACKET', oskey=True),),
    ),
    OperatorAction(
        operator='wm.call_panel',
        props={'name': 'TOPBAR_PT_name', 'keep_open': False},
        keymap_bindings=(KeymapBinding(
            'Video Sequence Editor', 'SEQUENCE_EDITOR', 'RET'),),
    ),
    OperatorAction(
        operator='wm.call_menu',
        props={'name': 'TEXT_MT_context_menu'},
        keymap_bindings=(KeymapBinding(
            'Text', 'TEXT_EDITOR', 'APP'),),
    ),
    OperatorAction(
        operator='text.new',
        keymap_bindings=(KeymapBinding(
            'Text', 'TEXT_EDITOR', 'N', ctrl=True),),
    ),
    OperatorAction(
        operator='text.new',
        keymap_bindings=(KeymapBinding(
            'Text', 'TEXT_EDITOR', 'N', oskey=True),),
    ),
    OperatorAction(
        operator='text.move',
        props={'type': 'NEXT_WORD'},
        keymap_bindings=(KeymapBinding(
            'Text', 'TEXT_EDITOR', 'RIGHT_ARROW', alt=True),),
    ),
    OperatorAction(
        operator='text.move',
        props={'type': 'PREVIOUS_WORD'},
        keymap_bindings=(KeymapBinding(
            'Text', 'TEXT_EDITOR', 'LEFT_ARROW', alt=True),),
    ),
    OperatorAction(
        operator='text.move',
        props={'type': 'FILE_BOTTOM'},
        keymap_bindings=(KeymapBinding(
            'Text', 'TEXT_EDITOR', 'DOWN_ARROW', ctrl=True),),
    ),
    OperatorAction(
        operator='text.move',
        props={'type': 'FILE_BOTTOM'},
        keymap_bindings=(KeymapBinding(
            'Text', 'TEXT_EDITOR', 'DOWN_ARROW', oskey=True),),
    ),
    OperatorAction(
        operator='text.move',
        props={'type': 'FILE_TOP'},
        keymap_bindings=(KeymapBinding(
            'Text', 'TEXT_EDITOR', 'UP_ARROW', ctrl=True),),
    ),
    OperatorAction(
        operator='text.move',
        props={'type': 'FILE_TOP'},
        keymap_bindings=(KeymapBinding(
            'Text', 'TEXT_EDITOR', 'UP_ARROW', oskey=True),),
    ),
    OperatorAction(
        operator='wm.context_toggle',
        props={'data_path': 'space_data.show_region_ui'},
        keymap_bindings=(KeymapBinding(
            'Text Generic', 'TEXT_EDITOR', 'I', ctrl=True),),
    ),
    OperatorAction(
        operator='wm.context_toggle',
        props={'data_path': 'space_data.show_region_ui'},
        keymap_bindings=(KeymapBinding(
            'Text Generic', 'TEXT_EDITOR', 'I', oskey=True),),
    ),
    OperatorAction(
        operator='nla.view_selected',
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'WHEELRIGHTMOUSE', shift=True, alt=True),),
    ),
    OperatorAction(
        operator='nla.view_all',
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'WHEELLEFTMOUSE', shift=True, alt=True),),
    ),
    OperatorAction(
        operator='nla.view_selected',
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'WHEELUPMOUSE', shift=True, alt=True),),
    ),
    OperatorAction(
        operator='nla.view_all',
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'WHEELDOWNMOUSE', shift=True, alt=True),),
    ),
    OperatorAction(
        operator='marker.rename',
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'RET'),),
    ),
    OperatorAction(
        operator='transform.transform',
        props={'mode': 'TIME_SCALE'},
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'R'),),
    ),
    OperatorAction(
        operator='transform.transform',
        props={'mode': 'TRANSLATION'},
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'MIDDLEMOUSE', value='CLICK_DRAG'),),
    ),
    OperatorAction(
        operator='transform.transform',
        props={'mode': 'TRANSLATION'},
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'W'),),
    ),
    OperatorAction(
        operator='nla.delete',
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'BACK_SPACE'),),
    ),
    OperatorAction(
        operator='nla.duplicate',
        props={'linked': True},
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'D', ctrl=True, alt=True),),
    ),
    OperatorAction(
        operator='nla.duplicate',
        props={'linked': True},
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'D', alt=True, oskey=True),),
    ),
    OperatorAction(
        operator='nla.duplicate',
        props={'linked': False},
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'D', ctrl=True),),
    ),
    OperatorAction(
        operator='nla.duplicate',
        props={'linked': False},
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'D', oskey=True),),
    ),
    OperatorAction(
        operator='nla.view_selected',
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'F'),),
    ),
    OperatorAction(
        operator='nla.select_box',
        props={'axis_range': True},
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'Q', alt=True),),
    ),
    OperatorAction(
        operator='nla.select_box',
        props={'axis_range': False},
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'Q'),),
    ),
    OperatorAction(
        operator='nla.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'A', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='nla.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'A', shift=True, oskey=True),),
    ),
    OperatorAction(
        operator='nla.select_leftright',
        props={'mode': 'CHECK', 'extend': True},
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'LEFTMOUSE', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='nla.select_leftright',
        props={'mode': 'CHECK', 'extend': True},
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'LEFTMOUSE', shift=True, oskey=True),),
    ),
    OperatorAction(
        operator='nla.tracks_delete',
        keymap_bindings=(KeymapBinding(
            'NLA Tracks', 'NLA_EDITOR', 'BACK_SPACE'),),
    ),
    OperatorAction(
        operator='nla.tweakmode_exit',
        keymap_bindings=(KeymapBinding(
            'NLA Generic', 'NLA_EDITOR', 'ESC'),),
    ),
    OperatorAction(
        operator='nla.tweakmode_enter',
        keymap_bindings=(KeymapBinding(
            'NLA Generic', 'NLA_EDITOR', 'LEFTMOUSE', value='DOUBLE_CLICK'),),
    ),
    OperatorAction(
        operator='screen.frame_jump',
        props={'end': False},
        keymap_bindings=(KeymapBinding(
            'NLA Generic', 'NLA_EDITOR', 'LEFT_ARROW', ctrl=True),),
    ),
    OperatorAction(
        operator='screen.frame_jump',
        props={'end': False},
        keymap_bindings=(KeymapBinding(
            'NLA Generic', 'NLA_EDITOR', 'LEFT_ARROW', oskey=True),),
    ),
    OperatorAction(
        operator='screen.frame_jump',
        props={'end': True},
        keymap_bindings=(KeymapBinding(
            'NLA Generic', 'NLA_EDITOR', 'RIGHT_ARROW', ctrl=True),),
    ),
    OperatorAction(
        operator='screen.frame_jump',
        props={'end': True},
        keymap_bindings=(KeymapBinding(
            'NLA Generic', 'NLA_EDITOR', 'RIGHT_ARROW', oskey=True),),
    ),
    OperatorAction(
        operator='screen.frame_offset',
        props={'delta': 1},
        keymap_bindings=(KeymapBinding(
            'NLA Generic', 'NLA_EDITOR', 'RIGHT_ARROW'),),
    ),
    OperatorAction(
        operator='screen.frame_offset',
        props={'delta': -1},
        keymap_bindings=(KeymapBinding(
            'NLA Generic', 'NLA_EDITOR', 'LEFT_ARROW'),),
    ),
    OperatorAction(
        operator='wm.call_panel',
        props={'name': 'TOPBAR_PT_name', 'keep_open': False},
        keymap_bindings=(KeymapBinding(
            'NLA Generic', 'NLA_EDITOR', 'RET'),),
    ),
    OperatorAction(
        operator='file.view_selected',
        keymap_bindings=(KeymapBinding(
            'File Browser Main', 'FILE_BROWSER', 'F'),),
    ),
    OperatorAction(
        operator='file.select_box',
        keymap_bindings=(KeymapBinding(
            'File Browser Main', 'FILE_BROWSER', 'Q'),),
    ),
    OperatorAction(
        operator='file.select_all',
        keymap_bindings=(KeymapBinding(
            'File Browser Main', 'FILE_BROWSER', 'A', ctrl=True),),
    ),
    OperatorAction(
        operator='file.select_all',
        keymap_bindings=(KeymapBinding(
            'File Browser Main', 'FILE_BROWSER', 'A', oskey=True),),
    ),
    OperatorAction(
        operator='file.select',
        props={'extend': True, 'fill': True, 'open': False},
        keymap_bindings=(KeymapBinding(
            'File Browser Main', 'FILE_BROWSER', 'RIGHTMOUSE', value='CLICK', alt=True),),
    ),
    OperatorAction(
        operator='file.select',
        props={'extend': True, 'open': False},
        keymap_bindings=(KeymapBinding(
            'File Browser Main', 'FILE_BROWSER', 'RIGHTMOUSE', value='CLICK', shift=True),),
    ),
    OperatorAction(
        operator='file.select',
        props={'open': False, 'deselect_all': True},
        keymap_bindings=(KeymapBinding(
            'File Browser Main', 'FILE_BROWSER', 'LEFTMOUSE', value='CLICK'),),
    ),
    OperatorAction(
        operator='file.refresh',
        keymap_bindings=(KeymapBinding(
            'File Browser Main', 'FILE_BROWSER', 'R', ctrl=True),),
    ),
    OperatorAction(
        operator='file.refresh',
        keymap_bindings=(KeymapBinding(
            'File Browser Main', 'FILE_BROWSER', 'R', oskey=True),),
    ),
    OperatorAction(
        operator='file.refresh',
        keymap_bindings=(KeymapBinding(
            'File Browser', 'FILE_BROWSER', 'R', ctrl=True),),
    ),
    OperatorAction(
        operator='file.refresh',
        keymap_bindings=(KeymapBinding(
            'File Browser', 'FILE_BROWSER', 'R', oskey=True),),
    ),
    OperatorAction(
        operator='file.next',
        keymap_bindings=(KeymapBinding(
            'File Browser', 'FILE_BROWSER', 'RIGHT_ARROW', ctrl=True),),
    ),
    OperatorAction(
        operator='file.next',
        keymap_bindings=(KeymapBinding(
            'File Browser', 'FILE_BROWSER', 'RIGHT_ARROW', oskey=True),),
    ),
    OperatorAction(
        operator='file.previous',
        keymap_bindings=(KeymapBinding(
            'File Browser', 'FILE_BROWSER', 'LEFT_ARROW', ctrl=True),),
    ),
    OperatorAction(
        operator='file.previous',
        keymap_bindings=(KeymapBinding(
            'File Browser', 'FILE_BROWSER', 'LEFT_ARROW', oskey=True),),
    ),
    OperatorAction(
        operator='file.parent',
        keymap_bindings=(KeymapBinding(
            'File Browser', 'FILE_BROWSER', 'UP_ARROW', ctrl=True),),
    ),
    OperatorAction(
        operator='file.parent',
        keymap_bindings=(KeymapBinding(
            'File Browser', 'FILE_BROWSER', 'UP_ARROW', oskey=True),),
    ),
    OperatorAction(
        operator='info.report_delete',
        keymap_bindings=(KeymapBinding(
            'Info', 'INFO', 'BACK_SPACE'),),
    ),
    OperatorAction(
        operator='info.select_box',
        keymap_bindings=(KeymapBinding(
            'Info', 'INFO', 'Q'),),
    ),
    OperatorAction(
        operator='info.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Info', 'INFO', 'A', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='info.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Info', 'INFO', 'A', shift=True, oskey=True),),
    ),
    OperatorAction(
        operator='info.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Info', 'INFO', 'A', ctrl=True),),
    ),
    OperatorAction(
        operator='info.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Info', 'INFO', 'A', oskey=True),),
    ),
    OperatorAction(
        operator='info.select_pick',
        props={'extend': True},
        keymap_bindings=(KeymapBinding(
            'Info', 'INFO', 'LEFTMOUSE', shift=True),),
    ),
    OperatorAction(
        operator='info.select_pick',
        keymap_bindings=(KeymapBinding(
            'Info', 'INFO', 'LEFTMOUSE'),),
    ),
    OperatorAction(
        operator='wm.search_menu',
        keymap_bindings=(KeymapBinding(
            'Info', 'INFO', 'TAB'),),
    ),
    OperatorAction(
        operator='wm.call_panel',
        props={'name': 'TOPBAR_PT_name', 'keep_open': False},
        keymap_bindings=(KeymapBinding(
            'Info', 'INFO', 'RET'),),
    ),
    OperatorAction(
        operator='node.join',
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'F', shift=True),),
    ),
    OperatorAction(
        operator='node.detach',
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'F', alt=True, repeat=True),),
    ),
    OperatorAction(
        operator='wm.call_menu',
        props={'name': 'NODE_MT_add'},
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'SPACE'),),
    ),
    OperatorAction(
        operator='node.clear_viewer_border',
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'Z', alt=True),),
    ),
    OperatorAction(
        operator='node.group_edit',
        props={'exit': True},
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'ESC'),),
    ),
    OperatorAction(
        operator='node.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'A', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='node.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'A', shift=True, oskey=True),),
    ),
    OperatorAction(
        operator='node.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'A', ctrl=True),),
    ),
    OperatorAction(
        operator='node.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'A', oskey=True),),
    ),
    OperatorAction(
        operator='node.delete_reconnect',
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'BACK_SPACE', ctrl=True),),
    ),
    OperatorAction(
        operator='node.delete_reconnect',
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'BACK_SPACE', oskey=True),),
    ),
    OperatorAction(
        operator='node.join',
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'J', ctrl=True),),
    ),
    OperatorAction(
        operator='node.join',
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'J', oskey=True),),
    ),
    OperatorAction(
        operator='node.select',
        props={'extend': True},
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'LEFTMOUSE', shift=True, ctrl=True, alt=True),),
    ),
    OperatorAction(
        operator='node.select',
        props={'extend': True},
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'LEFTMOUSE', shift=True, alt=True, oskey=True),),
    ),
    OperatorAction(
        operator='node.select',
        props={'extend': True},
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'LEFTMOUSE', shift=True),),
    ),
    OperatorAction(
        operator='node.select',
        props={'extend': False},
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'LEFTMOUSE', ctrl=True, alt=True),),
    ),
    OperatorAction(
        operator='node.select',
        props={'extend': False},
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'LEFTMOUSE', alt=True, oskey=True),),
    ),
    OperatorAction(
        operator='node.select',
        props={'extend': False},
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'LEFTMOUSE', alt=True),),
    ),
    OperatorAction(
        operator='node.select',
        props={'extend': False},
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'LEFTMOUSE', ctrl=True),),
    ),
    OperatorAction(
        operator='node.select',
        props={'extend': False},
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'LEFTMOUSE', oskey=True),),
    ),
    OperatorAction(
        operator='node.select',
        props={'extend': False, 'deselect_all': True, 'select_passthrough': True},
        keymap_bindings=(KeymapBinding(
            'Node Editor', 'NODE_EDITOR', 'LEFTMOUSE'),),
    ),
    OperatorAction(
        operator='wm.call_panel',
        props={'name': 'TOPBAR_PT_name', 'keep_open': False},
        keymap_bindings=(KeymapBinding(
            'Node Generic', 'NODE_EDITOR', 'RET'),),
    ),
    OperatorAction(
        operator='wm.tool_set_by_id',
        props={'name': 'builtin.sample', 'cycle': True},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'I'),),
    ),
    OperatorAction(
        operator='wm.tool_set_by_id',
        props={'name': 'builtin.annotate', 'cycle': True},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'D'),),
    ),
    OperatorAction(
        operator='wm.tool_set_by_id',
        props={'name': 'builtin.cursor', 'cycle': True},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'C'),),
    ),
    OperatorAction(
        operator='image.curves_point_set',
        props={'point': 'WHITE_POINT'},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'LEFTMOUSE', shift=True),),
    ),
    OperatorAction(
        operator='image.curves_point_set',
        props={'point': 'BLACK_POINT'},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'LEFTMOUSE', ctrl=True),),
    ),
    OperatorAction(
        operator='image.curves_point_set',
        props={'point': 'BLACK_POINT'},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'LEFTMOUSE', oskey=True),),
    ),
    OperatorAction(
        operator='image.view_zoom_ratio',
        props={'ratio': 0.125},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'F4'),),
    ),
    OperatorAction(
        operator='image.view_zoom_ratio',
        props={'ratio': 0.25},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'F3'),),
    ),
    OperatorAction(
        operator='image.view_zoom_ratio',
        props={'ratio': 0.5},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'F2'),),
    ),
    OperatorAction(
        operator='image.view_zoom_ratio',
        props={'ratio': 1.0},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'F1'),),
    ),
    OperatorAction(
        operator='image.view_zoom_ratio',
        props={'ratio': 2.0},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'F2', shift=True),),
    ),
    OperatorAction(
        operator='image.view_zoom_ratio',
        props={'ratio': 4.0},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'F3', shift=True),),
    ),
    OperatorAction(
        operator='image.view_zoom_ratio',
        props={'ratio': 8.0},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'F4', shift=True),),
    ),
    OperatorAction(
        operator='image.view_zoom_ratio',
        props={'ratio': 2.0},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'F2', ctrl=True),),
    ),
    OperatorAction(
        operator='image.view_zoom_ratio',
        props={'ratio': 2.0},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'F2', oskey=True),),
    ),
    OperatorAction(
        operator='image.view_zoom_ratio',
        props={'ratio': 4.0},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'F3', ctrl=True),),
    ),
    OperatorAction(
        operator='image.view_zoom_ratio',
        props={'ratio': 4.0},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'F3', oskey=True),),
    ),
    OperatorAction(
        operator='image.view_zoom_ratio',
        props={'ratio': 8.0},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'F4', ctrl=True),),
    ),
    OperatorAction(
        operator='image.view_zoom_ratio',
        props={'ratio': 8.0},
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'F4', oskey=True),),
    ),
    OperatorAction(
        operator='image.view_zoom_border',
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'Z'),),
    ),
    OperatorAction(
        operator='image.view_zoom_out',
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'WHEELOUTMOUSE', alt=True),),
    ),
    OperatorAction(
        operator='image.view_zoom_in',
        keymap_bindings=(KeymapBinding(
            'Image', 'IMAGE_EDITOR', 'WHEELINMOUSE', alt=True),),
    ),
    OperatorAction(
        operator='wm.search_menu',
        keymap_bindings=(KeymapBinding(
            'Image Generic', 'IMAGE_EDITOR', 'SPACE', repeat=True),),
    ),
    OperatorAction(
        operator='wm.search_menu',
        keymap_bindings=(KeymapBinding(
            'Image Generic', 'IMAGE_EDITOR', 'TAB'),),
    ),
    OperatorAction(
        operator='wm.call_panel',
        props={'name': 'TOPBAR_PT_name', 'keep_open': False},
        keymap_bindings=(KeymapBinding(
            'Image Generic', 'IMAGE_EDITOR', 'RET'),),
    ),
    OperatorAction(
        operator='marker.rename',
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'RET'),),
    ),
    OperatorAction(
        operator='transform.transform',
        props={'mode': 'TIME_EXTEND'},
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'Y'),),
    ),
    OperatorAction(
        operator='transform.translate',
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'MIDDLEMOUSE', value='CLICK_DRAG'),),
    ),
    OperatorAction(
        operator='anim.channels_editable_toggle',
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'LEFTMOUSE', value='DOUBLE_CLICK'),),
    ),
    OperatorAction(
        operator='graph.view_frame',
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'A', shift=True),),
    ),
    OperatorAction(
        operator='graph.view_selected',
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'F'),),
    ),
    OperatorAction(
        operator='wm.call_menu',
        props={'name': 'GRAPH_MT_delete'},
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'BACK_SPACE'),),
    ),
    OperatorAction(
        operator='graph.select_less',
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'DOWN_ARROW', repeat=True),),
    ),
    OperatorAction(
        operator='graph.select_more',
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'UP_ARROW', repeat=True),),
    ),
    OperatorAction(
        operator='graph.select_box',
        props={'axis_range': True},
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'Q', alt=True),),
    ),
    OperatorAction(
        operator='graph.select_box',
        props={'axis_range': False},
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'Q'),),
    ),
    OperatorAction(
        operator='graph.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'A', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='graph.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'A', shift=True, oskey=True),),
    ),
    OperatorAction(
        operator='graph.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'A', ctrl=True),),
    ),
    OperatorAction(
        operator='graph.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'A', oskey=True),),
    ),
    OperatorAction(
        operator='graph.select_leftright',
        props={'mode': 'CHECK', 'extend': True},
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'LEFTMOUSE', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='graph.select_leftright',
        props={'mode': 'CHECK', 'extend': True},
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'LEFTMOUSE', shift=True, oskey=True),),
    ),
    OperatorAction(
        operator='graph.cursor_set',
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'RIGHTMOUSE', oskey=True),),
    ),
    OperatorAction(
        operator='screen.frame_jump',
        props={'end': False},
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'LEFT_ARROW', ctrl=True),),
    ),
    OperatorAction(
        operator='screen.frame_jump',
        props={'end': False},
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'LEFT_ARROW', oskey=True),),
    ),
    OperatorAction(
        operator='screen.frame_jump',
        props={'end': True},
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'RIGHT_ARROW', ctrl=True),),
    ),
    OperatorAction(
        operator='screen.frame_jump',
        props={'end': True},
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'RIGHT_ARROW', oskey=True),),
    ),
    OperatorAction(
        operator='screen.frame_offset',
        props={'delta': 1},
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'RIGHT_ARROW'),),
    ),
    OperatorAction(
        operator='screen.frame_offset',
        props={'delta': -1},
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'LEFT_ARROW'),),
    ),
    OperatorAction(
        operator='graph.hide',
        props={'unselected': False},
        keymap_bindings=(KeymapBinding(
            'Graph Editor Generic', 'GRAPH_EDITOR', 'H', ctrl=True),),
    ),
    OperatorAction(
        operator='wm.call_panel',
        props={'name': 'TOPBAR_PT_name', 'keep_open': False},
        keymap_bindings=(KeymapBinding(
            'Graph Editor Generic', 'GRAPH_EDITOR', 'RET'),),
    ),
    OperatorAction(
        operator='mask.select_less',
        keymap_bindings=(KeymapBinding(
            'Mask Editing', 'EMPTY', 'LEFT_BRACKET', repeat=True),),
    ),
    OperatorAction(
        operator='mask.select_more',
        keymap_bindings=(KeymapBinding(
            'Mask Editing', 'EMPTY', 'RIGHT_BRACKET', repeat=True),),
    ),
    OperatorAction(
        operator='mask.parent_clear',
        keymap_bindings=(KeymapBinding(
            'Mask Editing', 'EMPTY', 'P', shift=True),),
    ),
    OperatorAction(
        operator='mask.hide_view_set',
        props={'unselected': False},
        keymap_bindings=(KeymapBinding(
            'Mask Editing', 'EMPTY', 'H', ctrl=True),),
    ),
    OperatorAction(
        operator='mask.select_less',
        keymap_bindings=(KeymapBinding(
            'Mask Editing', 'EMPTY', 'DOWN_ARROW', repeat=True),),
    ),
    OperatorAction(
        operator='mask.select_more',
        keymap_bindings=(KeymapBinding(
            'Mask Editing', 'EMPTY', 'UP_ARROW', repeat=True),),
    ),
    OperatorAction(
        operator='mask.select_box',
        keymap_bindings=(KeymapBinding(
            'Mask Editing', 'EMPTY', 'Q'),),
    ),
    OperatorAction(
        operator='mask.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Mask Editing', 'EMPTY', 'A', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='mask.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Mask Editing', 'EMPTY', 'A', shift=True, oskey=True),),
    ),
    OperatorAction(
        operator='mask.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Mask Editing', 'EMPTY', 'A', ctrl=True),),
    ),
    OperatorAction(
        operator='mask.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Mask Editing', 'EMPTY', 'A', oskey=True),),
    ),
    OperatorAction(
        operator='mask.delete',
        keymap_bindings=(KeymapBinding(
            'Mask Editing', 'EMPTY', 'BACK_SPACE'),),
    ),
    OperatorAction(
        operator='wm.search_menu',
        keymap_bindings=(KeymapBinding(
            'Mask Editing', 'EMPTY', 'TAB'),),
    ),
    OperatorAction(
        operator='wm.context_menu_enum',
        props={'data_path': 'tool_settings.snap_uv_element'},
        keymap_bindings=(KeymapBinding(
            'UV Editor', 'EMPTY', 'X', shift=True, repeat=True),),
    ),
    OperatorAction(
        operator='uv.select_circle',
        props={'wait_for_input': False},
        keymap_bindings=(KeymapBinding(
            'UV Editor', 'EMPTY', 'MIDDLEMOUSE', active=False),),
    ),
    OperatorAction(
        operator='wm.context_toggle',
        props={'data_path': 'tool_settings.use_snap'},
        keymap_bindings=(KeymapBinding(
            'UV Editor', 'EMPTY', 'X'),),
    ),
    OperatorAction(
        operator='wm.call_menu',
        props={'name': 'IMAGE_MT_uvs_context_menu'},
        keymap_bindings=(KeymapBinding(
            'UV Editor', 'EMPTY', 'RIGHTMOUSE', value='CLICK'),),
    ),
    OperatorAction(
        operator='wm.search_menu',
        keymap_bindings=(KeymapBinding(
            'UV Editor', 'EMPTY', 'TAB'),),
    ),
    OperatorAction(
        operator='wm.call_panel',
        props={'name': 'TOPBAR_PT_name', 'keep_open': False},
        keymap_bindings=(KeymapBinding(
            'UV Editor', 'EMPTY', 'RET'),),
    ),
    OperatorAction(
        operator='anim.channels_delete',
        keymap_bindings=(KeymapBinding(
            'Animation Channels', 'EMPTY', 'D', alt=True),),
    ),
    OperatorAction(
        operator='anim.channels_collapse',
        keymap_bindings=(KeymapBinding(
            'Animation Channels', 'EMPTY', 'LEFT_ARROW'),),
    ),
    OperatorAction(
        operator='anim.channels_expand',
        keymap_bindings=(KeymapBinding(
            'Animation Channels', 'EMPTY', 'RIGHT_ARROW'),),
    ),
    OperatorAction(
        operator='anim.channels_delete',
        keymap_bindings=(KeymapBinding(
            'Animation Channels', 'EMPTY', 'BACK_SPACE'),),
    ),
    OperatorAction(
        operator='anim.channels_select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Animation Channels', 'EMPTY', 'A', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='anim.channels_select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Animation Channels', 'EMPTY', 'A', shift=True, oskey=True),),
    ),
    OperatorAction(
        operator='anim.channels_select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Animation Channels', 'EMPTY', 'A', ctrl=True),),
    ),
    OperatorAction(
        operator='anim.channels_select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Animation Channels', 'EMPTY', 'A', oskey=True),),
    ),
    OperatorAction(
        operator='anim.channels_rename',
        keymap_bindings=(KeymapBinding(
            'Animation Channels', 'EMPTY', 'RET'),),
    ),
    OperatorAction(
        operator='anim.channels_click',
        props={'extend': True},
        keymap_bindings=(KeymapBinding(
            'Animation Channels', 'EMPTY', 'LEFTMOUSE', shift=True),),
    ),
    OperatorAction(
        operator='paint.weight_sample_group',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Paint Weight, Sample Vertex Group', 'VIEW_3D', 'MIDDLEMOUSE'),),
    ),
    OperatorAction(
        operator='paint.weight_sample',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Paint Weight, Sample Weight', 'VIEW_3D', 'MIDDLEMOUSE'),),
    ),
    OperatorAction(
        operator='paint.weight_gradient',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Paint Weight, Gradient', 'VIEW_3D', 'MIDDLEMOUSE'),),
    ),
    OperatorAction(
        operator='curve.vertex_add',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Edit Curve, Extrude to Cursor', 'VIEW_3D', 'MIDDLEMOUSE'),),
    ),
    OperatorAction(
        operator='armature.click_extrude',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Edit Armature, Extrude to Cursor', 'VIEW_3D', 'MIDDLEMOUSE'),),
    ),
    OperatorAction(
        operator='pose.relax',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Pose, Relax', 'VIEW_3D', 'MIDDLEMOUSE'),),
    ),
    OperatorAction(
        operator='pose.push',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Pose, Push', 'VIEW_3D', 'MIDDLEMOUSE'),),
    ),
    OperatorAction(
        operator='pose.breakdown',
        keymap_bindings=(KeymapBinding(
            '3D View Tool: Pose, Breakdowner', 'VIEW_3D', 'MIDDLEMOUSE'),),
    ),
    OperatorAction(
        operator='view3d.snap_cursor_to_center',
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'WHEELLEFTMOUSE', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='view3d.snap_cursor_to_selected',
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'WHEELRIGHTMOUSE', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='wm.call_panel',
        props={'name': 'VIEW3D_PT_snapping'},
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'X', shift=True, repeat=True),),
    ),
    OperatorAction(
        operator='view3d.snap_cursor_to_center',
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'WHEELDOWNMOUSE', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='view3d.snap_cursor_to_selected',
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'WHEELUPMOUSE', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='wm.search_menu',
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'SPACE'),),
    ),
    OperatorAction(
        operator='wm.call_menu',
        props={'name': 'VIEW3D_MT_add'},
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'A', value='RELEASE', shift=True),),
    ),
    OperatorAction(
        operator='wm.context_toggle',
        props={'data_path': 'tool_settings.use_snap'},
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'X'),),
    ),
    OperatorAction(
        operator='view3d.view_orbit',
        props={'angle': 3.1415927410125732, 'type': 'ORBITRIGHT'},
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'F5', repeat=True, active=False),),
    ),
    OperatorAction(
        operator='view3d.view_axis',
        props={'type': 'TOP'},
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'F3', repeat=True, active=False),),
    ),
    OperatorAction(
        operator='view3d.view_axis',
        props={'type': 'RIGHT'},
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'F2', repeat=True, active=False),),
    ),
    OperatorAction(
        operator='view3d.view_axis',
        props={'type': 'FRONT'},
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'F1', repeat=True, active=False),),
    ),
    OperatorAction(
        operator='view3d.view_camera',
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'F4', repeat=True, active=False),),
    ),
    OperatorAction(
        operator='view3d.view_all',
        props={'use_all_regions': True, 'center': False},
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'A', shift=True, repeat=True, active=False),),
    ),
    OperatorAction(
        operator='wm.search_menu',
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'TAB', repeat=True, active=False),),
    ),
    OperatorAction(
        operator='wm.call_panel',
        props={'name': 'TOPBAR_PT_name', 'keep_open': False},
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'RET'),),
    ),
    OperatorAction(
        operator='wm.call_menu',
        props={'name': 'VIEW3D_MT_edit_font_context_menu'},
        keymap_bindings=(KeymapBinding(
            'Font', 'EMPTY', 'RIGHTMOUSE', value='CLICK'),),
    ),
    OperatorAction(
        operator='particle.select_less',
        keymap_bindings=(KeymapBinding(
            'Particle', 'EMPTY', 'LEFT_BRACKET', repeat=True),),
    ),
    OperatorAction(
        operator='particle.select_more',
        keymap_bindings=(KeymapBinding(
            'Particle', 'EMPTY', 'RIGHT_BRACKET', repeat=True),),
    ),
    OperatorAction(
        operator='wm.context_toggle',
        props={'data_path': 'tool_settings.use_proportional_edit'},
        keymap_bindings=(KeymapBinding(
            'Particle', 'EMPTY', 'B'),),
    ),
    OperatorAction(
        operator='wm.radial_control',
        props={'data_path_primary': 'tool_settings.particle_edit.brush.strength'},
        keymap_bindings=(KeymapBinding(
            'Particle', 'EMPTY', 'U', shift=True),),
    ),
    OperatorAction(
        operator='particle.hide',
        props={'unselected': False},
        keymap_bindings=(KeymapBinding(
            'Particle', 'EMPTY', 'H', ctrl=True),),
    ),
    OperatorAction(
        operator='particle.delete',
        keymap_bindings=(KeymapBinding(
            'Particle', 'EMPTY', 'BACK_SPACE'),),
    ),
    OperatorAction(
        operator='particle.select_linked',
        keymap_bindings=(KeymapBinding(
            'Particle', 'EMPTY', 'RIGHT_BRACKET', ctrl=True),),
    ),
    OperatorAction(
        operator='particle.select_linked',
        keymap_bindings=(KeymapBinding(
            'Particle', 'EMPTY', 'RIGHT_BRACKET', oskey=True),),
    ),
    OperatorAction(
        operator='particle.select_linked_pick',
        props={'deselect': True},
        keymap_bindings=(KeymapBinding(
            'Particle', 'EMPTY', 'RIGHT_BRACKET', shift=True),),
    ),
    OperatorAction(
        operator='particle.select_linked_pick',
        props={'deselect': False},
        keymap_bindings=(KeymapBinding(
            'Particle', 'EMPTY', 'RIGHT_BRACKET'),),
    ),
    OperatorAction(
        operator='particle.select_less',
        keymap_bindings=(KeymapBinding(
            'Particle', 'EMPTY', 'DOWN_ARROW', repeat=True),),
    ),
    OperatorAction(
        operator='particle.select_more',
        keymap_bindings=(KeymapBinding(
            'Particle', 'EMPTY', 'UP_ARROW', repeat=True),),
    ),
    OperatorAction(
        operator='particle.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Particle', 'EMPTY', 'A', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='particle.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Particle', 'EMPTY', 'A', shift=True, oskey=True),),
    ),
    OperatorAction(
        operator='particle.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Particle', 'EMPTY', 'A', ctrl=True),),
    ),
    OperatorAction(
        operator='particle.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Particle', 'EMPTY', 'A', oskey=True),),
    ),
    OperatorAction(
        operator='wm.call_menu',
        props={'name': 'VIEW3D_MT_angle_control'},
        keymap_bindings=(KeymapBinding(
            'Image Paint', 'EMPTY', 'R'),),
    ),
    OperatorAction(
        operator='wm.context_toggle',
        props={'data_path': 'image_paint_object.data.use_paint_mask'},
        keymap_bindings=(KeymapBinding(
            'Image Paint', 'EMPTY', 'M'),),
    ),
    OperatorAction(
        operator='brush.stencil_control',
        props={'mode': 'ROTATION'},
        keymap_bindings=(KeymapBinding(
            'Image Paint', 'EMPTY', 'RIGHTMOUSE', value='CLICK', ctrl=True),),
    ),
    OperatorAction(
        operator='brush.stencil_control',
        props={'mode': 'TRANSLATION'},
        keymap_bindings=(KeymapBinding(
            'Image Paint', 'EMPTY', 'RIGHTMOUSE', value='RELEASE'),),
    ),
    OperatorAction(
        operator='wm.radial_control',
        props={'data_path_primary': 'tool_settings.image_paint.brush.strength',
               'data_path_secondary': 'tool_settings.unified_paint_settings.strength',
               'use_secondary': 'tool_settings.unified_paint_settings.use_unified_strength',
               'rotation_path': 'tool_settings.image_paint.brush.mask_texture_slot.angle',
               'color_path': 'tool_settings.image_paint.brush.cursor_color_add',
               'fill_color_path': 'tool_settings.image_paint.brush.color',
               'fill_color_override_path': 'tool_settings.unified_paint_settings.color',
               'fill_color_override_test_path': 'tool_settings.unified_paint_settings.use_unified_color',
               'zoom_path': '',
               'image_id': 'tool_settings.image_paint.brush',
               'secondary_tex': True},
        keymap_bindings=(KeymapBinding(
            'Image Paint', 'EMPTY', 'U'),),
    ),
    OperatorAction(
        operator='wm.radial_control',
        props={'data_path_primary': 'tool_settings.image_paint.brush.size',
               'data_path_secondary': 'tool_settings.unified_paint_settings.size',
               'use_secondary': 'tool_settings.unified_paint_settings.use_unified_size',
               'rotation_path': 'tool_settings.image_paint.brush.mask_texture_slot.angle',
               'color_path': 'tool_settings.image_paint.brush.cursor_color_add',
               'fill_color_path': 'tool_settings.image_paint.brush.color',
               'fill_color_override_path': 'tool_settings.unified_paint_settings.color',
               'fill_color_override_test_path': 'tool_settings.unified_paint_settings.use_unified_color',
               'zoom_path': 'space_data.zoom',
               'image_id': 'tool_settings.image_paint.brush',
               'secondary_tex': True},
        keymap_bindings=(KeymapBinding(
            'Image Paint', 'EMPTY', 'S'),),
    ),
    OperatorAction(
        operator='paint.grab_clone',
        keymap_bindings=(KeymapBinding(
            'Image Paint', 'EMPTY', 'MIDDLEMOUSE'),),
    ),
    OperatorAction(
        operator='paint.sample_color',
        keymap_bindings=(KeymapBinding(
            'Image Paint', 'EMPTY', 'I'),),
    ),
    OperatorAction(
        operator='wm.call_menu',
        props={'name': 'VIEW3D_MT_edit_curves_context_menu'},
        keymap_bindings=(KeymapBinding(
            'Curves', 'EMPTY', 'RIGHTMOUSE', value='CLICK'),),
    ),
    OperatorAction(
        operator='wm.call_panel',
        props={'name': 'VIEW3D_PT_paint_vertex_context_menu'},
        keymap_bindings=(KeymapBinding(
            'Vertex Paint', 'EMPTY', 'RIGHTMOUSE', value='CLICK'),),
    ),
    OperatorAction(
        operator='wm.call_menu',
        props={'name': 'VIEW3D_MT_angle_control'},
        keymap_bindings=(KeymapBinding(
            'Vertex Paint', 'EMPTY', 'R'),),
    ),
    OperatorAction(
        operator='wm.context_toggle',
        props={'data_path': 'vertex_paint_object.data.use_paint_mask'},
        keymap_bindings=(KeymapBinding(
            'Vertex Paint', 'EMPTY', 'M'),),
    ),
    OperatorAction(
        operator='brush.stencil_control',
        props={'mode': 'ROTATION'},
        keymap_bindings=(KeymapBinding(
            'Vertex Paint', 'EMPTY', 'RIGHTMOUSE', value='CLICK', ctrl=True),),
    ),
    OperatorAction(
        operator='wm.radial_control',
        props={'data_path_primary': 'tool_settings.vertex_paint.brush.strength',
               'data_path_secondary': 'tool_settings.unified_paint_settings.strength',
               'use_secondary': 'tool_settings.unified_paint_settings.use_unified_strength',
               'rotation_path': 'tool_settings.vertex_paint.brush.texture_slot.angle',
               'color_path': 'tool_settings.vertex_paint.brush.cursor_color_add',
               'fill_color_path': 'tool_settings.vertex_paint.brush.color',
               'fill_color_override_path': 'tool_settings.unified_paint_settings.color',
               'fill_color_override_test_path': 'tool_settings.unified_paint_settings.use_unified_color',
               'zoom_path': '',
               'image_id': 'tool_settings.vertex_paint.brush',
               'secondary_tex': False},
        keymap_bindings=(KeymapBinding(
            'Vertex Paint', 'EMPTY', 'U'),),
    ),
    OperatorAction(
        operator='wm.radial_control',
        props={'data_path_primary': 'tool_settings.vertex_paint.brush.size',
               'data_path_secondary': 'tool_settings.unified_paint_settings.size',
               'use_secondary': 'tool_settings.unified_paint_settings.use_unified_size',
               'rotation_path': 'tool_settings.vertex_paint.brush.texture_slot.angle',
               'color_path': 'tool_settings.vertex_paint.brush.cursor_color_add',
               'fill_color_path': 'tool_settings.vertex_paint.brush.color',
               'fill_color_override_path': 'tool_settings.unified_paint_settings.color',
               'fill_color_override_test_path': 'tool_settings.unified_paint_settings.use_unified_color',
               'zoom_path': '',
               'image_id': 'tool_settings.vertex_paint.brush',
               'secondary_tex': False},
        keymap_bindings=(KeymapBinding(
            'Vertex Paint', 'EMPTY', 'S'),),
    ),
    OperatorAction(
        operator='wm.tool_set_by_id',
        props={'name': 'builtin.sample_weight', 'cycle': True},
        keymap_bindings=(KeymapBinding(
            'Weight Paint', 'EMPTY', 'I'),),
    ),
    OperatorAction(
        operator='wm.call_panel',
        props={'name': 'VIEW3D_PT_paint_weight_context_menu'},
        keymap_bindings=(KeymapBinding(
            'Weight Paint', 'EMPTY', 'RIGHTMOUSE', value='CLICK'),),
    ),
    OperatorAction(
        operator='wm.context_toggle',
        props={'data_path': 'weight_paint_object.data.use_paint_mask'},
        keymap_bindings=(KeymapBinding(
            'Weight Paint', 'EMPTY', 'M'),),
    ),
    OperatorAction(
        operator='wm.radial_control',
        props={'data_path_primary': 'tool_settings.weight_paint.brush.strength',
               'data_path_secondary': 'tool_settings.unified_paint_settings.strength',
               'use_secondary': 'tool_settings.unified_paint_settings.use_unified_strength',
               'rotation_path': 'tool_settings.weight_paint.brush.texture_slot.angle',
               'color_path': 'tool_settings.weight_paint.brush.cursor_color_add',
               'fill_color_path': '',
               'fill_color_override_path': '',
               'fill_color_override_test_path': '',
               'zoom_path': '',
               'image_id': 'tool_settings.weight_paint.brush',
               'secondary_tex': False},
        keymap_bindings=(KeymapBinding(
            'Weight Paint', 'EMPTY', 'U'),),
    ),
    OperatorAction(
        operator='wm.radial_control',
        props={'data_path_primary': 'tool_settings.weight_paint.brush.size',
               'data_path_secondary': 'tool_settings.unified_paint_settings.size',
               'use_secondary': 'tool_settings.unified_paint_settings.use_unified_size',
               'rotation_path': 'tool_settings.weight_paint.brush.texture_slot.angle',
               'color_path': 'tool_settings.weight_paint.brush.cursor_color_add',
               'fill_color_path': '',
               'fill_color_override_path': '',
               'fill_color_override_test_path': '',
               'zoom_path': '',
               'image_id': 'tool_settings.weight_paint.brush',
               'secondary_tex': False},
        keymap_bindings=(KeymapBinding(
            'Weight Paint', 'EMPTY', 'S'),),
    ),
    OperatorAction(
        operator='paintcurve.delete_point',
        keymap_bindings=(KeymapBinding(
            'Paint Curve', 'EMPTY', 'BACK_SPACE'),),
    ),
    OperatorAction(
        operator='paint.vert_select_all',
        keymap_bindings=(KeymapBinding(
            'Paint Vertex Selection (Weight, Vertex)', 'EMPTY', 'A', ctrl=True),),
    ),
    OperatorAction(
        operator='paint.vert_select_all',
        keymap_bindings=(KeymapBinding(
            'Paint Vertex Selection (Weight, Vertex)', 'EMPTY', 'A', oskey=True),),
    ),
    OperatorAction(
        operator='paint.face_select_hide',
        props={'unselected': False},
        keymap_bindings=(KeymapBinding(
            'Paint Face Mask (Weight, Vertex, Texture)', 'EMPTY', 'H', ctrl=True),),
    ),
    OperatorAction(
        operator='paint.face_select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Paint Face Mask (Weight, Vertex, Texture)', 'EMPTY', 'A', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='paint.face_select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Paint Face Mask (Weight, Vertex, Texture)', 'EMPTY', 'A', shift=True, oskey=True),),
    ),
    OperatorAction(
        operator='paint.face_select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Paint Face Mask (Weight, Vertex, Texture)', 'EMPTY', 'A', ctrl=True),),
    ),
    OperatorAction(
        operator='paint.face_select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Paint Face Mask (Weight, Vertex, Texture)', 'EMPTY', 'A', oskey=True),),
    ),
    OperatorAction(
        operator='view3d.walk',
        keymap_bindings=(KeymapBinding(
            '3D View Generic', 'VIEW_3D', 'MIDDLEMOUSE', active=False),),
    ),
    OperatorAction(
        operator='view3d.select_circle',
        props={'mode': 'SET'},
        keymap_bindings=(KeymapBinding(
            '3D View Generic', 'VIEW_3D', 'MIDDLEMOUSE', active=False),),
    ),
    OperatorAction(
        operator='wm.context_toggle',
        props={'data_path': 'space_data.show_region_ui'},
        keymap_bindings=(KeymapBinding(
            '3D View Generic', 'VIEW_3D', 'TAB', shift=True, repeat=True),),
    ),
    OperatorAction(
        operator='wm.context_toggle',
        props={'data_path': 'space_data.show_region_ui'},
        keymap_bindings=(KeymapBinding(
            '3D View Generic', 'VIEW_3D', 'RIGHT_BRACKET', ctrl=True),),
    ),
    OperatorAction(
        operator='wm.context_toggle',
        props={'data_path': 'space_data.show_region_ui'},
        keymap_bindings=(KeymapBinding(
            '3D View Generic', 'VIEW_3D', 'RIGHT_BRACKET', oskey=True),),
    ),
    OperatorAction(
        operator='wm.context_toggle',
        props={'data_path': 'space_data.show_region_toolbar'},
        keymap_bindings=(KeymapBinding(
            '3D View Generic', 'VIEW_3D', 'LEFT_BRACKET', ctrl=True),),
    ),
    OperatorAction(
        operator='wm.context_toggle',
        props={'data_path': 'space_data.show_region_toolbar'},
        keymap_bindings=(KeymapBinding(
            '3D View Generic', 'VIEW_3D', 'LEFT_BRACKET', oskey=True),),
    ),
    OperatorAction(
        operator='wm.context_toggle',
        props={'data_path': 'space_data.show_region_ui'},
        keymap_bindings=(KeymapBinding(
            'Dopesheet Generic', 'DOPESHEET_EDITOR', 'RIGHT_BRACKET', ctrl=True),),
    ),
    OperatorAction(
        operator='wm.context_toggle',
        props={'data_path': 'space_data.show_region_ui'},
        keymap_bindings=(KeymapBinding(
            'Dopesheet Generic', 'DOPESHEET_EDITOR', 'RIGHT_BRACKET', oskey=True),),
    ),
    OperatorAction(
        operator='wm.search_menu',
        keymap_bindings=(KeymapBinding(
            'Dopesheet Generic', 'DOPESHEET_EDITOR', 'TAB'),),
    ),
    OperatorAction(
        operator='wm.call_panel',
        props={'name': 'TOPBAR_PT_name', 'keep_open': False},
        keymap_bindings=(KeymapBinding(
            'Dopesheet Generic', 'DOPESHEET_EDITOR', 'RET'),),
    ),
    OperatorAction(
        operator='screen.animation_play',
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'SPACE'),),
    ),
    OperatorAction(
        operator='marker.rename',
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'RET'),),
    ),
    OperatorAction(
        operator='transform.transform',
        props={'mode': 'TIME_TRANSLATE'},
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'MIDDLEMOUSE', value='CLICK_DRAG'),),
    ),
    OperatorAction(
        operator='transform.transform',
        props={'mode': 'TIME_TRANSLATE'},
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'W'),),
    ),
    OperatorAction(
        operator='anim.channels_editable_toggle',
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'LEFTMOUSE', value='DOUBLE_CLICK'),),
    ),
    OperatorAction(
        operator='action.view_selected',
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'F'),),
    ),
    OperatorAction(
        operator='wm.call_menu',
        props={'name': 'DOPESHEET_MT_delete'},
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'BACK_SPACE'),),
    ),
    OperatorAction(
        operator='action.select_less',
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'DOWN_ARROW', ctrl=True, repeat=True),),
    ),
    OperatorAction(
        operator='action.select_less',
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'DOWN_ARROW', oskey=True, repeat=True),),
    ),
    OperatorAction(
        operator='action.select_more',
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'UP_ARROW', ctrl=True, repeat=True),),
    ),
    OperatorAction(
        operator='action.select_more',
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'UP_ARROW', oskey=True, repeat=True),),
    ),
    OperatorAction(
        operator='action.select_box',
        props={'axis_range': True},
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'Q', alt=True),),
    ),
    OperatorAction(
        operator='action.select_box',
        props={'axis_range': False},
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'Q'),),
    ),
    OperatorAction(
        operator='action.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'A', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='action.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'A', shift=True, oskey=True),),
    ),
    OperatorAction(
        operator='action.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'A', ctrl=True),),
    ),
    OperatorAction(
        operator='action.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'A', oskey=True),),
    ),
    OperatorAction(
        operator='action.select_leftright',
        props={'mode': 'CHECK', 'extend': True},
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'LEFTMOUSE', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='action.select_leftright',
        props={'mode': 'CHECK', 'extend': True},
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'LEFTMOUSE', shift=True, oskey=True),),
    ),
    OperatorAction(
        operator='screen.frame_jump',
        props={'end': False},
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'LEFT_ARROW', ctrl=True),),
    ),
    OperatorAction(
        operator='screen.frame_jump',
        props={'end': False},
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'LEFT_ARROW', oskey=True),),
    ),
    OperatorAction(
        operator='screen.frame_jump',
        props={'end': True},
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'RIGHT_ARROW', ctrl=True),),
    ),
    OperatorAction(
        operator='screen.frame_jump',
        props={'end': True},
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'RIGHT_ARROW', oskey=True),),
    ),
    OperatorAction(
        operator='screen.frame_offset',
        props={'delta': 1},
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'RIGHT_ARROW'),),
    ),
    OperatorAction(
        operator='screen.frame_offset',
        props={'delta': -1},
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'LEFT_ARROW'),),
    ),
    OperatorAction(
        operator='marker.move',
        keymap_bindings=(KeymapBinding(
            'Markers', 'EMPTY', 'W'),),
    ),
    OperatorAction(
        operator='marker.rename',
        keymap_bindings=(KeymapBinding(
            'Markers', 'EMPTY', 'RET'),),
    ),
    OperatorAction(
        operator='marker.delete',
        keymap_bindings=(KeymapBinding(
            'Markers', 'EMPTY', 'BACK_SPACE'),),
    ),
    OperatorAction(
        operator='marker.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Markers', 'EMPTY', 'A', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='marker.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Markers', 'EMPTY', 'A', shift=True, oskey=True),),
    ),
    OperatorAction(
        operator='marker.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Markers', 'EMPTY', 'A', ctrl=True),),
    ),
    OperatorAction(
        operator='marker.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Markers', 'EMPTY', 'A', oskey=True),),
    ),
    OperatorAction(
        operator='marker.select_box',
        keymap_bindings=(KeymapBinding(
            'Markers', 'EMPTY', 'Q'),),
    ),
    OperatorAction(
        operator='marker.duplicate',
        keymap_bindings=(KeymapBinding(
            'Markers', 'EMPTY', 'D', ctrl=True),),
    ),
    OperatorAction(
        operator='marker.duplicate',
        keymap_bindings=(KeymapBinding(
            'Markers', 'EMPTY', 'D', oskey=True),),
    ),
    OperatorAction(
        operator='wm.search_menu',
        keymap_bindings=(KeymapBinding(
            'Markers', 'EMPTY', 'TAB'),),
    ),
    OperatorAction(
        operator='outliner.show_one_level',
        props={'open': False},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'WHEELRIGHTMOUSE', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='outliner.show_one_level',
        props={'open': True},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'WHEELLEFTMOUSE', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='outliner.show_one_level',
        props={'open': False},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'WHEELRIGHTMOUSE', shift=True),),
    ),
    OperatorAction(
        operator='outliner.show_active',
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'WHEELLEFTMOUSE', shift=True),),
    ),
    OperatorAction(
        operator='outliner.select_walk',
        props={'direction': 'DOWN', 'extend': True, 'toggle_all': False},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'WHEELLEFTMOUSE', shift=True, alt=True),),
    ),
    OperatorAction(
        operator='outliner.select_walk',
        props={'direction': 'UP', 'extend': True, 'toggle_all': False},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'WHEELRIGHTMOUSE', shift=True, alt=True),),
    ),
    OperatorAction(
        operator='outliner.select_walk',
        props={'direction': 'DOWN', 'extend': False, 'toggle_all': False},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'WHEELLEFTMOUSE', alt=True),),
    ),
    OperatorAction(
        operator='outliner.select_walk',
        props={'direction': 'UP', 'extend': False, 'toggle_all': False},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'WHEELRIGHTMOUSE', alt=True),),
    ),
    OperatorAction(
        operator='outliner.collection_duplicate',
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'D', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='object.duplicate',
        props={'linked': True},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'D', shift=True),),
    ),
    OperatorAction(
        operator='outliner.delete',
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'X', ctrl=True, repeat=True),),
    ),
    OperatorAction(
        operator='outliner.delete',
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'D', alt=True, repeat=True),),
    ),
    OperatorAction(
        operator='outliner.show_one_level',
        props={'open': False},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'WHEELUPMOUSE', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='outliner.show_one_level',
        props={'open': True},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'WHEELDOWNMOUSE', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='outliner.show_one_level',
        props={'open': False},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'WHEELUPMOUSE', shift=True),),
    ),
    OperatorAction(
        operator='outliner.show_active',
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'WHEELDOWNMOUSE', shift=True),),
    ),
    OperatorAction(
        operator='outliner.select_walk',
        props={'direction': 'DOWN', 'extend': True},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'WHEELDOWNMOUSE', shift=True, alt=True),),
    ),
    OperatorAction(
        operator='outliner.select_walk',
        props={'direction': 'UP', 'extend': True},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'WHEELUPMOUSE', shift=True, alt=True),),
    ),
    OperatorAction(
        operator='outliner.select_walk',
        props={'direction': 'DOWN'},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'WHEELDOWNMOUSE', alt=True),),
    ),
    OperatorAction(
        operator='outliner.select_walk',
        props={'direction': 'UP'},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'WHEELUPMOUSE', alt=True),),
    ),
    OperatorAction(
        operator='outliner.hide',
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'H', ctrl=True),),
    ),
    OperatorAction(
        operator='object.link_to_collection',
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'M', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='object.link_to_collection',
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'M', shift=True, oskey=True),),
    ),
    OperatorAction(
        operator='object.move_to_collection',
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'G', ctrl=True),),
    ),
    OperatorAction(
        operator='object.move_to_collection',
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'G', oskey=True),),
    ),
    OperatorAction(
        operator='outliner.delete',
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'BACK_SPACE'),),
    ),
    OperatorAction(
        operator='anim.keyframe_delete',
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'S', alt=True),),
    ),
    OperatorAction(
        operator='anim.keyframe_insert',
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'S'),),
    ),
    OperatorAction(
        operator='outliner.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'A', shift=True, ctrl=True),),
    ),
    OperatorAction(
        operator='outliner.select_all',
        props={'action': 'DESELECT'},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'A', shift=True, oskey=True),),
    ),
    OperatorAction(
        operator='outliner.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'A', ctrl=True),),
    ),
    OperatorAction(
        operator='outliner.select_all',
        props={'action': 'SELECT'},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'A', oskey=True),),
    ),
    OperatorAction(
        operator='outliner.show_active',
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'F'),),
    ),
    OperatorAction(
        operator='wm.search_menu',
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'TAB'),),
    ),
    OperatorAction(
        operator='outliner.item_rename',
        props={'use_active': True},
        keymap_bindings=(KeymapBinding(
            'Outliner', 'OUTLINER', 'RET'),),
    ),
    OperatorAction(
        operator='wm.call_menu',
        props={'name': 'OBJECT_MT_modifier_add'},
        keymap_bindings=(KeymapBinding(
            'Property Editor', 'PROPERTIES', 'SPACE'),),
    ),
    OperatorAction(
        operator='object.modifier_copy',
        keymap_bindings=(KeymapBinding(
            'Property Editor', 'PROPERTIES', 'D', ctrl=True),),
    ),
    OperatorAction(
        operator='object.modifier_copy',
        keymap_bindings=(KeymapBinding(
            'Property Editor', 'PROPERTIES', 'D', oskey=True),),
    ),
    OperatorAction(
        operator='object.modifier_remove',
        props={'report': True},
        keymap_bindings=(KeymapBinding(
            'Property Editor', 'PROPERTIES', 'BACK_SPACE'),),
    ),
    OperatorAction(
        operator='buttons.clear_filter',
        keymap_bindings=(KeymapBinding(
            'Property Editor', 'PROPERTIES', 'ESC'),),
    ),
    OperatorAction(
        operator='wm.search_menu',
        keymap_bindings=(KeymapBinding(
            'Property Editor', 'PROPERTIES', 'TAB'),),
    ),
    OperatorAction(
        operator='screen.animation_cancel',
        props={'restore_frame': True},
        keymap_bindings=(KeymapBinding(
            'Frames', 'EMPTY', 'SPACE', ctrl=True, repeat=True),),
    ),
    OperatorAction(
        operator='view2d.reset',
        keymap_bindings=(KeymapBinding(
            'View2D Buttons List', 'EMPTY', 'A'),),
    ),
    OperatorAction(
        operator='view2d.zoom_border',
        keymap_bindings=(KeymapBinding(
            'View2D', 'EMPTY', 'Z'),),
    ),
    OperatorAction(
        operator='view2d.zoom_in',
        keymap_bindings=(KeymapBinding(
            'View2D', 'EMPTY', 'WHEELINMOUSE', alt=True),),
    ),
    OperatorAction(
        operator='view2d.zoom_out',
        keymap_bindings=(KeymapBinding(
            'View2D', 'EMPTY', 'WHEELOUTMOUSE', alt=True),),
    ),
    OperatorAction(
        operator='anim.driver_button_remove',
        keymap_bindings=(KeymapBinding(
            'User Interface', 'EMPTY', 'D', alt=True, repeat=True, active=False),),
    ),
    OperatorAction(
        operator='anim.driver_button_add',
        keymap_bindings=(KeymapBinding(
            'User Interface', 'EMPTY', 'D'),),
    ),
    OperatorAction(
        operator='anim.keyframe_clear_button',
        keymap_bindings=(KeymapBinding(
            'User Interface', 'EMPTY', 'S', shift=True, alt=True),),
    ),
    OperatorAction(
        operator='anim.keyframe_delete_button',
        keymap_bindings=(KeymapBinding(
            'User Interface', 'EMPTY', 'S', alt=True),),
    ),
    OperatorAction(
        operator='anim.keyframe_insert_button',
        keymap_bindings=(KeymapBinding(
            'User Interface', 'EMPTY', 'S'),),
    ),
    OperatorAction(
        operator='ui.copy_data_path_button',
        props={'full_path': True},
        keymap_bindings=(KeymapBinding(
            'User Interface', 'EMPTY', 'C', ctrl=True, alt=True),),
    ),
    OperatorAction(
        operator='ui.copy_data_path_button',
        props={'full_path': True},
        keymap_bindings=(KeymapBinding(
            'User Interface', 'EMPTY', 'C', alt=True, oskey=True),),
    ),
    OperatorAction(
        operator='ui.copy_data_path_button',
        keymap_bindings=(KeymapBinding(
            'User Interface', 'EMPTY', 'C', ctrl=True),),
    ),
    OperatorAction(
        operator='ui.copy_data_path_button',
        keymap_bindings=(KeymapBinding(
            'User Interface', 'EMPTY', 'C', oskey=True),),
    ),
    OperatorAction(
        operator='render.render',
        props={'animation': True, 'use_viewport': True},
        keymap_bindings=(KeymapBinding(
            'Screen Editing', 'EMPTY', 'RET', ctrl=True, alt=True),),
    ),
    OperatorAction(
        operator='render.render',
        props={'animation': True, 'use_viewport': True},
        keymap_bindings=(KeymapBinding(
            'Screen Editing', 'EMPTY', 'RET', alt=True, oskey=True),),
    ),
    OperatorAction(
        operator='render.render',
        props={'use_viewport': True},
        keymap_bindings=(KeymapBinding(
            'Screen Editing', 'EMPTY', 'RET', ctrl=True),),
    ),
    OperatorAction(
        operator='render.render',
        props={'use_viewport': True},
        keymap_bindings=(KeymapBinding(
            'Screen Editing', 'EMPTY', 'R', ctrl=True, repeat=True),),
    ),
    OperatorAction(
        operator='render.opengl',
        props={'animation': False,
               'render_keyed_only': False,
               'sequencer': False,
               'view_context': True,
               'write_still': False},
        keymap_bindings=(KeymapBinding(
            'Screen', 'EMPTY', 'R', shift=True, alt=True, repeat=True),),
    ),
    OperatorAction(
        operator='screen.animation_play',
        props={'reverse': False, 'sync': False},
        keymap_bindings=(KeymapBinding(
            'Screen', 'EMPTY', 'SPACE', shift=True, repeat=True),),
    ),
    OperatorAction(
        operator='ed.redo',
        keymap_bindings=(KeymapBinding(
            'Screen', 'EMPTY', 'Y', ctrl=True, repeat=True),),
    ),
    OperatorAction(
        operator='ed.redo',
        keymap_bindings=(KeymapBinding(
            'Screen', 'EMPTY', 'Y', oskey=True, repeat=True),),
    ),
    OperatorAction(
        operator='ed.undo_history',
        keymap_bindings=(KeymapBinding(
            'Screen', 'EMPTY', 'Z', ctrl=True, alt=True),),
    ),
    OperatorAction(
        operator='ed.undo_history',
        keymap_bindings=(KeymapBinding(
            'Screen', 'EMPTY', 'Z', alt=True, oskey=True),),
    ),
    OperatorAction(
        operator='screen.repeat_last',
        keymap_bindings=(KeymapBinding(
            'Screen', 'EMPTY', 'G', repeat=True),),
    ),
    OperatorAction(
        operator='screen.screen_full_area',
        props={'use_hide_panels': True},
        keymap_bindings=(KeymapBinding(
            'Window', 'EMPTY', 'TAB', shift=True, ctrl=True, repeat=True),),
    ),
    OperatorAction(
        operator='wm.context_menu_enum',
        props={'data_path': 'scene.tool_settings.proportional_edit_falloff'},
        keymap_bindings=(KeymapBinding(
            'Window', 'EMPTY', 'B', shift=True, repeat=True),),
    ),
    OperatorAction(
        operator='wm.window_fullscreen_toggle',
        keymap_bindings=(KeymapBinding(
            'Window', 'EMPTY', 'F11', repeat=True),),
    ),
    OperatorAction(
        operator='wm.call_menu',
        props={'name': 'SCREEN_MT_user_menu'},
        keymap_bindings=(KeymapBinding(
            'Window', 'EMPTY', 'Q', value='DOUBLE_CLICK'),),
    ),
    OperatorAction(
        operator='wm.quit_blender',
        keymap_bindings=(KeymapBinding(
            'Window', 'EMPTY', 'Q', shift=True, ctrl=True, alt=True, repeat=True),),
    ),
)
