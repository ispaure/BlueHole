"""Assignments and Commands views inside Blue Hole's Keymaps preferences."""

import bpy

from . import deluxe_editor_ops as ops
from .deluxe_editor_model import (SOURCE_LABELS, STATUS_LABELS, context_label, display_value,
                                  shortcut, title)
from ....keymaps.deluxe_schema import same_value

PAGE_SIZE = 8


def find(text, query):
    return all(term in text.casefold() for term in query.casefold().split())


def paginate(layout, current, rows):
    last = max(0, (len(rows) - 1) // PAGE_SIZE)
    page = min(current.page, last)
    if last:
        bar = layout.row(align=True)
        prev = bar.row(align=True)
        prev.enabled = page > 0
        ops.operator_button(prev, 'page', 'Previous', str(page - 1), icon='TRIA_LEFT')
        bar.label(text=f'{page + 1} / {last + 1}')
        forward = bar.row(align=True)
        forward.enabled = page < last
        ops.operator_button(forward, 'page', 'Next', str(page + 1), icon='TRIA_RIGHT')
    return rows[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]


class BH_MT_deluxe_categories(bpy.types.Menu):
    bl_label = 'Category'

    def draw(self, _context):
        current = ops.editor()
        for id_, row in current.catalog['categories'].items():
            ops.operator_button(self.layout, 'category', row['label'], id_,
                                icon='CHECKMARK' if id_ == current.category else 'NONE')


class BH_MT_deluxe_sections(bpy.types.Menu):
    bl_label = 'Section'

    def draw(self, _context):
        current = ops.editor()
        for id_ in current.sections():
            row = current.catalog['sections'][id_]
            ops.operator_button(self.layout, 'section', row['label'], id_,
                                icon='CHECKMARK' if id_ == current.section else 'NONE')


class BH_MT_deluxe_command_categories(bpy.types.Menu):
    bl_label = 'Command Category'

    def draw(self, _context):
        current = ops.editor()
        ops.operator_button(self.layout, 'command_category', 'All Categories')
        for id_, row in current.catalog['categories'].items():
            ops.operator_button(self.layout, 'command_category', row['label'], id_,
                                icon='CHECKMARK' if id_ == current.command_category else 'NONE')


class BH_MT_deluxe_command_sections(bpy.types.Menu):
    bl_label = 'Command Section'

    def draw(self, _context):
        current = ops.editor()
        ops.operator_button(self.layout, 'command_section', 'All Sections')
        for id_ in current.sections(current.command_category):
            row = current.catalog['sections'][id_]
            ops.operator_button(self.layout, 'command_section', row['label'], id_,
                                icon='CHECKMARK' if id_ == current.command_section else 'NONE')


def toggle(layout, table, id_, row, *, required=False):
    button = layout.row(align=True)
    button.enabled = not required
    ops.operator_button(button, table, '', id_,
                        icon='CHECKBOX_HLT' if row.get('enabled', True) else 'CHECKBOX_DEHLT')


def group_controls(layout, current, preview):
    categories, sections = current.catalog['categories'], current.catalog['sections']
    if current.category not in categories:
        current.category = next(iter(categories), '')
    section_ids = current.sections()
    if current.section not in section_ids:
        current.section = next(iter(section_ids), '')
    if not categories:
        return
    group = layout.box()
    row = group.row(align=True)
    category = categories[current.category]
    toggle(row, 'categories', current.category, category)
    row.menu(BH_MT_deluxe_categories.__name__, text=category['label'], icon='DOWNARROW_HLT')
    section = sections.get(current.section)
    if section:
        toggle(row, 'sections', current.section, section, required=section.get('required', False))
        row.menu(BH_MT_deluxe_sections.__name__, text=section['label'], icon='DOWNARROW_HLT')
    row.operator(ops.BH_OT_deluxe_section.bl_idname, text='Add Section', icon='ADD')
    if section is None:
        return
    row = group.row(align=True)
    if section.get('required'):
        row.label(text='Required section', icon='LOCKED')
    else:
        row.operator(ops.BH_OT_deluxe_section.bl_idname, text='Rename').section = current.section
        index = section_ids.index(current.section)
        for offset, label, icon in ((-1, 'Move Up', 'TRIA_UP'), (1, 'Move Down', 'TRIA_DOWN')):
            arrow = row.row(align=True)
            neighbor = index + offset
            arrow.enabled = (0 <= neighbor < len(section_ids)
                             and not sections[section_ids[neighbor]].get('required'))
            ops.operator_button(arrow, 'order', label, str(offset), icon=icon)
        has_entries = any(item['section'] == current.section for table in ('assignments', 'suppressions')
                          for item in current.catalog[table].values())
        remove = row.row(align=True)
        remove.enabled = not has_entries
        ops.operator_button(remove, 'delete_section', '', current.section, icon='TRASH')
    if not preview['sections'][current.section]:
        group.label(text='Section inactive', icon='INFO')
    from ...prefs import prefs

    # Existing saved feature choices still gate the profile. Let artists
    # re-enable those choices in place if they block the selected section.
    if category.get('enabled', True) and section.get('enabled', True):
        for path in (category.get('switch'), section.get('switch')):
            if path:
                owner, name = preference_switch(prefs(), path)
                if not getattr(owner, name):
                    group.prop(owner, name)


def preference_switch(preferences, path):
    *parts, name = path.split('.')
    owner = preferences
    for part in parts:
        owner = getattr(owner, part)
    return getattr(owner, '_raw', owner), name


def assignments(layout, current, preview, query):
    group_controls(layout, current, preview)
    catalog = current.catalog
    section = catalog['sections'].get(current.section)
    if section and not section.get('required'):
        row = layout.row(align=True)
        row.operator(ops.BH_OT_deluxe_mapping.bl_idname, text='Add Assignment', icon='ADD')
        row.operator(ops.BH_OT_deluxe_shortcut.bl_idname, text='New Shortcut', icon='EVENT_A')
        row.operator(ops.BH_OT_deluxe_binding_picker.bl_idname,
                     text='Disable Existing Shortcut', icon='X').section = current.section
    found = []
    for id_, row in sorted(catalog['assignments'].items(), key=lambda entry: entry[1]['order']):
        if not query and row['section'] != current.section:
            continue
        meta = preview['commands'][row['command']]
        command = meta['label']
        event = shortcut(catalog['events'][row['event']])
        scope = context_label(row['scope'])
        owner = meta['owner']
        if find(' '.join((ops.command_name(current, row['command']), event, scope, owner,
                          catalog['sections'][row['section']]['label'])), query):
            found.append((id_, command, event, scope, owner))
    if not found:
        layout.label(text='No matching assignments' if query else 'No assignments in this section')
    shown = paginate(layout, current, found)
    if current.assignment not in {item[0] for item in shown}:
        current.assignment = shown[0][0] if shown else ''
    for id_, command, event, scope, owner in shown:
        box = layout.split(factor=0.45, align=True)
        icon = 'RADIOBUT_ON' if id_ == current.assignment else 'RADIOBUT_OFF'
        ops.operator_button(box, 'assignment', command, id_, icon=icon, depress=id_ == current.assignment)
        details = box.split(factor=0.45, align=True)
        details.label(text=event)
        details.label(text=f'{scope} · {owner}')
    if current.assignment:
        inspector(layout.box(), current, preview, current.assignment)
    if section:
        rules(layout, current, preview)


def inspector(layout, current, preview, id_):
    row = current.catalog['assignments'][id_]
    meta = preview['commands'][row['command']]
    state = preview['assignments'][id_]
    event = current.catalog['events'][row['event']]
    head = layout.row()
    head.label(text=ops.command_name(current, row['command']))
    if id_ not in current.defaults['assignments']:
        head.label(text='Custom assignment')
    elif same_value(row, current.defaults['assignments'][id_]) and all(
            same_value(current.catalog[table][row[key]], current.defaults[table].get(row[key]))
            for table, key in (('events', 'event'), ('commands', 'command'))):
        head.label(text='Deluxe default')
    else:
        head.label(text='Customized')
    layout.label(text=f'{shortcut(event)}  ·  {context_label(row["scope"])}  ·  {meta["owner"]}')
    if not state['eligible'] or not state['active']:
        layout.label(text='Inactive', icon='INFO')
    if meta['availability'] != 'available':
        layout.label(text=STATUS_LABELS[meta['availability']], icon='ERROR')
    elif state['eligible'] and state['active'] and not state['registered'] and id_ in current.saved['assignments']:
        layout.label(text='Waiting for runtime registration' if current.dirty
                     else 'Shortcut could not be registered', icon='INFO')
    count = len(current.draft.uses('events', row['event']))
    layout.label(text=f'Used by {count} assignment{"s" if count != 1 else ""}')
    linked = current.draft.uses('events', row['event'])
    if count > 1:
        scopes = dict.fromkeys(context_label(current.catalog['assignments'][other]['scope']) for other in linked)
        for scope in scopes:
            layout.label(text=scope, icon='DOT')
    if any(id_ in conflict for conflict in preview['conflicts']):
        layout.label(text='Another Deluxe assignment uses this input in this keymap', icon='ERROR')
    if id_ in preview['inherited_conflicts']:
        layout.label(text='Overlaps Blender: ' + ', '.join(preview['inherited_conflicts'][id_]), icon='INFO')
    if not state['editable']:
        layout.label(text='Required shortcut', icon='LOCKED')
        return
    actions = layout.row(align=True)
    op = actions.operator(ops.BH_OT_deluxe_capture.bl_idname, text='Capture for This Assignment', icon='REC')
    op.assignment = id_
    actions.operator(ops.BH_OT_deluxe_shortcut.bl_idname, text='Edit Shortcut').assignment = id_
    actions = layout.row(align=True)
    if count > 1 and all(preview['assignments'][other]['editable'] for other in linked):
        op = actions.operator(ops.BH_OT_deluxe_capture.bl_idname, text=f'Capture for All {count}', icon='LINKED')
        op.assignment, op.shared = id_, True
    actions.operator(ops.BH_OT_deluxe_mapping.bl_idname, text='Assignment Settings').assignment = id_
    toggle(actions, 'assignments', id_, row)
    ops.operator_button(actions, 'remove_assignment', '', id_, icon='TRASH')
    if meta['fields']:
        command_fields(layout, current, preview, row['command'], assignment=id_)
    ops.operator_button(layout, 'show_command', 'View Command', id_, icon='FORWARD')


def command_fields(layout, current, preview, id_, assignment=''):
    command = current.catalog['commands'][id_]
    meta = (preview['commands'][id_] if assignment else
            current.store.resolver.describe_command(command, include_unset=True))
    properties = command.get('properties', {})
    fields = meta['fields']
    for explicit, heading in ((True, 'Configured Settings'), (False, 'Additional Blender Settings')):
        names = [name for name in fields if (name in properties) == explicit]
        if not names:
            continue
        group = layout.column(align=True)
        if not assignment:
            group.label(text=heading)
        for name in names:
            field = fields[name]
            value = properties.get(name, field.get('default'))
            label = field.get('label', title(name))
            if value is not None:
                label += ': ' + display_value(value)
            if not explicit and value is not None:
                label += ' (default)'
            if field.get('editable'):
                op = group.operator(ops.BH_OT_deluxe_field.bl_idname, text=label, icon='GREASEPENCIL')
                op.command, op.field, op.assignment = id_, name, assignment
            else:
                group.label(text=label, icon='LOCKED')
    if not meta['editable'] and not assignment:
        layout.label(text='No editable settings for this command', icon='INFO')


def commands(layout, current, preview, query):
    categories = current.catalog['categories']
    if current.command_category not in categories:
        current.command_category, current.command_section = '', ''
    if current.command_section not in current.sections(current.command_category):
        current.command_section = ''
    row = layout.row(align=True)
    category = categories.get(current.command_category, {})
    section = current.catalog['sections'].get(current.command_section, {})
    row.menu(BH_MT_deluxe_command_categories.__name__,
             text=category.get('label', 'All Categories'), icon='DOWNARROW_HLT')
    section_menu = row.row(align=True)
    section_menu.enabled = bool(current.command_category)
    section_menu.menu(BH_MT_deluxe_command_sections.__name__,
                      text=section.get('label', 'All Sections'), icon='DOWNARROW_HLT')
    found = []
    for id_ in current.command_ids():
        meta = preview['commands'][id_]
        name = ops.command_name(current, id_)
        command = current.catalog['commands'][id_]
        if find(f"{name} {meta['owner']} {command.get('operator', '')}", query):
            found.append((id_, name, meta))
    found.sort(key=lambda item: (item[1].casefold(), item[0]))
    shown = paginate(layout, current, found)
    if current.command not in {item[0] for item in shown}:
        current.command = shown[0][0] if shown else ''
    if not shown:
        layout.label(text='No matching commands')
    for id_, name, meta in shown:
        row = layout.row(align=True)
        ops.operator_button(row, 'command', name, id_, depress=id_ == current.command)
        row.label(text=STATUS_LABELS.get(meta['availability'], meta['owner']))
    if not current.command:
        return
    id_ = current.command
    meta = preview['commands'][id_]
    box = layout.box()
    box.label(text=f"{ops.command_name(current, id_)}  ·  {meta['owner']}")
    if meta['availability'] != 'available':
        box.label(text=STATUS_LABELS[meta['availability']], icon='ERROR')
    uses = current.draft.uses('commands', id_)
    if uses:
        ops.draw_uses(box, current, 'commands', uses[0])
    else:
        box.label(text='Unused command')
    command_fields(box, current, preview, id_)


def rules(layout, current, preview):
    for id_, row in current.catalog['suppressions'].items():
        if row['section'] != current.section:
            continue
        status = preview['suppressions'][id_]
        box = layout.box()
        selector = row['selector']
        target = selector['target']
        box.label(text=f"{target.get('idname', target.get('modal_value'))}  ·  {shortcut(selector['event'])}")
        box.label(text=f"{context_label(selector['scope'])}  ·  {SOURCE_LABELS[selector['source_role']]}")
        committed = current.saved['suppressions'].get(id_)
        if status['registered'] and same_value(row, committed):
            label = 'Replacement active'
        elif not status['eligible']:
            label = 'Rule inactive'
        else:
            label = STATUS_LABELS[status['status']]
        box.label(text=label, icon='INFO')
        if 'replacement' in row:
            box.label(text='Replacement: ' + ops.command_name(current, row['replacement']))
        row_layout = box.row(align=True)
        toggle(row_layout, 'suppressions', id_, row)
        pick = row_layout.operator(ops.BH_OT_deluxe_binding_picker.bl_idname, text='Pick Again')
        pick.section, pick.rule = current.section, id_
        ops.operator_button(row_layout, 'remove_rule', 'Remove Rule', id_, icon='TRASH')


def draw(context, layout):
    try:
        current = ops.editor()
        view = ops.state(context)
    except ops.ERRORS:
        layout.label(text='The Deluxe profile editor is waiting for Blender keymaps', icon='INFO')
        return
    layout.operator_context = 'INVOKE_DEFAULT'
    toolbar = layout.row(align=True)
    toolbar.prop(view, 'tab', expand=True)
    toolbar.prop(view, 'search', text='', icon='VIEWZOOM')
    transaction_controls(layout, current)
    try:
        preview = current.preview()
    except ops.ERRORS as error:
        layout.label(text=str(error), icon='ERROR')
    else:
        query = view.search.strip()
        draw_tab = assignments if view.tab == 'ASSIGNMENTS' else commands
        draw_tab(layout, current, preview, query)
        if current.dirty and preview['conflicts']:
            layout.label(text=f"{len(preview['conflicts'])} conflicting Deluxe input groups", icon='ERROR')


def transaction_controls(layout, current):
    footer = layout.row(align=True)
    ops.operator_button(footer, 'reset', 'Reset Draft')
    ops.operator_button(footer, 'reload', 'Reload Profile', icon='FILE_REFRESH')
    staged = footer.row(align=True)
    discard = staged.row(align=True)
    discard.enabled = current.dirty
    ops.operator_button(discard, 'discard', 'Discard')
    apply = staged.row(align=True)
    apply.enabled = current.dirty or bool(current.store.load_issue)
    label = 'Save Recovered Profile' if current.store.load_issue and not current.dirty else 'Apply Changes'
    ops.operator_button(apply, 'apply', label, icon='CHECKMARK')
    if current.message:
        layout.label(text=current.message)
    if current.store.load_issue:
        messages = {
            'invalid_profile_recovered_previous': 'Profile file invalid. The last saved copy is active.',
            'invalid_profile_recovered_defaults': 'Profile file invalid. A valid profile is active.',
            'profile_saved_recovery_copy_unavailable': 'Profile saved. The recovery copy could not be updated.',
        }
        layout.label(text=messages.get(current.store.load_issue, 'Profile recovery required'), icon='ERROR')


classes = (BH_MT_deluxe_categories, BH_MT_deluxe_sections,
           BH_MT_deluxe_command_categories, BH_MT_deluxe_command_sections)


def register():
    ops.register()
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    ops.unregister()
