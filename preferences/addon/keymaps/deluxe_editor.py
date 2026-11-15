"""Context-grouped bindings inside Blue Hole's Keymaps preferences."""

import sys
import json
import textwrap

import bpy
from bl_keymap_utils import keymap_hierarchy

from . import deluxe_editor_ops as ops
from .deluxe_editor_model import (binding_context_path, binding_context_tree,
                                  context_label, display_value, key_filter, scope_key, shortcut, title)
from ....keymaps.deluxe_schema import assignment_required, same_value

_pending_icons = None


def pending_icon(kind):
    global _pending_icons
    if _pending_icons is None:
        from pathlib import Path
        import bpy.utils.previews
        _pending_icons = bpy.utils.previews.new()
        root = Path(__file__).resolve().parent / 'icons'
        for name in ('ADD', 'REMOVE', 'FILE_REFRESH'):
            _pending_icons.load(name, str(root / ('pending-' + name.lower() + '.png')), 'IMAGE')
    return _pending_icons[kind if kind in _pending_icons else 'ADD'].icon_id


def release_pending_icons():
    global _pending_icons
    from . import colored_labels
    colored_labels.clear()
    if _pending_icons is not None:
        import bpy.utils.previews
        bpy.utils.previews.remove(_pending_icons)
        _pending_icons = None


COMPACT_WIDTH = 440
DETAIL_PANE_MIN_WIDTH = 680
TWO_COLUMN_FIELDS_MIN_WIDTH = 520
ASSIGNMENT_TABLE_MIN_WIDTH = 380
LIST_WIDTH_FRACTION = 0.41


def balanced_rows(items, maximum=12):
    """Keep tab rows even, with at most `maximum` controls in each row."""
    items = list(items)
    count = (len(items) + maximum - 1) // maximum
    if not count:
        return
    size, extra = divmod(len(items), count)
    offset = 0
    for index in range(count):
        length = size + (index < extra)
        yield items[offset:offset + length]
        offset += length


def find(text, query):
    return all(term in text.casefold() for term in query.casefold().split())


def detail_columns(layout, width, *, detail_first=False):
    if width >= DETAIL_PANE_MIN_WIDTH:
        split = layout.split(factor=LIST_WIDTH_FRACTION)
        return split.box().column(align=True), split.column(), width * LIST_WIDTH_FRACTION
    first = layout.column()
    layout.separator()
    second = layout.column()
    listing, detail = (second, first) if detail_first else (first, second)
    return listing.box().column(align=True), detail, width


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


def toggle(layout, table, id_, row, *, required=False, text=''):
    prop = 'binding_enabled' if table == 'assignments' else 'boolean'
    enabled = row.get('enabled', True) and (table != 'assignments' or row.get('active', True))
    control = ops.inline_value(ops.state(bpy.context), 'enabled', prop, enabled,
                               table=table, entry=id_)
    checkbox = layout.row(align=True)
    checkbox.enabled = not required
    checkbox.prop(control, prop, text=text, toggle=False)


def binding_filters(layout, current, preview):
    current.ensure_selection()
    view = ops.state(bpy.context)
    group = layout.box()
    bar = group.row(align=True)
    ops.operator_button(bar, 'all_bindings', 'All Bindings', icon='HOME',
                        depress=current.binding_all and not view.search)
    categories = current.catalog['categories']
    for entries in balanced_rows(categories.items()):
        tabs = group.row(align=True)
        for id_, row in entries:
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
    for entries in balanced_rows(['', *sections]):
        tabs = group.row(align=True)
        for id_ in entries:
            if not id_:
                ops.operator_button(tabs, 'all_subsections', 'All ' + category['label'],
                                    depress=current.binding_category_all)
            else:
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


