"""Assignments and Commands views inside Blue Hole's Keymaps preferences."""

import sys

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
    bl_label = 'Section Options'

    def draw(self, _context):
        current = ops.editor()
        section = current.catalog['sections'].get(current.section)
        layout = self.layout
        layout.operator(ops.BH_OT_deluxe_section.bl_idname, text='Add Section', icon='ADD')
        if not section or section.get('required'):
            return
        layout.operator(ops.BH_OT_deluxe_section.bl_idname, text='Rename Section').section = current.section
        sections = current.sections()
        index = sections.index(current.section)
        for offset, label, icon in ((-1, 'Move Up', 'TRIA_UP'), (1, 'Move Down', 'TRIA_DOWN')):
            neighbor = index + offset
            if 0 <= neighbor < len(sections) and not current.catalog['sections'][sections[neighbor]].get('required'):
                ops.operator_button(layout, 'order', label, str(offset), icon=icon)
        has_entries = any(item['section'] == current.section for table in ('assignments', 'suppressions')
                          for item in current.catalog[table].values())
        if not has_entries:
            ops.operator_button(layout, 'delete_section', 'Delete Empty Section', current.section, icon='TRASH')


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


def toggle(layout, table, id_, row, *, required=False, text=''):
    button = layout.row(align=True)
    button.enabled = not required
    ops.operator_button(button, table, text, id_,
                        icon='CHECKBOX_HLT' if row.get('enabled', True) else 'CHECKBOX_DEHLT')


def group_controls(layout, current, preview, *, compact):
    categories, sections = current.catalog['categories'], current.catalog['sections']
    if current.category not in categories:
        current.category = next(iter(categories), '')
    section_ids = current.sections()
    if current.section not in section_ids:
        current.section = next(iter(section_ids), '')
    if not categories:
        return
    group = layout.box()
    group.label(text='BROWSE SECTIONS')
    row = group.row(align=True)
    category = categories[current.category]
    toggle(row, 'categories', current.category, category)
    row.menu(BH_MT_deluxe_categories.__name__, text=category['label'])
    if compact:
        row = group.row(align=True)
    section = sections.get(current.section)
    if section:
        toggle(row, 'sections', current.section, section, required=section.get('required', False))
        row.menu(BH_MT_deluxe_sections.__name__, text=section['label'])
    row.menu(BH_MT_deluxe_section_actions.__name__, text='', icon='THREE_DOTS')
    if section is None:
        return
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


def sections_view(layout, current, preview, *, width):
    """Show group choices without opening the assignment editor."""
    from ...prefs import prefs

    categories = current.catalog['categories']
    if not categories:
        layout.label(text='No shortcut categories')
        return
    if current.feature_category not in categories:
        current.feature_category = next(iter(categories))
    category_id = current.feature_category
    category = categories[category_id]
    category_ids = tuple(categories)
    columns = 5 if width >= DETAIL_PANE_MIN_WIDTH else 3
    for start in range(0, len(category_ids), columns):
        tabs = layout.row(align=True)
        for id_ in category_ids[start:start + columns]:
            ops.operator_button(tabs, 'feature_category', categories[id_]['label'], id_, depress=id_ == category_id)

    box = layout.box()
    category_line = box.row()
    category_line.alignment = 'LEFT'
    toggle(category_line, 'categories', category_id, category, text=f"Enable {category['label']} Shortcuts")
    enabled = category.get('enabled', True)
    if enabled and category.get('switch'):
        owner, name = preference_switch(prefs(), category['switch'])
        if not getattr(owner, name):
            box.prop(owner, name)
    box.separator(factor=0.5)

    waiting = {}
    section_ids = current.sections(category_id)
    for id_, row in current.catalog['assignments'].items():
        state = preview['assignments'][id_]
        if row['section'] not in section_ids or not (state['eligible'] and state['active']):
            continue
        meta = preview['commands'][row['command']]
        if meta['availability'] == 'waiting_for_provider':
            waiting.setdefault(row['section'], set()).add(meta['dependency'])
    for section_id in section_ids:
        section = current.catalog['sections'][section_id]
        items = box.column(align=True)
        line = items.row(align=True)
        line.alignment = 'LEFT'
        label = section['label']
        if section.get('required'):
            line.label(text=f'{label} (required)', icon='LOCKED')
        else:
            toggle(line, 'sections', section_id, section, text=label)
            if not preview['sections'][section_id] and section.get('enabled', True):
                line.label(text='Inactive', icon='PAUSE')
        ops.operator_button(line, 'show_assignments', 'View Assignments', section_id, icon='FORWARD', emboss=False)
        if section_id in waiting:
            items.label(text='Waiting for ' + ', '.join(sorted(waiting[section_id])), icon='INFO')
        if enabled and section.get('enabled', True) and section.get('switch'):
            owner, name = preference_switch(prefs(), section['switch'])
            if not getattr(owner, name):
                items.prop(owner, name)


class BH_MT_deluxe_assignment_actions(bpy.types.Menu):
    bl_label = 'Assignment Actions'

    def draw(self, _context):
        current = ops.editor()
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator(ops.BH_OT_deluxe_shortcut.bl_idname, text='New Shortcut', icon='EVENT_A')
        layout.operator(ops.BH_OT_deluxe_binding_picker.bl_idname, icon='VIEWZOOM').section = current.section


