"""Bulk reconciliation of the Object, Mesh and UV catalog."""

from collections import Counter, defaultdict
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

from runtime_keymap_fakes import FakeItems, FakeRuntime, row


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures'
BASELINE = FIXTURES / 'deluxe_keymaps'
CATEGORIES = ('object', 'mesh', 'uv')
# The common registrar installs Mesh before Object, then UV after 03.
REGISTRATION_ORDER = ('mesh', 'object', 'uv')


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def property_value(value):
    if isinstance(value, set):
        return tuple(sorted(value))
    if isinstance(value, list):
        return tuple(value)
    return value


class Category04CatalogTest(unittest.TestCase):
    def test_catalog_fields_order_toggles_and_coverage(self):
        receipt = json.loads((FIXTURES / 'deluxe_keymaps_category04/bulk-catalog.json').read_text())
        ledger = {r['row_id']: r for r in read_jsonl(BASELINE / 'reconciliation-ledger.jsonl')}
        transfers = {r['row_id'] for r in read_jsonl(
            FIXTURES / 'deluxe_keymaps_category03/reconciliation.jsonl')
            if r.get('authorized_transfer', {}).get('to_category') == '04'}
        self.assertEqual(set(receipt['transfers']), transfers)
        assigned = {id_ for id_, r in ledger.items() if r['owner'] == '04'} | transfers
        self.assertEqual(len(assigned), 310)

        def count(id_, capture):
            return ledger[id_]['presence'].get(capture, {}).get('user', 0)

        candidates = {id_ for id_ in assigned
                      if count(id_, 'full') > max(count(id_, 'stock'), count(id_, 'neither'))}
        declarations = {r['row_id']: r for r in receipt['declarations']}
        exceptions = {r['row_id'] for rows in receipt['exceptions'].values() for r in rows}
        self.assertEqual(len(declarations), len(receipt['declarations']))
        self.assertEqual(len(exceptions), sum(map(len, receipt['exceptions'].values())))
        self.assertFalse(declarations.keys() & exceptions)
        self.assertEqual(candidates, declarations.keys() | exceptions)
        self.assertLessEqual(transfers, declarations.keys())

        positions = defaultdict(set)
        for delta in read_jsonl(BASELINE / 'comparison-deltas.jsonl'):
            after = delta['after']
            if delta['comparison'] == 'stock-to-full' and after:
                positions[after['row_id']].add((after['map_order'], after['order']))

        runtime = FakeRuntime()
        runtime.bpy.types = types.SimpleNamespace(PropertyGroup=type('PropertyGroup', (), {}))
        prefs = types.SimpleNamespace(keymap=types.SimpleNamespace(enable_keymaps=True))
        bpy_props = types.ModuleType('bpy.props')
        bpy_props.BoolProperty = lambda **definition: definition
        prefix = '_bluehole_category04'
        with patch.dict(sys.modules, {'bpy': runtime.bpy, 'bpy.props': bpy_props}):
            def stub(suffix, path=None, **attrs):
                name = prefix + suffix
                module = types.ModuleType(name)
                if path is not None:
                    module.__path__ = [str(ROOT / path)]
                vars(module).update(attrs)
                sys.modules[name] = module

            def load(suffix):
                return importlib.import_module(prefix + '.' + suffix)

            stub('', '.')
            stub('.preferences', 'preferences')
            stub('.preferences.addon', 'preferences/addon')
            stub('.preferences.prefs', prefs=lambda: prefs)
            stub('.Lib.commonUtils.runtime.diagnostics')
            stub('.debug.debug_flags')
            stub('.operators.ui_ops',
                 WM_OT_BH_ToggleUISection=types.SimpleNamespace(bl_idname='test.toggle'),
                 draw_action_feature_keymaps_dropdown_state={})
            sys.modules['rna_keymap_ui'] = types.SimpleNamespace(draw_kmi=Mock())
            self.check_registration(runtime, prefs, load, ledger, declarations, positions)

    def check_registration(self, runtime, prefs, load, ledger, declarations, positions):
        utils = load('keymaps.keymap_utils')
        ui = load('preferences.addon.keymaps.keymap_props_modeling_ui')
        adapter = load('keymaps.keymap_action_utils')
        source_rows = defaultdict(list)
        registers = {}
        groups = {}
        expected = defaultdict(list)
        catalog = {}
        preset = json.loads((FIXTURES / 'deluxe_keymaps_category04/preset-explicit-properties.json').read_text())
        self.assertEqual(preset.keys(), {id_ for id_, entry in declarations.items()
                                        if entry['properties_source'] == 'reference preset explicit'})
        for category in CATEGORIES:
            module = load(f'actions.actions.keymaps.{category}')
            register = registers[category] = load(f'keymaps.{category}_keymaps_register')
            group_props = groups[category] = getattr(module, f'{category.upper()}_KEYMAP_GROUPS')
            props = load(f'preferences.addon.keymaps.keymap_props_{category}')
            cls = getattr(props, f'{category.upper() if category == "uv" else category.title()}KeymapPG')
            settings = types.SimpleNamespace(**{
                name: definition['default'] for name, definition in cls.__annotations__.items()
            })
            setattr(prefs.keymap, category, settings)
            actions = getattr(register, f'get_enabled_{category}_actions')()
            entries = [r for r in declarations.values() if r['category'] == category]
            for action, entry in zip(actions, entries, strict=True):
                binding, = action.keymap_bindings
                scope = adapter._binding_scope(binding, None)
                event = adapter._event(binding)
                id_ = entry['row_id']
                ref = ledger[id_]['binding']
                replacement = entry.get('replacement')
                target = ref['target']
                if replacement:
                    companion = ledger[replacement['also_covers']]['binding']
                    self.assertEqual(companion['scope'], ref['scope'])
                    self.assertEqual(companion['event'], ref['event'])
                    self.assertEqual(companion['target'], 'transform.translate')
                    self.assertTrue(companion['properties']['cursor_transform'])
                    self.assertTrue(companion['properties']['release_confirm'])
                    target = replacement['operator']
                self.assertEqual(asdict(scope), ref['scope'], id_)
                self.assertEqual(asdict(event), ref['event'], id_)
                self.assertEqual(action.get_idname(), target, id_)
                self.assertEqual(binding.active, ref['active'], id_)
                self.assertIn(tuple(entry['reference_order']), positions[id_], id_)
                self.assertIn(action, getattr(module, f'get_{category}_group_actions')(entry['group']))
                effective = {k: property_value(v) for k, v in ref['properties'].items()}
                properties = action.get_props()
                if replacement:
                    effective = {}
                    self.assertEqual(properties, effective, id_)
                elif entry['properties_source'] == 'reference preset explicit':
                    self.assertIn(properties, [{k: property_value(v) for k, v in m.items()}
                                               for m in preset[id_]], id_)
                    self.assertLessEqual(properties.items(), effective.items(), id_)
                else:
                    self.assertEqual(properties, effective, id_)
                key = (scope, event, target)
                self.assertNotIn(key, catalog)
                catalog[key] = (action, binding)
                source_rows[key].append(effective)
                expected[scope].append((entry['reference_order'][1], event, target, binding.active))
                if not any(utils.capture_scope(m) == scope for m in runtime.configs.default.keymaps):
                    stock = runtime.map('default', scope.name, space=scope.space_type)
                    stock.keymap_items.append_fixture(row('wm.inherited_stock', key='F23'))
                    provider = runtime.map('addon', scope.name, space=scope.space_type)
                    provider.keymap_items.append_fixture(row('wm.inherited_provider', key='F24'))

        create = FakeItems.new

        def with_schema(items, idname, *args, **kwargs):
            event = utils.KeymapEvent(
                **{k: v for k, v in kwargs.items() if k != 'head'},
                map_type='MOUSE' if 'MOUSE' in kwargs['type'] else 'KEYBOARD',
                hyper=False,
            )
            key = (utils.capture_scope(items.map), event, idname)
            schema, = source_rows[key]
            with patch.object(items, 'new_prop_schema', schema):
                return create(items, idname, *args, **kwargs)

        with patch.object(FakeItems, 'new', with_schema):
            for category in REGISTRATION_ORDER:
                register = registers[category]
                self.assertEqual(register.register(), sum(r['category'] == category
                                                         for r in declarations.values()))
            self.assertFalse([d for d in utils.runtime_diagnostics() if d.status != 'applied'])
            observed = {}
            for keymap in runtime.configs.user.keymaps:
                scope = utils.capture_scope(keymap)
                installed = [item for item in keymap.keymap_items
                             if not item.idname.startswith('wm.inherited_')]
                observed[scope] = [(utils.capture_event(item), item.idname, item.active)
                                   for item in installed]
                source = runtime.configs.addon.keymaps.get(scope.name)
                for item in installed:
                    key = (scope, utils.capture_event(item), item.idname)
                    effective, = source_rows[key]
                    self.assertEqual(dict(utils.capture_target(item).properties), effective)
                    action, binding = catalog[key]
                    self.assertIs(ui._find_binding(keymap, source, action, binding), item)
            self.assertEqual(observed, {scope: [row[1:] for row in sorted(rows)]
                                        for scope, rows in expected.items()})

            counts = Counter((r['category'], r['group']) for r in declarations.values())
            for category, register in registers.items():
                settings = getattr(prefs.keymap, category)
                total = sum(counts[category, group] for group in groups[category])
                for group, name in groups[category].items():
                    setattr(settings, name, False)
                    self.assertEqual(register.register(), total - counts[category, group])
                    setattr(settings, name, True)
                setattr(settings, f'enable_{category}_keymaps', False)
                self.assertEqual(register.register(), 0)
            self.assertEqual(utils.runtime_stats()['features'], 0)
            self.assertEqual(utils.runtime_stats()['owned'], 0)
            for keymap in runtime.configs.user.keymaps:
                self.assertEqual([item.idname for item in keymap.keymap_items],
                                 ['wm.inherited_provider', 'wm.inherited_stock'])
