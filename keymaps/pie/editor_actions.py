"""Reference Blender editor pie shortcuts."""

from ...actions.operator_action import KeymapBinding, OperatorAction

# Blender prepends add-on rows during merge. Register in reverse reference order
# so the merged map retains the order of these declarations.
EDITOR_PIE_ACTIONS = (
    OperatorAction(
        operator='wm.call_menu_pie',
        props={'name': 'NLA_MT_snap_pie'},
        keymap_bindings=(KeymapBinding(
            'NLA Editor', 'NLA_EDITOR', 'X', shift=True),),
    ),
    OperatorAction(
        operator='wm.call_menu_pie',
        props={'name': 'GRAPH_MT_snap_pie'},
        keymap_bindings=(KeymapBinding(
            'Graph Editor', 'GRAPH_EDITOR', 'X', shift=True),),
    ),
    OperatorAction(
        operator='wm.call_menu_pie',
        props={'name': 'VIEW3D_MT_snap_pie'},
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'X', shift=True, alt=True),),
    ),
    OperatorAction(
        operator='wm.call_menu_pie',
        props={'name': 'VIEW3D_MT_view_pie'},
        keymap_bindings=(KeymapBinding(
            '3D View', 'VIEW_3D', 'V'),),
    ),
    OperatorAction(
        operator='wm.call_menu_pie',
        props={'name': 'DOPESHEET_MT_snap_pie'},
        keymap_bindings=(KeymapBinding(
            'Dopesheet', 'DOPESHEET_EDITOR', 'X', shift=True),),
    ),
)
