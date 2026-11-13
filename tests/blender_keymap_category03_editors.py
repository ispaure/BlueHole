"""Isolated native proof of guarded Shift-wheel editor selection."""

import math


TARGETS = {
    'dopesheet': {
        'UP': ('action.select_more', 'c6ab041568a381b437574c6fbd40ca10a6d5f7fcdca9606977669b4129e10070'),
        'DOWN': ('action.select_less', '35ed259e5614c01c82e2dff057cc154ee4035a6897920ae121748fcf7f9fe169'),
    },
    'graph': {
        'UP': ('graph.select_more', '666a1aa5c96634fc7adf27556381de57f11561042afb72555a963ceaec5aac3b'),
        'DOWN': ('graph.select_less', '490423c8e75e32933e0e9cc54da79ce2074cf5ccfefb901605e67eadf4950238'),
    },
    'node': {
        'UP': ('node.select_linked_to', '1fbdfeda4b21c604e00c04d1c33f5b81612f1973e69c5908e9b37c12cd2c659a'),
        'DOWN': ('node.select_linked_from', '563a59cd97781701841e15ba1a89db510b750a5cb2e6d83c683885fbfa4977dc'),
    },
    'sequencer': {
        'UP': ('sequencer.select_more', '4c4a07c67c9977a151a695ae90c6efd5d4ea6860480e384c25decfe6ead47389'),
        'DOWN': ('sequencer.select_less', 'e3ac615438be89a3aea5a8ade6c3ce382f510aab38e4a1615fb65575c9a54eca'),
    },
}
SCROLL_ROWS = {
    'UP': ('217e62d492bcf3dcd6f2bb95205c8d8830fb8788782d348f43cd949ea6296813',
           'b05ae052799f48555368862eefc12fabd26fb613a79bafdc3b6f1944de86d682'),
    'DOWN': ('76b861597996c8ce546e5ca9504d2c8ce59cfb799c1172cbad9803e8aa1a0edb',
             '35f7ab776087679ae004a903fe4e0510bc264a6ab756d3efe624c84faa2c9925'),
}
DIRECTIONS = ('UP', 'DOWN')
PROBE_SCOPE = dict(name='View2D', space_type='EMPTY', region_type='WINDOW',
                   is_modal=False, is_tool=None)
EDITOR_SCOPES = {
    'dopesheet': 'Dopesheet', 'graph': 'Graph Editor', 'node': 'Node Editor',
    'sequencer': 'Sequencer',
}
CONTROL_SPACES = {
    'dopesheet': 'DOPESHEET_EDITOR', 'graph': 'GRAPH_EDITOR', 'node': 'NODE_EDITOR',
    'sequencer': 'SEQUENCE_EDITOR',
}
CONTROL_KEYS = {'window': 'F21', 'editor': 'F22'}
ERRORS = (AttributeError, KeyError, ReferenceError, RuntimeError, StopIteration,
          TypeError, ValueError)
PASSTHROUGH = ('image', 'nla', 'file_browser', 'timeline', 'sequencer_preview', 'node_without_tree')