def binding_list_data(current, preview, query, search_keys):
    catalog = current.catalog
    found = {}
    groups = {}
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
            found[id_] = command, event, meta
            groups.setdefault(scope_key(row['scope']), []).append(id_)
    for id_, rule in catalog['suppressions'].items():
        selector = rule['selector']
        if not current.accepts_binding({'section': rule['section'], 'scope': selector['scope']}):
            continue
        target = selector['target']
        command = ({'operator': target['idname'], 'properties': target['properties']}
                   if 'idname' in target else {'modal_value': target['modal_value']})
        meta = current.store.resolver.describe_command(command)
        event = shortcut(selector['event'])
        matches = (matches_key(selector['event']) if matches_key else
                   find(' '.join((meta['label'], target.get('idname', ''), event,
                                  context_label(selector['scope']),
                                  ops.SOURCE_LABELS[selector['source_role']] + ' disable rule')), query))
        if matches:
            found[id_] = meta['label'], event, meta
            groups.setdefault(scope_key(selector['scope']), []).append(id_)
    scopes = ops.assignment_scopes(current, bpy.context.window_manager.keyconfigs)
    if query:
        scopes = [scope for scope in scopes if scope_key(scope) in groups]
    contexts = binding_context_tree(keymap_hierarchy.generate(), groups, scopes)
    return found, contexts


def assignments(layout, current, preview, query, *, width, search_keys=False):
    if not binding_filters(layout, current, preview):
        return
    catalog = current.catalog
    key = (id(preview), query, search_keys, current.binding_all, current.binding_category_all,
           current.category, current.section)
    cached = current.display_cache.get('bindings')
    if cached is None or cached[0] != key:
        cached = key, binding_list_data(current, preview, query, search_keys)
        current.display_cache['bindings'] = cached
    found, contexts = cached[1]
    if not contexts:
        current.assignment = ''
        current.binding_selection_path = ()
        layout.label(text='No bindings match these filters')
        return
    listing, detail, list_width = detail_columns(layout, width, detail_first=True)
    detail_width = width - list_width if width >= DETAIL_PANE_MIN_WIDTH else width
    header = listing.row(align=True)
    removals = sum(id_ in catalog['suppressions'] for id_ in found)
    header.label(text=f'{len(found) - removals} assignments · {removals} removal rules')
    ops.operator_button(header, 'expand_binding_contexts', 'Expand All', icon='TRIA_DOWN')
    ops.operator_button(header, 'collapse_binding_contexts', 'Collapse All', icon='TRIA_RIGHT')
    listing.separator(factor=0.5)
    if current.assignment not in found:
        current.assignment = next(iter(found), '')
    path = binding_context_path(contexts, current.assignment)
    if path != current.binding_selection_path:
        for context_id in path:
            if current.binding_context_expansion.get(context_id) is False:
                del current.binding_context_expansion[context_id]
        current.binding_selection_path = path
    view = ops.state(bpy.context)
    row_key = repr((key, current.binding_state_revision, current.binding_selection_path,
                    tuple(current.binding_context_expansion.items())))
    ops.sync_binding_rows(view, row_key,
                          lambda: binding_rows(current, preview, contexts, found, searching=bool(query)),
                          current.assignment, focus_context=current.binding_focus_context)
    current.binding_focus_context = ''
    listing.template_list(BH_UL_deluxe_bindings.__name__, '', view, 'binding_rows', view,
                          'binding_index', rows=18, maxrows=18, sort_lock=True, item_dyntip_propname='tooltip')
    if current.assignment in catalog['assignments']:
        inspector(detail.box().column(), current, preview, current.assignment, width=detail_width)
    elif current.assignment in catalog['suppressions']:
        rule_inspector(detail.box().column(), current, preview, current.assignment)
    else:
        detail.label(text='Select a binding or choose Add New in a context')


def binding_tree_row(layout, depth):
    row = layout.row(align=True)
    if depth:
        row.separator(factor=depth)
    return row


