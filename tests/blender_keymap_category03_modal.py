"""Read-only E-switch witness; creates no modal keymap items or capabilities."""

from math import isfinite


def changed(left, right, tolerance=1e-6):
    if len(left) != len(right) or not all(isfinite(value) for value in (*left, *right)):
        raise ValueError('Invalid geometry observation')
    return any(abs(a - b) > tolerance for a, b in zip(left, right))


class ModalSwitchCases:
    def __init__(self, ordinary):
        self.common = ordinary
        self.bpy = ordinary.bpy
        self.steps, self.receipt, self.record = ordinary.steps, ordinary.receipt, ordinary.record
        self.object = None
        self.initial_maps = None
        self.cleaned = False
        self.proof = {
            'status': 'prepared', 'ledger_ids': list(ordinary.bindings),
            'modal_map_mutations': 0, 'runtime_capability_changes': 0,
            'interpretation': 'E and repeated E are observations; changed rotation alone does not identify Trackball.',
        }
        self.receipt['modal_switch_proof'] = self.proof

    def maps(self):
        return {role: [self.common.capture(km) for km in getattr(self.common.configs, role).keymaps
                       if km.name in self.common.scope_names]
                for role in ('default', 'active', 'addon', 'user')}

    def snapshot(self):
        obj = self.object
        return {
            'location': list(obj.location),
            'rotation_matrix': [value for row in obj.rotation_euler.to_matrix() for value in row],
            'scale': list(obj.scale),
            'matrix_world': [value for row in obj.matrix_world for value in row],
            'mesh_coordinates': [list(vertex.co) for vertex in obj.data.vertices],
            'modal_operators_observable': hasattr(self.common.window, 'modal_operators'),
            'modal_operators': [operator.bl_idname for operator in
                                getattr(self.common.window, 'modal_operators', ())],
        }

    @staticmethod
    def geometry_equal(left, right):
        return (all(not changed(left[key], right[key]) for key in
                    ('location', 'rotation_matrix', 'scale', 'matrix_world'))
                and left['mesh_coordinates'] == right['mesh_coordinates'])

    def press(self, key):
        self.common.event(key)
        self.common.event(key, 'RELEASE')

    def start(self):
        self.common.configs.update()
        self.initial_maps = self.maps()
        self.common.start()
        self.proof['exact_rows'] = {
            row_id: {role: self.common.exact_count(role, binding)
                     for role in ('default', 'active', 'addon', 'user')}
            for row_id, binding in self.common.bindings.items()
        }
        self.proof['maps_before_without_control'] = self.initial_maps
        self.record('modal_switch_ready')

    def case(self, control, *, switch_key='E', case_label=None):
        result = {'case': case_label or ('modal_direct_rotate_control' if control else 'modal_translate_e_switch'),
                  'minimal_invocation': 'transform.rotate' if control else 'transform.translate',
                  'switch_key': switch_key,
                  'phases': []}
        state = {}

        def observe(phase):
            value = self.snapshot()
            result['phases'].append({'phase': phase, 'snapshot': value})
            state[phase] = value
            self.record(result['case'] + '_' + phase)

        def prepare():
            self.common.setup_object('Object Mode')
            self.object = self.bpy.data.objects['Category Ordinary Cube']
            self.object.location = (0, 0, 0)
            self.object.rotation_euler = (0, 0, 0)
            self.object.scale = (1.0, 1.3, 0.7)
            with self.common.context():
                self.bpy.ops.wm.tool_set_by_id(name='builtin.select_box')
                self.bpy.context.view_layer.update()
            self.receipt['dispatch'].append(result)
            observe('before')

        def prime():
            state['control_index'] = len(self.common.input_callbacks)
            self.common.event('MOUSEMOVE', 'NOTHING')
            self.press('F23')

        def invoke():
            callbacks = self.common.input_callbacks[state['control_index']:]
            delivered = {'area': 'VIEW_3D', 'region': 'WINDOW'} in callbacks
            result['input_delivery'] = {'callbacks': callbacks, 'delivered': delivered}
            assert delivered, 'Window control did not reach the intended 3D region'
            with self.common.context():
                operator = self.bpy.ops.transform.rotate if control else self.bpy.ops.transform.translate
                result['invoke_poll'] = operator.poll()
                assert result['invoke_poll']
                result['invoke_result'] = sorted(operator('INVOKE_DEFAULT'))
            assert result['invoke_result'] == ['RUNNING_MODAL']

        def initial_effect():
            observe('initial_motion')
            field = 'rotation_matrix' if control else 'location'
            result['initial_positive_effect'] = changed(state['before'][field], state['initial_motion'][field])
            assert result['initial_positive_effect'], 'Native operation lacks a positive movement control'

        def after_first_e():
            observe('after_first_e_motion')
            result['first_e_rotation_observed'] = changed(
                state['initial_motion']['rotation_matrix'], state['after_first_e_motion']['rotation_matrix'])

        def after_second_e():
            observe('after_second_e_motion')
            result['second_e_rotation_changed'] = changed(
                state['after_first_e_motion']['rotation_matrix'], state['after_second_e_motion']['rotation_matrix'])
            result['trackball_identity'] = 'unresolved by geometry change alone'

        def cancelled():
            observe('after_cancel')
            result['cancel_restored_geometry'] = self.geometry_equal(state['before'], state['after_cancel'])
            assert result['cancel_restored_geometry']

        def finish():
            observe('after_extra_motion')
            result['confirmation_stopped_motion'] = self.geometry_equal(
                state['after_confirm'], state['after_extra_motion'])
            assert result['confirmation_stopped_motion']

        self.steps.extend((prepare, prime, invoke,
                           lambda: self.common.event('MOUSEMOVE', 'NOTHING', dx=60, dy=30),
                           initial_effect))
        if control:
            self.steps.extend((lambda: self.press('ESC'), cancelled))
        else:
            self.steps.extend((lambda: self.press(switch_key),
                               lambda: self.common.event('MOUSEMOVE', 'NOTHING', dx=120, dy=70),
                               after_first_e, lambda: self.press(switch_key),
                               lambda: self.common.event('MOUSEMOVE', 'NOTHING', dx=160, dy=-20),
                               after_second_e, lambda: self.press('RET'),
                               lambda: observe('after_confirm'),
                               lambda: self.common.event('MOUSEMOVE', 'NOTHING', dx=180, dy=10),
                               finish))

    def cleanup(self):
        if self.cleaned or self.initial_maps is None:
            return
        try:
            self.common.cleanup()
        finally:
            current = self.maps()
            self.proof['maps_after_without_control'] = current
            self.proof['exact_source_and_merged_preservation'] = current == self.initial_maps
            self.record('modal_switch_preservation')
        assert self.proof['exact_source_and_merged_preservation']
        self.cleaned = True
        self.proof['status'] = 'cleanup complete; inspect per-case phase receipts for completion and effects'

    def append(self):
        self.steps.append(self.start)
        self.case(control=True)
        self.case(control=False)
        self.steps.append(self.cleanup)
        return self
