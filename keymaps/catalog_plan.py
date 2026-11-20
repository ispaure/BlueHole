"""Pure catalog compiler. Availability is a supplied snapshot, never a bpy read."""
from dataclasses import replace
from . import descriptors as contract
from .deluxe_schema import event_descriptor, scope_descriptor
from .dispatch_policy import reviewed_groups
from .provider_policy import command_addon, required_class

OBJECT_NON_MODAL_SCOPES = frozenset(contract.KeymapScope('Object Non-modal', is_tool=is_tool)
                                   for is_tool in (None, False))
OBJECT_MODE = contract.KeymapScope('Object Mode')
DOPESHEET = contract.KeymapScope('Dopesheet', space_type='DOPESHEET_EDITOR')
FRAMES = contract.KeymapScope('Frames')
DOPESHEET_JUMP_EVENTS = frozenset(
    contract.KeymapEvent(key, **{modifier: 1})
    for key in ('LEFT_ARROW', 'RIGHT_ARROW') for modifier in ('ctrl', 'oskey'))
COLLECTION_NUMBER_EVENTS = frozenset(contract.KeymapEvent(key) for key in (
    'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'ZERO'))
MODE_OPERATORS = frozenset({'object.mode_set', 'object.mode_set_with_submode'})
CONTEXT_MODE_OPERATORS = frozenset({'object.bh_face_select_or_pose'})
NODE_DRAG_CHAIN = 'parity-chain-f46ef69f5ead'
NODE_LINK_TARGET = contract.KeymapTarget('node.bh_link_socket')


def profile_assignment_id(request_id):
    """Map a runtime companion back to its editable assignment."""
    return request_id.partition(':')[0]


class CatalogPlanner:
    def __init__(self, defaults):
        self.feature_categories = {row['feature']: defaults['sections'][row['section']]['category']
                                   for row in defaults['assignments'].values()}

    @staticmethod
    def section_enabled(catalog, preferences, section_id):
        section = catalog['sections'].get(section_id)
        if section is None:
            return False
        category = catalog['categories'][section['category']]
        return section.get('required', False) or (
            bool(preferences.keymap.enable_keymaps)
            and category.get('enabled', True) and section.get('enabled', True))

    def plan(self, catalog, preferences, *, required_only=False, assignment_ids=None, available_operators=frozenset()):
        sections = catalog['sections']
        state = {id_: (bool(section.get('required')) if required_only else
                       self.section_enabled(catalog, preferences, id_))
                 for id_, section in sections.items()}
        groups = {}
        node_drag = None
        commands = catalog['commands']
        dispatch_groups = reviewed_groups(catalog)
        rows = catalog['assignments'].items() if assignment_ids is None else (
            (id_, catalog['assignments'][id_]) for id_ in assignment_ids)
        for id_, row in sorted(rows, key=lambda entry: entry[1]['order']):
            if not (row.get('required') or state[row['section']] and row.get('enabled', True)):
                continue
            category = self.feature_categories.get(row['feature'], sections[row['section']]['category'])
            owner = 'legacy:' + self._category_label(category) + ':deluxe-' + row['feature']
            scope = scope_descriptor(row['scope'])
            event = event_descriptor(catalog['events'][row['event']])
            command = commands[row['command']]
            if not command.get('operator') and not command.get('modal_value'):
                continue
            samples = row.get('samples', ())
            request = contract.KeymapAssignment(
                id_, scope, event, self.target(command), declared_properties_only=True,
                active=row.get('active', True), ledger_id=catalog['base']['ledger'] if samples else '',
                sample_id=samples[0] if samples else '',
                requires_operator='operator' in command and (bool(command.get('provider')) or command['operator'] not in available_operators),
                dispatch_group=row.get('dispatch_group', '') if row.get('dispatch_group') in dispatch_groups else '',
                required_addon=command_addon(command),
                required_class=required_class(command))
            requests = groups.setdefault(owner, [])
            requests.append(request)
            if request.active and request.dispatch_group == NODE_DRAG_CHAIN:
                node_drag = owner, request
            # The viewport dispatches Object Mode before Object Non-modal.
            # Give compatible native mode changes a chance before stock collection
            # selection. The original route remains available in other modes.
            if (request.active and scope in OBJECT_NON_MODAL_SCOPES
                    and replace(event, repeat=False) in COLLECTION_NUMBER_EVENTS
                    and (command.get('operator') in CONTEXT_MODE_OPERATORS
                         or command.get('operator') in MODE_OPERATORS
                         and command['properties'].get('mode') not in (None, 'OBJECT'))):
                requests.append(replace(request, request_id=id_ + ':object-mode', scope=OBJECT_MODE))
            # Frames gets these presses before Dopesheet. Give the Deluxe
            # frame jump a scoped route without disabling the stock time jump.
            if (request.active and scope == DOPESHEET
                    and replace(event, repeat=False) in DOPESHEET_JUMP_EVENTS
                    and command.get('operator') == 'screen.frame_jump'):
                requests.append(replace(request, request_id=id_ + ':dopesheet-frames', scope=FRAMES,
                                        target=contract.KeymapTarget('wm.bh_dopesheet_frame_jump',
                                                                     command['properties']),
                                        dispatch_group=''))
        if node_drag:
            # Blender prepends add-on bindings. Give the stock socket handler
            # first refusal before the reviewed Deluxe translation chain.
            owner, request = node_drag
            groups[owner + ':node-socket'] = [replace(
                request, request_id=request.request_id + ':node-socket', target=NODE_LINK_TARGET,
                requires_operator=True)]
        return state, groups

    @staticmethod
    def _category_label(category):
        return 'UV' if category == 'uv' else category.capitalize()

    @staticmethod
    def target(row):
        if 'modal_value' in row:
            return contract.KeymapTarget(modal_value=row['modal_value'])
        return contract.KeymapTarget(row['operator'], row['properties'])