def assignments(layout, current, preview, query, *, width, search_keys=False):
    compact = width < COMPACT_WIDTH
    group_controls(layout, current, preview, compact=compact)
    catalog = current.catalog
    section = catalog['sections'].get(current.section)
    if section:
        row = layout.row(align=True)
        row.alignment = 'LEFT'
        if not section.get('required'):
            row.operator(ops.BH_OT_deluxe_mapping.bl_idname, text='Add Assignment', icon='ADD')
            row.menu(BH_MT_deluxe_assignment_actions.__name__, text='Actions')
        if compact and not section.get('required'):
            row = layout.row(align=True)
            row.alignment = 'LEFT'
        ops.operator_button(row, 'show_section_commands', 'View Commands', current.section, icon='FORWARD', emboss=False)
    found = []
    matches_key = None
    if query and search_keys:
        events = bpy.types.Event.bl_rna.properties['type'].enum_items
        matches_key = key_filter(query, {key: item.name for key, item in events.items()})
    for id_, row in sorted(catalog['assignments'].items(), key=lambda entry: entry[1]['order']):
        if not query and row['section'] != current.section:
            continue
        meta = preview['commands'][row['command']]
        command = meta['label']
        event_data = catalog['events'][row['event']]
        event = shortcut(event_data)
        scope = context_label(row['scope'])
        owner = meta['owner']
        operator = catalog['commands'][row['command']].get('operator', '')
        if matches_key:
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
        listing.label(text=f'{len(found)} {"matching " if query else ""}'
                           f'{"assignment" if len(found) == 1 else "assignments"}')
        listing.separator(factor=0.5)
        if current.assignment not in {item[0] for item in found}:
            current.assignment = found[0][0]
        if table:
            name, key, scope_column = assignment_columns(listing)
            name.label(text='Command')
            key.label(text='Shortcut')
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
            if table and waiting:
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
        layout.label(text='No matching assignments' if query else 'No assignments in this section')
    if section:
        rules(layout, current, preview)


def inspector(layout, current, preview, id_, *, width):
    row = current.catalog['assignments'][id_]
    meta = preview['commands'][row['command']]
    state = preview['assignments'][id_]
    event = current.catalog['events'][row['event']]
    heading = layout.row()
    heading.scale_y = 1.25
    heading.label(text=meta['label'])
    command = current.catalog['commands'][row['command']]
    identity = layout.row(align=True)
    identity.alignment = 'LEFT'
    if command.get('operator'):
        identity.label(text=command['operator'], icon='CONSOLE')
        if width < COMPACT_WIDTH:
            identity = layout.row(align=True)
    if id_ not in current.defaults['assignments']:
        identity.label(text='Custom assignment')
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
    settings.label(text='SHORTCUT')
    shortcut_controls(settings.column(align=True), id_, event, compact=width < COMPACT_WIDTH)
    actions = settings.row(align=True)
    actions.alignment = 'LEFT'
    toggle(actions, 'assignments', id_, row, text='Enabled')
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
    ops.operator_button(disclosure, 'linked_shortcut', f'Shared Shortcut · {len(linked)} Assignments',
                        event_id, icon='TRIA_DOWN' if expanded else 'TRIA_RIGHT', emboss=False)
    if not expanded:
        return
    if all(preview['assignments'][id2]['editable'] for id2 in linked):
        actions = box.row()
        actions.alignment = 'LEFT'
        op = actions.operator(ops.BH_OT_deluxe_capture.bl_idname,
                              text=f'Change All {len(linked)}', icon='LINKED')
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
    line = layout.row(align=True)
    line.alignment = 'LEFT'
    line.operator(ops.BH_OT_deluxe_capture.bl_idname, text=key_label(event['type']), icon='EVENT_A').assignment = assignment
    controls = [('value', 'PRESS', '')]
    if event.get('map_type', 'KEYBOARD') == 'KEYBOARD':
        controls.append(('repeat', False, 'Repeat'))
    for key, default, label in controls:
        value = event.get(key, default)
        prop = 'option' if key == 'value' else 'boolean'
        control = ops.inline_value(view, key, prop, value, assignment=assignment, items=options.get(key, ()))
        cell = line.row(align=True)
        cell.enabled = key != 'repeat' or event.get('value', 'PRESS') in {'PRESS', 'ANY'}
        cell.prop(control, prop, text=label)
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
    meta = current.store.resolver.describe_command(command, include_unset=not assignment)
    properties = command.get('properties', {})
    fields = meta['fields']
    editable = all(not current.catalog['sections'][current.catalog['assignments'][aid]['section']].get('required')
                   for aid in current.draft.uses('commands', id_))
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
                                           command=id_, items=field['enum_items'])
                cell.prop(control, prop, text=label)
                if explicit:
                    reset = cell.operator(ops.BH_OT_deluxe_inline_edit.bl_idname, text='', icon='X')
                    reset.command, reset.field = id_, name
                if assignment:
                    edit = cell.operator(ops.BH_OT_deluxe_field.bl_idname, text='', icon='DUPLICATE')
                    edit.command, edit.field, edit.assignment = id_, name, assignment
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
    filters.label(text='FILTER COMMANDS')
    row = filters.row(align=True)
    category = categories.get(current.command_category, {})
    section = current.catalog['sections'].get(current.command_section, {})
    row.menu(BH_MT_deluxe_command_categories.__name__,
             text=category.get('label', 'All Categories'))
    if width < COMPACT_WIDTH:
        row = filters.row(align=True)
    section_menu = row.row(align=True)
    section_menu.enabled = bool(current.command_category)
    section_menu.menu(BH_MT_deluxe_command_sections.__name__,
                      text=section.get('label', 'All Sections'))
    if section:
        toggle(row, 'sections', current.command_section, section, required=section.get('required', False))
        if width < COMPACT_WIDTH:
            row = filters.row(align=True)
            row.alignment = 'LEFT'
        ops.operator_button(row, 'show_assignments', 'View Assignments', current.command_section, icon='FORWARD')
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
        listing.label(text=STATUS_LABELS.get(meta['availability'], meta['owner']), icon='BLANK1')
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
    if uses:
        layout.label(text=f'Used by {len(uses)} assignment{"s" if len(uses) != 1 else ""}')
        links = layout.grid_flow(columns=2 if width >= TWO_COLUMN_FIELDS_MIN_WIDTH else 1, align=True)
        for section_id in sections:
            section = current.catalog['sections'][section_id]
            category = current.catalog['categories'][section['category']]
            label = f"{category['label']} / {section['label']}"
            ops.operator_button(links, 'show_assignments', label, section_id, icon='FORWARD', emboss=False)
    else:
        layout.label(text='No assignment uses this command')
    command_fields(layout, current, id_, width=width)


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


