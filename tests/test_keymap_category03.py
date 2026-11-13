"""Portable category 03 reconciliation and registration checks."""

from collections import Counter
from contextlib import nullcontext
import copy
from dataclasses import asdict
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

from runtime_keymap_fakes import FakeItems, FakeRuntime, row
from keymap_native_evidence import unpack_native


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures'
BASELINE = FIXTURES / 'deluxe_keymaps'
CATEGORY = FIXTURES / 'deluxe_keymaps_category03'
FRAMING = 'navigation_view_framing'
SELECTION_ALL_NONE = 'selection_all_none'
SELECTION_CIRCLE = 'selection_circle'
UV_BRACKETS = 'selection_more_less_uv_brackets'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def read_jsonl(path):
    with path.open(encoding='utf-8') as stream:
        return [json.loads(line) for line in stream]


class Category03Evidence:
    @classmethod
    def setUpClass(cls):
        cls.manifest = read_json(CATEGORY / 'manifest.json')
        cls.baseline = read_json(BASELINE / 'capture-manifest.json')
        cls.reconciliation = read_jsonl(CATEGORY / 'reconciliation.jsonl')
        cls.rows = {record['row_id']: record for record in cls.reconciliation}
        cls.ledger = {
            record['row_id']: record
            for record in read_jsonl(BASELINE / 'reconciliation-ledger.jsonl')
            if record['owner'] == '03'
        }


class Category03ReconciliationTests(Category03Evidence, unittest.TestCase):
    def test_review_uses_accepted_stock_blender_identity(self):
        base = self.manifest['base']
        stock = self.baseline['captures']['stock']
        neither = self.baseline['captures']['neither']
        industry = self.baseline['captures']['industry']
        self.assertEqual(self.manifest['baseline_id'], self.baseline['id'])
        self.assertEqual(base['capture'], stock['id'])
        self.assertEqual(base['keyconfig'], stock['active_keyconfig'])
        self.assertEqual((base['keyconfig'], base['platform']), ('Blender', 'macOS arm64'))
        self.assertEqual(base['blender'], self.baseline['test_blender'])
        # bl_idname is Blender RNA metadata, outside the factory keyconfig options.
        stock_options = {name: value for name, value in stock['active_options'].items()
                         if name != 'bl_idname'}
        self.assertEqual(base['options'], stock_options)
        self.assertEqual(base['option_differences_from_neither'], {
            name: {'stock': value, 'neither': neither['active_options'][name]}
            for name, value in stock_options.items()
            if value != neither['active_options'][name]
        })
        for capture in (neither, self.baseline['captures']['no-preset']):
            self.assertEqual(base['no_preset_and_neither_active_keyconfig'],
                             capture['active_keyconfig'])
        self.assertEqual(base['bundled_keyconfig_source_sha256'], {
            'Blender.py': '741c38bcef052efdd2ded5cab5d3790307fd336000f0868433442e5acb8b4bcb',
            'keymap_data/blender_default.py':
                '1881db1460b9d0984aba81a0ec8398efe5ef5de6fb81681d212e1d334d56a819',
        })
        audit = self.manifest['audit']
        self.assertEqual(audit['industry_comparator'], {
            'capture': industry['id'],
            'input_probe_limit': industry['input_probe_limit'],
        })
        self.assertEqual(audit['order']['snapshot_sha256'], {
            capture: self.baseline['captures'][capture]['snapshot_sha256']
            for capture in ('stock', 'full', 'industry', 'neither')
        })
        accepted = (
            'tests/fixtures/deluxe_keymaps/capture-manifest.json',
            'tests/fixtures/deluxe_keymaps/reconciliation-ledger.jsonl',
            'tests/fixtures/deluxe_keymaps/comparison-deltas.jsonl',
            'tests/fixtures/deluxe_keymaps_runtime/integrated-native.json',
        )
        self.assertEqual(audit['accepted_fixture_sha256'], {
            path: sha256((ROOT / path).read_bytes()).hexdigest() for path in accepted
        })

    def test_review_partitions_the_exact_owner03_ledger(self):
        audit = self.manifest['audit']
        self.assertEqual(self.manifest['category'], '03')
        self.assertEqual(len(self.reconciliation), 1032)
        self.assertEqual(audit['row_count'], len(self.reconciliation))
        self.assertEqual([review['row_id'] for review in self.reconciliation],
                         sorted(self.ledger))
        self.assertEqual(Counter(review['status'] for review in self.reconciliation),
                         audit['classification_counts'])
        self.assertEqual(audit['classification_counts'], {
            'base-equal': 160, 'existing': 280, 'reference-delta': 392, 'unresolved': 200,
        })
        self.assertEqual(Counter(review['runtime_disposition'] for review in self.reconciliation),
                         audit['runtime_disposition_counts'])
        self.assertEqual(audit['runtime_disposition_counts'], {
            'inherit': 327,
            'preserve-existing-declaration': 157,
            'review-full-side-candidate': 140,
            'stock-side-change': 252,
            'unresolved': 156,
        })

    def test_uv_transfer_is_limited_to_eight_authorized_candidates(self):
        transfers = self.manifest['authorized_transfers']
        self.assertEqual(set(transfers), {'04'})
        handoff = transfers['04']
        self.assertEqual(handoff['authorized_by'], 'root coordinator')
        self.assertEqual(handoff['source_chat'], '01a1d1f1-9859-7a11-b53d-0777e15aac0c')
        self.assertEqual({group: len(ids) for group, ids in handoff['groups'].items()}, {
            'uv_q_boundary': 1, 'other_uv_tweak_fallback': 2, 'uv_loop_linked': 5,
        })
        transferred = {
            row_id: {
                'to_category': '04', 'group': group, 'authorized_by': handoff['authorized_by'],
                'source_chat': handoff['source_chat'], 'reason': handoff['reason'],
            }
            for group, row_ids in handoff['groups'].items()
            for row_id in row_ids
        }
        self.assertEqual(len(transferred), 8)
        self.assertEqual(transferred, {
            row_id: review['authorized_transfer']
            for row_id, review in self.rows.items() if 'authorized_transfer' in review
        })
        selectors = {
            'uv_q_boundary': ('UV Editor', 'Q', {'wm.tool_set_by_id'}),
            'other_uv_tweak_fallback': (
                'Image Editor Tool: Uv, Tweak (fallback)', 'RIGHTMOUSE', {'uv.select'},
            ),
            'uv_loop_linked': ('UV Editor', 'LEFTMOUSE', {'uv.select_loop', 'uv.select_linked_pick'}),
        }
        for row_id, transfer in transferred.items():
            with self.subTest(row_id=row_id):
                review = self.rows[row_id]
                self.assertEqual(review['status'], 'reference-delta')
                self.assertEqual(review['runtime_disposition'], 'review-full-side-candidate')
                self.assertNotIn('declaration', review)
                binding = self.ledger[row_id]['binding']
                scope, event_type, targets = selectors[transfer['group']]
                self.assertEqual(binding['scope']['name'], scope)
                self.assertEqual(binding['event']['type'], event_type)
                self.assertIn(binding['target'], targets)

        retained = handoff['retained_by_03']
        self.assertCountEqual(retained['declaration_groups'], [UV_BRACKETS, SELECTION_ALL_NONE])
        for key, row_id in retained['transform_boundary'].items():
            self.assertIn(row_id, self.rows)
            self.assertNotIn(row_id, transferred)
            event = self.ledger[row_id]['binding']['event']
            self.assertEqual(event['type'], key[-1])
            self.assertEqual(bool(event['shift']), key.startswith('Shift-'))
        self.assertEqual(set(retained['transform_boundary']), {'W', 'G', 'Shift-W'})

    def test_evidence_links_resolve_to_exact_accepted_rows(self):
        deltas = {
            (delta['comparison'], delta['id']): delta
            for delta in read_jsonl(BASELINE / 'comparison-deltas.jsonl')
        }
        contract_samples = {
            (sample['row_id'], sample['capture'])
            for sample in read_json(BASELINE / 'contract-cases.json')['cases']
        }
        audit = self.manifest['audit']
        link_count = 0
        static_overlap_count = 0
        for row_id, review in self.rows.items():
            with self.subTest(row_id=row_id):
                accepted = self.ledger[row_id]
                evidence = review['evidence']
                self.assertEqual(evidence['owner_reason'], accepted['classification_reason'])
                for role in ('user', 'addon'):
                    self.assertEqual(evidence[f'{role}_counts'], [
                        accepted['presence'].get(capture, {}).get(role, 0)
                        for capture in audit['count_capture_order']
                    ])
                for role in ('active', 'default'):
                    self.assertEqual(evidence[f'full_{role}_count'],
                                     accepted['presence'].get('full', {}).get(role, 0))
                self.assertEqual(evidence['reference_owned_count'],
                                 accepted['runtime_coverage']['reference_bluehole_owned'])
                self.assertEqual(evidence['development_owned_count'],
                                 accepted['runtime_coverage']['development_bluehole_owned'])
                self.assertEqual(evidence['development_user_count'],
                                 accepted['runtime_coverage']['development_user_candidates'])

                links = []
                for comparison, entries in evidence['comparison_links'].items():
                    for kind, side, delta_id in entries:
                        delta = deltas[comparison, delta_id]
                        self.assertEqual(delta['kind'], kind)
                        self.assertEqual(delta[side]['row_id'], row_id)
                        links.append(dict(comparison=comparison, kind=kind, side=side,
                                          delta_id=delta_id))
                self.assertCountEqual(links, accepted['evidence'])
                link_count += len(links)
                for capture in evidence.get('contract_captures', ()):
                    self.assertIn((row_id, capture), contract_samples)
                overlaps = evidence.get('static_source_overlap', ())
                if overlaps:
                    static_overlap_count += 1
                for overlap in overlaps:
                    self.assertEqual(len(overlap), len(audit['static_source_overlap_fields']))
        self.assertEqual(link_count, audit['comparison_link_count'])
        self.assertEqual(link_count, 2985)
        self.assertEqual(static_overlap_count,
                         audit['evidence_counts']['static_declaration_overlap'])

    def test_inheritance_and_gaps_remain_distinct_from_reviewed_declarations(self):
        reviewed_rows = {}
        for group, declaration in self.manifest['reviewed_declarations'].items():
            self.assertTrue((ROOT / declaration['source']).is_file())
            for action, row_ids in declaration['actions'].items():
                for index, row_id in enumerate(row_ids):
                    self.assertNotIn(row_id, reviewed_rows)
                    reviewed_rows[row_id] = {
                        'group': group, 'action': action, 'binding_index': index,
                    }
        extension = self.manifest['reviewed_existing_declarations'][UV_BRACKETS]
        self.assertTrue((ROOT / extension['source']).is_file())
        for action, binding in extension['bindings'].items():
            row_id = binding['row_id']
            self.assertNotIn(row_id, reviewed_rows)
            reviewed_rows[row_id] = {
                'group': UV_BRACKETS, 'action': action, 'binding_index': binding['binding_index'],
            }
        reuse = self.manifest['accepted_mechanism_reuse']
        self.assertEqual(reuse['binding_count'], 12)
        self.assertFalse(set(reviewed_rows) & set(reuse['bindings']))
        reviewed_rows.update(reuse['bindings'])
        subtract = self.manifest['object_subtract_route']
        self.assertNotIn(subtract['row_id'], reviewed_rows)
        reviewed_rows[subtract['row_id']] = subtract['declaration']
        extend = self.manifest['object_extend_route']
        self.assertNotIn(extend['row_id'], reviewed_rows)
        reviewed_rows[extend['row_id']] = extend['declaration']
        uv_extend = self.manifest['uv_extend_route']
        self.assertNotIn(uv_extend['row_id'], reviewed_rows)
        reviewed_rows[uv_extend['row_id']] = uv_extend['declaration']
        self.assertEqual(self.manifest['candidate_accounting'], {
            'implemented': 38, 'transferred_04': 8, 'remaining_03': 94})
        self.assertEqual({
            row_id: review['declaration']
            for row_id, review in self.rows.items() if 'declaration' in review
        }, reviewed_rows)

        unresolved = Counter()
        for row_id, review in self.rows.items():
            with self.subTest(row_id=row_id):
                accepted = self.ledger[row_id]
                binding = accepted['binding']
                stock = accepted['presence'].get('stock', {}).get('user', 0)
                full = accepted['presence'].get('full', {}).get('user', 0)
                gates = review['potential_change_gates']
                self.assertIn('dispatch-unproved', gates)
                if review['status'] == 'unresolved':
                    if 'operator-or-RNA-schema-gap' in gates:
                        unresolved['schema_or_rna_gap'] += 1
                        self.assertTrue(binding['read_issues'] or accepted['ambiguities'])
                    elif stock == full == 0:
                        unresolved['absent_from_both_merged_user_roles'] += 1
                    else:
                        unresolved['equal_counts_with_fallback_attribution_caveat'] += 1
                        self.assertEqual(stock, full)
                        self.assertTrue(accepted['ambiguities'])
                if review['provider_inherited']:
                    full_roles = accepted['presence']['full']
                    neither_roles = accepted['presence']['neither']
                    for role in ('user', 'addon'):
                        self.assertGreater(full_roles[role], 0)
                        self.assertEqual(full_roles[role], neither_roles[role])
                    self.assertEqual(review['runtime_disposition'], 'inherit')
                    self.assertEqual(review['basis'], 'provider-equal-to-neither')
                    self.assertEqual(review['evidence']['reference_owned_count'], 0)
                if review['status'] == 'base-equal':
                    self.assertGreater(stock, 0)
                    self.assertEqual(stock, full)
                    self.assertEqual(review['basis'], 'stock-equal-user-count')
                    self.assertEqual(review['runtime_disposition'], 'inherit')
                if review['runtime_disposition'] == 'preserve-existing-declaration':
                    self.assertEqual(review['status'], 'existing')
                    self.assertGreater(review['evidence']['development_owned_count'], 0)
                if review['status'] == 'reference-delta':
                    self.assertNotEqual(stock, full)
                    self.assertEqual(review['basis'], 'stock-to-full-user-count-difference')
                    self.assertTrue(any(link['comparison'] == 'stock-to-full'
                                        and link['kind'] != 'reordered'
                                        for link in accepted['evidence']))
                if review['runtime_disposition'] == 'stock-side-change':
                    self.assertGreater(stock, full)
                    self.assertIn('old-event-suppression-unproved', gates)
                if row_id in reviewed_rows:
                    self.assertEqual(review['status'], 'reference-delta')
                    self.assertEqual(review['runtime_disposition'], 'review-full-side-candidate')
                    self.assertFalse(review['provider_inherited'])
                    self.assertTrue(binding['active'])
                    self.assertFalse(binding['scope']['is_modal'])
                    self.assertGreater(full, stock)
        self.assertEqual(unresolved, self.manifest['audit']['unresolved_partition'])

    def test_order_observations_preserve_the_inherited_precision_token(self):
        order = self.manifest['audit']['order']
        relative, absolute = map(set, (order['relative_rank_change_ids'],
                                      order['absolute_offset_only_ids']))
        self.assertEqual((len(relative), len(absolute)), (63, 74))
        self.assertFalse(relative & absolute)
        self.assertLessEqual(relative | absolute, self.ledger.keys())
        self.assertEqual(order['owner03_active_literal_overlap_inversions'], 0)
        precision = order['inherited_precision_example']
        row_id = precision['row_id']
        self.assertIn(row_id, relative)
        self.assertEqual(self.ledger[row_id]['binding']['target'], 'PRECISION')
        self.assertEqual(precision['absolute_order_by_capture'],
                         {'stock': 53, 'full': 40, 'industry': 52, 'neither': 53})
        self.assertEqual(self.rows[row_id]['runtime_disposition'], 'inherit')
        self.assertNotIn('declaration', self.rows[row_id])


