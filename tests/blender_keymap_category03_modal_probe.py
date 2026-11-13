"""Disposable native-template experiment, never a production capability."""

from copy import deepcopy
import json
from pathlib import Path


class PlannedInstallFailure(RuntimeError):
    pass


class ModalAliasProbeCases:
    E_IDS = (
        '299e9dbeb54d018fa47270d4aef02ecc9143a6bc0882df7d3dc0c836fa2df822',
        '95d1e4739cb33e21cb88513fd041e4a20cd56a06dd022e945218fb4d65af778e',
    )
    R_IDS = (
        '12ce5dca52b981775597be57252b0f9b8582d7f4b180aab5c1dd837b03340b93',
        '75db925e83eecc24de09c1eef4cd3b8aa8307566aaf417835807d258ede0d2df',
    )
    TOKENS = ('ROTATE', 'TRACKBALL')
    BINDING_FIELDS = ('target', 'event', 'active', 'properties', 'read_issues')

    def __init__(self, common, modal_type, ledger_path):
        self.common = common
        self.witness = modal_type(common)
        self.steps, self.receipt, self.record = common.steps, common.receipt, common.record
        rows = {row['row_id']: row['binding'] for row in
                map(json.loads, Path(ledger_path).read_text().splitlines())}
        self.expected = {token: rows[row_id] for token, row_id in zip(self.TOKENS, self.E_IDS)}
        self.templates = {token: rows[row_id] for token, row_id in zip(self.TOKENS, self.R_IDS)}
        for token in self.TOKENS:
            desired, template = self.expected[token], self.templates[token]
            assert desired['event']['repeat'] is True and template['event']['repeat'] is False
            adapted = deepcopy(template)
            adapted['event'].update(type='E', repeat=True)
            assert adapted == desired, 'Unexpected R-to-E field differences'
        self.owned = []
        self.native_map = None
        self.baseline = None
        self.installed_ids = {}
        self.proof = {'test_only': True, 'runtime_capability_changes': 0,
                      'E_ledger_ids': list(self.E_IDS), 'R_template_ids': list(self.R_IDS),
                      'expected_E_order': list(self.TOKENS),
                      'copy_changes': {'type': ['R', 'E'], 'repeat': [False, True]},
                      'generations': [], 'checkpoints': [], 'user_edit_limit':
                      'Current-process merged edits and exact release only; no save/reopen or production UI claim.'}
        self.receipt['modal_alias_probe'] = self.proof
        self.witness.proof['interpretation'] = 'Test-only native-template aliases; inspect live identities and exact preservation.'

    @classmethod
    def binding_matches(cls, row, binding):
        return all(row[field] == binding[field] for field in cls.BINDING_FIELDS)

    def modal_map(self, role):
        scope = self.templates['ROTATE']['scope']
        maps = [km for km in getattr(self.common.configs, role).keymaps
                if km.name == scope['name'] and km.space_type == scope['space_type']
                and km.region_type == scope['region_type'] and km.is_modal]
        assert len(maps) == 1, 'Missing or ambiguous native modal map'
        return maps[0]

    def start(self):
        bpy, configs = self.common.bpy, self.common.configs
        assert tuple(bpy.app.version) == (4, 5, 1) and bpy.app.build_hash == b'b0a72b245dcf'
        assert configs.active.name == 'Blender'
        assert configs.active.as_pointer() == configs.default.as_pointer()
        assert not list(getattr(self.common.window, 'modal_operators', ()))
        self.native_map = self.modal_map('default')
        self.map_pointer = self.native_map.as_pointer()
        self.witness.start()
        self.baseline = self.witness.maps()  # F23 stays present throughout the inner comparisons.
        self.preflight()
        self.record('modal_alias_probe_ready')

    def preflight(self):
        configs = self.common.configs
        assert configs.active.as_pointer() == configs.default.as_pointer()
        assert self.modal_map('default').as_pointer() == self.map_pointer
        assert not self.owned
        assert not any(item.type in ('E', 'F18') for role in ('default', 'active', 'addon', 'user')
                       for km in getattr(configs, role).keymaps if km.name == 'Transform Modal Map'
                       for item in km.keymap_items), 'Existing probe-event modal entry'
        capture = self.common.capture(self.native_map)
        assert capture['scope'] == self.templates['ROTATE']['scope']
        result = {}
        for token, binding in self.templates.items():
            matches = [row for row in capture['items'] if self.binding_matches(row, binding)]
            assert len(matches) == 1, 'Native R template missing or ambiguous'
            native = [item for item in self.native_map.keymap_items if item.id == matches[0]['blender_id']]
            assert len(native) == 1
            result[token] = native[0]
        return result

    def journal(self, item, token):
        entry = {'pointer': item.as_pointer(), 'native_id': item.id, 'token': token}
        self.owned.append(entry)
        self.proof['generations'].append(dict(entry))
        self.witness.proof['modal_map_mutations'] += 1

    def copy(self, template, token):
        before = {(item.as_pointer(), item.id) for item in self.native_map.keymap_items}
        try:
            item = self.native_map.keymap_items.new_from_item(template, head=True)
        except Exception:
            added = [item for item in self.native_map.keymap_items
                     if (item.as_pointer(), item.id) not in before]
            if len(added) == 1:
                self.journal(added[0], token)
            elif added:
                self.proof['ambiguous_native_allocation'] = len(added)
            raise
        self.journal(item, token)
        item.type = 'E'
        item.repeat = True

    def live_owned(self, entry):
        assert self.modal_map('default').as_pointer() == self.map_pointer
        matches = [item for item in self.native_map.keymap_items
                   if item.as_pointer() == entry['pointer'] and item.id == entry['native_id']]
        assert len(matches) == 1, 'Owned generation missing or ambiguous'
        return matches[0]

    def remove_owned(self):
        errors = []
        for entry in reversed(self.owned[:]):
            try:
                self.native_map.keymap_items.remove(self.live_owned(entry))
                self.owned.remove(entry)
            except Exception as exc:
                errors.append(type(exc).__name__ + ': ' + str(exc))
        self.common.configs.update()
        if errors:
            self.proof['removal_errors'] = errors
        assert not errors and not self.owned

    def exact_checkpoint(self, label):
        self.common.configs.update()
        current = self.witness.maps()
        exact = current == self.baseline
        self.proof['checkpoints'].append({'label': label, 'exact': exact, 'maps': current})
        self.record(label)
        assert exact, 'Strict source/merged comparison failed at ' + label

    def validate_install(self):
        self.common.configs.update()
        current = self.witness.maps()
        self.installed_ids = {}
        for role in ('default', 'active', 'user'):
            km = self.modal_map(role)
            captured = self.common.capture(km)
            ids = {}
            for token in self.TOKENS:
                matches = [row for row in captured['items']
                           if self.binding_matches(row, self.expected[token])]
                assert len(matches) == 1, 'Incomplete or ambiguous emitted E binding'
                ids[token] = matches[0]['blender_id']
            emitted = [row['target'] for row in captured['items'] if row['blender_id'] in ids.values()]
            assert emitted == list(self.TOKENS), 'Native E token ordering differs'
            self.installed_ids[role] = ids
        self.assert_foreign_items(current)
        self.proof.setdefault('installations', []).append({'owned_ids_by_role': deepcopy(self.installed_ids),
                                                           'maps': current})
        self.record('modal_alias_pair_installed')

    def assert_foreign_items(self, current):
        for role, before_maps in self.baseline.items():
            after_maps = current[role]
            assert [m['scope'] for m in before_maps] == [m['scope'] for m in after_maps]
            for before, after in zip(before_maps, after_maps):
                if before['scope']['name'] != 'Transform Modal Map':
                    assert after == before
                    continue
                ids = set(self.installed_ids.get(role, {}).values())
                foreign = [row for row in after['items'] if row['blender_id'] not in ids]
                assert foreign == before['items'], 'Foreign modal item changed'
        # Complete map metadata remains recorded. Exact full equality is required
        # at every release; no aggregate-marker normalization is applied there.

    def install(self, *, planned_failure=False):
        templates = self.preflight()
        try:
            for index, token in enumerate(reversed(self.TOKENS)):
                self.copy(templates[token], token)
                if planned_failure and index == 0:
                    raise PlannedInstallFailure('after first owned copy')
            self.validate_install()
        except Exception as exc:
            self.proof.setdefault('install_failures', []).append({'type': type(exc).__name__,
                'planned': isinstance(exc, PlannedInstallFailure), 'owned': deepcopy(self.owned),
                'maps': self.witness.maps()})
            try:
                self.remove_owned()
            finally:
                self.exact_checkpoint('modal_alias_install_rollback')
            raise

    def partial_install_control(self):
        try:
            self.install(planned_failure=True)
        except PlannedInstallFailure:
            self.proof['partial_install_rollback_passed'] = True
        else:
            raise AssertionError('Planned installation fault did not occur')

    def check_case(self, expected_switch):
        case = self.receipt['dispatch'][-1]
        phases = {phase['phase']: phase['snapshot'] for phase in case['phases']}
        expected = ['TRANSFORM_OT_translate', 'TRANSFORM_OT_rotate', 'TRANSFORM_OT_trackball'] \
            if expected_switch else ['TRANSFORM_OT_translate'] * 3
        actual = [phases[phase]['modal_operators'] for phase in
                  ('initial_motion', 'after_first_e_motion', 'after_second_e_motion')]
        assert actual == [[operator] for operator in expected]
        assert case['first_e_rotation_observed'] == expected_switch
        assert case['second_e_rotation_changed'] == expected_switch
        assert phases['after_confirm']['modal_operators'] == []
        assert phases['after_extra_motion'] == phases['after_confirm']
        case['expected_operator_sequence_verified'] = True

    def release(self):
        self.remove_owned()
        self.exact_checkpoint('modal_alias_pair_released')

    def edit_owned_user_rows(self):
        for entry in self.owned:
            self.live_owned(entry)  # Validate source generation before touching merged copies.
        km = self.modal_map('user')
        before = self.witness.maps()
        edits = {}
        self.proof['user_edits'] = {'before': before, 'edited_user_identities': edits,
                                   'native_aliasing_assumed': False}
        try:
            for token in self.TOKENS:
                native_id = self.installed_ids['user'][token]
                matches = [item for item in km.keymap_items if item.id == native_id]
                assert len(matches) == 1
                captured = next(row for row in self.common.capture(km)['items'] if row['blender_id'] == native_id)
                assert self.binding_matches(captured, self.expected[token])
                item = matches[0]
                edits[token] = {'pointer': item.as_pointer(), 'native_id': native_id}
                item.type = 'F18'
                item.active = token != 'ROTATE'
        finally:
            self.common.configs.update()
            after = self.witness.maps()
            self.proof['user_edits']['after'] = after
            self.record('modal_alias_user_edits')
        for token in self.TOKENS:
            expected = deepcopy(self.expected[token])
            expected['event']['type'] = 'F18'
            expected['active'] = token != 'ROTATE'
            matches = [row for row in self.common.capture(self.modal_map('user'))['items']
                       if row['blender_id'] == edits[token]['native_id']]
            assert len(matches) == 1 and self.binding_matches(matches[0], expected)
        self.assert_foreign_items(after)
        self.proof['user_edits']['complete_readback_passed'] = True

    def cleanup(self):
        if self.witness.initial_maps is None:
            return
        try:
            self.remove_owned()
        finally:
            self.witness.cleanup()

    def append_switch_case(self, key, label, expected):
        self.witness.case(False, switch_key=key, case_label=label)
        self.steps.append(lambda: self.check_case(expected))

    def append(self):
        self.steps.append(self.start)
        self.witness.case(True, case_label='modal_alias_rotate_cancel_control')
        self.steps.extend((self.partial_install_control, self.install))
        self.append_switch_case('E', 'modal_alias_E_enabled', True)
        self.append_switch_case('R', 'modal_alias_R_with_E_enabled', True)
        self.steps.append(self.release)
        self.append_switch_case('E', 'modal_alias_E_after_release', False)
        self.append_switch_case('R', 'modal_alias_R_after_release', True)
        self.steps.extend((self.install, self.edit_owned_user_rows, self.release, self.cleanup))
        return self