def binding_rows(current, preview, contexts, found, *, searching, depth=0):
    for context in contexts:
        expanded = current.binding_context_expansion.get(
            context.id, searching or context.id in current.binding_selection_path)
        yield dict(kind='context', target=context.id, label=context.label, depth=depth, expanded=expanded)
        if not expanded:
            continue
        for id_ in context.bindings:
            command, event, meta = found[id_]
            is_rule = id_ in current.catalog['suppressions']
            state = preview['suppressions' if is_rule else 'assignments'][id_]
            icon, origin = current.binding_origin(id_, preview)
            if not state['eligible'] or not state.get('active', True):
                command += ' (Inactive)'
            yield dict(kind='binding', target=id_, label=command, shortcut=event, depth=depth + 1,
                       icon=icon, tooltip=origin, rule=is_rule, pending=current.binding_pending(id_, preview), removable=is_rule or state['editable'])
        if context.scope is not None:
            section = ''
            if current.binding_all and context.bindings:
                first = context.bindings[0]
                source = current.catalog['assignments'].get(first) or current.catalog['suppressions'][first]
                section = source['section']
            yield dict(kind='add', scope=json.dumps(context.scope), section=section, depth=depth + 1)
        yield from binding_rows(current, preview, context.children, found, searching=searching, depth=depth + 1)


