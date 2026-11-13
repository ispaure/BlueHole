"""Bounded native observations for the 22 reviewed ordinary candidate rows.

The accepted ledger supplies exact row descriptors. Only these explicit IDs may
be staged as disposable add-on probes; the reference path observes existing maps.
"""

import json
import math
from pathlib import Path
import sys


CLUSTERS = {
    'axis': (
        '2ae7de8b565d9c03fc45535896de07dc97af7ebed6ce9357fa324e1ea8187219',  # 3D View: ctrl+F1
        '3ee7001bf2f7f96dae4711948f76694b1c3ceb57aef1db6f96d9c2949b6b8b99',  # 3D View: oskey+F1
        'aa588d20ab030355215e945cdf7ea42dd7e386dfdefb93728ffdbbfb7ba4e6d8',  # 3D View: ctrl+F2
        'c0d9e2aa23b51664bb6a7f52439f47fe4ca359575c1da6fcb2bd33afa7dd0d3a',  # 3D View: oskey+F2
        'ac571b681410e5ce9d989bed48844639b1711b4fbc3493c1d7480ed47c0b363e',  # 3D View: ctrl+F3
        '73b312d55cdc6a757ca15ccaa51cdd75ecf21fe184ddad45db575af78c6fcf97',  # 3D View: oskey+F3
        '62d31f078d497b73967dd785c682a5a6840c9d4c81ddd82e1b43208fd6714e15',  # 3D View: shift+I
    ),
    'wheel_zoom': (
        '1498e141d9619244e98c6eaae90422084cc4c9f90c27406fa4f33c1b936e729b',  # 3D View: alt+WHEELOUTMOUSE
        '291b254de1dbbd4fa32d997de0e25aa91eea9e2306902ea8e09ef3ca3580c549',  # 3D View: alt+WHEELINMOUSE
    ),
    'uv_edit': (
        '89f634fdfe8e4bf1fcc76b809e7d29b4eb03a658acbeea752515cfee3db0168a',  # UV Editor: UP_ARROW
        'a02eca7e5332335cd12650270686df12c738e997d7f8925495c37cba053fd839',  # UV Editor: DOWN_ARROW
        'ade9ef951b1ade1364980da4a38375de3cf040ad12a2419e56e644958dabfda1',  # UV Editor: ctrl+shift+MIDDLEMOUSE
    ),
    'tools': (
        'ba40873fbf25c357c6c711911eaa483711dba3a101390e753d9e7d2eabcce1a6',  # Image: E
        '75c4bbefab8e3cc7a898801350b900eae9aceea836329b236df37a0c14952850',  # Image: Q
        'ff57544c10325e3984fef99805970ba7d3fa9d4bc93e6aa1e388e7f21b22e749',  # Image: R
        '318ab4227e9699b1b4279142e4c99a612fec5ebf27e2f6a663adb07e6c88a02d',  # Image: W
        'a15ff41f58e3a58fe77ab5d970e06f238a62dbb08e41283277d47c86e2c3a489',  # Image Paint: Q
        '06f22b2be115a9adbc05174de8e78048c60c241aa07f6a6ff0e357df503ab717',  # UV Editor: T
        'e818d7f7e379627bc1cc8078ed75e4ae089ee3b87e4ab12e61c9c5de8d6d7111',  # Vertex Paint: Q
        'd5bb12b4ca2bf2a3ad36a8cdbbfa98483b61ec2fe1f85e83699dfcd49bd6571c',  # Weight Paint: Q
    ),
    'selection': (
        '64793560d160e29318d58c922bcb7cc1c4c952d758dffff9a992100420e70aae',  # Image Paint: alt+A
        'c668cd6405ddd1e2b7c17a066eeea197ea8063eac81bc238742430ad3a8eb973',  # 3D View: ESC
    ),
}
CLUSTER_SUBSETS = {
    'uv_cursor': ('uv_edit', ('ade9ef951b1ade1364980da4a38375de3cf040ad12a2419e56e644958dabfda1',)),
}
CLUSTER_GROUPS = {'tools_selection': ('tools', 'selection')}
OBSERVATION_CLUSTERS = {
    'modal_switch': (
        '299e9dbeb54d018fa47270d4aef02ecc9143a6bc0882df7d3dc0c836fa2df822',
        '95d1e4739cb33e21cb88513fd041e4a20cd56a06dd022e945218fb4d65af778e',
    ),
}
MODIFIERS = ('shift', 'ctrl', 'alt', 'oskey')
ITEM_FIELDS = ('type', 'value', 'any', *MODIFIERS, 'key_modifier', 'repeat', 'direction')
CASE_ERRORS = (AttributeError, KeyError, ReferenceError, RuntimeError, StopIteration,
               TypeError, ValueError)
TOOL_STARTS = {
    'Image': ('builtin.sample', 'builtin.annotate'),
    'Image Paint': ('builtin_brush.Draw', 'builtin.brush', 'builtin.annotate'),
    'Vertex Paint': ('builtin_brush.Draw', 'builtin.brush', 'builtin.annotate'),
    'Weight Paint': ('builtin_brush.Draw', 'builtin.brush', 'builtin.annotate'),
    'UV Editor': ('builtin.select_box', 'builtin.select'),
}


def native_control_properties(operator, properties):
    """Apply the runtime's reviewed enum-flag rules to direct RNA arguments."""
    converted = properties.copy()
    for prop in operator.get_rna_type().properties:
        name = prop.identifier
        if name not in converted or prop.type != 'ENUM' or getattr(prop, 'is_enum_flag', False) is not True:
            continue
        identifiers = tuple(item.identifier for item in prop.enum_items)
        if not identifiers or any(type(identifier) is not str for identifier in identifiers):
            raise ValueError('unreadable_property_schema')
        allowed = frozenset(identifier for identifier in identifiers if identifier)
        value = converted[name]
        if (not allowed or type(value) not in (list, tuple)
                or any(type(flag) is not str or flag not in allowed for flag in value)
                or tuple(value) != tuple(sorted(set(value)))):
            raise ValueError('unreadable_property_schema')
        converted[name] = set(value)
    return converted