def draw(context, layout, settings):
    try:
        current = ops.editor()
        view = ops.state(context)
    except ops.ERRORS:
        layout.label(text='The Deluxe profile editor is waiting for Blender keymaps', icon='INFO')
        return
    layout.operator_context = 'INVOKE_DEFAULT'
    scale = context.preferences.system.ui_scale or 1
    width = context.region.width / scale if context.region else 0
    transaction_controls(layout, current, settings, compact=width < COMPACT_WIDTH)
    layout.separator()
    toolbar = layout.row(align=True)
    toolbar.prop(view, 'tab', expand=True)
    if view.tab != 'SECTIONS':
        layout.separator(factor=0.5)
        search_box = layout.box()
        search_box.label(text='SEARCH')
        search = search_box
        if view.tab == 'ASSIGNMENTS':
            fields = search_box.split(factor=0.38 if width < COMPACT_WIDTH else 0.22, align=True)
            fields.prop(view, 'search_mode', text='')
            search = fields.row(align=True)
        placeholder = ('Search by Key-Binding' if view.tab == 'ASSIGNMENTS' and view.search_mode == 'KEY'
                       else 'Search by Name')
        search.prop(view, 'search', text='', icon='VIEWZOOM', placeholder=placeholder)
    layout.separator()
    try:
        preview = current.preview()
    except ops.ERRORS as error:
        layout.label(text=str(error), icon='ERROR')
    else:
        query = view.search.strip()
        if view.tab == 'SECTIONS':
            sections_view(layout, current, preview, width=width)
        elif view.tab == 'ASSIGNMENTS':
            assignments(layout, current, preview, query, width=width, search_keys=view.search_mode == 'KEY')
        else:
            commands(layout, current, preview, query, width=width)
        if view.tab != 'SECTIONS' and current.dirty and preview['conflicts']:
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
    label = 'Save Recovered Profile' if current.store.load_issue and not current.dirty else 'Save and Apply Changes'
    ops.operator_button(apply, 'apply', label, icon='CHECKMARK', depress=apply.enabled)
    discard = actions.row(align=True)
    discard.enabled = current.dirty
    ops.operator_button(discard, 'discard', 'Discard', emboss=False)
    if current.dirty:
        bar.label(text='Unsaved keymap changes', icon='DOT')
    if current.message and current.message != 'Changes staged':
        bar.label(text=current.message, icon='INFO')
    if current.store.load_issue:
        messages = {
            'invalid_profile_recovered_previous': 'Profile file invalid. The last saved copy is active.',
            'invalid_profile_recovered_defaults': 'Profile file invalid. A valid profile is active.',
            'profile_saved_recovery_copy_unavailable': 'Profile saved. The recovery copy could not be updated.',
        }
        bar.label(text=messages.get(current.store.load_issue, 'Profile recovery required'), icon='ERROR')


class BH_MT_deluxe_profile_actions(bpy.types.Menu):
    bl_label = 'Keymap Settings'

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.prop(context.preferences.inputs, 'invert_mouse_zoom')
        layout.operator('wm.bh_reset_deluxe_keymaps', text='Reset Feature Switches')
        layout.separator()
        ops.operator_button(layout, 'reset', 'Reset Draft')
        ops.operator_button(layout, 'reload', 'Reload Profile', icon='FILE_REFRESH')


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