class Category03ModalProbeTests(unittest.TestCase):
    def test_uv_extend_shared_schedule_keeps_three_event_paths_separate(self):
        from blender_keymap_category03_handlers import UVExtendCases
        ledger = {row['row_id']: row for row in read_jsonl(BASELINE / 'reconciliation-ledger.jsonl')}
        bindings = {cell[0]: ledger[cell[0]]['binding'] for cell in UVExtendCases.CELLS}
        self.assertEqual([binding['event']['value'] for binding in bindings.values()], ['CLICK', 'PRESS', 'PRESS'])
        self.assertEqual(len({binding['scope']['name'] for binding in bindings.values()}), 3)
        for binding in bindings.values():
            self.assertEqual(binding['target'], 'uv.select')
            self.assertTrue(binding['properties']['extend'])
            self.assertFalse(binding['properties']['toggle'])
        configs = types.SimpleNamespace(**{role: types.SimpleNamespace(keymaps=[])
                                          for role in ('default', 'active', 'addon', 'user')})
        fake_bpy = types.SimpleNamespace(context=types.SimpleNamespace(
            window_manager=types.SimpleNamespace(keyconfigs=configs)))
        controls = {'ledger_id': UVExtendCases.CELLS[0][0],
                    'binding': bindings[UVExtendCases.CELLS[0][0]],
                    'trials': [{'probe': False, 'initial_selected': selected,
                                'exact_map_event_witnessed': True, 'expected_selection_observed': True,
                                'geometry_and_tool_unchanged': True} for selected in (True, False)]}
        for probe, count, reuse in ((False, 40, None), (True, 67, None), (True, 59, controls)):
            with self.subTest(probe=probe), patch.dict(sys.modules, {'bpy': fake_bpy}):
                steps, receipt = [], {'dispatch': []}
                fixture = UVExtendCases(steps, receipt, Mock(), None, None, None,
                                        bindings=bindings, probe=probe, stock_click_controls=reuse)
                methods = ('prepare', 'start', 'begin_cell', 'prepare_cell', 'install_candidate',
                           'begin_trial', 'press_input', 'release_input', 'finish_trial',
                           'release_cell', 'cleanup')
                for method in methods:
                    setattr(fixture, method, Mock())
                fixture.append()
                self.assertEqual(len(steps), count)
                for step in steps:
                    step()
                self.assertEqual([call.args for call in fixture.begin_cell.call_args_list], list(UVExtendCases.CELLS))
                expected = [(True, False), (False, False)]
                if probe:
                    expected += [(True, True), (False, True)]
                expected = expected * 3
                if reuse:
                    expected = expected[2:]
                self.assertEqual([call.args for call in fixture.begin_trial.call_args_list], expected)
                fixture.prepare.assert_called_once()
                fixture.cleanup.assert_called_once()
                self.assertEqual(fixture.install_candidate.call_count, 3 if probe else 0)
                self.assertFalse(receipt['uv_extend_proof']['production_capability_enabled'])

    def test_uv_extend_positive_control_requires_real_addition_and_unchanged_geometry(self):
        from blender_keymap_category03_handlers import UVExtendCases
        before = {'target_selected': False, 'bystander_selected': True,
                  'uv_positions': [[0, 0, .2, .2], [0, 2, .8, .8]]}
        after = {**before, 'target_selected': True, 'selected': [[0, 0], [0, 2]], 'modal_operators': []}
        control = {'result': ['FINISHED', 'PASS_THROUGH']}
        UVExtendCases.assert_positive_control(control, before, after)
        for changed in ({'target_selected': False}, {'bystander_selected': False},
                        {'selected': [[0, 0], [0, 1], [0, 2]]}, {'uv_positions': []},
                        {'modal_operators': ['TRANSFORM_OT_translate']}):
            with self.subTest(changed=changed), self.assertRaises(AssertionError):
                UVExtendCases.assert_positive_control(control, before, {**after, **changed})
        for result in (['PASS_THROUGH'], ['FINISHED', 'CANCELLED'], ['RUNNING_MODAL']):
            with self.subTest(result=result), self.assertRaises(AssertionError):
                UVExtendCases.assert_positive_control({'result': result}, before, after)

    def test_uv_extend_direct_control_uses_uv_location_instead_of_projected_pixels(self):
        from blender_keymap_category03_handlers import UVExtendCases
        fixture = UVExtendCases.__new__(UVExtendCases)
        fixture.cell = {'tool_requested': 'builtin.select_box', 'tool_map_field': None, 'reused_stock_trials': []}
        fixture.tool_state = Mock(return_value={'idname': 'builtin.select_box'})
        ledger = {row['row_id']: row for row in read_jsonl(BASELINE / 'reconciliation-ledger.jsonl')}
        fixture.binding = ledger[UVExtendCases.CELLS[0][0]]['binding']
        fixture.values = {'point': (2055, 1229)}
        fixture.reset_selection = Mock()
        before = {'target_selected': False, 'bystander_selected': True, 'uv_positions': [[0, 0, .2, .2]]}
        after = {**before, 'target_selected': True, 'selected': [[0, 0], [0, 2]], 'modal_operators': []}
        fixture.snapshot = Mock(side_effect=[before, after])
        fixture.context = nullcontext
        operator = Mock(return_value={'FINISHED', 'PASS_THROUGH'})
        operator.poll.return_value = True
        fixture.bpy = types.SimpleNamespace(ops=types.SimpleNamespace(uv=types.SimpleNamespace(select=operator)))
        fixture.configs, fixture.maps = Mock(), Mock(return_value={})
        fixture.control_class = types.SimpleNamespace(bl_idname='wm.category03_uv_extend_control')
        fixture.allocations, fixture.cell_allocations = [object()], []
        fixture.add_item = Mock()
        fixture.prepare_cell()
        operator.assert_called_once_with('EXEC_DEFAULT', location=(.2, .2), extend=True)
        fixture.reset_selection.assert_called_once_with(False)
        self.assertTrue(fixture.cell['direct_control']['positive_addition'])

    def test_uv_extend_selection_effect_alone_does_not_establish_handler_admission(self):
        from blender_keymap_category03_handlers import UVExtendCases
        trials = [{'probe': probe, 'initial_selected': selected,
                   'exact_map_event_witnessed': True, 'expected_selection_observed': True,
                   'geometry_and_tool_unchanged': True}
                  for probe in (False, True) for selected in (True, False)]
        self.assertTrue(UVExtendCases.matched_effects(trials))
        self.assertFalse(UVExtendCases.matched_effects(trials[:2]))
        self.assertFalse(UVExtendCases.matched_effects(trials[::-1]))
        for index in range(4):
            for field in ('exact_map_event_witnessed', 'expected_selection_observed', 'geometry_and_tool_unchanged'):
                changed = copy.deepcopy(trials)
                changed[index][field] = False
                with self.subTest(index=index, field=field):
                    self.assertFalse(UVExtendCases.matched_effects(changed))

    def test_uv_extend_mouse_witness_only_passes_through(self):
        from blender_keymap_category03_handlers import UVExtendCases
        fixture = UVExtendCases.__new__(UVExtendCases)
        fixture.configs = types.SimpleNamespace(update=Mock(), user=types.SimpleNamespace(keymaps=[]))
        fixture.maps, fixture.add_item, fixture.record = Mock(return_value={}), Mock(), Mock()
        fixture.cell, fixture.proof, fixture.input_callbacks = {'ledger_id': 'exact-test-row'}, {}, []
        fixture.bpy = types.SimpleNamespace(types=types.SimpleNamespace(Operator=object),
                                           utils=types.SimpleNamespace(register_class=Mock()))
        fixture.start()
        context = types.SimpleNamespace(area=types.SimpleNamespace(type='IMAGE_EDITOR', ui_type='UV'),
                                        region=types.SimpleNamespace(type='WINDOW'))
        for key, value in (('LEFTMOUSE', 'PRESS'), ('LEFTMOUSE', 'CLICK'), ('F23', 'PRESS')):
            event = types.SimpleNamespace(type=key, value=value, mouse_region_x=150, mouse_region_y=200,
                                          **UVExtendCases.CONTROL_MODIFIERS)
            result = fixture.control_class().invoke(context, event)
            self.assertEqual(result, {'FINISHED'} if key == 'F23' else {'PASS_THROUGH'})
            self.assertEqual(fixture.input_callbacks[-1]['event'], [key, value])
            self.assertEqual(fixture.input_callbacks[-1]['ledger_id'], 'exact-test-row')

    def test_uv_extend_cleanup_refuses_an_unowned_item_and_retains_strict_failure(self):
        from blender_keymap_category03_handlers import UVExtendCases
        fixture = UVExtendCases.__new__(UVExtendCases)
        foreign = types.SimpleNamespace(id=9, as_pointer=lambda: 22)
        km = types.SimpleNamespace(keymap_items=[foreign])
        allocation = (km, object(), 11, 9)
        fixture.cell_allocations = [allocation]
        fixture.allocations = [allocation]
        with self.assertRaises(AssertionError):
            fixture.release_cell()
        self.assertEqual(km.keymap_items, [foreign])
        self.assertEqual(fixture.allocations, [allocation])
        fixture.cell_allocations, fixture.created_maps = [], []
        fixture.cell = {'trials': [], 'reused_stock_trials': [], 'maps_before_witness': {'foreign': 'original'}}
        fixture.maps = Mock(return_value={'foreign': 'changed'})
        fixture.configs, fixture.record, fixture.probe = Mock(), Mock(), True
        with self.assertRaises(AssertionError):
            fixture.release_cell()
        self.assertFalse(fixture.cell['exact_cell_preservation'])
        self.assertFalse(fixture.cell['production_accepted'])

    def test_uv_extend_retains_failed_candidate_positions_before_asserting(self):
        from blender_keymap_category03_handlers import UVExtendCases
        ledger = {row['row_id']: row for row in read_jsonl(BASELINE / 'reconciliation-ledger.jsonl')}
        fixture = UVExtendCases.__new__(UVExtendCases)
        fixture.bindings = {cell[0]: ledger[cell[0]]['binding'] for cell in UVExtendCases.CELLS}
        fixture.binding = fixture.bindings[UVExtendCases.CELLS[0][0]]
        fixture.cell = {'ledger_id': UVExtendCases.CELLS[0][0]}
        fixture.control_class = types.SimpleNamespace(bl_idname='wm.uv_test_witness')
        candidate = copy.deepcopy(fixture.binding)
        witness = {**candidate, 'target': fixture.control_class.bl_idname, 'properties': {}}
        stock = copy.deepcopy(candidate)
        stock['properties'].update(extend=False, toggle=True)
        for wrong_order in (True, False):
            fixture.result, fixture.record = {'case': 'order_test'}, Mock()
            source = {'scope': candidate['scope'], 'items': [candidate, witness]}
            merged = {'scope': candidate['scope'], 'items':
                      [candidate, witness, stock] if wrong_order else [witness, candidate, stock]}
            fixture.maps = Mock(return_value={'default': [], 'active': [], 'addon': [source], 'user': [merged]})
            if wrong_order:
                with self.assertRaises(AssertionError):
                    fixture.candidate_maps(True)
            else:
                fixture.candidate_maps(True)
            self.assertEqual(fixture.result['native_maps']['user'], [merged])
            self.assertEqual(fixture.result['witness_order']['indices'], [1 if wrong_order else 0])
            self.assertEqual(fixture.result['exact_candidate_counts']['user'][fixture.cell['ledger_id']], 1)
            self.assertEqual(fixture.record.call_args_list[-1].args, ('order_test_admission_order',))

    def test_uv_extend_candidate_source_order_accounts_for_prepend_merge(self):
        from blender_keymap_category03_handlers import UVExtendCases
        fixture = UVExtendCases.__new__(UVExtendCases)
        ledger = {row['row_id']: row for row in read_jsonl(BASELINE / 'reconciliation-ledger.jsonl')}
        fixture.binding = ledger[UVExtendCases.CELLS[0][0]]['binding']
        source = ['witness']
        fixture.allocations, fixture.cell_allocations = [], []
        fixture.configs = Mock()
        def add_item(scope, target, event, properties):
            self.assertEqual(scope, fixture.binding['scope'])
            self.assertEqual(properties, fixture.binding['properties'])
            source.insert(0 if event.get('head') else len(source), 'candidate')
            fixture.allocations.append(object())
        fixture.add_item = add_item
        fixture.install_candidate()
        # Pinned wm_keymap_addon_add uses BLI_addhead for every source item.
        merged = ['stock']
        for item in source:
            merged.insert(0, item)
        self.assertEqual(merged, ['witness', 'candidate', 'stock'])
        self.assertEqual(fixture.cell_allocations, fixture.allocations)

    def test_uv_extend_reference_is_only_two_click_states_without_candidate_insertion(self):
        from blender_keymap_category03_handlers import UVExtendCases, UVExtendReferenceCases
        ledger = {row['row_id']: row for row in read_jsonl(BASELINE / 'reconciliation-ledger.jsonl')}
        bindings = {UVExtendCases.CELLS[0][0]: ledger[UVExtendCases.CELLS[0][0]]['binding']}
        configs = types.SimpleNamespace(**{role: types.SimpleNamespace(keymaps=[])
                                          for role in ('default', 'active', 'addon', 'user')})
        fake_bpy = types.SimpleNamespace(context=types.SimpleNamespace(
            window_manager=types.SimpleNamespace(keyconfigs=configs)))
        with patch.dict(sys.modules, {'bpy': fake_bpy}):
            steps, receipt = [], {'dispatch': []}
            fixture = UVExtendReferenceCases(steps, receipt, Mock(), None, None, None, bindings=bindings)
            for method in ('prepare', 'start', 'begin_cell', 'prepare_cell', 'install_candidate',
                           'begin_trial', 'press_input', 'release_input', 'finish_trial', 'release_cell', 'cleanup'):
                setattr(fixture, method, Mock())
            fixture.append()
            self.assertEqual(len(steps), 16)
            for step in steps:
                step()
            self.assertEqual(fixture.begin_cell.call_args_list[0].args, UVExtendCases.CELLS[0])
            fixture.begin_cell.assert_called_once()
            self.assertEqual([call.args for call in fixture.begin_trial.call_args_list], [(True, False), (False, False)])
            fixture.install_candidate.assert_not_called()
            self.assertTrue(receipt['uv_extend_proof']['reference'])
            self.assertFalse(receipt['uv_extend_proof']['probe'])
            with self.assertRaises(AssertionError):
                UVExtendReferenceCases([], {'dispatch': []}, Mock(), None, None, None, bindings=bindings, probe=True)

    def test_uv_extend_reference_requires_active_user_binding_and_keeps_addon_empty(self):
        from blender_keymap_category03_handlers import UVExtendReferenceCases
        fixture = UVExtendReferenceCases.__new__(UVExtendReferenceCases)
        ledger = {row['row_id']: row for row in read_jsonl(BASELINE / 'reconciliation-ledger.jsonl')}
        row_id = UVExtendReferenceCases.CELLS[0][0]
        fixture.binding = ledger[row_id]['binding']
        fixture.bindings, fixture.cell = {row_id: fixture.binding}, {'ledger_id': row_id}
        fixture.control_class = types.SimpleNamespace(bl_idname='wm.uv_reference_witness')
        candidate = copy.deepcopy(fixture.binding)
        witness = {**candidate, 'target': fixture.control_class.bl_idname, 'properties': {}}
        maps = {'default': [], 'active': [{'scope': candidate['scope'], 'items': [candidate]}],
                'addon': [{'scope': candidate['scope'], 'items': [witness]}],
                'user': [{'scope': candidate['scope'], 'items': [witness, candidate]}]}
        fixture.maps, fixture.record = Mock(return_value=maps), Mock()
        fixture.result = {'case': 'reference_admission'}
        fixture.candidate_maps(False)
        maps['addon'][0]['items'].append(candidate)
        with self.assertRaises(AssertionError):
            fixture.candidate_maps(False)
        self.assertEqual(fixture.result['exact_candidate_counts']['addon'][row_id], 1)

    def test_uv_extend_production_reuses_group_with_two_states_and_no_probe(self):
        from blender_keymap_category03_handlers import UVExtendCases, UVExtendProductionCases
        ledger = {row['row_id']: row for row in read_jsonl(BASELINE / 'reconciliation-ledger.jsonl')}
        binding = ledger[UVExtendCases.CELLS[0][0]]['binding']
        configs = types.SimpleNamespace(**{role: types.SimpleNamespace(keymaps=[])
                                          for role in ('default', 'active', 'addon', 'user')})
        fake_bpy = types.SimpleNamespace(context=types.SimpleNamespace(
            window_manager=types.SimpleNamespace(keyconfigs=configs)))
        with patch.dict(sys.modules, {'bpy': fake_bpy}):
            steps, receipt = [], {'dispatch': []}
            fixture = UVExtendProductionCases(steps, receipt, Mock(), None, None, None, None, {}, binding=binding)
            for method in ('prepare', 'production_baseline', 'toggle', 'start', 'begin_cell', 'prepare_cell',
                           'install_candidate', 'begin_trial', 'press_input', 'release_input', 'finish_trial',
                           'release_cell', 'release_controls', 'cleanup'):
                setattr(fixture, method, Mock())
            fixture.append()
            self.assertEqual(len(steps), 20)
            for step in steps:
                step()
            self.assertEqual([call.args for call in fixture.toggle.call_args_list], [(True,), (False,)])
            self.assertEqual([call.args for call in fixture.begin_trial.call_args_list], [(True, False), (False, False)])
            fixture.install_candidate.assert_not_called()
            fixture.release_controls.assert_called_once()
            self.assertFalse(fixture.WITNESS_HEAD)
            self.assertTrue(UVExtendCases.WITNESS_HEAD)
            self.assertTrue(receipt['uv_extend_production']['production'])
            self.assertFalse(receipt['uv_extend_production']['direct_candidate_injection'])

    def test_uv_extend_production_control_failure_still_attempts_group_release(self):
        from blender_keymap_category03_handlers import UVExtendProductionCases, ObjectSubtractProductionCases
        fixture = UVExtendProductionCases.__new__(UVExtendProductionCases)
        fixture.closed, fixture.proof = False, {}
        fixture.release_controls = Mock(side_effect=AssertionError('strict control preservation'))
        with patch.object(ObjectSubtractProductionCases, 'cleanup') as release:
            with self.assertRaises(AssertionError):
                fixture.cleanup()
            release.assert_called_once_with(fixture)
        self.assertFalse(fixture.closed)
        self.assertIn('strict control preservation', fixture.proof['combined_cleanup_errors'][0])

    def test_extend_production_reuses_two_states_without_probe_injection(self):
        from blender_keymap_category03_handlers import ObjectExtendProductionCases, ObjectExtendTrial
        ledger = {r['row_id']: r for r in read_jsonl(BASELINE / 'reconciliation-ledger.jsonl')}
        binding = ledger[ObjectExtendTrial.LEDGER_ID]['binding']
        fake_bpy = types.SimpleNamespace(context=types.SimpleNamespace(
            window_manager=types.SimpleNamespace(keyconfigs=object())))
        with patch.dict(sys.modules, {'bpy': fake_bpy}):
            steps, receipt = [], {'dispatch': []}
            fixture = ObjectExtendProductionCases(steps, receipt, lambda *a, **k: None,
                None, None, None, None, {}, binding=binding).append()
        self.assertEqual(len(steps), 28)
        self.assertEqual([f.initial_selected for f in fixture.fixtures], [True, False])
        self.assertTrue(all(not f.probe and not f.defer_preservation_failure for f in fixture.fixtures))
        self.assertFalse(receipt['extend_production']['direct_candidate_injection'])
        for initial in (True, False):
            before = {'target_selected': initial, 'target_active': initial,
                      'bystander_selected': True, 'bystander_visible': True}
            after = {'target_selected': True, 'target_active': True, 'bystander_selected': True}
            result = {'phases': [{'phase': 'before_press', 'snapshot': before},
                                 {'phase': 'after_release', 'snapshot': after}],
                      'direct_control': {'positive_addition': True}}
            fixture.assert_trial_effect(result, initial, True)
            for field in after:
                with self.subTest(initial=initial, field=field), self.assertRaises(AssertionError):
                    changed = copy.deepcopy(result)
                    changed['phases'][1]['snapshot'][field] = False
                    fixture.assert_trial_effect(changed, initial, True)

    def test_extend_probe_uses_exact_selector_six_states_and_owned_modifiers(self):
        from blender_keymap_category03_handlers import (
            BINDINGS, ObjectExtendCases, ObjectExtendTrial, ObjectSubtractCases)
        ledger = {r['row_id']: r for r in read_jsonl(BASELINE / 'reconciliation-ledger.jsonl')}
        binding = ledger[ObjectExtendTrial.LEDGER_ID]['binding']
        self.assertEqual(binding['scope']['name'], '3D View')
        self.assertEqual((binding['event']['type'], binding['event']['value']), ('LEFTMOUSE', 'CLICK'))
        self.assertEqual(ObjectExtendTrial.CONTROL_MODIFIERS,
                         {name: bool(binding['event'][name]) for name in ('shift', 'oskey', 'ctrl', 'alt')})
        self.assertEqual(ObjectSubtractCases.CONTROL_MODIFIERS, {})
        self.assertEqual(len(BINDINGS), 7)
        fake_bpy = types.SimpleNamespace(context=types.SimpleNamespace(
            window_manager=types.SimpleNamespace(keyconfigs=object())))
        with patch.dict(sys.modules, {'bpy': fake_bpy}):
            for probe, reference, count, step_count in (
                    (True, False, 6, 68), (False, False, 2, 24), (False, True, 2, 24)):
                steps, receipt = [], {'dispatch': []}
                fixture = ObjectExtendCases(steps, receipt, lambda *a, **k: None,
                                            None, None, None, binding, probe=probe,
                                            reference=reference).append()
                self.assertEqual(len(steps), step_count)
                self.assertEqual(len(fixture.fixtures), count)
                self.assertEqual([f.initial_selected for f in fixture.fixtures], [True, False] * (count // 2))
                self.assertEqual([f.probe for f in fixture.fixtures],
                                 [False, False, True, True, False, False] if probe else [False, False])
                self.assertTrue(all(f.binding == binding for f in fixture.fixtures))
                self.assertTrue(all(f.defer_preservation_failure == reference for f in fixture.fixtures))

    def test_extend_reference_defers_only_snapshot_failure_after_owned_cleanup(self):
        from blender_keymap_category03_handlers import ObjectExtendTrial, ObjectSubtractCases
        fixture = ObjectExtendTrial.__new__(ObjectExtendTrial)
        for fault in (None, 'allocation', 'class', 'cleanup_error', 'not_reference', 'other_assertion'):
            fixture.defer_preservation_failure = fault != 'not_reference'
            fixture.allocations = [object()] if fault == 'allocation' else []
            fixture.created_maps = []
            fixture.control_class = object() if fault == 'class' else None
            fixture.initial_maps = {'captured': True}
            fixture.proof = {'cleanup_errors': ['failure'] if fault == 'cleanup_error' else [],
                             'exact_source_and_merged_preservation': fault == 'other_assertion'}
            with self.subTest(fault=fault), patch.object(
                    ObjectSubtractCases, 'cleanup', side_effect=AssertionError('retained failure')):
                if fault is None:
                    fixture.cleanup()
                    self.assertIsNone(fixture.initial_maps)
                    self.assertTrue(fixture.proof['strict_preservation_failure_deferred'])
                    self.assertFalse(fixture.proof['exact_source_and_merged_preservation'])
                else:
                    with self.assertRaises(AssertionError):
                        fixture.cleanup()

    def test_extend_reference_still_fails_after_a_deferred_strict_mismatch(self):
        from blender_keymap_category03_handlers import ObjectExtendCases
        fixture = ObjectExtendCases.__new__(ObjectExtendCases)
        fixture.closed, fixture.fixtures = False, []
        fixture.baseline = {'unchanged': True}
        fixture.proof = {'trials': [{'preservation': {'exact_source_and_merged_preservation': False}}]}
        fixture.inspector = types.SimpleNamespace(configs=types.SimpleNamespace(update=Mock()),
                                                  maps=Mock(return_value=fixture.baseline))
        fixture.record = Mock()
        with self.assertRaises(AssertionError):
            fixture.cleanup()
        self.assertTrue(fixture.proof['exact_final_preservation'])
        self.assertFalse(fixture.proof['strict_trial_preservation'])
        self.assertTrue(fixture.closed)
        fixture.cleanup()

    def test_extend_controls_require_active_state_and_positive_add_without_bystander_loss(self):
        from blender_keymap_category03_handlers import ObjectExtendTrial
        initial = {'target_selected': True, 'target_active': True,
                   'bystander_selected': True, 'bystander_visible': True}
        ObjectExtendTrial.assert_initial_state(initial, True)
        with self.assertRaises(AssertionError):
            ObjectExtendTrial.assert_initial_state({**initial, 'target_active': False}, True)
        control = {'result': ['FINISHED', 'PASS_THROUGH']}
        after = {'target_selected': True, 'target_active': True, 'bystander_selected': True}
        ObjectExtendTrial.assert_positive_control(control, after)
        for key in after:
            with self.subTest(missing_effect=key), self.assertRaises(AssertionError):
                ObjectExtendTrial.assert_positive_control(control, {**after, key: False})
        for result in (['PASS_THROUGH'], ['FINISHED', 'CANCELLED'], ['RUNNING_MODAL']):
            with self.subTest(result=result), self.assertRaises(AssertionError):
                ObjectExtendTrial.assert_positive_control({'result': result}, after)

    def test_subtraction_production_rejects_selecting_an_unselected_target(self):
        from blender_keymap_category03_handlers import ObjectSubtractProductionCases
        for initial, final, enabled, accepted in (
                (True, False, True, True), (False, False, True, True),
                (False, True, True, False), (True, True, True, False),
                (False, True, False, True), (True, False, False, True)):
            with self.subTest(initial=initial, final=final, enabled=enabled):
                result = {'phases': [
                    {'phase': 'before_press', 'snapshot': {'target_selected': initial}},
                    {'phase': 'after_release', 'snapshot': {'target_selected': final}}],
                    'direct_control': {'positive_subtraction': True}}
                if accepted:
                    ObjectSubtractProductionCases.assert_trial_effect(result, initial, enabled)
                else:
                    with self.assertRaises(AssertionError):
                        ObjectSubtractProductionCases.assert_trial_effect(result, initial, enabled)

    def test_subtraction_control_accepts_finished_passthrough_only_with_effect(self):
        from blender_keymap_category03_handlers import ObjectSubtractCases
        fixture = ObjectSubtractCases.__new__(ObjectSubtractCases)
        for result, selected, accepted in (
                (['FINISHED'], False, True),
                (['FINISHED', 'PASS_THROUGH'], False, True),
                (['FINISHED', 'PASS_THROUGH'], True, False),
                (['PASS_THROUGH'], False, False),
                (['CANCELLED'], False, False),
                (['FINISHED', 'RUNNING_MODAL'], False, False),
                (['FINISHED', 'INTERFACE'], False, False)):
            with self.subTest(result=result, selected=selected):
                fixture.result = {'direct_control': {'result': result}}
                fixture.snapshot = lambda phase: {'target_selected': selected}
                if accepted:
                    fixture.verify_direct_control()
                else:
                    with self.assertRaises(AssertionError):
                        fixture.verify_direct_control()

    def fixture(self):
        from blender_keymap_category03_modal import ModalSwitchCases
        from blender_keymap_category03_modal_probe import ModalAliasProbeCases
        from runtime_keymap_fakes import FakeItem, FakeMap
        ledger = {row['row_id']: row['binding'] for row in
                  read_jsonl(BASELINE / 'reconciliation-ledger.jsonl')}
        common = types.SimpleNamespace(
            steps=[], receipt={'dispatch': []}, record=Mock(), bpy=None,
            bindings={key: ledger[key] for key in ModalAliasProbeCases.E_IDS},
            configs=types.SimpleNamespace(update=Mock()))
        probe = ModalAliasProbeCases(common, ModalSwitchCases,
                                     BASELINE / 'reconciliation-ledger.jsonl')
        km = FakeMap('Transform Modal Map', 'EMPTY', 'WINDOW', True)
        templates = {token: km.keymap_items.append_fixture(
            FakeItem(modal_value=token, **binding['event']))
            for token, binding in probe.templates.items()}
        probe.native_map, probe.map_pointer = km, km.as_pointer()
        probe.modal_map = Mock(return_value=km)
        probe.preflight = Mock(return_value=templates)
        probe.validate_install = Mock()

        def snapshots():
            return [{'id': item.id, 'pointer': item.as_pointer(), 'token': item.propvalue,
                     'event': {field: getattr(item, field) for field in probe.expected['ROTATE']['event']},
                     'active': item.active, 'properties': dict(item.properties)}
                    for item in km.keymap_items]

        probe.witness.maps = snapshots
        probe.baseline = snapshots()
        return probe, templates

    def test_modal_probe_copies_repeat_and_type_without_changing_R(self):
        probe, templates = self.fixture()
        for token in reversed(probe.TOKENS):
            probe.copy(templates[token], token)
        copies = probe.witness.maps()[:2]
        self.assertEqual([row['token'] for row in copies], ['ROTATE', 'TRACKBALL'])
        for row in copies:
            self.assertEqual(row['event']['type'], 'E')
            self.assertTrue(row['event']['repeat'])
        self.assertEqual(probe.witness.maps()[2:], probe.baseline)
        probe.remove_owned()
        self.assertEqual(probe.witness.maps(), probe.baseline)

    def test_modal_probe_readback_rejects_missing_repeat(self):
        probe, _ = self.fixture()
        for token, expected in probe.expected.items():
            self.assertTrue(probe.binding_matches(expected, expected))
            wrong = copy.deepcopy(expected)
            wrong['event']['repeat'] = False
            self.assertFalse(probe.binding_matches(wrong, expected))
            self.assertFalse(probe.templates[token]['event']['repeat'])

    def test_modal_probe_partial_install_rolls_back_exactly(self):
        probe, _ = self.fixture()
        probe.partial_install_control()
        self.assertTrue(probe.proof['partial_install_rollback_passed'])
        self.assertEqual(probe.owned, [])
        self.assertEqual(probe.witness.maps(), probe.baseline)
        self.assertEqual([row['token'] for row in probe.proof['generations']], ['TRACKBALL'])
        probe.validate_install.assert_not_called()

    def test_modal_probe_native_allocation_and_repeat_setter_failures_unwind(self):
        from runtime_keymap_fakes import FakeItem

        class RejectRepeatItem(FakeItem):
            def __setattr__(self, name, value):
                if name == 'repeat' and value is True:
                    raise RuntimeError('injected repeat setter failure')
                super().__setattr__(name, value)

        for failure in ('after_native_allocation', 'repeat_setter'):
            with self.subTest(failure=failure):
                probe, _ = self.fixture()
                items = probe.native_map.keymap_items
                original = items.new_from_item

                def create(*args, **kwargs):
                    item = original(*args, **kwargs)
                    if failure == 'after_native_allocation':
                        raise RuntimeError('injected after native allocation')
                    item.__class__ = RejectRepeatItem
                    return item

                with patch.object(items, 'new_from_item', side_effect=create):
                    with self.assertRaises(RuntimeError):
                        probe.install()
                self.assertEqual(probe.owned, [])
                self.assertEqual(probe.witness.maps(), probe.baseline)
                self.assertTrue(probe.proof['checkpoints'][-1]['exact'])
                probe.validate_install.assert_not_called()

        probe, _ = self.fixture()
        probe.validate_install.side_effect = AssertionError('injected merged readback failure')
        with self.assertRaises(AssertionError):
            probe.install()
        self.assertEqual(len(probe.proof['generations']), 2)
        self.assertEqual(probe.owned, [])
        self.assertEqual(probe.witness.maps(), probe.baseline)

    def test_modal_probe_refuses_reused_address_with_different_id(self):
        from runtime_keymap_fakes import FakeItem
        probe, templates = self.fixture()
        probe.copy(templates['ROTATE'], 'ROTATE')
        owned = probe.owned[0]
        original = probe.live_owned(owned)
        probe.native_map.keymap_items.remove(original)
        foreign = FakeItem(modal_value='ROTATE', type='E', repeat=True)
        foreign._pointer = owned['pointer']
        probe.native_map.keymap_items.append_fixture(foreign)
        with self.assertRaises(AssertionError):
            probe.remove_owned()
        self.assertIn(foreign, list(probe.native_map.keymap_items))
        self.assertEqual(probe.owned, [owned])
        self.assertTrue(probe.proof['removal_errors'])


class Category03NativeReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = read_json(CATEGORY / 'manifest.json')
        cls.verification = cls.manifest['native_verification']
        cls.native = unpack_native(read_json(CATEGORY / cls.verification['fixture']))
        cls.runs = {run['id']: run for run in cls.native['runs']}
        cls.reference_runs = {run['id']: run for run in cls.native['reference_runs']}

    def test_uv_extend_production_matches_addition_under_actual_runtime_identity(self):
        route = self.manifest['uv_extend_route']
        run = self.runs['uv_extend_production-1794574142641917000']
        self.assertEqual(run['native_status'], 'complete')
        for path, expected in route['source_sha256'].items():
            self.assertEqual(run['source_sha256'][path], expected)
        proof = run['uv_extend_production']
        self.assertFalse(proof['direct_candidate_injection'])
        self.assertFalse(proof['shared_runtime_capability_changes'])
        cell, = proof['cells']
        self.assertEqual(cell['ledger_id'], route['row_id'])
        self.assertTrue(cell['production_additive_effects'])
        self.assertTrue(cell['exact_cell_preservation'])
        self.assertTrue(cell['direct_control']['positive_addition'])
        self.assertEqual(len(cell['trials']), 2)
        for trial, initial in zip(cell['trials'], (True, False)):
            phases = {p['phase']: p['snapshot'] for p in trial['phases']}
            self.assertEqual(phases['after_press']['target_selected'], initial)
            self.assertTrue(phases['after_release']['target_selected'])
            self.assertTrue(phases['after_release']['bystander_selected'])
            self.assertTrue(trial['input_delivery']['delivered'])
            self.assertTrue(trial['exact_map_event_witnessed'])
            self.assertTrue(trial['expected_selection_observed'])
            self.assertTrue(trial['geometry_and_tool_unchanged'])
            self.assertEqual(trial['witness_order'], {'indices': [0], 'competing_indices': [1, 27]})
            self.assertEqual(trial['exact_candidate_counts'], {
                role: {route['row_id']: count}
                for role, count in (('default', 0), ('active', 0), ('addon', 1), ('user', 1))})
        install, = proof['installs']
        self.assertEqual(install['owner_id'],
                         'legacy:Selection:de1a2030dc8d4baa0792cff32127ec7f6c081ec3d3dfa7bf5e7764c26a191a80')
        self.assertEqual(install['request_id'], '0:UV Editor:LEFTMOUSE:CLICK')
        self.assertTrue(install['runtime_owned_valid'])
        self.assertEqual(install['registered_pair_matches'], 1)
        self.assertEqual(len(proof['releases']), 2)
        self.assertTrue(all(release['accepted_preservation'] for release in proof['releases']))
        self.assertTrue(proof['exact_source_and_merged_preservation'])
        self.assertEqual(proof['combined_cleanup_errors'], [])
        self.assertEqual(proof['cleanup_errors'], [])
        for key in ('owned', 'pending_cleanup', 'tracked_resources'):
            self.assertEqual(run['cleanup'][key], 0)
        self.assertTrue(run['watcher_stopped'])
        self.assertTrue(run['protected_unchanged'])
        self.assertEqual(run['remaining_owned_resources'], [])
        self.assertEqual(self.native['candidate_accounting'], self.manifest['candidate_accounting'])
        self.assertFalse(route['acceptance']['PRESS_rows_accepted'])

    def test_uv_extend_reference_effects_match_but_final_strict_failure_remains(self):
        run = self.reference_runs['reference-evidence-1794573067246147000']
        native = run['observations']
        self.assertEqual(native['status'], 'error')
        proof = native['uv_extend_proof']
        cell, = proof['cells']
        self.assertTrue(cell['reference_additive_effects'])
        self.assertTrue(cell['exact_cell_preservation'])
        self.assertFalse(proof['exact_source_and_merged_preservation'])
        self.assertFalse(proof['cleanup_errors'])
        for trial, initial in zip(cell['trials'], (True, False)):
            phases = {p['phase']: p['snapshot'] for p in trial['phases']}
            self.assertEqual(phases['after_press']['target_selected'], initial)
            self.assertTrue(phases['after_release']['target_selected'])
            self.assertTrue(phases['after_release']['bystander_selected'])
            self.assertTrue(trial['exact_map_event_witnessed'])
            self.assertTrue(trial['expected_selection_observed'])
            self.assertEqual(trial['projected_point'], [1978, 1126])
        before, after = proof['maps_before_without_controls'], proof['maps_after_without_control']
        changes = Counter()
        removed = []
        for role in before:
            self.assertEqual([m['scope'] for m in before[role]], [m['scope'] for m in after[role]])
            for left, right in zip(before[role], after[role]):
                old = {r['blender_id']: r for r in left['items']}
                new = {r['blender_id']: r for r in right['items']}
                self.assertLessEqual(new.keys(), old.keys())
                removed.extend((role, left['scope']['name'], old[i]['target']) for i in old.keys() - new.keys())
                for i in old.keys() & new.keys():
                    fields = {key for key in old[i] if old[i][key] != new[i][key]}
                    self.assertLessEqual(fields, {'read_issues'})
                    changes[role] += bool(fields)
        self.assertEqual(changes, {'default': 0, 'active': 226, 'addon': 1, 'user': 173})
        self.assertEqual(Counter(removed), {('user', 'UV Editor', 'uv.toolkit_center_cursor_and_frame_all'): 45,
                                           ('user', 'UV Editor', 'uv.toolkit_distribute'): 1})
        self.assertTrue(run['protected_unchanged'])
        self.assertFalse(run['cleanup']['remaining_resources'])

    def test_uv_extend_corrected_click_matches_addition_with_verified_stock_reuse(self):
        run = self.runs['uv_extend_probe-1794572360320071000']
        self.assertEqual(run['native_status'], 'complete')
        proof = run['uv_extend_proof']
        self.assertEqual(proof['stock_click_reuse']['run'], 'uv_extend_probe-1794571757033229000')
        self.assertEqual(proof['stock_click_reuse']['input_sha256'],
                         'ad20dd8fe6eb010f0597f1df0126bd8f7b8fa5318b13709525fe1fe7a89b3fe4')
        cell = proof['cells'][0]
        self.assertEqual(len(cell['reused_stock_trials']), 2)
        self.assertEqual(len(cell['trials']), 2)
        self.assertTrue(cell['matched_stock_probe_effects'])
        for trial, initial in zip(cell['trials'], (True, False)):
            phases = {p['phase']: p['snapshot'] for p in trial['phases']}
            self.assertEqual(phases['after_press']['target_selected'], initial)
            self.assertTrue(phases['after_release']['target_selected'])
            self.assertTrue(phases['after_release']['bystander_selected'])
            self.assertTrue(trial['exact_map_event_witnessed'])
            self.assertTrue(trial['expected_selection_observed'])
            self.assertEqual(trial['witness_order'], {'indices': [0], 'competing_indices': [1, 27]})
        self.assertTrue(proof['exact_source_and_merged_preservation'])
        self.assertTrue(run['protected_unchanged'])
        self.assertTrue(run['watcher_stopped'])
        self.assertFalse(run['remaining_owned_resources'])
        self.assertFalse(run['cleanup']['owned'])

    def test_uv_extend_tool_press_admission_does_not_hide_nonadditive_effects(self):
        run = self.runs['uv_extend_probe-1794572360320071000']
        for cell in run['uv_extend_proof']['cells'][1:]:
            self.assertEqual(cell['event'], 'PRESS')
            self.assertTrue(cell['direct_control']['positive_addition'])
            self.assertIsNone(cell['tool_readback']['keymap'])
            self.assertIsNone(cell['tool_readback']['keymap_fallback'])
            self.assertFalse(cell['matched_stock_probe_effects'])
            self.assertTrue(cell['exact_cell_preservation'])
            self.assertEqual(len(cell['trials']), 4)
            for trial in cell['trials']:
                phases = {p['phase']: p['snapshot'] for p in trial['phases']}
                expected = False if trial['probe'] else not trial['initial_selected']
                self.assertEqual(phases['after_press']['target_selected'], expected)
                self.assertEqual(phases['after_release']['target_selected'], expected)
                self.assertTrue(phases['after_release']['bystander_selected'])
                self.assertTrue(trial['exact_map_event_witnessed'])
                self.assertTrue(trial['geometry_and_tool_unchanged'])
                self.assertTrue(trial['input_delivery']['delivered'])
                self.assertEqual(trial['expected_selection_observed'], not trial['probe'])

    def test_uv_extend_stock_click_controls_and_pre_input_failure_are_retained(self):
        run = self.runs['uv_extend_probe-1794571757033229000']
        self.assertEqual(run['native_status'], 'error')
        self.assertIn('Witness is not ahead of competing rows', run['error'])
        proof = run['uv_extend_proof']
        cell, = proof['cells']
        self.assertTrue(cell['direct_control']['positive_addition'])
        self.assertEqual(cell['direct_control']['result'], ['FINISHED', 'PASS_THROUGH'])
        self.assertEqual(len(cell['trials']), 3)
        for trial, initial in zip(cell['trials'][:2], (True, False)):
            phases = {p['phase']: p['snapshot'] for p in trial['phases']}
            self.assertFalse(trial['probe'])
            self.assertTrue(trial['exact_map_event_witnessed'])
            self.assertTrue(trial['expected_selection_observed'])
            self.assertEqual(phases['after_press']['target_selected'], initial)
            self.assertEqual(phases['after_release']['target_selected'], not initial)
            self.assertTrue(phases['after_release']['bystander_selected'])
        candidate = cell['trials'][2]
        self.assertTrue(candidate['probe'])
        self.assertEqual([p['phase'] for p in candidate['phases']], ['before_press'])
        self.assertNotIn('native_maps', candidate)
        self.assertNotIn('witness_order', candidate)
        self.assertTrue(proof['exact_source_and_merged_preservation'])
        self.assertFalse(proof['cleanup_errors'])
        self.assertTrue(run['watcher_stopped'])
        self.assertFalse(run['cleanup']['owned'])
        self.assertFalse(run['remaining_owned_resources'])
        self.assertTrue(run['protected_unchanged'])

    def test_extend_actual_production_identity_effects_and_releases(self):
        route = self.manifest['object_extend_route']
        run = self.runs[route['native_result']['run']]
        self.assertEqual(run['native_status'], 'complete')
        for path, expected in route['source_sha256'].items():
            self.assertEqual(run['source_sha256'][path], expected)
        proof = run['extend_production']
        self.assertFalse(proof['direct_candidate_injection'])
        self.assertEqual(len(proof['trials']), 2)
        for trial, selected in zip(proof['trials'], (True, False)):
            self.assertTrue(trial['group_enabled'])
            result = trial['result']
            phases = {p['phase']: p['snapshot'] for p in result['phases']}
            self.assertEqual(phases['before_press']['target_selected'], selected)
            self.assertEqual(phases['before_press']['target_active'], selected)
            after = phases['after_release']
            self.assertTrue(after['target_selected'] and after['target_active'] and after['bystander_selected'])
            self.assertTrue(result['input_delivery']['delivered'])
            self.assertTrue(result['direct_control']['positive_addition'])
            self.assertEqual(result['direct_control']['point'], result['projected_point'])
            self.assertTrue(trial['preservation']['exact_source_and_merged_preservation'])
            self.assertEqual(trial['preservation']['exact_candidate_counts'], {
                'default': 0, 'active': 0, 'addon': 1, 'user': 1})
        self.assertEqual(len(proof['installs']), 2)
        self.assertEqual(len({x['owner_id'] for x in proof['installs']}), 1)
        for install in proof['installs']:
            self.assertTrue(install['owner_id'].startswith('legacy:Selection:'))
            self.assertEqual(install['request_id'], '0:3D View:LEFTMOUSE:CLICK')
            self.assertTrue(install['runtime_owned_valid'])
            self.assertEqual(install['registered_pair_matches'], 1)
        self.assertEqual(len(proof['releases']), 3)
        self.assertTrue(all(x['accepted_preservation'] for x in proof['releases']))
        self.assertEqual(proof['cleanup_errors'], [])
        for key in ('owned', 'pending_cleanup', 'tracked_resources'):
            self.assertEqual(run['cleanup'][key], 0)
        self.assertTrue(run['watcher_stopped'])
        self.assertEqual(run['remaining_owned_resources'], [])

    def test_extend_reference_matches_effects_but_retains_strict_trial_failures(self):
        run = self.reference_runs['reference-evidence-1794569668793426000']
        native = run['observations']
        self.assertEqual(native['status'], 'error')
        proof = native['extend_proof']
        self.assertTrue(proof['reference'])
        self.assertEqual(len(proof['trials']), 2)
        for trial, selected in zip(proof['trials'], (True, False)):
            result = trial['result']
            phases = {p['phase']: p['snapshot'] for p in result['phases']}
            self.assertEqual(phases['before_press']['target_selected'], selected)
            self.assertEqual(phases['before_press']['target_active'], selected)
            after = phases['after_release']
            self.assertTrue(after['target_selected'] and after['target_active'] and after['bystander_selected'])
            self.assertTrue(result['input_delivery']['delivered'])
            self.assertTrue(result['direct_control']['positive_addition'])
            self.assertEqual(result['direct_control']['point'], result['projected_point'])
            preservation = trial['preservation']
            self.assertEqual(preservation['exact_candidate_counts'], {
                'default': 0, 'active': 1, 'addon': 0, 'user': 1})
            self.assertFalse(preservation['exact_source_and_merged_preservation'])
            self.assertTrue(preservation['strict_preservation_failure_deferred'])
            self.assertEqual(preservation['cleanup_errors'], [])
        self.assertFalse(proof['strict_trial_preservation'])
        self.assertTrue(proof['exact_final_preservation'])
        self.assertEqual(proof['maps_before'], proof['maps_after'])
        self.assertEqual(run['cleanup']['remaining_resources'], [])
        self.assertEqual(run['cleanup']['retention_errors'], [])

    def test_extend_probe_changes_selected_active_without_losing_bystander(self):
        evidence = self.manifest['selection_extend_probe']
        run = self.runs[evidence['run']]
        self.assertEqual(run['native_status'], 'complete')
        self.assertEqual(run['handler_fixture_sha256'], evidence['fixture_sha256'])
        proof = run['extend_proof']
        self.assertFalse(proof['production_capability_enabled'])
        self.assertEqual(len(proof['trials']), 6)
        for trial, initial, final in zip(proof['trials'], [True, False] * 3,
                                         [False, True, True, True, False, True]):
            result = trial['result']
            phases = {p['phase']: p['snapshot'] for p in result['phases']}
            self.assertEqual(phases['before_press']['target_selected'], initial)
            self.assertEqual(phases['before_press']['target_active'], initial)
            after = phases['after_release']
            self.assertEqual(after['target_selected'], final)
            self.assertTrue(after['target_active'] and after['bystander_selected'])
            self.assertTrue(result['input_delivery']['delivered'])
            self.assertIn({'area': 'VIEW_3D', 'region': 'WINDOW',
                           'point': result['projected_point'],
                           'modifiers': {'shift': True, 'oskey': True, 'ctrl': False, 'alt': False}},
                          result['input_delivery']['callbacks'])
            self.assertEqual(result['direct_control']['point'], result['projected_point'])
            self.assertTrue(result['direct_control']['positive_addition'])
            preservation = trial['preservation']
            self.assertTrue(preservation['exact_source_and_merged_preservation'])
            self.assertEqual(preservation['exact_candidate_counts'], {
                'default': 0, 'active': 0, 'addon': int(trial['probe']), 'user': int(trial['probe'])})
        self.assertTrue(proof['stock_behavior_restored'] and proof['exact_final_preservation'])
        self.assertEqual(proof['cleanup_errors'], [])
        for key in ('owned', 'pending_cleanup', 'tracked_resources'):
            self.assertEqual(run['cleanup'][key], 0)
        self.assertTrue(run['watcher_stopped'])
        self.assertEqual(run['remaining_owned_resources'], [])

    def test_subtract_production_selected_unselected_stock_on_off_and_cleanup(self):
        route = self.manifest['object_subtract_route']
        run = self.runs[route['acceptance']['production_run']]
        self.assertEqual(run['native_status'], 'complete')
        for path, expected in route['source_sha256'].items():
            self.assertEqual(run['source_sha256'][path], expected)
        proof = run['subtract_production']
        self.assertFalse(proof['direct_candidate_injection'])
        self.assertEqual(len(proof['trials']), 6)
        for trial, initial, enabled, final in zip(
                proof['trials'], [True, False] * 3,
                [False, False, True, True, False, False],
                [True, True, False, False, True, True]):
            self.assertEqual((trial['initial_selected'], trial['group_enabled']), (initial, enabled))
            result = trial['result']
            phases = {p['phase']: p['snapshot']['target_selected'] for p in result['phases']}
            self.assertEqual(phases, {'before_press': initial, 'after_press': initial,
                                     'after_release': final, 'direct_reset': True, 'after_direct': False})
            self.assertTrue(result['input_delivery']['delivered'])
            self.assertEqual(result['direct_control']['point'], result['projected_point'])
            self.assertTrue(result['direct_control']['positive_subtraction'])
            self.assertTrue(trial['preservation']['exact_source_and_merged_preservation'])
        self.assertEqual(len(proof['installs']), 2)
        self.assertEqual(len({i['owner_id'] for i in proof['installs']}), 1)
        for install in proof['installs']:
            self.assertTrue(install['owner_id'].startswith('legacy:Selection:'))
            self.assertEqual(install['request_id'], '0:3D View:LEFTMOUSE:CLICK')
            self.assertTrue(install['runtime_owned_valid'])
            self.assertEqual(install['registered_pair_matches'], 1)
        self.assertEqual(len(proof['releases']), 3)
        self.assertTrue(all(r['accepted_preservation'] for r in proof['releases']))
        self.assertEqual(proof['cleanup_errors'], [])
        for key in ('owned', 'pending_cleanup', 'tracked_resources'):
            self.assertEqual(run['cleanup'][key], 0)
        self.assertTrue(run['watcher_stopped'])
        self.assertEqual(run['remaining_owned_resources'], [])

    def test_partial_native_receipt_keeps_cleanup_and_scoped_proof(self):
        manifest, verification, native = self.manifest, self.verification, self.native
        self.assertEqual(native['status'], 'partial-native-evidence')
        self.assertEqual(verification['status'], native['status'])
        self.assertTrue(native['open_checks'])

        runs = self.runs
        self.assertEqual(len(runs), len(native['runs']))
        protected_inputs = {
            'packaged_preset', 'packaged_preferences', 'reference_preset', 'reference_preferences',
        }
        exited = [run for run in runs.values() if run['child_exited']]
        self.assertTrue(exited)
        self.assertTrue(any(run['returncode'] or run['native_status'] != 'complete'
                            for run in exited))
        resource_groups = {'resources', 'config', 'scripts', 'extensions', 'datafiles',
                           'tmp', 'cache'}
        for run in exited:
            with self.subTest(run_id=run['id']):
                self.assertEqual(set(run['protected_before']), protected_inputs)
                self.assertEqual(run['protected_before'], run['protected_after'])
                self.assertTrue(run['protected_unchanged'])
                for digest in run['protected_before'].values():
                    self.assertRegex(digest, r'^[0-9a-f]{64}$')
                self.assertEqual(run['remaining_owned_resources'], [])
                self.assertLessEqual(resource_groups, set(run['removed_resources']))
                if run['native_status'] == 'complete':
                    self.assertEqual(run['returncode'], 0)
                    self.assertTrue(run['watcher_stopped'])
                if 'cleanup' in run:
                    for counter in ('features', 'owned', 'retained_edited', 'pending_cleanup',
                                    'tracked_resources'):
                        self.assertEqual(run['cleanup'][counter], 0, counter)
        for run in native['reference_runs']:
            with self.subTest(run_id=run['id']):
                self.assertTrue(run['child_exited'])
                self.assertEqual(set(run['protected_before']), protected_inputs)
                self.assertEqual(run['protected_before'], run['protected_after'])
                self.assertTrue(run['protected_unchanged'])
                cleanup = run['cleanup']
                removed = {entry['resource'] if isinstance(entry, dict) else entry
                           for entry in cleanup['removed_resources']}
                self.assertLessEqual(resource_groups | {'redirected'},
                                     removed)
                self.assertEqual(cleanup['remaining_resources'], [])

        schema_proofs = [
            run for run in exited
            if run['mode'] == 'schema' and run['native_status'] == 'complete'
            and run.get('schema_assignments')
        ]
        self.assertTrue(schema_proofs)
        for run in schema_proofs:
            with self.subTest(run_id=run['id']):
                assignments = [case for case in run['schema_assignments'] if 'declared' in case]
                self.assertCountEqual([case['operator'] for case in assignments], [
                    'transform.translate', 'transform.rotate', 'transform.resize',
                    'image.view_pan', 'clip.view_pan',
                ])
                for case in assignments:
                    self.assertTrue(case['released'])
                    self.assertTrue(case['merged_readback_matches'])
                    self.assertTrue(case['foreign_default_unchanged'])
                    for key, value in case['declared'].items():
                        self.assertEqual(case['complete_readback'][key], value)
                self.assertEqual({
                    case['operator']: case['edited_source_retained_then_removed_by_fixture']
                    for case in assignments if 'edited_source_retained_then_removed_by_fixture' in case
                }, {'transform.translate': 'snap_elements', 'image.view_pan': 'offset'})

        gizmo = manifest['reviewed_existing_declarations']['transform_tools_gizmo']
        evidence = gizmo['post_correction_native_evidence']
        self.assertEqual(evidence['fixture'], verification['fixture'])
        self.assertEqual(evidence['context'], 'Object Mode')
        run = runs[evidence['run_id']]
        self.assertEqual(run['mode'], 'transform')
        self.assertEqual(run['native_status'], 'complete')
        cases = {case['case']: case for case in run['dispatch']}
        expected_tools = {'W': 'builtin.move', 'E': 'builtin.rotate', 'R': 'builtin.scale'}
        dispatch = [cases[name] for name in evidence['dispatch_cases']]
        self.assertCountEqual([case['key'] for case in dispatch], expected_tools.keys())
        for case in dispatch:
            self.assertTrue(case['shift'])
            self.assertEqual(case['before']['tool'], 'builtin.select_box')
            self.assertEqual(case['after']['tool'], expected_tools[case['key']])

    def test_q_production_receipt_confirms_wrapper_and_tool_across_lifecycle(self):
        group = self.manifest['reviewed_existing_declarations']['selection_tool_switch']
        production = group['native_production_evidence']
        run = self.runs[production['run_id']]
        probe = group['native_press_probe']
        self.assertEqual(production['fixture'], self.verification['fixture'])
        self.assertEqual(probe['fixture'], self.verification['fixture'])
        self.assertEqual(run['mode'], 'q_modes')
        self.assertEqual(run['source_sha256'][group['source']], production['source_sha256'])
        modes = ('object', 'mesh', 'curve', 'curves')
        phases = ('absent', 'enabled', 'preference_off', 'disabled', 'reenabled')
        expected_cases = [(mode, phase) for phase in phases for mode in modes]
        for receipt, probe_count in ((self.runs[probe['run_id']], 4), (run, 0)):
            self.assertEqual(receipt['native_status'], 'complete')
            cases = {case['case']: case for case in receipt['dispatch']}
            self.assertCountEqual([case['case'] for case in receipt['dispatch']],
                                  [f'q_{mode}_{phase}' for mode, phase in expected_cases])
            for mode, phase in expected_cases:
                case = cases[f'q_{mode}_{phase}']
                with self.subTest(run_id=receipt['id'], case=case['case']):
                    self.assertEqual(case['kind'], mode)
                    self.assertEqual(case['before_tool'], 'builtin.move')
                    self.assertEqual(case['probe_owned_before_input'], probe_count)
                    self.assertEqual(case['wrapper_calls'], [{
                        'operator': f'wm.bh_tool_select_box_xray_{mode}', 'result': ['FINISHED'],
                    }])
                    expected_tool = 'builtin.select_box'
                    if mode in ('object', 'mesh') and phase in ('enabled', 'reenabled'):
                        expected_tool = f'{mode}_tool.select_box_xray'
                    self.assertEqual(case['after_tool'], expected_tool)

    def test_box_selection_receipt_keeps_failed_drags_and_confirms_corrected_fixture(self):
        group = self.manifest['reviewed_existing_declarations']['selection_tool_switch']
        evidence = group['native_box_selection_evidence']
        for run_id, after_count in ((evidence['earlier_attempt_run_id'], 0),
                                    (evidence['run_id'], 1)):
            run = self.runs[run_id]
            self.assertEqual((run['mode'], run['native_status']), ('q_tools', 'complete'))
            cases = {case['case']: case for case in run['dispatch']}
            self.assertEqual(len(cases), 4)
            for mode in ('object', 'mesh'):
                for provider in ('provider', 'builtin'):
                    case = cases[f'box_tool_{mode}_{provider}']
                    with self.subTest(run_id=run_id, case=case['case']):
                        self.assertTrue(case['activation_method'].startswith(
                            'direct wrapper invocation'))
                        self.assertEqual(case['activation_result'], ['FINISHED'])
                        self.assertEqual(case['selection_method'],
                                         'native left-button drag through active tool')
                        self.assertEqual((len(case['before']), len(case['after'])), (0, after_count))
                        callbacks = {entry['operator']: entry['result']
                                     for entry in case['observed_callbacks']}
                        self.assertEqual(callbacks[f'wm.bh_tool_select_box_xray_{mode}'],
                                         ['FINISHED'])
                        if provider == 'provider':
                            self.assertEqual(case['tool'], f'{mode}_tool.select_box_xray')
                            self.assertEqual(callbacks[f'{mode}.select_box_xray'], ['RUNNING_MODAL'])
                        else:
                            self.assertEqual(case['tool'], 'builtin.select_box')

    def test_uv_selection_receipt_confirms_counts_and_toggle_isolation(self):
        all_none = self.manifest['reviewed_declarations'][SELECTION_ALL_NONE]['native_evidence']
        brackets = self.manifest['reviewed_existing_declarations'][UV_BRACKETS]['native_evidence']
        self.assertEqual(all_none['run_id'], brackets['run_id'])
        run = self.runs[all_none['run_id']]
        self.assertEqual((run['mode'], run['native_status']), ('selection', 'complete'))
        cases = {case['case']: case for case in run['dispatch']}
        expected_counts = {
            'more_less_uv_RIGHT_BRACKET': 9, 'more_less_uv_LEFT_BRACKET': 1,
            'uv_select_all_ctrl': 64, 'uv_deselect_all_ctrl': 0,
            'uv_select_all_cmd': 64, 'uv_deselect_all_cmd': 0,
        }
        case_names = [*all_none['dispatch_cases'], *brackets['dispatch_cases']]
        self.assertCountEqual(case_names, expected_counts.keys())
        for name in case_names:
            with self.subTest(case=name):
                self.assertEqual(len(cases[name]['before']), 4)
                self.assertEqual(len(cases[name]['after']), expected_counts[name])
                self.assertTrue(cases[name]['changed'])
        isolation = {case['case']: case for case in run['invariants']}[all_none['isolation_case']]
        self.assertEqual(isolation['owned_bindings'], 4)
        self.assertTrue(isolation['other_groups_unchanged'])
        self.assertTrue(isolation['foreign_default_unchanged'])
        self.assertTrue(isolation['restored'])

    def test_transform_receipt_confirms_object_effects_and_active_move_gizmo(self):
        evidence = self.verification['transform_dispatch']
        run = self.runs[evidence['run_id']]
        self.assertEqual((run['mode'], run['native_status']), ('transform', 'complete'))
        cases = {case['case']: case for case in run['dispatch']}
        effects = {
            'transform_W': ('location', 'TRANSFORM_OT_translate'),
            'transform_E': ('rotation', 'TRANSFORM_OT_rotate'),
            'transform_R': ('scale', 'TRANSFORM_OT_resize'),
            'transform_W_gizmo_active': ('location', 'TRANSFORM_OT_translate'),
        }
        menu_case = 'object_context_menu_with_active_move_gizmo'
        self.assertCountEqual(evidence['object_mode_cases'], [*effects, menu_case])
        for name, (field, operator) in effects.items():
            with self.subTest(case=name):
                case = cases[name]
                self.assertFalse(case['shift'])
                self.assertIn(operator, case['operator_history'])
                self.assertNotEqual(case['before'][field], case['after'][field])
                self.assertEqual(case['during'][field], case['after'][field])
        move = cases['transform_W_gizmo_active']
        self.assertEqual(move['before']['tool'], 'builtin.move')
        self.assertEqual(move['after']['tool'], 'builtin.move')
        self.assertEqual(cases[menu_case]['tool'], 'builtin.move')
        self.assertGreater(cases[menu_case]['menu_draws'], 0)
        face = cases[evidence['mesh_edit_mode_case']]
        self.assertEqual(face['before_tool'], 'builtin.move')
        self.assertEqual(face['tool'], 'builtin.move')
        self.assertEqual(face['target_face'], 0)
        self.assertNotIn(face['target_face'], face['before'])
        self.assertEqual(face['after'], [face['target_face']])

    def test_selection_wheel_receipt_distinguishes_shortcuts_from_direct_controls(self):
        evidence = self.verification['selection_wheel_controls']
        run = self.runs[evidence['run_id']]
        self.assertEqual((run['mode'], run['native_status']), ('selection_failures', 'complete'))
        cases = {case['case']: case for case in run['dispatch']}
        self.assertCountEqual(evidence['observed_shortcut_modes'], ['mesh', 'curve'])
        self.assertCountEqual(evidence['unchanged_selection_after_shortcut'],
                              ['dopesheet', 'graph', 'node', 'sequencer'])
        self.assertEqual(evidence['fixture_errors'], ['mask'])
        for direction in ('UP', 'DOWN'):
            for mode in evidence['observed_shortcut_modes']:
                case = cases[f'more_less_{mode}_WHEEL{direction}MOUSE']
                with self.subTest(case=case['case']):
                    self.assertTrue(case['shift'])
                    self.assertEqual(case['editor'], 'VIEW_3D')
                    self.assertTrue(case['changed'])
                    self.assertEqual(case['view_before'], [None, None])
                    self.assertEqual(case['view_after'], [None, None])
                    expected = {
                        ('mesh', 'UP'): [6, 7, 8, 11, 12, 13, 16, 17, 18],
                        ('curve', 'UP'): [1, 2, 3],
                    }
                    self.assertEqual(case['after'], expected.get((mode, direction), []))
            for mode in evidence['unchanged_selection_after_shortcut']:
                case = cases[f'more_less_{mode}_WHEEL{direction}MOUSE']
                with self.subTest(case=case['case']):
                    self.assertFalse(case['changed'])
                    self.assertEqual(case['before'], case['after'])
                    control = case['direct_control']
                    self.assertEqual(control['result'], ['FINISHED'])
                    if (mode, direction) == ('sequencer', 'DOWN'):
                        self.assertEqual(case['before'], control['after'])
                    else:
                        self.assertNotEqual(case['before'], control['after'])
            self.assertEqual(cases[f'more_less_mask_WHEEL{direction}MOUSE']['status'],
                             'fixture_error')
        self.assertIn(run['id'], self.native['sanitization']['nonfinite_values'])

    def test_uv_g_receipt_retains_invalid_controls_and_process_failures(self):
        direct_id = 'uv_g_control-1794543421357052000'
        factory_abort_id = 'uv_g_control-1794543695708576000'
        zero_effect_id = 'uv_g_control-1794543845284578000'
        reference_error_id = 'reference-evidence-1794543743806341000'
        reference_exit_id = 'reference-evidence-1794543897313830000'
        notes = self.native['failed_attempt_notes']
        self.assertLessEqual({direct_id, factory_abort_id, zero_effect_id, reference_error_id,
                              reference_exit_id}, notes.keys())

        direct = self.runs[direct_id]['dispatch'][0]['prior_rotation_control']
        self.assertEqual(direct['history_before_g'], [])
        self.assertNotEqual(direct['control_before'], direct['control_after'])
        factory_abort = self.runs[factory_abort_id]
        self.assertEqual(factory_abort['returncode'], -6)
        self.assertEqual(factory_abort['dispatch'], [])
        zero_effect = self.runs[zero_effect_id]['dispatch'][0]['prior_rotation_control']
        self.assertIn('TRANSFORM_OT_rotate', zero_effect['history_before_g'])
        self.assertEqual(zero_effect['control_before'], zero_effect['control_after'])

        reference = {run['id']: run for run in self.native['reference_runs']}
        self.assertEqual(reference[reference_error_id]['observations']['status'], 'error')
        failed_exit = reference[reference_exit_id]
        self.assertEqual(failed_exit['returncode'], -11)
        self.assertEqual(failed_exit['observations']['status'], 'complete')
        control = failed_exit['observations']['dispatch'][0]['prior_rotation_control']
        self.assertIn('TRANSFORM_OT_rotate', control['history_before_g'])
        self.assertEqual(control['control_before'], control['control_after'])

    def test_circle_production_receipt_matches_scoped_toggle_and_source(self):
        group = self.manifest['reviewed_declarations'][SELECTION_CIRCLE]
        evidence = group['native_probe_evidence']['production_verification']
        run = self.runs[evidence['run_id']]
        self.assertEqual(run['native_status'], 'complete')
        self.assertEqual(run['source_sha256'][group['source']], evidence['source_sha256'])
        proof = run['handler_proof']
        self.assertEqual(proof['stage'], 'production_circle')
        self.assertEqual(proof['owned_count'], 0)
        self.assertTrue(proof['foreign_source_fields_and_order_unchanged'])
        self.assertEqual(run['circle_toggle'], {
            'off_removed_exactly_four': True, 'unrelated_categories_unchanged': True,
            'restored_exactly': True,
        })
        counts = {
            'object_add': (0, 1), 'object_subtract': (1, 0), 'uv_add': (0, 4),
            'uv_subtract': (64, 60), 'disabled_object_add': (0, 0),
            'reenabled_object_add': (0, 1),
        }
        self.assertEqual({
            case['case'].removeprefix('production_circle_'): (
                len(case['before']['selected']), len(case['after_gesture']['selected']),
            )
            for case in run['dispatch']
        }, counts)

    def test_valid_uv_g_control_distinguishes_translation_and_repeat_rotation(self):
        evidence = self.verification['uv_g_prior_rotation']
        factory = self.runs[evidence['factory_run_id']]
        reference = self.reference_runs[evidence['reference_run_id']]
        self.assertEqual(factory['native_status'], 'complete')
        self.assertEqual(reference['returncode'], 0)
        self.assertEqual(reference['observations']['status'], 'complete')
        for observation in (factory, reference['observations']):
            self.assertTrue(observation['g_control_binding']['fixture_owned'])
            self.assertTrue(observation['g_control_binding']['removed_before_g'])
            control = observation['uv_g_control']
            self.assertIn('TRANSFORM_OT_rotate', control['history_before_g'])
            self.assertNotEqual(control['control_before'], control['control_after'])
        factory_case, = factory['dispatch']
        self.assertEqual(factory_case['after_key'], factory_case['before'])
        initial = factory_case['before']['selected_positions']
        final = factory_case['after']['selected_positions']
        self.assertEqual([row[:2] for row in initial], [row[:2] for row in final])
        translation = [tuple(round(end - start, 6) for start, end in zip(old[2:], new[2:]))
                       for old, new in zip(initial, final, strict=True)]
        self.assertEqual(len(set(translation)), 1)
        self.assertNotEqual(translation[0], (0, 0))
        reference_case, = reference['observations']['dispatch']
        rotated = reference['observations']['uv_g_control']['control_after']
        self.assertEqual(reference_case['after_key'], rotated)
        self.assertEqual(reference_case['after'], rotated)

    def test_axis_production_receipt_preserves_partial_reference_result(self):
        evidence = self.verification['ordinary_axis_dispatch']
        production = self.runs[evidence['production_run_id']]
        reference = self.reference_runs[evidence['reference_run_id']]['observations']
        draft_groups = self.manifest['ordinary_source_drafts']['groups']
        expected_ids = set()
        for group in ('navigation_viewport_axis', FRAMING):
            draft = draft_groups[group]
            self.assertEqual(production['source_sha256'][draft['source']], draft['source_sha256'])
            expected_ids.update(row_id for items in draft['actions'].values()
                                for row_id in items.values())
        self.assertEqual(production['native_status'], 'complete')
        self.assertEqual(production['ordinary_proof']['owned_created'], 0)
        self.assertTrue(production['ordinary_proof']['foreign_source_fields_and_order_unchanged'])
        self.assertEqual(reference['status'], 'error')
        self.assertIn('AssertionError', reference['ordinary_cleanup_error'])
        self.assertFalse(reference['ordinary_proof']['foreign_source_fields_and_order_unchanged'])
        for observation in (production, reference):
            self.assertCountEqual([case['ledger_id'] for case in observation['dispatch']],
                                  expected_ids)
            for case in observation['dispatch']:
                field = 'local' if case['tested_key'] == 'I' else 'rotation'
                before, after = case['before']['view'][field], case['after']['view'][field]
                with self.subTest(run=observation.get('id', 'reference'), case=case['case']):
                    self.assertTrue(case['direct_control']['poll'])
                    if observation is reference and case['tested_key'] == 'F1' and case['expected_event']['ctrl']:
                        self.assertEqual(before, after)
                    else:
                        self.assertNotEqual(before, after)
                        self.assertEqual(after, case['direct_control']['after']['view'][field])

    def test_editor_receipts_preserve_delivery_and_reference_cleanup_limits(self):
        evidence = self.verification['editor_handler_controls']
        probe = self.runs[evidence['guarded_probe_run_id']]
        reference = self.reference_runs[evidence['reference_run_id']]['observations']
        self.assertEqual(probe['native_status'], 'complete')
        self.assertEqual(reference['status'], 'error')
        probe_proof = probe['editor_handler_proof']
        ref_proof = reference['editor_handler_proof']
        self.assertTrue(probe_proof['foreign_source_fields_and_order_unchanged'])
        self.assertFalse(ref_proof['foreign_source_fields_and_order_unchanged'])
        self.assertIn('AssertionError', reference['editor_cleanup_error'])
        self.assertEqual(len(probe_proof['installations']), 2)
        self.assertEqual(len(probe_proof['releases']), 2)
        self.assertTrue(all(release['merged_probe_rows_absent']
                            and release['foreign_source_fields_and_order_unchanged']
                            for release in probe_proof['releases']))
        self.assertEqual(ref_proof['input_controls']['removed_rows'], 16)
        active_before = ref_proof['source_before']['active']
        active_after = ref_proof['source_after']['active']
        before_issues = {row['target'] for keymap in active_before for row in keymap['items']
                         if row['read_issues'].get('properties') == 'RNA_unavailable'}
        after_readable = {row['target'] for keymap in active_after for row in keymap['items']
                          if row['properties'] and not row['read_issues']}
        self.assertTrue(before_issues & after_readable)

        expected_ids = {row_id for directions in probe_proof['owner03_rows'].values()
                        for row_id in directions.values()}
        self.assertEqual(len(expected_ids), 8)
        probe_cases = [case for case in probe['dispatch'] if case['stage'] == 'installed']
        self.assertCountEqual([case['owner03_ledger_id'] for case in probe_cases], expected_ids)
        self.assertCountEqual([case['owner03_ledger_id'] for case in reference['dispatch']],
                              expected_ids)
        for case in probe_cases:
            self.assertTrue(case['probe_poll'])
            self.assertTrue(case['selection_changed'])
            self.assertFalse(case['view_changed'])
            self.assertEqual([call['target'] for call in case['callbacks']], [case['target']])
        for case in reference['dispatch']:
            self.assertEqual(case['wheel_observation'], 'observed')
            self.assertTrue(case['selection_changed'])
            self.assertFalse(case['view_changed'])
            self.assertEqual(case['input_delivery']['counts_in_expected_window_region'],
                             {'window': 1, 'editor': 1})
            self.assertEqual(case['input_delivery']['unmodified_wheel']['status'],
                             'observed_view_change')
        states = {case['stage']: case for case in probe['dispatch']
                  if case['kind'] == 'dopesheet' and case['tested_key'] == 'WHEELUPMOUSE'}
        self.assertFalse(states['after_release']['selection_changed'])
        self.assertTrue(states['reinstalled']['selection_changed'])


    def test_primed_editor_recheck_retains_strict_readability_failure(self):
        batch = self.native['batch07']
        process = self.reference_runs[batch['reference_run']]
        observation = process['observations']
        readiness = observation['editor_readiness']
        proof = observation['editor_handler_proof']
        self.assertEqual(observation['status'], 'error')
        self.assertEqual(process['returncode'], 0)
        self.assertTrue(process['protected_unchanged'])
        self.assertFalse(process['cleanup']['remaining_resources'])
        self.assertTrue(readiness['window_delivered'])
        self.assertTrue(readiness['stable_source_snapshots'])
        self.assertFalse(readiness['unreadable_relevant_targets'])
        self.assertEqual(len(proof['unknown_properties_before']), 30)
        self.assertEqual(len(proof['unknown_properties_after']), 117)
        self.assertFalse(proof['complete_property_comparison'])
        self.assertFalse(proof['foreign_source_fields_and_order_unchanged'])
        self.assertIn('AssertionError', observation['editor_cleanup_error'])
        transitions = 0
        for role, maps in proof['source_before'].items():
            after = proof['source_after'][role]
            self.assertEqual(len(maps), len(after))
            for before_map, after_map in zip(maps, after, strict=True):
                self.assertEqual({k: v for k, v in before_map.items() if k != 'items'},
                                 {k: v for k, v in after_map.items() if k != 'items'})
                self.assertEqual(len(before_map['items']), len(after_map['items']))
                for before_row, after_row in zip(before_map['items'], after_map['items'], strict=True):
                    self.assertEqual({k: v for k, v in before_row.items() if k != 'read_issues'},
                                     {k: v for k, v in after_row.items() if k != 'read_issues'})
                    if before_row['read_issues'] != after_row['read_issues']:
                        transitions += 1
                        self.assertEqual(before_row['read_issues'], {})
                        self.assertEqual(after_row['read_issues'], {'properties': 'RNA_unavailable'})
        self.assertEqual(transitions, 87)
        self.assertEqual(len(observation['dispatch']), 8)
        for case in observation['dispatch']:
            self.assertTrue(case['selection_changed'])
            self.assertFalse(case['view_changed'])
            self.assertEqual(case['input_delivery']['counts_in_expected_window_region'],
                             {'window': 1, 'editor': 1})
            self.assertEqual(case['input_delivery']['unmodified_wheel']['status'],
                             'observed_view_change')

    def test_uv_repeat_candidate_dispatch_and_exact_release(self):
        run = self.runs['uv_g_probe-1794549192779191000']
        self.assertEqual(run['native_status'], 'complete')
        proof = run['uv_repeat_probe']
        self.assertEqual(len(proof['installations']), 2)
        self.assertEqual(len(proof['releases']), 2)
        for installation in proof['installations']:
            self.assertEqual(installation['owned_count'], 1)
            assignment = installation['assignment']
            self.assertEqual(assignment['target']['idname'], 'screen.repeat_last')
            self.assertEqual(assignment['scope']['name'], 'UV Editor')
            self.assertEqual(assignment['scope']['space_type'], 'EMPTY')
            self.assertEqual(assignment['scope']['region_type'], 'WINDOW')
            self.assertEqual(assignment['event']['type'], 'G')
            self.assertEqual(assignment['event']['value'], 'PRESS')
            self.assertTrue(assignment['event']['repeat'])
        for release in proof['releases']:
            self.assertTrue(release['strict_preservation'])
            self.assertTrue(release['owned_candidate_absent'])
            self.assertEqual(release['source_and_foreign_merged_after'],
                             proof['source_and_foreign_merged_before'])
        cases = run['dispatch']
        self.assertEqual([case['expectation'] for case in cases],
                         ['empty_history', 'single_repeat', 'single_repeat', 'translate',
                          'move_tool', 'translate', 'single_repeat'])
        self.assertEqual(cases[0]['history_before_input'], [])
        self.assertFalse(cases[0]['repeat_poll_before_input'])
        self.assertEqual(cases[0]['history_after_input'], ['TRANSFORM_OT_translate'])
        for case in cases:
            if case['expectation'] == 'single_repeat':
                expected = case['prior_rotation_control']['control_after']['selected_positions']
                self.assertTrue(case['repeat_poll_before_input'])
                for phase in ('after_key', 'during', 'after'):
                    actual = case[phase]['selected_positions']
                    self.assertEqual(len(actual), len(expected))
                    for old, new in zip(expected, actual, strict=True):
                        self.assertEqual(old[:2], new[:2])
                        for x, y in zip(old[2:], new[2:], strict=True):
                            self.assertAlmostEqual(x, y, places=6)
            elif case['expectation'] == 'move_tool':
                self.assertEqual(case['after']['tool'], 'builtin.move')
                self.assertEqual(case['after']['selected_positions'], case['before']['selected_positions'])
            else:
                before = case['before']['selected_positions']
                after = case['after']['selected_positions']
                self.assertEqual(case['after_key']['selected_positions'], before)
                deltas = [tuple(round(y-x, 6) for x, y in zip(old[2:], new[2:]))
                          for old, new in zip(before, after, strict=True)]
                self.assertEqual(len(set(deltas)), 1)
                self.assertNotEqual(deltas[0], (0, 0))

    def test_uv_repeat_failed_save_retains_only_aggregate_map_difference(self):
        run = self.runs['uv_g_save-1794549373328440000']
        self.assertEqual(run['native_status'], 'error')
        self.assertIn('strict_preservation', run['error'])
        proof = run['uv_repeat_probe']
        self.assertTrue(proof['saved_edit']['immediate_save'])
        self.assertFalse(proof['saved_edit']['active'])
        self.assertEqual(proof['saved_edit']['event'], 'F20/PRESS')
        release, = proof['releases']
        self.assertTrue(release['owned_candidate_absent'])
        self.assertFalse(release['strict_preservation'])
        before, after = proof['source_and_foreign_merged_before'], release['source_and_foreign_merged_after']
        for role in ('default', 'active', 'addon'):
            self.assertEqual(before[role], after[role])
        changes = 0
        for old, new in zip(before['user'], after['user'], strict=True):
            self.assertEqual({k: v for k, v in old.items() if k != 'is_user_modified'},
                             {k: v for k, v in new.items() if k != 'is_user_modified'})
            if old['is_user_modified'] != new['is_user_modified']:
                changes += 1
                self.assertEqual(old['scope']['name'], 'UV Editor')
                self.assertEqual(len(old['items']), 105)
                self.assertFalse(old['is_user_modified'])
                self.assertTrue(new['is_user_modified'])
        self.assertEqual(changes, 1)

    def test_uv_repeat_saved_edit_reacquisition_and_fresh_reopen(self):
        writer = self.runs['uv_g_save-1794551925248438000']
        reader = self.runs['uv_g_reopen-1794552019120090000']
        saved = writer['uv_repeat_probe']['saved_edit']
        self.assertTrue(saved['immediate_save'])
        self.assertTrue(saved['owned_source_unchanged'])
        self.assertEqual(saved['owned_source_before'], saved['owned_source_after'])
        # Preserve the evidence that a held RNA wrapper was reused by save.
        self.assertEqual(saved['actual_before_save']['idname'], 'screen.repeat_last')
        self.assertNotEqual(saved['held_wrapper_after_save']['idname'], 'screen.repeat_last')
        actual = saved['reacquired_after_update']
        self.assertEqual((actual['idname'], actual['type'], actual['value']),
                         ('screen.repeat_last', 'F20', 'PRESS'))
        self.assertFalse(actual['active'])
        self.assertTrue(actual['repeat'])
        self.assertTrue(actual['is_user_modified'])
        self.assertEqual(reader['uv_repeat_probe']['verified_incoming_manifest'], saved['saved_manifest'])
        for run in (writer, reader):
            self.assertEqual(run['native_status'], 'complete')
            proof = run['uv_repeat_probe']
            restored = proof['saved_edit_restored']
            self.assertEqual((restored['event'], restored['active'], restored['repeat']),
                             ('F20', False, True))
            self.assertEqual(restored['fresh_process'], run is reader)
            self.assertTrue(restored['is_user_modified'])
            self.assertEqual(len(proof['releases']), 2)
            for release in proof['releases']:
                self.assertTrue(release['strict_preservation'])
                self.assertTrue(release['source_maps_exact'])
                self.assertTrue(release['owned_candidate_absent'])
                self.assertEqual(release['retained_source_edit_count'], 0)

    def test_uv_repeat_actual_production_identity_and_behavior(self):
        run = self.runs['uv_g_production-1794553968267516000']
        self.assertEqual(run['native_status'], 'complete')
        proof = run['uv_repeat_probe']
        self.assertTrue(proof['production_identity'])
        self.assertTrue(proof['owner'].startswith('legacy:Transform:'))
        self.assertEqual(proof['request_id'], '0:UV Editor:G:PRESS')
        for path, expected in self.manifest['uv_repeat_route']['source_sha256'].items():
            self.assertEqual(run['source_sha256'][path], expected)
        self.assertEqual(len(proof['installations']), 2)
        for entry in proof['installations']:
            self.assertTrue(entry['via_production_toggle'])
            self.assertEqual(entry['owner'], proof['owner'])
            self.assertEqual(entry['owned_count'], 1)
            self.assertTrue(entry['assignment']['event']['repeat'])
        self.assertEqual(len(proof['releases']), 2)
        for release in proof['releases']:
            self.assertTrue(release['strict_preservation'])
            self.assertTrue(release['strict_snapshot_equality'])
            self.assertTrue(release['source_maps_exact'])
            self.assertTrue(release['other_transform_declarations_preserved_after_actions_off'])
            self.assertTrue(release['owned_candidate_absent'])
        self.assertEqual(Counter(case['expectation'] for case in run['dispatch']), {
            'empty_history': 1, 'single_repeat': 3, 'translate': 3, 'move_tool': 2})
        empty = run['dispatch'][0]
        self.assertEqual(empty['history_before_input'], [])
        self.assertFalse(empty['repeat_poll_before_input'])

    def test_uv_repeat_production_saved_edit_and_fresh_reopen(self):
        writer = self.runs['uv_g_production_save-1794554158037432000']
        reader = self.runs['uv_g_production_reopen-1794554208354408000']
        manifest = writer['uv_repeat_probe']['saved_edit']['saved_manifest']
        self.assertEqual(reader['uv_repeat_probe']['verified_incoming_manifest'], manifest)
        self.assertTrue(manifest['production_identity'])
        self.assertTrue(writer['uv_repeat_probe']['saved_edit']['immediate_save'])
        self.assertTrue(writer['uv_repeat_probe']['saved_edit']['owned_source_unchanged'])
        for run in (writer, reader):
            self.assertEqual(run['native_status'], 'complete')
            proof = run['uv_repeat_probe']
            self.assertEqual(proof['owner'], manifest['owner'])
            self.assertTrue(proof['owner'].startswith('legacy:Transform:'))
            actual = proof['saved_edit_restored']
            self.assertEqual((actual['event'], actual['active'], actual['repeat']), ('F20', False, True))
            self.assertTrue(actual['is_user_modified'])
            self.assertEqual(actual['fresh_process'], run is reader)
            self.assertEqual(len(proof['releases']), 2)
            for release in proof['releases']:
                self.assertTrue(release['strict_preservation'])
                self.assertTrue(release['source_maps_exact'])
                self.assertTrue(release['owned_candidate_absent'])
                self.assertTrue(release['other_transform_declarations_preserved_after_actions_off'])
                self.assertEqual(release['retained_source_edit_count'], 0)

    def test_matched_editor_guard_preserves_exact_endpoints_and_unknowns(self):
        run = self.runs['editor_probe-1794550412457976000']
        self.assertEqual(run['native_status'], 'complete')
        endpoints = run['editor_matched_endpoints']['endpoints']
        self.assertEqual([value['label'] for value in endpoints],
                         ['before_owned_probe', 'after_first_release', 'after_second_release'])
        baseline = endpoints[0]
        for value in endpoints:
            self.assertEqual(value['context'], baseline['context'])
            self.assertTrue(value['window_delivered'])
            self.assertTrue(value['stable_sources'])
            self.assertTrue(value['stable_merged'])
            self.assertFalse(value['missing_relevant_targets'])
            self.assertFalse(value['relevant_target_unknowns'])
            self.assertEqual(len(value['readable_foreign_sentinels']), 4)
            self.assertTrue(all(not entry['row']['read_issues']
                                for entry in value['readable_foreign_sentinels']))
            self.assertEqual(value['source'], baseline['source'])
            self.assertEqual(value['foreign_merged'], baseline['foreign_merged'])
            self.assertEqual(value['unknown_properties'], baseline['unknown_properties'])
            self.assertEqual(len(value['unknown_properties']), 40)
        for value in endpoints[1:]:
            self.assertTrue(value['strict_sources_equal'])
            self.assertTrue(value['strict_foreign_merged_equal'])
        proof = run['editor_handler_proof']
        self.assertTrue(proof['foreign_source_fields_and_order_unchanged'])
        self.assertFalse(proof['complete_property_comparison'])
        self.assertEqual(len(proof['installations']), 2)
        self.assertEqual(len(proof['releases']), 2)
        installed = [case for case in run['dispatch'] if case['stage'] == 'installed']
        self.assertEqual(len(installed), 8)
        for case in installed:
            self.assertTrue(case['probe_poll'])
            self.assertTrue(case['selection_changed'])
            self.assertFalse(case['view_changed'])
            self.assertEqual([call['target'] for call in case['callbacks']], [case['target']])


    def test_production_editor_retains_owned_generation_identity_failure(self):
        run = self.runs['editor_production-1794553202272103000']
        self.assertEqual(run['native_status'], 'error')
        self.assertIn('Matched-context source comparison failed', run['error'])
        self.assertIn('cleanup_error', run)
        before, after = run['editor_matched_endpoints']['endpoints']
        self.assertFalse(after['strict_sources_equal'])
        self.assertTrue(after['strict_foreign_merged_equal'])
        for role in ('default', 'active'):
            self.assertEqual(before['source'][role], after['source'][role])
        changes = []
        for old_map, new_map in zip(before['source']['addon'], after['source']['addon'], strict=True):
            self.assertEqual({k: v for k, v in old_map.items() if k != 'items'},
                             {k: v for k, v in new_map.items() if k != 'items'})
            for old, new in zip(old_map['items'], new_map['items'], strict=True):
                if old != new:
                    self.assertEqual(old['target'], 'wm.bh_save_as_mainfile')
                    self.assertEqual({k: v for k, v in old.items() if k != 'blender_id'},
                                     {k: v for k, v in new.items() if k != 'blender_id'})
                    changes.append((old['blender_id'], new['blender_id']))
        self.assertEqual(changes, [(18, 39), (19, 40)])
        installed = [case for case in run['dispatch'] if case['stage'] == 'installed']
        self.assertEqual(len(installed), 8)
        for case in installed:
            self.assertTrue(case['selection_changed'])
            self.assertFalse(case['view_changed'])
            self.assertEqual([call['target'] for call in case['callbacks']], [case['target']])
            self.assertEqual(case['input_delivery']['counts_in_expected_window_region'],
                             {'window': 1, 'editor': 1})
            self.assertEqual(case['input_delivery']['unmodified_wheel']['status'], 'observed_view_change')

    def test_editor_source_comparison_requires_exact_owned_provenance(self):
        from blender_keymap_category03_editors import EditorCases
        baseline, released = self.runs['editor_production-1794553202272103000']['editor_matched_endpoints']['endpoints']
        before, after = baseline['source'], released['source']

        def synthetic_provenance(source):
            # Comparator test only: historical batch14 did not collect live
            # ownership evidence and must remain a failed native receipt.
            return [{'owner_id': 'legacy:Pipeline:synthetic', 'request_id': str(j),
                     'runtime_owned_valid': True, 'registered_pair_matches': True,
                     'map_index': 0, 'row_index': j, 'scope': source['addon'][0]['scope'],
                     'row': source['addon'][0]['items'][j]} for j in (1, 2)]

        a, b = synthetic_provenance(before), synthetic_provenance(after)
        compare = EditorCases.compare_sources
        result = compare(before, after, a, b)
        self.assertTrue(result['accepted_sources_equal'])
        self.assertFalse(result['strict_raw_sources_equal'])
        self.assertFalse(compare(before, after)['accepted_sources_equal'])
        foreign_edit = copy.deepcopy(after)
        foreign_edit['addon'][0]['items'][0]['blender_id'] += 1
        self.assertFalse(compare(before, foreign_edit, a, b)['strict_foreign_identity_equal'])
        owned_edit = copy.deepcopy(after)
        owned_edit['addon'][0]['items'][1]['active'] = False
        self.assertFalse(compare(before, owned_edit, a, synthetic_provenance(owned_edit))['owned_semantics_and_order_equal'])
        invalid_proof = copy.deepcopy(b)
        invalid_proof[0]['runtime_owned_valid'] = False
        with self.assertRaises(AssertionError):
            compare(before, after, a, invalid_proof)

    def test_production_editor_ownership_toggles_and_outside_context_limits(self):
        selection = self.runs['editor_production-1794553648264616000']
        outside = self.runs['editor_production-1794553721545059000']
        corrected_outside = self.runs['editor_production-1794556971140047000']
        for run, count in ((selection, 14), (outside, 20), (corrected_outside, 8)):
            self.assertEqual(run['native_status'], 'complete')
            self.assertEqual(len(run['dispatch']), count)
            self.assertTrue(run['watcher_stopped'])
            self.assertEqual(run['cleanup']['owned'], 0)
            for endpoint in run['editor_matched_endpoints']['endpoints']:
                proof = endpoint['owned_source_generations']
                self.assertEqual(len(proof), 2)
                for entry in proof:
                    self.assertTrue(entry['runtime_owned_valid'])
                    self.assertTrue(entry['registered_pair_matches'])
                    self.assertTrue(entry['owner_id'].startswith('legacy:Pipeline:'))
                    self.assertEqual(entry['row']['target'], 'wm.bh_save_as_mainfile')
                if not endpoint.get('is_baseline'):
                    self.assertFalse(endpoint['strict_sources_equal'])
                    self.assertTrue(endpoint['strict_foreign_merged_equal'])
                    self.assertEqual(endpoint['source_comparison'], {
                        'strict_raw_sources_equal': False, 'strict_foreign_identity_equal': True,
                        'owned_semantics_and_order_equal': True, 'proven_owned_generations': 2,
                        'accepted_sources_equal': True})
        for case in selection['dispatch']:
            self.assertFalse(case.get('errors'))
            self.assertEqual(case['input_delivery']['counts_in_expected_window_region'],
                             {'window': 1, 'editor': 1})
            self.assertEqual(case['input_delivery']['unmodified_wheel']['status'], 'observed_view_change')
            enabled = case['stage'] in ('installed', 'reinstalled')
            self.assertEqual(case['selection_changed'], enabled)
            self.assertEqual([call['target'] for call in case['callbacks']],
                             [case['target']] if enabled else [])
            if enabled:
                self.assertFalse(case['view_changed'])
        for case in outside['dispatch']:
            delivery = case['input_delivery']
            if case['kind'] == 'sequencer_preview':
                self.assertFalse(delivery['window_delivered'])
                self.assertEqual(case['wheel_observation'], 'window_control_missing')
                self.assertNotIn('probe_poll', case)
                continue
            self.assertTrue(delivery['window_delivered'])
            self.assertFalse(case['probe_poll'])
            self.assertEqual(case['callbacks'], [])
            self.assertFalse(case['selection_changed'])
            expected = 'inconclusive' if case['kind'] == 'file_browser' else 'observed_view_change'
            self.assertEqual(delivery['unmodified_wheel']['status'], expected)
        for case in corrected_outside['dispatch']:
            delivery = case['input_delivery']
            self.assertTrue(delivery['window_delivered'])
            self.assertEqual(delivery['expected_region'],
                             'PREVIEW' if case['kind'] == 'sequencer_preview' else 'WINDOW')
            self.assertEqual(delivery['unmodified_wheel']['status'], 'observed_view_change')
            self.assertFalse(case['probe_poll'])
            self.assertEqual(case['callbacks'], [])
            self.assertFalse(case['selection_changed'])
            self.assertTrue(case['view_changed'])

    def test_uv_ordinary_receipt_retains_dispatch_mismatch_and_cursor_fixture_error(self):
        production = self.runs['ordinary_production-1794557329510485000']
        reference = next(run for run in self.native['reference_runs']
                         if run['id'] == 'reference-evidence-1794557393495550000')
        self.assertEqual(set(self.manifest['historical_dispatch_mismatches']), {
            case['ledger_id'] for case in production['dispatch'][:2]})
        for item in self.manifest['historical_dispatch_mismatches'].values():
            self.assertEqual(item['status'], 'implemented-dispatch-mismatch')
        for cases, expected in ((production['dispatch'], (4, 4)),
                                (reference['observations']['dispatch'], (9, 1))):
            self.assertEqual(len(cases), 3)
            for case, count in zip(cases[:2], expected):
                self.assertTrue(case['input_delivery']['delivered'])
                self.assertEqual(case['before']['editor_ui_type'], 'UV')
                self.assertEqual(case['before']['context_mode'], 'EDIT_MESH')
                self.assertEqual(len(case['before']['selected_uv']), 4)
                self.assertEqual(len(case['after']['selected_uv']), count)
                self.assertEqual(case['exact_rows_before_probe']['user'], 1)
                self.assertTrue(case['direct_control']['poll'])
                direct_count = 9 if case['tested_key'] == 'UP_ARROW' else 1
                self.assertEqual(len(case['direct_control']['after']['selected_uv']), direct_count)
            cursor = cases[2]
            self.assertEqual(cursor['before']['cursor'], cursor['after']['cursor'])
            self.assertEqual(cursor['error']['phase'], 'direct_fixture_control')
            self.assertEqual(cursor['error']['type'], 'TypeError')
            self.assertIn('expected a set, not a list', cursor['error']['message'])
        self.assertEqual(reference['observations']['status'], 'error')
        self.assertFalse(reference['observations']['ordinary_proof']['foreign_source_fields_and_order_unchanged'])

    def test_uv_arrow_probe_proves_frames_winner_and_scoped_precedence(self):
        run = self.runs['uv_arrow_probe-1794558496042342000']
        proof = run['uv_arrow_precedence']
        self.assertEqual(run['native_status'], 'complete')
        self.assertEqual(proof['status'], 'complete')
        self.assertEqual(len(proof['cases']), 13)
        self.assertEqual(len(proof['installs']), 2)
        self.assertEqual(len(proof['releases']), 2)
        self.assertTrue(proof['fixture_cleanup_complete'])
        self.assertTrue(run['ordinary_proof']['foreign_source_fields_and_order_unchanged'])
        self.assertTrue(run['watcher_stopped'])
        self.assertEqual(run['cleanup']['owned'], 0)
        for endpoint in proof['releases']:
            self.assertTrue(endpoint['exact_sources_and_merged_equal'])
            self.assertEqual(endpoint['maps'], proof['baseline_maps'])
        for case in proof['cases']:
            self.assertTrue(case['passed'])
            self.assertTrue(case['input_delivery']['delivered'])
            self.assertEqual(case['before']['frame_current'], 5)
            if case['expected'] == 'uv_selection':
                self.assertEqual(case['after']['frame_current'], 5)
                self.assertNotEqual(case['before']['selected_uv'], case['after']['selected_uv'])
            else:
                self.assertIn(case['after']['frame_current'], (1, 10))
                self.assertEqual(case['callbacks'], [])
                if case['kind'] == 'uv':
                    self.assertEqual(case['before']['selected_uv'], case['after']['selected_uv'])
                else:
                    self.assertFalse(case['guard_poll'])

    def test_uv_arrow_partial_production_retains_control_order_failure(self):
        run = self.runs['uv_arrow_production-1794559318047548000']
        proof = run['uv_arrow_precedence']
        self.assertEqual(run['native_status'], 'error')
        self.assertEqual(len(run['dispatch']), 10)
        self.assertTrue(all(case['passed'] for case in run['dispatch']))
        self.assertFalse(proof['releases'][0]['accepted_preservation'])
        final = proof['final_without_control']
        self.assertTrue(final['source_comparison']['accepted_sources_equal'])
        self.assertTrue(final['strict_foreign_merged_equal'])
        self.assertIn('cleanup_error', run)
        self.assertNotIn('watcher_stopped', run)
        self.assertTrue(all(owner['owner_id'].startswith('legacy:Selection:')
                            for owner in proof['installs'][0]['actual_owners']))

    def test_uv_arrow_production_preserves_context_fallback_and_matched_endpoints(self):
        run = self.runs['uv_arrow_production-1794559722114724000']
        proof = run['uv_arrow_precedence']
        self.assertEqual(run['native_status'], 'complete')
        self.assertEqual(proof['status'], 'complete')
        self.assertTrue(proof['production'])
        self.assertEqual(len(run['dispatch']), 13)
        self.assertTrue(all(case['passed'] and case['input_delivery']['delivered'] for case in run['dispatch']))
        self.assertEqual(self.manifest['blocking_dispatch_reconciliation'], {})
        self.assertEqual(len(self.manifest['resolved_dispatch_reconciliation']), 2)
        for install in proof['installs']:
            self.assertEqual(install['owned_pair_count'], 2)
            self.assertEqual(install['registered_pair_matches'], [1, 1])
            self.assertTrue(all(owner['owner_id'].startswith('legacy:Selection:')
                                for owner in install['actual_owners']))
        self.assertEqual(len(proof['releases']), 2)
        for endpoint in proof['releases']:
            self.assertTrue(endpoint['accepted_preservation'])
            self.assertTrue(endpoint['source_comparison']['strict_foreign_identity_equal'])
            self.assertTrue(endpoint['source_comparison']['owned_semantics_and_order_equal'])
            self.assertTrue(endpoint['strict_foreign_merged_equal'])
            for maps in endpoint['maps'].values():
                self.assertFalse(any(row['target'] == 'wm.category03_ordinary_control'
                                     for keymap in maps for row in keymap['items']))
        final = proof['final_without_control']
        self.assertTrue(final['source_comparison']['accepted_sources_equal'])
        self.assertTrue(final['strict_foreign_merged_equal'])
        self.assertTrue(run['watcher_stopped'])
        self.assertEqual(run['cleanup']['owned'], 0)

    def test_cursor_phase_control_does_not_claim_an_effect_from_finished(self):
        production = self.runs['ordinary_production-1794560686280956000']
        reference = next(run for run in self.native['reference_runs']
                         if run['id'] == 'reference-evidence-1794560733807712000')
        self.assertEqual(production['native_status'], 'complete')
        self.assertEqual(reference['observations']['status'], 'error')
        self.assertFalse(reference['observations']['ordinary_proof']['foreign_source_fields_and_order_unchanged'])
        for cases in (production['dispatch'], reference['observations']['dispatch']):
            self.assertEqual(len(cases), 1)
            case = cases[0]
            self.assertEqual(case['ledger_id'], self.manifest['uv_cursor_dispatch']['row_id'])
            self.assertTrue(case['input_delivery']['delivered'])
            self.assertNotIn('error', case)
            control = case['direct_control']
            self.assertTrue(control['poll'])
            self.assertEqual(control['result'], ['FINISHED'])
            self.assertEqual(control['native_enum_flag_arguments'], {'snap_elements': ['INCREMENT']})
            self.assertEqual(control['properties']['value'], [0.125, 0.0625, 0.0])
            self.assertEqual([phase['phase'] for phase in case['input_phases']], [
                'after_press', 'after_initial_motion', 'after_second_motion', 'after_release'])
            for snapshot in [case['after'], control['after'],
                             *(phase['snapshot'] for phase in case['input_phases'])]:
                self.assertEqual(snapshot['cursor'], [0.5, 0.5])
                for key in ('selected_uv', 'uv_coordinates', 'view_center'):
                    self.assertEqual(snapshot[key], case['before'][key])
        self.assertEqual(self.manifest['uv_cursor_dispatch']['status'], 'unverified: gesture and direct control had no effect in either setup')

    def test_combined_context_receipt_retains_tool_effects_and_control_failures(self):
        production = self.runs['ordinary_production-1794561360052050000']
        reference = next(run for run in self.native['reference_runs']
                         if run['id'] == 'reference-evidence-1794561456886365000')
        prod, ref = production['dispatch'], reference['observations']['dispatch']
        self.assertEqual(len(prod), 16)
        self.assertEqual(len(ref), 16)
        self.assertEqual(production['native_status'], 'complete')
        self.assertEqual(reference['observations']['status'], 'error')
        for left, right in zip(prod, ref):
            self.assertEqual(left['ledger_id'], right['ledger_id'])
            self.assertEqual(left['context_variant'], right['context_variant'])
            for case in (left, right):
                self.assertTrue(case['context_ready'])
                self.assertTrue(case['input_delivery']['delivered'])
                if case['target'] == 'wm.tool_set_by_id':
                    self.assertTrue(case['start_control_valid'])
                    self.assertEqual(case['error']['phase'], 'direct_fixture_control')
                    self.assertEqual(case['error']['type'], 'RuntimeError')
        for cases in (prod, ref):
            self.assertEqual(sum('error' in case for case in cases), 14)
            uv_t = next(case for case in cases if case['tested_key'] == 'T')
            self.assertEqual(uv_t['before']['active_tool'], 'builtin.select_box')
            self.assertEqual(uv_t['after']['active_tool'], 'builtin.transform')
        # First-press agreement does not establish cycling parity.
        prod_q, ref_q = prod[3], ref[3]
        self.assertEqual(prod_q['after']['active_tool'], ref_q['after']['active_tool'])
        self.assertEqual(prod_q['after_second_input']['active_tool'], 'builtin.select_circle')
        self.assertEqual(ref_q['after_second_input']['active_tool'], 'builtin.select_box')
        self.assertFalse(reference['observations']['ordinary_proof']['foreign_source_fields_and_order_unchanged'])
        self.assertTrue(production['watcher_stopped'])
        self.assertEqual(production['cleanup']['owned'], 0)

    def test_reference_modal_switch_retains_identity_and_strict_merged_loss(self):
        reference = next(run for run in self.native['reference_runs']
                         if run['id'] == 'reference-evidence-1794563307033648000')
        data = reference['observations']
        self.assertEqual(data['status'], 'error')
        control, switch = data['dispatch']
        for case in (control, switch):
            self.assertTrue(case['input_delivery']['delivered'])
            self.assertTrue(case['initial_positive_effect'])
            self.assertEqual(case['invoke_result'], ['RUNNING_MODAL'])
        self.assertTrue(control['cancel_restored_geometry'])
        self.assertTrue(switch['first_e_rotation_observed'])
        self.assertTrue(switch['second_e_rotation_changed'])
        self.assertTrue(switch['confirmation_stopped_motion'])
        phases = {phase['phase']: phase['snapshot'] for phase in switch['phases']}
        self.assertEqual([phases[phase]['modal_operators'] for phase in
                          ('initial_motion', 'after_first_e_motion', 'after_second_e_motion')],
                         [['TRANSFORM_OT_translate'], ['TRANSFORM_OT_rotate'], ['TRANSFORM_OT_trackball']])
        self.assertEqual(phases['after_confirm']['modal_operators'], [])
        self.assertEqual(phases['after_extra_motion'], phases['after_confirm'])
        proof = data['modal_switch_proof']
        self.assertFalse(proof['exact_source_and_merged_preservation'])
        for role, before in proof['maps_before_without_control'].items():
            after = proof['maps_after_without_control'][role]
            self.assertEqual([km for km in before if km['scope']['name'] == 'Transform Modal Map'],
                             [km for km in after if km['scope']['name'] == 'Transform Modal Map'])
        before_uv = next(km for km in proof['maps_before_without_control']['user'] if km['scope']['name'] == 'UV Editor')
        after_uv = next(km for km in proof['maps_after_without_control']['user'] if km['scope']['name'] == 'UV Editor')
        self.assertEqual((len(before_uv['items']), len(after_uv['items'])), (318, 272))
        remaining_ids = {row['blender_id'] for row in after_uv['items']}
        self.assertEqual(Counter(row['target'] for row in before_uv['items']
                                 if row['blender_id'] not in remaining_ids),
                         {'uv.toolkit_center_cursor_and_frame_all': 45, 'uv.toolkit_distribute': 1})
        self.assertTrue(data['ordinary_proof']['input_control']['released'])

    def test_factory_modal_comparison_keeps_translate_and_exact_maps(self):
        factory = self.runs['modal_observe-1794564688446795000']
        reference = self.reference_runs['reference-evidence-1794563307033648000']
        self.assertEqual(factory['native_status'], 'complete')
        for key in ('modal_fixture_sha256', 'ordinary_fixture_sha256'):
            self.assertEqual(factory[key], reference[key])
        control, switch = factory['dispatch']
        for case in (control, switch):
            self.assertTrue(case['input_delivery']['delivered'])
            self.assertTrue(case['invoke_poll'])
            self.assertEqual(case['invoke_result'], ['RUNNING_MODAL'])
            self.assertTrue(case['initial_positive_effect'])
        self.assertTrue(control['cancel_restored_geometry'])
        self.assertFalse(switch['first_e_rotation_observed'])
        self.assertFalse(switch['second_e_rotation_changed'])
        self.assertTrue(switch['confirmation_stopped_motion'])
        phases = {phase['phase']: phase['snapshot'] for phase in switch['phases']}
        for phase in ('initial_motion', 'after_first_e_motion', 'after_second_e_motion'):
            self.assertEqual(phases[phase]['modal_operators'], ['TRANSFORM_OT_translate'])
            self.assertEqual(phases[phase]['rotation_matrix'], phases['before']['rotation_matrix'])
        self.assertEqual(phases['after_confirm']['modal_operators'], [])
        self.assertEqual(phases['after_extra_motion'], phases['after_confirm'])
        readiness = factory['modal_capture_readiness']
        self.assertTrue(readiness['matched_context_and_counts'])
        self.assertEqual(readiness['before_capture'], readiness['before_addon_shutdown'])
        self.assertTrue(readiness['before_capture']['native_keyconfig_update'])
        proof = factory['modal_switch_proof']
        self.assertEqual(proof['modal_map_mutations'], 0)
        self.assertEqual(proof['runtime_capability_changes'], 0)
        self.assertTrue(proof['exact_source_and_merged_preservation'])
        self.assertEqual(proof['maps_before_without_control'], proof['maps_after_without_control'])
        self.assertTrue(factory['ordinary_proof']['input_control']['released'])

    def test_modal_alias_probe_retains_user_edit_rebinding_to_stock_R(self):
        run = self.runs['modal_alias_probe-1794565828872658000']
        self.assertEqual(run['native_status'], 'error')
        probe = run['modal_alias_probe']
        self.assertTrue(probe['partial_install_rollback_passed'])
        self.assertEqual([p['exact'] for p in probe['checkpoints']], [True, True, False])
        self.assertEqual(len(probe['installations']), 2)
        control, *cases = run['dispatch']
        self.assertTrue(control['cancel_restored_geometry'])
        for case in cases:
            self.assertTrue(case['initial_positive_effect'])
            self.assertTrue(case['expected_operator_sequence_verified'])
            self.assertTrue(case['confirmation_stopped_motion'])
        self.assertTrue(probe['user_edits']['complete_readback_passed'])
        self.assertEqual({entry['native_id'] for entry in
                          probe['user_edits']['edited_user_identities'].values()}, {60, 61})
        proof = run['modal_switch_proof']
        self.assertFalse(proof['exact_source_and_merged_preservation'])
        for role in ('default', 'active', 'addon'):
            self.assertEqual(proof['maps_before_without_control'][role],
                             proof['maps_after_without_control'][role])
        before = proof['maps_before_without_control']['user']
        after = proof['maps_after_without_control']['user']
        for old, new in zip(before, after):
            if old['scope']['name'] != 'Transform Modal Map':
                self.assertEqual(old, new)
                continue
            self.assertEqual(len(old['items']), 56)
            self.assertEqual([row['blender_id'] for row in old['items']],
                             [row['blender_id'] for row in new['items']])
            changed = [(left, right) for left, right in zip(old['items'], new['items'])
                       if left != right]
            self.assertEqual([row['blender_id'] for row, _ in changed], [16, 17])
            for left, right in changed:
                self.assertEqual(left['event']['type'], 'R')
                self.assertFalse(left['event']['repeat'])
                self.assertEqual(right['event']['type'], 'F18')
                self.assertTrue(right['event']['repeat'])
                self.assertEqual(right['active'], right['target'] == 'TRACKBALL')
                self.assertTrue(right['is_user_modified'])
            self.assertFalse(old['is_user_modified'])
            self.assertTrue(new['is_user_modified'])
        self.assertTrue(run['modal_capture_readiness']['matched_context_and_counts'])
        self.assertTrue(run['watcher_stopped'])
        self.assertEqual(run['cleanup']['owned'], 0)

    def test_focused_subtraction_retains_matching_effects_and_fixture_errors(self):
        factory = self.runs['subtract_probe-1794566659165110000']
        reference = self.reference_runs['reference-evidence-1794566535713559000']
        self.assertEqual(factory['handler_fixture_sha256'], reference['handler_fixture_sha256'])
        self.assertEqual(factory['native_status'], 'error')
        data = reference['observations']
        self.assertEqual(data['status'], 'error')
        for run in (factory, data):
            case, = run['dispatch']
            self.assertTrue(case['input_delivery']['delivered'])
            self.assertTrue(case['native_subtraction_observed'])
            self.assertEqual(case['direct_control']['point'], case['projected_point'])
            self.assertEqual(case['direct_control']['result'], ['FINISHED', 'PASS_THROUGH'])
            self.assertTrue(case['direct_control']['positive_subtraction'])
            phases = {phase['phase']: phase['snapshot'] for phase in case['phases']}
            self.assertEqual([phases[label]['target_selected'] for label in
                              ('before_press', 'after_press', 'after_release', 'direct_reset', 'after_direct')],
                             [True, True, False, True, False])
        self.assertTrue(factory['subtract_proof']['exact_source_and_merged_preservation'])
        self.assertFalse(data['subtract_proof']['exact_source_and_merged_preservation'])
        self.assertEqual(factory['subtract_proof']['exact_candidate_counts'],
                         {'default': 0, 'active': 0, 'addon': 1, 'user': 1})
        self.assertEqual(data['subtract_proof']['exact_candidate_counts'],
                         {'default': 0, 'active': 1, 'addon': 0, 'user': 1})
        self.assertTrue(factory['watcher_stopped'])
        self.assertEqual(factory['cleanup']['owned'], 0)

    def test_shared_production_persistence_restores_editor_circle_framing_and_arrow_edits(self):
        pairs = (
            ('editor_save-1794555923466868000', 'editor_reopen-1794556023841045000', {'editor_more'}),
            ('persistence-1794556127823686000', 'reopen-1794556179765247000', {'circle', 'framing'}),
            ('uv_arrow_save-1794559822761297000', 'uv_arrow_reopen-1794559885933843000', {'uv_arrow_more'}),
        )
        for writer_id, reader_id, names in pairs:
            writer, reader = self.runs[writer_id], self.runs[reader_id]
            manifest = writer['production_persistence']['saved_manifest']
            self.assertTrue(writer['production_persistence']['immediate_save'])
            self.assertTrue(writer['production_persistence']['declared_sources_unchanged'])
            self.assertEqual(reader['production_persistence']['verified_incoming_manifest'], manifest)
            self.assertEqual(writer['source_sha256'], reader['source_sha256'])
            for run in (writer, reader):
                self.assertEqual(run['native_status'], 'complete')
                self.assertTrue(run['watcher_stopped'])
                self.assertEqual(run['cleanup']['owned'], 0)
                proof = run['production_persistence']
                self.assertEqual(proof['fresh_process'], run is reader)
                self.assertEqual(len(proof['restorations']), 2 if run is reader else 1)
                for restored in proof['restorations']:
                    self.assertEqual(set(restored), names)
                    for name, value in restored.items():
                        row = value['row']
                        self.assertTrue(row['is_user_modified'])
                        self.assertTrue(value['map_is_user_modified'])
                        self.assertEqual(row['event']['type'], {
                            'editor_more': 'F18', 'framing': 'F19', 'circle': 'F20', 'uv_arrow_more': 'F17'}[name])
                        self.assertEqual(row['active'], name not in ('editor_more', 'uv_arrow_more'))
                        if name == 'uv_arrow_more':
                            self.assertTrue(row['event']['repeat'])
                        if name == 'circle':
                            self.assertEqual(row['properties']['radius'], 31)
                for endpoint in run['editor_matched_endpoints']['endpoints'][1:]:
                    self.assertTrue(endpoint['source_comparison']['accepted_sources_equal'])
                    self.assertTrue(endpoint['strict_foreign_merged_preservation'])
                    self.assertTrue(endpoint['expected_owned_map_edit_markers'])


class Category03RegistrationTests(Category03Evidence, unittest.TestCase):
    def setUp(self):
        prefix = '_bluehole_category03_test'
        self.runtime = FakeRuntime()
        bpy = self.runtime.bpy
        bpy.types = types.SimpleNamespace(PropertyGroup=type('PropertyGroup', (), {}))
        bpy_props = types.ModuleType('bpy.props')
        bpy_props.BoolProperty = bpy_props.EnumProperty = lambda **definition: definition

        def stub(suffix, *, path=None, **attributes):
            name = prefix + suffix
            module = types.ModuleType(name)
            if path is not None:
                module.__path__ = [str(ROOT / path)]
            vars(module).update(attributes)
            sys.modules[name] = module

        modules = patch.dict(sys.modules, {'bpy': bpy, 'bpy.props': bpy_props})
        modules.start()
        self.addCleanup(modules.stop)

        stub('', path='.')
        stub('.preferences', path='preferences')
        stub('.preferences.addon', path='preferences/addon')
        self.navigation_prefs = types.SimpleNamespace(active_navigation_keymap_tab='VIEW_FRAMING')
        self.preferences = types.SimpleNamespace(keymap=types.SimpleNamespace(
            enable_keymaps=False, navigation=self.navigation_prefs))
        stub('.preferences.prefs', prefs=lambda: self.preferences)
        self.draw_feature = Mock()
        stub('.preferences.addon.keymaps.keymap_ui_utils',
             draw_action_feature_keymaps=self.draw_feature)
        stub('.Lib.commonUtils.runtime.diagnostics')
        stub('.debug.debug_flags')

        def load(suffix):
            return importlib.import_module(prefix + '.' + suffix)

        self.load = load
        self.stub = stub
        self.navigation = load('actions.actions.keymaps.navigation')
        self.register = load('keymaps.navigation_keymaps_register')
        self.keymap_utils = load('keymaps.keymap_utils')
        self.preference_ui = load('preferences.addon.keymaps.keymap_props_navigation')
        self.framing = load('actions.actions.keymaps.navigation.view_framing')
        self.keymap_utils.bind_category_pairs(self.register.KEYMAP_CATEGORY,
                                              self.register.registered_navigation_keymaps)
        self.addCleanup(self.keymap_utils.release_all)
        self.addCleanup(self.register.unregister)

        # Blender exposes properties before values are applied to a new item.
        # The accepted fake needs a schema to expose those same writable fields.
        schemas = {
            'view3d.view_selected': {'use_all_regions': False},
            'view3d.view_all': {'center': False, 'use_all_regions': False},
            'view3d.localview': {'frame_selected': True},
            'view3d.view_axis': {'type': 'FRONT', 'align_active': False, 'relative': False},
            'view3d.view_pan': {'type': 'PANLEFT'},
            'view3d.zoom': {'delta': 0, 'mx': 0, 'my': 0, 'use_cursor_init': True},
            'transform.translate': {'cursor_transform': False, 'release_confirm': False},
            'image.view_all': {'fit_view': False},
            'mesh.select_more': {'use_face_step': True},
            'mesh.select_less': {'use_face_step': True},
            'object.select_hierarchy': {'direction': 'PARENT', 'extend': True},
            'uv.select_all': {'action': 'TOGGLE'},
            'uv.select': {'deselect': False, 'deselect_all': False, 'extend': False,
                          'location': [0.0, 0.0], 'select_passthrough': False, 'toggle': False},
            'uv.select_circle': {'mode': 'SET', 'radius': 25, 'wait_for_input': False,
                                 'x': 0, 'y': 0},
            'view3d.select_circle': {'mode': 'SET', 'radius': 25, 'wait_for_input': True,
                                     'x': 0, 'y': 0},
            'view3d.select': {'center': False, 'deselect': False, 'deselect_all': False,
                              'enumerate': False, 'extend': False, 'location': [0, 0],
                              'object': False, 'select_passthrough': False, 'toggle': False},
            'wm.tool_set_by_id': {
                'as_fallback': False, 'cycle': False, 'name': '', 'space_type': 'EMPTY',
            },
        }
        create_item = FakeItems.new

        def new_item(items, idname, *args, **kwargs):
            schema = schemas.get(idname)
            if idname == 'transform.translate' and items.map.name == 'Node Editor':
                schema = {**schema, 'view2d_edge_pan': False}
            with patch.object(items, 'new_prop_schema', schema):
                return create_item(items, idname, *args, **kwargs)

        item_schema = patch.object(FakeItems, 'new', new_item)
        item_schema.start()
        self.addCleanup(item_schema.stop)
        definitions = self.preference_ui.NavigationKeymapPG.__annotations__
        for name in ('enable_navigation_keymaps', 'enable_navigation_viewport_movement',
                     'enable_navigation_viewport_axis', 'enable_navigation_view_framing'):
            setattr(self.navigation_prefs, name, definitions[name]['default'])

    def framing_actions(self):
        return self.framing.get_navigation_view_framing_actions()

    def addon_rows(self):
        return [(keymap, item) for keymap in self.runtime.configs.addon.keymaps
                for item in keymap.keymap_items]

    def draft_actions(self, group, module):
        entries = self.manifest['ordinary_source_drafts']['groups'][group]['actions']
        return {symbol: getattr(module, symbol) for symbol in entries}

    def assert_registered_binding(self, pair, binding):
        keymap, item = pair
        self.assertEqual(asdict(self.keymap_utils.capture_scope(keymap)), binding['scope'])
        self.assertEqual(asdict(self.keymap_utils.capture_event(item)), binding['event'])
        self.assertEqual(item.idname, binding['target'])
        self.assertEqual(item.active, binding['active'])

    def test_framing_actions_emit_exact_reviewed_targets_and_events(self):
        declaration = self.manifest['reviewed_declarations'][FRAMING]
        actions = [getattr(self.framing, symbol) for symbol in declaration['actions']]
        self.assertEqual(len(actions), 5)
        drafts = self.draft_actions(FRAMING, self.framing)
        self.assertEqual(self.framing_actions(), [*actions, *drafts.values()])
        self.assertTrue(all(action in self.navigation.get_all_navigation_actions()
                            for action in actions))

        self.preferences.keymap.enable_keymaps = True
        self.navigation_prefs.enable_navigation_viewport_movement = False
        self.navigation_prefs.enable_navigation_viewport_axis = False
        self.assertEqual(self.register.get_enabled_navigation_actions(), self.framing_actions())
        self.assertEqual(self.register.register(), 14)

        actual = iter(self.register.registered_navigation_keymaps[:13])
        for action, row_ids in zip(actions, declaration['actions'].values(), strict=True):
            self.assertEqual(len(action.keymap_bindings), len(row_ids))
            for row_id in row_ids:
                with self.subTest(row_id=row_id):
                    binding = self.ledger[row_id]['binding']
                    keymap, item = next(actual)
                    self.assertEqual(asdict(self.keymap_utils.capture_scope(keymap)),
                                     binding['scope'])
                    self.assertEqual(asdict(self.keymap_utils.capture_event(item)),
                                     binding['event'])
                    self.assertEqual(action.get_idname(), binding['target'])
                    self.assertEqual(item.idname, binding['target'])
                    self.assertEqual(action.get_props(), binding['properties'])
                    self.assertEqual(dict(item.properties), binding['properties'])
                    self.assertEqual(item.active, binding['active'])
        self.assertIsNone(next(actual, None))

    def test_framing_toggle_preserves_movement_axis_and_foreign_rows(self):
        stock = self.runtime.map('default')
        provider_map = self.runtime.map('addon')
        inherited_stock = row('view3d.view_all', key='HOME', prop_values={
            'center': False, 'use_all_regions': False,
        })
        provider_item = row('view3d.view_selected', key='F', prop_values={
            'use_all_regions': False,
        })
        stock.keymap_items.append_fixture(inherited_stock)
        provider_map.keymap_items.append_fixture(provider_item)
        self.assertEqual(self.register.register(), 0)

        self.preferences.keymap.enable_keymaps = True
        self.assertTrue(self.navigation_prefs.enable_navigation_view_framing)
        self.navigation_prefs.enable_navigation_view_framing = False
        movement_and_axis = self.register.get_enabled_navigation_actions()
        self.assertTrue(movement_and_axis)
        self.assertFalse(any(action in movement_and_axis for action in self.framing_actions()))
        previous_count = self.register.register()
        self.assertGreater(previous_count, 0)

        self.navigation_prefs.enable_navigation_view_framing = True
        self.assertCountEqual(self.register.get_enabled_navigation_actions(),
                              [*movement_and_axis, *self.framing_actions()])
        self.assertEqual(self.register.register(), previous_count + 14)
        self.navigation_prefs.enable_navigation_view_framing = False
        self.assertEqual(self.register.register(), previous_count)
        self.assertEqual(self.register.get_enabled_navigation_actions(), movement_and_axis)
        self.assertEqual(self.register.register(), previous_count)

        self.navigation_prefs.enable_navigation_view_framing = True
        self.assertEqual(self.register.register(), previous_count + 14)

        self.navigation_prefs.enable_navigation_keymaps = False
        self.assertEqual(self.register.register(), 0)
        self.assertEqual(self.addon_rows(), [(provider_map, provider_item)])
        self.assertEqual(list(stock.keymap_items), [inherited_stock])
        self.assertTrue(inherited_stock.active)
        self.assertTrue(provider_item.active)

    def test_framing_preferences_draw_the_same_actions_and_toggle(self):
        layout = Mock()
        self.preference_ui.draw(self.preferences, self.runtime.bpy.context, layout)
        self.draw_feature.assert_called_once_with(
            column=layout.column.return_value,
            feature_owner=self.navigation_prefs,
            feature_prop_name='enable_navigation_view_framing',
            actions=self.framing_actions(),
        )

    def load_selection_register(self):
        self.runtime.bpy.types.Operator = type('Operator', (), {})
        self.stub('.blenderUtils', path='blenderUtils')
        self.selection_tool_set = Mock(return_value=False)
        self.stub('.blenderUtils.toolUtils', tool_set=self.selection_tool_set)
        register = self.load('keymaps.selection_keymaps_register')
        self.keymap_utils.bind_category_pairs(register.KEYMAP_CATEGORY,
                                              register.registered_selection_keymaps)
        self.addCleanup(register.unregister)
        return register

    def test_extend_group_is_editable_independent_and_preserves_stock(self):
        register = self.load_selection_register()
        module = self.load('actions.actions.keymaps.selection.selection_extend')
        selection = self.load('actions.actions.keymaps.selection')
        subtract = self.load('actions.actions.keymaps.selection.selection_subtract')
        self.stub('.blenderUtils.operatorUtils', op_exists=lambda _idname: True)
        ui = self.load('preferences.addon.keymaps.keymap_props_selection')
        prefs = types.SimpleNamespace(**{name: definition['default']
            for name, definition in ui.SelectionKeymapPG.__annotations__.items()})
        self.assertTrue(prefs.enable_selection_extend)
        prefs.enable_selection_more_less = prefs.enable_selection_tool_switch = False
        prefs.enable_selection_all_none = prefs.enable_selection_circle = False
        prefs.enable_selection_extend = False
        self.preferences.keymap.selection = prefs
        self.preferences.keymap.enable_keymaps = True
        actions = module.get_selection_extend_actions()
        self.assertEqual(len(actions), 2)
        self.assertTrue(all(action in selection.get_all_selection_actions() for action in actions))
        expected = self.ledger['fee4a4d6ed723ffaa6fff80bdf81c6a3449e33667c182ee2ec2019699bff7d6d']['binding']
        stock_binding = self.ledger['4b0804a9a14135505b4bb747a327063796dab714ec18c2422dc44470567d396f']['binding']
        stock_item = row('view3d.select', key='LEFTMOUSE', value='CLICK', shift=True, oskey=True,
                         prop_values=stock_binding['properties'])
        stock = self.runtime.map('default', '3D View', space='VIEW_3D')
        stock.keymap_items.append_fixture(stock_item)
        uv_expected = self.ledger['0e8d690a0470457363cd15ff3448c54325c24261cae1dc525ebff9c3dd459f1d']['binding']
        uv_stock_binding = self.ledger['3f963e7c3ca365432c5a880e7e9c92b41b84f5f3670617f4fc367c62aac2da39']['binding']
        uv_stock = self.runtime.map('default', 'UV Editor')
        uv_stock_item = row('uv.select', key='LEFTMOUSE', value='CLICK', shift=True,
                            prop_values=uv_stock_binding['properties'])
        uv_stock.keymap_items.append_fixture(uv_stock_item)
        self.assertEqual(register.get_enabled_selection_actions(), subtract.get_selection_subtract_actions())
        self.assertEqual(register.register(), 1)
        prefs.enable_selection_extend = True
        self.assertEqual(register.register(), 3)
        for pair, binding in zip(register.registered_selection_keymaps[-2:], (expected, uv_expected)):
            self.assert_registered_binding(pair, binding)
            self.assertEqual(dict(pair[1].properties), binding['properties'])
        owners = [h for h in self.keymap_utils._FEATURES.values()
                  if any(dict(r.target.properties).get('extend') is True for r in h.assignments)]
        self.assertEqual(len(owners), 2)
        self.assertTrue(all(owner.owner_id.startswith('legacy:Selection:') for owner in owners))
        self.assertEqual({owner.assignments[0].request_id for owner in owners},
                         {'0:3D View:LEFTMOUSE:CLICK', '0:UV Editor:LEFTMOUSE:CLICK'})
        prefs.enable_selection_extend = False
        self.assertEqual(register.register(), 1)
        prefs.enable_selection_extend = True
        self.assertEqual(register.register(), 3)
        prefs.active_selection_keymap_tab = 'EXTEND'
        layout = Mock()
        ui.draw(self.preferences, self.runtime.bpy.context, layout)
        self.draw_feature.assert_called_once_with(column=layout.column.return_value,
            feature_owner=prefs, feature_prop_name='enable_selection_extend', actions=actions)
        prefs.enable_selection_keymaps = False
        self.assertEqual(register.register(), 0)
        prefs.enable_selection_keymaps = True
        self.assertEqual(register.register(), 3)
        self.preferences.keymap.enable_keymaps = False
        self.assertEqual(register.register(), 0)
        self.assertEqual(list(stock.keymap_items), [stock_item])
        self.assertTrue(stock_item.active)
        self.assertEqual(dict(stock_item.properties), stock_binding['properties'])
        self.assertEqual(list(uv_stock.keymap_items), [uv_stock_item])
        self.assertTrue(uv_stock_item.active)
        self.assertEqual(dict(uv_stock_item.properties), uv_stock_binding['properties'])

    def test_subtract_group_is_editable_independent_and_preserves_stock(self):
        register = self.load_selection_register()
        module = self.load('actions.actions.keymaps.selection.selection_subtract')
        selection = self.load('actions.actions.keymaps.selection')
        circle = self.load('actions.actions.keymaps.selection.selection_circle')
        self.stub('.blenderUtils.operatorUtils', op_exists=lambda _idname: True)
        ui = self.load('preferences.addon.keymaps.keymap_props_selection')
        definitions = ui.SelectionKeymapPG.__annotations__
        prefs = types.SimpleNamespace(**{name: definition['default']
                                        for name, definition in definitions.items()})
        self.assertTrue(prefs.enable_selection_subtract)
        prefs.enable_selection_extend = False
        prefs.enable_selection_more_less = prefs.enable_selection_tool_switch = False
        prefs.enable_selection_all_none = prefs.enable_selection_subtract = False
        self.preferences.keymap.selection = prefs
        self.preferences.keymap.enable_keymaps = True
        action, = module.get_selection_subtract_actions()
        self.assertIn(action, selection.get_all_selection_actions())
        expected = self.ledger['8674bcb4d856346f287980fd961ade31095f1165d1f6e25725e4c06b81f582f3']['binding']
        stock_binding = self.ledger['f33578f15e8bd108c710b0cb2dc3eaf3fe900e2011af912da8e54354433cd526']['binding']
        stock_item = row('view3d.select', key='LEFTMOUSE', value='CLICK', ctrl=True,
                         prop_values=stock_binding['properties'])
        stock = self.runtime.map('default', '3D View', space='VIEW_3D')
        stock.keymap_items.append_fixture(stock_item)
        self.assertEqual(register.get_enabled_selection_actions(), circle.get_selection_circle_actions())
        self.assertEqual(register.register(), 4)
        prefs.enable_selection_subtract = True
        self.assertEqual(register.register(), 5)
        self.assert_registered_binding(register.registered_selection_keymaps[-1], expected)
        self.assertEqual(dict(register.registered_selection_keymaps[-1][1].properties), expected['properties'])
        owners = [handle for handle in self.keymap_utils._FEATURES.values()
                  if any(request.target.idname == 'view3d.select' for request in handle.assignments)]
        self.assertEqual(len(owners), 1)
        self.assertTrue(owners[0].owner_id.startswith('legacy:Selection:'))
        self.assertEqual(owners[0].assignments[0].request_id, '0:3D View:LEFTMOUSE:CLICK')
        prefs.enable_selection_subtract = False
        self.assertEqual(register.register(), 4)
        self.assertEqual(register.get_enabled_selection_actions(), circle.get_selection_circle_actions())
        prefs.enable_selection_subtract = True
        self.assertEqual(register.register(), 5)
        prefs.active_selection_keymap_tab = 'SUBTRACT'
        layout = Mock()
        ui.draw(self.preferences, self.runtime.bpy.context, layout)
        self.draw_feature.assert_called_once_with(
            column=layout.column.return_value, feature_owner=prefs,
            feature_prop_name='enable_selection_subtract', actions=[action])
        prefs.enable_selection_keymaps = False
        self.assertEqual(register.register(), 0)
        prefs.enable_selection_keymaps = True
        self.assertEqual(register.register(), 5)
        self.preferences.keymap.enable_keymaps = False
        self.assertEqual(register.register(), 0)
        self.assertEqual(list(stock.keymap_items), [stock_item])
        self.assertTrue(stock_item.active)
        self.assertEqual(dict(stock_item.properties), stock_binding['properties'])

    def test_q_tool_switch_changes_only_click_to_press_for_existing_wrappers(self):
        register = self.load_selection_register()
        tool_switch = self.load('actions.actions.keymaps.selection.selection_tool_switch')
        group = self.manifest['reviewed_existing_declarations']['selection_tool_switch']
        correction = group['event_correction']
        self.assertEqual(correction, {'field': 'value', 'before': 'CLICK', 'after': 'PRESS'})
        self.preferences.keymap.selection = types.SimpleNamespace(
            enable_selection_keymaps=True,
            enable_selection_all_none=False,
            enable_selection_circle=False,
            enable_selection_subtract=False, enable_selection_extend=False,
            enable_selection_more_less=False,
            enable_selection_tool_switch=True,
        )
        self.preferences.keymap.enable_keymaps = True
        self.preferences.thirdparty = types.SimpleNamespace(
            x_ray_selection_tools=types.SimpleNamespace(enable_selection_tool_switch_box_x_ray=True),
        )
        actions = [getattr(tool_switch, symbol) for symbol in group['original_click_rows']]
        drafts = self.draft_actions('selection_tool_switch', tool_switch)
        self.assertEqual(register.get_enabled_selection_actions(), [*actions, *drafts.values()])
        self.assertEqual(register.register(), 8)

        for action, row_id, (keymap, item) in zip(
                actions, group['original_click_rows'].values(),
                register.registered_selection_keymaps[:4], strict=True):
            with self.subTest(row_id=row_id):
                binding = self.ledger[row_id]['binding']
                self.assertEqual(binding['event']['value'], correction['before'])
                self.assertEqual(self.rows[row_id]['runtime_disposition'],
                                 'preserve-existing-declaration')
                self.assertNotIn('declaration', self.rows[row_id])
                self.assertEqual(asdict(self.keymap_utils.capture_scope(keymap)), binding['scope'])
                self.assertEqual(asdict(self.keymap_utils.capture_event(item)),
                                 {**binding['event'], correction['field']: correction['after']})
                self.assertEqual(item.idname, binding['target'])
                self.assertEqual(dict(item.properties), binding['properties'])
                self.assertEqual(item.active, binding['active'])

                self.selection_tool_set.reset_mock()
                self.assertEqual(action.operator().execute(self.runtime.bpy.context), {'FINISHED'})
                self.assertEqual(self.selection_tool_set.call_args.args, ('builtin.select_box',))

        setattr(self.preferences.keymap.selection, group['preference'], False)
        self.assertEqual(register.register(), 0)
        self.assertEqual(self.addon_rows(), [])

    def test_uv_all_none_matches_reviewed_aliases_and_has_independent_controls(self):
        register = self.load_selection_register()
        selection = self.load('actions.actions.keymaps.selection')
        all_none = self.load('actions.actions.keymaps.selection.selection_all_none')
        more_less = self.load('actions.actions.keymaps.selection.selection_more_less')
        tool_switch = self.load('actions.actions.keymaps.selection.selection_tool_switch')
        self.stub('.blenderUtils.operatorUtils', op_exists=lambda _idname: True)
        preference_ui = self.load('preferences.addon.keymaps.keymap_props_selection')
        definitions = preference_ui.SelectionKeymapPG.__annotations__
        feature = self.manifest['reviewed_declarations'][SELECTION_ALL_NONE]
        preference = feature['preference']
        selection_prefs = types.SimpleNamespace(**{
            name: definition['default'] for name, definition in definitions.items()
        })
        self.preferences.keymap.selection = selection_prefs
        self.assertTrue(getattr(selection_prefs, preference))
        self.assertIn('ALL_NONE', {entry[0] for entry in
                                  definitions['active_selection_keymap_tab']['items']})
        selection_prefs.enable_selection_circle = False
        selection_prefs.enable_selection_subtract = False
        selection_prefs.enable_selection_extend = False
        self.assertEqual(register.register(), 0)

        actions = [getattr(all_none, symbol) for symbol in feature['actions']]
        self.assertEqual(getattr(all_none, feature['get_actions'])(), actions)
        self.assertTrue(all(action in selection.get_all_selection_actions()
                            for action in actions))
        self.preferences.keymap.enable_keymaps = True
        previous_groups = [*more_less.get_selection_more_less_actions(),
                           *tool_switch.get_selection_tool_switch_actions()]
        self.assertCountEqual(register.get_enabled_selection_actions(),
                              [*previous_groups, *actions])
        setattr(selection_prefs, preference, False)
        self.assertEqual(register.get_enabled_selection_actions(), previous_groups)

        setattr(selection_prefs, preference, True)
        selection_prefs.enable_selection_more_less = False
        selection_prefs.enable_selection_tool_switch = False
        self.assertEqual(register.get_enabled_selection_actions(), actions)
        self.assertEqual(register.register(), 4)
        actual = iter(register.registered_selection_keymaps)
        for action, row_ids in zip(actions, feature['actions'].values(), strict=True):
            self.assertEqual(len(action.keymap_bindings), len(row_ids))
            for row_id in row_ids:
                with self.subTest(row_id=row_id):
                    accepted = self.ledger[row_id]
                    self.assertFalse(accepted['presence'].get('stock'))
                    self.assertFalse(self.rows[row_id]['provider_inherited'])
                    binding = accepted['binding']
                    keymap, item = next(actual)
                    self.assertEqual(asdict(self.keymap_utils.capture_scope(keymap)),
                                     binding['scope'])
                    self.assertEqual(asdict(self.keymap_utils.capture_event(item)),
                                     binding['event'])
                    self.assertEqual(item.idname, binding['target'])
                    self.assertEqual(dict(item.properties), binding['properties'])
                    self.assertEqual(item.active, binding['active'])
        self.assertIsNone(next(actual, None))

        setattr(selection_prefs, preference, False)
        self.assertEqual(register.register(), 0)
        self.assertEqual(self.addon_rows(), [])
        setattr(selection_prefs, preference, True)

        selection_prefs.active_selection_keymap_tab = 'ALL_NONE'
        layout = Mock()
        preference_ui.draw(self.preferences, self.runtime.bpy.context, layout)
        self.draw_feature.assert_called_once_with(
            column=layout.column.return_value,
            feature_owner=selection_prefs,
            feature_prop_name=preference,
            actions=actions,
        )
        selection_prefs.enable_selection_keymaps = False
        self.assertEqual(register.register(), 0)
        self.assertEqual(self.addon_rows(), [])
        selection_prefs.enable_selection_keymaps = True
        self.assertEqual(register.register(), 4)
        self.preferences.keymap.enable_keymaps = False
        self.assertEqual(register.register(), 0)
        self.assertEqual(self.addon_rows(), [])

    def test_uv_brackets_extend_more_less_and_preserve_all_wheel_bindings(self):
        register = self.load_selection_register()
        more_less = self.load('actions.actions.keymaps.selection.selection_more_less')
        self.preferences.keymap.enable_keymaps = True
        self.preferences.keymap.selection = types.SimpleNamespace(
            enable_selection_keymaps=True,
            enable_selection_all_none=False,
            enable_selection_circle=False,
            enable_selection_subtract=False, enable_selection_extend=False,
            enable_selection_more_less=True,
            enable_selection_tool_switch=False,
        )
        existing = [
            self.ledger[row_id]['binding']
            for row_id, review in self.rows.items()
            if any(overlap[0] == 'selection_more_less'
                   for overlap in review['evidence'].get('static_source_overlap', ()))
        ]
        self.assertEqual(len(existing), 52)
        extensions = self.manifest['reviewed_existing_declarations'][UV_BRACKETS]['bindings']
        self.assertEqual(set(extensions), {'SELECTION_UV_SELECT_MORE', 'SELECTION_UV_SELECT_LESS'})
        self.assertEqual(register.register(), 59)
        draft_entries = self.manifest['ordinary_source_drafts']['groups']['selection_more_less']
        draft_bindings = {
            (id(getattr(more_less, symbol)), int(index))
            for symbol, bindings in draft_entries['actions'].items() for index in bindings
        }
        actual = register.registered_selection_keymaps
        next_index = 0
        for action in more_less.get_selection_more_less_actions():
            for index, _ in enumerate(action.keymap_bindings):
                keymap, item = actual[next_index]
                next_index += 1
                if ((id(action), index) in draft_bindings
                        or action in (more_less.SELECTION_EDITOR_SELECT_MORE,
                                      more_less.SELECTION_EDITOR_SELECT_LESS)):
                    continue
                emitted = {
                    'scope': asdict(self.keymap_utils.capture_scope(keymap)),
                    'event': asdict(self.keymap_utils.capture_event(item)),
                    'target': item.idname,
                    'properties': dict(item.properties),
                    'active': item.active,
                    'read_issues': {},
                }
                with self.subTest(action=item.idname, index=index, key=item.type):
                    if item.type in ('LEFT_BRACKET', 'RIGHT_BRACKET'):
                        symbol, = (symbol for symbol in extensions
                                   if getattr(more_less, symbol) is action)
                        extension = extensions[symbol]
                        self.assertEqual(index, extension['binding_index'])
                        self.assertEqual(index, 2)
                        self.assertEqual(emitted, self.ledger[extension['row_id']]['binding'])
                    else:
                        wheel_index = {
                            'WHEELUPMOUSE': 0, 'WHEELDOWNMOUSE': 0,
                            'WHEELLEFTMOUSE': 1, 'WHEELRIGHTMOUSE': 1,
                        }
                        self.assertEqual(index, wheel_index[item.type])
                        self.assertIn(emitted, existing)
                        existing.remove(emitted)
        self.assertEqual(next_index, len(actual))
        self.assertEqual(existing, [])

    def test_selection_circle_registers_only_the_four_reviewed_bindings(self):
        register = self.load_selection_register()
        selection = self.load('actions.actions.keymaps.selection')
        circle = self.load('actions.actions.keymaps.selection.selection_circle')
        self.stub('.blenderUtils.operatorUtils', op_exists=lambda _idname: True)
        preference_ui = self.load('preferences.addon.keymaps.keymap_props_selection')
        definitions = preference_ui.SelectionKeymapPG.__annotations__
        feature = self.manifest['reviewed_declarations'][SELECTION_CIRCLE]
        preference = feature['preference']
        selection_prefs = types.SimpleNamespace(**{
            name: definition['default'] for name, definition in definitions.items()
        })
        self.preferences.keymap.selection = selection_prefs
        self.assertTrue(getattr(selection_prefs, preference))
        self.assertIn('CIRCLE', {entry[0] for entry in
                                definitions['active_selection_keymap_tab']['items']})
        selection_prefs.enable_selection_subtract = False
        selection_prefs.enable_selection_extend = False
        self.assertEqual(register.register(), 0)

        actions = [getattr(circle, symbol) for symbol in feature['actions']]
        self.assertEqual(getattr(circle, feature['get_actions'])(), actions)
        self.assertTrue(all(action in selection.get_all_selection_actions() for action in actions))
        self.preferences.keymap.enable_keymaps = True
        enabled = register.get_enabled_selection_actions()
        for action in actions:
            self.assertIn(action, enabled)
        setattr(selection_prefs, preference, False)
        previous_groups = register.get_enabled_selection_actions()
        self.assertEqual(previous_groups, [action for action in enabled if action not in actions])
        previous_count = register.register()
        self.assertGreater(previous_count, 0)
        setattr(selection_prefs, preference, True)
        self.assertEqual(register.register(), previous_count + 4)
        setattr(selection_prefs, preference, False)
        self.assertEqual(register.register(), previous_count)

        selection_prefs.enable_selection_all_none = False
        selection_prefs.enable_selection_more_less = False
        selection_prefs.enable_selection_tool_switch = False
        setattr(selection_prefs, preference, True)
        self.assertEqual(register.get_enabled_selection_actions(), actions)
        self.assertEqual(register.register(), 4)
        row_ids = [row_id for ids in feature['actions'].values() for row_id in ids]
        for row_id, pair in zip(row_ids, register.registered_selection_keymaps, strict=True):
            with self.subTest(row_id=row_id):
                binding = self.ledger[row_id]['binding']
                self.assert_registered_binding(pair, binding)
                self.assertEqual(dict(pair[1].properties), binding['properties'])

        selection_prefs.active_selection_keymap_tab = 'CIRCLE'
        layout = Mock()
        preference_ui.draw(self.preferences, self.runtime.bpy.context, layout)
        self.draw_feature.assert_called_once_with(
            column=layout.column.return_value, feature_owner=selection_prefs,
            feature_prop_name=preference, actions=actions,
        )
        self.preferences.keymap.enable_keymaps = False
        self.assertEqual(register.register(), 0)
        self.assertEqual(self.addon_rows(), [])

    def test_editor_guard_rows_use_only_exact_vertical_inputs_and_existing_toggle(self):
        register = self.load_selection_register()
        self.preferences.keymap.enable_keymaps = True
        self.preferences.keymap.selection = types.SimpleNamespace(
            enable_selection_keymaps=True, enable_selection_all_none=False,
            enable_selection_circle=False, enable_selection_subtract=False, enable_selection_extend=False,
            enable_selection_more_less=True,
            enable_selection_tool_switch=False)
        self.assertEqual(register.register(), 59)
        rows = [(km, item) for km, item in register.registered_selection_keymaps
                if item.idname.startswith('wm.bh_editor_select_')]
        self.assertEqual(len(rows), 2)
        for (keymap, item), direction, suffix in zip(rows, ('UP', 'DOWN'), ('more', 'less'), strict=True):
            self.assertEqual(asdict(self.keymap_utils.capture_scope(keymap)),
                             asdict(self.keymap_utils.KeymapScope('View2D', 'EMPTY', 'WINDOW')))
            self.assertEqual(asdict(self.keymap_utils.capture_event(item)),
                             asdict(self.keymap_utils.KeymapEvent('WHEEL' + direction + 'MOUSE',
                                                                 shift=True, map_type='MOUSE')))
            self.assertEqual(item.idname, 'wm.bh_editor_select_' + suffix)
            self.assertEqual(dict(item.properties), {})
        self.preferences.keymap.selection.enable_selection_more_less = False
        self.assertEqual(register.register(), 0)
        self.assertEqual(self.addon_rows(), [])

    def test_editor_guards_respect_exact_context_and_underlying_poll(self):
        self.stub('.operators', path='operators')
        self.runtime.bpy.types.Operator = type('Operator', (), {})
        operators = {}
        for namespace, names in {
            'action': ('select_more', 'select_less'), 'graph': ('select_more', 'select_less'),
            'node': ('select_linked_to', 'select_linked_from'),
            'sequencer': ('select_more', 'select_less'),
        }.items():
            for name in names:
                operator = Mock(return_value={'FINISHED'})
                operator.poll = Mock(return_value=True)
                operators[namespace + '.' + name] = operator
        self.runtime.bpy.ops = types.SimpleNamespace(**{
            namespace: types.SimpleNamespace(**{name.split('.')[1]: operator
                                                for name, operator in operators.items()
                                                if name.startswith(namespace + '.')})
            for namespace in ('action', 'graph', 'node', 'sequencer')})
        module = self.load('operators.selection_more_less_ops')

        def context(area_type, *, mode='DOPESHEET', ui_type='', tree=None,
                    view_type='SEQUENCER', region='WINDOW'):
            area = types.SimpleNamespace(type=area_type, ui_type=ui_type,
                                         spaces=types.SimpleNamespace(active=types.SimpleNamespace(
                                             mode=mode, edit_tree=tree, view_type=view_type)))
            return types.SimpleNamespace(area=area, region=types.SimpleNamespace(type=region))

        accepted = [
            (context('DOPESHEET_EDITOR'), ('action.select_more', 'action.select_less')),
            (context('GRAPH_EDITOR', mode='FCURVES'), ('graph.select_more', 'graph.select_less')),
            (context('NODE_EDITOR', ui_type='CompositorNodeTree', tree=object()),
             ('node.select_linked_to', 'node.select_linked_from')),
            (context('SEQUENCE_EDITOR'), ('sequencer.select_more', 'sequencer.select_less')),
        ]
        for ctx, targets in accepted:
            for cls, target in zip(module.classes[:2], targets, strict=True):
                with self.subTest(context=ctx.area.type, operator=cls.bl_idname):
                    for operator in operators.values():
                        operator.reset_mock()
                        operator.poll.return_value = True
                    self.assertTrue(cls.poll(ctx))
                    self.assertEqual(cls().execute(ctx), {'FINISHED'})
                    operators[target].assert_called_once_with('EXEC_DEFAULT')
                    self.assertEqual(sum(operator.call_count for operator in operators.values()), 1)
                    operators[target].reset_mock()
                    operators[target].poll.return_value = False
                    self.assertFalse(cls.poll(ctx))
                    self.assertEqual(cls().execute(ctx), {'PASS_THROUGH'})
                    operators[target].assert_not_called()

        excluded = [context(name) for name in ('IMAGE_EDITOR', 'NLA_EDITOR', 'FILE_BROWSER', 'VIEW_3D')]
        excluded.extend((context('DOPESHEET_EDITOR', mode='TIMELINE'),
                         context('GRAPH_EDITOR', mode='DRIVERS'),
                         context('NODE_EDITOR', ui_type='ShaderNodeTree', tree=object()),
                         context('NODE_EDITOR', ui_type='CompositorNodeTree'),
                         context('SEQUENCE_EDITOR', view_type='PREVIEW'),
                         context('DOPESHEET_EDITOR', region='HEADER'),
                         types.SimpleNamespace(area=None, region=None)))
        for operator in operators.values():
            operator.reset_mock()
        for ctx in excluded:
            for cls in module.classes:
                self.assertFalse(cls.poll(ctx))
                self.assertEqual(cls().execute(ctx), {'PASS_THROUGH'})
        for operator in operators.values():
            operator.assert_not_called()
            operator.poll.assert_not_called()

    def test_uv_arrow_guards_preserve_other_contexts_and_underlying_poll(self):
        self.stub('.operators', path='operators')
        self.runtime.bpy.types.Operator = type('Operator', (), {})
        more, less = Mock(return_value={'FINISHED'}), Mock(return_value={'FINISHED'})
        more.poll, less.poll = Mock(return_value=True), Mock(return_value=True)
        self.runtime.bpy.ops = types.SimpleNamespace(uv=types.SimpleNamespace(select_more=more, select_less=less))
        module = self.load('operators.selection_more_less_ops')
        accepted = types.SimpleNamespace(area=types.SimpleNamespace(type='IMAGE_EDITOR', ui_type='UV'),
                                         region=types.SimpleNamespace(type='WINDOW'))
        for cls, operator in zip(module.classes[2:], (more, less), strict=True):
            self.assertTrue(cls.poll(accepted))
            self.assertEqual(cls().execute(accepted), {'FINISHED'})
            operator.assert_called_once_with('EXEC_DEFAULT')
            operator.reset_mock()
            operator.poll.return_value = False
            self.assertFalse(cls.poll(accepted))
            self.assertEqual(cls().execute(accepted), {'PASS_THROUGH'})
            operator.assert_not_called()
            operator.poll.return_value = True
        for area_type, ui_type, region in (('VIEW_3D', 'VIEW_3D', 'WINDOW'),
                                           ('IMAGE_EDITOR', 'IMAGE_EDITOR', 'WINDOW'),
                                           ('IMAGE_EDITOR', 'UV', 'HEADER'),
                                           ('DOPESHEET_EDITOR', 'DOPESHEET', 'WINDOW')):
            ctx = types.SimpleNamespace(area=types.SimpleNamespace(type=area_type, ui_type=ui_type),
                                        region=types.SimpleNamespace(type=region))
            for cls in module.classes[2:]:
                self.assertFalse(cls.poll(ctx))
                self.assertEqual(cls().execute(ctx), {'PASS_THROUGH'})

    def load_transform_register(self):
        self.stub('.operators', path='operators')
        self.stub('.operators.transform_ops', **{
            f'WM_OT_BH_{operator.title()}AutoConstraint': type('AutoConstraint', (), {
                'bl_idname': f'wm.bh_{operator}_auto_constraint',
            })
            for operator in ('translate', 'rotate', 'resize')
        })
        register = self.load('keymaps.transform_keymaps_register')
        self.keymap_utils.bind_category_pairs(register.KEYMAP_CATEGORY,
                                              register.registered_transform_keymaps)
        self.addCleanup(register.unregister)
        return register

    def test_existing_gizmo_switches_emit_into_native_mode_map_scopes(self):
        register = self.load_transform_register()
        gizmo = self.load('actions.actions.keymaps.transform.transform_tools_gizmo')
        self.preferences.keymap.enable_keymaps = True
        self.preferences.keymap.transform = types.SimpleNamespace(
            enable_transform_keymaps=True,
            enable_transform_tools_gizmo=True,
            enable_transform_tools_modal=False,
            enable_transform_action_shortcuts=False,
        )
        modes = {
            'Armature', 'Curve', 'Curves', 'Grease Pencil Edit Mode', 'Lattice',
            'Mesh', 'Metaball', 'Object Mode', 'Pose', 'UV Editor',
        }
        for mode in modes:
            self.runtime.map('default', mode, space='EMPTY')
        self.assertEqual(register.register(), 34)

        owned = {}
        for keymap, item in register.registered_transform_keymaps[:30]:
            scope = self.keymap_utils.capture_scope(keymap)
            self.assertEqual((scope.space_type, scope.region_type, scope.is_modal),
                             ('EMPTY', 'WINDOW', False))
            key = (scope.name, item.type)
            self.assertNotIn(key, owned)
            owned[key] = (scope, item)
        self.assertEqual(set(owned), {(mode, key) for mode in modes for key in 'WER'})

        group = self.manifest['reviewed_existing_declarations']['transform_tools_gizmo']
        self.assertTrue((ROOT / group['source']).is_file())
        templates = {}
        for symbol, row_id in group['accepted_full_user_rows'].items():
            with self.subTest(row_id=row_id):
                accepted = self.ledger[row_id]
                review = self.rows[row_id]
                self.assertGreater(accepted['presence']['full']['user'], 0)
                self.assertEqual(review['runtime_disposition'], 'preserve-existing-declaration')
                self.assertNotIn('declaration', review)
                binding = accepted['binding']
                scope, item = owned[binding['scope']['name'], binding['event']['type']]
                self.assertEqual(asdict(scope), binding['scope'])
                self.assertEqual(asdict(self.keymap_utils.capture_event(item)), binding['event'])
                self.assertEqual(item.idname, binding['target'])
                self.assertEqual(dict(item.properties), binding['properties'])
                action = getattr(gizmo, symbol)
                self.assertIn(action, register.get_enabled_transform_actions())
                self.assertEqual(action.get_props()['name'], binding['properties']['name'])
                templates[item.type] = binding
        for (mode, key), (_, item) in owned.items():
            with self.subTest(mode=mode, key=key):
                template = templates[key]
                self.assertEqual(asdict(self.keymap_utils.capture_event(item)), template['event'])
                self.assertEqual(item.idname, template['target'])
                self.assertEqual(dict(item.properties), template['properties'])

    def test_uv_repeat_production_toggle_preserves_modal_gizmo_and_stock(self):
        for path, expected in self.manifest['uv_repeat_route']['source_sha256'].items():
            self.assertEqual(sha256((ROOT / path).read_bytes()).hexdigest(), expected)
        register = self.load_transform_register()
        module = self.load('actions.actions.keymaps.transform.transform_tools_modal')
        aggregate = self.load('actions.actions.keymaps.transform')
        action, = module.get_transform_action_shortcuts()
        self.assertIn(action, aggregate.get_all_transform_actions())
        self.preferences.keymap.enable_keymaps = True
        prefs = types.SimpleNamespace(
            enable_transform_keymaps=True, enable_transform_tools_gizmo=True,
            enable_transform_tools_modal=True, enable_transform_action_shortcuts=False,
            active_transform_keymap_tab='ACTIONS')
        self.preferences.keymap.transform = prefs
        stock = self.runtime.map('default', 'UV Editor', space='EMPTY')
        stock_g = row('transform.translate', key='G')
        stock.keymap_items.append_fixture(stock_g)
        existing = register.get_enabled_transform_actions()
        count = register.register()
        self.assertGreater(count, 0)
        prefs.enable_transform_action_shortcuts = True
        self.assertEqual(register.get_enabled_transform_actions(), [*existing, action])
        self.assertEqual(register.register(), count + 1)
        keymap, item = register.registered_transform_keymaps[-1]
        self.assertEqual((keymap.name, keymap.space_type, keymap.region_type),
                         ('UV Editor', 'EMPTY', 'WINDOW'))
        self.assertEqual((item.idname, item.type, item.value, item.repeat, item.active),
                         ('screen.repeat_last', 'G', 'PRESS', True, True))
        self.assertFalse(any((item.shift, item.ctrl, item.alt, item.oskey, item.any)))
        self.assertEqual(dict(item.properties), {})
        owners = [handle for handle in self.keymap_utils._FEATURES.values()
                  if any(request.target.idname == 'screen.repeat_last'
                         for request in handle.assignments)]
        self.assertEqual(len(owners), 1)
        self.assertTrue(owners[0].owner_id.startswith('legacy:Transform:'))
        self.assertEqual(owners[0].assignments[0].request_id, '0:UV Editor:G:PRESS')
        prefs.enable_transform_action_shortcuts = False
        self.assertEqual(register.register(), count)
        self.assertEqual(register.get_enabled_transform_actions(), existing)
        self.assertEqual(list(stock.keymap_items), [stock_g])
        self.assertTrue(stock_g.active)
        prefs.enable_transform_action_shortcuts = True
        self.assertEqual(register.register(), count + 1)
        ui = self.load('preferences.addon.keymaps.keymap_props_transform')
        layout = Mock()
        ui.draw(self.preferences, self.runtime.bpy.context, layout)
        self.draw_feature.assert_called_once_with(
            column=layout.column.return_value, feature_owner=prefs,
            feature_prop_name='enable_transform_action_shortcuts', actions=[action])

    def test_direct_fixture_enum_flags_match_accepted_runtime_conversion(self):
        from blender_keymap_category03_ordinary import native_control_properties
        flag = types.SimpleNamespace(
            identifier='snap_elements', type='ENUM', is_enum_flag=True,
            enum_items=[types.SimpleNamespace(identifier=value) for value in ('', 'INCREMENT', 'VERTEX')])
        scalar = types.SimpleNamespace(identifier='action', type='ENUM', is_enum_flag=False)
        schema = types.SimpleNamespace(properties=[flag, scalar])
        operator = types.SimpleNamespace(get_rna_type=lambda: schema)
        properties = {'snap_elements': ['INCREMENT'], 'action': 'SELECT', 'value': [0.125, 0.0625, 0.0]}
        converted = native_control_properties(operator, properties)
        native = types.SimpleNamespace(properties=types.SimpleNamespace(bl_rna=schema))
        self.keymap_utils._set_property(native, 'snap_elements', ('INCREMENT',))
        self.assertEqual(converted['snap_elements'], native.properties.snap_elements)
        self.assertEqual(converted['action'], 'SELECT')
        self.assertEqual(converted['value'], properties['value'])
        self.assertEqual(properties['snap_elements'], ['INCREMENT'])
        for flags in (['UNKNOWN'], ['INCREMENT', 'INCREMENT'], ['VERTEX', 'INCREMENT'], 'INCREMENT'):
            with self.assertRaises(ValueError):
                native_control_properties(operator, {'snap_elements': flags})

    def test_shared_persistence_selectors_match_exact_production_declarations(self):
        from blender_keymap_category03_persistence import PersistenceCases
        self.load_selection_register()
        circle = self.load('actions.actions.keymaps.selection.selection_circle')
        more_less = self.load('actions.actions.keymaps.selection.selection_more_less')
        actions = [*self.framing_actions(), *circle.get_selection_circle_actions(),
                   *more_less.get_selection_more_less_actions()]
        for editor_only, uv_arrow_only in ((False, False), (True, False), (False, True)):
            helper = PersistenceCases(
                bpy=None, configs=None, runtime=None, categories=None, preferences=None,
                fixture=None, root=ROOT, record=None, receipt={}, set_groups=None,
                production_paths=(), package='fixture', editor_only=editor_only, uv_arrow_only=uv_arrow_only)
            self.assertEqual(len(helper.specs), 1 if editor_only or uv_arrow_only else 2)
            for spec in helper.specs:
                matches = [(action, binding) for action in actions
                           if action.get_idname() == spec['target']
                           for binding in action.keymap_bindings
                           if (binding.keymap_name, binding.space_type, binding.region_type,
                               binding.key, binding.shift) ==
                           (spec['scope'], spec['space'], 'WINDOW', spec['key'], spec['shift'])
                           and not any((binding.ctrl, binding.alt, binding.oskey, binding.any))]
                self.assertEqual(len(matches), 1, spec['name'])
                if spec['name'] == 'circle':
                    self.assertEqual(matches[0][0].get_props()['radius'], 25)
                    self.assertEqual(spec['edited_radius'], 31)

    def test_native_preview_input_uses_visible_region_and_rejects_hidden_coordinates(self):
        from blender_keymap_category03_editors import EditorCases
        hidden = types.SimpleNamespace(type='WINDOW', x=0, y=0, width=0, height=0)
        preview = types.SimpleNamespace(type='PREVIEW', x=10, y=20, width=800, height=600)
        fixture = EditorCases.__new__(EditorCases)
        fixture.area = types.SimpleNamespace(type='SEQUENCE_EDITOR', regions=[hidden, preview],
                                            spaces=types.SimpleNamespace(active=types.SimpleNamespace(view_type='PREVIEW')))
        self.assertEqual(fixture.point(), (410, 320))
        self.assertIs(fixture.region(visible=True), preview)
        preview.width = 0
        with self.assertRaises(StopIteration):
            fixture.point()

    def test_ordinary_drafts_emit_the_21_reviewed_bindings_under_existing_controls(self):
        draft = self.manifest['ordinary_source_drafts']
        self.assertEqual(draft['status'], 'partial-mechanism-accepted')
        selection = self.load_selection_register()
        transform = self.load_transform_register()
        categories = {
            'navigation': (self.register, self.register.get_enabled_navigation_actions,
                           self.navigation_prefs, self.navigation.get_all_navigation_actions()),
            'selection': (selection, selection.get_enabled_selection_actions,
                          types.SimpleNamespace(enable_selection_keymaps=True,
                                                enable_selection_all_none=False,
                                                enable_selection_circle=False,
                                                enable_selection_subtract=False, enable_selection_extend=False),
                          self.load('actions.actions.keymaps.selection').get_all_selection_actions()),
            'transform': (transform, transform.get_enabled_transform_actions,
                          types.SimpleNamespace(enable_transform_keymaps=True,
                                                enable_transform_action_shortcuts=False),
                          self.load('actions.actions.keymaps.transform').get_all_transform_actions()),
        }
        self.preferences.keymap.enable_keymaps = True
        for category, (_, _, prefs, _) in categories.items():
            setattr(self.preferences.keymap, category, prefs)
        for group, info in draft['groups'].items():
            category = group.split('_', 1)[0]
            setattr(categories[category][2], info['preference'], False)

        draft_ids = []
        for group, info in draft['groups'].items():
            with self.subTest(group=group):
                category = group.split('_', 1)[0]
                register, enabled_actions, prefs, aggregate = categories[category]
                pairs = getattr(register, f'registered_{category}_keymaps')
                source = ROOT / info['source']
                self.assertEqual(sha256(source.read_bytes()).hexdigest(), info['source_sha256'])
                module = self.load('.'.join(Path(info['source']).with_suffix('').parts))
                actions = self.draft_actions(group, module)
                setattr(prefs, info['preference'], True)
                try:
                    enabled = enabled_actions()
                    offsets = {}
                    emitted_count = 0
                    for action in enabled:
                        offsets[id(action)] = emitted_count
                        emitted_count += len(action.keymap_bindings)
                    self.assertEqual(register.register(), emitted_count)
                    for symbol, bindings in info['actions'].items():
                        action = actions[symbol]
                        self.assertIn(id(action), offsets)
                        # This aggregate historically omits Tool Switch. Its
                        # public feature getter and register both expose it.
                        if group == 'selection_tool_switch':
                            self.assertIn(action, module.get_selection_tool_switch_actions())
                        else:
                            self.assertIn(action, aggregate)
                        for index, row_id in bindings.items():
                            with self.subTest(row_id=row_id):
                                draft_ids.append(row_id)
                                review = self.rows[row_id]
                                self.assertEqual(review['runtime_disposition'],
                                                 'review-full-side-candidate')
                                if row_id in draft['accepted_row_ids']:
                                    self.assertEqual(review['declaration'],
                                                     self.manifest['accepted_mechanism_reuse']['bindings'][row_id])
                                else:
                                    self.assertNotIn('declaration', review)
                                self.assertNotIn('authorized_transfer', review)
                                binding = self.ledger[row_id]['binding']
                                if row_id in self.manifest.get('handler_adaptations', {}):
                                    adaptation = self.manifest['handler_adaptations'][row_id]
                                    self.assertEqual(adaptation['reference_binding'], binding)
                                    binding = adaptation['runtime_binding']
                                    self.assertEqual(binding['event'], adaptation['reference_binding']['event'])
                                    self.assertEqual(binding['scope']['name'], 'Frames')
                                    self.assertIn(binding['target'], ('wm.bh_uv_select_more', 'wm.bh_uv_select_less'))
                                pair = pairs[offsets[id(action)] + int(index)]
                                self.assert_registered_binding(pair, binding)
                                expected = binding['properties']
                                declared = action.get_props()
                                self.assertEqual(declared,
                                                 {key: expected[key] for key in declared})
                                emitted = dict(pair[1].properties)
                                self.assertEqual(emitted,
                                                 {key: expected[key] for key in emitted})
                                self.assertEqual(declared, {key: emitted[key] for key in declared})
                finally:
                    setattr(prefs, info['preference'], False)
                    self.assertEqual(register.register(), 0)
                    self.assertEqual(self.addon_rows(), [])
        self.assertEqual(len(draft_ids), 21)
        self.assertEqual(len(set(draft_ids)), 21)


if __name__ == '__main__':
    unittest.main()