class OrdinaryCases:
    def __init__(self, steps, receipt, record, window, area, exporter, *,
                 probe=False, cluster='axis', invert_zoom=None, ledger_path=None):
        import bpy

        self.bpy = bpy
        self.steps, self.receipt, self.record = steps, receipt, record
        self.window, self.area, self.exporter = window, area, exporter
        self.configs = bpy.context.window_manager.keyconfigs
        self.probe, self.cluster, self.invert_zoom = probe, cluster, invert_zoom
        if invert_zoom is not None and cluster != 'wheel_zoom':
            raise ValueError('invert_zoom applies only to wheel_zoom')
        if cluster in CLUSTER_SUBSETS:
            parent, ids = CLUSTER_SUBSETS[cluster]
            assert set(ids) <= set(CLUSTERS[parent])
        elif cluster in CLUSTER_GROUPS:
            ids = tuple(row_id for family in CLUSTER_GROUPS[cluster] for row_id in CLUSTERS[family])
            assert len(ids) == len(set(ids))
        elif cluster in OBSERVATION_CLUSTERS:
            ids = OBSERVATION_CLUSTERS[cluster]
        else:
            ids = CLUSTERS[cluster]
        if ledger_path is None:
            ledger_path = Path(exporter.__file__).parent / 'fixtures/deluxe_keymaps/reconciliation-ledger.jsonl'
        found = {}
        with Path(ledger_path).open(encoding='utf-8') as source:
            for line in source:
                row = json.loads(line)
                if row['row_id'] in ids:
                    assert row['owner'] == '03' and row['row_id'] not in found
                    found[row['row_id']] = row['binding']
        self.bindings = {row_id: found[row_id] for row_id in ids}
        self.scope_names = {row['scope']['name'] for row in self.bindings.values()}
        self.scope_names.update(('Window', 'Screen', 'Frames', 'View2D', '3D View', 'Image', 'UV Editor'))
        self.foreign = {}
        self.owned = None
        self.saved_inversion = None
        self.proof = None
        self.input_callbacks = []
        self.input_control = None
        self.input_control_class = None

    def region(self):
        return next(region for region in self.area.regions if region.type == 'WINDOW')

    def context(self):
        return self.bpy.context.temp_override(window=self.window, area=self.area, region=self.region())

    def event(self, key, value='PRESS', *, dx=0, dy=0, **mods):
        region = self.region()
        x, y = region.width // 2 + dx, region.height // 2 + dy
        if not (0 <= x < region.width and 0 <= y < region.height):
            raise ValueError('Input point outside WINDOW region')
        self.window.event_simulate(type=key, value=value, x=region.x + x,
                                   y=region.y + y, **mods)

    def capture(self, keymap):
        return self.exporter._capture_map(keymap, self.bpy.types.OperatorProperties)

    def fingerprint_foreign(self):
        maps = {}
        for role in ('default', 'active', 'addon'):
            for keymap in getattr(self.configs, role).keymaps:
                if keymap.name in self.scope_names:
                    maps[role, keymap.as_pointer()] = self.capture(keymap)
        return maps

    @staticmethod
    def describe_foreign_changes(before, after):
        def snapshot(key, maps):
            role, pointer = key
            return {'role': role, 'pointer': pointer, 'map': maps[key]}

        removed = before.keys() - after.keys()
        added = after.keys() - before.keys()
        changed = []
        for key in before.keys() & after.keys():
            old, new = before[key], after[key]
            if old == new:
                continue
            fields = sorted(field for field in old.keys() | new.keys()
                            if old.get(field) != new.get(field))
            old_order = [row['blender_id'] for row in old['items']]
            new_order = [row['blender_id'] for row in new['items']]
            changed.append({
                'role': key[0], 'pointer': key[1], 'changed_fields': fields,
                'item_id_order_changed': old_order != new_order,
                'before': old, 'after': new,
            })
        same_scope_pairs = []
        for old_key in sorted(removed):
            for new_key in sorted(added):
                if (old_key[0] == new_key[0]
                        and before[old_key]['scope'] == after[new_key]['scope']):
                    same_scope_pairs.append({
                        'role': old_key[0], 'scope': before[old_key]['scope'],
                        'before_pointer': old_key[1], 'after_pointer': new_key[1],
                        'capture_equal': before[old_key] == after[new_key],
                    })
        return {
            'removed': [snapshot(key, before) for key in sorted(removed)],
            'added': [snapshot(key, after) for key in sorted(added)],
            'changed_in_place': sorted(changed, key=lambda row: (row['role'], row['pointer'])),
            'same_scope_removed_added_pairs': same_scope_pairs,
        }

    def start(self):
        self.foreign = self.fingerprint_foreign()
        inputs = self.bpy.context.preferences.inputs
        self.proof = {
            'stage': 'owned_exact_addon' if self.probe else 'readonly_reference_or_factory',
            'cluster': self.cluster, 'ledger_ids': list(self.bindings),
            'owned_created': 0, 'owned_exact_source': 0, 'owned_exact_merged': 0,
            'owned_released': 0, 'production_capability_enabled': False,
        }
        self.receipt['ordinary_proof'] = self.proof
        if self.cluster == 'wheel_zoom':
            if self.invert_zoom is not None:
                self.saved_inversion = inputs.invert_mouse_zoom
                inputs.invert_mouse_zoom = self.invert_zoom
            self.proof['invert_mouse_zoom'] = inputs.invert_mouse_zoom
            self.proof['input_limit'] = 'Synthetic event delivery; hardware event generation is unverified'
        self.install_input_control()
        self.record('ordinary_ready')

    def install_input_control(self):
        bpy, callbacks = self.bpy, self.input_callbacks
        assert not any(item.type == 'F23' for km in self.configs.user.keymaps for item in km.keymap_items)

        class WM_OT_category03_ordinary_control(bpy.types.Operator):
            bl_idname = 'wm.category03_ordinary_control'
            bl_label = 'Category 03 ordinary input control'

            def execute(self, context):
                callbacks.append({'area': context.area.type if context.area else None,
                                  'region': context.region.type if context.region else None})
                return {'FINISHED'}

        bpy.utils.register_class(WM_OT_category03_ordinary_control)
        self.input_control_class = WM_OT_category03_ordinary_control
        before = {km.as_pointer() for km in self.configs.addon.keymaps}
        keymap = self.configs.addon.keymaps.new(name='Window', space_type='EMPTY', region_type='WINDOW')
        self.input_control = keymap, None, keymap.as_pointer() not in before
        item = keymap.keymap_items.new(WM_OT_category03_ordinary_control.bl_idname, 'F23', 'PRESS')
        self.input_control = keymap, item, self.input_control[2]
        self.configs.update()
        matches = [item for km in self.configs.user.keymaps if km.name == 'Window'
                   for item in km.keymap_items if item.idname == WM_OT_category03_ordinary_control.bl_idname]
        self.proof['input_control'] = {'key': 'F23', 'addon_id': item.id, 'merged_occurrences': len(matches)}
        assert len(matches) == 1

    def release_input_control(self):
        if self.input_control is not None:
            keymap, item, created = self.input_control
            if item is not None:
                keymap.keymap_items.remove(item)
            if created and not len(keymap.keymap_items):
                self.configs.addon.keymaps.remove(keymap)
            self.input_control = None
        if self.input_control_class is not None:
            self.bpy.utils.unregister_class(self.input_control_class)
            self.input_control_class = None
        self.configs.update()
        if self.proof and 'input_control' in self.proof:
            self.proof['input_control']['released'] = True

    def release(self):
        if self.owned is None:
            return
        keymap, item, created_map = self.owned
        if item is not None:
            keymap.keymap_items.remove(item)
            self.proof['owned_released'] += 1
            self.owned = keymap, None, created_map
        if created_map and not len(keymap.keymap_items):
            self.configs.addon.keymaps.remove(keymap)
        self.owned = None
        self.configs.update()

    def cleanup(self):
        if self.proof is None:
            return
        try:
            self.release()
        finally:
            self.release_input_control()
            if self.saved_inversion is not None:
                inputs = self.bpy.context.preferences.inputs
                inputs.invert_mouse_zoom = self.saved_inversion
                self.saved_inversion = None
                self.proof['inversion_restored'] = True
        current = self.fingerprint_foreign()
        self.proof['foreign_source_fields_and_order_unchanged'] = current == self.foreign
        if current != self.foreign:
            self.proof['foreign_source_changes'] = self.describe_foreign_changes(
                self.foreign, current,
            )
            self.record('ordinary_foreign_source_changed')
        assert self.proof['foreign_source_fields_and_order_unchanged']
        assert self.proof['owned_created'] == self.proof['owned_released']

    def matching_maps(self, role, scope):
        return [km for km in getattr(self.configs, role).keymaps
                if all(getattr(km, name, None) == value for name, value in scope.items())]

    @staticmethod
    def item_matches(item, binding):
        fields = ('target', 'active', 'event', 'properties', 'read_issues')
        return all(item[field] == binding[field] for field in fields)

    def exact_count(self, role, binding):
        return sum(self.item_matches(item, binding)
                   for km in self.matching_maps(role, binding['scope'])
                   for item in self.capture(km)['items'])

    def stage_exact(self, binding):
        scope, event = binding['scope'], binding['event']
        assert not scope['is_modal'] and scope['is_tool'] is None and binding['active']
        assert not binding['read_issues'] and event['hyper'] == 0
        addon_maps = self.matching_maps('addon', scope)
        if len(addon_maps) > 1:
            raise ValueError('Ambiguous add-on scope')
        if addon_maps:
            keymap = addon_maps[0]
            created_map = False
        else:
            before = {km.as_pointer() for km in self.configs.addon.keymaps}
            keymap = self.configs.addon.keymaps.new(
                name=scope['name'], space_type=scope['space_type'], region_type=scope['region_type'],
            )
            created_map = keymap.as_pointer() not in before
        self.owned = keymap, None, created_map
        if any(getattr(keymap, name, None) != value for name, value in scope.items()):
            raise ValueError('Created map differs from requested scope')
        item = keymap.keymap_items.new(binding['target'], **{key: event[key] for key in ITEM_FIELDS})
        self.owned = keymap, item, created_map
        self.proof['owned_created'] += 1
        operator_properties = self.bpy.types.OperatorProperties
        defaults, _ = self.exporter._read_properties(
            item.properties, operator_properties=operator_properties,
        )
        for name, value in binding['properties'].items():
            if defaults.get(name) != value:
                setattr(item.properties, name, value)
        self.configs.update()
        captured = next(row for row in self.capture(keymap)['items'] if row['blender_id'] == item.id)
        source_exact = self.item_matches(captured, binding)
        self.proof['owned_exact_source'] += int(source_exact)
        return source_exact

    def setup_object(self, scope):
        bpy = self.bpy
        self.area.type = 'VIEW_3D'
        with self.context():
            obj = bpy.context.object
            if obj and obj.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            if self.area.spaces.active.local_view:
                bpy.ops.view3d.localview(frame_selected=False)
            cube = bpy.data.objects.get('Category Ordinary Cube')
            if cube is None:
                bpy.ops.mesh.primitive_cube_add()
                cube = bpy.context.object
                cube.name = 'Category Ordinary Cube'
                cube.rotation_euler = (0.22, 0.31, -0.4)
            other = bpy.data.objects.get('Category Ordinary Control')
            if other is None:
                bpy.ops.mesh.primitive_cube_add(location=(4, 0, 0))
                other = bpy.context.object
                other.name = 'Category Ordinary Control'
            for obj in bpy.context.scene.objects:
                obj.select_set(False)
            cube.select_set(True)
            other.select_set(scope == '3D View')
            bpy.context.view_layer.objects.active = cube
            paint_modes = {'Vertex Paint': 'VERTEX_PAINT', 'Weight Paint': 'WEIGHT_PAINT'}
            if scope in paint_modes:
                bpy.ops.object.mode_set(mode=paint_modes[scope])
        self.reset_view()

    def reset_view(self):
        from mathutils import Euler

        view = self.area.spaces.active.region_3d
        view.view_rotation = Euler((0.63, -0.38, 0.51)).to_quaternion()
        view.view_location = (0.4, -0.3, 0.7)
        view.view_distance = 10
        view.view_perspective = 'ORTHO'

    def setup_image(self, scope):
        bpy = self.bpy
        if scope in ('UV Editor', 'Image Paint'):
            self.setup_object(scope)
            with self.context():
                grid = bpy.data.objects.get('Category Ordinary UV Grid')
                if grid is None:
                    bpy.ops.mesh.primitive_grid_add(x_subdivisions=4, y_subdivisions=4, size=2)
                    grid = bpy.context.object
                    grid.name = 'Category Ordinary UV Grid'
                for obj in bpy.context.scene.objects:
                    obj.select_set(False)
                grid.select_set(True)
                bpy.context.view_layer.objects.active = grid
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
            self.reset_uv(grid)

        self.area.type = 'IMAGE_EDITOR'
        self.area.ui_type = 'UV' if scope == 'UV Editor' else 'IMAGE_EDITOR'
        image = self.area.spaces.active
        if scope != 'UV Editor':
            fixture = bpy.data.images.get('Category Ordinary Image')
            if fixture is None:
                fixture = bpy.data.images.new('Category Ordinary Image', width=256, height=256)
            image.image = fixture
            image.mode = 'PAINT' if scope == 'Image Paint' else 'VIEW'
        image.cursor_location = (0.5, 0.5)
        with self.context():
            bpy.ops.image.view_all()

    def reset_uv(self, obj):
        import bmesh

        tool_settings = self.bpy.context.scene.tool_settings
        tool_settings.use_uv_select_sync = False
        tool_settings.uv_select_mode = 'VERTEX'
        bm = bmesh.from_edit_mesh(obj.data)
        uv = bm.loops.layers.uv.verify()
        for face in bm.faces:
            for loop in face.loops:
                loop[uv].select = face.index == 0
        bmesh.update_edit_mesh(obj.data)

    def setup(self, binding, variant=None):
        scope = binding['scope']['name']
        setup_scope = 'UV Editor' if variant and variant.get('image_mode') == 'UV' else scope
        if variant and variant.get('image_mode') == 'VIEW':
            self.setup_object(scope)
        if scope in ('Image', 'Image Paint', 'UV Editor'):
            self.setup_image(setup_scope)
        else:
            self.setup_object(scope)
            if binding['target'] == 'view3d.localview':
                self.bpy.data.objects['Category Ordinary Control'].select_set(False)
        if variant and 'paint_mask' in variant:
            with self.context():
                mesh = self.bpy.context.object.data
                mesh.use_paint_mask = variant['paint_mask']
                mesh.use_paint_mask_vertex = False
        attempts = []
        if binding['target'] == 'wm.tool_set_by_id':
            for name in TOOL_STARTS[setup_scope]:
                try:
                    with self.context():
                        result = sorted(self.bpy.ops.wm.tool_set_by_id(name=name))
                except CASE_ERRORS as error:
                    result = [type(error).__name__]
                active = self.active_tool()
                attempts.append({'requested': name, 'result': result, 'active_tool': active})
                valid = active is not None and active != binding['properties']['name']
                if variant:
                    valid = valid and result == ['FINISHED'] and active == name
                if valid:
                    break
        return attempts

    def active_tool(self):
        with self.context():
            tools = self.bpy.context.workspace.tools
            space = self.area.spaces.active
            if self.area.type == 'IMAGE_EDITOR':
                mode = 'UV' if self.area.ui_type == 'UV' else space.mode
                tool = tools.from_space_image_mode(mode, create=False)
            else:
                tool = tools.from_space_view3d_mode(self.bpy.context.mode, create=False)
            return tool.idname if tool else None

    def snapshot(self):
        import bmesh

        with self.context():
            ctx = self.bpy.context
            active = ctx.object
            result = {
                'editor': self.area.type, 'editor_ui_type': self.area.ui_type,
                'context_mode': ctx.mode, 'active_tool': self.active_tool(),
                'frame_current': ctx.scene.frame_current,
                'operator_history': [operator.bl_idname for operator in ctx.window_manager.operators],
                'modal_operators_observable': hasattr(self.window, 'modal_operators'),
                'modal_operators': [operator.bl_idname for operator in
                                    getattr(self.window, 'modal_operators', ())],
            }
            if self.area.type == 'VIEW_3D':
                space = self.area.spaces.active
                view = space.region_3d
                result['view'] = {
                    'rotation': list(view.view_rotation), 'location': list(view.view_location),
                    'distance': view.view_distance, 'perspective': view.view_perspective,
                    'local': bool(space.local_view),
                }
                result['selected_objects'] = sorted(
                    obj.name for obj in ctx.selected_objects if obj.name.startswith('Category Ordinary')
                )
                if active and active.type == 'MESH' and ctx.mode in ('PAINT_VERTEX', 'PAINT_WEIGHT'):
                    result['paint_mask'] = active.data.use_paint_mask
                    result['paint_mask_vertex'] = active.data.use_paint_mask_vertex
            elif self.area.type == 'IMAGE_EDITOR':
                result['image_mode'] = self.area.spaces.active.mode
                result['cursor'] = list(self.area.spaces.active.cursor_location)
                region = self.region()
                coords = region.view2d.region_to_view(region.width / 2, region.height / 2)
                result['view_center'] = [value if math.isfinite(value) else None for value in coords]
                if active and active.type == 'MESH' and active.mode == 'EDIT':
                    bm = bmesh.from_edit_mesh(active.data)
                    uv = bm.loops.layers.uv.active
                    result['selected_uv'] = [
                        [face.index, index] for face in bm.faces for index, loop in enumerate(face.loops)
                        if loop[uv].select
                    ]
                    result['uv_coordinates'] = [
                        [face.index, index, *loop[uv].uv]
                        for face in bm.faces for index, loop in enumerate(face.loops)
                    ]
            return result

    def direct_control(self, binding):
        module, name = binding['target'].split('.', 1)
        operator = getattr(getattr(self.bpy.ops, module), name)
        properties = binding['properties'].copy()
        if binding['target'] == 'transform.translate':
            # A nonzero EXEC value checks cursor movement without replaying the gesture.
            properties['value'] = (0.125, 0.0625, 0.0)
        elif binding['target'] == 'view3d.zoom':
            region = self.region()
            properties.update(mx=region.width // 2, my=region.height // 2)
        with self.context():
            poll = operator.poll()
            native_properties = native_control_properties(operator, properties) if poll else {}
            result = sorted(operator('EXEC_DEFAULT', **native_properties)) if poll else []
        return {'poll': poll, 'result': result, 'properties': properties,
                'native_enum_flag_arguments': {
                    name: sorted(value) for name, value in native_properties.items()
                    if type(value) is set},
                'method': 'direct operator fixture control'}

    def conflicting_rows(self, binding):
        event = binding['event']
        candidates = []
        for keymap in self.configs.user.keymaps:
            if keymap.name not in self.scope_names:
                continue
            for row in self.capture(keymap)['items']:
                actual = row['event']
                if (row['active'] and actual.get('type') == event['type']
                        and (actual.get('any') or all(actual.get(modifier) in
                             (event[modifier], -1) for modifier in MODIFIERS))):
                    candidates.append({
                        'scope': keymap.name, 'space_type': keymap.space_type,
                        'target': row['target'], 'event': actual,
                    })
        return candidates

    def case(self, row_id, binding, variant=None):
        state = {}
        event = binding['event']
        key = event['type']
        mods = {name: bool(event[name]) for name in MODIFIERS if event[name]}
        is_drag = event['value'] == 'CLICK_DRAG'
        is_tool = binding['target'] == 'wm.tool_set_by_id'
        result = {
            'case': f'ordinary_{self.cluster}_{key}_{row_id[:12]}',
            'ledger_id': row_id, 'tested_key': key, 'expected_event': event,
            'scope': binding['scope'], 'target': binding['target'],
        }
        if variant:
            result['context_variant'] = variant
            result['case'] += '_' + variant['name']
            result['family'] = next(family for family in CLUSTER_GROUPS[self.cluster]
                                    if row_id in CLUSTERS[family])

        def attempt(phase, operation):
            if 'error' in result:
                return
            try:
                operation()
            except CASE_ERRORS as error:
                result['error'] = {'phase': phase, 'type': type(error).__name__,
                                   'message': str(error)}
                if phase.startswith('probe'):
                    result['probe_status'] = 'unavailable_or_unverified'
                elif phase.startswith('direct'):
                    result['direct_control_status'] = 'fixture_control_error'
                else:
                    result['input_status'] = 'fixture_or_delivery_error'

        def prepare():
            def work():
                result['tool_setup'] = self.setup(binding, variant)
                if is_tool:
                    active = self.active_tool()
                    result['distinct_start_tool'] = (
                        active is not None and active != binding['properties']['name']
                    )
                    if variant:
                        result['start_control_valid'] = any(
                            attempt['result'] == ['FINISHED']
                            and attempt['active_tool'] == attempt['requested'] == active
                            and active != binding['properties']['name']
                            for attempt in result['tool_setup'])
            attempt('fixture_setup', work)

        def observe_maps():
            def work():
                result['exact_rows_before_probe'] = {
                    role: self.exact_count(role, binding)
                    for role in ('default', 'active', 'addon', 'user')
                }
                result['merged_event_candidates'] = self.conflicting_rows(binding)
            attempt('map_observation', work)
            if not self.probe:
                return

            def probe():
                before = result['exact_rows_before_probe']
                if before['addon'] or before['user']:
                    result['probe_status'] = 'exact_row_already_present'
                    return
                source_exact = self.stage_exact(binding)
                merged_delta = self.exact_count('user', binding) - before['user']
                result['probe_readback'] = {
                    'source_exact': source_exact, 'merged_occurrence_delta': merged_delta,
                }
                if merged_delta == 1:
                    self.proof['owned_exact_merged'] += 1
                if not source_exact or merged_delta != 1:
                    raise ValueError('Owned row failed exact source and merged readback')
                result['probe_status'] = 'verified'
            attempt('probe_exact_addon', probe)

        def begin():
            def work():
                callbacks = self.input_callbacks[state['control_index']:]
                delivered = {'area': self.area.type, 'region': 'WINDOW'} in callbacks
                result['input_delivery'] = {'callbacks': callbacks,
                                            'expected_area': self.area.type,
                                            'expected_region': 'WINDOW', 'delivered': delivered}
                state['input_delivered'] = delivered
                if not delivered:
                    result['input_status'] = 'window_control_missing'
                    return
                result['before'] = self.snapshot()
                if variant:
                    before = result['before']
                    scope = binding['scope']['name']
                    expected = variant.get('image_mode')
                    if expected == 'UV' or scope == 'UV Editor':
                        ready = before['editor_ui_type'] == 'UV' and before['context_mode'] == 'EDIT_MESH'
                    elif expected == 'VIEW' or scope == 'Image Paint':
                        ready = (before['editor_ui_type'] != 'UV'
                                 and before['image_mode'] == ('VIEW' if expected else 'PAINT'))
                    elif scope in ('Vertex Paint', 'Weight Paint'):
                        ready = (before['context_mode'] == {'Vertex Paint': 'PAINT_VERTEX',
                                                          'Weight Paint': 'PAINT_WEIGHT'}[scope]
                                 and before['paint_mask'] == variant['paint_mask']
                                 and not before['paint_mask_vertex'])
                    else:
                        ready = before['editor'] == 'VIEW_3D' and before['context_mode'] == 'OBJECT'
                    result['context_ready'] = ready
                    if not ready:
                        raise ValueError('Combined family fixture did not reach its declared context')
                self.event('MOUSEMOVE', 'NOTHING')
                self.event(key, **mods)
                state['pressed'] = True
                if not is_drag and 'WHEEL' not in key:
                    self.event(key, 'RELEASE', **mods)
                    state['pressed'] = False
            attempt('input_press', work)

        def prime_input():
            state['control_index'] = len(self.input_callbacks)
            def work():
                self.event('MOUSEMOVE', 'NOTHING')
                self.event('F23')
                self.event('F23', 'RELEASE')
            attempt('native_input_control', work)

        def drag(dx, dy):
            if state.get('input_delivered'):
                attempt('input_drag', lambda: self.event('MOUSEMOVE', 'NOTHING', dx=dx, dy=dy, **mods))

        def observe_phase(phase):
            if state.get('input_delivered'):
                attempt('input_phase_observation', lambda: result.setdefault('input_phases', []).append({
                    'phase': phase, 'snapshot': self.snapshot()}))

        def end_drag():
            if not state.pop('pressed', False):
                return
            # Release even when motion failed, so a later case cannot inherit a modal drag.
            try:
                self.event(key, 'RELEASE', dx=70, dy=32, **mods)
            except CASE_ERRORS as error:
                result['input_status'] = 'fixture_or_delivery_error'
                result['release_error'] = type(error).__name__

        def observe():
            if not state.get('input_delivered'):
                return
            def work():
                result['after'] = self.snapshot()
                result['input_status'] = 'observed'
                if is_tool:
                    self.event(key, **mods)
                    self.event(key, 'RELEASE', **mods)
            attempt('input_observation', work)

        def reset():
            def work():
                if is_tool:
                    result['after_second_input'] = self.snapshot()
                # A competing Quick Favorites or modal action may still be open.
                # Cancel it after observations and before reinitializing the fixture.
                self.event('ESC')
                self.event('ESC', 'RELEASE')
            attempt('input_reset', work)

        def fixture_control():
            def work():
                result['direct_control_tool_setup'] = self.setup(binding, variant)
                result['direct_control_before'] = self.snapshot()
                result['direct_control'] = self.direct_control(binding)
            attempt('direct_fixture_control', work)

        def finish():
            try:
                if 'direct_control' in result:
                    attempt('direct_fixture_observation',
                            lambda: result['direct_control'].update(after=self.snapshot()))
            finally:
                owned = self.owned is not None and self.owned[1] is not None
                self.release()
                if owned:
                    result['probe_released'] = (
                        self.exact_count('user', binding) ==
                        result['exact_rows_before_probe']['user']
                    )
                    assert result['probe_released'], 'Merged probe occurrence remained after release'
                self.receipt['dispatch'].append(result)
                self.record(result['case'])

        self.steps.extend((prepare, observe_maps, prime_input, begin))
        if is_drag:
            self.steps.extend((lambda: observe_phase('after_press'),
                               lambda: drag(8, 4), lambda: observe_phase('after_initial_motion'),
                               lambda: drag(70, 32), lambda: observe_phase('after_second_motion'),
                               end_drag, lambda: observe_phase('after_release')))
        self.steps.extend((observe, reset, fixture_control, finish))

    def append(self):
        self.steps.append(self.start)
        for row_id, binding in self.bindings.items():
            if self.cluster == 'tools_selection':
                scope = binding['scope']['name']
                if scope == 'Image':
                    variants = ({'name': 'image_view', 'image_mode': 'VIEW'},
                                {'name': 'image_uv', 'image_mode': 'UV'})
                elif scope in ('Vertex Paint', 'Weight Paint'):
                    variants = ({'name': 'mask_off', 'paint_mask': False},
                                {'name': 'face_mask_on', 'paint_mask': True})
                else:
                    variants = ({'name': 'exact_scope'},)
                for variant in variants:
                    self.case(row_id, binding, variant)
            else:
                self.case(row_id, binding)
        self.steps.append(self.cleanup)
        return self


class UVArrowPrecedenceCases:
    """One isolated Frames assignment experiment; inherited rows are read-only."""

    def __init__(self, ordinary, runtime, *, production=None):
        self.fixture, self.runtime = ordinary, runtime
        self.bpy, self.configs = ordinary.bpy, ordinary.configs
        self.steps, self.receipt, self.record = ordinary.steps, ordinary.receipt, ordinary.record
        self.classes, self.callbacks = [], []
        self.handle = None
        self.production = production
        self.installed = False
        self.previous_profile = None
        self.profiling = False
        self.owner = 'category03:uv-arrow-frames-probe'
        self.proof = {'status': 'prepared', 'owner': self.owner, 'production': production is not None,
                      'source_policy': 'ordinary owned assignments only; inherited rows read-only',
                      'cases': [], 'installs': [], 'releases': []}
        self.receipt['uv_arrow_precedence'] = self.proof

    def setup(self, kind):
        self.fixture.setup_image('UV Editor') if kind == 'uv' else self.fixture.setup_object('3D View')
        with self.fixture.context():
            obj, scene = self.bpy.context.object, self.bpy.context.scene
            for frame, value in ((1, 0.0), (10, 1.0)):
                scene.frame_set(frame)
                obj.location.x = value
                assert obj.keyframe_insert(data_path='location', index=0, frame=frame)
            scene.frame_set(5)
        return obj.name

    def maps(self):
        return {role: [self.fixture.capture(keymap) for keymap in getattr(self.configs, role).keymaps
                       if keymap.name in self.fixture.scope_names]
                for role in ('default', 'active', 'addon', 'user')}

    def guard_class(self, direction):
        bpy, callbacks = self.bpy, self.callbacks
        target = 'uv.select_' + direction

        class WM_OT_category03_uv_guard(bpy.types.Operator):
            bl_idname = 'wm.category03_uv_' + direction + '_guard'
            bl_label = 'Category 03 UV ' + direction + ' priority probe'

            @classmethod
            def poll(cls, context):
                return bool(context.area and context.area.type == 'IMAGE_EDITOR'
                            and context.area.ui_type == 'UV'
                            and context.region and context.region.type == 'WINDOW'
                            and getattr(bpy.ops.uv, 'select_' + direction).poll())

            def execute(self, context):
                if not type(self).poll(context):
                    return {'PASS_THROUGH'}
                result = getattr(bpy.ops.uv, 'select_' + direction)('EXEC_DEFAULT')
                callbacks.append({'target': target, 'area': context.area.type,
                                  'ui_type': context.area.ui_type, 'region': context.region.type,
                                  'mode': context.mode, 'result': sorted(result)})
                return result

        WM_OT_category03_uv_guard.__name__ = 'WM_OT_category03_uv_' + direction + '_guard'
        return WM_OT_category03_uv_guard

    def start(self):
        if self.production:
            self.classes.extend(self.production['classes'])
            self.initial_maps = self.maps()
            self.initial_owners = self.production['source_provenance'](self.initial_maps)
            self.proof['initial_maps_without_control'] = self.initial_maps
            self.proof['initial_owned_generations'] = self.initial_owners
        else:
            for direction in ('more', 'less'):
                cls = self.guard_class(direction)
                self.bpy.utils.register_class(cls)
                self.classes.append(cls)
        self.fixture.start()
        if self.production:
            self.fixture.release_input_control()
        self.baseline = self.maps()
        if self.production:
            self.baseline_owners = self.production['source_provenance'](self.baseline)
            self.proof['baseline_owned_generations'] = self.baseline_owners
        self.proof.update(status='running', baseline_maps=self.baseline,
                          order_limit='Captured map/item order is not handler priority; frame/UV effects prove the winner')
        self.record('uv_arrow_probe_ready')

    def install(self):
        rt = self.runtime
        assert self.handle is None
        if self.production:
            self.production['toggle'](True)
            self.installed = True
            pairs = self.production['registered_pairs']()
            proof = {'source_rows': [], 'merged_rows': [], 'registered_pair_matches': [],
                     'actual_owners': [], 'owned_pair_count': 0}
            self.proof['installs'].append(proof)
            wanted = {cls.bl_idname for cls in self.classes}
            for owner_id, handle in rt._FEATURES.items():
                if not owner_id.startswith('legacy:Selection:'):
                    continue
                for request_id, owned in handle._owned.items():
                    if owned.item.idname not in wanted:
                        continue
                    assert rt._valid_owned(owned)
                    assert sum(rt._same(km, owned.map) and rt._same(item, owned.item)
                               for km, item in pairs) == 1
                    assert (owned.map.name, owned.map.space_type, owned.map.region_type) == ('Frames', 'EMPTY', 'WINDOW')
                    source = next(row for row in self.fixture.capture(owned.map)['items']
                                  if row['blender_id'] == owned.item.id)
                    merged = [row for km in self.configs.user.keymaps if km.name == 'Frames'
                              for row in self.fixture.capture(km)['items']
                              if row['target'] == owned.item.idname]
                    assert len(merged) == 1
                    assert source['active'] and source['event']['repeat']
                    assert {k: v for k, v in source.items() if k != 'blender_id'} == {
                        k: v for k, v in merged[0].items() if k != 'blender_id'}
                    proof['source_rows'].append(source)
                    proof['merged_rows'].append(merged[0])
                    proof['registered_pair_matches'].append(1)
                    proof['actual_owners'].append({'owner_id': owner_id, 'request_id': request_id})
            proof['owned_pair_count'] = len(proof['source_rows'])
            assert proof['owned_pair_count'] == 2
            assert {row['event']['type'] for row in proof['source_rows']} == {'UP_ARROW', 'DOWN_ARROW'}
            self.record('uv_arrow_production_enabled')
            return
        assignments = tuple(rt.KeymapAssignment(
            request_id=direction, scope=rt.KeymapScope('Frames'),
            event=rt.KeymapEvent(key, repeat=True),
            target=rt.KeymapTarget(idname=cls.bl_idname))
            for direction, key, cls in zip(('more', 'less'), ('UP_ARROW', 'DOWN_ARROW'), self.classes))
        self.handle = rt.register_feature(self.owner, assignments=assignments)
        self.installed = True
        self.configs.update()
        proof = {'source_rows': [], 'merged_rows': [], 'registered_pair_matches': [],
                 'owned_pair_count': len(self.handle.owned_pairs)}
        self.proof['installs'].append(proof)
        assert proof['owned_pair_count'] == 2
        for request in assignments:
            owned = self.handle._owned[request.request_id]
            assert rt._valid_owned(owned)
            pair_matches = sum(rt._same(km, owned.map) and rt._same(item, owned.item)
                               for km, item in self.handle.owned_pairs)
            assert pair_matches == 1
            source = self.fixture.capture(owned.map)
            row = next(row for row in source['items'] if row['blender_id'] == owned.item.id)
            proof['source_rows'].append(row)
            assert row['active'] and row['target'] == request.target.idname
            assert row['event']['type'] == request.event.type and row['event']['repeat']
            matches = [row for km in self.configs.user.keymaps
                       if km.name == 'Frames' and km.space_type == 'EMPTY' and km.region_type == 'WINDOW'
                       for row in self.fixture.capture(km)['items'] if row['target'] == request.target.idname]
            assert len(matches) == 1
            merged = matches[0]
            proof['merged_rows'].append(merged)
            assert {k: v for k, v in merged.items() if k != 'blender_id'} == {
                k: v for k, v in row.items() if k != 'blender_id'}
            proof['registered_pair_matches'].append(pair_matches)
        self.record('uv_arrow_probe_installed')

    def release(self):
        if self.production and self.installed:
            self.production['toggle'](False)
        if self.handle is not None:
            self.handle.release()
            self.handle = None
            self.configs.update()
        self.installed = False
        assert not any(row.idname in {cls.bl_idname for cls in self.classes}
                       for role in ('addon', 'user') for km in getattr(self.configs, role).keymaps
                       for row in km.keymap_items)

    def release_endpoint(self):
        if self.production:
            self.fixture.release_input_control()
        current = self.maps()
        proof = {'maps': current, 'exact_sources_and_merged_equal': current == self.baseline}
        if self.production:
            source_roles = ('default', 'active', 'addon')
            before = {role: self.baseline[role] for role in source_roles}
            after = {role: current[role] for role in source_roles}
            owners = self.production['source_provenance'](current)
            comparison = self.production['compare_sources'](before, after, self.baseline_owners, owners)
            proof.update(source_comparison=comparison, owned_source_generations=owners,
                         strict_foreign_merged_equal=current['user'] == self.baseline['user'])
            proof['accepted_preservation'] = (comparison['accepted_sources_equal']
                                               and proof['strict_foreign_merged_equal'])
        else:
            proof['accepted_preservation'] = proof['exact_sources_and_merged_equal']
        self.proof['releases'].append(proof)
        self.record('uv_arrow_probe_released')
        assert proof['accepted_preservation']

    def start_profile(self):
        if not self.production:
            return
        codes = {cls.execute.__code__: 'uv.select_' + direction
                 for cls, direction in zip(self.classes, ('more', 'less'))}
        self.previous_profile = sys.getprofile()

        def profile(frame, event, result):
            if event == 'return' and frame.f_code in codes:
                context = frame.f_locals['context']
                self.callbacks.append({'target': codes[frame.f_code], 'area': context.area.type,
                                       'ui_type': context.area.ui_type, 'region': context.region.type,
                                       'mode': context.mode, 'result': sorted(result)})

        sys.setprofile(profile)
        self.profiling = True

    def stop_profile(self):
        if self.profiling:
            sys.setprofile(self.previous_profile)
            self.profiling = False

    def case(self, label, key, kind, expected, direction):
        result = {'case': label, 'key': key, 'kind': kind, 'expected': expected}
        state = {}

        def prepare():
            result['keyframed_object'] = self.setup(kind)
            if self.production and self.fixture.input_control is None:
                self.fixture.install_input_control()
            state['control_start'] = len(self.fixture.input_callbacks)
            state['callback_start'] = len(self.callbacks)

        def prime():
            self.fixture.event('MOUSEMOVE', 'NOTHING')
            self.fixture.event('F23')
            self.fixture.event('F23', 'RELEASE')

        def begin():
            callbacks = self.fixture.input_callbacks[state['control_start']:]
            expected_context = {'area': self.fixture.area.type, 'region': 'WINDOW'}
            delivered = expected_context in callbacks
            result['input_delivery'] = {'callbacks': callbacks, 'expected': expected_context,
                                        'delivered': delivered}
            if not delivered:
                result.update(passed=False, status='window_control_missing')
                self.proof['cases'].append(result)
                self.receipt['dispatch'].append(result)
                self.record(label)
            assert delivered
            result['before'] = self.fixture.snapshot()
            result['live_maps_before_input'] = self.maps()
            with self.fixture.context():
                result['guard_poll'] = self.classes[0 if direction == 'more' else 1].poll(self.bpy.context)
                result['stock_jump_poll'] = self.bpy.ops.screen.keyframe_jump.poll()
            self.start_profile()
            self.fixture.event('MOUSEMOVE', 'NOTHING')
            self.fixture.event(key)
            self.fixture.event(key, 'RELEASE')

        def observe():
            self.stop_profile()
            result['after'] = self.fixture.snapshot()
            result['callbacks'] = self.callbacks[state['callback_start']:]
            before, after = result['before'], result['after']
            if expected == 'uv_selection':
                result['passed'] = (len(before['selected_uv']) == 4
                                    and len(after['selected_uv']) == (9 if direction == 'more' else 1)
                                    and after['frame_current'] == 5)
                if self.installed and key in ('UP_ARROW', 'DOWN_ARROW'):
                    result['passed'] &= len(result['callbacks']) == 1
                else:
                    result['passed'] &= not result['callbacks']
            else:
                result['passed'] = (after['frame_current'] == (10 if direction == 'more' else 1)
                                    and not result['callbacks'])
                if kind == 'uv':
                    result['passed'] &= before['selected_uv'] == after['selected_uv']
                else:
                    result['passed'] &= not result['guard_poll']
            result['passed'] &= before['frame_current'] == 5
            self.proof['cases'].append(result)
            self.receipt['dispatch'].append(result)
            self.record(label)
            assert result['passed'], label

        self.steps.extend((prepare, prime, begin, observe))

    def cleanup(self):
        self.stop_profile()
        finished = False
        try:
            self.release()
            if self.production:
                self.fixture.release_input_control()
                if not hasattr(self, 'initial_maps'):
                    return
                current = self.maps()
                roles = ('default', 'active', 'addon')
                owners = self.production['source_provenance'](current)
                comparison = self.production['compare_sources'](
                    {role: self.initial_maps[role] for role in roles},
                    {role: current[role] for role in roles}, self.initial_owners, owners)
                merged_equal = current['user'] == self.initial_maps['user']
                self.proof['final_without_control'] = {
                    'maps': current, 'owned_source_generations': owners,
                    'source_comparison': comparison, 'strict_foreign_merged_equal': merged_equal}
                self.proof['control_released'] = True
                assert comparison['accepted_sources_equal'] and merged_equal
            else:
                self.fixture.cleanup()
            finished = True
        finally:
            if not self.production:
                for cls in reversed(self.classes):
                    self.bpy.utils.unregister_class(cls)
            self.classes.clear()
            self.proof['fixture_cleanup_complete'] = finished
            if (finished and len(self.proof['cases']) == 13 and all(case['passed'] for case in self.proof['cases'])
                    and len(self.proof['releases']) == 2
                    and all(item['accepted_preservation'] for item in self.proof['releases'])):
                self.proof['status'] = 'complete'

    def append(self):
        self.steps.extend((lambda: self.setup('uv'),
                           lambda: self.fixture.event('F24'),
                           lambda: self.fixture.event('F24', 'RELEASE'), self.start))
        for direction, key in (('more', 'UP_ARROW'), ('less', 'DOWN_ARROW')):
            self.case('baseline_uv_' + direction, key, 'uv', 'keyframe_jump', direction)
        if not self.production:
            for direction, key in (('more', 'RIGHT_BRACKET'), ('less', 'LEFT_BRACKET')):
                self.case('baseline_bracket_' + direction, key, 'uv', 'uv_selection', direction)
        for direction, key in (('more', 'UP_ARROW'), ('less', 'DOWN_ARROW')):
            self.case('baseline_3d_' + direction, key, 'object', 'keyframe_jump', direction)
        self.steps.append(self.install)
        for direction, key in (('more', 'UP_ARROW'), ('less', 'DOWN_ARROW')):
            self.case('owned_uv_' + direction, key, 'uv', 'uv_selection', direction)
        if self.production:
            for direction, key in (('more', 'RIGHT_BRACKET'), ('less', 'LEFT_BRACKET')):
                self.case('owned_bracket_' + direction, key, 'uv', 'uv_selection', direction)
        for direction, key in (('more', 'UP_ARROW'), ('less', 'DOWN_ARROW')):
            self.case('owned_3d_' + direction, key, 'object', 'keyframe_jump', direction)
        self.steps.extend((self.release, lambda: self.setup('uv'), self.release_endpoint))
        for direction, key in (('more', 'UP_ARROW'), ('less', 'DOWN_ARROW')):
            self.case('released_uv_' + direction, key, 'uv', 'keyframe_jump', direction)
        self.steps.append(self.install)
        self.case('reinstalled_uv_more', 'UP_ARROW', 'uv', 'uv_selection', 'more')
        self.steps.extend((self.release, lambda: self.setup('uv'), self.release_endpoint))
        return self