class EditorCases:
    def __init__(self, steps, receipt, record, window, area, exporter, *,
                 probe=False, cluster='selection', input_controls=False, prime_readiness=False,
                 matched_endpoints=False):
        import bpy

        if cluster not in ('selection', 'passthrough'):
            raise ValueError('Unknown editor proof cluster')
        if input_controls and (probe or cluster != 'selection'):
            raise ValueError('Input controls require the read-only selection cluster')
        self.bpy, self.steps, self.receipt, self.record = bpy, steps, receipt, record
        self.window, self.area, self.exporter = window, area, exporter
        self.probe, self.cluster = probe, cluster
        self.input_controls = input_controls
        self.prime_readiness = prime_readiness
        self.matched_endpoints = matched_endpoints
        self.endpoint_label = None
        self.matched_baseline = None
        self.readiness = None
        self.control_class = None
        self.control_items, self.control_maps, self.control_callbacks = [], [], []
        self.configs = bpy.context.window_manager.keyconfigs
        self.owned, self.classes, self.callbacks = [], [], []
        self.created_map = None
        self.source_before = None
        self.fixture_object = None
        self.fixture_strips = []
        self.state = None

    def region(self):
        return next(region for region in self.area.regions if region.type == 'WINDOW')

    def context(self):
        return self.bpy.context.temp_override(window=self.window, area=self.area, region=self.region())

    def operator(self, idname):
        module, name = idname.split('.', 1)
        return getattr(getattr(self.bpy.ops, module), name)

    def guarded_kind(self, context):
        area, region = context.area, context.region
        if area is None or region is None or region.type != 'WINDOW':
            return None
        if area.type == 'DOPESHEET_EDITOR' and area.spaces.active.mode == 'DOPESHEET':
            return 'dopesheet'
        if area.type == 'GRAPH_EDITOR' and area.spaces.active.mode == 'FCURVES':
            return 'graph'
        if (area.type == 'NODE_EDITOR' and area.ui_type == 'CompositorNodeTree'
                and getattr(area.spaces.active, 'edit_tree', None) is not None):
            return 'node'
        if area.type == 'SEQUENCE_EDITOR' and area.spaces.active.view_type == 'SEQUENCER':
            return 'sequencer'
        return None

    def probe_class(self, direction):
        fixture = self
        suffix = direction.lower()

        def target(context):
            kind = fixture.guarded_kind(context)
            return TARGETS[kind][direction][0] if kind else None

        def poll(cls, context):
            idname = target(context)
            return bool(idname and fixture.operator(idname).poll())

        def execute(self, context):
            idname = target(context)
            if not idname or not fixture.operator(idname).poll():
                return {'PASS_THROUGH'}
            result = fixture.operator(idname)('EXEC_DEFAULT')
            fixture.callbacks.append({'direction': direction, 'target': idname,
                                      'result': sorted(result)})
            return result

        return type('WM_OT_deluxe_category03_editor_' + suffix, (self.bpy.types.Operator,), {
            '__module__': __name__,
            'bl_idname': 'wm.deluxe_category03_editor_' + suffix,
            'bl_label': 'Category 03 editor probe ' + direction,
            'poll': classmethod(poll),
            'execute': execute,
        })

    def capture(self, keymap):
        return self.exporter._capture_map(keymap, self.bpy.types.OperatorProperties)

    def source_maps(self):
        names = {'Window', 'View2D', 'Image', 'NLA Editor', 'File Browser',
                 *EDITOR_SCOPES.values()}
        return {
            role: [self.capture(keymap) for keymap in getattr(self.configs, role).keymaps
                   if keymap.name in names]
            for role in ('default', 'active', 'addon')
        }

    def merged_rows(self):
        return [self.capture(keymap) for keymap in self.configs.user.keymaps
                if keymap.name in ('View2D', *EDITOR_SCOPES.values())]

    def foreign_merged_maps(self):
        names = {'Window', 'View2D', 'Image', 'NLA Editor', 'File Browser', *EDITOR_SCOPES.values()}
        return [self.capture(keymap) for keymap in self.configs.user.keymaps if keymap.name in names]

    @staticmethod
    def exact_descriptor(direction):
        return {
            'target': 'wm.deluxe_category03_editor_' + direction.lower(),
            'event': {
                'type': f'WHEEL{direction}MOUSE', 'value': 'PRESS', 'shift': 1,
                'any': False, 'ctrl': 0, 'alt': 0, 'oskey': 0, 'hyper': 0,
                'key_modifier': 'NONE', 'direction': 'ANY', 'repeat': False, 'map_type': 'MOUSE',
            },
            'active': True, 'properties': {}, 'read_issues': {},
        }

    @staticmethod
    def exact_row(row, expected):
        return all(row.get(field) == value for field, value in expected.items())

    def describe(self):
        """Expose exact probe descriptors and owned merged identities to the host."""
        merged = self.merged_rows()
        return {
            'scope': PROBE_SCOPE,
            'bindings': {
                direction: {
                    'descriptor': self.exact_descriptor(direction),
                    'owned_addon_id': next((item.id for _, item in self.owned
                                            if item.idname == self.exact_descriptor(direction)['target']), None),
                    'merged_occurrences': [
                        {'scope': capture['scope'], 'item': row}
                        for capture in merged if capture['scope'] == PROBE_SCOPE
                        for row in capture['items']
                        if row['target'] == self.exact_descriptor(direction)['target']
                    ],
                }
                for direction in DIRECTIONS
            },
            'persistence': 'Host must verify user edits and save/reopen in separate owned runs',
        }

    def start(self):
        current = self.source_maps()
        unknown = self.property_read_issues(current)
        if self.readiness is not None:
            self.readiness['stable_source_snapshots'] = current == self.readiness['first_primed_source']
            self.readiness['primed_unknown_properties'] = self.property_read_issues(current)
            self.readiness['source_changed_during_priming'] = current != self.readiness['initial_source']
            if not self.readiness['stable_source_snapshots']:
                self.readiness['second_primed_source'] = current
            self.record('editor_readiness_checked')
            assert self.readiness['stable_source_snapshots'], 'Editor source snapshots did not stabilize'
            relevant_targets = {target for entries in TARGETS.values() for target, _ in entries.values()}
            relevant_targets.update(('view2d.scroll_up', 'view2d.scroll_down'))
            self.readiness['unreadable_relevant_targets'] = [
                row for row in unknown if row['target'] in relevant_targets]
            assert not self.readiness['unreadable_relevant_targets'], 'Relevant editor RNA is not readable'
        self.source_before = current
        self.state = {
            'stage': 'owned_probe' if self.probe else 'readonly_reference_or_factory',
            'cluster': self.cluster,
            'owner03_rows': {kind: {direction: row_id for direction, (_, row_id) in entries.items()}
                             for kind, entries in TARGETS.items()},
            'owner05_scroll_rows': {key: {'stock': stock, 'full': full}
                                    for key, (stock, full) in SCROLL_ROWS.items()},
            'source_before': self.source_before,
            'merged_before': self.merged_rows(),
            'installations': [],
            'releases': [],
            'unknown_properties_before': unknown,
            'complete_property_comparison': not unknown,
        }
        if self.input_controls:
            self.state['input_controls'] = {
                'keys': CONTROL_KEYS, 'installations': [], 'removed_rows': 0,
                'window_control_required_for_wheel_observation': True,
            }
        self.receipt['editor_handler_proof'] = self.state
        self.record('editor_handler_ready')

    @staticmethod
    def property_read_issues(sources):
        return [
            {'role': role, 'scope': keymap['scope'], 'item_id': row['blender_id'],
             'target': row['target'], 'issues': row['read_issues']}
            for role, maps in sources.items() for keymap in maps for row in keymap['items']
            if row['read_issues']
        ]

    def begin_readiness(self):
        initial = self.source_maps()
        self.readiness = {
            'initial_source': initial, 'initial_unknown_properties': self.property_read_issues(initial),
            'removed_rows': 0, 'installations': [], 'stable_source_snapshots': False,
        }
        self.receipt['editor_readiness'] = self.readiness
        self.install_input_controls(None)
        self.readiness['coordinates'] = self.point()
        self.readiness['expected_area'] = self.area.type
        self.event('MOUSEMOVE', 'NOTHING', point=self.readiness['coordinates'])
        self.record('editor_readiness_primer_installed')

    def deliver_readiness(self):
        self.event(CONTROL_KEYS['window'], 'PRESS', point=self.readiness['coordinates'])
        self.event(CONTROL_KEYS['window'], 'RELEASE', point=self.readiness['coordinates'])

    def finish_readiness(self):
        callbacks = self.control_callbacks[:]
        self.readiness['callbacks'] = callbacks
        merged_occurrences = self.readiness['installations'][0]['window']['merged_occurrences']
        delivered = any(callback['label'] == 'window' and callback['region'] == 'WINDOW'
                        and callback['area'] == self.readiness['expected_area']
                        for callback in callbacks)
        self.readiness['window_delivered'] = delivered
        self.release_input_controls()
        self.unregister_control_class()
        self.configs.update()
        self.record('editor_readiness_primer_removed')
        assert merged_occurrences == 1, 'Expected exactly one merged Window readiness primer'
        assert delivered, 'Window readiness primer did not receive native input'

    def capture_primed_source(self):
        self.readiness['first_primed_source'] = self.source_maps()
        if self.endpoint_label:
            self.readiness['first_primed_merged'] = self.foreign_merged_maps()

    def begin_matched_endpoint(self, label):
        """Use the same context and readiness lifecycle before and after ownership."""
        self.endpoint_label = label
        self.setup('dopesheet', 'UP')
        self.configs.update()
        self.begin_readiness()
        self.readiness['label'] = label
        self.readiness['context'] = {'area': self.area.type,
                                    'mode': self.area.spaces.active.mode,
                                    'region': self.region().type}
        endpoints = self.receipt.setdefault('editor_matched_endpoints', {
            'comparison': 'exact source and foreign merged snapshots; full read_issues retained',
            'endpoints': [],
        })
        endpoints['endpoints'].append(self.readiness)

    def finish_matched_endpoint(self):
        sources, merged = self.source_maps(), self.foreign_merged_maps()
        value = self.readiness
        value['source'] = sources
        value['foreign_merged'] = merged
        value['unknown_properties'] = self.property_read_issues(sources)
        value['stable_sources'] = sources == value['first_primed_source']
        value['stable_merged'] = merged == value['first_primed_merged']
        assert value['stable_sources'] and value['stable_merged'], 'Matched endpoint did not stabilize'
        relevant = {target for targets in TARGETS.values() for target, _ in targets.values()}
        relevant.update(('view2d.scroll_up', 'view2d.scroll_down'))
        source_rows = [row for maps in sources.values() for keymap in maps for row in keymap['items']]
        value['missing_relevant_targets'] = sorted(relevant - {row['target'] for row in source_rows})
        assert not value['missing_relevant_targets'], 'Relevant source selector is missing'
        value['relevant_target_unknowns'] = [row for row in source_rows
                                           if row['target'] in relevant and row['read_issues']]
        assert not value['relevant_target_unknowns'], 'Relevant selector property read failed'
        # Explicit, inherited sentinel rows are checked independently of the
        # fixture operators and the selected eight target declarations.
        sentinel_targets = {'Dopesheet': 'action.select_all', 'Graph Editor': 'graph.select_all',
                            'Node Editor': 'node.select_all', 'Sequencer': 'sequencer.select_all'}
        sentinels = []
        for name, target in sentinel_targets.items():
            matches = [row for keymap in sources['default'] if keymap['scope']['name'] == name
                       for row in keymap['items'] if row['target'] == target
                       and row['event']['type'] == 'A' and row['event']['value'] == 'PRESS'
                       and not any(row['event'][flag] for flag in ('shift', 'ctrl', 'alt', 'oskey', 'any'))]
            assert len(matches) == 1 and not matches[0]['read_issues'], (name, matches)
            sentinels.append({'map': name, 'row': matches[0]})
        value['readable_foreign_sentinels'] = sentinels
        if self.matched_baseline is None:
            self.matched_baseline = {'context': value['context'], 'source': sources, 'merged': merged}
            value['is_baseline'] = True
        else:
            value['context_matches'] = value['context'] == self.matched_baseline['context']
            value['strict_sources_equal'] = sources == self.matched_baseline['source']
            value['strict_foreign_merged_equal'] = merged == self.matched_baseline['merged']
            self.record('editor_matched_endpoint_compared')
            assert value['context_matches']
            assert value['strict_sources_equal'], 'Matched-context source comparison failed'
            assert value['strict_foreign_merged_equal'], 'Matched-context foreign merged comparison failed'
        self.endpoint_label = None
        self.record('editor_matched_endpoint_complete')

    def append_matched_endpoint(self, label):
        self.steps.extend((lambda: self.begin_matched_endpoint(label), self.deliver_readiness,
                           self.finish_readiness, self.capture_primed_source,
                           self.finish_matched_endpoint))

    def input_control_receipt(self):
        if self.state is None or self.endpoint_label:
            return self.readiness
        return self.state['input_controls']

    def install_input_controls(self, kind):
        scopes = {'window': ('Window', 'EMPTY')}
        if kind is not None:
            scopes['editor'] = (EDITOR_SCOPES[kind], CONTROL_SPACES[kind])
        keys = {CONTROL_KEYS[label] for label in scopes}
        occupied = [
            (keymap.name, item.type)
            for keymap in self.configs.user.keymaps for item in keymap.keymap_items
            if item.type in keys
        ]
        if occupied:
            raise ValueError(f'Control input keys already occur in merged maps: {occupied}')
        if self.control_class is None:
            bpy, callbacks = self.bpy, self.control_callbacks

            class WM_OT_deluxe_category03_input_control(bpy.types.Operator):
                bl_idname = 'wm.deluxe_category03_input_control'
                bl_label = 'Category 03 input delivery control'
                label: bpy.props.StringProperty()

                def execute(self, context):
                    callbacks.append({
                        'label': self.label,
                        'area': context.area.type if context.area else None,
                        'ui_type': context.area.ui_type if context.area else None,
                        'region': context.region.type if context.region else None,
                    })
                    return {'FINISHED'}

            bpy.utils.register_class(WM_OT_deluxe_category03_input_control)
            self.control_class = WM_OT_deluxe_category03_input_control

        maps = self.configs.addon.keymaps
        installation = {}
        for label, (name, space) in scopes.items():
            scope = {**PROBE_SCOPE, 'name': name, 'space_type': space}
            exact_maps = [km for km in maps if all(
                getattr(km, field, None) == value for field, value in scope.items()
            )]
            if len(exact_maps) > 1:
                raise ValueError(f'Ambiguous control scope: {name}')
            if exact_maps:
                keymap = exact_maps[0]
            else:
                before = {km.as_pointer() for km in maps}
                keymap = maps.new(name=name, space_type=space, region_type='WINDOW')
                if keymap.as_pointer() in before:
                    raise ValueError(f'Control map creation returned a foreign scope: {name}')
                self.control_maps.append(keymap)
            if self.capture(keymap)['scope'] != scope:
                raise ValueError(f'Control map scope readback differs: {name}')
            item = keymap.keymap_items.new(self.control_class.bl_idname,
                                          CONTROL_KEYS[label], 'PRESS')
            self.control_items.append((keymap, item))
            item.properties.label = label
            installation[label] = {'scope': scope, 'key': CONTROL_KEYS[label], 'addon_id': item.id}
        self.configs.update()
        for label, data in installation.items():
            matches = [
                row for keymap in self.configs.user.keymaps
                if all(getattr(keymap, field, None) == value
                       for field, value in data['scope'].items())
                for row in self.capture(keymap)['items']
                if (row['target'] == self.control_class.bl_idname
                    and row['properties'].get('label') == label and row['active']
                    and row['event']['type'] == data['key'] and row['event']['value'] == 'PRESS')
            ]
            data['merged_occurrences'] = len(matches)
        self.input_control_receipt()['installations'].append({'kind': kind, **installation})
        return installation

    def release_input_controls(self):
        if not (self.control_items or self.control_maps):
            return
        while self.control_items:
            keymap, item = self.control_items[-1]
            keymap.keymap_items.remove(item)
            self.control_items.pop()
            self.input_control_receipt()['removed_rows'] += 1
        while self.control_maps:
            keymap = self.control_maps[-1]
            if not len(keymap.keymap_items):
                self.configs.addon.keymaps.remove(keymap)
            self.control_maps.pop()
        self.configs.update()

    def unregister_control_class(self):
        if self.control_class is not None:
            self.bpy.utils.unregister_class(self.control_class)
            self.control_class = None

    def install(self):
        """Install and verify two owned rows in this disposable add-on keyconfig."""
        if not self.probe:
            raise RuntimeError('Read-only editor host cannot install a probe')
        if self.owned:
            return self.describe()
        for direction in DIRECTIONS:
            cls = self.probe_class(direction)
            self.bpy.utils.register_class(cls)
            self.classes.append(cls)
        maps = self.configs.addon.keymaps
        matching = [keymap for keymap in maps if all(
            getattr(keymap, field, None) == value for field, value in PROBE_SCOPE.items()
        )]
        if len(matching) > 1:
            raise ValueError('Ambiguous View2D add-on scope')
        if matching:
            keymap = matching[0]
        else:
            existing = {keymap.as_pointer() for keymap in maps}
            keymap = maps.new(name='View2D', space_type='EMPTY', region_type='WINDOW')
            if keymap.as_pointer() in existing:
                raise ValueError('View2D map creation returned a foreign scope')
            self.created_map = keymap
        assert self.capture(keymap)['scope'] == PROBE_SCOPE
        for direction in DIRECTIONS:
            expected = self.exact_descriptor(direction)
            item = keymap.keymap_items.new(expected['target'], f'WHEEL{direction}MOUSE',
                                          'PRESS', shift=True)
            self.owned.append((keymap, item))
            captured = next(row for row in self.capture(keymap)['items'] if row['blender_id'] == item.id)
            assert self.exact_row(captured, expected)
        self.configs.update()
        observation = self.describe()
        for data in observation['bindings'].values():
            occurrences = data['merged_occurrences']
            assert len(occurrences) == 1
            assert self.exact_row(occurrences[0]['item'], data['descriptor'])
        self.state['installations'].append(observation)
        self.record('editor_handler_installed')
        return observation

    def release(self):
        """Release only owned identities and capture resulting source and merged rows."""
        if not (self.owned or self.classes or self.created_map is not None):
            return
        while self.owned:
            keymap, item = self.owned[-1]
            keymap.keymap_items.remove(item)
            self.owned.pop()
        if self.created_map is not None:
            if not len(self.created_map.keymap_items):
                self.configs.addon.keymaps.remove(self.created_map)
            self.created_map = None
        while self.classes:
            self.bpy.utils.unregister_class(self.classes[-1])
            self.classes.pop()
        self.configs.update()
        source_after = self.source_maps()
        description = self.describe()
        merged_probe_rows_absent = all(
            not entry['merged_occurrences'] for entry in description['bindings'].values()
        )
        self.state['releases'].append({
            'source_after': source_after, 'merged_after': self.merged_rows(),
            'foreign_source_fields_and_order_unchanged': source_after == self.source_before,
            'merged_probe_rows_absent': merged_probe_rows_absent,
        })
        if not self.matched_endpoints:
            assert source_after == self.source_before
        assert merged_probe_rows_absent
        self.record('editor_handler_released')

    def cleanup(self):
        self.release_input_controls()
        self.unregister_control_class()
        if self.state is None:
            return
        self.release()
        self.state['source_after'] = self.source_maps()
        self.state['unknown_properties_after'] = self.property_read_issues(self.state['source_after'])
        self.state['complete_property_comparison'] = not (
            self.state['unknown_properties_before'] or self.state['unknown_properties_after'])
        self.state['foreign_source_fields_and_order_unchanged'] = (
            self.state['source_after'] == self.source_before
        )
        self.state['known_source_fields_and_order_unchanged'] = self.state['foreign_source_fields_and_order_unchanged']
        assert self.state['foreign_source_fields_and_order_unchanged']

    def setup_animation(self, kind):
        bpy = self.bpy
        self.area.type = 'VIEW_3D'
        if self.fixture_object is not None:
            bpy.data.objects.remove(self.fixture_object, do_unlink=True)
        obj = bpy.data.objects.new('Category Editor Animated', None)
        self.fixture_object = obj
        bpy.context.collection.objects.link(obj)
        for other in bpy.context.view_layer.objects:
            other.select_set(other == obj)
        bpy.context.view_layer.objects.active = obj
        for frame in (1, 10, 20, 30, 40):
            obj.location.x = frame / 10
            obj.keyframe_insert(data_path='location', index=0, frame=frame)
        curves = obj.animation_data.action.fcurves
        for curve in curves:
            curve.select = True
            for index, key in enumerate(curve.keyframe_points):
                key.select_control_point = key.select_left_handle = key.select_right_handle = index == 2
        if kind == 'nla':
            action = obj.animation_data.action
            obj.animation_data.action = None
            for index in range(16):
                track = obj.animation_data.nla_tracks.new()
                track.strips.new(f'Category Editor Track {index}', 1 + index, action)
            self.area.type = 'NLA_EDITOR'
        else:
            self.area.type = 'GRAPH_EDITOR' if kind == 'graph' else 'DOPESHEET_EDITOR'
            self.area.spaces.active.mode = {
                'graph': 'FCURVES', 'dopesheet': 'DOPESHEET', 'timeline': 'TIMELINE',
            }[kind]
        return lambda: [[i, j] for i, curve in enumerate(curves)
                        for j, key in enumerate(curve.keyframe_points) if key.select_control_point]

    def setup_nodes(self, kind):
        self.area.type = 'NODE_EDITOR'
        if kind == 'node_without_tree':
            self.area.ui_type = 'GeometryNodeTree'
            return lambda: []
        self.area.ui_type = 'CompositorNodeTree'
        scene = self.bpy.context.scene
        scene.use_nodes = True
        tree = scene.node_tree
        tree.nodes.clear()
        nodes = [tree.nodes.new('CompositorNodeMath') for _ in range(3)]
        for index, node in enumerate(nodes):
            node.location = (index * 200, 0)
            node.select = index == 1
        for left, right in zip(nodes, nodes[1:]):
            tree.links.new(left.outputs[0], right.inputs[0])
        tree.nodes.active = nodes[1]
        return lambda: [i for i, node in enumerate(nodes) if node.select]

    def setup_sequence(self, kind, direction):
        scene = self.bpy.context.scene
        editor = scene.sequence_editor_create()
        for strip in self.fixture_strips:
            editor.strips.remove(strip)
        # Keep neighbors on both sides of a selected contiguous run for Less.
        count = 7 if direction == 'DOWN' else 3
        strips = [editor.strips.new_effect(f'Category Editor Strip {i}', type='COLOR', channel=1,
                                          frame_start=1 + i * 10, frame_end=11 + i * 10)
                  for i in range(count)]
        self.fixture_strips = strips
        for index, strip in enumerate(strips):
            strip.select = 1 <= index <= 5 if direction == 'DOWN' else index == 1
        editor.active_strip = strips[count // 2]
        self.area.type = 'SEQUENCE_EDITOR'
        self.area.spaces.active.view_type = 'PREVIEW' if kind == 'sequencer_preview' else 'SEQUENCER'
        return lambda: [i for i, strip in enumerate(strips) if strip.select]

    def setup(self, kind, direction):
        if kind in ('dopesheet', 'graph', 'timeline', 'nla'):
            return self.setup_animation(kind)
        if kind in ('node', 'node_without_tree'):
            return self.setup_nodes(kind)
        if kind in ('sequencer', 'sequencer_preview'):
            return self.setup_sequence(kind, direction)
        if kind == 'image':
            self.area.type = 'IMAGE_EDITOR'
            self.area.ui_type = 'IMAGE_EDITOR'
            image = self.bpy.data.images.get('Category Editor Image')
            if image is None:
                image = self.bpy.data.images.new('Category Editor Image', width=512, height=512)
            self.area.spaces.active.image = image
            with self.context():
                self.bpy.ops.image.view_all()
        else:
            self.area.type = 'FILE_BROWSER'
            self.area.ui_type = 'FILES'
        return lambda: []

    def view(self):
        region = self.region()
        points = ((0, 0), (region.width // 2, region.height // 2),
                  (region.width - 1, region.height - 1))
        return [[value if math.isfinite(value) else None
                 for value in region.view2d.region_to_view(x, y)] for x, y in points]

    def point(self):
        region = self.region()
        return region.x + region.width // 2, region.y + region.height // 2

    def event(self, key, value, *, point=None, **modifiers):
        x, y = self.point() if point is None else point
        self.window.event_simulate(type=key, value=value, x=x, y=y, **modifiers)

    def case(self, kind, direction, stage, *, direct):
        key = f'WHEEL{direction}MOUSE'
        underlying_kind = {'timeline': 'dopesheet', 'sequencer_preview': 'sequencer',
                           'node_without_tree': 'node'}.get(kind, kind)
        target, row_id = TARGETS.get(underlying_kind, {}).get(direction, (None, None))
        row = {'case': f'editor_{stage}_{kind}_{direction.lower()}', 'stage': stage,
               'kind': kind, 'tested_key': key, 'shift': True, 'target': target,
               'owner03_ledger_id': row_id,
               'owner05_scroll_ids': dict(zip(('stock', 'full'), SCROLL_ROWS[direction]))}
        values = {}

        def attempt(phase, operation):
            try:
                operation()
            except ERRORS as error:
                row.setdefault('errors', {})[phase] = {
                    'type': type(error).__name__, 'message': str(error),
                }

        def prepare():
            attempt('fixture_setup', lambda: values.update(read=self.setup(kind, direction)))

        def control_setup():
            if 'read' not in values:
                return

            def work():
                row['input_controls'] = self.install_input_controls(kind)
                values['control_callback_index'] = len(self.control_callbacks)
                values['input_point'] = self.point()
                self.event('MOUSEMOVE', 'NOTHING', point=values['input_point'])
            attempt('native_input_control_setup', work)

        def controls():
            if 'input_point' not in values:
                return

            def work():
                for control_key in CONTROL_KEYS.values():
                    self.event(control_key, 'PRESS', point=values['input_point'])
                    self.event(control_key, 'RELEASE', point=values['input_point'])
            attempt('native_keyboard_controls', work)

        def control_wheel():
            if 'input_point' not in values:
                return

            def work():
                events = self.control_callbacks[values['control_callback_index']:]
                expected_area = CONTROL_SPACES[kind]
                counts = {
                    label: sum(event['label'] == label and event['area'] == expected_area
                               and event['region'] == 'WINDOW' for event in events)
                    for label in CONTROL_KEYS
                }
                row['input_delivery'] = {
                    'coordinates': values['input_point'], 'callbacks': events,
                    'counts_in_expected_window_region': counts,
                    'window_delivered': counts['window'] > 0,
                    'editor_delivered': counts['editor'] > 0,
                }
                if not counts['window']:
                    row['wheel_observation'] = 'window_control_missing'
                    return
                wheel = {
                    'key': 'WHEELUPMOUSE', 'modifiers': {},
                    'view_before': self.view(), 'selection_before': values['read'](),
                }
                row['input_delivery']['unmodified_wheel'] = wheel
                self.event(wheel['key'], 'PRESS', point=values['input_point'])
                values['control_wheel_sent'] = True
            attempt('native_unmodified_wheel_control', work)

        def observe_control_wheel():
            if not values.get('control_wheel_sent'):
                return

            def work():
                wheel = row['input_delivery']['unmodified_wheel']
                wheel['view_after'] = self.view()
                wheel['selection_after'] = values['read']()
                valid_samples = all(
                    value is not None for sample in (*wheel['view_before'], *wheel['view_after'])
                    for value in sample
                )
                wheel['view_changed'] = (
                    wheel['view_before'] != wheel['view_after'] if valid_samples else None
                )
                wheel['status'] = 'observed_view_change' if wheel['view_changed'] else 'inconclusive'
                if wheel['selection_before'] != wheel['selection_after']:
                    reset_read = self.setup(kind, direction)
                    if self.point() != values['input_point']:
                        raise ValueError('Editor WINDOW coordinates changed while resetting selection')
                    values['read'] = reset_read
                    wheel['fixture_recreated'] = True
                self.event('MOUSEMOVE', 'NOTHING', point=values['input_point'])
                values['ready_for_shortcut'] = True
            attempt('native_unmodified_wheel_observation', work)

        def press():
            if 'read' not in values:
                return
            if self.input_controls and not values.get('ready_for_shortcut'):
                row.setdefault('wheel_observation', 'controls_unavailable')
                return

            def work():
                with self.context():
                    context = self.bpy.context
                    row['context'] = {
                        'type': self.area.type, 'ui_type': self.area.ui_type,
                        'mode': getattr(self.area.spaces.active, 'mode', None),
                        'view_type': getattr(self.area.spaces.active, 'view_type', None),
                        'guarded_kind': self.guarded_kind(context),
                    }
                    row['underlying_poll'] = self.operator(target).poll() if target else None
                    row['inherited_scroll_poll'] = self.operator(
                        'view2d.scroll_' + direction.lower(),
                    ).poll()
                    row['probe_poll'] = (
                        self.operator(self.exact_descriptor(direction)['target']).poll()
                        if self.owned else None
                    )
                values['callbacks_before'] = len(self.callbacks)
                row['before'] = values['read']()
                row['view_before'] = self.view()
                row['operator_history_before'] = [
                    operator.bl_idname for operator in self.bpy.context.window_manager.operators
                ]
                point = values.get('input_point')
                if not self.input_controls:
                    self.event('MOUSEMOVE', 'NOTHING')
                self.event(key, 'PRESS', point=point, shift=True)
            attempt('native_input', work)

        def observe():
            if 'before' not in row:
                return

            def work():
                row['after'] = values['read']()
                row['view_after'] = self.view()
                row['callbacks'] = self.callbacks[values['callbacks_before']:]
                row['operator_history_after'] = [
                    operator.bl_idname for operator in self.bpy.context.window_manager.operators
                ]
                row['selection_changed'] = row['before'] != row['after']
                row['view_changed'] = row['view_before'] != row['view_after']
                row['wheel_observation'] = 'observed'
            attempt('native_observation', work)

        def direct_setup():
            if target:
                attempt('direct_fixture_setup',
                        lambda: values.update(direct_read=self.setup(kind, direction)))

        def direct_execute():
            if 'direct_read' not in values:
                return

            def work():
                operator = self.operator(target)
                result = {'before': values['direct_read'](), 'method': 'direct operator control'}
                row['direct_control'] = result
                with self.context():
                    result['poll'] = operator.poll()
                    result['result'] = sorted(operator('EXEC_DEFAULT')) if result['poll'] else []
                result['after'] = values['direct_read']()
                if kind == 'sequencer' and direction == 'DOWN':
                    result['contraction_observed'] = (
                        set(result['after']) < set(result['before'])
                    )
            attempt('direct_operator_control', work)

        def finish():
            if self.input_controls:
                self.release_input_controls()
            self.receipt['dispatch'].append(row)
            self.record(row['case'])

        if direct:
            self.steps.extend((direct_setup, direct_execute))
        self.steps.append(prepare)
        if self.input_controls:
            self.steps.extend((control_setup, controls, control_wheel, observe_control_wheel))
        self.steps.extend((press, observe, finish))

    def append(self):
        if self.matched_endpoints:
            self.append_matched_endpoint('before_owned_probe' if self.probe else 'before_no_probe')
        elif self.prime_readiness:
            self.steps.extend((self.begin_readiness, self.deliver_readiness,
                               self.finish_readiness, self.capture_primed_source))
        self.steps.append(self.start)
        kinds = tuple(TARGETS) if self.cluster == 'selection' else PASSTHROUGH
        if not self.probe:
            for kind in kinds:
                for direction in DIRECTIONS:
                    self.case(kind, direction, 'readonly', direct=self.cluster == 'selection')
            if self.matched_endpoints:
                self.append_matched_endpoint('after_no_probe')
        else:
            for kind in kinds:
                self.case(kind, 'UP', 'before_install', direct=False)
            self.steps.append(self.install)
            for kind in kinds:
                for direction in DIRECTIONS:
                    self.case(kind, direction, 'installed', direct=self.cluster == 'selection')
            self.steps.append(self.release)
            if self.matched_endpoints:
                self.append_matched_endpoint('after_first_release')
            self.case(kinds[0], 'UP', 'after_release', direct=False)
            self.steps.append(self.install)
            self.case(kinds[0], 'UP', 'reinstalled', direct=False)
            self.steps.append(self.release)
            if self.matched_endpoints:
                self.append_matched_endpoint('after_second_release')
        self.steps.append(self.cleanup)
        return self
