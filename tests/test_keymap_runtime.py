"""Behavioral contract for reversible, session-owned Deluxe keymaps.

This suite runs without Blender.  Native dispatch and persistence evidence lives
in the bounded Blender receipts; these cases exercise ownership and recovery.
"""

import importlib.util
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import types
import unittest
from unittest.mock import patch

from runtime_keymap_fakes import FakeConfig, FakeProperties, FakeRuntime, MergedMaps, ReusedIdWrapper, row


ROOT = Path(__file__).resolve().parents[1]


class RuntimeKeymapTests(unittest.TestCase):
    def setUp(self):
        self.runtime = FakeRuntime()
        self.modules = set(sys.modules)
        prefix = '_bluehole_runtime_' + self.id().rsplit('.', 1)[-1]
        self.prefix = prefix
        for name, path in ((prefix, ROOT), (prefix + '.keymaps', ROOT / 'keymaps')):
            package = types.ModuleType(name)
            package.__path__ = [str(path)]
            sys.modules[name] = package
        name = prefix + '.keymaps.keymap_utils'
        spec = importlib.util.spec_from_file_location(name, ROOT / 'keymaps/keymap_utils.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        with patch.dict(sys.modules, {'bpy': self.runtime.bpy}):
            spec.loader.exec_module(module)
        self.utils = module
        self.addCleanup(lambda: [sys.modules.pop(name, None) for name in tuple(sys.modules)
                         if name not in self.modules and name.startswith(prefix)])
        self.bpy_patch = patch.dict(sys.modules, {'bpy': self.runtime.bpy})
        self.bpy_patch.start()
        self.addCleanup(self.bpy_patch.stop)

    def scope(self, **changes):
        values = dict(name='3D View', space_type='VIEW_3D', region_type='WINDOW',
                      is_modal=False, is_tool=False)
        values.update(changes)
        return self.utils.KeymapScope(**values)

    def event(self, **changes):
        values = dict(type='A', value='PRESS')
        values.update(changes)
        return self.utils.KeymapEvent(**values)

    def native_modal_event(self, **changes):
        values = dict(type='LEFT_SHIFT', value='ANY', any=True, shift=-1,
                      ctrl=-1, alt=-1, oskey=-1, hyper=-1,
                      key_modifier='NONE', direction='ANY', repeat=False,
                      map_type='KEYBOARD')
        values.update(changes)
        return self.utils.KeymapEvent(**values)

    def native_modal_row(self, token='PRECISION', *, key='LEFT_SHIFT', **changes):
        event = self.native_modal_event(type=key, **changes)
        return row('', key=event.type, value=event.value, any=event.any,
                   shift=event.shift, ctrl=event.ctrl, alt=event.alt,
                   oskey=event.oskey, hyper=event.hyper,
                   key_modifier=event.key_modifier, direction=event.direction,
                   repeat=event.repeat, map_type=event.map_type,
                   modal_value=token)

    def target(self, name='object.select_all', **properties):
        return self.utils.KeymapTarget(idname=name,
                                       properties=tuple(sorted(properties.items())))

    def selector(self, *, scope=None, event=None, target=None, role='default'):
        return self.utils.KeymapSelector(scope or self.scope(), event or self.event(),
                                         target or self.target(), source_role=role,
                                         ledger_id='ledger-stock-a', sample_id='sample-a')

    def assignment(self, request_id='replacement', *, event=None, target=None,
                   scope=None):
        return self.utils.KeymapAssignment(request_id, scope or self.scope(),
                                           event or self.event(),
                                           target or self.target('bluehole.replacement'))

    def override(self, request_id='override', *, selector=None,
                 assignment=None, capability='ordinary_tail',
                 context='synthetic_ordinary_provider'):
        return self.utils.KeymapOverride(request_id, selector or self.selector(),
                                         assignment or self.assignment(),
                                         capability=capability, context=context)

    def source(self, *rows):
        map_ = self.runtime.map('default', tool=False)
        for item in rows:
            map_.keymap_items.append_fixture(item)
        return map_

    def addon(self, *rows):
        map_ = self.runtime.map('addon', tool=False)
        for item in rows:
            map_.keymap_items.append_fixture(item)
        return map_

    def merged_names(self):
        return [item.idname for item in self.runtime.configs.user.keymaps.get('3D View').keymap_items]

    def reasons(self, handle):
        return {diagnostic.reason for diagnostic in handle.diagnostics}

    def numeric_rna_types(self):
        """Minimal stand-ins for the three classes observed in the native probe."""
        class NativeSequence:
            def __init__(self, values):
                self.values = tuple(values)
            def __len__(self):
                return len(self.values)
            def __getitem__(self, index):
                return self.values[index]
            def __iter__(self):
                return iter(self.values)
        class Vector(NativeSequence):
            pass
        class Matrix(NativeSequence):
            def __init__(self, values):
                super().__init__(Vector(v) for v in values)
        class RNAArray(NativeSequence):
            pass
        module = types.ModuleType('mathutils')
        module.Vector, module.Matrix = Vector, Matrix
        replacement = patch.dict(sys.modules, {'mathutils': module})
        replacement.start()
        self.addCleanup(replacement.stop)
        self.runtime.bpy.types = types.SimpleNamespace(bpy_prop_array=RNAArray)
        return Vector, Matrix, RNAArray

    def array_property(self, kind, dimensions, length, name='value'):
        return types.SimpleNamespace(identifier=name, type=kind, is_array=True,
                                     array_dimensions=dimensions, array_length=length)

    def test_native_numeric_arrays_have_exact_immutable_shape_and_scalar_types(self):
        Vector, Matrix, RNAArray = self.numeric_rna_types()
        cases = (
            ('FLOAT', (2, 0, 0), 2, Vector((2.5, -0.0)), (2.5, 0.0)),
            ('FLOAT', (2, 3, 0), 6, Matrix(((1., 2., 3.), (4., 5., 6.))),
             ((1., 2., 3.), (4., 5., 6.))),
            ('BOOLEAN', (3, 0, 0), 3, RNAArray((True, False, True)), (True, False, True)),
            ('INT', (2, 0, 0), 2, RNAArray((2, -3)), (2, -3)),
        )
        for kind, dimensions, length, value, expected in cases:
            with self.subTest(kind=kind, dimensions=dimensions):
                item = row(prop_values={'value': value})
                item.properties.bl_rna.properties = [self.array_property(kind, dimensions, length)]
                self.assertEqual(self.utils._properties(item), (('value', expected),))
                # Descriptors use ordinary tuples; native readback converges on
                # exactly the same signature without broadening generic _freeze.
                self.assertEqual(self.utils._target(item, False), self.target(value=expected))
                with self.assertRaises(ValueError):
                    self.utils._freeze(value)

    def test_numeric_array_shape_or_schema_mismatch_fails_closed(self):
        Vector, Matrix, RNAArray = self.numeric_rna_types()
        cases = (
            ('FLOAT', (3, 0, 0), 3, Vector((1., 2.))),
            ('FLOAT', (2, 2, 0), 4, Matrix(((1., 2.), (3.,)))),
            ('FLOAT', (2, 2, 0), 4, Vector((1., 2., 3., 4.))),
            ('FLOAT', (2, 0, 0), 3, Vector((1., 2.))),
            ('FLOAT', (2, 0, 1), 2, Vector((1., 2.))),
            ('FLOAT', (0, 0, 0), 0, Vector(())),
            ('FLOAT', (-1, 0, 0), -1, Vector(())),
            ('FLOAT', (True, 0, 0), 1, Vector((1.,))),
            ('ENUM', (2, 0, 0), 2, RNAArray(('A', 'B'))),
        )
        for kind, dimensions, length, value in cases:
            with self.subTest(kind=kind, dimensions=dimensions, value=value):
                item = row(prop_values={'value': value})
                item.properties.bl_rna.properties = [self.array_property(kind, dimensions, length)]
                with self.assertRaises(self.utils._Pending):
                    self.utils._properties(item)

    def test_numeric_arrays_reject_nonfinite_wrong_scalar_and_generic_iterables(self):
        Vector, Matrix, RNAArray = self.numeric_rna_types()
        class UnknownIterable:
            def __iter__(self):
                raise AssertionError('Must reject this class without iterating')
        cases = (
            ('FLOAT', Vector((float('nan'), 0.))),
            ('FLOAT', Vector((float('inf'), 0.))),
            ('FLOAT', Vector((1, 2.))),
            ('FLOAT', Vector((True, 2.))),
            ('BOOLEAN', RNAArray((1, False))),
            ('INT', RNAArray((True, 2))),
            ('INT', RNAArray((1., 2))),
            ('FLOAT', [1., 2.]),
            ('FLOAT', (1., 2.)),
            ('FLOAT', UnknownIterable()),
        )
        for kind, value in cases:
            with self.subTest(kind=kind, value=type(value).__name__):
                with self.assertRaises(ValueError):
                    self.utils._freeze_rna_array(self.array_property(kind, (2, 0, 0), 2), value)
        # This array fix does not admit enum-flag sets or pointer collections.
        with self.assertRaises(ValueError):
            self.utils._freeze({'INCREMENT'})
        for kind in ('POINTER', 'COLLECTION'):
            item = row(prop_values={'value': Vector((1., 2.))})
            item.properties.bl_rna.properties = [self.array_property(kind, (2, 0, 0), 2)]
            with self.assertRaises(self.utils._Pending):
                self.utils._properties(item)

    def test_numeric_array_assignment_readback_release_and_failed_shape_rollback(self):
        Vector, _, _ = self.numeric_rna_types()
        source = self.source(row('foreign.inherited'))
        addon = self.addon()
        runtime_test = self
        class PanProperties(FakeProperties):
            def __init__(self):
                super().__init__({'offset': Vector((0., 0.))})
                self.bl_rna.properties = [runtime_test.array_property('FLOAT', (2, 0, 0), 2, 'offset')]
            def __setattr__(self, name, value):
                if name == 'offset':
                    value = Vector(value)
                return super().__setattr__(name, value)
        original_new = addon.keymap_items.new
        def create(*args, **kwargs):
            item = original_new(*args, **kwargs)
            item.properties = PanProperties()
            return item
        with patch.object(addon.keymap_items, 'new', side_effect=create):
            request = self.assignment(target=self.target('image.view_pan', offset=(2.5, -3.25)))
            handle = self.utils.register_feature('array-owner', assignments=(request,))
            self.assertEqual(len(handle.owned_pairs), 1)
            self.assertEqual(self.utils._target(handle.owned_pairs[0][1], False), request.target)
            handle.release()
            self.assertEqual(len(addon.keymap_items), 0)
            self.assertEqual(len(source.keymap_items), 1)
            bad = self.assignment(target=self.target('image.view_pan', offset=(2.5,)))
            failed = self.utils.register_feature('bad-array-owner', assignments=(bad,))
            self.assertFalse(failed.owned_pairs)
            self.assertEqual(len(addon.keymap_items), 0)
            self.assertIn('unreadable_property_schema', self.reasons(failed))
            failed.release()
            self.assertEqual(self.utils.runtime_stats()['tracked_resources'], 0)

    def test_typed_matrix_setter_preserves_rows_without_relaxing_shape_or_types(self):
        _, Matrix, _ = self.numeric_rna_types()
        schema = self.array_property('FLOAT', (2, 2, 0), 4, 'matrix')
        class MatrixProperties(FakeProperties):
            def __setattr__(self, name, value):
                if name == 'matrix':
                    # This mirrors the separately observed native distinction:
                    # tuple input uses columns; typed Matrix input preserves rows.
                    value = value if type(value) is Matrix else Matrix(zip(*value))
                return super().__setattr__(name, value)
        item = row()
        item.properties = MatrixProperties({'matrix': Matrix(((0., 0.), (0., 0.)))})
        item.properties.bl_rna.properties = [schema]
        canonical = ((1., 2.), (3., 4.))
        self.utils._set_property(item, 'matrix', canonical)
        self.assertEqual(self.utils._properties(item), (('matrix', canonical),))
        for invalid in (((1.,), (2.,)), ((1, 2), (3, 4)), ((float('inf'), 2.), (3., 4.)),
                        ((True, 2.), (3., 4.)), ((1., 2.),), (1., 2.)):
            with self.subTest(invalid=invalid), self.assertRaises((ValueError, TypeError)):
                self.utils._set_property(item, 'matrix', invalid)
            self.assertEqual(self.utils._properties(item), (('matrix', canonical),))

    def flag_property(self, *, flag=True, identifiers=('EDGE', 'VERTEX'), name='snap_elements'):
        return types.SimpleNamespace(identifier=name, type='ENUM', is_array=False,
                                     is_enum_flag=flag, enum_items=[
                                         types.SimpleNamespace(identifier=value) for value in identifiers])

    def test_rna_enum_flags_are_sorted_and_empty_flags_preserved(self):
        for value, expected in (({'VERTEX', 'EDGE'}, ('EDGE', 'VERTEX')), (set(), ())):
            item = row(prop_values={'snap_elements': value})
            item.properties.bl_rna.properties = [self.flag_property()]
            self.assertEqual(self.utils._properties(item), (('snap_elements', expected),))
            self.assertEqual(item.properties.snap_elements, value)
        with self.assertRaises(ValueError):
            self.utils._freeze({'VERTEX'})  # Generic descriptors still reject sets.

    def test_rna_enum_flags_reject_unreadable_schema_and_malformed_members(self):
        cases = (
            (self.flag_property(), {'UNKNOWN'}),
            (self.flag_property(), {1}),
            (self.flag_property(), ('VERTEX',)),
            (self.flag_property(), frozenset({'VERTEX'})),
            (self.flag_property(flag=False), {'VERTEX'}),
            (self.flag_property(identifiers=()), set()),
            (self.flag_property(identifiers=(None,)), set()),
            (self.flag_property(identifiers=('',)), set()),
        )
        for schema, value in cases:
            with self.subTest(schema=schema, value=value):
                item = row(prop_values={'snap_elements': value})
                item.properties.bl_rna.properties = [schema]
                with self.assertRaises(self.utils._Pending):
                    self.utils._properties(item)
        missing = self.flag_property()
        del missing.enum_items
        item = row(prop_values={'snap_elements': set()})
        item.properties.bl_rna.properties = [missing]
        with self.assertRaises(self.utils._Pending):
            self.utils._properties(item)

    def test_flag_setter_requires_canonical_tuple_and_uses_schema_specific_set(self):
        item = row(prop_values={'snap_elements': set()})
        item.properties.bl_rna.properties = [self.flag_property()]
        for value in (('EDGE', 'VERTEX'), ()):
            self.utils._set_property(item, 'snap_elements', value)
            self.assertIs(type(item.properties.snap_elements), set)
            self.assertEqual(self.utils._properties(item), (('snap_elements', value),))
        before = item.properties.snap_elements.copy()
        for value in (('VERTEX', 'EDGE'), ('EDGE', 'EDGE'), ('UNKNOWN',), {1}, ['EDGE'], {'EDGE'}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.utils._set_property(item, 'snap_elements', value)
            self.assertEqual(item.properties.snap_elements, before)
        # An ordinary tuple property is not silently converted to a set.
        ordinary = row(prop_values={'offset': (0., 0.)})
        self.utils._set_property(ordinary, 'offset', (1., 2.))
        self.assertIs(type(ordinary.properties.offset), tuple)

    def test_flag_assignment_rollback_and_edited_source_preservation(self):
        source = self.source(row('foreign.inherited'))
        addon = self.addon()
        original_new = addon.keymap_items.new
        def create(*args, **kwargs):
            item = original_new(*args, **kwargs)
            item.properties = FakeProperties({'snap_elements': set()})
            item.properties.bl_rna.properties = [self.flag_property()]
            return item
        with patch.object(addon.keymap_items, 'new', side_effect=create):
            request = self.assignment(target=self.target('transform.translate', snap_elements=('EDGE', 'VERTEX')))
            handle = self.utils.register_feature('flags-owner', assignments=(request,))
            self.assertEqual(len(handle.owned_pairs), 1)
            km, item = handle.owned_pairs[0]
            self.assertEqual(self.utils._target(item, False), request.target)
            count = addon.keymap_items.created
            handle.refresh()
            self.assertEqual(addon.keymap_items.created, count)
            item.properties.snap_elements = {'VERTEX'}
            handle.release()
            self.assertTrue(self.utils.retained_edits())
            self.assertIn(item, tuple(addon.keymap_items))
            km.keymap_items.remove(item)  # Test author removes its intentional retained edit.
            self.assertFalse(self.utils.retained_edits())
            failed = self.utils.register_feature('bad-flags-owner', assignments=(
                self.assignment(target=self.target('transform.translate', snap_elements=('UNKNOWN',))),))
            self.assertFalse(failed.owned_pairs)
            self.assertEqual(len(addon.keymap_items), 0)
            self.assertEqual(len(source.keymap_items), 1)
            failed.release()
            self.assertEqual(self.utils.runtime_stats()['tracked_resources'], 0)

    def test_forward_prepend_priority_and_exact_release(self):
        original = row(prop_values={'action': 'SELECT'})
        foreign = row('other.fallback')
        self.source(original, foreign)
        addon = self.addon(row('other.provider'))
        selector = self.selector(target=self.target(action='SELECT'))
        handle = self.utils.register_feature('owner-a', overrides=(self.override(selector=selector),))
        self.assertEqual((handle.diagnostics[0].ledger_id,
                          handle.diagnostics[0].sample_id,
                          handle.diagnostics[0].observed_role),
                         ('ledger-stock-a', 'sample-a', 'default'))
        self.assertFalse(handle.diagnostics[0].dispatch_evidence)
        self.assertEqual(self.merged_names()[0], 'bluehole.replacement')
        self.assertEqual([item.idname for item in addon.keymap_items],
                         ['other.provider', 'bluehole.replacement'])
        lookalike = row('bluehole.replacement')
        addon.keymap_items.append_fixture(lookalike)
        handle.release()
        handle.release()
        self.assertEqual([item.idname for item in addon.keymap_items],
                         ['other.provider', 'bluehole.replacement'])
        self.assertIs(addon.keymap_items[-1], lookalike)
        self.assertEqual([item.idname for item in self.runtime.configs.default.keymaps.get('3D View').keymap_items],
                         ['object.select_all', 'other.fallback'])
        self.assertTrue(original.active)

    def test_full_scope_event_and_property_selector_blocks_near_matches(self):
        source = self.source(row(prop_values={'action': 'DESELECT'}, shift=True),
                             row(prop_values={'action': 'SELECT'}, ctrl=True))
        self.addon()
        handle = self.utils.register_feature('owner-a', overrides=(
            self.override(selector=self.selector(target=self.target(action='SELECT'),
                                                 event=self.event(shift=True))),))
        self.assertEqual(len(self.runtime.configs.addon.keymaps.get('3D View').keymap_items), 0)
        self.assertEqual(len(source.keymap_items), 2)
        self.assertTrue(self.reasons(handle))
        handle.release()

    def test_every_observable_event_field_is_part_of_selector(self):
        alternatives = dict(type='B', value='RELEASE', any=True, shift=-1,
                            ctrl=True, alt=True, oskey=True, hyper=True,
                            key_modifier='SHIFT', direction='NORTH', repeat=True,
                            map_type='MOUSE')
        for field, changed in alternatives.items():
            with self.subTest(field=field):
                original = row(**({'key': changed} if field == 'type' else {field: changed}))
                source = self.source(original)
                addon = self.addon()
                handle = self.utils.register_feature('owner-' + field,
                    overrides=(self.override(),))
                self.assertEqual(len(addon.keymap_items), 0)
                self.assertIs(source.keymap_items[0], original)
                self.assertTrue(self.reasons(handle))
                handle.release()
                self.runtime.configs.default.keymaps.remove(source)
                self.runtime.configs.addon.keymaps.remove(addon)

    def test_unknown_tool_and_wrong_source_role_fail_closed(self):
        source = self.source(row())
        addon = self.addon()
        cases = (self.selector(scope=self.scope(is_tool=None)),
                 self.selector(role='user'),
                 self.selector(scope=self.scope(space_type='NODE_EDITOR')))
        for index, selector in enumerate(cases):
            handle = self.utils.register_feature('gate-' + str(index),
                overrides=(self.override(selector=selector),))
            self.assertEqual(len(addon.keymap_items), 0)
            self.assertTrue(self.reasons(handle))
            handle.release()
        self.assertEqual(len(source.keymap_items), 1)

    def test_unreadable_schema_and_unknown_modal_token_fail_closed(self):
        original = row(prop_values={'action': 'SELECT'})
        original.properties.bl_rna.properties.append(types.SimpleNamespace(
            identifier='unreadable', type='INT', is_array=False))
        source = self.source(original)
        addon = self.addon()
        handle = self.utils.register_feature('schema-owner', overrides=(
            self.override(selector=self.selector(target=self.target(action='SELECT'))),))
        self.assertEqual(len(addon.keymap_items), 0)
        self.assertTrue(self.reasons(handle))
        handle.release()
        modal = self.runtime.map('default', 'Transform Modal Map', space='EMPTY',
                                 modal=True, tool=False)
        modal.keymap_items.append_fixture(self.native_modal_row('NONE'))
        scope = self.scope(name='Transform Modal Map', space_type='EMPTY', is_modal=True)
        selector = self.selector(scope=scope, event=self.native_modal_event(),
            target=self.utils.KeymapTarget(modal_value='PRECISION'))
        request = self.override(selector=selector,
            assignment=self.assignment(scope=scope, event=self.native_modal_event(),
                target=self.utils.KeymapTarget(modal_value='CANCEL')),
            capability='modal_head', context='transform_translate_precision_cancel')
        handle = self.utils.register_feature('modal-owner', overrides=(request,))
        self.assertEqual(len(modal.keymap_items), 1)
        self.assertEqual(modal.keymap_items[0].propvalue, 'NONE')
        self.assertTrue(self.reasons(handle))
        handle.release()

    def test_unemittable_nondefault_event_field_rolls_back(self):
        for field, value in (('hyper', True), ('map_type', 'MOUSE')):
            with self.subTest(field=field):
                source = self.source(row(**{field: value}))
                addon = self.addon()
                event = self.event(**{field: value})
                request = self.override(selector=self.selector(event=event),
                    assignment=self.assignment(event=event))
                handle = self.utils.register_feature('owner-' + field,
                    overrides=(request,))
                self.assertEqual(len(addon.keymap_items), 0)
                self.assertTrue(self.reasons(handle))
                handle.release()
                self.runtime.configs.default.keymaps.remove(source)
                self.runtime.configs.addon.keymaps.remove(addon)

    def test_active_default_alias_is_one_source(self):
        original = row()
        source = self.source(original)
        addon = self.addon()
        handle = self.utils.register_feature('owner-a', overrides=(self.override(
            selector=self.selector(role='active')),))
        self.assertEqual(len(addon.keymap_items), 1)
        self.assertIs(source.keymap_items[0], original)
        handle.release()
        self.assertEqual(len(addon.keymap_items), 0)

    def test_missing_optional_native_tool_and_hyper_fields_are_unknown_defaults(self):
        original = row()
        del original.hyper
        source = self.source(original)
        addon = self.addon()
        del source.is_tool
        del addon.is_tool
        addon.keymap_items.new_missing_fields.add('hyper')
        self.assertEqual(self.utils.capture_scope(source), self.scope(is_tool=None))
        captured = self.utils.capture_event(original)
        self.assertEqual(captured, self.event(hyper=None))
        handle = self.utils.register_feature('owner-a', overrides=(self.override(
            selector=self.selector(scope=self.scope(is_tool=None), event=captured),
            assignment=self.assignment(scope=self.scope(is_tool=None), event=captured)),))
        self.assertEqual(len(addon.keymap_items), 1)
        self.assertIs(source.keymap_items[0], original)
        handle.release()
        self.assertEqual(len(addon.keymap_items), 0)

    def test_missing_inactive_ambiguous_and_unsupported_fail_closed(self):
        cases = (
            ([], 'ordinary_tail'),
            ([row(active=False)], 'ordinary_tail'),
            ([row(), row()], 'ordinary_tail'),
            ([row()], 'suppress_item'),
        )
        for index, (items, capability) in enumerate(cases):
            with self.subTest(index=index):
                source = self.source(*items)
                addon = self.addon()
                handle = self.utils.register_feature('owner-' + str(index),
                    overrides=(self.override(capability=capability),))
                self.assertEqual(len(addon.keymap_items), 0)
                self.assertEqual(list(source.keymap_items), items)
                self.assertTrue(self.reasons(handle))
                handle.release()
                self.runtime.configs.default.keymaps.remove(source)
                self.runtime.configs.addon.keymaps.remove(addon)

    def test_partial_failure_rolls_back_own_work_and_recovers(self):
        self.source(row())
        addon = self.addon()
        addon.keymap_items.fail_next_new = True
        handle = self.utils.register_feature('owner-a', overrides=(self.override(),))
        self.assertEqual(len(addon.keymap_items), 0)
        self.assertTrue(self.reasons(handle))
        handle.refresh()
        self.assertEqual([item.idname for item in addon.keymap_items], ['bluehole.replacement'])
        handle.release()
        self.assertEqual(len(addon.keymap_items), 0)

    def test_second_request_failure_is_atomic(self):
        self.source(row(), row('object.other', key='B'))
        addon = self.addon()
        addon.keymap_items.fail_create_at = 2
        second = self.override('second', selector=self.selector(
            event=self.event(type='B'), target=self.target('object.other')),
            assignment=self.assignment('second-replacement', event=self.event(type='B'),
                                       target=self.target('bluehole.second')))
        handle = self.utils.register_feature('owner-a',
            overrides=(self.override(), second))
        self.assertEqual(len(addon.keymap_items), 0)
        self.assertTrue(self.reasons(handle))
        handle.refresh()
        self.assertEqual([item.idname for item in addon.keymap_items],
                         ['bluehole.replacement', 'bluehole.second'])
        handle.release()
        self.assertEqual(len(addon.keymap_items), 0)

    def test_property_setter_failure_removes_created_item(self):
        self.source(row())
        addon = self.addon()
        addon.keymap_items.new_prop_schema = {'mode': 0}
        addon.keymap_items.new_prop_fail = 'mode'
        replacement = self.assignment(target=self.target('bluehole.replacement', mode=1))
        handle = self.utils.register_feature('owner-a', overrides=(
            self.override(assignment=replacement),))
        self.assertEqual(len(addon.keymap_items), 0)
        self.assertTrue(self.reasons(handle))
        addon.keymap_items.new_prop_fail = None
        handle.refresh()
        self.assertEqual(len(addon.keymap_items), 1)
        handle.release()
        self.assertEqual(len(addon.keymap_items), 0)

    def test_modal_copy_changes_only_owned_token(self):
        source = self.runtime.map('default', 'Transform Modal Map', space='EMPTY',
                                  modal=True, tool=False)
        original = self.native_modal_row()
        source.keymap_items.append_fixture(original)
        valid_cancel = source.keymap_items.append_fixture(
            self.native_modal_row('CANCEL', key='ESC'))
        scope = self.scope(name='Transform Modal Map', space_type='EMPTY',
                           is_modal=True)
        event = self.native_modal_event()
        selector = self.selector(scope=scope, event=event,
                                 target=self.utils.KeymapTarget(modal_value='PRECISION'))
        replacement = self.assignment(scope=scope, event=event,
            target=self.utils.KeymapTarget(modal_value='CANCEL'))
        handle = self.utils.register_feature('modal-owner', overrides=(
            self.override(selector=selector, assignment=replacement,
                          capability='modal_head',
                          context='transform_translate_precision_cancel'),))
        self.assertEqual([item.propvalue for item in source.keymap_items],
                         ['CANCEL', 'PRECISION', 'CANCEL'])
        self.assertIs(source.keymap_items[1], original)
        handle.release()
        self.assertEqual(list(source.keymap_items), [original, valid_cancel])

    def test_modal_replacement_token_must_be_observed_in_source(self):
        source = self.runtime.map('default', 'Transform Modal Map', space='EMPTY',
                                  modal=True, tool=False)
        original = source.keymap_items.append_fixture(
            self.native_modal_row())
        scope = self.scope(name='Transform Modal Map', space_type='EMPTY',
                           is_modal=True)
        event = self.native_modal_event()
        request = self.override(selector=self.selector(scope=scope, event=event,
            target=self.utils.KeymapTarget(modal_value='PRECISION')),
            assignment=self.assignment(scope=scope, event=event,
                target=self.utils.KeymapTarget(modal_value='CANCEL')),
            capability='modal_head', context='transform_translate_precision_cancel')
        handle = self.utils.register_feature('modal-owner', overrides=(request,))
        self.assertEqual(list(source.keymap_items), [original])
        self.assertTrue(self.reasons(handle))
        handle.release()

    def test_stock_capability_accepts_exact_row_and_rejects_near_matches(self):
        scope = self.scope(name='Object Mode', space_type='EMPTY')
        for label, event, action in (
                ('exact', self.event(), 'SELECT'),
                ('alt_a', self.event(alt=True), 'SELECT'),
                ('deselect', self.event(), 'DESELECT')):
            with self.subTest(case=label):
                source = self.runtime.map('default', 'Object Mode', space='EMPTY',
                                          tool=False)
                original = source.keymap_items.append_fixture(
                    row(prop_values={'action': action}, alt=event.alt))
                addon = self.runtime.map('addon', 'Object Mode', space='EMPTY',
                                         tool=False)
                selector = self.selector(scope=scope, event=event,
                    target=self.target(action=action))
                request = self.override(selector=selector,
                    assignment=self.assignment(scope=scope, event=event),
                    context='stock_object_mode_select_all')
                handle = self.utils.register_feature('stock-' + label,
                    overrides=(request,))
                self.assertEqual(len(addon.keymap_items), 1 if label == 'exact' else 0)
                self.assertEqual(list(source.keymap_items), [original])
                if label != 'exact':
                    self.assertTrue(self.reasons(handle))
                handle.release()
                self.runtime.configs.default.keymaps.remove(source)
                self.runtime.configs.addon.keymaps.remove(addon)

    def test_modal_capability_rejects_press_and_wrong_scope(self):
        for label, event, space in (
                ('press', self.native_modal_event(value='PRESS'), 'EMPTY'),
                ('wrong_scope', self.native_modal_event(), 'VIEW_3D')):
            with self.subTest(case=label):
                source = self.runtime.map('default', 'Transform Modal Map',
                                          space=space, modal=True, tool=False)
                original = source.keymap_items.append_fixture(
                    self.native_modal_row(value=event.value))
                cancel = source.keymap_items.append_fixture(
                    self.native_modal_row('CANCEL', key='ESC'))
                scope = self.scope(name='Transform Modal Map', space_type=space,
                                   is_modal=True)
                selector = self.selector(scope=scope, event=event,
                    target=self.utils.KeymapTarget(modal_value='PRECISION'))
                request = self.override(selector=selector,
                    assignment=self.assignment(scope=scope, event=event,
                        target=self.utils.KeymapTarget(modal_value='CANCEL')),
                    capability='modal_head',
                    context='transform_translate_precision_cancel')
                handle = self.utils.register_feature('modal-' + label,
                    overrides=(request,))
                self.assertEqual(list(source.keymap_items), [original, cancel])
                self.assertTrue(self.reasons(handle))
                handle.release()
                self.runtime.configs.default.keymaps.remove(source)

    def test_modal_active_role_requires_default_alias_and_cleans_after_switch(self):
        scope = self.scope(name='Transform Modal Map', space_type='EMPTY',
                           is_modal=True)
        event = self.native_modal_event()
        request = self.override(selector=self.selector(scope=scope, event=event,
                target=self.utils.KeymapTarget(modal_value='PRECISION'),
                role='active'),
            assignment=self.assignment(scope=scope, event=event,
                target=self.utils.KeymapTarget(modal_value='CANCEL')),
            capability='modal_head', context='transform_translate_precision_cancel')
        default_map = self.runtime.map('default', 'Transform Modal Map',
                                       space='EMPTY', modal=True, tool=False)
        original = default_map.keymap_items.append_fixture(self.native_modal_row())
        cancel = default_map.keymap_items.append_fixture(
            self.native_modal_row('CANCEL', key='ESC'))
        custom = FakeConfig('custom-active')
        custom_map = custom.keymaps.new('Transform Modal Map', space_type='EMPTY',
                                       modal=True, tool=False)
        custom_original = custom_map.keymap_items.append_fixture(self.native_modal_row())
        custom_cancel = custom_map.keymap_items.append_fixture(
            self.native_modal_row('CANCEL', key='ESC'))
        self.runtime.configs.active = custom
        rejected = self.utils.register_feature('modal-custom', overrides=(request,))
        self.assertEqual(list(custom_map.keymap_items), [custom_original, custom_cancel])
        self.assertTrue(self.reasons(rejected))
        rejected.release()
        self.runtime.configs.active = self.runtime.configs.default
        applied = self.utils.register_feature('modal-default', overrides=(request,))
        self.assertEqual(len(default_map.keymap_items), 3)
        self.runtime.configs.active = custom
        applied.release()
        self.assertEqual(list(default_map.keymap_items), [original, cancel])
        self.assertEqual(list(custom_map.keymap_items), [custom_original, custom_cancel])

    def test_changed_source_selector_withdraws_owned_override(self):
        original = row(prop_values={'action': 'SELECT'})
        source = self.source(original)
        addon = self.addon()
        handle = self.utils.register_feature('owner-a', overrides=(self.override(
            selector=self.selector(target=self.target(action='SELECT'))),))
        self.assertEqual(len(addon.keymap_items), 1)
        original.type = 'F19'
        original.properties.action = 'DESELECT'
        handle.refresh()
        self.assertEqual(len(addon.keymap_items), 0)
        self.assertEqual(original.type, 'F19')
        self.assertEqual(original.properties.action, 'DESELECT')
        self.assertIs(source.keymap_items[0], original)
        handle.release()

    def test_merged_user_original_must_be_exact_unique_and_active_before_creation(self):
        class ChangedMerged(MergedMaps):
            def __init__(self, configs, change):
                super().__init__(configs)
                self.change = change

            def __iter__(self):
                for map_ in super().__iter__():
                    if map_.name == '3D View':
                        original = next(item for item in map_.keymap_items
                                        if item.idname == 'object.select_all')
                        if self.change == 'edited':
                            original.type = 'F19'
                            original.properties.action = 'DESELECT'
                        elif self.change == 'duplicate':
                            map_.keymap_items.rows.append(original.clone())
                        else:
                            original.active = False
                    yield map_

        for change in ('edited', 'duplicate', 'inactive'):
            with self.subTest(merged_original=change):
                source = self.source(row(prop_values={'action': 'SELECT'}))
                addon = self.addon()
                self.runtime.configs.user.keymaps = ChangedMerged(self.runtime.configs,
                                                                    change)
                handle = self.utils.register_feature('owner-' + change, overrides=(
                    self.override(selector=self.selector(
                        target=self.target(action='SELECT'))),))
                self.assertEqual(addon.keymap_items.created, 0)
                for _ in range(3):
                    self.utils.reconcile(budget=1, time_budget=1)
                self.assertEqual(addon.keymap_items.created, 0)
                self.assertEqual(len(addon.keymap_items), 0)
                self.assertEqual(len(source.keymap_items), 1)
                self.assertTrue(self.reasons(handle))
                handle.release()
                self.runtime.configs.default.keymaps.remove(source)
                self.runtime.configs.addon.keymaps.remove(addon)

    def test_config_replacement_does_not_delete_new_lookalike(self):
        self.source(row())
        addon = self.addon()
        handle = self.utils.register_feature('owner-a', overrides=(self.override(),))
        self.assertEqual(len(addon.keymap_items), 1)
        self.runtime.replace_config('addon')
        replacement_map = self.addon(row('bluehole.replacement'))
        handle.release()
        self.assertEqual(len(replacement_map.keymap_items), 1)
        self.assertEqual(replacement_map.keymap_items[0].idname, 'bluehole.replacement')

    def test_live_alias_wrapper_pointer_reuse_cannot_delete_foreign_item(self):
        addon = self.addon()
        addon.keymap_items.return_alias_wrappers = True
        handle = self.utils.register_feature('owner-a', assignments=(self.assignment(),))
        stored = handle.owned_pairs[0][1]
        live = addon.keymap_items[0]
        self.assertIsNot(stored, live)
        self.assertEqual(stored.as_pointer(), live.as_pointer())
        self.assertEqual(stored.id, live.id)
        addon.keymap_items.remove(live)
        foreign = row('bluehole.replacement')
        foreign._pointer = stored.as_pointer()
        self.assertNotEqual(foreign.id, stored.id)
        addon.keymap_items.append_fixture(foreign)
        created = addon.keymap_items.created
        self.utils.reconcile(budget=1, time_budget=1)
        self.assertEqual(addon.keymap_items.created, created)
        self.assertEqual(list(addon.keymap_items), [foreign])
        handle.release()
        self.utils.release_all()
        self.assertEqual(list(addon.keymap_items), [foreign])

    def test_source_map_generation_change_revalidates_fresh_membership(self):
        source = self.source(row())
        addon = self.addon()
        handle = self.utils.register_feature('owner-a', overrides=(self.override(),))
        prior = addon.keymap_items[0]
        self.runtime.configs.default.keymaps.remove(source)
        new_source = row()
        recreated = self.source(new_source)
        handle.refresh()
        self.assertFalse(prior._alive)
        self.assertEqual(len(addon.keymap_items), 0)
        handle.refresh()
        self.assertEqual(len(addon.keymap_items), 1)
        self.assertEqual(list(recreated.keymap_items), [new_source])
        handle.release()
        self.assertEqual(len(addon.keymap_items), 0)

    def test_reconcile_unchanged_does_not_rebuild(self):
        self.source(row())
        addon = self.addon()
        handle = self.utils.register_feature('owner-a', overrides=(self.override(),))
        self.assertEqual(len(addon.keymap_items), 1)
        identity = addon.keymap_items[0].as_pointer()
        for _ in range(5):
            self.utils.reconcile(budget=1)
        self.assertEqual(addon.keymap_items.created, 1)
        self.assertEqual(addon.keymap_items[0].as_pointer(), identity)
        handle.release()

    def test_late_provider_displacement_recovers_only_owned_item(self):
        self.source(row())
        foreign = row('other.provider')
        addon = self.addon(foreign)
        handle = self.utils.register_feature('owner-a', overrides=(self.override(),))
        first = addon.keymap_items[-1]
        self.assertEqual(self.merged_names()[0], 'bluehole.replacement')
        replacement_provider = foreign.clone()
        addon.keymap_items.remove(foreign)
        addon.keymap_items.append_fixture(replacement_provider)
        provider = addon.keymap_items[-1]
        self.assertEqual(self.merged_names()[0], 'other.provider')
        for _ in range(4):
            self.utils.reconcile(budget=4)
        self.assertIs(addon.keymap_items[-2], provider)
        self.assertEqual(self.merged_names()[0], 'bluehole.replacement')
        self.assertEqual([item.idname for item in addon.keymap_items],
                         ['other.provider', 'bluehole.replacement'])
        self.assertFalse(first._alive)
        handle.release()
        self.assertEqual(list(addon.keymap_items), [provider])

    def test_conflicting_owners_do_not_choose_priority_by_registration_order(self):
        self.source(row())
        addon = self.addon()
        first_request = self.override()
        first = self.utils.register_feature('owner-a', overrides=(first_request,))
        self.assertIs(self.utils.register_feature('owner-a', overrides=(first_request,)), first)
        second_request = self.override(assignment=self.assignment(
            target=self.target('bluehole.different')),
            selector=self.utils.KeymapSelector(self.scope(), self.event(),
                self.target(), source_role='default', ledger_id='other-ledger',
                sample_id='other-sample'))
        second = self.utils.register_feature('owner-b', overrides=(second_request,))
        self.assertEqual(len(addon.keymap_items), 1)
        self.assertEqual(addon.keymap_items[0].idname, 'bluehole.replacement')
        self.assertIn('conflicting_assignment', self.reasons(second))
        second.release()
        first.release()
        self.assertEqual(len(addon.keymap_items), 0)

    def test_direct_owned_source_edit_is_retained_and_request_cancelled(self):
        self.source(row())
        addon = self.addon()
        handle = self.utils.register_feature('owner-a', overrides=(self.override(),))
        owned = addon.keymap_items[0]
        owned.type = 'F19'
        created = addon.keymap_items.created
        for _ in range(4):
            handle.refresh()
            self.utils.reconcile(budget=1, time_budget=1)
        self.assertEqual(addon.keymap_items.created, created)
        self.assertEqual(list(addon.keymap_items), [owned])
        trace = self.utils.retained_edits()
        self.assertEqual(len(trace), 1)
        self.assertEqual((trace[0]['owner_id'], trace[0]['request_id']),
                         ('owner-a', 'override'))
        self.assertEqual(self.utils.runtime_stats()['retained_edited'], 1)
        handle.release()
        self.assertEqual(list(addon.keymap_items), [owned])
        again = self.utils.register_feature('owner-a', overrides=(self.override(),))
        self.assertEqual(list(addon.keymap_items), [owned])
        self.assertEqual(addon.keymap_items.created, created)
        self.assertIn('user_edited_owned_item_retained', self.reasons(again))
        again.release()

    def test_merged_user_wrapper_edit_does_not_transfer_owned_source(self):
        self.source(row())
        addon = self.addon()
        handle = self.utils.register_feature('owner-a', overrides=(self.override(),))
        owned = addon.keymap_items[0]
        merged = self.runtime.configs.user.keymaps.get('3D View')
        merged.keymap_items[0].type = 'F19'
        self.assertEqual(owned.type, 'A')
        handle.release()
        self.assertFalse(owned._alive)
        self.assertEqual(len(addon.keymap_items), 0)
        self.assertEqual(self.utils.retained_edits(), ())

    def test_unrelated_late_provider_row_does_not_recreate_override(self):
        self.source(row())
        addon = self.addon(row('other.provider'))
        handle = self.utils.register_feature('owner-a', overrides=(self.override(),))
        owned = addon.keymap_items[-1]
        addon.keymap_items.append_fixture(row('other.unrelated', key='B'))
        for _ in range(4):
            handle.refresh()
        self.assertIs(addon.keymap_items[1], owned)
        self.assertEqual(addon.keymap_items.created, 1)
        handle.release()

    def test_unrelated_unreadable_source_row_does_not_block_exact_target(self):
        exact = row()
        unreadable = row('other.unrelated')
        unreadable.properties.bl_rna.properties.append(types.SimpleNamespace(
            identifier='missing', type='INT', is_array=False))
        source = self.source(unreadable, exact)
        addon = self.addon()
        handle = self.utils.register_feature('owner-a', overrides=(self.override(),))
        self.assertEqual(len(addon.keymap_items), 1)
        self.assertEqual(list(source.keymap_items), [unreadable, exact])
        handle.release()

    def test_provider_lookalike_requires_enabled_module_pref_and_exact_reference(self):
        scope = self.scope(name='3D View Generic')
        event = self.event(type='TAB', alt=True)
        provider_target = self.target('machin3.toggle_smooth',
            toggle_subd_overlays=False,
            toggle_korean_bevel_overlays=True, mode='SUBD')
        addon = self.runtime.map('addon', '3D View Generic', tool=False)
        provider = addon.keymap_items.append_fixture(row('machin3.toggle_smooth',
            key='TAB', alt=True, prop_values=dict(provider_target.properties)))
        request = self.override(selector=self.selector(scope=scope, event=event,
            target=provider_target, role='addon'),
            assignment=self.assignment(scope=scope, event=event),
            context='machin3tools_object_toggle_smooth')
        provider_module = types.ModuleType('MACHIN3tools')
        provider_module.bl_info = {'version': (1, 13, 2, 'DeusEx')}
        prefs = types.SimpleNamespace(activate_smooth=True)
        addon_entry = types.SimpleNamespace(module='MACHIN3tools', preferences=prefs)
        self.runtime.bpy.context.preferences = types.SimpleNamespace(
            addons={'MACHIN3tools': addon_entry})
        self.runtime.bpy.ops = types.SimpleNamespace(machin3=types.SimpleNamespace(
            toggle_smooth=types.SimpleNamespace(get_rna_type=lambda: object())))
        provider_module.keymaps = [(addon, provider)]
        forged_reference = provider.clone()
        forged_reference._pointer = provider.as_pointer()
        self.assertNotEqual(forged_reference.id, provider.id)
        with patch.dict(sys.modules, {'MACHIN3tools': provider_module}):
            for name, enabled, addons, references, should_apply in (
                    ('disabled', False, {'MACHIN3tools': addon_entry},
                     [(addon, provider)], False),
                    ('missing_prefs', True, {}, [(addon, provider)], False),
                    ('lookalike_only', True, {'MACHIN3tools': addon_entry}, [], False),
                    ('pointer_reused', True, {'MACHIN3tools': addon_entry},
                     [(addon, forged_reference)], False),
                    ('trusted', True, {'MACHIN3tools': addon_entry},
                     [(addon, provider)], True)):
                with self.subTest(case=name):
                    provider_module.__addon_enabled__ = enabled
                    provider_module.keymaps = references
                    self.runtime.bpy.context.preferences.addons = addons
                    handle = self.utils.register_feature('provider-' + name,
                        overrides=(request,))
                    self.assertEqual(len(addon.keymap_items), 2 if should_apply else 1)
                    self.assertIs(addon.keymap_items[0], provider)
                    if not should_apply:
                        self.assertTrue(self.reasons(handle))
                    handle.release()
                    self.assertEqual(list(addon.keymap_items), [provider])

    def test_provider_retained_wrapper_id_change_rejects_reused_address(self):
        scope = self.scope(name='3D View Generic')
        event = self.event(type='TAB', alt=True)
        provider_target = self.target('machin3.toggle_smooth',
            toggle_subd_overlays=False,
            toggle_korean_bevel_overlays=True, mode='SUBD')
        addon = self.runtime.map('addon', '3D View Generic', tool=False)
        original = addon.keymap_items.append_fixture(row('machin3.toggle_smooth',
            key='TAB', alt=True, prop_values=dict(provider_target.properties)))
        retained_wrapper = ReusedIdWrapper(addon, original)
        module = types.ModuleType('MACHIN3tools')
        module.__addon_enabled__ = True
        module.bl_info = {'version': (1, 13, 2, 'DeusEx')}
        module.keymaps = [(addon, retained_wrapper)]
        self.runtime.bpy.context.preferences = types.SimpleNamespace(addons={
            'MACHIN3tools': types.SimpleNamespace(module='MACHIN3tools',
                preferences=types.SimpleNamespace(activate_smooth=True))})
        self.runtime.bpy.ops = types.SimpleNamespace(machin3=types.SimpleNamespace(
            toggle_smooth=types.SimpleNamespace(get_rna_type=lambda: object())))
        request = self.override(selector=self.selector(scope=scope, event=event,
            target=provider_target, role='addon'),
            assignment=self.assignment(scope=scope, event=event),
            context='machin3tools_object_toggle_smooth')
        with patch.dict(sys.modules, {'MACHIN3tools': module}):
            handle = self.utils.register_feature('provider-owner', overrides=(request,))
            self.assertEqual(len(addon.keymap_items), 2)
            original_id = retained_wrapper.id
            addon.keymap_items.remove(original)
            foreign = row('machin3.toggle_smooth', key='TAB', alt=True,
                          prop_values=dict(provider_target.properties))
            foreign._pointer = retained_wrapper.as_pointer()
            addon.keymap_items.append_fixture(foreign)
            self.assertNotEqual(retained_wrapper.id, original_id)
            handle.refresh()
            self.assertEqual(list(addon.keymap_items), [foreign])
            self.assertEqual(addon.keymap_items.created, 1)
            self.assertIn('provider_reference_generation_changed', self.reasons(handle))
            handle.release()

    def test_created_map_is_removed_after_release_and_creation_failure(self):
        source = self.runtime.map('default', tool=None)
        source.keymap_items.append_fixture(row())
        request = self.override(selector=self.selector(scope=self.scope(is_tool=None)),
            assignment=self.assignment(scope=self.scope(is_tool=None)))
        handle = self.utils.register_feature('owner-a', overrides=(request,))
        self.assertEqual(len(tuple(self.runtime.configs.addon.keymaps)), 1)
        self.assertEqual(self.runtime.configs.update_calls[-1][0][1],
                         ('bluehole.replacement',))
        handle.release()
        self.assertEqual(len(tuple(self.runtime.configs.addon.keymaps)), 0)
        self.assertEqual(self.runtime.configs.update_calls[-1], ())

    def test_feature_preflight_is_atomic_for_pending_second_request(self):
        self.source(row())
        addon = self.addon()
        missing = self.override('missing', selector=self.selector(
            event=self.event(type='B'), target=self.target('object.other')),
            assignment=self.assignment('other', event=self.event(type='B'),
                                       target=self.target('bluehole.other')))
        handle = self.utils.register_feature('owner-a', overrides=(self.override(), missing))
        self.assertEqual(len(addon.keymap_items), 0)
        self.assertIn('feature_preflight_incomplete', self.reasons(handle))
        source = self.runtime.configs.default.keymaps.get('3D View')
        source.keymap_items.append_fixture(row('object.other', key='B'))
        handle.refresh()
        self.assertEqual([item.idname for item in addon.keymap_items],
                         ['bluehole.replacement', 'bluehole.other'])
        handle.release()
        self.assertEqual(len(addon.keymap_items), 0)

    def test_partial_compatibility_pair_release_cancels_only_that_request(self):
        addon = self.addon()
        requests = (self.assignment('first', target=self.target('bluehole.first')),
                    self.assignment('second', event=self.event(type='B'),
                                    target=self.target('bluehole.second')))
        handle = self.utils.register_feature('owner-a', assignments=requests)
        self.assertEqual(len(addon.keymap_items), 2)
        first_pair = [handle.owned_pairs[0]]
        first = first_pair[0][1]
        second = handle.owned_pairs[1][1]
        self.utils.release_owned_pairs(first_pair)
        self.assertEqual(first_pair, [])
        self.assertFalse(first._alive)
        self.assertEqual(list(addon.keymap_items), [second])
        for _ in range(3):
            handle.refresh()
        self.assertEqual(list(addon.keymap_items), [second])
        handle.release()
        self.assertEqual(len(addon.keymap_items), 0)

    def test_reprioritization_limit_survives_source_reallocation(self):
        source = self.source(row())
        addon = self.addon(row('other.provider'))
        handle = self.utils.register_feature('owner-a', overrides=(self.override(),))
        for _ in range(2):
            provider = next(item for item in addon.keymap_items
                            if item.idname == 'other.provider')
            replacement = provider.clone()
            addon.keymap_items.remove(provider)
            addon.keymap_items.append_fixture(replacement)
            handle.refresh()
            self.assertEqual(self.merged_names()[0], 'bluehole.replacement')
        self.runtime.configs.default.keymaps.remove(source)
        self.source(row())
        handle.refresh()
        handle.refresh()
        self.assertEqual(self.merged_names()[0], 'bluehole.replacement')
        provider = next(item for item in addon.keymap_items
                        if item.idname == 'other.provider')
        replacement = provider.clone()
        addon.keymap_items.remove(provider)
        addon.keymap_items.append_fixture(replacement)
        created = addon.keymap_items.created
        for _ in range(3):
            handle.refresh()
        self.assertEqual(addon.keymap_items.created, created)
        self.assertIn('provider_priority_conflict', self.reasons(handle))
        handle.release()

    def test_repeated_provider_overtaking_stops_priority_fight(self):
        self.source(row())
        provider = row('other.provider')
        addon = self.addon(provider)
        handle = self.utils.register_feature('owner-a', overrides=(self.override(),))
        for _ in range(2):
            current = next(item for item in addon.keymap_items
                           if item.idname == 'other.provider')
            copied = current.clone()
            addon.keymap_items.remove(current)
            addon.keymap_items.append_fixture(copied)
            self.assertEqual(self.merged_names()[0], 'other.provider')
            handle.refresh()
            self.assertEqual(self.merged_names()[0], 'bluehole.replacement')
        current = next(item for item in addon.keymap_items
                       if item.idname == 'other.provider')
        copied = current.clone()
        addon.keymap_items.remove(current)
        addon.keymap_items.append_fixture(copied)
        created_before = addon.keymap_items.created
        for _ in range(5):
            handle.refresh()
        self.assertEqual(addon.keymap_items.created, created_before)
        self.assertIn('provider_priority_conflict', self.reasons(handle))
        handle.release()
        self.assertEqual([item.idname for item in addon.keymap_items], ['other.provider'])

    def test_copied_legacy_pair_from_before_repriority_releases_current_item(self):
        self.source(row())
        provider = row('other.provider')
        addon = self.addon(provider)
        handle = self.utils.register_feature('legacy:Mesh:one', overrides=(self.override(),))
        copied_pairs = list(handle.owned_pairs)
        old_item = copied_pairs[0][1]
        replacement_provider = provider.clone()
        addon.keymap_items.remove(provider)
        addon.keymap_items.append_fixture(replacement_provider)
        handle.refresh()
        self.assertFalse(old_item._alive)
        with self.assertRaises(ReferenceError):
            old_item.as_pointer()
        foreign_lookalike = addon.keymap_items.append_fixture(row('bluehole.replacement', key='F18'))
        self.utils.release_owned_pairs(copied_pairs)
        self.assertEqual(copied_pairs, [])
        self.assertEqual(list(addon.keymap_items), [replacement_provider, foreign_lookalike])
        handle.refresh()
        self.assertEqual(list(addon.keymap_items), [replacement_provider, foreign_lookalike])
        handle.release()

    def test_copied_legacy_pair_from_old_map_releases_recreated_item(self):
        self.addon()
        handle = self.utils.register_feature('legacy:Mesh:one', assignments=(self.assignment(),))
        copied_pairs = list(handle.owned_pairs)
        old_item = copied_pairs[0][1]
        self.runtime.replace_config('addon')
        new_map = self.addon(row('other.foreign', key='B'))
        foreign = new_map.keymap_items[0]
        handle.refresh()
        self.assertFalse(old_item._alive)
        self.assertEqual(len(new_map.keymap_items), 2)
        self.utils.release_owned_pairs(copied_pairs)
        self.assertEqual(list(new_map.keymap_items), [foreign])
        handle.refresh()
        self.assertEqual(list(new_map.keymap_items), [foreign])
        handle.release()

    def test_setter_failure_with_remove_failure_retains_cleanup_ownership(self):
        self.source(row())
        addon = self.addon(row('other.foreign', key='B'))
        foreign = addon.keymap_items[0]
        addon.keymap_items.new_prop_schema = {'mode': 0}
        addon.keymap_items.new_prop_fail = 'mode'
        addon.keymap_items.fail_next_remove = True
        replacement = self.assignment(target=self.target('bluehole.replacement', mode=1))
        handle = self.utils.register_feature('owner-a', overrides=(
            self.override(assignment=replacement),))
        self.assertEqual(len(addon.keymap_items), 2)
        self.assertEqual(self.utils.runtime_stats()['pending_cleanup'], 1)
        created = addon.keymap_items.created
        addon.keymap_items.new_prop_fail = None
        handle.refresh()
        self.assertEqual(addon.keymap_items.created, created)
        self.utils.reconcile(budget=1, time_budget=1)
        self.assertEqual(self.utils.runtime_stats()['pending_cleanup'], 0)
        self.assertEqual(list(addon.keymap_items), [foreign])
        handle.release()

    def test_release_remove_failure_blocks_same_owner_until_cleanup(self):
        addon = self.addon(row('other.foreign', key='B'))
        foreign = addon.keymap_items[0]
        request = self.assignment()
        handle = self.utils.register_feature('owner-a', assignments=(request,))
        created = addon.keymap_items.created
        addon.keymap_items.fail_next_remove = True
        result = handle.release()
        self.assertIn(('replacement', 'owned_remove_failed'), result)
        self.assertEqual(self.utils.runtime_stats()['pending_cleanup'], 1)
        again = self.utils.register_feature('owner-a', assignments=(request,))
        self.assertEqual(addon.keymap_items.created, created)
        self.utils.release_all()
        self.assertEqual(self.utils.runtime_stats()['pending_cleanup'], 0)
        self.assertEqual(list(addon.keymap_items), [foreign])
        again.release()

    def test_pending_cleanup_blocks_new_same_event_request_until_exact_removal(self):
        for second_owner in ('owner-b', 'owner-a'):
            with self.subTest(second_owner=second_owner):
                addon = self.addon(row('other.foreign', key='B'))
                foreign = addon.keymap_items[0]
                first = self.utils.register_feature('owner-a',
                    assignments=(self.assignment(),))
                addon.keymap_items.remove_failures_remaining = 2
                first.release()
                self.assertEqual(self.utils.runtime_stats()['pending_cleanup'], 1)
                second_request = self.assignment('other',
                    target=self.target('bluehole.other'))
                second = self.utils.register_feature(second_owner,
                    assignments=(second_request,))
                self.assertEqual(addon.keymap_items.created, 1)
                self.assertEqual([item.idname for item in addon.keymap_items],
                                 ['other.foreign', 'bluehole.replacement'])
                self.assertIn('conflicting_assignment', self.reasons(second))
                self.utils.reconcile(budget=1, time_budget=1)
                self.assertEqual(self.utils.runtime_stats()['pending_cleanup'], 1)
                self.assertEqual(addon.keymap_items.created, 1)
                self.utils.reconcile(budget=1, time_budget=1)
                self.assertEqual(self.utils.runtime_stats()['pending_cleanup'], 0)
                second.refresh()
                self.assertEqual([item.idname for item in addon.keymap_items],
                                 ['other.foreign', 'bluehole.other'])
                second.release()
                self.assertEqual(list(addon.keymap_items), [foreign])
                self.runtime.configs.addon.keymaps.remove(addon)

    def test_repriority_remove_failure_does_not_duplicate_owned_item(self):
        self.source(row())
        provider = row('other.provider')
        addon = self.addon(provider)
        handle = self.utils.register_feature('owner-a', overrides=(self.override(),))
        replacement_provider = provider.clone()
        addon.keymap_items.remove(provider)
        addon.keymap_items.append_fixture(replacement_provider)
        addon.keymap_items.fail_next_remove = True
        created = addon.keymap_items.created
        self.utils.reconcile(budget=1, time_budget=1)
        self.assertEqual(addon.keymap_items.created, created)
        self.assertEqual(sum(item.idname == 'bluehole.replacement'
                             for item in addon.keymap_items), 1)
        self.assertGreater(self.utils.runtime_stats()['pending_cleanup'], 0)
        self.utils.reconcile(budget=1, time_budget=1)
        self.utils.release_all()
        self.assertEqual(self.utils.runtime_stats()['pending_cleanup'], 0)
        self.assertEqual(list(addon.keymap_items), [replacement_provider])

    def test_repriority_cleanup_then_refresh_reapplies_request(self):
        self.source(row())
        provider = row('other.provider')
        addon = self.addon(provider)
        handle = self.utils.register_feature('owner-a', overrides=(self.override(),))
        replacement_provider = provider.clone()
        addon.keymap_items.remove(provider)
        addon.keymap_items.append_fixture(replacement_provider)
        addon.keymap_items.fail_next_remove = True
        self.utils.reconcile(budget=1, time_budget=1)
        self.assertEqual(self.utils.runtime_stats()['pending_cleanup'], 1)
        self.utils.reconcile(budget=1, time_budget=1)
        self.assertEqual(self.utils.runtime_stats()['pending_cleanup'], 0)
        handle.refresh()
        self.assertEqual([item.idname for item in addon.keymap_items],
                         ['other.provider', 'bluehole.replacement'])
        self.assertEqual(self.merged_names()[0], 'bluehole.replacement')
        self.assertNotIn('user_removed_owned_item', self.reasons(handle))
        handle.release()
        self.assertEqual(list(addon.keymap_items), [replacement_provider])

    def test_repeated_toggle_and_global_clear_are_idempotent(self):
        self.source(row())
        addon = self.addon()
        for _ in range(3):
            handle = self.utils.register_feature('owner-a', overrides=(self.override(),))
            self.assertEqual(len(addon.keymap_items), 1)
            handle.release()
            self.assertEqual(len(addon.keymap_items), 0)
        handle = self.utils.register_feature('owner-a', overrides=(self.override(),))
        self.utils.release_all()
        self.utils.release_all()
        handle.release()
        self.assertEqual(len(addon.keymap_items), 0)

    def test_plain_assignment_owns_only_its_exact_item(self):
        addon = self.addon(row('bluehole.replacement'))
        foreign = addon.keymap_items[0]
        handle = self.utils.register_feature('owner-a', assignments=(
            self.assignment(),))
        self.assertEqual(len(addon.keymap_items), 2)
        self.assertIs(addon.keymap_items[0], foreign)
        self.assertEqual(addon.keymap_items[1].idname, 'bluehole.replacement')
        handle.release()
        self.assertEqual(list(addon.keymap_items), [foreign])

    def test_bound_empty_pending_list_later_fills_then_drains_exactly(self):
        addon = self.addon()
        pairs = []
        self.utils.bind_category_pairs('Mesh', pairs)
        request = self.override(selector=self.selector(role='addon',
            target=self.target('other.provider')))
        handle = self.utils.register_feature('legacy:Mesh:provider', overrides=(request,))
        self.assertEqual(pairs, [])
        provider = addon.keymap_items.append_fixture(row('other.provider'))
        self.utils.reconcile(budget=1, time_budget=1)
        self.assertEqual(len(pairs), 1)
        self.assertIs(pairs[0][1], addon.keymap_items[-1])
        self.utils.release_owned_pairs(pairs)
        self.assertEqual(pairs, [])
        self.assertEqual(list(addon.keymap_items), [provider])
        self.utils.reconcile(budget=1, time_budget=1)
        self.assertEqual(list(addon.keymap_items), [provider])
        handle.release()

    def test_bound_pending_empty_list_release_cancels_future_apply(self):
        addon = self.addon()
        pairs = []
        self.utils.bind_category_pairs('Mesh', pairs)
        handle = self.utils.register_feature('legacy:Mesh:provider', overrides=(
            self.override(selector=self.selector(role='addon',
                target=self.target('other.provider'))),))
        self.assertEqual(pairs, [])
        self.utils.release_owned_pairs(pairs)
        provider = addon.keymap_items.append_fixture(row('other.provider'))
        self.utils.reconcile(budget=1, time_budget=1)
        self.assertEqual(list(addon.keymap_items), [provider])
        self.assertEqual(pairs, [])
        handle.release()

    def test_capture_selector_freezes_complete_native_row(self):
        original = row(prop_values={'action': 'SELECT', 'count': 3},
                       ctrl=-1, direction='NORTH', repeat=True)
        source = self.source(original)
        selector = self.utils.capture_selector(source, original,
            source_role='default', ledger_id='ledger-x', sample_id='sample-x')
        self.assertEqual(selector.scope, self.scope())
        self.assertEqual(selector.event, self.event(ctrl=-1, direction='NORTH',
                                                   repeat=True))
        self.assertEqual(selector.target, self.target(action='SELECT', count=3))
        self.assertEqual((selector.ledger_id, selector.sample_id),
                         ('ledger-x', 'sample-x'))
        original.properties.action = 'DESELECT'
        self.assertEqual(selector.target, self.target(action='SELECT', count=3))

    def test_bounded_reconcile_visits_many_features_fairly(self):
        self.addon()
        handles = [self.utils.register_feature('owner-' + str(index), assignments=(
            self.assignment('request-' + str(index),
                event=self.event(type='F' + str(index + 1)),
                target=self.target('bluehole.action_' + str(index))),))
            for index in range(12)]
        before = self.utils.runtime_stats()['checked']
        for _ in range(12):
            self.utils.reconcile(budget=1, time_budget=1)
        after = self.utils.runtime_stats()['checked']
        self.assertEqual(after - before, 12)
        self.assertTrue(all(handle.stats['refreshes'] >= 2 for handle in handles))
        self.utils.release_all()

    def test_oversized_feature_is_skipped_without_exceeding_reconcile_budget(self):
        self.addon()
        requests = (self.assignment('one'),
                    self.assignment('two', event=self.event(type='B'),
                                    target=self.target('bluehole.second')))
        handle = self.utils.register_feature('owner-a', assignments=requests)
        before = self.utils.runtime_stats()['checked']
        results = self.utils.reconcile(budget=1, time_budget=1)
        self.assertEqual(self.utils.runtime_stats()['checked'], before)
        self.assertIn('feature_exceeds_reconcile_budget',
                      {result.reason for result in results})
        self.assertEqual(handle.stats['refreshes'], 1)
        handle.release()

    def test_different_targets_same_event_conflict_across_owners(self):
        addon = self.addon()
        first = self.utils.register_feature('owner-a', assignments=(self.assignment(),))
        second = self.utils.register_feature('owner-b', assignments=(
            self.assignment('other', target=self.target('bluehole.other')),))
        self.assertEqual(len(addon.keymap_items), 1)
        self.assertIn('conflicting_assignment', self.reasons(second))
        second.release()
        first.release()

    def test_user_active_keyconfigs_cannot_be_used_to_create_maps(self):
        user = self.runtime.configs.user
        active = self.runtime.configs.active
        addon = self.runtime.configs.addon
        self.assertIsNone(self.utils.get_or_create_keymap(user, 'No Write', 'EMPTY'))
        self.assertIsNone(self.utils.get_or_create_keymap(active, 'No Write', 'EMPTY'))
        self.assertEqual(len(tuple(active.keymaps)), 0)
        created = self.utils.get_or_create_keymap(addon, 'Owned Empty', 'EMPTY')
        self.assertIsNotNone(created)
        self.assertEqual(len(tuple(addon.keymaps)), 1)
        self.utils.release_all()
        self.assertEqual(len(tuple(addon.keymaps)), 0)

    def test_map_creation_collision_never_claims_or_deletes_foreign_scope(self):
        foreign_map = self.runtime.map('addon', name='3D View', space='EMPTY',
                                       tool=None)
        foreign_item = foreign_map.keymap_items.append_fixture(row('other.foreign'))
        maps = self.runtime.configs.addon.keymaps
        maps.new = lambda **kwargs: foreign_map
        handle = self.utils.register_feature('owner-a', assignments=(
            self.assignment(),))
        self.assertEqual(list(foreign_map.keymap_items), [foreign_item])
        self.assertTrue(self.reasons(handle))
        handle.release()
        self.utils.release_all()
        self.assertEqual(list(maps), [foreign_map])
        self.assertEqual(list(foreign_map.keymap_items), [foreign_item])

    def load_production_action_adapter(self):
        for suffix in ('actions', 'Lib', 'Lib.commonUtils',
                       'Lib.commonUtils.runtime', 'debug'):
            package = types.ModuleType(self.prefix + '.' + suffix)
            package.__path__ = []
            sys.modules[package.__name__] = package
        for suffix in ('Lib.commonUtils.runtime.diagnostics', 'debug.debug_flags'):
            sys.modules[self.prefix + '.' + suffix] = types.ModuleType(self.prefix + '.' + suffix)
        action_name = self.prefix + '.actions.operator_action'
        action_spec = importlib.util.spec_from_file_location(action_name,
            ROOT / 'actions/operator_action.py')
        actions = importlib.util.module_from_spec(action_spec)
        sys.modules[action_name] = actions
        action_spec.loader.exec_module(actions)
        name = self.prefix + '.keymaps.keymap_action_utils'
        spec = importlib.util.spec_from_file_location(name,
            ROOT / 'keymaps/keymap_action_utils.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return actions, module

    def test_legacy_binding_accepts_unobservable_default_hyper(self):
        addon = self.addon()
        addon.keymap_items.new_missing_fields.add('hyper')
        actions, module = self.load_production_action_adapter()
        for key, expected_map_type in (('A', 'KEYBOARD'), ('LEFTMOUSE', 'MOUSE')):
            with self.subTest(key=key):
                binding = actions.KeymapBinding('3D View', 'VIEW_3D', key,
                                                is_tool=False)
                self.assertIsNone(binding.map_type)
                action = actions.OperatorAction('bluehole.legacy_' + key.lower(),
                                                keymap_bindings=(binding,))
                pairs = module.ensure_action_keymaps('Legacy', action,
                    context=self.runtime.bpy.context)
                self.assertEqual(len(pairs), 1)
                self.assertEqual(pairs[0][1].idname, 'bluehole.legacy_' + key.lower())
                observed = self.utils.capture_event(pairs[0][1])
                self.assertIsNone(observed.hyper)
                self.assertEqual(observed.map_type, expected_map_type)
                self.utils.release_owned_pairs(pairs)
        self.assertEqual(len(addon.keymap_items), 0)

    def test_equivalent_transient_actions_share_exact_legacy_owner(self):
        addon = self.addon()
        actions, adapter = self.load_production_action_adapter()
        binding = actions.KeymapBinding('3D View', 'VIEW_3D', 'A', is_tool=False)
        first_action = actions.OperatorAction('bluehole.legacy',
                                              keymap_bindings=(binding,))
        second_action = actions.OperatorAction('bluehole.legacy',
                                               keymap_bindings=(binding,))
        self.assertIsNot(first_action, second_action)
        first = adapter.ensure_action_keymaps('Legacy', first_action,
                                              context=self.runtime.bpy.context)
        second = adapter.ensure_action_keymaps('Legacy', second_action,
                                               context=self.runtime.bpy.context)
        self.assertEqual(len(addon.keymap_items), 1)
        self.assertEqual(self.utils.runtime_stats()['features'], 1)
        self.assertEqual(len(first), 1)
        self.assertIs(first[0][1], second[0][1])
        self.utils.release_owned_pairs(first)
        self.assertEqual(len(addon.keymap_items), 0)

    def test_equivalent_transient_action_cannot_recreate_direct_user_edit(self):
        addon = self.addon()
        actions, adapter = self.load_production_action_adapter()
        binding = actions.KeymapBinding('3D View', 'VIEW_3D', 'A', is_tool=False)
        first_action = actions.OperatorAction('bluehole.legacy',
                                              keymap_bindings=(binding,))
        first = adapter.ensure_action_keymaps('Legacy', first_action,
                                              context=self.runtime.bpy.context)
        self.assertEqual(len(first), 1)
        owned = first[0][1]
        owned.type = 'F19'
        self.utils.release_owned_pairs(first)
        self.assertEqual(list(addon.keymap_items), [owned])
        replacement_action = actions.OperatorAction('bluehole.legacy',
            keymap_bindings=(binding,))
        second = adapter.ensure_action_keymaps('Legacy', replacement_action,
                                               context=self.runtime.bpy.context)
        self.assertEqual(second, [])
        self.assertEqual(list(addon.keymap_items), [owned])
        self.assertEqual(len(self.utils.retained_edits()), 1)

    def test_stable_merged_priority_failure_does_not_rebuild_forever(self):
        class ReversedMerged(MergedMaps):
            def __iter__(self):
                for map_ in super().__iter__():
                    map_.keymap_items.rows.reverse()
                    yield map_

        self.runtime.configs.user.keymaps = ReversedMerged(self.runtime.configs)
        self.source(row())
        addon = self.addon()
        handle = self.utils.register_feature('owner-a', overrides=(self.override(),))
        self.assertEqual(len(addon.keymap_items), 0)
        created = addon.keymap_items.created
        self.assertGreater(created, 0)
        for _ in range(5):
            self.utils.reconcile(budget=1, time_budget=1)
        self.assertEqual(addon.keymap_items.created, created)
        handle.refresh()
        self.assertEqual(addon.keymap_items.created, created)
        handle.release()


class LifecycleIntegrationTests(unittest.TestCase):
    """Import only the orchestrator, with category and preference seams stubbed."""

    def setUp(self):
        harness = RuntimeKeymapTests('test_plain_assignment_owns_only_its_exact_item')
        harness.setUp()
        self.addCleanup(harness.doCleanups)
        self.h = harness
        self.core = harness.utils
        self.runtime = harness.runtime
        self.runtime.map('addon', tool=False)
        prefix = harness.prefix
        self.category_modules = {}
        self.fail_category = None
        self.calls = []
        self.timers = {}

        class Timers:
            def __init__(timers_self, registry):
                timers_self.registry = registry

            def is_registered(timers_self, callback):
                return callback in timers_self.registry

            def register(timers_self, callback, **options):
                timers_self.registry[callback] = options

            def unregister(timers_self, callback):
                del timers_self.registry[callback]

        self.runtime.bpy.app = types.SimpleNamespace(timers=Timers(self.timers))
        self.runtime.bpy.types = types.SimpleNamespace(PropertyGroup=type('PropertyGroup', (), {}))
        self.runtime.bpy.context.preferences = types.SimpleNamespace(
            keymap=types.SimpleNamespace(active_keyconfig='Blender'))
        resources = Path(self.enterContext(TemporaryDirectory()))
        self.runtime.bpy.utils = types.SimpleNamespace(
            user_resource=lambda kind, *, path: str(resources / kind / path),
            preset_find=lambda *args, **kwargs: None,
        )

        def preference_group(**values):
            group = types.SimpleNamespace(**values)
            group.bl_rna = types.SimpleNamespace(properties=[types.SimpleNamespace(
                identifier=name, type='BOOLEAN') for name in values])
            return group

        self.preferences = types.SimpleNamespace(
            keymap=preference_group(enable_keymaps=True, deluxe_configured=False),
            pie=preference_group(enable_pie_menus=True),
            thirdparty=preference_group(enable_thirdparty=True),
            is_ready=lambda: True)

        def stub_module(name, *, package=False):
            module = types.ModuleType(name)
            if package:
                module.__path__ = []
            sys.modules[name] = module
            return module

        for suffix in ('Lib', 'Lib.commonUtils', 'Lib.commonUtils.runtime',
                       'preferences', 'debug', 'keymaps.pie'):
            stub_module(prefix + '.' + suffix, package=True)
        diagnostics = stub_module(prefix + '.Lib.commonUtils.runtime.diagnostics')
        diagnostics.log = lambda *args: None
        diagnostics.Severity = types.SimpleNamespace(INFO=1, WARNING=2, DEBUG=3)
        stub_module(prefix + '.Lib.commonUtils.persistence').atomic_write_bytes = lambda *args: None
        stub_module(prefix + '.debug.debug_flags')
        preference_module = stub_module(prefix + '.preferences.prefs')
        preference_module.prefs = lambda: self.preferences

        category_names = ('Mesh', 'Navigation', 'Object', 'Pipeline', 'Sculpt',
                          'Selection', 'Transform', 'UV', 'Other', 'Pie')
        for category_index, category in enumerate(category_names):
            stem = category.lower() + '_keymaps_register'
            path = prefix + ('.keymaps.pie.' if category == 'Pie' else '.keymaps.') + stem
            module = stub_module(path)
            module.KEYMAP_CATEGORY = category
            pairs = []
            setattr(module, 'registered_' + category.lower() + '_keymaps', pairs)

            def register(category=category, pairs=pairs, category_index=category_index):
                self.calls.append(('register', category))
                if self.fail_category == category:
                    raise RuntimeError('injected category failure')
                if category == 'Pie' and not self.preferences.pie.enable_pie_menus:
                    return 0
                self.core.register_feature('legacy:' + category + ':fixture',
                    assignments=(self.h.assignment('request-' + category,
                        event=self.h.event(type='F' + str(category_index + 1)),
                        target=self.h.target('bluehole.' + category.lower())),))
                self.core.sync_category_pairs(category)
                return len(pairs)

            def unregister(category=category, pairs=pairs):
                self.calls.append(('unregister', category))
                self.core.release_owned_pairs(pairs)
                return 0

            module.register = register
            module.unregister = unregister
            self.category_modules[category] = module

        name = prefix + '.keymaps.keymaps_register'
        spec = importlib.util.spec_from_file_location(name, ROOT / 'keymaps/keymaps_register.py')
        orchestrator = importlib.util.module_from_spec(spec)
        sys.modules[name] = orchestrator
        spec.loader.exec_module(orchestrator)
        self.orchestrator = orchestrator
        # This harness substitutes all native category registrars. Keep the
        # same fixture for the Deluxe branch, which now installs one catalog.
        def register_deluxe(_catalog):
            return sum(module.register() for category, module in self.category_modules.items()
                       if self.preferences.keymap.enable_keymaps or category == 'Pipeline')

        orchestrator.deluxe_profile = lambda: types.SimpleNamespace(register=register_deluxe)
        self.addCleanup(orchestrator.unregister)

    def addon_names(self):
        return [item.idname for item in self.runtime.configs.addon.keymaps.get('3D View').keymap_items]

    def test_global_off_preserves_pipeline_and_independent_pie(self):
        self.orchestrator.register()
        self.assertEqual(len(self.addon_names()), 10)
        self.assertEqual(len(self.timers), 1)
        names_before = tuple(self.addon_names())
        creations = self.runtime.configs.addon.keymaps.get('3D View').keymap_items.created
        for _ in range(3):
            self.orchestrator._watch_keymaps()
        self.assertEqual(tuple(self.addon_names()), names_before)
        self.assertEqual(self.runtime.configs.addon.keymaps.get('3D View').keymap_items.created,
                         creations)
        self.preferences.keymap.enable_keymaps = False
        self.orchestrator._watch_keymaps()
        self.assertEqual(set(self.addon_names()), {'bluehole.pipeline', 'bluehole.pie'})
        self.preferences.pie.enable_pie_menus = False
        self.orchestrator._watch_keymaps()
        self.assertEqual(self.addon_names(), ['bluehole.pipeline'])
        self.orchestrator.unregister()
        self.assertEqual(self.addon_names(), [])
        self.assertEqual(self.timers, {})

    def test_legacy_profile_blocks_saved_runtime_switches_until_review(self):
        settings = self.runtime.bpy.context.preferences.keymap
        settings.active_keyconfig = 'BH_Keymaps'
        self.orchestrator.register()
        self.assertEqual(self.addon_names(), [])
        settings.active_keyconfig = 'Blender'
        self.orchestrator._watch_keymaps()
        self.assertEqual(self.addon_names(), [])
        self.preferences.keymap.deluxe_configured = True
        self.orchestrator._watch_keymaps()
        self.assertEqual(len(self.addon_names()), 10)
        settings.active_keyconfig = 'BH_Keymaps'
        self.orchestrator._watch_keymaps()
        self.assertEqual(self.addon_names(), [])

    def test_disabling_deluxe_drains_pies_without_changing_the_saved_pie_switch(self):
        self.preferences.keymap.deluxe_configured = True
        self.orchestrator.register()
        self.preferences.keymap.enable_keymaps = False
        self.orchestrator.refresh()
        self.assertEqual(self.addon_names(), ['bluehole.pipeline'])
        self.assertTrue(self.preferences.pie.enable_pie_menus)
        self.preferences.keymap.enable_keymaps = True
        self.orchestrator.refresh()
        self.assertEqual(len(self.addon_names()), 10)

    def test_later_category_failure_drains_earlier_work_and_timer(self):
        self.fail_category = 'Sculpt'
        with self.assertRaisesRegex(RuntimeError, 'injected category failure'):
            self.orchestrator.register()
        self.assertEqual(self.addon_names(), [])
        self.assertEqual(self.timers, {})
        self.assertEqual(self.core.runtime_stats()['features'], 0)
        self.orchestrator.unregister()
        self.assertEqual(self.addon_names(), [])

    def test_addon_unload_drains_failed_post_register_init(self):
        prefix = self.h.prefix

        def stub(name, *, package=False, **attributes):
            module = types.ModuleType(prefix + '.' + name)
            if package:
                module.__path__ = []
            module.__dict__.update(attributes)
            sys.modules[module.__name__] = module
            return module

        stub('Lib.commonUtils.ui', use_pyside=True)
        diagnostics = sys.modules[prefix + '.Lib.commonUtils.runtime.diagnostics']
        diagnostics.configure = lambda **kwargs: None
        stub('Lib.commonUtils.ui.diagnostics', present_diagnostic=lambda *args: None)
        stub('wrappers', package=True)
        stub('wrappers.perforce', initialize_runtime=lambda: None)
        stub('blenderUtils', package=True)
        stub('operators', package=True)
        stub('environment', package=True)
        stub('ui', package=True)
        stub('ui.menus', package=True)
        for name in ('blenderUtils.callbacks', 'blenderUtils.addon_callbacks',
                     'preferences.addon_prefs', 'operators.operators_register',
                     'ui.menus.menus_register'):
            stub(name, register=lambda: None, unregister=lambda: None)
        env = stub('environment.envManager')
        env.if_current_env_missing_set_default = lambda: None
        env.get_env_from_prefs_active_env = lambda: types.SimpleNamespace(
            set_pref_from_ini=lambda: None)
        root_name = prefix
        spec = importlib.util.spec_from_file_location(root_name, ROOT / '__init__.py',
                                                       submodule_search_locations=[str(ROOT)])
        addon = importlib.util.module_from_spec(spec)
        sys.modules[root_name] = addon
        spec.loader.exec_module(addon)
        addon.register()
        self.fail_category = 'Sculpt'
        retry = addon._post_register_init()
        self.assertGreater(retry, 0)
        self.assertFalse(addon._keymaps_registered)
        self.assertEqual(self.addon_names(), [])
        self.assertEqual(self.core.runtime_stats()['features'], 0)
        addon.unregister()
        self.assertEqual(self.timers, {})
        self.assertEqual(self.addon_names(), [])


if __name__ == '__main__':
    unittest.main()
