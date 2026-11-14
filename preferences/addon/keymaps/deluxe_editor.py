"""Bindings and Commands views inside Blue Hole's Keymaps preferences."""

import sys
import textwrap

import bpy

from . import deluxe_editor_ops as ops
from .deluxe_editor_model import (SOURCE_LABELS, STATUS_LABELS, context_label, display_value,
                                  key_filter, key_label, shortcut, title)
from ....keymaps.deluxe_schema import same_value

PAGE_SIZE = 8
COMPACT_WIDTH = 440
DETAIL_PANE_MIN_WIDTH = 680
TWO_COLUMN_FIELDS_MIN_WIDTH = 520
ASSIGNMENT_TABLE_MIN_WIDTH = 380
LIST_WIDTH_FRACTION = 0.41


def find(text, query):
    return all(term in text.casefold() for term in query.casefold().split())


def paginate(layout, current, rows):
    last = max(0, (len(rows) - 1) // PAGE_SIZE)
    page = min(current.page, last)
    if last:
        bar = layout.row(align=True)
        bar.alignment = 'LEFT'
        prev = bar.row(align=True)
        prev.enabled = page > 0
        ops.operator_button(prev, 'page', '', str(max(0, page - 1)), icon='TRIA_LEFT')
        number = bar.row(align=True)
        number.alignment = 'CENTER'
        number.label(text=f'{page + 1} / {last + 1}')
        forward = bar.row(align=True)
        forward.enabled = page < last
        ops.operator_button(forward, 'page', '', str(min(last, page + 1)), icon='TRIA_RIGHT')
    return rows[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]


def detail_columns(layout, width, *, detail_first=False):
    if width >= DETAIL_PANE_MIN_WIDTH:
        split = layout.split(factor=LIST_WIDTH_FRACTION)
        return split.box().column(align=True), split.column(), width * LIST_WIDTH_FRACTION
    first = layout.column()
    layout.separator()
    second = layout.column()
    listing, detail = (second, first) if detail_first else (first, second)
    return listing.box().column(align=True), detail, width


def assignment_columns(layout):
    row = layout.split(factor=0.40, align=True)
    name = row.row(align=True)
    binding = row.split(factor=0.52, align=True)
    return name, binding.row(align=True), binding.row(align=True)


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


class BH_MT_deluxe_section_actions(bpy.types.Menu):
    bl_label = 'Subsection Options'

    def draw(self, _context):
        current = ops.editor()
        section = current.catalog['sections'].get(current.section)
        layout = self.layout
        layout.operator(ops.BH_OT_deluxe_section.bl_idname, text='Add Subsection', icon='ADD')
        if current.binding_category_all or not section or section.get('required'):
            return
        layout.operator(ops.BH_OT_deluxe_section.bl_idname, text='Rename Subsection').section = current.section
        sections = current.sections()
        index = sections.index(current.section)
        for offset, label, icon in ((-1, 'Move Up', 'TRIA_UP'), (1, 'Move Down', 'TRIA_DOWN')):
            neighbor = index + offset
            if 0 <= neighbor < len(sections) and not current.catalog['sections'][sections[neighbor]].get('required'):
                ops.operator_button(layout, 'order', label, str(offset), icon=icon)
        has_entries = any(item['section'] == current.section for table in ('assignments', 'suppressions')
                          for item in current.catalog[table].values())
        if not has_entries:
            ops.operator_button(layout, 'delete_section', 'Delete Empty Subsection', current.section, icon='TRASH')


class BH_MT_deluxe_command_categories(bpy.types.Menu):
    bl_label = 'Used in Section'

    def draw(self, _context):
        current = ops.editor()
        ops.operator_button(self.layout, 'command_category', 'All Sections (including unused)')
        for id_, row in current.catalog['categories'].items():
            ops.operator_button(self.layout, 'command_category', row['label'], id_,
                                icon='CHECKMARK' if id_ == current.command_category else 'NONE')


class BH_MT_deluxe_command_sections(bpy.types.Menu):
    bl_label = 'Used in Subsection'

    def draw(self, _context):
        current = ops.editor()
        ops.operator_button(self.layout, 'command_section', 'All Subsections')
        for id_ in current.sections(current.command_category):
            row = current.catalog['sections'][id_]
            ops.operator_button(self.layout, 'command_section', row['label'], id_,
                                icon='CHECKMARK' if id_ == current.command_section else 'NONE')


def toggle(layout, table, id_, row, *, required=False, text=''):
    control = ops.inline_value(ops.state(bpy.context), 'enabled', 'boolean', row.get('enabled', True),
                               table=table, entry=id_)
    checkbox = layout.row(align=True)
    checkbox.enabled = not required
    checkbox.prop(control, 'boolean', text=text, toggle=False)


def binding_filters(layout, current, preview):
    current.ensure_selection()
    view = ops.state(bpy.context)
    group = layout.box()
    bar = group.row(align=True)
    ops.operator_button(bar, 'all_bindings', 'All Bindings', icon='HOME',
                        depress=current.binding_all and not current.binding_context and not current.binding_command and not view.search)
    bar.label(text='Blender Context:')
    scope = current.binding_contexts().get(current.binding_context)
    bar.operator(ops.BH_OT_deluxe_filter_context.bl_idname,
                 text=context_label(scope) if scope else 'All Contexts', icon='VIEWZOOM')
    if current.binding_context:
        ops.operator_button(bar, 'clear_context', '', icon='X')
    if current.binding_command:
        row = group.row(align=True)
        row.label(text='Command: ' + ops.command_name(current, current.binding_command))
        ops.operator_button(row, 'clear_command_filter', '', icon='X')
    categories = current.catalog['categories']
    tabs = group.row(align=True)
    for id_, row in categories.items():
        ops.operator_button(tabs, 'feature_category', row['label'], id_,
                            depress=not current.binding_all and id_ == current.category)
    if current.binding_all or not categories:
        return True
    category = categories[current.category]
    line = group.row(align=True)
    toggle(line, 'categories', current.category, category, text=f"Enable {category['label']} Keymaps")
    line.menu(BH_MT_deluxe_section_actions.__name__, text='', icon='THREE_DOTS')
    if not category.get('enabled', True):
        return False
    sections = current.sections()
    if not sections:
        group.label(text='No subsections')
        return True
    tabs = group.row(align=True)
    ops.operator_button(tabs, 'all_subsections', 'All ' + category['label'], depress=current.binding_category_all)
    for id_ in sections:
        row = current.catalog['sections'][id_]
        ops.operator_button(tabs, 'feature_section', row['label'], id_,
                            depress=not current.binding_category_all and id_ == current.section)
    if current.binding_category_all:
        return True
    section = current.catalog['sections'][current.section]
    line = group.row(align=True)
    if section.get('required'):
        line.label(text=section['label'] + ' Keymaps (required)', icon='LOCKED')
    else:
        toggle(line, 'sections', current.section, section, text=f"Enable {section['label']} Keymaps")
    return section.get('enabled', True) or section.get('required', False)


class BH_MT_deluxe_assignment_actions(bpy.types.Menu):
    bl_label = 'Binding Actions'

    def draw(self, _context):
        current = ops.editor()
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator(ops.BH_OT_deluxe_shortcut.bl_idname, text='New Shortcut', icon='EVENT_A')
        layout.operator(ops.BH_OT_deluxe_binding_picker.bl_idname, icon='VIEWZOOM').section = current.section


def assignments(layout, current, preview, query, *, width, search_keys=False):
    if not binding_filters(layout, current, preview):
        return
    catalog = current.catalog
    row = layout.row(align=True)
    row.alignment = 'LEFT'
    row.operator(ops.BH_OT_deluxe_mapping.bl_idname, text='Add Binding', icon='ADD')
    row.menu(BH_MT_deluxe_assignment_actions.__name__, text='Actions')
    rules(layout, current, preview)
    found = []
    matches_key = None
    if query and search_keys:
        events = bpy.types.Event.bl_rna.properties['type'].enum_items
        matches_key = key_filter(query, {key: item.name for key, item in events.items()})
    for id_, row in sorted(catalog['assignments'].items(), key=lambda entry: entry[1]['order']):
        if not current.accepts_binding(row):
            continue
        meta = preview['commands'][row['command']]
        command = meta['label']
        event_data = catalog['events'][row['event']]
        event = shortcut(event_data)
        scope = context_label(row['scope'])
        owner = meta['owner']
        operator = catalog['commands'][row['command']].get('operator', '')
        if not query:
            matches = True
        elif matches_key:
            matches = matches_key(event_data)
        else:
            matches = find(' '.join((ops.command_name(current, row['command']), operator, event,
                                     scope, owner, catalog['sections'][row['section']]['label'])), query)
        if matches:
            found.append((id_, command, event, scope, meta))
    if found:
        listing, detail, list_width = detail_columns(layout, width, detail_first=True)
        detail_width = width - list_width if width >= DETAIL_PANE_MIN_WIDTH else width
        table = list_width >= ASSIGNMENT_TABLE_MIN_WIDTH
        listing.label(text=f'{len(found)} {"binding" if len(found) == 1 else "bindings"}')
        listing.separator(factor=0.5)
        if current.assignment not in {item[0] for item in found}:
            current.assignment = found[0][0]
        if table:
            name, key, scope_column = assignment_columns(listing)
            name.label(text='Command')
            key.label(text='Keymap Binding')
            scope_column.label(text='Context')
            listing.separator(type='LINE')
        for id_, command, event, scope, meta in found:
            selected = id_ == current.assignment
            waiting = meta['availability'] == 'waiting_for_provider'
            if table:
                name, key, scope_column = assignment_columns(listing)
            else:
                name = listing.row(align=True)
            icon = 'RADIOBUT_ON' if selected else 'RADIOBUT_OFF'
            if not preview['assignments'][id_]['eligible'] or not preview['assignments'][id_]['active']:
                icon = 'PAUSE'
            elif waiting:
                icon = 'ERROR'
            ops.operator_button(name, 'assignment', command, id_, icon=icon, emboss=selected, depress=selected)
            if table:
                key.label(text=event)
                scope_column.label(text=scope)
            else:
                listing.label(text=f'{event}  ·  {scope}', icon='BLANK1')
                if waiting:
                    listing.label(text=f"Waiting for {meta['dependency']}", icon='ERROR')
            if id_ != found[-1][0]:
                listing.separator(factor=0.5, type='LINE')
        inspector(detail.box().column(), current, preview, current.assignment, width=detail_width)
    else:
        current.assignment = ''
        layout.label(text='No bindings match these filters')


def inspector(layout, current, preview, id_, *, width):
    row = current.catalog['assignments'][id_]
    meta = preview['commands'][row['command']]
    state = preview['assignments'][id_]
    event = current.catalog['events'][row['event']]
    heading = layout.row()
    heading.scale_y = 1.25
    toggle(heading, 'assignments', id_, row, text=meta['label'], required=not state['editable'])
    command = current.catalog['commands'][row['command']]
    identity = layout.row(align=True)
    identity.alignment = 'LEFT'
    if command.get('operator'):
        identity.label(text=command['operator'], icon='CONSOLE')
        if width < COMPACT_WIDTH:
            identity = layout.row(align=True)
    if id_ not in current.defaults['assignments']:
        identity.label(text='Custom binding')
    elif same_value(row, current.defaults['assignments'][id_]) and all(
            same_value(current.catalog[table][row[key]], current.defaults[table].get(row[key]))
            for table, key in (('events', 'event'), ('commands', 'command'))):
        identity.label(text='Deluxe default')
    else:
        identity.label(text='Customized')
    section = current.catalog['sections'][row['section']]
    category = current.catalog['categories'][section['category']]
    path = f"{category['label']} / {section['label']}"
    location = layout.row(align=True)
    location.alignment = 'LEFT'
    ops.operator_button(location, 'show_assignments', path, row['section'], icon='FILE_FOLDER', emboss=False)
    toggle(location, 'sections', row['section'], section, required=section.get('required', False))
    if not preview['sections'][row['section']]:
        layout.label(text='Section inactive', icon='INFO')
    scope_row = layout.column(align=True) if width < COMPACT_WIDTH else layout.row(align=True)
    scope_row.alignment = 'LEFT'
    scope_row.label(text='Keymap Context')
    scope = context_label(row['scope'])
    if state['editable']:
        scope_row.operator(ops.BH_OT_deluxe_context.bl_idname, text=scope, icon='VIEWZOOM').assignment = id_
    else:
        scope_row.label(text=scope, icon='LOCKED')
    if not state['eligible'] or not state['active']:
        layout.label(text='Inactive', icon='INFO')
    if meta['availability'] == 'waiting_for_provider':
        layout.label(text=f"Waiting for {meta['dependency']}", icon='ERROR')
    elif meta['dependency']:
        layout.label(text=f"Requires {meta['dependency']}", icon='INFO')
    elif meta['availability'] != 'available':
        layout.label(text=STATUS_LABELS[meta['availability']], icon='ERROR')
    elif state['eligible'] and state['active'] and not state['registered'] and id_ in current.saved['assignments']:
        layout.label(text='Waiting for runtime registration' if current.dirty
                     else 'Shortcut could not be registered', icon='INFO')
    if any(id_ in conflict for conflict in preview['conflicts']):
        layout.label(text='Another Deluxe assignment uses this input in this keymap', icon='ERROR')
    if id_ in preview['inherited_conflicts']:
        layout.label(text='Overlaps Blender: ' + ', '.join(preview['inherited_conflicts'][id_]), icon='INFO')
    if not state['editable']:
        layout.label(text='Required shortcut', icon='LOCKED')
        ops.operator_button(layout, 'show_command', 'View Command', id_, icon='FORWARD', emboss=False)
        return
    settings = layout.box()
    settings.label(text='KEYMAP BINDING')
    shortcut_controls(settings.column(align=True), id_, event, compact=width < COMPACT_WIDTH)
    actions = settings.row(align=True)
    actions.alignment = 'LEFT'
    actions.operator(ops.BH_OT_deluxe_shortcut.bl_idname, text='Advanced Shortcut', emboss=False).assignment = id_
    actions.operator(ops.BH_OT_deluxe_mapping.bl_idname, text='', icon='PREFERENCES', emboss=False).assignment = id_
    actions.operator(ops.BH_OT_deluxe_remove_assignment.bl_idname, text='', icon='TRASH', emboss=False).assignment = id_
    linked_shortcut(layout, current, preview, id_)
    command_fields(layout, current, row['command'], width=width, assignment=id_)
    link = layout.row()
    link.alignment = 'LEFT'
    ops.operator_button(link, 'show_command', 'View Command', id_, icon='FORWARD', emboss=False)


def linked_shortcut(layout, current, preview, id_):
    event_id = current.catalog['assignments'][id_]['event']
    linked = current.draft.uses('events', event_id)
    if len(linked) < 2:
        return
    layout.separator()
    box = layout.box().column(align=True)
    expanded = current.expanded_shortcut == event_id
    disclosure = box.row(align=True)
    disclosure.alignment = 'LEFT'
    ops.operator_button(disclosure, 'linked_shortcut', f'Shared Keymap Binding · {len(linked)} Bindings',
                        event_id, icon='TRIA_DOWN' if expanded else 'TRIA_RIGHT', emboss=False)
    if not expanded:
        return
    if all(preview['assignments'][id2]['editable'] for id2 in linked):
        actions = box.row()
        actions.alignment = 'LEFT'
        op = actions.operator(ops.BH_OT_deluxe_capture.bl_idname,
                              text='Input Key…' if current.capture_assignment == id_ and current.capture_shared
                              else f'Change All {len(linked)}', icon='LINKED')
        op.assignment, op.shared = id_, True
    else:
        box.label(text='Includes a required assignment', icon='LOCKED')
    box.separator(factor=0.5)
    for section_id, ids, total in current.linked_sections(linked):
        section = current.catalog['sections'][section_id]
        category = current.catalog['categories'][section['category']]
        label = f"{category['label']} / {section['label']}"
        count = f'All {total}' if len(ids) == total else str(len(ids))
        expanded_section = current.expanded_linked_section == section_id
        header = box.row(align=True)
        ops.operator_button(header, 'linked_section', f'{label} · {count}', section_id,
                            icon='TRIA_DOWN' if expanded_section else 'TRIA_RIGHT', emboss=False)
        ops.operator_button(header, 'show_assignments', '', section_id, icon='FORWARD', emboss=False)
        if expanded_section:
            details = box.box().column(align=True)
            for assignment in ids:
                row = current.catalog['assignments'][assignment]
                status, icon = current.assignment_status(preview, assignment)
                details.label(text=preview['commands'][row['command']]['label'],
                              icon='RADIOBUT_ON' if assignment == id_ else 'NONE')
                details.label(text=f"{context_label(row['scope'])} · {status}", icon=icon)


def shortcut_controls(layout, assignment, event, *, compact):
    view = ops.state(bpy.context)
    options = ops.resolver.input_options()['event']
    input_type = event.get('map_type', ops.map_type(event['type']))
    line = layout.row(align=True)
    if input_type in {'KEYBOARD', 'MOUSE'}:
        control = ops.inline_value(view, 'map_type', 'option', input_type,
                                   assignment=assignment, items=ops.INPUT_TYPES)
        line.prop(control, 'option', text='')
    else:
        line.label(text=title(input_type))
    capturing = ops.editor().capture_assignment == assignment
    line.operator(ops.BH_OT_deluxe_capture.bl_idname,
                  text='Input Key…' if capturing else key_label(event['type']),
                  icon='EVENT_A', depress=capturing).assignment = assignment
    trigger = layout.row(align=True)
    phase = ops.inline_value(view, 'value', 'option', event.get('value', 'PRESS'),
                             assignment=assignment, items=options.get('value', ()))
    trigger.prop(phase, 'option', text='')
    repeat = trigger.row(align=True)
    repeat.enabled = input_type == 'KEYBOARD' and event.get('value', 'PRESS') in {'PRESS', 'ANY'}
    control = ops.inline_value(view, 'repeat', 'boolean', event.get('repeat', False), assignment=assignment)
    repeat.prop(control, 'boolean', text='Repeat', toggle=False)
    modifier_row = layout if compact else layout.split(factor=0.64, align=True)
    mods = modifier_row.row(align=True)
    any_mod = ops.inline_value(view, 'any', 'boolean', event.get('any', False), assignment=assignment)
    mods.prop(any_mod, 'boolean', text='Any', toggle=True)
    controls = mods.row(align=True)
    controls.enabled = not event.get('any', False)
    oskey = {'darwin': 'Cmd', 'win32': 'Win'}.get(sys.platform, 'OS Key')
    for key, label in (('shift', 'Shift'), ('ctrl', 'Ctrl'), ('alt', 'Alt'), ('oskey', oskey)):
        value = event.get(key, False)
        button = controls.operator(ops.BH_OT_deluxe_inline_edit.bl_idname,
                                   text=label + (' (Either)' if value == -1 else ''), depress=bool(value))
        button.assignment, button.field = assignment, key
    modifier = ops.inline_value(view, 'key_modifier', 'option', event.get('key_modifier', 'NONE'),
                                assignment=assignment, items=options['key_modifier'])
    modifier_key = modifier_row.row(align=True)
    modifier_key.prop(modifier, 'option', text='Key Modifier')
    if event.get('value') == 'CLICK_DRAG':
        control = ops.inline_value(view, 'direction', 'option', event.get('direction', 'ANY'),
                                   assignment=assignment, items=options['direction'])
        direction = layout.row(align=True)
        direction.alignment = 'LEFT'
        direction.prop(control, 'option', text='Direction')


def command_fields(layout, current, id_, *, width, assignment=''):
    command = current.catalog['commands'][id_]
    meta = current.store.resolver.describe_command(command, include_unset=True)
    properties = command.get('properties', {})
    fields = meta['fields']
    view = ops.state(bpy.context)
    if assignment:
        uses = len(current.draft.uses('commands', id_))
        scope = layout.box()
        scope.label(text=f'Command settings · used by {uses} binding' + ('s' if uses != 1 else ''))
        if meta['editable']:
            scope.row(align=True).prop(view, 'command_edit_scope', expand=True)
        else:
            scope.label(text='No editable command settings', icon='LOCKED')
        ops.operator_button(scope, 'command_bindings', 'View All Bindings for This Command', id_, icon='FORWARD', emboss=False)

    affected = ((assignment,) if assignment and view.command_edit_scope == 'SINGLE'
                else current.draft.uses('commands', id_))
    editable = all(not current.catalog['sections'][current.catalog['assignments'][aid]['section']].get('required')
                   for aid in affected)
    for explicit, heading in ((True, 'Configured Settings'), (False, 'Additional Blender Settings')):
        names = [name for name in fields if (name in properties) == explicit]
        if not names:
            continue
        group = layout.box()
        if explicit:
            group.label(text='COMMAND SETTINGS' if assignment else heading.upper())
        else:
            view = ops.state(bpy.context)
            group.prop(view, 'show_extra_fields', text=heading, emboss=False,
                       icon='TRIA_DOWN' if view.show_extra_fields else 'TRIA_RIGHT')
            if not view.show_extra_fields:
                continue
        grid = group.grid_flow(columns=2 if width >= TWO_COLUMN_FIELDS_MIN_WIDTH else 1, align=True)
        for name in names:
            field = fields[name]
            value = properties.get(name, field.get('default'))
            label = field.get('label', title(name))
            cell = grid.row(align=True)
            prop = ops.INLINE_VALUES.get(field.get('type'))
            if editable and field.get('editable') and prop and not (field['shape'] or field['flags']):
                control = ops.inline_value(ops.state(bpy.context), name, prop, value,
                                           command=id_, assignment=assignment, items=field['enum_items'])
                cell.prop(control, prop, text=label)
                if explicit:
                    reset = cell.operator(ops.BH_OT_deluxe_inline_edit.bl_idname, text='', icon='X')
                    reset.command, reset.field, reset.assignment = id_, name, assignment
                continue
            if value is not None:
                label += ': ' + display_value(value)
            if not explicit and value is not None:
                label += ' (default)'
            if editable and field.get('editable'):
                op = cell.operator(ops.BH_OT_deluxe_field.bl_idname, text=label, icon='GREASEPENCIL')
                op.command, op.field, op.assignment = id_, name, assignment
            else:
                cell.label(text=label, icon='LOCKED')
    if not meta['editable'] and not assignment:
        layout.label(text='No editable settings for this command', icon='INFO')


def commands(layout, current, preview, query, *, width):
    categories = current.catalog['categories']
    if current.command_category not in categories:
        current.command_category, current.command_section = '', ''
    if current.command_section not in current.sections(current.command_category):
        current.command_section = ''
    filters = layout.box()
    filters.label(text='COMMAND LIBRARY')
    filters.operator(ops.BH_OT_deluxe_command.bl_idname, text='New Command', icon='ADD')
    row = filters.row(align=True)
    category = categories.get(current.command_category, {})
    section = current.catalog['sections'].get(current.command_section, {})
    row.menu(BH_MT_deluxe_command_categories.__name__,
             text=category.get('label', 'All Sections (including unused)'))
    if width < COMPACT_WIDTH:
        row = filters.row(align=True)
    section_menu = row.row(align=True)
    section_menu.enabled = bool(current.command_category)
    section_menu.menu(BH_MT_deluxe_command_sections.__name__,
                      text=section.get('label', 'All Subsections'))
    if section:
        if width < COMPACT_WIDTH:
            row = filters.row(align=True)
            row.alignment = 'LEFT'
        ops.operator_button(row, 'show_assignments', 'View Bindings', current.command_section, icon='FORWARD')
    found = []
    for id_ in current.command_ids():
        meta = preview['commands'][id_]
        name = ops.command_name(current, id_)
        command = current.catalog['commands'][id_]
        if find(f"{name} {meta['owner']} {command.get('operator', '')}", query):
            found.append((id_, name, meta))
    found.sort(key=lambda item: (item[1].casefold(), item[0]))
    if not found:
        current.command = ''
        layout.label(text='No matching commands')
        return
    if current.focus_command:
        current.page = next((index // PAGE_SIZE for index, item in enumerate(found) if item[0] == current.command), 0)
        current.focus_command = False
    listing, detail, list_width = detail_columns(layout, width)
    detail_width = width - list_width if width >= DETAIL_PANE_MIN_WIDTH else width
    listing.label(text=f'{len(found)} {"command" if len(found) == 1 else "commands"}')
    listing.separator(factor=0.5)
    shown = paginate(listing, current, found)
    if current.command not in {item[0] for item in shown}:
        current.command = shown[0][0]
    for id_, name, meta in shown:
        selected = id_ == current.command
        icon = 'RADIOBUT_ON' if selected else 'RADIOBUT_OFF'
        ops.operator_button(listing, 'command', name, id_, icon=icon, emboss=selected, depress=selected)
        uses = len(current.draft.uses('commands', id_))
        command = current.catalog['commands'][id_]
        source = command.get('operator', command.get('modal_value', ''))
        listing.label(text=f'{uses} binding' + ('s' if uses != 1 else '') + ' · ' + source, icon='BLANK1')
        if meta['availability'] != 'available':
            listing.label(text=STATUS_LABELS.get(meta['availability'], meta['owner']), icon='INFO')
        if id_ != shown[-1][0]:
            listing.separator(factor=0.5, type='LINE')
    command_details(detail.box().column(), current, preview['commands'][current.command], current.command,
                    width=detail_width)


def command_details(layout, current, meta, id_, *, width):
    header = layout.row()
    header.scale_y = 1.25
    header.label(text=ops.command_name(current, id_))
    layout.label(text=meta['owner'])
    if meta['availability'] != 'available':
        layout.label(text=STATUS_LABELS[meta['availability']], icon='INFO')
    uses = current.draft.uses('commands', id_)
    sections = dict.fromkeys(current.catalog['assignments'][aid]['section'] for aid in uses)
    actions = layout.row(align=True)
    actions.operator(ops.BH_OT_deluxe_mapping.bl_idname, text='Add Binding', icon='ADD').command_hint = id_
    actions.operator(ops.BH_OT_deluxe_command.bl_idname, text='Duplicate', icon='DUPLICATE').source = id_
    replacements = sum(row.get('replacement') == id_ for row in current.catalog['suppressions'].values())
    if not uses and not replacements:
        ops.operator_button(actions, 'remove_command', 'Delete Unused', id_, icon='TRASH')
    if replacements:
        layout.label(text=f'Used by {replacements} default replacement rules')
    if uses:
        layout.label(text=f'Edits apply to all {len(uses)} linked bindings, including inactive ones')
        ops.operator_button(layout, 'command_bindings', 'View All Bindings', id_, icon='FORWARD')
        links = layout.grid_flow(columns=2 if width >= TWO_COLUMN_FIELDS_MIN_WIDTH else 1, align=True)
        for section_id in sections:
            section = current.catalog['sections'][section_id]
            category = current.catalog['categories'][section['category']]
            label = f"{category['label']} / {section['label']}"
            ops.operator_button(links, 'show_assignments', label, section_id, icon='FORWARD', emboss=False)
    else:
        layout.label(text='No bindings yet · add one to use this command')
    command_fields(layout, current, id_, width=width)


def rules(layout, current, preview):
    group = layout.box()
    heading = group.row(align=True)
    heading.label(text='BLENDER DEFAULTS & OVERRIDES')
    view = ops.state(bpy.context)
    browse = group.row()
    browse.alignment = 'LEFT'
    op = browse.operator(ops.BH_OT_deluxe_binding_picker.bl_idname, text='Browse Blender Defaults', icon='VIEWZOOM')
    op.section, op.defaults = current.section, True
    found = False
    for id_, row in current.catalog['suppressions'].items():
        if not current.accepts_binding({'section': row['section'], 'scope': row['selector']['scope'],
                                        'command': row.get('replacement', '')}):
            continue
        found = True
        status = preview['suppressions'][id_]
        box = group.box()
        selector = row['selector']
        target = selector['target']
        box.label(text=f"{target.get('idname', target.get('modal_value'))}  ·  {shortcut(selector['event'])}")
        box.label(text=f"{context_label(selector['scope'])}  ·  {SOURCE_LABELS[selector['source_role']]}")
        installed = current.store.runtime_catalog()['suppressions'].get(id_)
        if status['registered'] and same_value(row, installed):
            label = 'Disabled by Blue Hole' if row.get('disable') else 'Replacement active'
            if not same_value(row, current.saved['suppressions'].get(id_)):
                label += ' · unsaved preview'
        elif not status['eligible']:
            label = 'Rule inactive'
        elif not row.get('disable') and 'replacement' not in row:
            label = 'Review only · no runtime change'
        else:
            label = STATUS_LABELS[status['status']]
        box.label(text=label, icon='INFO')
        if 'replacement' in row:
            box.label(text='Replacement: ' + ops.command_name(current, row['replacement']))
        for name, value in target.get('properties', {}).items():
            box.label(text=f'{title(name)}: {display_value(value)}')
        row_layout = box.row(align=True)
        toggle(row_layout, 'suppressions', id_, row, text='Enable Rule')
        pick = row_layout.operator(ops.BH_OT_deluxe_binding_picker.bl_idname, text='Pick Again')
        pick.section, pick.rule = current.section, id_
        ops.operator_button(row_layout, 'remove_rule', 'Restore Binding' if row.get('disable') else 'Remove Rule', id_, icon='LOOP_BACK')
        if current.binding_all or current.binding_category_all:
            section = current.catalog['sections'][row['section']]
            category = current.catalog['categories'][section['category']]
            ops.operator_button(box, 'show_assignments', f"{category['label']} / {section['label']}",
                                row['section'], icon='FORWARD', emboss=False)
    if not found:
        group.label(text='No managed default bindings match these filters')


def draw(context, layout, settings):
    try:
        current = ops.editor()
        view = ops.state(context)
    except ops.ERRORS as error:
        for line in textwrap.wrap(str(error), width=100):
            layout.label(text=line, icon='ERROR')
        return
    layout.operator_context = 'INVOKE_DEFAULT'
    scale = context.preferences.system.ui_scale or 1
    width = context.region.width / scale if context.region else 0
    transaction_controls(layout, current, settings, compact=width < COMPACT_WIDTH)
    if not settings.enable_keymaps:
        return
    notice = layout.column(align=True)
    notice.label(text='Blue Hole updates replace editor changes', icon='ERROR')
    message = ('Saved assignments, commands and section choices belong to this Blue Hole installation. '
               'Installing an update replaces them with the new version’s catalog.')
    for line in textwrap.wrap(message, width=max(24, int((width - 40) / 7))):
        notice.label(text=line)
    layout.separator()
    toolbar = layout.row(align=True)
    toolbar.prop(view, 'tab', expand=True)
    layout.separator(factor=0.5)
    search_box = layout.box()
    search = search_box.row(align=True)
    if view.tab == 'BINDINGS':
        search.prop(view, 'search_mode', text='')
    placeholder = ('Search by Key-Binding' if view.tab == 'BINDINGS' and view.search_mode == 'KEY'
                   else 'Search by Name')
    search.prop(view, 'search', text='', icon='VIEWZOOM', placeholder=placeholder)
    layout.separator()
    try:
        preview = current.preview()
    except ops.ERRORS as error:
        layout.label(text=str(error), icon='ERROR')
    else:
        query = view.search.strip()
        if view.tab == 'BINDINGS':
            assignments(layout, current, preview, query, width=width, search_keys=view.search_mode == 'KEY')
        else:
            commands(layout, current, preview, query, width=width)
        if current.dirty and preview['conflicts']:
            layout.label(text=f"{len(preview['conflicts'])} conflicting Deluxe input groups", icon='ERROR')


def transaction_controls(layout, current, settings, *, compact):
    bar = layout.box()
    toolbar = bar if compact else bar.row()
    profile = toolbar.row(align=True)
    profile.alignment = 'LEFT'
    profile.prop(settings, 'enable_keymaps')
    profile.menu(BH_MT_deluxe_profile_actions.__name__, text='', icon='PREFERENCES')
    actions = toolbar.row(align=True)
    actions.alignment = 'LEFT' if compact else 'RIGHT'
    apply = actions.row(align=True)
    apply.enabled = current.dirty or bool(current.store.load_issue)
    ops.operator_button(apply, 'apply', 'Save and Apply Changes', icon='CHECKMARK', depress=apply.enabled)
    discard = actions.row(align=True)
    discard.enabled = current.dirty
    ops.operator_button(discard, 'discard', 'Discard', emboss=False)
    if current.dirty:
        live = same_value(current.catalog, current.store.runtime_catalog()) and not current.preview_error
        bar.label(text='Unsaved changes · live preview' if live else 'Unsaved changes · preview not active', icon='DOT')
    if current.preview_error:
        bar.label(text='Preview failed: ' + current.preview_error, icon='ERROR')
    if current.message and current.message != 'Changes staged':
        bar.label(text=current.message, icon='INFO')
    if current.store.load_issue:
        messages = {
            'invalid_profile_recovered_previous': 'Profile file invalid. The last saved copy is active.',
            'invalid_profile_recovered_defaults': 'Profile file invalid. A valid profile is active.',
            'profile_saved_recovery_copy_unavailable': 'Profile saved. The recovery copy could not be updated.',
        }
        bar.label(text=messages.get(current.store.load_issue, 'Profile recovery required'), icon='ERROR')
        for line in textwrap.wrap(current.store.load_error, width=60 if compact else 110):
            bar.label(text=line)


class BH_MT_deluxe_profile_actions(bpy.types.Menu):
    bl_label = 'Keymap Settings'

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.prop(context.preferences.inputs, 'invert_mouse_zoom')
        layout.separator()
        ops.operator_button(layout, 'reset', 'Reset Draft')
        ops.operator_button(layout, 'reload', 'Validate and Reload JSON Files', icon='FILE_REFRESH')


classes = (BH_MT_deluxe_categories, BH_MT_deluxe_sections, BH_MT_deluxe_section_actions,
           BH_MT_deluxe_profile_actions, BH_MT_deluxe_assignment_actions,
           BH_MT_deluxe_command_categories, BH_MT_deluxe_command_sections)


def register():
    ops.register()
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    ops.unregister()