class BH_UL_deluxe_bindings(bpy.types.UIList):
    """A bounded native viewport keeps the inspector beside a long context tree."""
    def draw_item(self, context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        row = binding_tree_row(layout, item.depth)
        if item.kind == 'context':
            row.alignment = 'LEFT'
            action = 'collapse_binding_context' if item.expanded else 'expand_binding_context'
            ops.operator_button(row, action, item.label, item.target,
                                icon='TRIA_DOWN' if item.expanded else 'TRIA_RIGHT', emboss=False)
        elif item.kind == 'add':
            row.alignment = 'LEFT'
            add = row.operator(ops.BH_OT_deluxe_add_binding.bl_idname, text='Add New', icon='ADD', emboss=False)
            add.scope, add.section = item.scope, item.section
        else:
            scale = context.preferences.system.ui_scale or 1
            width = context.region.width / scale
            list_width = width * LIST_WIDTH_FRACTION if width >= DETAIL_PANE_MIN_WIDTH else width
            content = row.split(factor=0.60, align=True) if list_width >= ASSIGNMENT_TABLE_MIN_WIDTH else row
            content.alert = item.icon == 'REMOVE' and not item.pending
            if item.pending:
                from .colored_labels import label as pending_label
                cell = content.row(align=True)
                cell.label(text='', icon_value=pending_icon(item.icon))
                available = max(40, list_width - 80 - item.depth * 6)
                pending_label(cell, item.label, width=available * (0.60 if content != row else 1) - 20)
            elif item.icon == 'REMOVE':
                # Native list selection keeps this label clickable without
                # turning Blender's alert colour into a filled button.
                content.label(text=item.label, icon=item.icon)
            else:
                ops.operator_button(content, 'assignment', item.label, item.target, icon=item.icon, emboss=False)
            if content != row:
                if item.pending:
                    pending_label(content, item.shortcut, width=available * 0.40)
                else:
                    content.label(text=item.shortcut)
            remove = row.row(align=True)
            remove.alert = False
            remove.enabled = item.removable
            if item.rule:
                ops.operator_button(remove, 'remove_rule', '', item.target, icon='X', emboss=False)
            else:
                remove.operator(ops.BH_OT_deluxe_remove_assignment.bl_idname, text='', icon='X',
                                emboss=False).assignment = item.target

    def draw_filter(self, _context, _layout):
        pass  # The common Name / Key-Binding search above the panes owns filtering.


def inspector(layout, current, preview, id_, *, width):
    row = current.catalog['assignments'][id_]
    meta = preview['commands'][row['command']]
    state = preview['assignments'][id_]
    event = current.catalog['events'][row['event']]
    heading = layout.row()
    heading.scale_y = 1.25
    heading.label(text=meta['label'])
    toggle(heading, 'assignments', id_, row, text='Enabled', required=not state['editable'])
    icon, origin = current.binding_origin(id_, preview)
    layout.label(text=origin, icon=icon)
    location = layout.column()
    location.enabled = state['editable']
    binding_categories(location, current, id_)
    if any(id_ in conflict for conflict in preview['conflicts']):
        layout.label(text='Another Deluxe binding uses this input in this context', icon='ERROR')
    if id_ in preview['inherited_conflicts']:
        layout.label(text='Overlaps Blender: ' + ', '.join(preview['inherited_conflicts'][id_]), icon='INFO')
    if any(id_ in group for group in preview.get('potential_overlaps', ())):
        layout.label(text='Possible input overlap (wildcard/modifier/repeat); dispatch depends on context.', icon='INFO')

    keymap = layout.box().column(align=True)
    keymap.label(text='KEYMAP')
    controls = keymap.column(align=True)
    controls.enabled = state['editable']
    context = controls.row(align=True)
    context.label(text='Context')
    context.operator(ops.BH_OT_deluxe_context.bl_idname, text=context_label(row['scope']), icon='VIEWZOOM').assignment = id_
    shortcut_controls(controls, id_, event, compact=width < COMPACT_WIDTH)
    if not state['editable']:
        keymap.label(text='Required shortcut', icon='LOCKED')

    command = layout.box().column(align=True)
    command.label(text='COMMAND')
    if 'modal_value' in current.catalog['commands'][row['command']]:
        command.label(text='Modal action: ' + current.catalog['commands'][row['command']]['modal_value'])
        return
    control = ops.inline_value(ops.state(bpy.context), 'operator', 'operator_id',
                               current.catalog['commands'][row['command']]['operator'],
                               command=row['command'], assignment=id_)
    field = command.row()
    field.enabled = state['editable']
    field.prop(control, 'operator_id', text='Operator')
    if meta['availability'] != 'available':
        command.label(text=('Choose an operator to see its properties' if not current.catalog['commands'][row['command']]['operator']
                            else 'Operator unavailable; properties appear when it is available'), icon='INFO')
    elif meta['dependency']:
        command.label(text=f"Requires {meta['dependency']}", icon='INFO')
    command_fields(layout, current, row['command'], width=width, assignment=id_)


def binding_categories(layout, current, id_):
    row = current.catalog['assignments'].get(id_) or current.catalog['suppressions'][id_]
    section = current.catalog['sections'][row['section']]
    view = ops.state(bpy.context)
    fields = layout.row(align=True)
    categories = [(key, item['label'], '') for key, item in current.catalog['categories'].items()
                  if any(not current.catalog['sections'][s].get('required') for s in current.sections(key))]
    control = ops.inline_value(view, 'binding_category', 'option', section['category'], assignment=id_, items=categories)
    category = fields.column(align=True)
    category.label(text='Category')
    category.prop(control, 'option', text='')
    sections = [(key, current.catalog['sections'][key]['label'], '') for key in current.sections(section['category'])
                if not current.catalog['sections'][key].get('required') or key == row['section']]
    control = ops.inline_value(view, 'binding_section', 'option', row['section'], assignment=id_, items=sections)
    subsection = fields.column(align=True)
    subsection.label(text='Subsection')
    subsection.prop(control, 'option', text='')


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
    key = ops.inline_value(view, 'type', 'option', event['type'],
                           assignment=assignment, items=options['type'])
    line.prop(key, 'option', text='')
    line.operator(ops.BH_OT_deluxe_capture.bl_idname,
                  text='Input Key…' if capturing else '',
                  icon='EVENT_A', depress=capturing).assignment = assignment
    trigger = layout.row(align=True)
    phase = ops.inline_value(view, 'value', 'option', event.get('value', 'PRESS'),
                             assignment=assignment, items=options.get('value', ()))
    trigger.prop(phase, 'option', text='')
    repeat = trigger.row(align=True)
    repeat.enabled = input_type == 'KEYBOARD' and event.get('value', 'PRESS') in {'PRESS', 'ANY'}
    control = ops.inline_value(view, 'repeat', 'repeat', event.get('repeat', False), assignment=assignment)
    repeat.prop(control, 'repeat', text='Repeat', toggle=False)
    modifier_row = layout if compact else layout.split(factor=0.64, align=True)
    mods = modifier_row.row(align=True)
    any_mod = ops.inline_value(view, 'any', 'any_modifier', event.get('any', False), assignment=assignment)
    mods.prop(any_mod, 'any_modifier', text='Any', toggle=True)
    controls = mods.row(align=True)
    controls.enabled = not event.get('any', False)
    oskey = {'darwin': 'Cmd', 'win32': 'Win'}.get(sys.platform, 'OS Key')
    modifiers = [('shift', 'Shift'), ('ctrl', 'Ctrl'), ('alt', 'Alt'), ('oskey', oskey)]
    if 'hyper' in bpy.types.KeyMapItem.bl_rna.properties:
        modifiers.append(('hyper', 'Hyper'))
    for key, label in modifiers:
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
    cached = current.display_cache.get('command_fields')
    if cached is None or cached[0] != id_:
        cached = id_, current.store.resolver.describe_command(command, include_unset=True)
        current.display_cache['command_fields'] = cached
    meta = cached[1]
    properties = command.get('properties', {})
    fields = meta['fields']
    view = ops.state(bpy.context)
    editable = not assignment_required(current.catalog, current.catalog['assignments'][assignment])
    group = layout.box()
    group.label(text='PROPERTIES')
    if fields:
        grid = group.grid_flow(columns=2 if width >= TWO_COLUMN_FIELDS_MIN_WIDTH else 1, align=True)
        for name, field in fields.items():
            value = properties.get(name, field.get('default'))
            label = field.get('label', title(name))
            cell = grid.row(align=True)
            prop = ops.INLINE_VALUES.get(field.get('type'))
            can_edit = editable and field.get('editable')
            if can_edit and prop and not (field['shape'] or field['flags']):
                control = ops.inline_value(view, name, prop, value,
                                           command=id_, assignment=assignment, items=field['enum_items'])
                cell.prop(control, prop, text=label)
            else:
                if value is not None:
                    label += ': ' + display_value(value)
                if can_edit:
                    op = cell.operator(ops.BH_OT_deluxe_field.bl_idname, text=label, icon='GREASEPENCIL')
                    op.command, op.field, op.assignment = id_, name, assignment
                else:
                    cell.label(text=label, icon='LOCKED')
            if can_edit and name in properties:
                reset = cell.row(align=True)
                reset.alignment = 'RIGHT'
                op = reset.operator(ops.BH_OT_deluxe_inline_edit.bl_idname, text='Reset')
                op.command, op.field, op.assignment = id_, name, assignment
    if not fields:
        group.label(text='No properties available' if meta['availability'] != 'available' else 'No properties', icon='INFO')


def rule_inspector(layout, current, preview, id_):
    rule = current.catalog['suppressions'][id_]
    selector = rule['selector']
    target = selector['target']
    icon, origin = current.binding_origin(id_, preview)
    layout.label(text=origin, icon=icon)
    toggle(layout, 'suppressions', id_, rule, text='Enable Rule')
    binding_categories(layout, current, id_)
    keymap = layout.box()
    keymap.label(text='KEYMAP')
    keymap.label(text=context_label(selector['scope']))
    keymap.label(text=shortcut(selector['event']))
    command = layout.box()
    command.label(text='COMMAND')
    command.label(text=target.get('idname', target.get('modal_value', '')))
    properties = layout.box()
    properties.label(text='PROPERTIES')
    for name, value in target.get('properties', {}).items():
        properties.label(text=f'{title(name)}: {display_value(value)}')
    if not target.get('properties'):
        properties.label(text='No overridden properties')
    if 'replacement' in rule:
        layout.label(text='Replacement: ' + ops.command_name(current, rule['replacement']))
    status = preview['suppressions'][id_]
    layout.label(text=current.rule_status(id_, preview), icon='INFO')
    if rule.get('disable'):
        if not status['eligible']:
            layout.label(text='Original shortcut left unchanged by this rule')
        elif selector['source_role'] == 'addon':
            layout.label(text='Applies automatically when the add-on registers this shortcut')
        layout.label(text='Disable or remove this rule to keep the original binding')
    actions = layout.row(align=True)
    ops.operator_button(actions, 'remove_rule', 'Restore Binding' if rule.get('disable') else 'Remove Rule', id_,
                        icon='LOOP_BACK')


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
    notice.label(text='Editing shipped defaults' if current.store.edit_defaults else 'Personal keymap profile',
                 icon='ERROR' if current.store.edit_defaults else 'USER')
    message = ('These edits change the addon catalog. Publish them with the addon to retain them in updates.'
               if current.store.edit_defaults else 'Saved shortcuts and section choices are kept when Blue Hole updates.')
    for line in textwrap.wrap(message, width=max(24, int((width - 40) / 7))):
        notice.label(text=line)
    layout.separator()
    search_box = layout.box()
    search = search_box.row(align=True)
    search.prop(view, 'search_mode', text='')
    placeholder = ('Search by Key-Binding' if view.search_mode == 'KEY'
                   else 'Search by Name')
    search.prop(view, 'search', text='', icon='VIEWZOOM', placeholder=placeholder)
    layout.separator()
    try:
        preview = current.preview()
    except ops.ERRORS as error:
        layout.label(text=str(error), icon='ERROR')
    else:
        query = view.search.strip()
        assignments(layout, current, preview, query, width=width, search_keys=view.search_mode == 'KEY')
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
    apply.alignment = actions.alignment
    apply.enabled = current.dirty or bool(current.store.load_issue)
    ops.operator_button(apply, 'apply', 'Save and Apply Changes', icon='CHECKMARK', depress=apply.enabled)
    discard = actions.row(align=True)
    discard.alignment = actions.alignment
    discard.enabled = current.dirty
    ops.operator_button(discard, 'discard', 'Discard', emboss=False)
    undo = actions.row(align=True)
    undo.alignment = actions.alignment
    undo.enabled = current.can_undo
    undo.operator(ops.BH_OT_deluxe_undo.bl_idname, text='Undo', icon='LOOP_BACK', emboss=False)
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
            'invalid_installed_catalog_using_factory': 'Installed catalog invalid. Using the release snapshot and your personal profile.',
        }
        bar.label(text=messages.get(current.store.load_issue, 'Profile recovery required'), icon='ERROR')
        for line in textwrap.wrap(current.store.load_error, width=60 if compact else 110):
            bar.label(text=line)
    for conflict in current.store.profile_conflicts[:5]:
        for line in textwrap.wrap(conflict, width=60 if compact else 110):
            bar.label(text=line, icon='INFO')
    if len(current.store.profile_conflicts) > 5:
        bar.label(text=f'{len(current.store.profile_conflicts)} update merge notices; save to accept the merged profile.', icon='INFO')


class BH_MT_deluxe_profile_actions(bpy.types.Menu):
    bl_label = 'Keymap Settings'

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.prop(context.preferences.inputs, 'invert_mouse_zoom')
        layout.separator()
        ops.operator_button(layout, 'reset', 'Reset Draft')
        ops.operator_button(layout, 'reload', 'Validate and Reload JSON Files', icon='FILE_REFRESH')
        layout.separator()
        ops.operator_button(layout, 'authoring_mode', 'Edit Shipped Defaults',
                            depress=ops.editor().store.edit_defaults)


classes = (BH_UL_deluxe_bindings, BH_MT_deluxe_categories, BH_MT_deluxe_sections, BH_MT_deluxe_section_actions,
           BH_MT_deluxe_profile_actions)


def register():
    ops.register()
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    release_pending_icons()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    ops.unregister()
